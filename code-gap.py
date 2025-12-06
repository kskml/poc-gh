import os
import sys
import argparse
import json
import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Any, Set
from collections import defaultdict

import tiktoken
import openai

# --- Configuration ---
# Leave a buffer for the response tokens and prompt overhead
MAX_TOKENS_PER_REQUEST = 100000  
MODEL_NAME = "gpt-4-turbo" # This is the model name in Azure, not the deployment name

class CodeDocAnalyzer:
    """Analyzes code and documentation to find gaps using Azure OpenAI."""

    def __init__(self, api_key: str, endpoint: str, deployment_name: str):
        """Initializes the analyzer with Azure OpenAI credentials."""
        self.client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version="2024-02-15-preview"
        )
        self.deployment_name = deployment_name
        # Use tiktoken for accurate token counting, compatible with OpenAI models
        try:
            self.encoding = tiktoken.encoding_for_model(MODEL_NAME)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base") # Default for GPT-4

    def _count_tokens(self, text: str) -> int:
        """Counts the number of tokens in a text string."""
        return len(self.encoding.encode(text))

    def _extract_code_structure(self, repo_path: str) -> Dict[str, Any]:
        """
        Extracts the structure of the repository, including directories,
        files, and Python import relationships.
        """
        structure = {
            "directories": set(),
            "files": {},
            "imports": defaultdict(set),
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip irrelevant directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env', '.git']]
            
            rel_dir = os.path.relpath(root, repo_path)
            if rel_dir != '.':
                structure["directories"].add(rel_dir)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                structure["files"][rel_path] = {
                    "path": file_path,
                    "relative_path": rel_path,
                    "directory": rel_dir if rel_dir != '.' else "root",
                    "extension": os.path.splitext(file)[1],
                }
                
                # Extract imports for Python files to build a dependency graph
                if file.endswith('.py'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        structure["imports"][rel_path].add(alias.name)
                                elif isinstance(node, ast.ImportFrom):
                                    module = node.module or ""
                                    for alias in node.names:
                                        structure["imports"][rel_path].add(f"{module}.{alias.name}")
                    except Exception as e:
                        print(f"Warning: Could not parse {rel_path} for imports: {e}")
        
        # Convert sets to lists for JSON serialization
        structure["directories"] = list(structure["directories"])
        structure["imports"] = {k: list(v) for k, v in structure["imports"].items()}
        return structure

    def _group_files_semantically(self, code_structure: Dict[str, Any]) -> List[List[str]]:
        """
        Groups files based on directory structure and import relationships.
        This creates semantically coherent units for analysis.
        """
        file_groups = defaultdict(set)
        
        # Initial grouping by directory
        for file_path, file_info in code_structure["files"].items():
            directory = file_info["directory"]
            file_groups[directory].add(file_path)
        
        # Merge groups based on import relationships
        changed = True
        while changed:
            changed = False
            groups_to_merge = []
            
            group_keys = list(file_groups.keys())
            for i, dir1 in enumerate(group_keys):
                for dir2 in group_keys[i+1:]:
                    if dir1 not in file_groups or dir2 not in file_groups: # Already merged
                        continue
                    
                    # Check if files in dir1 import files in dir2
                    for file1 in file_groups[dir1]:
                        if file1 in code_structure["imports"]:
                            for import_path in code_structure["imports"][file1]:
                                # A simple heuristic: if an import path contains the other directory name, merge
                                if import_path.startswith(dir2.replace('/', '.')) or import_path.startswith(dir2.replace('\\', '.')):
                                    groups_to_merge.append((dir1, dir2))
                                    break
                        if groups_to_merge:
                            break
                    if groups_to_merge:
                        break
            
            # Perform the merges
            for dir1, dir2 in groups_to_merge:
                if dir1 in file_groups and dir2 in file_groups:
                    file_groups[dir1].update(file_groups[dir2])
                    del file_groups[dir2]
                    changed = True
        
        return [list(files) for files in file_groups.values()]

    def _create_chunks(self, file_paths: List[str], code_repo_path: str, docs_repo_path: str) -> List[Dict[str, Any]]:
        """
        Creates chunks of files that fit within the token limit.
        Handles large files by splitting them intelligently.
        """
        chunks = []
        current_chunk_files = []
        current_chunk_tokens = 0
        
        for file_path in file_paths:
            # Determine which repo the file belongs to
            code_full_path = os.path.join(code_repo_path, file_path)
            docs_full_path = os.path.join(docs_repo_path, file_path)
            
            file_type, full_path = None, None
            if os.path.exists(code_full_path):
                file_type, full_path = "code", code_full_path
            elif os.path.exists(docs_full_path):
                file_type, full_path = "doc", docs_full_path
            
            if not full_path:
                continue

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Skip binary files
                continue
            
            file_tokens = self._count_tokens(f"File: {file_path}\n\n{content}")

            # If the file itself is too large, split it
            if file_tokens > MAX_TOKENS_PER_REQUEST:
                # Save current chunk if it has content
                if current_chunk_files:
                    chunks.append({"files": current_chunk_files, "tokens": current_chunk_tokens})
                    current_chunk_files, current_chunk_tokens = [], 0
                
                self._split_large_file(file_path, content, file_type, chunks)
                continue

            # If adding this file exceeds the limit, start a new chunk
            if current_chunk_tokens + file_tokens > MAX_TOKENS_PER_REQUEST:
                chunks.append({"files": current_chunk_files, "tokens": current_chunk_tokens})
                current_chunk_files, current_chunk_tokens = [], 0
            
            # Add file to current chunk
            current_chunk_files.append({"path": file_path, "content": content, "type": file_type})
            current_chunk_tokens += file_tokens

        # Add the last chunk
        if current_chunk_files:
            chunks.append({"files": current_chunk_files, "tokens": current_chunk_tokens})
            
        return chunks

    def _split_large_file(self, file_path: str, content: str, file_type: str, chunks: List[Dict[str, Any]]):
        """Splits a single large file into smaller, manageable chunks."""
        if file_type == "code" and file_path.endswith('.py'):
            try:
                tree = ast.parse(content)
                functions = []
                classes = []
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions.append((node.lineno, node.end_lineno or len(content.split('\n')), f"def {node.name}"))
                    elif isinstance(node, ast.ClassDef):
                        classes.append((node.lineno, node.end_lineno or len(content.split('\n')), f"class {node.name}"))
                
                # Sort by line number and create chunks
                all_items = sorted(functions + classes, key=lambda x: x[0])
                lines = content.split('\n')
                
                for start, end, name in all_items:
                    chunk_content = '\n'.join(lines[start-1:end])
                    chunk_tokens = self._count_tokens(f"File: {file_path} ({name})\n\n{chunk_content}")
                    if chunk_tokens > MAX_TOKENS_PER_REQUEST:
                        # If a single function is too large, split it by lines
                        self._split_by_lines(file_path, chunk_content, file_type, chunks, name)
                    else:
                        chunks.append({
                            "files": [{"path": f"{file_path} ({name})", "content": chunk_content, "type": file_type}],
                            "tokens": chunk_tokens
                        })
                return # Successfully split by AST
            except Exception:
                # Fallback to line-based splitting if AST parsing fails
                pass
        
        # Fallback for non-Python files or if AST fails
        self._split_by_lines(file_path, content, file_type, chunks)

    def _split_by_lines(self, file_path: str, content: str, file_type: str, chunks: List[Dict[str, Any]], name_suffix=""):
        """Splits file content by line count to fit token limit."""
        lines = content.split('\n')
        current_lines = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = self._count_tokens(line + '\n')
            
            if current_tokens + line_tokens > MAX_TOKENS_PER_REQUEST:
                if current_lines:
                    chunk_content = '\n'.join(current_lines)
                    path_suffix = f" ({name_suffix})" if name_suffix else ""
                    chunks.append({
                        "files": [{"path": f"{file_path}{path_suffix}", "content": chunk_content, "type": file_type}],
                        "tokens": current_tokens
                    })
                    current_lines, current_tokens = [line], line_tokens
                else:
                    # Single line is too long, truncate it
                    truncated_line = line[:MAX_TOKENS_PER_REQUEST // 4]
                    chunks.append({
                        "files": [{"path": f"{file_path} (truncated)", "content": truncated_line, "type": file_type}],
                        "tokens": self._count_tokens(truncated_line)
                    })
            else:
                current_lines.append(line)
                current_tokens += line_tokens
        
        # Add remaining lines
        if current_lines:
            chunk_content = '\n'.join(current_lines)
            path_suffix = f" ({name_suffix})" if name_suffix else ""
            chunks.append({
                "files": [{"path": f"{file_path}{path_suffix}", "content": chunk_content, "type": file_type}],
                "tokens": current_tokens
            })

    def _analyze_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Sends a chunk of files to Azure OpenAI for gap analysis."""
        prompt = self._create_analysis_prompt(chunk["files"])
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name, # Deployment name in Azure
                messages=[
                    {"role": "system", "content": "You are an expert software architect and documentation specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2, # Lower temperature for more deterministic output
                response_format={"type": "json_object"} # Enforce JSON output
            )
            
            result_text = response.choices[0].message.content
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Error analyzing chunk: {e}")
            return {
                "error": str(e),
                "files_analyzed": [f["path"] for f in chunk["files"]],
                "structured": False
            }

    def _create_analysis_prompt(self, files: List[Dict[str, Any]]) -> str:
        """Creates the detailed prompt for the LLM."""
        files_text = ""
        for file_info in files:
            files_text += f"File: {file_info['path']} ({file_info['type']})\n"
            files_text += "```\n"
            files_text += file_info['content']
            files_text += "\n```\n\n"
        
        prompt = f"""
Analyze the provided code and documentation files to identify gaps between them.

A "gap" is any of the following:
- **missing_documentation**: Code exists but has no corresponding documentation.
- **outdated_documentation**: Documentation exists but does not accurately reflect the current code implementation.
- **missing_implementation**: Documentation describes a feature, function, or API that is not present in the code.
- **inaccurate_documentation**: Documentation is misleading or incorrect about the code's behavior.

Files to analyze:
{files_text}

Provide your analysis in the following JSON format:
{{
  "summary": "Brief summary of the overall gap analysis for this chunk.",
  "gaps": [
    {{
      "type": "missing_documentation|outdated_documentation|missing_implementation|inaccurate_documentation",
      "severity": "low|medium|high|critical",
      "file": "path/to/related/file",
      "description": "Detailed description of the gap, citing specific examples if possible.",
      "suggested_change": "A clear, actionable suggestion to fix the gap."
    }}
  ]
}}
"""
        return prompt

    def synthesize_results(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combines results from all chunks into a final report."""
        all_gaps = []
        files_analyzed = set()
        
        for result in chunk_results:
            if "error" in result or "gaps" not in result:
                continue
                
            files_analyzed.update(result.get("files_analyzed", []))
            all_gaps.extend(result["gaps"])
        
        # Sort gaps by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_gaps.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))
        
        critical_count = sum(1 for gap in all_gaps if gap.get("severity") == "critical")
        high_count = sum(1 for gap in all_gaps if gap.get("severity") == "high")
        
        summary = f"Analyzed {len(files_analyzed)} files and found {len(all_gaps)} gaps. "
        summary += f"Priority: {critical_count} critical and {high_count} high-severity issues require immediate attention."
        
        return {
            "summary": summary,
            "gaps": all_gaps,
            "files_analyzed": sorted(list(files_analyzed))
        }

    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Formats the final results into a Markdown report."""
        report = f"# Code-Documentation Gap Analysis Report\n\n"
        report += f"## Summary\n\n{results['summary']}\n\n"
        
        if results['gaps']:
            report += "## Identified Gaps\n\n"
            # Group gaps by severity for better readability
            gaps_by_severity = defaultdict(list)
            for gap in results['gaps']:
                severity = gap.get('severity', 'low')
                gaps_by_severity[severity].append(gap)
            
            for severity in ['critical', 'high', 'medium', 'low']:
                if severity in gaps_by_severity:
                    report += f"### {severity.title()} Severity\n\n"
                    for gap in gaps_by_severity[severity]:
                        report += f"**File:** `{gap.get('file', 'N/A')}`\n\n"
                        report += f"**Type:** {gap.get('type', 'N/A')}\n\n"
                        report += f"**Description:** {gap.get('description', 'No description')}\n\n"
                        report += f"**Suggested Change:** {gap.get('suggested_change', 'No suggestion')}\n\n"
                        report += "---\n\n"
        else:
            report += "## ✅ No Gaps Found\n\nCongratulations! The analysis did not find any significant gaps between the code and documentation.\n\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(description='Analyze gaps between code and documentation using Azure OpenAI.')
    parser.add_argument('--code-repo', required=True, help='Path to the code repository.')
    parser.add_argument('--docs-repo', required=True, help='Path to the documentation repository.')
    parser.add_argument('--output-file', default='gap_analysis_report.md', help='Output file name for the report.')
    
    args = parser.parse_args()
    
    # Get credentials from environment variables set by GitHub Action
    api_key = os.environ.get('AZURE_OPENAI_API_KEY')
    endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
    deployment_name = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME')
    
    if not all([api_key, endpoint, deployment_name]):
        print("Error: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME must be set as environment variables.")
        sys.exit(1)
        
    print("Initializing Azure OpenAI Analyzer...")
    analyzer = CodeDocAnalyzer(api_key, endpoint, deployment_name)
    
    print("1. Extracting code structure...")
    code_structure = analyzer._extract_code_structure(args.code_repo)
    
    print("2. Grouping files semantically...")
    file_groups = analyzer._group_files_semantically(code_structure)
    print(f"   Created {len(file_groups)} semantic groups.")
    
    print("3. Creating chunks for analysis...")
    all_chunks = []
    for i, group in enumerate(file_groups):
        chunks = analyzer._create_chunks(group, args.code_repo, args.docs_repo)
        all_chunks.extend(chunks)
    print(f"   Created {len(all_chunks)} chunks total.")
    
    print("4. Analyzing chunks with Azure OpenAI...")
    chunk_results = []
    for i, chunk in enumerate(all_chunks):
        print(f"   Analyzing chunk {i+1}/{len(all_chunks)} ({len(chunk['files'])} files, {chunk['tokens']} tokens)...")
        result = analyzer._analyze_chunk(chunk)
        chunk_results.append(result)
    
    print("5. Synthesizing results...")
    final_results = analyzer.synthesize_results(chunk_results)
    
    print("6. Generating Markdown report...")
    report = analyzer.generate_markdown_report(final_results)
    
    with open(args.output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Analysis complete. Report saved to {args.output_file}")

if __name__ == "__main__":
    main()

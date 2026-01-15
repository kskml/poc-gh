import os
import requests
from dotenv import load_dotenv
from openai import AzureOpenAI
from markdownify import markdownify as md
from pathlib import Path

# Load environment variables
load_dotenv()

# --- CONFIGURATION FOR DEMO ---
# Add this comment to your code to flag it for review
# Example: # NEW_CHANGE: Added retry logic
SEARCH_TAG = "NEW_CHANGE" 

# How many lines above/below the tag to capture (provides context to the LLM)
CONTEXT_LINES = 10 
# ------------------------------

def get_confluence_content(base_url, email, token, page_id):
    """Fetches documentation and converts to Markdown."""
    auth = (email, token)
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage"
    print(f"Fetching Confluence page ID: {page_id}...")
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Confluence API Error: {response.status_code}")
    return md(response.json()['body']['storage']['value'])

def extract_flagged_snippets(root_path_str):
    """
    Scans local files for the SEARCH_TAG and extracts surrounding code.
    """
    root_path = Path(root_path_str)
    ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'bin', 'obj', 'dist'}
    extensions = {'.py', '.js', '.ts', '.java', '.cs', '.go', '.cpp', '.h', '.c'}
    
    found_snippets = []
    
    print(f"🔍 Scanning for tag '{SEARCH_TAG}' in: {root_path_str}")
    
    for file_path in root_path.rglob('*'):
        if not file_path.is_file() or any(part in ignore_dirs for part in file_path.parts):
            continue
            
        if file_path.suffix.lower() in extensions:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines):
                    if SEARCH_TAG in line:
                        start_index = max(0, i - CONTEXT_LINES)
                        end_index = min(len(lines), i + CONTEXT_LINES + 1)
                        
                        snippet_lines = lines[start_index:end_index]
                        snippet_text = "".join(snippet_lines)
                        
                        found_snippets.append({
                            "file": str(file_path.relative_to(root_path)),
                            "line": i + 1,
                            "snippet": snippet_text
                        })
                        print(f"   → Found change in: {file_path.name} (Line {i+1})")
                        
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
                
    return found_snippets

def analyze_flagged_changes(client, deployment_name, doc_content, snippets):
    """
    Refined Prompt for SWE2 Demo Output.
    """
    
    system_prompt = """
    You are a Senior SWE2 performing a "Triage Review" for a documentation update request.
    
    **Your Task:**
    Analyze the provided code snippets (flagged as changes) against the Existing Documentation.
    Determine if the documentation is still accurate or requires updates.
    
    **Classification Logic:**
    - 🔴 **CRITICAL:** Breaking changes in API signatures, removed parameters, or changed error codes.
    - 🟠 **HIGH:** New parameters, new endpoints, or significant logic flow changes.
    - 🟡 **MEDIUM:** Minor logic tweaks, enum value updates, or internal refactoring.
    - ✅ **NO ACTION:** Comment-only changes, variable renames, or whitespace fixes.
    
    **Output Structure (Markdown):**
    Generate a professional report.
    
    1. **Header:** "SWE2 Code Change Impact Analysis"
    2. **Executive Summary:** Bullet points summarizing the findings (e.g., "2 Critical gaps found", "1 New endpoint detected").
    3. **Detailed Review Table:**
       Columns:
       - **Severity:** (Use the emoji logic above)
       - **File:** (Filename)
       - **Confluence Section:** (The specific section header # or ## that needs updating)
       - **Gap Type:** (API Contract, Logic, Error Handling, None)
       - **Observation:** (What changed?)
       - **Required Action:** (Specific text to add/edit in Confluence)
    
    **Style Guide:**
    - Be concise and direct.
    - If the doc is accurate, state "Documentation is Valid" in the Action column.
    - Use bold text for file names and section headers.
    """

    # Prepare the snippets for the prompt
    formatted_snippets = ""
    for idx, snip in enumerate(snippets):
        formatted_snippets += f"\n--- FLAGGED CHANGE {idx+1} ---\n"
        formatted_snippets += f"File: {snip['file']} (Line {snip['line']})\n"
        formatted_snippets += f"Code:\n{snip['snippet']}\n"

    user_prompt = f"""
    EXISTING DOCUMENTATION:
    {doc_content}

    ---
    
    FLAGGED CODE CHANGES:
    {formatted_snippets}
    """
    
    print("🧠 Generating SWE2 Impact Analysis...")
    
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error calling Azure OpenAI: {str(e)}"

def save_report(content, filename="SWE2_Impact_Analysis.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Report saved to {filename}")

def main():
    # 1. Initialize Client
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return

    # 2. Config
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    email = os.getenv("CONFLUENCE_EMAIL")
    token = os.getenv("CONFLUENCE_API_TOKEN")
    page_id = os.getenv("PAGE_ID")
    code_path = os.getenv("LOCAL_CODE_PATH")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not all([base_url, email, token, page_id, code_path]):
        print("❌ Error: Missing configuration in .env file.")
        return

    try:
        # 3. Fetch Docs
        doc_text = get_confluence_content(base_url, email, token, page_id)
        
        # 4. Find Flagged Snippets
        snippets = extract_flagged_snippets(code_path)
        
        if snippets:
            # 5. Analyze
            report_content = analyze_flagged_changes(client, deployment_name, doc_text, snippets)
            
            # 6. Save
            save_report(report_content)
        else:
            print(f"⚠️  No code changes found with tag '{SEARCH_TAG}'. Make a change and tag it!")

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    main()

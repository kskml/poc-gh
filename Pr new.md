import os
import requests
from dotenv import load_dotenv
from openai import AzureOpenAI
from markdownify import markdownify as md
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI Client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

class ConfluenceReader:
    def __init__(self):
        self.base_url = os.getenv("CONFLUENCE_BASE_URL")
        self.email = os.getenv("CONFLUENCE_EMAIL")
        self.token = os.getenv("CONFLUENCE_API_TOKEN")
        self.auth = (self.email, self.token)

    def get_content(self, page_id):
        url = f"{self.base_url}/rest/api/content/{page_id}?expand=body.storage"
        response = requests.get(url, auth=self.auth)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching Confluence: {response.status_code} - {response.text}")
        
        html_data = response.json()['body']['storage']['value']
        return md(html_data)

class CodeAggregator:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'bin', 'obj'}

    def get_combined_code(self):
        combined_text = ""
        extensions = {'.py', '.js', '.ts', '.java', '.cs', '.go', '.cpp', '.h', '.c', '.json', '.yaml', '.yml'}
        
        print("Reading source files...")
        for file_path in self.root_path.rglob('*'):
            if not file_path.is_file() or any(part in self.ignore_dirs for part in file_path.parts):
                continue
                
            if file_path.suffix.lower() in extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        combined_text += f"\n\n--- FILE: {file_path.relative_to(self.root_path)} ---\n"
                        combined_text += content
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")
        
        return combined_text

def run_analysis():
    # 1. Get Documentation
    print("Fetching Confluence page...")
    confluence_reader = ConfluenceReader()
    page_id = os.getenv("PAGE_ID")
    doc_content = confluence_reader.get_content(page_id)

    # 2. Get Code
    code_path = os.getenv("LOCAL_CODE_PATH")
    if not os.path.exists(code_path):
        print(f"Error: Path {code_path} does not exist.")
        return

    aggregator = CodeAggregator(code_path)
    code_content = aggregator.get_combined_code()

    # 3. SWE2 Focused Prompt
    system_prompt = """
    You are a Level 2 Software Engineer (SWE2) performing a detailed peer review. 
    Your task is to verify that the 'Technical Documentation' accurately describes the provided 'Source Code'.
    
    Strictly adhere to SWE2 standards. Focus on implementation details, logic correctness, and interface definitions.
    
    Check for the following specific categories of gaps:
    
    1. **Interface/Signature Mismatch:**
       - Do function names, parameters, and return types match the documentation?
       - Are API endpoints defined correctly in docs vs code?
    
    2. **Business Logic Deviation:**
       - Does the conditional logic (if/else/switch) in the code match the documented behavior?
       - Are there hardcoded values or magic numbers in code that contradict the spec?
    
    3. **Error Handling & Edge Cases:**
       - Does the code handle errors that are documented (e.g., "throws 404 if not found")?
       - Does the code have try/catch blocks or validations that are NOT mentioned in the docs?
    
    4. **Undocumented Features:**
       - Are there significant functions, classes, or endpoints in the code that are completely absent from the documentation?
    
    Return your analysis in the following Markdown format:
    
    # SWE2 Code-to-Doc Gap Analysis
    
    ## Review Summary
    [One sentence summary of alignment status]
    
    ## Critical Gaps (Implementation vs Docs)
    * **Discrepancy:** [Describe what the Doc says vs what the Code does]
    * **File Reference:** [Mention the specific file if possible]
    * **Proposed Change:** [Specific technical text to fix the doc or code]
    
    ## Missing Documentation (Code features not in Doc)
    * **Feature:** [Describe the code implementation]
    * **Proposed Change:** [Suggest text to add to documentation]
    """

    user_prompt = f"""
    TECHNICAL DOCUMENTATION:
    {doc_content}

    ---
    
    SOURCE CODE:
    {code_content}
    """

    total_chars = len(doc_content) + len(user_prompt)
    print(f"Total input characters: {total_chars}")
    
    print("Sending to Azure OpenAI for SWE2 analysis...")
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1 # Low temperature for high precision/technical accuracy
        )
        
        analysis_result = response.choices[0].message.content
        
        # 4. Save Report
        output_file = "swe2_gap_analysis_report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(analysis_result)
            
        print(f"Success! Report saved to {output_file}")

    except Exception as e:
        print(f"Error during LLM call: {e}")

if __name__ == "__main__":
    run_analysis()

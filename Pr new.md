import os
import requests
from dotenv import load_dotenv
from openai import AzureOpenAI
from markdownify import markdownify as md
from pathlib import Path

# Load environment variables once at the start
load_dotenv()

def get_confluence_content(base_url, email, token, page_id):
    """
    Fetches content from Confluence and converts HTML to Markdown.
    """
    auth = (email, token)
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage"
    
    print(f"Fetching Confluence page ID: {page_id}...")
    response = requests.get(url, auth=auth)
    
    if response.status_code != 200:
        raise Exception(f"Confluence API Error: {response.status_code} - {response.text}")
    
    html_data = response.json()['body']['storage']['value']
    return md(html_data)

def read_local_code(root_path_str):
    """
    Reads all relevant code files from the local directory and combines them
    into a single string with file headers.
    """
    root_path = Path(root_path_str)
    ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'bin', 'obj', 'dist'}
    extensions = {'.py', '.js', '.ts', '.java', '.cs', '.go', '.cpp', '.h', '.c', '.json', '.yaml', '.yml'}
    
    combined_text = ""
    file_count = 0
    
    print(f"Scanning local code in: {root_path_str}")
    
    for file_path in root_path.rglob('*'):
        # Skip directories and ignored folders
        if not file_path.is_file() or any(part in ignore_dirs for part in file_path.parts):
            continue
            
        if file_path.suffix.lower() in extensions:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Add a clear separator for the LLM
                    relative_path = file_path.relative_to(root_path)
                    combined_text += f"\n\n--- FILE START: {relative_path} ---\n"
                    combined_text += content
                    combined_text += "\n--- FILE END ---\n"
                    file_count += 1
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
                
    print(f"Successfully read {file_count} files.")
    return combined_text

def analyze_with_azure_openai(client, deployment_name, doc_content, code_content):
    """
    Sends the documentation and code to Azure OpenAI for SWE2 level analysis.
    """
    
    # SWE2 Specific System Prompt
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
    
    print("Sending request to Azure OpenAI...")
    print(f"Total characters in input: {len(doc_content) + len(code_content)}")
    
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1 # Low temperature for technical precision
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling Azure OpenAI: {str(e)}"

def save_report(content, filename="swe2_gap_analysis_report.md"):
    """
    Saves the generated report to a markdown file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Report saved to {filename}")

def main():
    # 1. Initialize Azure Client
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    except Exception as e:
        print(f"Failed to initialize Azure OpenAI Client: {e}")
        return

    # 2. Get Configuration
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    email = os.getenv("CONFLUENCE_EMAIL")
    token = os.getenv("CONFLUENCE_API_TOKEN")
    page_id = os.getenv("PAGE_ID")
    code_path = os.getenv("LOCAL_CODE_PATH")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not all([base_url, email, token, page_id, code_path]):
        print("Error: Missing configuration in .env file.")
        return

    try:
        # 3. Fetch Data
        doc_text = get_confluence_content(base_url, email, token, page_id)
        code_text = read_local_code(code_path)

        # 4. Analyze
        analysis_result = analyze_with_azure_openai(client, deployment_name, doc_text, code_text)

        # 5. Save Output
        save_report(analysis_result)

    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()

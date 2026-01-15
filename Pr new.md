import os
import requests
from dotenv import load_dotenv
from openai import AzureOpenAI
from markdownify import markdownify as md
from pathlib import Path

# Load environment variables
load_dotenv()

def get_confluence_content(base_url, email, token, page_id):
    auth = (email, token)
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage"
    
    print(f"Fetching Confluence page ID: {page_id}...")
    response = requests.get(url, auth=auth)
    
    if response.status_code != 200:
        raise Exception(f"Confluence API Error: {response.status_code} - {response.text}")
    
    html_data = response.json()['body']['storage']['value']
    return md(html_data)

def read_local_code(root_path_str):
    root_path = Path(root_path_str)
    ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'bin', 'obj', 'dist'}
    extensions = {'.py', '.js', '.ts', '.java', '.cs', '.go', '.cpp', '.h', '.c', '.json', '.yaml', '.yml'}
    
    combined_text = ""
    file_count = 0
    
    print(f"Scanning local code in: {root_path_str}")
    
    for file_path in root_path.rglob('*'):
        if not file_path.is_file() or any(part in ignore_dirs for part in file_path.parts):
            continue
            
        if file_path.suffix.lower() in extensions:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
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
    Generates a professional SWE2 Audit Report in Markdown format.
    """
    
    # Optimized Prompt for Demo Presentation
    system_prompt = """
    You are a Senior Technical Lead reviewing an SWE2's audit of Documentation vs Source Code.
    Generate a professional "Gap Analysis Report" in Markdown format.
    
    **Structure the report as follows:**
    
    1. **Header:**
       - Title: "SWE2 Documentation Compliance Report"
       - Date: [Today's Date]
       - Status: "Review Required"
    
    2. **Executive Summary:**
       - A bulleted list summarizing the overall health of the documentation.
       - Example: "Documentation is 80% aligned with code. 3 Critical Logic Gaps found."
    
    3. **Detailed Findings Table:**
       Use a Markdown table with the following columns:
       - **Severity:** (Assign: P0-Critical, P1-High, P2-Medium, P3-Low based on impact)
       - **Confluence Section:** (The specific Header # or ## that needs update)
       - **Gap Type:** (Logic Mismatch, API Contract Missing, Error Handling, Typo)
       - **Observation:** (Detailed technical observation)
       - **SWE2 Recommendation:** (Specific action to fix the doc or code)
       - **Evidence File:** (The source file proving the gap)
       
    4. **Next Steps:**
       - A numbered list of immediate actions for the engineering team.
       
    **Style Guidelines:**
    - Be precise and technical.
    - Use bolding for key terms in the table.
    - Ensure the table is aligned and readable.
    """

    user_prompt = f"""
    TECHNICAL DOCUMENTATION:
    {doc_content}

    ---
    
    SOURCE CODE:
    {code_content}
    """
    
    print("Generating Professional SWE2 Audit Report...")
    
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1 # Low temperature for factual consistency
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling Azure OpenAI: {str(e)}"

def save_report(content, filename="SWE2_Audit_Report.md"):
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
        report_content = analyze_with_azure_openai(client, deployment_name, doc_text, code_text)

        # 5. Save Output
        save_report(report_content)

    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()

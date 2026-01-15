import os
import requests
from dotenv import load_dotenv
from openai import AzureOpenAI
from markdownify import markdownify as md
from pathlib import Path

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
# This is the specific comment tag you will add to your code to mark new changes
# Example in Python: # NEW_CHANGE
# Example in Java/JS: // NEW_CHANGE
SEARCH_TAG = "NEW_CHANGE" 
CONTEXT_LINES = 15 # How many lines before and after the tag to include
# --------------------

def get_confluence_content(base_url, email, token, page_id):
    """Fetches documentation."""
    auth = (email, token)
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage"
    print(f"Fetching Confluence page ID: {page_id}...")
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Confluence API Error: {response.status_code}")
    return md(response.json()['body']['storage']['value'])

def extract_flagged_snippets(root_path_str):
    """
    Scans local files for the SEARCH_TAG and extracts the surrounding code context.
    Returns a list of dictionaries containing file path and code snippet.
    """
    root_path = Path(root_path_str)
    ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'bin', 'obj', 'dist'}
    extensions = {'.py', '.js', '.ts', '.java', '.cs', '.go', '.cpp', '.h', '.c'}
    
    found_snippets = []
    
    print(f"Scanning for tag '{SEARCH_TAG}' in: {root_path_str}")
    
    for file_path in root_path.rglob('*'):
        if not file_path.is_file() or any(part in ignore_dirs for part in file_path.parts):
            continue
            
        if file_path.suffix.lower() in extensions:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines):
                    # Check if the magic tag is present in the line
                    if SEARCH_TAG in line:
                        # Calculate context window
                        start_index = max(0, i - CONTEXT_LINES)
                        end_index = min(len(lines), i + CONTEXT_LINES + 1)
                        
                        # Extract snippet
                        snippet_lines = lines[start_index:end_index]
                        snippet_text = "".join(snippet_lines)
                        
                        found_snippets.append({
                            "file": str(file_path.relative_to(root_path)),
                            "line_number": i + 1, # 1-based index for reporting
                            "snippet": snippet_text
                        })
                        
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
                
    if not found_snippets:
        print(f"No code changes found with tag '{SEARCH_TAG}'. Please add the tag to your code.")
    else:
        print(f"Found {len(found_snippets)} change(s).")
        
    return found_snippets

def analyze_flagged_changes(client, deployment_name, doc_content, snippets):
    """
    Analyzes specific code snippets against documentation.
    """
    
    system_prompt = """
    You are a Senior SWE2 reviewing specific code updates against existing documentation.
    
    **Context:**
    1. You have "Existing Documentation".
    2. You have "Code Snippets" that have been flagged by the developer as new/changed code.
    
    **Your Task:**
    For each flagged snippet, determine if the documentation accurately reflects the new code behavior.
    
    **Output Format (Markdown Table):**
    Create a table with the following columns:
    - **File:** (The filename of the change)
    - **Confluence Section:** (Which section needs update, e.g., ## API Endpoints)
    - **Gap Type:** (New Feature, Logic Change, Parameter Update, No Action Needed)
    - **Observation:** (What is different in the code?)
    - **SWE2 Action:** (Specific instruction to fix the documentation)
    
    If the change is trivial (e.g., a comment or a variable rename), mark "No Action Needed".
    """

    # Format snippets for the prompt
    formatted_snippets = ""
    for idx, snip in enumerate(snippets):
        formatted_snippets += f"\n--- SNIPPET {idx+1} ---\n"
        formatted_snippets += f"File: {snip['file']} (Line {snip['line_number']})\n"
        formatted_snippets += f"Code:\n{snip['snippet']}\n"

    user_prompt = f"""
    EXISTING DOCUMENTATION:
    {doc_content}

    ---
    
    FLAGGED CODE CHANGES:
    {formatted_snippets}
    """
    
    print("Analyzing flagged changes against documentation...")
    
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
        return f"Error calling Azure OpenAI: {str(e)}"

def save_report(content, filename="Tagged_Change_Report.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# SWE2 Flagged Change Impact Report\n\n")
        f.write(content)
    print(f"Report saved to {filename}")

def main():
    # 1. Initialize Client
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    except Exception as e:
        print(f"Initialization Error: {e}")
        return

    # 2. Config
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    email = os.getenv("CONFLUENCE_EMAIL")
    token = os.getenv("CONFLUENCE_API_TOKEN")
    page_id = os.getenv("PAGE_ID")
    code_path = os.getenv("LOCAL_CODE_PATH")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not all([base_url, email, token, page_id, code_path]):
        print("Error: Missing configuration.")
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
            print("No code changes found with the specified tag.")

    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    main()

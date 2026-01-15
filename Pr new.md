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
SEARCH_TAG = "NEW_CHANGE" 
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
    """Scans local files for the SEARCH_TAG."""
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
                        print(f"   → Found change in: {file_path.name}")
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return found_snippets

def analyze_flagged_changes(client, deployment_name, doc_content, snippets):
    """
    Refined Prompt for Functional Reporting.
    """
    
    system_prompt = """
    You are a Senior SWE2 acting as a liaison between Engineering and the Product Team.
    Your task is to review code changes and generate a report for **Functional Stakeholders** (PM, QA, Business).
    
    **CRITICAL INSTRUCTION - FUNCTIONAL PERSPECTIVE:**
    - In the "Observation" column, describe the **Business Impact** or **User Experience Change**.
    - DO NOT mention variable names, classes, database tables, or internal code mechanics (e.g., "refactored loop").
    - DO mention changes to inputs, outputs, errors displayed to users, or behavior flows.
    
    **Translation Examples:**
    - Code: `added timeout parameter` 
      -> Observation: "Users can now control how long the system waits before giving up."
    - Code: `removed include_profile param`
      -> Observation: "The system will no longer return extended profile details in the standard response."
    - Code: `renamed var x to y`
      -> Observation: "No functional change."
    
    **Severity Logic:**
    - 🔴 **CRITICAL:** Breaks existing user flows or changes data returned to the user.
    - 🟠 **HIGH:** Adds new capability or changes validation rules.
    - 🟡 **MEDIUM:** Cosmetic changes or minor wording updates in error messages.
    - ✅ **NO ACTION:** Internal refactoring with zero user impact.
    
    **Output Structure (Markdown Table):**
    1. **Severity:** (Use emojis)
    2. **Area:** (e.g., User Login, Payments, Reporting)
    3. **Observation:** (Functional description of the change)
    4. **Documentation Action:** (What specifically needs to be added/edited in Confluence)
    5. **File:** (Filename for Dev reference)
    """

    formatted_snippets = ""
    for idx, snip in enumerate(snippets):
        formatted_snippets += f"\n--- CHANGE {idx+1} ---\n"
        formatted_snippets += f"File: {snip['file']}\n"
        formatted_snippets += f"Code:\n{snip['snippet']}\n"

    user_prompt = f"""
    EXISTING DOCUMENTATION:
    {doc_content}

    ---
    
    CODE CHANGES (Review these):
    {formatted_snippets}
    """
    
    print("🧠 Generating Functional Impact Report...")
    
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

def save_report(content, filename="Functional_Impact_Report.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Report saved to {filename}")

def main():
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return

    base_url = os.getenv("CONFLUENCE_BASE_URL")
    email = os.getenv("CONFLUENCE_EMAIL")
    token = os.getenv("CONFLUENCE_API_TOKEN")
    page_id = os.getenv("PAGE_ID")
    code_path = os.getenv("LOCAL_CODE_PATH")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not all([base_url, email, token, page_id, code_path]):
        print("❌ Error: Missing configuration.")
        return

    try:
        doc_text = get_confluence_content(base_url, email, token, page_id)
        snippets = extract_flagged_snippets(code_path)
        
        if snippets:
            report_content = analyze_flagged_changes(client, deployment_name, doc_text, snippets)
            save_report(report_content)
        else:
            print(f"⚠️  No code changes found with tag '{SEARCH_TAG}'.")
    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    main()

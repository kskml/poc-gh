import os
import requests
from dotenv import load_dotenv
from openai import AzureOpenAI
from markdownify import markdownify as md
from pathlib import Path

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
SEARCH_TAG = "NEW_CHANGE" 
CONTEXT_LINES = 10 
# ----------------------

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
    Refined Prompt for Section Mapping & Functional Severity.
    """
    
    system_prompt = """
    You are a Senior Technical Writer analyzing code changes for Product Management.
    Your goal is to map code changes to the existing Confluence Documentation and assess the functional impact.
    
    **STRICT RULES:**
    1. **Confluence Section:** You MUST identify the specific Section Header (e.g., ## Login, ### API Responses) from the provided "Existing Documentation" that relates to the code change. 
       - If no section exists, suggest where it *should* go (e.g., "N/A - Needs New Section").
    2. **Functional Observation:** Describe the change in **Business/User Terms**.
       - DO NOT mention variables, classes, or internal methods.
       - DO mention inputs, outputs, error messages, or user permissions.
       - Example: "Users can now upload files larger than 10MB." (Not "Increased buffer size").
    3. **Severity (Functional):**
       - 🔴 **CRITICAL:** Breaks existing user flow, removes a feature, or returns different data than expected.
       - 🟠 **HIGH:** Adds a new feature or capability visible to the user.
       - 🟡 **MEDIUM:** Changes validation rules, error text, or UI labels.
       - ✅ **NONE:** Internal refactoring (zero user impact).
    
    **Output Format (Markdown):**
    
    # Functional Impact Dashboard
    
    ## Executive Summary
    - **Total Changes:** [Count]
    - **Critical:** [Count]
    - **New Features:** [Count]
    - **Documentation Coverage:** [Percentage]
    
    ## Detailed Review
    
    | Severity | Confluence Section | Functional Impact (Observation) | Documentation Action | File |
    | :--- | :--- | :--- | :--- | :--- |
    | [Emoji] | [Exact Header from Doc] | [User description] | [What to edit/add] | [File Name] |
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
    
    CODE CHANGES:
    {formatted_snippets}
    """
    
    print("🧠 Generating Functional Dashboard...")
    
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

def save_report(content, filename="Functional_Impact_Dashboard.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Dashboard saved to {filename}")

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

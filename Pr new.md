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
    """Fetches documentation."""
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
                        print(f"   → Found change.")
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return found_snippets

def analyze_flagged_changes(client, deployment_name, doc_content, snippets):
    """
    ASPICE SWE.2 Aligned Prompt.
    """
    
    system_prompt = """
    You are an ASPICE SWE.2 Auditor performing a **Functional Consistency Check**.
    You are verifying that the Code Implementation is consistent with the Functional Documentation (Confluence).
    
    **CRITICAL INSTRUCTIONS - ASPICE SWE.2 CONTEXT:**
    1. **Perspective:** Report on **Functional Behavior**, **User Experience**, and **System Logic**.
    2. **No Code Details:** Do not mention variables, classes, file paths, or internal methods in the output.
    3. **SWE.2 Consistency Check:** Verify if the documented functional behavior matches the implemented behavior.
    
    **Column Definitions:**
    - **Severity:** 
      - 🔴 **NON-CONFORMANT:** Functional behavior in code contradicts documentation.
      - 🟠 **GAP IDENTIFIED:** Code has new functional behavior not covered in documentation.
      - 🟡 **INCONSISTENCY:** Minor text or parameter description mismatch.
      - ✅ **CONFORMANT:** Functional behavior matches documentation perfectly.
      
    - **SWE.2 Observation (Functional):**
      - Describe the gap in terms of **Functional Specification**.
      - Example: "Functional Specification describes behavior A, but implementation performs behavior B."
      
    - **Corrective Action:**
      - Frame actions as updates to the **Functional Specification**.
      - Example: "Update Functional Specification to reflect new behavior."

    **Output Format:**
    Return ONLY a single Markdown table. Do not include headers or introductions.
    """

    formatted_snippets = ""
    for idx, snip in enumerate(snippets):
        formatted_snippets += f"\n--- CHANGE {idx+1} ---\n"
        formatted_snippets += f"Code:\n{snip['snippet']}\n"

    user_prompt = f"""
    FUNCTIONAL DOCUMENTATION (Confluence):
    {doc_content}

    ---
    
    CODE IMPLEMENTATION CHANGES:
    {formatted_snippets}
    """
    
    print("🧠 Running ASPICE SWE.2 Functional Consistency Check...")
    
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

def save_report(content, filename="ASPICE_SWE2_Audit_Report.md"):
    """
    Saves the report with explicit Severity Definitions at the top.
    """
    with open(filename, "w", encoding="utf-8") as f:
        # 1. Main Title
        f.write("# ASPICE SWE.2 Functional Consistency Report\n\n")
        
        # 2. Severity Definitions Section (New Requirement)
        f.write("## Severity & Classification Definitions\n\n")
        f.write("This report evaluates the consistency between Functional Specification and Code Implementation based on ASPICE SWE.2 criteria.\n\n")
        f.write("| Severity | Definition (ASPICE Context) |\n")
        f.write("| :--- | :--- |\n")
        f.write("| 🔴 **NON-CONFORMANT** | The implemented functionality contradicts the Functional Specification. This represents a High Risk to quality and compliance. | \n")
        f.write("| 🟠 **GAP IDENTIFIED** | New functional behavior exists in the code but is missing from the Specification. Represents a Traceability Gap. | \n")
        f.write("| 🟡 **INCONSISTENCY** | Minor discrepancies in parameter definitions, descriptions, or limits. | \n")
        f.write("| ✅ **CONFORMANT** | Functional behavior matches the specification accurately. | \n")
        f.write("\n---\n\n")
        
        # 3. LLM Analysis Content (The Table)
        f.write("## Detailed Analysis\n\n")
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

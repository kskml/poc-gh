import os
import requests
from dotenv import load_dotenv
from openai import AzureOpenAI
from markdownify import markdownify as md

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
# Confluence
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

# GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER") # e.g., "my-org"
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME") # e.g., "my-project"
GITHUB_BASE_TAG = os.getenv("GITHUB_BASE_TAG")   # e.g., "v1.0.0"
GITHUB_HEAD_TAG = os.getenv("GITHUB_HEAD_TAG")   # e.g., "v1.1.0"

# Azure
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
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

def get_github_diff(owner, repo, base_tag, head_tag, token):
    """
    Fetches the Unified Diff between two release tags from GitHub API.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base_tag}...{head_tag}"
    print(f"Fetching GitHub Diff: {base_tag} -> {head_tag}...")
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GitHub API Error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    # Extract the diff string from the response
    # GitHub returns a large 'files' array, but the top-level 'diff' field aggregates it for us nicely
    diff_content = data.get('diff', '')
    
    if not diff_content:
        print("Warning: No diff found between tags (or identical tags).")
        return ""
        
    print(f"✅ Diff retrieved (Length: {len(diff_content)} chars).")
    return diff_content

def analyze_diff_with_confluence(client, deployment_name, doc_content, git_diff):
    """
    Analyzes the Git Diff against Confluence Documentation.
    Uses the same ASPICE SWE.2 logic and combined severity.
    """
    
    system_prompt = """
    You are an ASPICE SWE.2 Auditor analyzing the impact of a **Software Release** (GitHub Diff) on **Functional Documentation** (Confluence).
    
    **CRITICAL INSTRUCTIONS:**
    1. **Source Material:** You are given a "GitHub Unified Diff". Parse `+` (additions) and `-` (deletions) to understand functionality.
    2. **Functional Filtering:** IGNORE whitespace, imports, comments, and variable renames (refactoring). Focus ONLY on functional logic, API contracts, and business rules.
    3. **Confluence Section:** Identify the EXACT Section Header from the documentation.
    4. **Observation ID:** Assign a sequential ID (1, 2, 3...) to every row.
    5. **Combined Severity Logic:**
       - If a functional change violates the existing spec AND adds new behavior, use "NON-CONFORMANT / GAP".
    
    **Severity Definitions:**
    - 🔴 **NON-CONFORMANT:** Code change contradicts the existing documentation (Breaking Change).
    - 🟠 **GAP IDENTIFIED:** Code adds new functionality not covered in documentation.
    - 🔴 **NON-CONFORMANT / GAP:** Complex change violating spec AND adding features.
    - 🟡 **INCONSISTENCY:** Minor text or parameter description mismatch.
    - ✅ **CONFORMANT:** Change is purely internal refactoring or documentation matches new code.
    
    **Columns:**
    - **ID:** Sequential number.
    - **Severity:** (Use definitions above).
    - **Confluence Section:** The exact header from the docs.
    - **Impact Scope:** User Interface, System Logic, Data Processing, API Contract, Security.
    - **SWE.2 Observation (Functional):** Describe the functional gap clearly.
    - **Corrective Action:** Specific update to the Functional Specification.

    **Output Format:**
    Return ONLY a single Markdown table.
    """

    user_prompt = f"""
    FUNCTIONAL DOCUMENTATION (Confluence):
    {doc_content}

    ---
    
    GITHUB RELEASE DIFF (Changes between tags):
    {git_diff}
    """
    
    print("🧠 Running ASPICE SWE.2 Functional Consistency Check on Release...")
    
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

def save_report(content, filename="GitHub_Release_Impact_Report.md"):
    """
    Saves the report with Release Summary and Definitions.
    """
    with open(filename, "w", encoding="utf-8") as f:
        # 1. Main Title
        f.write("# ASPICE SWE.2 Release Impact Analysis\n\n")
        
        # 2. Release Info (Hardcoded for now, could be dynamic)
        f.write(f"**Release Comparison:** `{GITHUB_BASE_TAG}` → `{GITHUB_HEAD_TAG}`\n\n")
        
        # 3. Executive Summary
        f.write("## Executive Summary\n\n")
        f.write("This report details the functional discrepancies introduced by the code release changes.\n\n")
        f.write("---\n\n")
        
        # 4. Definitions
        f.write("## Assessment Criteria & Definitions\n\n")
        f.write("| Assessment Aspect | Definition |\n")
        f.write("| :--- | :--- |\n")
        f.write("| **Severity** | Risk level of the functional gap introduced by the release. |\n")
        f.write("| **Impact Scope** | The functional area affected (UI, Logic, Data, API, Security). |\n")
        f.write("\n### Severity Options\n\n")
        f.write("| Option | Definition |\n")
        f.write("| :--- | :--- |\n")
        f.write("| 🔴 **NON-CONFORMANT** | Code behavior contradicts the existing Functional Specification (Breaking Change). |\n")
        f.write("| 🟠 **GAP IDENTIFIED** | Code implements new functionality that is missing from the Specification. |\n")
        f.write("| 🔴 **NON-CONFORMANT / GAP** | A complex change that **both** violates the existing specification AND introduces new undocumented behavior. |\n")
        f.write("| 🟡 **INCONSISTENCY** | Minor discrepancies in parameter definitions or descriptions. |\n")
        f.write("| ✅ **CONFORMANT** | Functional behavior matches the specification accurately. |\n")
        f.write("\n---\n\n")
        
        # 5. LLM Analysis Content
        f.write("## Detailed Functional Analysis\n\n")
        f.write(content)
        
    print(f"✅ Report saved to {filename}")

def main():
    # 1. Initialize Clients
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return

    if not all([CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, PAGE_ID, 
                GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_BASE_TAG, GITHUB_HEAD_TAG]):
        print("❌ Error: Missing configuration in .env file.")
        return

    try:
        # 2. Fetch Docs
        doc_text = get_confluence_content(CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, PAGE_ID)
        
        # 3. Fetch GitHub Diff
        git_diff = get_github_diff(GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_BASE_TAG, GITHUB_HEAD_TAG, GITHUB_TOKEN)
        
        if git_diff:
            # 4. Analyze
            report_content = analyze_diff_with_confluence(client, AZURE_OPENAI_DEPLOYMENT, doc_text, git_diff)
            
            # 5. Save
            save_report(report_content)
        else:
            print("⚠️  No Diff found to analyze.")

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    main()

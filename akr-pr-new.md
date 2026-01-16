import os
import requests
import json
import re
import base64
import time

# --- Configuration from environment variables ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GH_PAT = os.environ.get("GH_PAT")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO_OWNER = os.environ.get("REPO_OWNER")
REPO_NAME = os.environ.get("REPO_NAME")
DOCS_REPO_NAME = os.environ.get("DOCS_REPO_NAME")

# --- API Endpoints ---
SOURCE_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
SOURCE_PR_URL = f"{SOURCE_API_URL}/pulls/{PR_NUMBER}"
DOCS_API_URL = f"https://api.github.com/repos/{DOCS_REPO_NAME}"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

# --- (Include all your existing helper functions here) ---
# For example: get_latest_open_pr_number, get_pr_diff_and_files, analyze_code_with_gemini
# I am including them below for completeness.

def get_latest_open_pr_number(repo_api_url, token):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    params = {"state": "open", "sort": "updated", "direction": "desc"}
    response = requests.get(f"{repo_api_url}/pulls", headers=headers, params=params)
    if response.status_code == 200 and response.json():
        return str(response.json()[0].get("number"))
    return None

def get_pr_diff_and_files():
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3.diff"}
    diff_response = requests.get(f"{SOURCE_PR_URL}.diff", headers=headers)
    if diff_response.status_code != 200: return None, None
    diff_text = diff_response.text
    changed_files = set(re.findall(r'diff --git a/.*? b/(.*?)\n', diff_text))
    return diff_text, changed_files

def analyze_code_with_gemini(diff):
    headers = {"Content-Type": "application/json"}
    if len(diff) > 30000: diff = diff[:30000] + "\n\n... (diff truncated)"
    
    prompt = f"""
    You are an expert senior Java developer specializing in Spring Boot. Review the following code diff and provide constructive feedback.
    CRITICAL RULES:
    1. Only provide feedback on the files explicitly shown in the provided diff.
    2. The "line" number for each issue MUST correspond to a line that was ADDED or MODIFIED in the diff.
    3. In addition to code review, identify any necessary documentation updates. Focus on API changes, new configuration properties, or breaking changes.
    Your response must be a single JSON object with the following keys: "summary", "issues", "suggestions", "documentation_updates".
    The "documentation_updates" should be an array of objects, each with "file_path", "action", and "content".
    If there are no updates, return empty arrays.
    Code diff to review: {diff}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
    for attempt in range(3):
        try:
            response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)
            if response.status_code == 200: break
            if response.status_code in [503, 429]:
                error_message = response.json().get("error", {}).get("message", "Unknown error")
                print(f"Attempt {attempt + 1}/3 failed with {response.status_code}: {error_message}. Retrying...")
                time.sleep(2 ** attempt)
                continue
            print(f"Failed to get response from Gemini: {response.status_code}"); return None
        except requests.exceptions.RequestException as e: print(f"Network error: {e}"); return None
    if response.status_code != 200: print("All retry attempts failed."); return None

    try:
        result = response.json()
        content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
        analysis = json.loads(content)
        if all(k in analysis for k in ["summary", "issues", "suggestions", "documentation_updates"]): return analysis
        else: return {"summary": "AI provided a JSON response with an unexpected structure.", "issues": [], "suggestions": [], "documentation_updates": [], "raw_response": content}
    except Exception as e: print(f"Error parsing Gemini response: {e}"); return None

def create_proposal_pr(docs_repo_name, pat_token, updates_json, original_pr_number):
    """Creates a proposal PR with the AI's JSON data in its description using only APIs."""
    print("--- Stage 1: Creating Proposal PR ---")
    api_base_url = f"https://api.github.com/repos/{docs_repo_name}"
    headers = {"Authorization": f"token {pat_token}", "Accept": "application/vnd.github.v3+json"}
    new_branch_name = f"ai-docs-update-for-pr-{original_pr_number}"
    
    try:
        # Get base commit SHA
        ref_response = requests.get(f"{api_base_url}/git/ref/heads/main", headers=headers)
        if ref_response.status_code != 200: return False
        base_commit_sha = ref_response.json()["object"]["sha"]

        # Create empty commit
        commit_response = requests.post(f"{api_base_url}/git/commits", headers=headers, json={
            "message": f"chore: Trigger documentation proposal for PR #{original_pr_number}",
            "parents": [base_commit_sha], "tree": requests.get(f"{api_base_url}/git/commits/{base_commit_sha}", headers=headers).json()["tree"]["sha"]
        })
        if commit_response.status_code != 201: return False
        new_commit_sha = commit_response.json()["sha"]

        # Create branch
        branch_response = requests.post(f"{api_base_url}/git/refs", headers=headers, json={"ref": f"refs/heads/{new_branch_name}", "sha": new_commit_sha})
        if branch_response.status_code != 201: return False

        # Create PR
        pr_body = f"### 🤖 AI-Generated Documentation Proposal\n\nThis PR contains an empty commit. The following JSON data contains the structured suggestions for the next automation step.\n\n```json\n{updates_json}\n```"
        pr_response = requests.post(f"{api_base_url}/pulls", headers=headers, json={
            "title": f"docs: [AI-Generated] Documentation proposal for PR #{original_pr_number}", "body": pr_body, "head": new_branch_name, "base": "main"
        })
        if pr_response.status_code == 201:
            print(f"✅ Proposal PR created: {pr_response.json()['html_url']}")
            return True
        return False
    except Exception as e: print(f"Error creating proposal PR: {e}"); return False

def apply_changes_and_create_final_pr(docs_repo_name, pat_token, updates, original_pr_number):
    """Applies file changes and creates a final PR using only APIs."""
    print("\n--- Stage 2: Applying Changes and Creating Final PR ---")
    api_base_url = f"https://api.github.com/repos/{docs_repo_name}"
    headers = {"Authorization": f"token {pat_token}", "Accept": "application/vnd.github.v3+json"}
    new_branch_name = f"apply-docs-from-pr-{original_pr_number}"

    try:
        # 1. Get base commit SHA from the main branch
        ref_response = requests.get(f"{api_base_url}/git/ref/heads/main", headers=headers)
        if ref_response.status_code != 200:
            print(f"❌ Failed to get base branch SHA: {ref_response.status_code}")
            return False
        base_commit_sha = ref_response.json()["object"]["sha"]
        
        # 2. Create a new branch from the base commit
        branch_response = requests.post(f"{api_base_url}/git/refs", headers=headers, json={
            "ref": f"refs/heads/{new_branch_name}",
            "sha": base_commit_sha
        })
        if branch_response.status_code != 201:
            print(f"❌ Failed to create new branch: {branch_response.status_code}")
            return False
        print(f"✅ Created new branch '{new_branch_name}'")

        # 3. Apply all file changes to the new branch
        for update in updates:
            file_path = update.get("file_path")
            content = update.get("content")
            if not file_path or not content:
                print(f"Skipping update due to missing file_path or content.")
                continue
            
            print(f"Updating file: {file_path}")
            file_data = {
                "message": f"docs: Update {file_path}",
                "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
                "branch": new_branch_name
            }
            # Check if file exists to get its SHA for an update
            get_resp = requests.get(f"{api_base_url}/contents/{file_path}", headers=headers, params={"ref": "main"})
            if get_resp.status_code == 200:
                file_data["sha"] = get_resp.json().get("sha")

            put_response = requests.put(f"{api_base_url}/contents/{file_path}", headers=headers, json=file_data)
            if put_response.status_code not in [200, 201]:
                print(f"❌ Failed to update file {file_path}: {put_response.status_code} - {put_response.text}")
                return False
        
        print("✅ All files updated successfully.")

        # 4. Create the final Pull Request
        pr_body = f"### 🤖 Applied Documentation Changes\n\nThis PR applies changes proposed for source PR #{original_pr_number}.\n\n**Modified Files:**\n"
        for update in updates: pr_body += f"- `{update.get('file_path', 'N/A')}`\n"
        
        pr_response = requests.post(f"{api_base_url}/pulls", headers=headers, json={
            "title": f"refactor: Apply documentation changes for PR #{original_pr_number}", "body": pr_body, "head": new_branch_name, "base": "main"
        })
        if pr_response.status_code == 201:
            print(f"✅ Final PR created: {pr_response.json()['html_url']}")
            return True
        else:
            print(f"❌ Failed to create final PR: {pr_response.status_code} - {pr_response.text}")
            return False

    except Exception as e:
        print(f"An error occurred during the apply process: {e}")
        return False

# --- Main Orchestration Function ---
def main():
    print("Starting automated LLM Code Review and Docs PR process...")
    
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number: pr_number = get_latest_open_pr_number(SOURCE_API_URL, GITHUB_TOKEN)
    if not pr_number: print("Could not determine PR number. Exiting."); return
    
    # Get PR details
    pr_details = requests.get(f"{SOURCE_PR_URL}", headers={"Authorization": f"token {GITHUB_TOKEN}"}).json()
    original_pr_author, original_pr_url = pr_details.get('user', {}).get('login'), pr_details.get('html_url')

    # Analyze code
    diff, _ = get_pr_diff_and_files()
    if not diff: print("Failed to get PR diff. Exiting."); return
    analysis = analyze_code_with_gemini(diff)
    if not analysis: print("Failed to analyze code. Exiting."); return
    
    # Post review comments to source PR (you can add this logic back in)
    # post_summary_comment(analysis, [])
    
    # Handle Documentation PRs
    doc_updates = analysis.get("documentation_updates", [])
    if doc_updates:
        updates_json = json.dumps(doc_updates, indent=2)
        
        # Stage 1: Create Proposal PR
        proposal_success = create_proposal_pr(DOCS_REPO_NAME, GH_PAT, updates_json, pr_number)
        
        # Stage 2: Apply Changes and Create Final PR
        if proposal_success:
            apply_changes_and_create_final_pr(DOCS_REPO_NAME, GH_PAT, doc_updates, pr_number)
    else:
        print("\nNo documentation updates were suggested by the AI.")

    print("Automated process completed.")

if __name__ == "__main__":
    main()

import os
import requests
import json
import re
import base64
import time
import subprocess
import shutil

# --- Configuration from environment variables ---
# For commenting on the source PR
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
# For writing to the docs repo
GH_PAT = os.environ.get("GH_PAT")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO_OWNER = os.environ.get("REPO_OWNER")
REPO_NAME = os.environ.get("REPO_NAME")
DOCS_REPO_NAME = os.environ.get("DOCS_REPO_NAME")
GENERATE_DOCS_PR = os.environ.get("GENERATE_DOCS_PR", "false").lower() == 'true'

# --- API Endpoints ---
# For the source repository
SOURCE_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
SOURCE_PR_URL = f"{SOURCE_API_URL}/pulls/{PR_NUMBER}"
# For the documentation repository
DOCS_API_URL = f"https://api.github.com/repos/{DOCS_REPO_NAME}"

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

# (Keep all your existing functions: get_pr_diff_and_files, analyze_code_with_gemini, etc.)
# For brevity, I am not repeating them here, but you MUST include them from the previous version.
# The analyze_code_with_gemini prompt should still ask for "documentation_updates".

def get_pr_diff_and_files():
    """Get the diff for the pull request and a set of changed files."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3.diff"}
    diff_response = requests.get(f"{SOURCE_PR_URL}.diff", headers=headers)
    if diff_response.status_code != 200:
        print(f"Failed to fetch PR diff: {diff_response.status_code}")
        return None, None
    diff_text = diff_response.text
    changed_files = set(re.findall(r'diff --git a/.*? b/(.*?)\n', diff_text))
    print(f"Found {len(changed_files)} changed files in the PR: {', '.join(changed_files)}")
    return diff_text, changed_files

def analyze_code_with_gemini(diff):
    """Send the diff to Gemini for analysis, with retries and enforced JSON output."""
    headers = {"Content-Type": "application/json"}
    max_length = 30000
    if len(diff) > max_length:
        diff = diff[:max_length] + "\n\n... (diff truncated for analysis)"
    
    prompt = f"""
    You are an expert senior Java developer specializing in Spring Boot. Review the following code diff and provide constructive feedback.

    CRITICAL RULES:
    1. Only provide feedback on the files explicitly shown in the provided diff.
    2. The "line" number for each issue MUST correspond to a line that was ADDED or MODIFIED in the diff.
    3. In addition to code review, identify any necessary documentation updates. Focus on API changes, new configuration properties, or breaking changes.

    Your response must be a single JSON object with the following keys:
    - "summary": A brief summary of the changes.
    - "issues": An array of issue objects (file, line, severity, message, suggestion).
    - "suggestions": An array of suggestion objects (file, line, message).
    - "documentation_updates": An array of documentation objects. Each object must have:
        - "file_path": The path to the documentation file to create or update (e.g., "docs/api/updates.md").
        - "action": Either "create" or "update".
        - "content": The full Markdown content for the new file or the section to be added.

    If there are no issues, suggestions, or documentation updates, return empty arrays for those keys.

    Code diff to review:
    {diff}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
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
        if all(k in analysis for k in ["summary", "issues", "suggestions", "documentation_updates"]):
            return analysis
        else: return {"summary": "AI provided a JSON response with an unexpected structure.", "issues": [], "suggestions": [], "documentation_updates": [], "raw_response": content}
    except Exception as e: print(f"Error parsing Gemini response: {e}"); return None

# --- NEW FUNCTIONS FOR INTERACTING WITH THE DOCS REPOSITORY ---

def run_git_command(command, cwd):
    """Runs a git command and returns its output."""
    try:
        result = subprocess.run(
            ["git"] + command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command {' '.join(command)}: {e.stderr}")
        return None

def create_docs_pr(doc_updates, original_pr_url, original_pr_author, base_branch):
    """Handles the entire process of creating a PR in the docs repository."""
    if not doc_updates:
        print("No documentation updates were suggested by the AI.")
        return

    print(f"\nFound {len(doc_updates)} documentation updates. Creating a new PR in '{DOCS_REPO_NAME}'...")
    
    # Define branch and PR details
    new_branch_name = f"ai-docs-update-for-pr-{PR_NUMBER}"
    pr_title = f"docs: [AI-Generated] Documentation updates for {REPO_NAME} PR #{PR_NUMBER}"
    
    # Standard PR Body
    pr_body = f"""
### 🤖 AI-Generated Documentation

This pull request was automatically generated by the LLM code review bot for **[{REPO_NAME} PR #{PR_NUMBER}]({original_pr_url})**.

#### Summary of Changes
The AI identified the following documentation updates as necessary:
"""
    for update in doc_updates:
        pr_body += f"- **`{update.get('file_path', 'N/A')}`**: {update.get('action', 'create').title()}d.\n"
    
    pr_body += f"""
#### Context
Please review the proposed documentation changes for accuracy and completeness. This PR aims to keep our documentation in sync with the codebase changes introduced in the original PR.

*Original PR Author: @{original_pr_author}*
    """
    
    # --- Git Operations ---
    temp_dir = None
    try:
        # 1. Clone the docs repository
        temp_dir = f"temp_docs_repo_{PR_NUMBER}"
        clone_url = f"https://{GH_PAT}@github.com/{DOCS_REPO_NAME}.git"
        run_git_command(["clone", clone_url, temp_dir], ".")
        
        # 2. Create and checkout a new branch
        run_git_command(["config", "user.name", "github-actions[bot]"], temp_dir)
        run_git_command(["config", "user.email", "github-actions[bot]@users.noreply.github.com"], temp_dir)
        run_git_command(["checkout", "-b", new_branch_name], temp_dir)
        
        # 3. Create/update all documentation files
        for update in doc_updates:
            file_path = os.path.join(temp_dir, update.get("file_path"))
            content = update.get("content")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w") as f:
                f.write(content)
            
            run_git_command(["add", file_path], temp_dir)
        
        commit_msg = f"feat: Add documentation updates for {REPO_NAME} PR #{PR_NUMBER}"
        run_git_command(["commit", "-m", commit_msg], temp_dir)
        
        # 4. Push the new branch to the remote docs repository
        run_git_command(["push", "origin", new_branch_name], temp_dir)
        
        # 5. Create the Pull Request via API
        print(f"Creating pull request from {new_branch_name} to {base_branch}")
        url = f"{DOCS_API_URL}/pulls"
        headers = {"Authorization": f"token {GH_PAT}", "Accept": "application/vnd.github.v3+json"}
        data = {"title": pr_title, "body": pr_body, "head": new_branch_name, "base": base_branch}
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            pr_data = response.json()
            print(f"✅ Documentation Pull Request created successfully: {pr_data['html_url']}")
        else:
            print(f"❌ Failed to create pull request: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"An error occurred during docs PR creation: {e}")
    finally:
        # 6. Clean up the temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")


def main():
    """Main function to orchestrate the code review process."""
    print("Starting LLM code review for Spring Boot project...")
    
    # Get details from the source repository
    pr_details_response = requests.get(SOURCE_PR_URL, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if pr_details_response.status_code != 200: print(f"Failed to get PR details: {pr_details_response.status_code}"); return
    commit_sha = pr_details_response.json().get('head', {}).get('sha')
    base_branch = pr_details_response.json().get('base', {}).get('ref')
    original_pr_author = pr_details_response.json().get('user', {}).get('login')
    original_pr_url = pr_details_response.json().get('html_url')

    diff, changed_files = get_pr_diff_and_files()
    if not diff or not changed_files: print("Failed to get PR diff or changed files. Exiting."); return
    
    print("Got PR diff, analyzing with Gemini...")
    analysis = analyze_code_with_gemini(diff)
    if not analysis: print("Failed to analyze code with Gemini. Exiting."); return
    
    print("Analysis complete. Posting review comments...")
    # (Keep your existing logic for posting inline comments and summary comment to the SOURCE PR here)
    # For example: post_summary_comment(analysis, out_of_scope_issues)
    
    # --- Handle Documentation PR Creation in the SEPARATE REPO ---
    if GENERATE_DOCS_PR:
        doc_updates = analysis.get("documentation_updates", [])
        create_docs_pr(doc_updates, original_pr_url, original_pr_author, base_branch)
    else:
        print("\nDocumentation PR generation is disabled.")

    print("LLM code review completed!")

if __name__ == "__main__":
    main()

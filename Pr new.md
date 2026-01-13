import os
import requests
import json
import base64

def create_docs_pr(
    docs_repo_name: str,
    pat_token: str,
    file_path: str,
    file_content: str,
    original_pr_number: str,
    base_branch: str = "main"
):
    """
    Creates a new branch, adds a file, and raises a pull request in a documentation repository
    using only the GitHub API.

    Args:
        docs_repo_name (str): The full name of the documentation repository (e.g., "my-org/my-project-docs").
        pat_token (str): A Personal Access Token with 'repo' scope.
        file_path (str): The path where the new file should be created (e.g., "docs/api-changes.md").
        file_content (str): The Markdown content for the new file.
        original_pr_number (str): The PR number to reference for uniqueness.
        base_branch (str, optional): The base branch to merge into. Defaults to "main".
    
    Returns:
        bool: True if the PR was created successfully, False otherwise.
    """
    print(f"--- Starting documentation PR process for repo: {docs_repo_name} ---")
    
    api_base_url = f"https://api.github.com/repos/{docs_repo_name}"
    headers = {"Authorization": f"token {pat_token}", "Accept": "application/vnd.github.v3+json"}

    new_branch_name = f"ai-docs-update-for-pr-{original_pr_number}"
    pr_title = f"docs: [AI-Generated] Documentation updates for PR #{original_pr_number}"
    
    pr_body = f"""
### 🤖 AI-Generated Documentation

This pull request was automatically generated based on an analysis of a recent code change.

#### Summary of Changes
A new documentation file has been proposed:
- **`{file_path}`**: Created.

Please review the proposed documentation for accuracy and completeness.
    """

    try:
        # 1. Get the SHA of the latest commit on the base branch
        print(f"Fetching latest commit SHA from branch '{base_branch}'...")
        ref_url = f"{api_base_url}/git/ref/heads/{base_branch}"
        ref_response = requests.get(ref_url, headers=headers)
        if ref_response.status_code != 200:
            print(f"❌ Failed to get base branch SHA: {ref_response.status_code} - {ref_response.text}")
            return False
        base_sha = ref_response.json()["object"]["sha"]
        print(f"Base SHA found: {base_sha}")

        # 2. Create a new branch from the base SHA
        print(f"Creating new branch '{new_branch_name}'...")
        branch_data = {"ref": f"refs/heads/{new_branch_name}", "sha": base_sha}
        branch_response = requests.post(f"{api_base_url}/git/refs", headers=headers, json=branch_data)
        if branch_response.status_code != 201:
            print(f"❌ Failed to create branch: {branch_response.status_code} - {branch_response.text}")
            return False
        print("Branch created successfully.")

        # 3. Create the new file on the new branch
        print(f"Creating file '{file_path}' on branch '{new_branch_name}'...")
        file_data = {
            "message": f"feat: Add documentation for PR #{original_pr_number}",
            "content": base64.b64encode(file_content.encode('utf-8')).decode('utf-8'),
            "branch": new_branch_name
        }
        file_url = f"{api_base_url}/contents/{file_path}"
        file_response = requests.put(file_url, headers=headers, json=file_data)
        if file_response.status_code not in [200, 201]: # 200 for update, 201 for create
            print(f"❌ Failed to create file: {file_response.status_code} - {file_response.text}")
            return False
        print("File created successfully.")

        # 4. Create the Pull Request via API
        print("Creating pull request via API...")
        pr_data = {
            "title": pr_title,
            "body": pr_body,
            "head": new_branch_name,
            "base": base_branch
        }
        pr_response = requests.post(f"{api_base_url}/pulls", headers=headers, json=pr_data)
        
        if pr_response.status_code == 201:
            pr_data = pr_response.json()
            print(f"✅ Documentation Pull Request created successfully: {pr_data['html_url']}")
            return True
        else:
            # Handle case where PR already exists
            if pr_response.status_code == 422 and "already exists" in pr_response.json().get("message", ""):
                print(f"ℹ️ A pull request for branch '{new_branch_name}' already exists. No new PR created.")
                return True # Consider this a success
            else:
                print(f"❌ Failed to create pull request: {pr_response.status_code} - {pr_response.text}")
                return False

    except Exception as e:
        print(f"An unexpected error occurred during docs PR creation: {e}")
        return False


# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # --- Replace these with your actual values for testing ---
    TEST_DOCS_REPO = "your-org/your-docs-repo"
    TEST_PAT = "ghp_YourPersonalAccessTokenHere"
    TEST_FILE_PATH = "docs/new-api-endpoint.md"
    TEST_FILE_CONTENT = """
# New User Endpoint

## Description
Adds a new endpoint to create a user.

## Endpoint
`POST /api/v1/users`
"""
    TEST_ORIGINAL_PR_NUM = "123"

    # To run this test, make sure you have a real PAT and a test docs repo.
    # Then, uncomment the line below.
    # create_docs_pr(TEST_DOCS_REPO, TEST_PAT, TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_ORIGINAL_PR_NUM)
    print("Example usage is commented out. Please fill in your test details and uncomment to run.")

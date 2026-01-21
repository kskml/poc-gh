import requests
import json
import getpass
import os
import base64

# --- CONFIGURATION ---
# TODO: Update these variables with your specific details

GITHUB_ENTERPRISE_URL = "https://domain"  # Your domain, without /api/v3
REPO_OWNER = "owner"
REPO_NAME = "repo"
BASE_BRANCH = "main"
HEAD_BRANCH = "feature/update-asciidoc-via-contents-api"

# --- Pull Request Details ---
PR_TITLE = "Automated PR: Update docs via Contents API"
PR_BODY = "This PR was created using the GitHub Contents API to avoid blob creation issues."

# --- Files to be included in the Pull Request ---
# Define each file you want to add/update.
# Set 'is_binary' to True for images, PDFs, zips, etc.
MODIFIED_FILES = [
    {"path": "docs/guide.adoc", "is_binary": False},
    # {"path": "images/logo.png", "is_binary": True},
]

# --- END OF CONFIGURATION ---


def get_api_session(token: str) -> requests.Session:
    """Creates and returns a requests session with GitHub API headers."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    })
    return session

def handle_response(response: requests.Response):
    """Checks for API errors and returns JSON response."""
    if response.status_code == 404:
        print("\n--- 404 Not Found Error ---")
        print(f"Request URL was: {response.url}")
        print("Please check your GITHUB_ENTERPRISE_URL, REPO_OWNER, and REPO_NAME.")
        print("---------------------------\n")
        response.raise_for_status()

    if response.status_code >= 400:
        try:
            error_data = response.json()
            error_message = error_data.get('message', 'Unknown API error')
            print(f"Error: {response.status_code} - {error_message}")
            if 'errors' in error_data:
                for err in error_data['errors']:
                    print(f"  - {err.get('message', '')}")
        except json.JSONDecodeError:
            print(f"Error: {response.status_code} - {response.text}")
        response.raise_for_status()
    return response.json()

def get_latest_commit_sha(session: requests.Session, base_branch: str) -> str:
    """Step 1: Get the SHA of the latest commit on the base branch."""
    print(f"\nStep 1: Getting latest commit SHA for branch '{base_branch}'...")
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{base_branch}"
    response = session.get(url)
    data = handle_response(response)
    commit_sha = data['object']['sha']
    print(f"   Latest commit SHA: {commit_sha}")
    return commit_sha

def create_or_update_branch(session: requests.Session, branch_name: str, commit_sha: str):
    """Step 2: Create the new branch and point it to the new commit."""
    print(f"\nStep 2: Creating/updating branch '{branch_name}'...")
    ref_data = {"ref": f"refs/heads/{branch_name}", "sha": commit_sha}
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/git/refs"
    
    # Try to create the branch. If it fails with 422, it might already exist.
    response = session.post(url, data=json.dumps(ref_data))
    if response.status_code == 422:
        print(f"   Branch '{branch_name}' already exists. No need to create it.")
    else:
        handle_response(response) # Will raise an error for other issues
        print(f"   ✅ Branch '{branch_name}' created successfully.")
    
def update_files_via_contents_api(session: requests.Session, files_config: list, branch_name: str):
    """Step 3: Update files on the new branch using the Contents API."""
    print(f"\nStep 3: Updating files on branch '{branch_name}' via Contents API...")
    
    for file_info in files_config:
        file_path = file_info["path"]
        is_binary = file_info.get("is_binary", False)
        full_path = os.path.abspath(file_path)

        if not os.path.exists(full_path):
            print(f"   ❌ ERROR: File not found at '{full_path}'. Skipping.")
            continue
        
        print(f"\n   Processing file: {file_path}")
        
        # Read file content
        with open(full_path, 'rb') as f:
            content_bytes = f.read()

        if is_binary:
            content_to_upload = base64.b64encode(content_bytes).decode('utf-8')
            encoding = "base64"
        else:
            content_to_upload = content_bytes.decode('utf-8', errors='replace')
            encoding = "utf-8"
        
        # To update a file, we need its current SHA. Let's try to get it.
        # If the file doesn't exist, this will fail, and we'll know to create it.
        file_sha = None
        get_url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
        try:
            get_response = session.get(get_url, params={"ref": branch_name})
            if get_response.status_code == 200:
                file_sha = handle_response(get_response)['sha']
                print(f"   -> Found existing file with SHA: {file_sha}")
        except requests.exceptions.HTTPError:
            print(f"   -> File '{file_path}' does not exist on branch '{branch_name}'. Will create it.")

        # Prepare the PUT request payload
        put_payload = {
            "message": f"Automated commit: Update {file_path}",
            "content": content_to_upload,
            "branch": branch_name
        }
        if file_sha:
            put_payload["sha"] = file_sha

        # Make the PUT request to create/update the file
        put_url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
        response = session.put(put_url, data=json.dumps(put_payload))
        result = handle_response(response)
        print(f"   ✅ Successfully updated/created file. Commit SHA: {result['commit']['sha']}")


def create_pull_request(session: requests.Session, head_branch: str, base_branch: str, title: str, body: str):
    """Step 4: Create the Pull Request."""
    print("\nStep 4: Creating the Pull Request...")
    pr_data = {"title": title, "body": body, "head": head_branch, "base": base_branch}
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    response = session.post(url, data=json.dumps(pr_data))
    pr_info = handle_response(response)
    pr_url = pr_info['html_url']
    print("\n----------------------------------------------------")
    print(f"✅ Success! Pull Request created.")
    print(f"   View it here: {pr_url}")
    print("----------------------------------------------------")


def main():
    print("--- GitHub Enterprise PR Creator (Contents API Version) ---")
    token = getpass.getpass("Enter your GitHub Personal Access Token: ")
    session = get_api_session(token)
    
    try:
        # 1. Get the starting point from the base branch
        latest_commit_sha = get_latest_commit_sha(session, BASE_BRANCH)
        
        # 2. Create the new branch
        create_or_update_branch(session, HEAD_BRANCH, latest_commit_sha)
        
        # 3. Update files on the new branch (the new method)
        update_files_via_contents_api(session, MODIFIED_FILES, HEAD_BRANCH)
        
        # 4. Create the Pull Request
        create_pull_request(session, HEAD_BRANCH, BASE_BRANCH, PR_TITLE, PR_BODY)

    except requests.exceptions.RequestException as e:
        print(f"\nAn API request failed: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

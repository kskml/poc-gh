import requests
import json
import getpass
import os

# --- CONFIGURATION ---
# TODO: Update these variables with your specific details

# The base URL of your GitHub Enterprise instance.
# e.g., 'https://github.mycompany.com'
GITHUB_ENTERPRISE_URL = "https://github.mycompany.com" 

# The repository owner and name.
# e.g., for 'https://github.mycompany.com/my-org/my-repo', owner is 'my-org' and name is 'my-repo'.
REPO_OWNER = "your-org"
REPO_NAME = "your-repo"

# The branch you want to merge your changes INTO.
BASE_BRANCH = "main"

# The name for the NEW branch that will contain your changes.
# It's good practice to make this unique.
HEAD_BRANCH = "feature/my-new-changes-from-api"

# --- Pull Request Details ---
PR_TITLE = "Automated PR: Add new feature from script"
PR_BODY = """
This pull request was created automatically by a Python script.

It includes the following changes:
- Updated the README.md file.
- Added a new configuration file.

Please review the changes before merging.
"""

# --- Files to be included in the Pull Request ---
# TODO: List the paths of the files you have modified locally.
# The script will read these files from your current directory.
MODIFIED_FILES = [
    "README.md",
    "config/new_settings.json"
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
        response.raise_for_status()  # This will raise an HTTPError
    return response.json()

def get_latest_commit_sha(session: requests.Session, base_branch: str) -> str:
    """Step 1: Get the SHA of the latest commit on the base branch."""
    print(f"Step 1: Getting latest commit SHA for branch '{base_branch}'...")
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{base_branch}"
    response = session.get(url)
    data = handle_response(response)
    commit_sha = data['object']['sha']
    print(f"   Latest commit SHA: {commit_sha}")
    return commit_sha

def create_blobs_for_files(session: requests.Session, file_paths: list) -> dict:
    """Step 2: Create a blob for each modified file's content."""
    print("\nStep 2: Creating blobs for modified files...")
    file_blobs = {}
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"   Warning: File '{file_path}' not found. Skipping.")
            continue
        
        print(f"   Processing file: {file_path}")
        with open(file_path, 'rb') as f:
            # The API expects content to be base64 encoded for binary files or UTF-8 for text.
            # We'll read as text, assuming source files. For true binary files, use base64.
            content = f.read().decode('utf-8', errors='replace')

        blob_data = {
            "content": content,
            "encoding": "utf-8"
        }
        url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs"
        response = session.post(url, data=json.dumps(blob_data))
        blob_sha = handle_response(response)['sha']
        file_blobs[file_path] = blob_sha
        print(f"     -> Created blob with SHA: {blob_sha}")
    return file_blobs

def create_new_tree(session: requests.Session, base_commit_sha: str, file_blobs: dict) -> str:
    """Step 3: Create a new tree with the updated file blobs."""
    print("\nStep 3: Creating a new Git tree...")
    
    # First, get the base tree SHA from the base commit
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{base_commit_sha}"
    response = session.get(url)
    base_tree_sha = handle_response(response)['tree']['sha']
    print(f"   Base tree SHA: {base_tree_sha}")

    # Prepare the tree items for the modified files
    tree_items = []
    for path, blob_sha in file_blobs.items():
        tree_items.append({
            "path": path,
            "mode": "100644",  # Represents a regular file (blob)
            "type": "blob",
            "sha": blob_sha
        })

    tree_data = {
        "base_tree": base_tree_sha,
        "tree": tree_items
    }
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/git/trees"
    response = session.post(url, data=json.dumps(tree_data))
    new_tree_sha = handle_response(response)['sha']
    print(f"   New tree created with SHA: {new_tree_sha}")
    return new_tree_sha

def create_new_commit(session: requests.Session, base_commit_sha: str, new_tree_sha: str, message: str) -> str:
    """Step 4: Create a new commit."""
    print("\nStep 4: Creating a new commit...")
    commit_data = {
        "message": message,
        "parents": [base_commit_sha],
        "tree": new_tree_sha
        # You can also add author/committer details here if needed
    }
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/git/commits"
    response = session.post(url, data=json.dumps(commit_data))
    new_commit_sha = handle_response(response)['sha']
    print(f"   New commit created with SHA: {new_commit_sha}")
    return new_commit_sha

def create_or_update_branch(session: requests.Session, branch_name: str, commit_sha: str):
    """Step 5: Create the new branch and point it to the new commit."""
    print(f"\nStep 5: Creating/updating branch '{branch_name}'...")
    ref_data = {
        "ref": f"refs/heads/{branch_name}",
        "sha": commit_sha
    }
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/git/refs"
    response = session.post(url, data=json.dumps(ref_data))
    # A 422 error here might mean the branch already exists, so we try to update it.
    if response.status_code == 422:
        print(f"   Branch '{branch_name}' might already exist. Attempting to update...")
        update_url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{branch_name}"
        update_data = {"sha": commit_sha, "force": False}
        response = session.patch(update_url, data=json.dumps(update_data))
    
    handle_response(response)
    print(f"   Branch '{branch_name}' now points to commit {commit_sha}.")

def create_pull_request(session: requests.Session, head_branch: str, base_branch: str, title: str, body: str):
    """Step 6: Create the Pull Request."""
    print("\nStep 6: Creating the Pull Request...")
    pr_data = {
        "title": title,
        "body": body,
        "head": head_branch,
        "base": base_branch
    }
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    response = session.post(url, data=json.dumps(pr_data))
    pr_info = handle_response(response)
    pr_url = pr_info['html_url']
    print("\n----------------------------------------------------")
    print(f"✅ Success! Pull Request created.")
    print(f"   View it here: {pr_url}")
    print("----------------------------------------------------")


def main():
    """Main function to orchestrate the PR creation process."""
    print("--- GitHub Enterprise PR Creator ---")
    
    # 1. Authenticate
    token = getpass.getpass("Enter your GitHub Personal Access Token: ")
    session = get_api_session(token)
    
    # 2. Execute the workflow
    try:
        # Get the starting point from the base branch
        latest_commit_sha = get_latest_commit_sha(session, BASE_BRANCH)

        # Create blobs for the content of your modified files
        file_blobs = create_blobs_for_files(session, MODIFIED_FILES)
        if not file_blobs:
            print("\nNo valid files were processed. Aborting PR creation.")
            return

        # Create a new tree that includes the new blobs
        new_tree_sha = create_new_tree(session, latest_commit_sha, file_blobs)

        # Create a new commit that points to the new tree
        new_commit_sha = create_new_commit(session, latest_commit_sha, new_tree_sha, PR_TITLE)

        # Create a new branch that points to the new commit
        create_or_update_branch(session, HEAD_BRANCH, new_commit_sha)

        # Finally, create the pull request
        create_pull_request(session, HEAD_BRANCH, BASE_BRANCH, PR_TITLE, PR_BODY)

    except requests.exceptions.RequestException as e:
        print(f"\nAn API request failed: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

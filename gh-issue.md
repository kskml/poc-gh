import requests
import json
import os

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------

# For GitHub Enterprise Server, change this to your API endpoint (e.g., "https://github.yourcompany.com/api/v3")
# For GitHub.com, leave as is.
GITHUB_API_BASE_URL = "https://api.github.com" 

# Replace with your repository details
REPO_OWNER = "your-organization-or-username"
REPO_NAME = "your-repository-name"

# Best practice: Load the token from an environment variable for security
GITHUB_TOKEN = os.getenv("GITHUB_PAT")

# -------------------------------------------------------------------------
# FUNCTION DEFINITION
# -------------------------------------------------------------------------

def create_github_issue(title, body=None, assignees=None, labels=None):
    """
    Creates an issue in a GitHub repository.
    
    :param title: (str) The title of the issue.
    :param body: (str, optional) The body content of the issue.
    :param assignees: (list, optional) List of usernames to assign.
    :param labels: (list, optional) List of label strings.
    :return: The JSON response from the API if successful.
    """
    
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_PAT environment variable is not set.")

    # Construct the API URL
    url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues"

    # Prepare Headers
    # We include 'Accept' for v3 compatibility and the API version header for modern stability
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Prepare Payload
    payload = {
        "title": title
    }
    
    if body:
        payload["body"] = body
    if assignees:
        payload["assignees"] = assignees
    if labels:
        payload["labels"] = labels

    try:
        # Make the POST request
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload)
        )

        # Check for successful creation (HTTP 201 Created)
        if response.status_code == 201:
            print(f"Issue created successfully!")
            return response.json()
        else:
            # Handle errors (4xx or 5xx)
            print(f"Failed to create issue. Status: {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# -------------------------------------------------------------------------
# EXECUTION
# -------------------------------------------------------------------------

if __name__ == "__main__":
    # Example Usage
    issue_title = "Test Issue via Python API"
    issue_body = """
    This issue was created automatically using Python scripts.
    
    - Details here
    - More details here
    """
    issue_labels = ["bug", "high-priority"]
    issue_assignees = ["your-username"] # Ensure this user exists in the repo

    create_github_issue(
        title=issue_title, 
        body=issue_body, 
        labels=issue_labels,
        assignees=issue_assignees
    )

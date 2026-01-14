import requests
import json

def create_docs_pr(
    docs_repo_name: str,
    pat_token: str,
    proposed_content: str,
    original_pr_number: str,
    base_branch: str = "main"
):
    """
    Creates a new branch with an empty commit and a pull request in a documentation repository.
    The proposed documentation content is placed in the PR description. No files are created.

    Args:
        docs_repo_name (str): The full name of the documentation repository (e.g., "my-org/my-project-docs").
        pat_token (str): A Personal Access Token with 'repo' scope.
        proposed_content (str): The Markdown content for the proposed documentation.
        original_pr_number (str): The PR number to reference for uniqueness.
        base_branch (str, optional): The base branch to merge into. Defaults to "main".
    
    Returns:
        bool: True if the PR was created successfully, False otherwise.
    """
    print(f"--- Starting documentation PR process for repo: {docs_repo_name} ---")
    
    api_base_url = f"https://api.github.com/repos/{docs_repo_name}"
    headers = {"Authorization": f"token {pat_token}", "Accept": "application/vnd.github.v3+json"}

    new_branch_name = f"ai-docs-update-for-pr-{original_pr_number}"
    pr_title = f"docs: [AI-Generated] Documentation proposal for PR #{original_pr_number}"
    
    pr_body = f"""
### 🤖 AI-Generated Documentation Proposal

This pull request was automatically generated based on an analysis of a recent code change.

This PR contains an empty commit to enable its creation. No files have been changed in this repository.

#### Proposed Documentation Content
Please review the following Markdown content for potential inclusion in the documentation:

```markdown
{proposed_content}

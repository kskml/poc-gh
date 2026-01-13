import os
import requests
import json
import re
import base64
import time

# Configuration
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO_OWNER = os.environ.get("REPO_OWNER")
REPO_NAME = os.environ.get("REPO_NAME")

# Retry Configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY_SECONDS = 2

# GitHub API endpoints
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
PR_URL = f"{GITHUB_API_URL}/pulls/{PR_NUMBER}"
COMMENTS_URL = f"{GITHUB_API_URL}/pulls/{PR_NUMBER}/comments"

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

def get_pr_diff_and_files():
    """Get the diff for the pull request and a set of changed files."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    
    diff_response = requests.get(f"{PR_URL}.diff", headers=headers)
    if diff_response.status_code != 200:
        print(f"Failed to fetch PR diff: {diff_response.status_code}")
        return None, None
    
    diff_text = diff_response.text
    changed_files = set(re.findall(r'diff --git a/.*? b/(.*?)\n', diff_text))
    
    print(f"Found {len(changed_files)} changed files in the PR: {', '.join(changed_files)}")
    return diff_text, changed_files

def analyze_code_with_gemini(diff):
    """Send the diff to Gemini for analysis, with retries and enforced JSON output."""
    headers = {
        "Content-Type": "application/json",
    }
    
    max_length = 30000
    if len(diff) > max_length:
        diff = diff[:max_length] + "\n\n... (diff truncated for analysis)"
    
    # --- REVISED PROMPT WITH STRICTER LINE NUMBER INSTRUCTIONS ---
    prompt = f"""
    You are an expert senior Java developer specializing in Spring Boot. Review the following code diff and provide constructive feedback.

    CRITICAL RULES:
    1. Only provide feedback on the files explicitly shown in the provided diff.
    2. The "line" number for each issue or suggestion MUST correspond to a line that was ADDED or MODIFIED in the diff. Do not reference deleted lines or lines that were not changed. If you cannot find a suitable line, omit the "line" field from your JSON object.

    Focus on:
    1.  Spring Boot Best Practices (e.g., constructor injection, correct annotations).
    2.  Java Code Quality (e.g., SOLID principles, null safety).
    3.  Security (e.g., SQL injection, input validation).
    4.  Performance (e.g., N+1 queries).
    5.  Error Handling (e.g., @ControllerAdvice).

    Your response must be a JSON object with the following keys: "summary", "issues", "suggestions".
    The "issues" and "suggestions" should be arrays of objects, where each object contains "file", "line" (optional but recommended), "message", and for issues, also "severity" and "suggestion".
    
    If there are no issues or suggestions, return empty arrays.

    Code diff to review:
    {diff}
    """
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                print("Successfully received response from Gemini.")
                break
            
            if response.status_code in [503, 429]:
                error_message = response.json().get("error", {}).get("message", "Unknown error")
                print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed with {response.status_code}: {error_message}")
                if attempt < MAX_RETRIES - 1:
                    delay = INITIAL_RETRY_DELAY_SECONDS * (2 ** attempt)
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
            
            print(f"Failed to get response from Gemini: {response.status_code}")
            print(response.text)
            return None

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed with a network error: {e}")
            if attempt < MAX_RETRIES - 1:
                delay = INITIAL_RETRY_DELAY_SECONDS * (2 ** attempt)
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            else:
                return None
    
    if response.status_code != 200:
        print("All retry attempts failed.")
        return None

    try:
        result = response.json()
        content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
        analysis = json.loads(content)
        
        if "summary" in analysis and "issues" in analysis and "suggestions" in analysis:
            return analysis
        else:
            print("Warning: Parsed JSON does not have the expected structure. Returning raw response.")
            return {
                "summary": "AI provided a JSON response with an unexpected structure.",
                "issues": [],
                "suggestions": [],
                "raw_response": content
            }

    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON response even with MIME type enforcement: {e}")
        return {
            "summary": "AI provided a response that could not be parsed as JSON.",
            "issues": [],
            "suggestions": [],
            "raw_response": result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No content found')
        }
    except Exception as e:
        print(f"An unexpected error occurred during parsing: {e}")
        return None

def is_line_valid_in_pr(file_path, line_number, commit_sha):
    """Check if a file and line number exist in a specific commit."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    file_url = f"{GITHUB_API_URL}/contents/{file_path}?ref={commit_sha}"
    
    try:
        response = requests.get(file_url, headers=headers)
        if response.status_code != 200:
            return False
        
        file_content_b64 = response.json().get("content")
        if not file_content_b64:
            return False
            
        file_content = base64.b64decode(file_content_b64).decode('utf-8')
        lines = file_content.splitlines()
        if 1 <= line_number <= len(lines):
            return True
        else:
            return False

    except Exception:
        return False

# --- UPDATED FUNCTION WITH GRACEFUL 422 HANDLING ---
def post_comment_to_pr(file_path, line, message, commit_sha):
    """Post a comment to a specific line in the PR, handling validation errors."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "body": message,
        "commit_id": commit_sha,
        "path": file_path,
        "line": line
    }
    
    response = requests.post(COMMENTS_URL, headers=headers, json=payload)
    
    if response.status_code == 201:
        return True

    # --- GRACEFUL ERROR HANDLING ---
    if response.status_code == 422:
        error_json = response.json()
        error_message = error_json.get("errors", [{}])[0].get("message", "Unknown validation error")
        print(f"Warning: Could not post comment on {file_path}:{line}. GitHub API says: '{error_message}'. Skipping.")
    else:
        print(f"Failed to post comment on {file_path}:{line}. Status: {response.status_code}")
        print(response.text)
        
    return False

def post_summary_comment(analysis, out_of_scope_issues):
    """Post a summary comment to the PR."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    summary = analysis.get("summary", "No summary provided")
    issues = analysis.get("issues", [])
    suggestions = analysis.get("suggestions", [])
    raw_response = analysis.get("raw_response")

    comment_body = f"## 🤖 AI Code Review (Spring Boot)\n\n"
    
    if raw_response:
        comment_body += f"**Note:** The AI response could not be parsed as JSON. Here is the raw review:\n\n```\n{raw_response}\n```"
    else:
        comment_body += f"**Summary:** {summary}\n\n"
        if issues:
            comment_body += "### 🚨 Issues Found\n\n"
            for issue in issues:
                severity_emoji = {"low": "🔵", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(issue.get("severity", "low"), "⚪")
                comment_body += f"{severity_emoji} **{issue.get('severity', 'low').title()}** - {issue.get('message', 'No message')}\n"
                comment_body += f"- **File:** `{issue.get('file', 'unknown')}` (Line {issue.get('line', 'unknown')})\n"
                comment_body += f"- **Suggestion:** {issue.get('suggestion', 'No suggestion')}\n\n"
        
        if suggestions:
            comment_body += "### 💡 Suggestions\n\n"
            for suggestion in suggestions:
                comment_body += f"- **File:** `{suggestion.get('file', 'unknown')}` (Line {suggestion.get('line', 'unknown')})\n"
                comment_body += f"- **Suggestion:** {suggestion.get('message', 'No message')}\n\n"

        if out_of_scope_issues:
            comment_body += "### 📄 General Suggestions (Out of PR Scope)\n\n"
            comment_body += "The following suggestions were made for files not modified in this PR. Please review them manually:\n\n"
            for item in out_of_scope_issues:
                comment_body += f"- **File:** `{item.get('file', 'unknown')}` (Line {item.get('line', 'unknown')})\n"
                comment_body += f"- **Message:** {item.get('message', 'No message')}\n\n"
        
        if not issues and not suggestions and not out_of_scope_issues:
            comment_body += "No issues or suggestions found. The code looks good! 👍"
    
    existing_comments_url = f"{GITHUB_API_URL}/issues/{PR_NUMBER}/comments"
    existing_comments_response = requests.get(existing_comments_url, headers=headers)
    if existing_comments_response.status_code != 200:
        return False
        
    existing_comments = existing_comments_response.json()
    bot_comment_id = None
    for comment in existing_comments:
        if comment.get("user", {}).get("type") == "Bot" and "AI Code Review (Spring Boot)" in comment.get("body", ""):
            bot_comment_id = comment.get("id")
            break
    
    if bot_comment_id:
        update_url = f"{GITHUB_API_URL}/issues/comments/{bot_comment_id}"
        response = requests.patch(update_url, headers=headers, json={"body": comment_body})
        if response.status_code != 200:
            return False
    else:
        response = requests.post(existing_comments_url, headers=headers, json={"body": comment_body})
        if response.status_code != 201:
            return False
    
    return True

def main():
    """Main function to orchestrate the code review process."""
    print("Starting LLM code review for Spring Boot project...")
    
    pr_details_response = requests.get(PR_URL, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if pr_details_response.status_code != 200:
        print(f"Failed to get PR details for commit SHA: {pr_details_response.status_code}")
        return
    commit_sha = pr_details_response.json().get('head', {}).get('sha')
    print(f"Using commit SHA: {commit_sha}")

    diff, changed_files = get_pr_diff_and_files()
    if not diff or not changed_files:
        print("Failed to get PR diff or changed files. Exiting.")
        return
    
    print("Got PR diff, analyzing with Gemini...")
    
    analysis = analyze_code_with_gemini(diff)
    if not analysis:
        print("Failed to analyze code with Gemini. Exiting.")
        return
    
    print("Analysis complete, posting comments...")
    
    out_of_scope_items = []
    
    if not analysis.get("raw_response"):
        all_items = analysis.get("issues", []) + analysis.get("suggestions", [])
        for item in all_items:
            file_path = item.get("file")
            line = item.get("line")

            if not file_path:
                print(f"Skipping item due to missing file path: {item}")
                continue

            if file_path not in changed_files:
                print(f"Skipping inline comment for file not in PR diff: {file_path}")
                out_of_scope_items.append(item)
                continue
            
            # If line is not provided, we can't post an inline comment.
            if not line:
                print(f"Skipping item for {file_path} due to missing line number.")
                continue

            try:
                line_num = int(line)
            except (ValueError, TypeError):
                print(f"Skipping item for {file_path} due to invalid line number '{line}'.")
                continue
            
            # We still check for validity, but the main protection is the try/catch in post_comment_to_pr
            if not is_line_valid_in_pr(file_path, line_num, commit_sha):
                print(f"Skipping comment on invalid line: {file_path}:{line_num}")
                continue
            
            message = f"**{item.get('severity', 'Suggestion').title()}** - {item.get('message', 'No message')}\n\n**Suggestion:** {item.get('suggestion', 'No suggestion')}"
            post_comment_to_pr(file_path, line_num, message, commit_sha)
    
    post_summary_comment(analysis, out_of_scope_items)
    
    print("LLM code review completed!")

if __name__ == "__main__":
    main()

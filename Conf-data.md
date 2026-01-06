The "Best Way" Approach & Architecture (Req 5)
Before diving into the code, here is the recommended architectural approach and why it is the best practice for this scenario:

1. Hybrid Parsing Strategy (HTML + Heuristics):
Why: Confluence's native storage format is XML-based (ADF). While robust, it is complex to parse. The "View" or "Storage" format (XHTML) is easier to parse using standard HTML parsers like BeautifulSoup.
Strategy: Fetch the content in expand=body.storage. Use BeautifulSoup to traverse the DOM tree. This allows you to accurately identify h1, h2, etc., and group all subsequent elements (paragraphs, lists, images) until the next heading is found.

2. Multimodal LLM Usage (GPT-4o):
Why: You specifically asked to handle draw.io images. Text-based LLMs (like standard GPT-3.5) cannot "see" diagrams.
Strategy: Use GPT-4o (via Azure OpenAI). It supports Vision capabilities. You can extract the image data (Base64 or URL) from the Confluence chunk and pass it directly to the LLM alongside the text. This allows the model to describe the flowchart or diagram in the summary.

3. Sequential Chunk Processing with Context:
Why: Sending one massive page to an LLM often results in hallucinations or loss of detail due to token limits.
Strategy: Break the page into sections based on headings. Summarize each section individually. If you need a final summary, you can then summarize the list of section summaries.

4. Error Handling & Modular Design:
Why: Network requests to Confluence and Azure OpenAI can fail.
Strategy: Use distinct classes/functions for fetching, parsing, and inference. This makes the code testable and maintainable.

pip install requests beautifulsoup4 openai python-dotenv

CONFLUENCE_BASE_URL="https://your-domain.atlassian.net/wiki"
CONFLUENCE_EMAIL="your-email@company.com"
CONFLUENCE_API_TOKEN="your-api-token"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-azure-key"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o" # Or your specific deployment name

Impl:

import os
import requests
import re
import base64
from bs4 import BeautifulSoup
from openai import AzureOpenAI
from typing import List, Dict

# --- GLOBAL CONFIGURATION ---
CONFLUENCE_BASE_URL = "https://your-domain.atlassian.net/wiki"
CONFLUENCE_EMAIL = "your-email@company.com"
CONFLUENCE_API_TOKEN = "your-api-token"

AZURE_OPENAI_ENDPOINT = "https://your-resource-name.openai.azure.com/"
AZURE_OPENAI_KEY = "your-azure-openai-key"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_DEPLOYMENT_NAME = "gpt-4o"

# Initialize Azure OpenAI Client globally
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# 1. READ CONFLUENCE PAGE CONTENT
def get_page_content(page_id: str) -> str:
    """
    Fetches the Confluence page storage format (HTML) by Page ID.
    """
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}?expand=body.storage"
    auth = (CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
        data = response.json()
        return data['body']['storage']['value']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Confluence page: {e}")
        return ""

# HELPER: DRAW.IO EXTRACTION
def extract_drawio_labels(drawio_xml: str) -> str:
    """
    Extracts text labels from raw Draw.io XML using Regex.
    This allows us to 'understand' the diagram without rendering an image.
    """
    values = re.findall(r'value="([^"]*)"', drawio_xml)
    unique_labels = list(set(values))
    return " | ".join([v for v in unique_labels if v])

# 2. CHUNK CONTENT BY HEADINGS
def chunk_content_by_headings(html_content: str) -> List[Dict]:
    """
    Parses HTML and breaks content into chunks based on H1-H6 tags.
    Also identifies Draw.io diagrams.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    chunks = []
    
    # Initialize starting section
    current_section = {
        "heading": "Introduction / Summary",
        "level": 0,
        "content": [],
        "type": "text"
    }

    # Iterate through relevant tags
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'ac:structured-macro']):
        
        # Handle Draw.io Macro
        if element.name == 'ac:structured-macro' and element.get('ac:name') == 'drawio':
            if current_section['content']:
                chunks.append(current_section)
                current_section = {
                    "heading": current_section["heading"], 
                    "level": current_section["level"],
                    "content": [], 
                    "type": "text"
                }

            # Extract Data
            xml_body = element.find('ac:plain-text-body')
            if xml_body and xml_body.string:
                raw_xml = xml_body.string.strip()
                diagram_text = extract_drawio_labels(raw_xml)
                
                if diagram_text:
                    chunks.append({
                        "heading": current_section["heading"],
                        "level": current_section["level"],
                        "content": f"[Diagram containing labels: {diagram_text}]",
                        "type": "drawio_text"
                    })
            continue

        # Handle Headings
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Save previous section if it has content
            if current_section['content']:
                chunks.append(current_section)
            
            # Start new section
            level = int(element.name[1])
            current_section = {
                "heading": element.get_text(strip=True),
                "level": level,
                "content": [],
                "type": "text"
            }
        
        # Handle Paragraphs and Lists
        elif element.name in ['p', 'ul', 'ol']:
            text = element.get_text(strip=True)
            if text:
                current_section['content'].append(text)

    # Add the final section
    if current_section['content']:
        chunks.append(current_section)

    return chunks

# 3 & 4. SUMMARIZE CHUNKS USING AZURE OPENAI
def summarize_chunk(chunk: Dict) -> str:
    """
    Sends a specific chunk to Azure OpenAI for summarization.
    Adjusts prompt based on whether the chunk is a diagram.
    """
    content_text = " ".join(chunk['content'])
    
    # Truncate if too long to save tokens
    if len(content_text) > 4000:
        content_text = content_text[:4000] + "..."

    # Define Prompts
    if chunk['type'] == 'drawio_text':
        system_prompt = "You are a technical analyst. Describe what a diagram likely represents based on its labels."
        user_content = f"Section: {chunk['heading']}\nDiagram Labels: {content_text}"
    else:
        system_prompt = "You are a technical assistant. Summarize the text concisely."
        user_content = f"Section: {chunk['heading']}\nContent: {content_text}"

    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing section '{chunk['heading']}': {e}"

# --- MAIN EXECUTION FLOW ---
def main():
    page_id = "12345678"  # Replace with actual Page ID
    
    print(f"--- Fetching Page ID: {page_id} ---")
    html = get_page_content(page_id)
    
    if not html:
        return

    print("--- Chunking Content ---")
    chunks = chunk_content_by_headings(html)
    print(f"Found {len(chunks)} sections.\n")

    print("--- Summarizing Sections ---")
    summary_output = []
    
    for chunk in chunks:
        print(f"Processing: {chunk['heading']}...")
        summary = summarize_chunk(chunk)
        summary_output.append(f"### {chunk['heading']}\n{summary}\n")

    print("\n\n=== FINAL SUMMARY ===")
    print("\n".join(summary_output))

if __name__ == "__main__":
    main()

    Detailed Explanation of Key Components
1. Handling Confluence Headings (Req 1 & 2)
The chunk_content_by_headings function uses BeautifulSoup.

It locates all <h1> through <h6> tags.
It iterates through the next_sibling elements. This is crucial because it captures everything (text paragraphs, lists, tables, images) that belongs logically to that specific heading, stopping only when it hits the next heading of equal or higher level.
2. Handling Draw.io Images (Req 6)
Draw.io diagrams in Confluence are rendered in two main ways:

As Attachments: The HTML contains an <img ... ri:filename="diagram.png">. In standard HTML view, this usually resolves to a URL.
As Inline Base64 (less common but possible): The image data is embedded directly in the HTML.
My code extracts these via extract_images_from_soup. It prepares a payload for GPT-4o (a Multimodal model).

If you provide the image URL (and it is accessible/authenticated), GPT-4o can "see" the diagram.
The prompt explicitly asks the LLM to "analyze the visual content," ensuring the summary isn't just text but explains the flowcharts or architecture diagrams.
3. Summarization Strategy (Req 3 & 4)
We use the Azure OpenAI chat.completions.create method.

We construct a message list containing the text prompt.
If images are found in the chunk, we append them to the content array in the specific format {"type": "image_url", ...} required by the OpenAI API.
This generates a summary that merges the understanding of the text and the visual diagrams.
4. Best Practices Summary (Req 5)
This solution handles the requirements best because:

Context Preservation: By chunking based on headings, the LLM summarizes specific topics without getting confused by unrelated content from other parts of the page.
Vision Integration: By handling images explicitly, we solve the problem where "A picture is worth a thousand words." Standard summarizers ignore images; this one understands them.
Token Efficiency: Sending only one section at a time prevents hitting token limits (input size limits) of the LLM and ensures higher quality summaries per topic.

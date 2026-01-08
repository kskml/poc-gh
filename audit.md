import os
import glob
from dotenv import load_dotenv

# LangChain Imports
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
SOURCE_CODE_DIR = "./repo/source_code"
ASCII_DOC_DIR = "./repo/ascii_docs"
CHROMA_DB_DIR = "./chroma_db_storage"
REPORTS_DIR = "./reports"

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Deployment names (Must match your Azure resources)
EMBEDDING_DEPLOYMENT_NAME = "text-embedding-ada-002"
CHAT_DEPLOYMENT_NAME = "gpt-4" # or gpt-35-turbo

# -------------------------------------------------------------------------
# INITIALIZATION
# -------------------------------------------------------------------------

def initialize_azure_clients():
    """Initialize and return the Embeddings and LLM clients."""
    print("[*] Initializing Azure OpenAI clients...")
    
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=EMBEDDING_DEPLOYMENT_NAME,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY
    )
    
    llm = AzureChatOpenAI(
        azure_deployment=CHAT_DEPLOYMENT_NAME,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        temperature=0.1 # Low temperature for precise validation
    )
    
    return embeddings, llm

# -------------------------------------------------------------------------
# INDEXING (INGESTION)
# -------------------------------------------------------------------------

def load_and_split_code_files():
    """Load all code files and split them into chunks."""
    documents = []
    file_types = ['*.py', '*.js', '*.java', '*.ts', '*.cs']
    
    print(f"[*] Loading source code from {SOURCE_CODE_DIR}...")
    
    for ext in file_types:
        # Recursive search for files
        files = glob.glob(os.path.join(SOURCE_CODE_DIR, "**", ext), recursive=True)
        for file in files:
            try:
                loader = TextLoader(file, autodetect_encoding=True)
                documents.extend(loader.load())
            except Exception as e:
                print(f"[!] Warning: Could not load {file}: {e}")
    
    if not documents:
        raise FileNotFoundError("No source code documents found in the specified directory.")

    # Split code into manageable chunks
    # This helps with context window management and precise retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\nclass ", "\ndef ", "\nfunction ", "\n\n", "\n", " ", ""]
    )
    
    splits = text_splitter.split_documents(documents)
    print(f"[*] Source code split into {len(splits)} chunks.")
    return splits

def get_or_create_vectorstore(embeddings):
    """
    Load existing ChromaDB or create a new one from source code.
    Returns: Chroma VectorStore
    """
    if os.path.exists(CHROMA_DB_DIR):
        print("[*] Found existing ChromaDB. Loading index...")
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR, 
            embedding=embeddings
        )
        return vectorstore
    else:
        print("[*] No existing DB found. Indexing source code...")
        splits = load_and_split_code_files()
        print("[*] Creating embeddings and storing in ChromaDB...")
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings,
            persist_directory=CHROMA_DB_DIR
        )
        return vectorstore

# -------------------------------------------------------------------------
# VALIDATION LOGIC
# -------------------------------------------------------------------------

def create_validation_prompt(doc_section, code_snippets):
    """Constructs the prompt for the LLM."""
    return f"""
    You are an expert Software Architect and Documentation Auditor.
    
    TASK:
    Compare the provided 'DOCUMENTATION SECTION' against the 'RETRIEVED SOURCE CODE'.
    
    1. Verify if the documentation accurately reflects the code logic, inputs, outputs, and behavior.
    2. If the documentation is missing information, outdated, or incorrect, identify the gap.
    3. If a gap exists, provide the corrected documentation text.
    
    DOCUMENTATION SECTION:
    ---
    {doc_section}
    ---
    
    RETRIEVED SOURCE CODE (Relevant sections):
    ---
    {code_snippets}
    ---
    
    OUTPUT FORMAT (Strict):
    - Status: [ALIGNED / GAP FOUND]
    - Reasoning: [Brief explanation]
    - Proposed Change: [The corrected markdown/text if gap found, otherwise 'None']
    """

def save_report(file_path, analysis_results):
    """Write the validation report to a markdown file."""
    # Create output directory if it doesn't exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Generate filename
    filename = os.path.basename(file_path)
    out_name = filename.replace(".adoc", "_report.md").replace(".md", "_report.md")
    out_path = os.path.join(REPORTS_DIR, out_name)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Validation Report for {filename}\n\n")
        f.write(f"**Source File:** {file_path}\n\n")
        f.write("---\n\n")
        
        for idx, result in enumerate(analysis_results):
            f.write(f"## Issue #{idx + 1}\n")
            f.write(f"**Section Preview:** {result['section_preview']}\n\n")
            f.write(f"**Analysis:**\n{result['analysis']}\n\n")
            f.write("---\n\n")
            
    print(f"    [*] Report saved to {out_path}")

def process_documentation_file(file_path, vectorstore, llm):
    """
    Process a single documentation file:
    1. Split doc.
    2. Retrieve code (RAG).
    3. Validate with LLM.
    4. Save Report if issues found.
    """
    print(f"[*] Validating: {file_path}")
    
    # Load Doc
    loader = TextLoader(file_path, autodetect_encoding=True)
    docs = loader.load()
    
    # Split Doc (by headers or generic text)
    doc_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, 
        chunk_overlap=100,
        separators=["\n== ", "\n## ", "\n\n", "\n", ". ", " "]
    )
    chunks = doc_splitter.split_documents(docs)
    
    # Setup Retriever (Top 3 code chunks per doc section to manage context)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    issues_found = []
    
    for i, chunk in enumerate(chunks):
        doc_text = chunk.page_content
        
        # 1. Retrieve relevant code
        try:
            retrieved_docs = retriever.invoke(doc_text)
            code_context = "\n\n".join([d.page_content for d in retrieved_docs])
            
            # 2. Generate Prompt
            prompt = create_validation_prompt(doc_text, code_context)
            
            # 3. Ask LLM
            response = llm.invoke(prompt)
            response_content = response.content
            
            # 4. Check for Gap
            if "GAP FOUND" in response_content:
                issues_found.append({
                    "section_preview": doc_text[:100].replace("\n", " ") + "...",
                    "analysis": response_content
                })
                print(f"    [!] Gap detected in section {i+1}.")
            else:
                print(f"    [+] Section {i+1} aligned.")
                
        except Exception as e:
            print(f"    [!] Error processing section {i+1}: {e}")

    # Save report only if gaps were found
    if issues_found:
        save_report(file_path, issues_found)

def run_validation_process(vectorstore, llm):
    """Orchestrates the validation of all documentation files."""
    print(f"[*] Starting validation process...")
    
    # Find all documentation files
    doc_files = []
    doc_files.extend(glob.glob(os.path.join(ASCII_DOC_DIR, "**", "*.adoc"), recursive=True))
    doc_files.extend(glob.glob(os.path.join(ASCII_DOC_DIR, "**", "*.md"), recursive=True))
    
    if not doc_files:
        print("[!] No documentation files found.")
        return

    print(f"[*] Found {len(doc_files)} documentation files.")
    
    for doc_file in doc_files:
        process_documentation_file(doc_file, vectorstore, llm)

# -------------------------------------------------------------------------
# MAIN ENTRY POINT
# -------------------------------------------------------------------------

def main():
    load_dotenv()
    
    try:
        # 1. Setup Clients
        embeddings, llm = initialize_azure_clients()
        
        # 2. Load or Create Vector Store (RAG Index)
        vectorstore = get_or_create_vectorstore(embeddings)
        
        # 3. Validate Documentation against Code
        run_validation_process(vectorstore, llm)
        
        print("\n[*] Validation complete. Check the './reports' folder for details.")
        
    except Exception as e:
        print(f"[!] Critical Error: {e}")

if __name__ == "__main__":
    main()

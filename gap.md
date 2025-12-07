 Approaches for Code-Documentation Gap Analysis
Here are the potential approaches, with their pros and cons, specifically considering the context window limitations of LLMs.

| Approach | Description | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **1. Monolithic Analysis** | Concatenate the entire codebase and all documentation into a single, massive prompt. | The LLM has complete context, potentially identifying subtle cross-module gaps. | **Impractical.** Will exceed the token limit of even the most advanced models (e.g., GPT-4 Turbo's 128k) for any non-trivial project. |
| **2. Naive Chunking** | Split all files (code and docs) into arbitrary chunks based on file size or alphabetical order. Send each chunk to the LLM. | Simple to implement. Guarantees staying within the token limit. | **Destroys semantic context.** A `user_controller.py` file might be analyzed without its corresponding `user_model.py` or `user_guide.md`, leading to a high rate of false negatives (missing gaps). |
| **3. RAG (Retrieval-Augmented Generation)** | Index all code and documentation files into a vector database. For each file, retrieve the most semantically similar other files to provide as context. | Very powerful. Can find non-obvious relationships based on semantic similarity, not just structure. | **High complexity.** Requires setting up and maintaining a vector database (e.g., ChromaDB, Pinecone), an embedding step, and a more complex query pipeline. Might be overkill for this specific task. |
| **4. Hybrid Semantic Chunking (Recommended)** | First, understand the repository structure (directories, imports). Group related files together (e.g., all files for the "authentication" module). Then, chunk these *semantically coherent groups* to fit the token limit. | **Best of both worlds.** Maintains logical context by keeping related files together, while still respecting the token limit. It mimics how a human would perform this review. | More complex to implement than naive chunking, as it requires parsing the codebase structure. |

Recommended Approach: Hybrid Semantic Chunking
This approach is the most effective because it balances the need for comprehensive analysis with the practical constraints of LLM context windows.

Why it's best:

Context Preservation: 
By analyzing related files together (e.g., a service, its model, and its corresponding documentation), the LLM can accurately identify discrepancies.
Scalability: It works for projects of any size by breaking them down into manageable, logical units.
Efficiency: It avoids the overhead of a full RAG system while still being significantly more intelligent than naive chunking.

The Algorithm Explained
The process follows a clear, multi-step pipeline:

Repository Checkout: 
The GitHub Action checks out both the source code repository and the documentation repository into separate directories.

Structure Extraction: 
The Python script walks the code repository to build a mental model of its structure. It identifies:
All directories and files.
For Python files, it uses the ast module to parse import statements, creating a dependency graph (e.g., auth_service.py imports user_model.py).

Semantic Grouping:
Files are initially grouped by their parent directory.
The algorithm then refines these groups by merging them if files in one group import files from another. For example, if src/controllers/ files import src/models/ files, these two directories might be merged into a single analysis group.

Intelligent Chunking:
For each semantic group, the algorithm calculates the total token count.
If the group is too large, it creates chunks.
Large File Handling: If a single file is too large (e.g., a 5,000-line file), it's split intelligently. For Python, it's split at function and class boundaries. For other files, it's split by lines, ensuring no single part exceeds the limit.
Small File Aggregation: Smaller files are combined into chunks until the token limit is reached, maximizing context in each API call.

LLM Analysis (Azure OpenAI):
Each chunk is sent to Azure OpenAI with a carefully engineered prompt.
The prompt defines what constitutes a "gap" (e.g., missing documentation, outdated documentation, undocumented features) and asks for a structured JSON response.
The JSON includes the gap type, severity (critical, high, medium, low), the file path, a description, and a suggested change.

Result Synthesis:
The script collects all the JSON results from every chunk.
It merges them, removes duplicate recommendations, and sorts all identified gaps by severity.

Report Generation:
The synthesized results are formatted into a clean, human-readable Markdown report.
The GitHub Action then creates a new issue in the repository, posting this report for the development team to review.

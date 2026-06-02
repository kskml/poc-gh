Part 1: Idea & Setup Configuration
1.1 The Core Idea
Your GitHub Action currently runs as a black box. By integrating the Langfuse SDK, you wrap your pipeline in a Trace, its steps in Spans, and your LLM calls in Generations. This captures prompts, completions, token usage, latency, and errors—giving you full visibility without changing your business logic.

1.2 Architecture & Data Flow Diagrams

flowchart LR
    subgraph GitHub [GitHub Actions Runner]
        A[PR Event Trigger] --> B(Python Pipeline Script)
        B --> C{Langfuse SDK}
    end

    subgraph Langfuse [Self-Hosted Langfuse]
        D[Ingestion API]
        E[(PostgreSQL)]
        F[Web Dashboard]
    end

    C -- HTTPS POST /public/traces --> D
    D --> E
    F --> E

GitHub Repository Secrets:

Secret Name
Value
LANGFUSE_PUBLIC_KEY	pk-lf-...
LANGFUSE_SECRET_KEY	sk-lf-...
LANGFUSE_HOST	https://langfuse.yourcompany.com

Part 2: High Level Overview
2.1 Langfuse Data Model Mapping
Langfuse Concept
Automation Mapping
Why it matters
Trace	One complete pipeline run per PR	Groups all steps; measures total latency and cost
Span	Non-LLM steps (API calls, parsing)	Tracks latency and success of infrastructure steps
Generation	LLM calls (Gap analysis, deep-dives)	Captures exact prompt, completion, model, and token cost
Score	Assessment result, gap count	Enables filtering and trend analysis in the dashboard
Session	The PR number	Groups multiple runs on the same PR (e.g., new commits pushed)
User	The PR author	Allows tracking which developers trigger the most architectural gaps


2.2 The CI/CD Flushing Problem
The Langfuse SDK sends data asynchronously. In a web app, background threads flush data over time. In GitHub Actions, the process terminates abruptly when the workflow finishes.

If you don't flush, traces are lost.

We solve this by:

Setting flush_at=1 (send immediately, no batching).
Calling langfuse.flush() in a finally block before the script exits.


2.3 Context Propagation
By using the @observe decorator on the main pipeline function, the SDK creates a root Trace and stores it in langfuse_context. Any nested function using @observe or manually calling langfuse_context will automatically nest under that root Trace, creating the parent-child hierarchy shown in the Mermaid diagram above.

langfuse==2.57.0
python-dotenv==1.0.1

3.2 src/observability.py (Langfuse Initialization & Helpers)
import os
import functools
from langfuse import Langfuse
from langfuse.decorators import langfuse_context


# ─── Singleton Client ────────────────────────────────────────────────

_langfuse_client = None


def get_langfuse_client() -> Langfuse:
    """
    Initialize and return the Langfuse client as a singleton.
    Configured specifically for CI/CD environments.
    """
    global _langfuse_client
    if _langfuse_client is None:
        host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

        _langfuse_client = Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=host,
            
            # CI CRITICAL: Flush immediately, don't batch.
            # The GitHub Action process will terminate abruptly,
            # background batching threads will die before sending.
            flush_at=1,
            flush_interval=1,
            
            # Self-hosted instances may need longer timeouts
            request_timeout=30,
            
            # Toggle off for local dev/testing without Langfuse
            enabled=os.environ.get("LANGFUSE_ENABLED", "true").lower() == "true",
            
            # SSL verification (set to false ONLY for self-signed dev certs)
            verify_ssl=os.environ.get("LANGFUSE_VERIFY_SSL", "true").lower() == "true",
            
            # Map Git SHA to Langfuse Release for version tracking
            release=os.environ.get("GITHUB_SHA", "unknown"),
            
            # CI context automatically attached to every trace
            metadata={
                "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
                "github_run_number": os.environ.get("GITHUB_RUN_NUMBER", ""),
                "github_ref": os.environ.get("GITHUB_REF", ""),
                "github_repository": os.environ.get("GITHUB_REPOSITORY", ""),
                "github_actor": os.environ.get("GITHUB_ACTOR", ""),
                "github_event_name": os.environ.get("GITHUB_EVENT_NAME", ""),
                "deployment": "self-hosted" if "cloud.langfuse.com" not in host else "cloud",
            },
        )
    return _langfuse_client


def flush_langfuse():
    """
    CRITICAL: Must be called before the process exits.
    Ensures all async telemetry data is sent to the Langfuse server.
    """
    client = get_langfuse_client()
    client.flush()
    print("[Langfuse] All traces flushed successfully.")


# ─── Custom Decorator for Non-LLM Spans ──────────────────────────────

def traced(name: str = None, metadata: dict = None, **kwargs):
    """
    Decorator for tracing non-LLM operations (API calls, parsing, etc.).
    Creates a span within the current trace context.
    """
    def decorator(func):
        span_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **fkwargs):
            client = get_langfuse_client()

            try:
                # Nest under existing trace if available
                current_trace = langfuse_context.get_current_trace()
                span = current_trace.span(
                    name=span_name,
                    metadata=metadata or {},
                    **kwargs,
                )
            except Exception:
                # Fallback if no trace context exists (e.g., isolated testing)
                trace = client.trace(
                    name=span_name,
                    metadata=metadata or {},
                    **kwargs,
                )
                span = trace.span(name=span_name)

            try:
                result = func(*args, **fkwargs)
                span.end(output=result)
                return result
            except Exception as e:
                span.end(output={"error": str(e)}, level="ERROR")
                raise

        return wrapper
    return decorator


     LANGFUSE_PUBLIC_KEY: ${{ secrets.LANGFUSE_PUBLIC_KEY }}
          LANGFUSE_SECRET_KEY: ${{ secrets.LANGFUSE_SECRET_KEY }}
          LANGFUSE_HOST: ${{ secrets.LANGFUSE_HOST }}
          LANGFUSE_ENABLED: "true"
          LANGFUSE_VERIFY_SSL: "true"

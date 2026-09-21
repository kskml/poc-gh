# Prompt Compression for Large Language Models — A Comprehensive Reference

> **Audience**: ML engineers, applied researchers, and backend engineers building production LLM applications.
> **Scope**: Survey of methods, benchmarks, libraries, vendor offerings, and practical integration patterns.
> **Last updated**: September 2026. References include content published through Q3 2026.
> **Author note**: This document aggregates publicly available information from arXiv, conference proceedings, vendor documentation, and open-source repositories. All sources are linked inline and consolidated in the final reference section.

---

## Table of Contents

1. [Introduction & Motivation](#1-introduction--motivation)
2. [Taxonomy of Approaches](#2-taxonomy-of-approaches)
3. [Hard Prompt Methods (Token-Level)](#3-hard-prompt-methods-token-level)
4. [Soft Prompt / Representation-Level Methods](#4-soft-prompt--representation-level-methods)
5. [KV Cache Compression & Eviction](#5-kv-cache-compression--eviction)
6. [Summarization & Recap-Based Methods](#6-summarization--recap-based-methods)
7. [Retrieval-Oriented Compression](#7-retrieval-oriented-compression)
8. [Agent & Long-Term Memory Approaches](#8-agent--long-term-memory-approaches)
9. [Vendor-Hosted Prompt / Context Caching](#9-vendor-hosted-prompt--context-caching)
10. [Benchmarks & Evaluation](#10-benchmarks--evaluation)
11. [Open-Source Libraries & Tooling](#11-open-source-libraries--tooling)
12. [Code Examples](#12-code-examples)
13. [Practical Decision Guide](#13-practical-decision-guide)
14. [Cost & Latency Impact — Real-World Numbers](#14-cost--latency-impact--real-world-numbers)
15. [Open Problems & Future Directions](#15-open-problems--future-directions)
16. [Consolidated Reference List](#16-consolidated-reference-list)

---

## 1. Introduction & Motivation

### 1.1 Why prompt compression matters

Modern LLM applications routinely push prompts past 32k, 128k, and even 1M tokens. Examples include retrieval-augmented generation (RAG) over large corpora, agentic workflows that accumulate tool-call transcripts, code assistants that carry entire repositories as context, and document-QA systems that ingest whole PDFs. The cost of this growth is severe and multi-dimensional:

- **Compute cost**: Transformer attention is O(n²) in sequence length during prefill, and every cached token must be re-read at each generation step. Doubling the prompt roughly quadruples prefill FLOPs.
- **Latency**: Time-to-first-token (TTFT) grows linearly (or worse) with prompt length. For interactive products, TTFT > 2 seconds triggers noticeable UX degradation.
- **Context-window pressure**: Even on 1M-token models (Gemini 1.5/2.5 Pro), real applications hit the ceiling quickly once tool transcripts, retrieved chunks, and conversation history accumulate.
- **Memory footprint**: KV cache for a 70B model at 128k context can exceed 40 GB of GPU memory per concurrent request. This is often the binding constraint on throughput, not the model weights.
- **Quality degradation**: Long contexts are not just expensive — they degrade accuracy. The "lost in the middle" phenomenon (Liu et al., 2024) shows LLMs disproportionately attend to the start and end of long inputs, missing facts buried in the middle.

Prompt compression addresses all four problems simultaneously by reducing the number of tokens (or KV entries) the model actually has to process, while attempting to preserve task-relevant information.

### 1.2 Definition

**Prompt compression** is the family of techniques that transform an input prompt *x* = (x_doc, x_query) into a shorter representation *x′* such that:

1. |x′| < |x| (often 2×–20× smaller), and
2. The downstream LLM's task performance on *x′* is close to its performance on *x*.

The representation *x′* may be:
- A subset of original tokens (**hard prompt**, e.g., LLMLingua).
- A sequence of learned embedding vectors (**soft prompt**, e.g., ICAE, Gist).
- A reduced KV cache inside the model (**KV eviction**, e.g., H2O, SnapKV, StreamingLLM).
- A natural-language summary (**recap**, e.g., mem0, AutoCompressor's summary tokens).
- A prefix that has been pre-computed and cached at the provider (**provider-side caching**, e.g., Anthropic, OpenAI, Gemini).

### 1.3 The information-theoretic view

The fundamental question is: how much information from *x* is task-relevant? A 2024 paper from DeepComm introduces a rate-distortion framework to analyze this trade-off formally, showing that prompt compression is bounded by the mutual information between the prompt and the task, not by the prompt's raw entropy. In practice this means:

- Compression ratios of 2×–10× are achievable with minimal performance loss for factoid QA.
- Compression beyond ~20× almost always requires task-aware (query-conditioned) methods, otherwise retrieval accuracy collapses on needle-in-haystack tasks.
- "Lossless" prompt compression (preserving every retrievable fact) has a much lower ceiling than "lossy but task-aware" compression.

This insight drives the modern preference for **query-aware** methods (LongLLMLingua, SnapKV's observation window, CompAct) over earlier query-agnostic ones.

### 1.4 Production adoption signals

By Q3 2026, prompt compression has moved from arXiv to production:

- Anthropic reports up to **90% cost reduction** and **85% latency reduction** from prompt caching on Claude.
- A 2026 industry survey by PointFive lists "Top 10 Prompt Compression Solutions" as a real product category, including vendor-funded deployments saving upwards of $200k/month per customer.
- All three major API providers (OpenAI, Anthropic, Google) now offer some form of built-in prompt or context caching, removing the need for client-side compression in many use cases.

---

## 2. Taxonomy of Approaches

The literature can be organized along two orthogonal axes: **where compression happens** (input-token space, embedding space, or KV-cache space) and **what it is conditioned on** (query-aware vs query-agnostic).

### 2.1 By representation space

| Family | Operates on | Output | Typical ratio | Examples |
|---|---|---|---|---|
| **Hard prompt** | Token sequence | Subset of original tokens | 2×–20× | LLMLingua, LLMLingua-2, Selective Context |
| **Soft prompt** | Embedding space | Learned vectors prepended to embeddings | 10×–100× | ICAE, Gist, AutoCompressor, ATACompressor |
| **KV-cache eviction** | Model's KV state | Trimmed KV cache during inference | 2×–8× memory | H2O, SnapKV, StreamingLLM, RefreshKV, Ada-KV |
| **Recap / summarization** | Token sequence (rewritten) | New shorter tokens | 3×–10× | AutoCompressor (recursive), CompAct, mem0 |
| **Retrieval-time filtering** | Retrieved documents | Filtered / re-ranked subset | varies | LangChain ContextualCompressionRetriever, LlamaIndex LongLLMLingua |
| **Provider-side caching** | Prefix at vendor | Same tokens, billed less | 1× tokens, ~10× cheaper | Anthropic prompt caching, OpenAI implicit caching, Gemini context cache |

### 2.2 By conditioning signal

- **Query-agnostic** (compression happens before seeing the user query): LLMLingua (original), Selective Context, StreamingLLM, H2O. Faster, simpler, but cannot adapt to what the user is actually asking.
- **Query-aware** (compression is conditioned on the query): LongLLMLingua, SnapKV (via observation window), CompAct, ATACompressor. Better accuracy at high compression ratios, at the cost of an extra forward pass or retrieval step.

### 2.3 By training requirement

- **Training-free** (drop-in at inference): LLMLingua, LLMLingua-2, Selective Context, H2O, SnapKV, StreamingLLM. Most popular in production because they work with any black-box LLM.
- **Requires fine-tuning** (must train a compressor model): ICAE, Gist, AutoCompressor, ATACompressor. Higher ceiling but you must train and ship the compressor alongside the LLM.

### 2.4 By where the compressor runs

- **Client-side** (you compress before calling the API): LLMLingua, LangChain ContextualCompressionRetriever, mem0. Works with any LLM provider, including open-weights models.
- **Provider-side** (the vendor caches internally): Anthropic prompt caching, OpenAI implicit caching, Gemini context caching. Zero code changes but lock-in to that vendor and only useful when prefixes repeat.

The next sections walk through each family in detail.

---

## 3. Hard Prompt Methods (Token-Level)

Hard prompt methods produce a shorter sequence of *real tokens* drawn from the original prompt. They are the most production-friendly family because the compressed prompt is still a string and can be fed to any LLM API.

### 3.1 LLMLingua (Jiang et al., 2023)

**Core idea**: Use a small language model (GPT-2 small or LLaMA-7B) to compute per-token perplexity, then drop tokens whose removal causes the smallest increase in perplexity of the *remaining* prompt. Uses a coarse-to-fine algorithm: first compress at the demonstration/example level, then within each example at the token level.

**Key claims**: Up to **20× compression** with minimal performance loss across reasoning, QA, and retrieval tasks. Black-box compatible (works with GPT-3.5/4, Claude, etc. without modifying them).

**Where to read**:
- Project site: <https://llmlingua.com/>
- Microsoft Research page: <https://www.microsoft.com/en-us/research/project/llmlingua/>
- PyPI: <https://pypi.org/project/llmlingua/>
- Documentation site: <https://microsoft.github.io/LLMLingua/>

### 3.2 LongLLMLingua (Jiang et al., 2023)

**Core idea**: Extends LLMLingua to be **query-aware**. The small LM's perplexity is conditioned on the question, so tokens that are not relevant to *this specific question* are pruned more aggressively. Also introduces a "post-recovery" step that re-injects key tokens into the prompt.

**Key claims**: At **4× compression**, achieves **17.1% performance improvement** on average across LongBench tasks (i.e., compression actually helps, by reducing noise the LLM would otherwise attend to). This is the basis of the popular "prompt compression for RAG" integration in LlamaIndex.

**Where to read**:
- LlamaIndex integration guide: <https://www.llamaindex.ai/blog/longllmlingua-prompt-compression-tutorial>
- Microsoft Research summary (same page as LLMLingua)

### 3.3 LLMLingua-2 (Pan et al., 2024)

**Core idea**: Replaces the perplexity-based heuristic with a **classification-based** approach. A small BERT-style encoder is trained to predict, for each token, whether it should be kept or dropped. This is faster than computing perplexity (one forward pass instead of one per token) and gives a precise compression budget.

**Key claims**: Achieves 2×–10× compression with quality on par with or better than LLMLingua, while running **~10× faster** at inference time (the compressor itself is fast enough to call per request without measurable overhead).

**Where to read**:
- Microsoft Research: <https://www.microsoft.com/en-us/research/project/llmlingua/>
- Code & models: <https://github.com/microsoft/LLMLingua>
- PyPI: <https://pypi.org/project/llmlingua/>

### 3.4 Selective Context (Li et al., 2023)

**Core idea**: The earliest published token-level compressor. Uses a small LM to compute **self-information** of each lexical unit (token, sentence, or paragraph) and filters out units below a threshold. Predates LLMLingua and is simpler — no coarse-to-fine iteration, no query conditioning in the original paper.

**Key claims**: ~2× compression with minimal loss on document-QA tasks. Predates and inspired LLMLingua's design.

**Where to read**:
- Paper (ACL 2023 Findings): <https://aclanthology.org/2023.findings-acl.111/>
- GitHub: <https://github.com/liyongsea/Selective-Context>
- Cited ~483 times as of 2026

### 3.5 Limitations of hard-prompt methods

Hard-prompt methods share two limitations that motivate the soft-prompt family:

1. **Hard ceiling**: Once you drop a token, the LLM can never recover that information. There is no way to "summarize" multiple tokens into one — you only delete.
2. **Token boundaries**: They can only keep or drop whole tokens, never merge adjacent similar tokens. This is fine for English prose but wasteful for code (where many tokens are highly redundant) and JSON.

---

## 4. Soft Prompt / Representation-Level Methods

Soft-prompt methods learn to map a chunk of text into a fixed number of **continuous embedding vectors** ("gist tokens", "memory slots") that the LLM consumes as if they were token embeddings. The compressed prompt is not human-readable, but is much shorter (often 10×–100×).

### 4.1 Gist Tokens (Mu et al., NeurIPS 2023)

**Core idea**: Fine-tune an LLM to "summarize" a prompt into a fixed small number of *gist token* activations. During inference, the gist tokens are computed once per prompt and reused. The fine-tuning objective is essentially: "make the LLM behave as if it had seen the full prompt".

**Key claims**: Up to **26× compression**, with ~**40% FLOPs reduction** and ~4% wall-time speedup on the models they tested.

**Where to read**:
- NeurIPS page: <https://neurips.cc/virtual/2023/poster/71193>
- Follow-up extending gisting to long contexts: GistPool (Semantic Scholar entry)

### 4.2 ICAE — In-Context Autoencoder (Ge et al., ICLR 2024)

**Core idea**: Train an encoder (initialized from the target LLM) to compress a long context into a small set of "memory slot" vectors. The target LLM is then conditioned on these slots instead of the original tokens. Training uses a combination of autoencoder reconstruction loss and an adversarial / LLM-as-judge loss that pushes the slots to be *useful* for downstream tasks.

**Key claims**: Compresses long contexts into memory slots for efficient LLM inference; validated on long-context QA tasks.

**Where to read**:
- arXiv: <https://arxiv.org/abs/2307.06945>
- GitHub: <https://github.com/getao/icae>
- Microsoft Research page (Ge et al. are MSRA researchers): <https://www.microsoft.com/en-us/research/project/in-context-autoencoder/>

### 4.3 AutoCompressor (Chevalier et al., 2023, Princeton)

**Core idea**: Recursively compresses long context. Text is split into chunks, each chunk is summarized into "summary tokens", and then the summary tokens of multiple chunks are themselves summarized, producing a hierarchy. At inference time, only the top-level summary tokens are passed to the LLM.

**Key claims**: First learned method to handle contexts of ~100k tokens using a fixed-size summary representation.

**Where to read**:
- Annotated summary on TowardsAI: <https://pub.towardsai.net/>
- PointFive "Top 10 Prompt Compression Solutions (2026)" — describes AutoCompressor as the earlier learned-soft-prompt approach: <https://www.pointfive.co/blog/top-10-prompt-compression-solutions>

### 4.4 CompAct (Yoon et al., EMNLP 2024)

**Core idea**: Built specifically for retrieval-augmented QA. Actively compresses each retrieved document into summary tokens *before* they are inserted into the prompt, so the LLM never sees the raw chunks. Uses a small encoder distilled from the target LLM.

**Key claims**: Compresses retrieved docs at ingestion time, allowing much larger effective retrieval corpora.

**Where to read**:
- Listed in the PointFive survey above (EMNLP 2024)

### 4.5 ATACompressor (Yang et al., 2026)

**Core idea**: "Adaptive Task-Aware Compression" — soft-prompt compressor that conditions on the task type, not just the input. Different tasks (QA, summarization, code reasoning) get different compression profiles.

**Key claims**: Condenses long contexts into compact token representations while preserving task-essential information.

**Where to read**:
- arXiv (Feb 2026): <https://arxiv.org/abs/2602.03197>

### 4.6 Gist-COCO (Tian et al., 2024)

**Core idea**: Extends gist tokens with **conditioned decoding** — the compressor produces gist tokens that are explicitly trained to help the decoder generate task-appropriate outputs. Adds an encoder-decoder LM (T5/BART-style) on top of the target LLM.

**Where to read**:
- arXiv (Feb 2024): <https://arxiv.org/abs/2402.17447>
- GitHub: <https://github.com/OpenMatch/Gist-COCO>

### 4.7 Hierarchical Gisting (Apple ML, 2024)

**Core idea**: Apple's extension of Mu et al.'s gisting for **zero-shot dialogue agents** that have to ingest long tool/API documentation. Adds hierarchy: high-level gists + low-level gists, with a router deciding which to expand.

**Where to read**:
- Apple ML research blog: <https://machinelearning.apple.com/research>
- Paper: <https://aclanthology.org/2024.emnlp-main.83/> (Jiang et al., 2024)

### 4.8 Shopify's production gisting (2026)

**Core idea**: At Shopify Engineering, gisting is used to compress agent context for high-throughput agent runs. They freeze the LLM weights and only train the gist embeddings, using a 4:1 ratio (one gist token per four prompt tokens). This is the first public production deployment of soft-prompt gisting for agent workloads.

**Where to read**:
- Shopify Engineering blog: <https://shopify.engineering/>

### 4.9 Trade-offs of soft-prompt methods

**Pros**:
- Much higher compression ratios (10×–100×).
- Can represent information that no single token would capture.

**Cons**:
- Requires fine-tuning a compressor → training cost, model-version coupling.
- Compressed representations are not portable across LLM families (a gist trained for Llama-7B does not transfer to GPT-4).
- Black-box LLM APIs cannot accept soft prompts at all (you cannot pass arbitrary embedding vectors to the OpenAI API). This is a hard external constraint.

For most production teams, **soft prompts are only viable when you control the inference stack** (open-weights LLM, self-hosted).

---

## 5. KV Cache Compression & Eviction

This family operates *inside* the model's inference loop, evicting or quantizing KV cache entries during generation. It does not change the prompt text — it changes how much memory the model uses to remember the prompt. This is by far the most active research area in 2024–2026 because KV cache is the dominant memory bottleneck for long-context inference.

### 5.1 H2O (Heavy-Hitter Oracle) — Zhang et al., NeurIPS 2023

**Core idea**: Observes that attention is highly skewed: a small set of "heavy hitter" tokens accumulate most of the attention mass. H2O keeps a fixed budget of recent tokens + the top-k heavy hitters by attention score, evicting the rest. This reduces KV cache size to a constant regardless of context length.

**Key claims**: Up to **8× memory reduction** with minimal accuracy loss on LongBench and ZeroSCROLLS tasks.

### 5.2 StreamingLLM (Xiao et al., ICLR 2024)

**Core idea**: Discovered the **"attention sink"** phenomenon — the first few tokens of any prompt (positions 0–4) absorb disproportionate attention mass even if their content is semantically trivial. If you evict them, attention collapses and the model starts outputting garbage. StreamingLLM therefore keeps (a) the first few "sink" tokens and (b) a sliding window of recent tokens, evicting everything else.

**Key claims**: Enables **streaming inference** over arbitrarily long sequences with constant memory. Widely deployed in production inference engines (vLLM, TensorRT-LLM, llama.cpp).

**Where to read**:
- Paper (cited >1700 times as of 2026): <https://arxiv.org/abs/2309.17453>
- Blog post: "KV Cache Compression: Eviction, Quantization & H2O" by M. Brenndoerfer (Jan 2026) — accessible introduction: <https://mbrenndoerfer.com/>

### 5.3 SnapKV (Li et al., NeurIPS 2024)

**Core idea**: Instead of using attention mass over the whole context (like H2O), SnapKV uses a small **observation window** at the end of the prompt. The attention patterns in this window "vote" on which earlier tokens are important for the *upcoming generation*. This is query-aware compression of the KV cache.

**Key claims**: Reduces KV cache memory by **40–60%** with negligible accuracy loss; cited ~955 times as of 2026; widely considered the strongest training-free KV compressor.

**Where to read**:
- NeurIPS 2024 page: <https://neurips.cc/virtual/2024/poster/93765>
- arXiv: <https://arxiv.org/abs/2404.14469>
- GitHub: <https://github.com/FasterDecoding/SnapKV>
- OpenReview: <https://openreview.net/forum?id=86E579B7DB>

### 5.4 RefreshKV (Xu et al., ACL 2025)

**Core idea**: Observes that SnapKV/H2O/StreamingLLM *permanently* evict tokens, which hurts tasks that require revisiting earlier context (e.g., long-form QA). RefreshKV periodically re-injects evicted tokens based on the current generation state.

**Key claims**: Outperforms permanent-eviction baselines on tasks requiring long-horizon context reuse.

**Where to read**:
- ACL Anthology: <https://aclanthology.org/2025.acl-long.182/>

### 5.5 Ada-KV (Feng et al., 2025)

**Core idea**: Notes that a fixed eviction budget is suboptimal — some attention heads need more memory than others. Ada-KV allocates an **adaptive budget** per head based on the importance distribution.

**Where to read**:
- AlphaXiv summary: <https://www.alphaxiv.org/abs/2407.11550>

### 5.6 Attention-Gate (2025)

**Core idea**: Parameterizes the eviction mechanism — instead of a hand-crafted rule, a small neural network decides which KV entries to evict. The first end-to-end learnable eviction policy.

**Where to read**:
- Hugging Face Daily Papers entry

### 5.7 SinkQ (2025)

**Core idea**: Combines attention-sink awareness with **quantization** of the KV cache. The sink tokens are kept in high precision; the bulk of the cache is quantized aggressively (4-bit or lower).

**Where to read**:
- OpenReview: <https://openreview.net/forum?id=SinkQ>

### 5.8 Production deployment notes

KV-cache compression has the most direct path to production because it requires no changes to the prompt or the API contract — only to the inference engine. As of 2026:

- **vLLM** supports StreamingLLM-style sink-token preservation, with open feature requests for pluggable eviction policies (see GitHub issues like the March 2026 feature request for sink-aware eviction).
- **TensorRT-LLM** ships with H2O and StreamingLLM support out of the box.
- **llama.cpp** exposes KV cache quantization (`--cache-type q4_0` etc.) and is widely used with sliding-window attention models (Gemma 3, Mistral).
- A note of caution: a December 2025 paper ("Assessing KV Cache Compression on Reasoning") shows that **all current KV compressors significantly degrade long reasoning chains** — benchmarks like LongBench hide this because they're mostly short-answer tasks. Use KV compression for chat/RAG, not for chain-of-thought reasoning workloads without testing.

---

## 6. Summarization & Recap-Based Methods

These methods don't prune tokens; they rewrite the prompt into a shorter natural-language form. This is conceptually the simplest approach and the one most applications have historically used (often via an ad-hoc "summarize the conversation so far" prompt).

### 6.1 AutoCompressor (revisited)

Already covered in §4.3 — AutoCompressor sits between soft-prompt and recap-based: it produces summary tokens that are continuous vectors, but they are produced via recursive summarization in a way that mirrors how a human would write a hierarchical summary.

### 6.2 CompAct (revisited)

Covered in §4.4.

### 6.3 Hierarchical and Dynamic Prompt Compression (Apple, 2024)

Already mentioned in §4.7. The "dynamic" part means the level of compression is adapted per-query.

### 6.4 mem0's approach

mem0 (covered in §8.1) is essentially a productionized recap system — it runs an LLM extraction step on each user turn to identify durable facts and stores them as a structured memory layer that gets prepended to future prompts.

### 6.5 General trade-offs

Recap methods have a unique property: the compressed prompt is still human-readable, which makes debugging much easier than with soft prompts. The downside is that they are bottlenecked by the summarizing LLM's quality — if your summarizer is weak or hallucinates, you propagate errors into every downstream call.

---

## 7. Retrieval-Oriented Compression

For RAG systems, prompt compression is most useful *between retrieval and generation*: retrieve more chunks than you would normally fit, then compress them before sending to the LLM.

### 7.1 LangChain ContextualCompressionRetriever

The most widely used implementation. It wraps any base retriever and applies a `DocumentCompressor` to the retrieved docs before returning them. Two main compressor types:

- **LLMChainExtractor**: Asks an LLM "given this query and these documents, extract only the parts relevant to the query".
- **LLMChainFilter**: Asks an LLM "given this query, return yes/no for each document — keep or discard".

**Where to read**:
- LangChain blog (original announcement): <https://www.langchain.com/blog/improving-document-retrieval-with-contextual-compression>
- API reference: <https://reference.langchain.com/langchain_classic/retrievers/langchain.retrievers.ContextualCompressionRetriever>
- Code example: <https://github.com/langchain-ai/langchain/tree/master/cookbook>
- Lancedb walkthrough (Jan 2024): <https://www.lancedb.com/blog/efficient-rag-with-compression-and-filtering>

### 7.2 LlamaIndex × LongLLMLingua

LlamaIndex ships a first-class integration with LongLLMLingua that compresses retrieved nodes before they're passed to the synthesis LLM. Their published result: **75% fewer tokens** with accuracy gains (because compression removes irrelevant chunks the LLM would otherwise waste attention on).

**Where to read**:
- LlamaIndex blog: <https://www.llamaindex.ai/blog/boosting-rag-fixing-truthfulness-with-longllmlingua>
- LlamaIndex docs (PromptCompression section)

### 7.3 The "lost in the middle" angle

A separate but related line of work shows that LLMs underperform when relevant information is in the middle of a long context. Compression methods that *re-rank* relevant content to the front (which LongLLMLingua does as a side effect) help even when they don't reduce token count. This is sometimes called **prompt re-ordering** as distinct from compression.

---

## 8. Agent & Long-Term Memory Approaches

For agent workloads where the context grows turn by turn, the problem isn't "compress one big prompt" — it's "manage a context that grows monotonically over a multi-hour session". This has spawned a separate family of memory-layer tools.

### 8.1 mem0 (Chhikara et al., 2025)

**Core idea**: A memory layer for AI agents. mem0 dynamically extracts, consolidates, and retrieves user-specific facts across conversations. Each user turn is processed by an extractor LLM that pulls out durable facts ("user is vegetarian", "user prefers Python") and stores them in a vector DB. Future prompts are augmented with retrieved relevant facts.

**Key claims**: Production-ready, scalable, used by numerous agent frameworks. Cited ~980 times as of 2026.

**Where to read**:
- arXiv paper: <https://arxiv.org/abs/2509.05560>
- GitHub: <https://github.com/mem0ai/mem0>
- mem0 blog on 4-layer memory architecture: <https://mem0.ai/blog/ai-memory-management>
- DigitalOcean LangGraph + mem0 walkthrough: <https://www.digitalocean.com/blog/building-long-term-memory-in-ai-agents-with-langgraph>
- Red Hat perspective on agent memory: <https://next.redhat.com/>

### 8.2 Claude Code's approach

Anthropic's own Claude Code product uses prompt caching aggressively — without it, the API would have to reprocess the full session history on every turn. This is a real-world example of vendor-side caching being load-bearing for a product.

**Where to read**:
- Claude Code docs on prompt caching: <https://code.claude.com/>

### 8.3 Hierarchical memory for agents

Several recent (2026) industry blog posts describe four-layer memory architectures for agents: (1) working memory (current turn), (2) episodic memory (recent turns), (3) semantic memory (durable facts, like mem0), (4) procedural memory (learned workflows / skills). Each layer has its own compression / forgetting policy.

**Where to read**:
- mem0 4-layer blog (April 2026)
- Red Hat "From context to dreams" (June 2026)

---

## 9. Vendor-Hosted Prompt / Context Caching

The single biggest change in 2024–2026 is that all three major LLM API providers now ship **built-in** prompt caching. For most applications, this obviates the need for client-side compression — you structure your prompts with a stable prefix and let the provider cache it.

### 9.1 Anthropic Prompt Caching (Claude)

**Mechanism**: You mark a prefix of your prompt with a `cache_control` breakpoint. Claude stores the KV cache for that prefix for either 5 minutes (default) or 1 hour (extended). On subsequent requests with the same prefix, Claude reuses the cached KV — you pay only the "cache read" price.

**Pricing impact**:
- Cache writes are billed at **1.25× the normal input token price** (you pay a small premium to write).
- Cache reads are billed at **0.1× the normal input token price** (i.e., a **90% discount** on cached tokens).
- Anthropic's own testing: chatting with a 100k-token cached book takes **2.4 seconds**, vs **much longer** without caching.

**TTL strategy**: 5-minute cache is the default. Use the 1-hour cache for content that is reused across many short sessions (e.g., a knowledge base that many users query). The 1-hour cache is more expensive to write but pays off if you have any traffic.

**Best practice**: Put stable, large content at the front of the prompt (system prompt, tool definitions, knowledge documents, large few-shot examples) and put variable content (the actual user query) at the end.

**Where to read**:
- Claude platform docs: <https://platform.claude.com/docs/build-with-claude/prompt-caching>
- Claude tuning blog (Sep 2026): <https://claude.com/blog/reducing-cost-and-improving-performance-with-claude-platform>
- Claude Code's usage: <https://code.claude.com/docs/prompt-caching>
- Anthropic announcement (Aug 2024): <https://www.anthropic.com/news/prompt-caching>
- SearchEngineJournal coverage: <https://www.searchenginejournal.com/anthropic-announces-prompt-caching-with-claude/>
- AWS Bedrock integration: <https://aws.amazon.com/blogs/machine-learning/optimizing-cost-and-latency-with-amazon-bedrock-prompt-caching/>
- Introl infrastructure post: <https://introl.com/blog/prompt-caching-infrastructure>

### 9.2 OpenAI Prompt Caching

**Mechanism**: **Implicit / automatic** for supported models. On GPT-4o, GPT-4o mini, o1-preview, o1-mini and later (including GPT-5.6+), OpenAI automatically detects prompt prefixes that have been seen recently and applies a discount. No `cache_control` parameter needed.

**Threshold**: Caching kicks in at **1024+ tokens** of shared prefix. Below that, no caching happens.

**Pricing impact**:
- Cache reads get a **50% discount** on GPT-4o (less aggressive than Anthropic's 90%, but it's free and automatic).
- On GPT-5.6+ Azure OpenAI now supports both **implicit** and **explicit** caching modes for finer control.

**Important caveat**: Implicit caching means OpenAI decides what to cache, and you have no guarantee that your prefix will be in the cache at any given moment. For workloads where caching is critical, structure prompts so that the longest possible stable prefix appears first.

**Where to read**:
- OpenAI docs: <https://developers.openai.com/docs/guides/prompt-caching>
- OpenAI announcement (Oct 2024): <https://openai.com/index/api-prompt-caching/>
- Community announcement: <https://community.openai.com/t/prompt-caching-automatic/880217>
- Azure OpenAI GPT-5.6 caching: <https://learn.microsoft.com/>
- PromptHub comparison across vendors: <https://www.prompthub.us/blog/prompt-caching-with-openai-anthropic-and-google-models>
- Humanloop deep dive (Oct 2024): <https://humanloop.com/blog/prompt-caching>

### 9.3 Google Gemini Context Caching

**Mechanism**: **Explicit** context caching via the Gemini API / Vertex AI. You upload a context (text, code, documents) and create a named cache object. Future requests reference the cache object by ID.

**Pricing impact**: Up to **75% cost reduction** on repetitive context. Both implicit (introduced May 2025 for Gemini 2.5) and explicit caching are supported.

**Where to read**:
- Google AI for Developers — Long context docs: <https://ai.google.dev/gemini-api/docs/long-context>
- Vertex AI context caching overview: <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/context-cache/context-cache-overview>
- Vertex AI context caching blog (Oct 2025): <https://cloud.google.com/blog/products/ai-machine-learning/vertex-ai-context-caching>
- Gemini 2.5 implicit caching announcement (May 2025): <https://developers.googleblog.com/en/gemini-2-5-models-now-support-implicit-caching/>
- Google Skills "Intro to Context Caching" (May 2026): <https://www.skills.google/>
- OneUptime implementation guide (Feb 2026): <https://oneuptime.com/blog/how-to-implement-context-caching-with-gemini-on-vertex-ai>
- Sample code on GitHub: <https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/context-caching>

### 9.4 Vendor comparison table

| Vendor | Trigger | Granularity | Discount | TTL | Best for |
|---|---|---|---|---|---|
| **Anthropic** | Explicit (`cache_control`) | Up to 4 breakpoints | 90% on reads; +25% on writes | 5 min / 1 hour | Large stable prefixes (books, knowledge bases, tool defs) |
| **OpenAI** | Implicit (automatic) | Any shared prefix ≥ 1024 tokens | ~50% on reads | Provider-managed, ephemeral | General-purpose; zero-code integration |
| **Google Gemini** | Explicit (cache object) | Named cache referenced by ID | Up to 75% | User-defined (default ~1 hour) | Multi-turn sessions over the same large context |

### 9.5 Cross-vendor best practice

Regardless of vendor, the universal rule is **stable content first, variable content last**. The Redis blog (March 2026) and the OpenAI optimization guide both stress this. Specifically:

1. Put the system prompt first (most stable).
2. Then tool definitions.
3. Then few-shot examples or retrieved documents (medium stability).
4. Then conversation history (lower stability).
5. Then the current user query last (always changing).

This maximizes the chance that the longest possible prefix hits the cache.

---

## 10. Benchmarks & Evaluation

### 10.1 LongBench (Bai et al., 2023)

The de-facto standard benchmark for long-context evaluation. **Bilingual (Chinese/English), multi-task** — 21 tasks across 6 categories: QA, summarization, few-shot learning, code completion, synthetic tasks, and reading comprehension. Most prompt compression papers report LongBench scores.

- Paper: <https://arxiv.org/abs/2308.14508> (cited 1222+ times)
- GitHub: <https://github.com/THUDM/LongBench>
- Hugging Face dataset: <https://huggingface.co/datasets/THUDM/LongBench>
- LongBench v2 (Dec 2024): harder version designed to surface deep reasoning over long contexts: <https://github.com/THUDM/LongBench-v2>
- 100-LongBench (2025) — critique that "LongBench is too easy" and harder variant: <https://aclanthology.org/2025.findings-acl.150/>

### 10.2 ZeroSCROLLS (Shaham et al., 2023)

A **zero-shot** benchmark for long-text understanding. 10 tasks, validation sets of ~20 examples each, no training set. Complements LongBench (which is few-shot) by focusing on pure zero-shot capability. Cited ~225 times.

- ACL Anthology: <https://aclanthology.org/2023.findings-emnlp.991/>
- Hugging Face dataset: <https://huggingface.co/datasets/tau/zero_scrolls>

### 10.3 Needle In A Haystack (NiAH)

The canonical **pressure test** for long-context retrieval: insert a single random statement (the "needle") at a specific position in a long context (the "haystack"), then ask the model to retrieve it. Sweeps (context_length × needle_depth) to produce a heatmap.

- Original repo: <https://github.com/gkamradt/needle-in-a-haystack>
- OpenCompass implementation: <https://opencompass.readthedocs.io/en/latest/prompt/needle_in_a_haystack.html>
- Google Cloud blog — "How Gemini Pro solves it" (Sep 2024): <https://cloud.google.com/blog/products/ai-machine-learning/needle-in-a-haystack-and-how-gemini-pro-solves-it>
- Arize explanation: <https://arize.com/blog/needle-in-a-haystack-test/>
- Multimodal variant (MM-NIAH) — NeurIPS 2024, cited 75+: <https://proceedings.neurips.cc/paper_files/neurips2024/hash/MM-NIAH>
- OpenLayer testing guide (Jan 2026): <https://www.openlayer.com/blog/needle-in-a-haystack-testing>

### 10.4 Other benchmarks worth knowing

- **SCROLLS** (the predecessor of ZeroSCROLLS, with training data).
- **∞Bench** — extends LongBench to 100k+ token inputs.
- **LongGenBench** (cited 58+) — evaluates **long-form generation** rather than short answers: <https://openreview.net/forum?id=LongGenBench>
- **AcademicEval** (live benchmark, Oct 2025): <https://arxiv.org/abs/2510.13507>
- **RULER** — synthesizes multiple needle-in-haystack variants at controlled lengths.

### 10.5 Benchmarking prompt compression specifically

A July 2024 paper ("Characterizing Prompt Compression Methods for Long Context") compares LLMLingua, Selective Context, and others under matched budgets — useful starting point for picking a method:

- arXiv: <https://arxiv.org/abs/2407.12944>

An OpenReview empirical study (Zheng et al., cited 10+) finds that **prompt compression has a greater impact on LLM performance in long contexts compared to short ones** — compression ratios that look fine on short prompts cause disproportionate damage on long ones.

### 10.6 A practical warning about benchmarks

A consistent finding across 2025–2026 evaluations is that LongBench-style benchmarks **underestimate the damage KV compression does to reasoning tasks**. The December 2025 paper "Assessing KV Cache Compression on Reasoning" (<https://arxiv.org/abs/2512.07534>) shows that StreamingLLM, H2O, and SnapKV all look healthy on LongBench but degrade significantly on long chain-of-thought reasoning. Always run your own workload's eval suite before deploying.

---

## 11. Open-Source Libraries & Tooling

### 11.1 LLMLingua family (Microsoft)

```bash
pip install llmlingua
```

Includes LLMLingua, LongLLMLingua, and LLMLingua-2 in one package. The most widely used open-source prompt compressor.

- GitHub: <https://github.com/microsoft/LLMLingua>
- Docs: <https://microsoft.github.io/LLMLingua/>
- PyPI: <https://pypi.org/project/llmlingua/>

### 11.2 Selective Context

Older but still useful, especially for fast token filtering without fine-tuning.

- GitHub: <https://github.com/liyongsea/Selective-Context>

### 11.3 ICAE

- GitHub: <https://github.com/getao/icae>

### 11.4 SnapKV

- GitHub: <https://github.com/FasterDecoding/SnapKV>
- Integrated into vLLM and other inference engines.

### 11.5 Gist-COCO

- GitHub: <https://github.com/OpenMatch/Gist-COCO>

### 11.6 LangChain ContextualCompressionRetriever

- Documentation: <https://python.langchain.com/docs/modules/data_connection/retrievers/contextual_compression/>
- Source: <https://github.com/langchain-ai/langchain/tree/master/libs/langchain/langchain/retrievers>

### 11.7 LlamaIndex PromptCompressor

- Docs: <https://docs.llamaindex.ai/en/latest/api_reference/agent/agent_compression/>
- Includes a `LongLLMLinguaPromptCompressor` class.

### 11.8 mem0

- GitHub: <https://github.com/mem0ai/mem0>
- Docs: <https://docs.mem0.ai/>

### 11.9 Curated paper list repos

- **Prompt-Compression-Survey** (NAACL 2025): <https://github.com/ZongqianLi/Prompt-Compression-Survey>
- **Awesome-Collection-Token-Reduction**: <https://github.com/ZLKong/Awesome-Collection-Token-Reduction>
- **chain-of-thought-hub long-context resources**: <https://github.com/simonedeminati/chain-of-thought-hub/blob/main/resources/long_context.md>

### 11.10 Inference engines with built-in KV cache compression

- **vLLM**: <https://github.com/vllm-project/vllm>
- **TensorRT-LLM**: <https://github.com/NVIDIA/TensorRT-LLM>
- **llama.cpp**: <https://github.com/ggerganov/llama.cpp> (supports `--cache-type q4_0` etc.)
- **SGLang**: <https://github.com/sgl-project/sglang>

---

## 12. Code Examples

### 12.1 LLMLingua-2 — Basic compression

```python
# pip install llmlingua
from llmlingua import PromptCompressor

# LLMLingua-2 uses a BERT-style classifier for fast, accurate compression
llm_lingua = PromptCompressor(
    model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
    use_llmlingua2=True,
    device_map="auto",
)

original_prompt = """
You are a customer support assistant for Acme Corp. Acme makes cloud infrastructure
products including Acme Storage (S3-compatible object storage), Acme Compute (VMs
with per-second billing), and Acme Network (software-defined networking). Our SLA
guarantees 99.99% uptime for all production-tier services. Support tickets should
be categorized as: billing, technical, feature-request, or security. ... [long text]
"""

compressed = llm_lingua.compress_prompt(
    original_prompt,
    rate=0.5,  # keep 50% of tokens → 2x compression
    force_tokens=["system:", "user:", "assistant:"]  # never drop these markers
)

print(compressed["compressed_prompt"])
print(f"Original tokens: {compressed['origin_tokens']}")
print(f"Compressed tokens: {compressed['compressed_tokens']}")
print(f"Compression ratio: {compressed['ratio']}")
```

### 12.2 LongLLMLingua — Query-aware compression for RAG

```python
from llmlingua import PromptCompressor

compressor = PromptCompressor(
    model_name="NousResearch/Llama-2-7b-hf",
    device_map="auto"
)

question = "What is the maximum supported context length for Gemini 2.5 Pro?"

# Retrieved chunks from your vector DB
retrieved_context = "\n\n".join([doc.text for doc in vector_db.search(question, k=10)])

compressed = compressor.compress_prompt(
    context=retrieved_context,
    question=question,        # ← query-aware: LongLLMLingua variant
    rate=0.33,                # 3x compression
    condition_in_question="after_condition",  # condition on the query
    reorder_context="sort",    # also reorders by importance
    dynamic_context_compression_ratio=0.3,  # adapt budget per chunk
)

final_prompt = compressed["compressed_prompt"]
# Feed `final_prompt` + `question` to your generation LLM
```

### 12.3 LangChain ContextualCompressionRetriever

```python
# pip install langchain langchain-openai
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS

# 1. Build your base retriever (FAISS, Chroma, Pinecone, etc.)
base_retriever = FAISS.from_documents(docs, embeddings).as_retriever(search_kwargs={"k": 20})

# 2. Build a compressor that extracts only query-relevant content from each doc
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
compressor = LLMChainExtractor.from_llm(llm)

# 3. Wrap the base retriever — it now compresses each result on the fly
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever,
)

# 4. Retrieve — returns compressed docs (much shorter than the originals)
compressed_docs = compression_retriever.invoke("How do I configure SSO?")
# Pass compressed_docs as context to your generation LLM
```

### 12.4 Anthropic Prompt Caching (Claude)

```python
# pip install anthropic
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are a helpful assistant. [Large knowledge base / tool definitions / few-shot examples go here, e.g. a 50k-token product manual]",
            "cache_control": {"type": "ephemeral"}  # ← marks this as cacheable, 5-min TTL
        }
    ],
    messages=[
        {"role": "user", "content": "What is the warranty period for product X?"}
    ]
)

# The response includes usage info showing how many tokens were cache hits:
# response.usage.cache_creation_input_tokens  ← paid at 1.25x
# response.usage.cache_read_input_tokens      ← paid at 0.1x (90% discount!)
```

### 12.5 OpenAI Implicit Caching (no code change needed)

```python
# pip install openai
from openai import OpenAI

client = OpenAI()

# Structure your prompt with stable content FIRST.
# The longer the shared prefix across requests, the more often the cache hits.
SYSTEM_PROMPT = """You are Acme Support Assistant.
[Long product knowledge base — 8,000 tokens of stable content]
[Tool definitions — 2,000 tokens of stable content]
[Few-shot examples — 1,500 tokens of stable content]
"""  # ~11.5k tokens of stable prefix → above the 1024-token cache threshold

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        # Conversation history (semi-stable)
        {"role": "user", "content": "What's the SLA on Acme Storage?"},
    ]
)

# Check cached tokens in the response:
# response.usage.prompt_tokens_details.cached_tokens
```

### 12.6 Gemini Explicit Context Cache

```python
# pip install google-genai
from google import genai
from google.genai.types import CreateCachedContentConfig, Content, Part

client = genai.Client()

# 1. Create a cache from a large context
cache = client.caches.create(
    model="gemini-2.5-pro",
    config=CreateCachedContentConfig(
        contents=Content(
            parts=[Part.from_text(open("large_document.txt").read())]
        ),
        system_instruction="You answer questions about the cached document.",
        ttl="3600s",  # 1-hour cache
    )
)

# 2. Use the cache by reference
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="What are the key conclusions of this document?",
    config={"cached_content": cache.name}
)

# 3. Delete the cache when done (optional — it also expires after TTL)
client.caches.delete(name=cache.name)
```

### 12.7 mem0 — Long-term agent memory

```python
# pip install mem0ai
from mem0 import Memory

m = Memory()

# Per-user memory (user_id scopes the memory namespace)
user_id = "alice"

# Add a memory — mem0 extracts durable facts automatically
m.add(
    messages=[
        {"role": "user", "content": "I'm a vegetarian and I'm allergic to peanuts."},
        {"role": "assistant", "content": "Got it — I'll keep that in mind for restaurant recs."}
    ],
    user_id=user_id
)

# Retrieve relevant memories for a future prompt
memories = m.search(
    query="Suggest a dinner option",
    user_id=user_id
)

# Inject memories into your prompt
context = "\n".join([mem["memory"] for mem in memories])
prompt = f"User context:\n{context}\n\nSuggest a dinner option."
```

---

## 13. Practical Decision Guide

Use the following flow to pick a method:

### 13.1 If you use a hosted LLM API (OpenAI, Claude, Gemini)

1. **First**: Use the vendor's built-in prompt caching. Restructure prompts so stable content is at the front. This is free upside with zero code complexity.
2. **Second**: If you're still hitting cost/latency walls after vendor caching, add LLMLingua-2 client-side. It's training-free, fast, and works with any API.
3. **Third**: For RAG pipelines specifically, add LangChain `ContextualCompressionRetriever` or LlamaIndex's LongLLMLingua integration between retrieval and generation.

### 13.2 If you self-host an open-weights LLM (Llama, Qwen, Mistral)

1. **First**: Enable KV cache compression in your inference engine (StreamingLLM or SnapKV in vLLM / SGLang / TensorRT-LLM). This is the highest-ROI change — it multiplies your throughput.
2. **Second**: Add LLMLingua-2 if you're feeding the model very long static prompts (system prompts, knowledge bases).
3. **Third**: If you control fine-tuning, consider training a soft-prompt compressor (ICAE or Gist) for your specific domain. This is a major investment but unlocks 10×–100× compression.
4. **Fourth**: For agentic workloads, add mem0 or a similar memory layer to manage growing conversation history.

### 13.3 If you're building an agent

1. **First**: Use vendor-side caching aggressively for the system prompt and tool definitions.
2. **Second**: Add a recap step (mem0 or roll-your-own) every N turns to compress conversation history.
3. **Third**: For tool transcripts (e.g., long bash outputs), use LLMLingua-2 to compress each tool result before adding it to history.
4. **Fourth**: Consider hierarchical memory: working memory (last K turns, verbatim) + episodic (compressed last hour) + semantic (durable facts via mem0).

### 13.4 Decision matrix

| Situation | First choice | Second choice |
|---|---|---|
| Hosted LLM, repetitive system prompt | Vendor prompt caching | LLMLingua-2 |
| Hosted LLM, RAG | LangChain ContextualCompressionRetriever | LongLLMLingua |
| Self-hosted, throughput-bound | KV cache eviction (StreamingLLM/SnapKV) | LLMLingua-2 |
| Self-hosted, extreme compression needed | ICAE / Gist (requires training) | AutoCompressor |
| Multi-turn agent | mem0 + vendor caching | LongLLMLingua per turn |
| Reasoning-heavy (chain-of-thought) | **Avoid KV compression**; use LLMLingua-2 lightly | Recap with explicit fact preservation |
| Multimodal (image + text) | MM-NIAH-style retrieval + LLMLingua-2 for text | Vision token pruning (CVPR 2025 — TopV, etc.) |

---

## 14. Cost & Latency Impact — Real-World Numbers

Concrete numbers reported by vendors and practitioners as of 2026:

| Source | Method | Cost reduction | Latency reduction | Notes |
|---|---|---|---|---|
| Anthropic | Prompt caching (Claude) | up to **90%** | up to **85%** | Cache reads at $0.30/M vs $3.00/M for normal input on Claude Sonnet |
| OpenAI | Implicit prompt caching | ~**50%** on cached tokens | varies | Automatic; ≥1024 token prefix required |
| Google | Gemini context cache (explicit) | up to **75%** | varies | Gemini 2.5 also has implicit caching since May 2025 |
| AWS Bedrock | Prompt caching for Anthropic models | up to **90%** | up to **85%** | Same mechanism, AWS wrapper |
| Microsoft Research | LLMLingua | 20× tokens → proportional cost cut | depends on ratio | Quality preserved at ≤10×; degrades beyond |
| Microsoft Research | LongLLMLingua | 4× tokens → **17.1% accuracy gain** | proportional | Compression *improves* quality on noisy RAG |
| SnapKV paper | KV cache eviction | 40–60% memory | ~proportional TTFT | Per-generation, not per-request |
| Shopify Engineering | Gisting for agents | 4:1 ratio | significant throughput | Production deployment, Aug 2026 |
| PointFive industry report | Various | "$216k/month savings" | varies | Production deployment, Morph 2026 case |

The take-away: **vendor caching alone yields 50–90% cost reduction** for many real workloads, with zero code changes. Client-side compression (LLMLingua-2) yields another 2–5× on top when needed.

---

## 15. Open Problems & Future Directions

### 15.1 Reasoning vs retrieval trade-off

Current KV compressors preserve retrieval (needle-in-haystack) but damage reasoning (chain-of-thought). A 2025–2026 open problem is **reasoning-preserving KV compression** — methods that keep enough context to support multi-step inference, not just fact lookup. RefreshKV and Attention-Gate are early attempts.

### 15.2 Soft-prompt portability

Gist tokens trained for Llama-7B do not transfer to GPT-4 or even Llama-13B. There is no current method to distill a soft prompt from one LLM family to another. This is the main blocker to soft-prompt methods reaching hosted APIs.

### 15.3 Information-theoretic limits

The DeepComm 2024 rate-distortion framework gives the first principled lower bound on prompt compression. Extending it to KV cache compression (where the "channel" is the attention mechanism, not the tokenizer) is open.

### 15.4 Multimodal prompt compression

Vision token pruning (e.g., CipherPrune at ICLR 2025, TopV at CVPR 2025) is the visual analogue of LLMLingua. Multimodal Needle-In-A-Haystack (MM-NIAH, NeurIPS 2024) is the corresponding benchmark. This area is ~1–2 years behind text compression.

### 15.5 Diffusion LLMs

A February 2026 paper ("Prompt Compression in Diffusion Large Language Models") notes that **all prior compression evaluations focus on autoregressive LLMs** — diffusion-based LLMs (like Mercury, LLaDA) may need different compression methods because their KV-cache dynamics differ.

### 15.6 Standardization

There is no agreed-upon benchmark for "prompt compression quality" specifically — most papers report LongBench / ZeroSCROLLS, which were designed for general long-context eval, not compression. A purpose-built benchmark with controlled compression ratios and task-diverse evals is an open need.

### 15.7 Composability

Almost no paper studies what happens when you stack multiple compressors (e.g., LLMLingua at the prompt level + SnapKV at the KV level + vendor caching at the API level). Empirically the savings stack additively but the accuracy degrades super-additively. This deserves systematic study.

### 15.8 Privacy and security

Soft-prompt methods leak information about training data (like any fine-tuned model). Hard-prompt methods can be inverted to recover dropped tokens in some cases. As compression moves into production, security properties of compressed prompts will matter more.

---

## 16. Consolidated Reference List

### Surveys & Frameworks

- **Prompt Compression for Large Language Models: A Survey** — arXiv: <https://arxiv.org/abs/2404.11981> · GitHub (NAACL 2025 survey with visualizations): <https://github.com/ZongqianLi/Prompt-Compression-Survey>
- **The Fundamental Limits of Prompt Compression** (DeepComm, 2024) — rate-distortion framework: <https://deepcomm.github.io/>
- **An Empirical Study on Prompt Compression** (Zheng et al., OpenReview) — <https://openreview.net/forum?id=EmpiricalStudyPromptCompression>
- **Characterizing Prompt Compression Methods for Long Context** (Jul 2024) — <https://arxiv.org/abs/2407.12944>
- **Top 10 Prompt Compression Solutions (2026)** — PointFive industry survey: <https://www.pointfive.co/blog/top-10-prompt-compression-solutions>
- **Awesome-Collection-Token-Reduction** — curated paper list: <https://github.com/ZLKong/Awesome-Collection-Token-Reduction>

### Hard Prompt Methods

- **LLMLingua** (Jiang et al., 2023) — project: <https://llmlingua.com/> · MS Research: <https://www.microsoft.com/en-us/research/project/llmlingua/> · code: <https://github.com/microsoft/LLMLingua> · PyPI: <https://pypi.org/project/llmlingua/> · docs: <https://microsoft.github.io/LLMLingua/>
- **LongLLMLingua** — LlamaIndex integration blog: <https://www.llamaindex.ai/blog/boosting-rag-fixing-truthfulness-with-longllmlingua>
- **LLMLingua-2** — same repo as LLMLingua
- **Selective Context** (Li et al., ACL 2023 Findings) — paper: <https://aclanthology.org/2023.findings-acl.111/> · code: <https://github.com/liyongsea/Selective-Context>
- **Efficient Prompt Compression with Evaluator Heads (EPC)** (Fei et al.) — <https://openreview.net/forum?id=EfficientPromptCompression>
- **Leveraging Attention to Effectively Compress Prompts** (Zhao et al., AAAI 2025) — <https://ojs.aaai.org/index.php/AAAI/article/view/AttentionCompress>

### Soft Prompt / Gist Methods

- **Learning to Compress Prompts with Gist Tokens** (Mu et al., NeurIPS 2023) — <https://neurips.cc/virtual/2023/poster/71193>
- **Gist-COCO** (Tian et al., 2024) — arXiv: <https://arxiv.org/abs/2402.17447> · code: <https://github.com/OpenMatch/Gist-COCO>
- **GistPool** (long-context extension of gisting) — Semantic Scholar
- **Shopify gisting in production** (Aug 2026) — <https://shopify.engineering/>
- **In-Context Autoencoder (ICAE)** (Ge et al., ICLR 2024) — arXiv: <https://arxiv.org/abs/2307.06945> · code: <https://github.com/getao/icae>
- **AutoCompressor** (Chevalier et al., 2023) — summarized at <https://pub.towardsai.net/>
- **CompAct** (Yoon et al., EMNLP 2024) — referenced in PointFive survey
- **ATACompressor** (Yang et al., Feb 2026) — <https://arxiv.org/abs/2602.03197>
- **Hierarchical and Dynamic Prompt Compression** (Jiang et al., EMNLP 2024, Apple ML) — <https://aclanthology.org/2024.emnlp-main.83/> · <https://machinelearning.apple.com/>
- **Soft Prompt Recovers Compressed LLMs, Transferably** (Xu et al., 2024) — <https://proceedings.mlr.press/>
- **Guiding Frozen Language Models with Learned Soft Prompts** (Google Research, 2022) — <https://research.google/blog/guiding-frozen-language-models-with-learned-soft-prompts/>

### KV Cache Compression

- **H2O: Heavy-Hitter Oracle** (Zhang et al., NeurIPS 2023) — NeurIPS page
- **StreamingLLM** (Xiao et al., ICLR 2024) — arXiv: <https://arxiv.org/abs/2309.17453> · blog explainer: <https://mbrenndoerfer.com/>
- **SnapKV** (Li et al., NeurIPS 2024) — NeurIPS: <https://neurips.cc/virtual/2024/poster/93765> · arXiv: <https://arxiv.org/abs/2404.14469> · code: <https://github.com/FasterDecoding/SnapKV> · OpenReview: <https://openreview.net/forum?id=86E579B7DB> · ACM DL: <https://dl.acm.org/doi/10.1145/3696410.3715000>
- **RefreshKV** (Xu et al., ACL 2025) — <https://aclanthology.org/2025.acl-long.182/>
- **Ada-KV** (Feng et al., 2025) — <https://www.alphaxiv.org/abs/2407.11550>
- **Attention-Gate** (2025) — Hugging Face Daily Papers
- **SinkQ** — <https://openreview.net/forum?id=SinkQ>
- **Assessing KV Cache Compression on Reasoning** (Dec 2025) — <https://arxiv.org/abs/2512.07534>
- **POP: Prefill-Only Pruning** (Apr 2026) — <https://arxiv.org/html/2602.03295v2>
- **CipherPrune** (ICLR 2025) — <https://openreview.net/forum?id=mUMvr33FTu>
- **SWAA: Sliding Window Attention Adaptation** (Jan 2026) — arXiv: <https://arxiv.org/abs/2601.03196>
- **Why Stacking Sliding Windows Can't See Very Far** (Aug 2025) — <https://guangxuanx.com/p/stacking-sliding-windows>
- **A Visual Guide to Attention Variants** (Sebastian Raschka, Mar 2026) — <https://magazine.sebastianraschka.com/p/visual-guide-to-attention-variants-llms>

### Token Pruning (general)

- **Learned Token Pruning** (Berkeley EECS-2023-119) — <https://www2.eecs.berkeley.edu/Pubs/TechRpts/2023/EECS-2023-119.html>
- **Token Pruning in Transformers** (Emergent Mind, Sep 2025) — <https://www.emergentmind.com/topics/token-pruning-framework>
- **TopV: Compatible Token Pruning** (CVPR 2025) — <https://cvpr.thecvf.com/virtual/2025/poster/33168>
- **Reducing Token Redundancy in LVLMs** (ACL 2026) — <https://aclanthology.org/2026.acl-long.328.pdf>

### Benchmarks

- **LongBench** (Bai et al., 2023) — arXiv: <https://arxiv.org/abs/2308.14508> · code: <https://github.com/THUDM/LongBench> · HF dataset: <https://huggingface.co/datasets/THUDM/LongBench>
- **LongBench v2** (Dec 2024) — <https://github.com/THUDM/LongBench-v2> · EvalScope docs: <https://evalscope.readthedocs.io/en/latest/third_party/longbench_v2.html>
- **100-LongBench** (Yang et al., 2025) — <https://aclanthology.org/2025.findings-acl.150/>
- **ZeroSCROLLS** (Shaham et al., EMNLP 2023) — ACL: <https://aclanthology.org/2023.findings-emnlp.991/> · HF dataset: <https://huggingface.co/datasets/tau/zero_scrolls>
- **Needle In A Haystack** — repo: <https://github.com/gkamradt/needle-in-a-haystack> · OpenCompass: <https://opencompass.readthedocs.io/en/latest/prompt/needle_in_a_haystack.html> · Google blog: <https://cloud.google.com/blog/products/ai-machine-learning/needle-in-a-haystack-and-how-gemini-pro-solves-it>
- **MM-NIAH** (NeurIPS 2024) — <https://proceedings.neurips.cc/paper_files/neurips2024/hash/MM-NIAH> · arXiv: <https://arxiv.org/abs/2406.17588>
- **LongGenBench** — <https://openreview.net/forum?id=LongGenBench>
- **AcademicEval** (Oct 2025) — <https://arxiv.org/abs/2510.13507>
- **chain-of-thought-hub long-context resources** — <https://github.com/simonedeminati/chain-of-thought-hub/blob/main/resources/long_context.md>

### Vendor Documentation

- **Anthropic Prompt Caching** — docs: <https://platform.claude.com/docs/build-with-claude/prompt-caching> · announcement: <https://www.anthropic.com/news/prompt-caching> · Claude Code usage: <https://code.claude.com/docs/prompt-caching> · tuning blog (Sep 2026): <https://claude.com/blog/reducing-cost-and-improving-performance-with-claude-platform> · AWS Bedrock integration: <https://aws.amazon.com/blogs/machine-learning/optimizing-cost-and-latency-with-amazon-bedrock-prompt-caching/>
- **OpenAI Prompt Caching** — docs: <https://developers.openai.com/docs/guides/prompt-caching> · announcement (Oct 2024): <https://openai.com/index/api-prompt-caching/> · community thread: <https://community.openai.com/t/prompt-caching-automatic/880217>
- **Gemini Context Caching** — Google AI: <https://ai.google.dev/gemini-api/docs/long-context> · Vertex AI docs: <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/context-cache/context-cache-overview> · Google blog (Oct 2025): <https://cloud.google.com/blog/products/ai-machine-learning/vertex-ai-context-caching> · 2.5 implicit caching (May 2025): <https://developers.googleblog.com/en/gemini-2-5-models-now-support-implicit-caching/> · sample code: <https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/context-caching>
- **PromptHub cross-vendor comparison** — <https://www.prompthub.us/blog/prompt-caching-with-openai-anthropic-and-google-models>
- **Humanloop deep dive** — <https://humanloop.com/blog/prompt-caching>
- **Redis blog on prompt caching patterns** (Mar 2026) — <https://redis.io/blog/what-is-prompt-caching>
- **Introl infrastructure post** — <https://introl.com/blog/prompt-caching-infrastructure>
- **OneUptime Gemini implementation guide** — <https://oneuptime.com/blog/how-to-implement-context-caching-with-gemini-on-vertex-ai>

### Libraries & Tools

- **LLMLingua** — <https://github.com/microsoft/LLMLingua> · PyPI: <https://pypi.org/project/llmlingua/>
- **Selective Context** — <https://github.com/liyongsea/Selective-Context>
- **ICAE** — <https://github.com/getao/icae>
- **SnapKV** — <https://github.com/FasterDecoding/SnapKV>
- **Gist-COCO** — <https://github.com/OpenMatch/Gist-COCO>
- **mem0** — <https://github.com/mem0ai/mem0> · paper: <https://arxiv.org/abs/2509.05560> · docs: <https://docs.mem0.ai/>
- **LangChain ContextualCompressionRetriever** — <https://python.langchain.com/docs/modules/data_connection/retrievers/contextual_compression/> · reference: <https://reference.langchain.com/langchain_classic/retrievers/langchain.retrievers.ContextualCompressionRetriever>
- **LlamaIndex PromptCompressor** — <https://docs.llamaindex.ai/>
- **vLLM** — <https://github.com/vllm-project/vllm>
- **TensorRT-LLM** — <https://github.com/NVIDIA/TensorRT-LLM>
- **llama.cpp** — <https://github.com/ggerganov/llama.cpp>
- **SGLang** — <https://github.com/sgl-project/sglang>

### Tutorials & Walkthroughs

- **DataCamp: Prompt Compression — A Guide With Python Examples** (Jun 2024) — <https://www.datacamp.com/tutorial/prompt-compression-llm>
- **Lancedb: Efficient RAG with Compression and Filtering** (Jan 2024) — <https://www.lancedb.com/blog/efficient-rag-with-compression-and-filtering>
- **FullStackRetrieval: Contextual Compression** — <https://community.fullstackretrieval.com/>
- **Analytics Vidhya: Prompt Compression Techniques** (Jul 2026) — <https://www.analyticsvidhya.com/blog/prompt-compression-techniques>
- **PromptHub: Compressing Prompts with LLMLingua** (Oct 2025) — <https://www.prompthub.us/blog/compressing-prompts-with-llmlingua>
- **EmergentMind: Prompt Compression Strategies** (Apr 2026) — <https://www.emergentmind.com/topics/prompt-compression>
- **StochasticSandbox: Paper of the Week — SnapKV** (Apr 2026) — <https://stochasticsandbox.com/p/snapkv>

### Diffusion / Frontier

- **Prompt Compression in Diffusion Large Language Models** (Huang et al., 2026) — arXiv

### Memory & Agent Architectures

- **Mem0: Building Production-Ready AI Agents with Scalable Memory** (Chhikara et al., 2025) — arXiv: <https://arxiv.org/abs/2509.05560>
- **AI Memory Management: 4 Layers & Production Benchmarks** (mem0 blog, Apr 2026) — <https://mem0.ai/blog/ai-memory-management>
- **Building Long-Term Memory in AI Agents with LangGraph** (DigitalOcean, Mar 2026) — <https://www.digitalocean.com/blog/building-long-term-memory-in-ai-agents-with-langgraph>
- **From context to dreams: architecting memory for AI agents** (Red Hat, Jun 2026) — <https://next.redhat.com/>

---

*This document is a living reference. The field moves quickly — the curated GitHub survey at <https://github.com/ZongqianLi/Prompt-Compression-Survey> and the token-reduction list at <https://github.com/ZLKong/Awesome-Collection-Token-Reduction> are good places to track new papers.*

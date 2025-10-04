# xu-ai-news-rag PRD (Product Requirements Document)

## 1. Introduction (Background, Target Users, Product Vision)

- **Background**: In the era of information overload, individuals and teams need efficient ways to acquire, accumulate, and reuse industry news and insights. Existing information tools lack the capability of "personalized knowledge base + semantic search + local controllability". xu-ai-news-rag aims to build an integrated closed-loop from "collection-storage-retrieval-analysis-notification" using locally controllable LLM and vector retrieval capabilities.

- **Target Users**:
  - Knowledge workers (Product/Operations/Investment Research/Media)
  - Small and medium teams/startup teams (need low-cost, controllable, secure internal knowledge systems)
  - Technical practitioners (local private deployment enthusiasts)

- **Product Vision**: Create a "localized, controllable, and scalable" news knowledge base system that enables users to perform news collection, semantic search, and insight analysis with the lowest barrier to entry, while improving efficiency through automated processes.

## 2. User Stories and Scenario Descriptions

- **Collector**: I want the system to automatically crawl my subscribed RSS and web sources on a daily schedule and store them in the database, with failure alerts.
- **Knowledge Base Administrator**: I need to view data lists after login, filter by type/time, support batch deletion, edit tags and source metadata, and upload PDF/Markdown/Excel files through the page.
- **Analysis User**: I want to ask questions in natural language in the search box, with the system prioritizing local knowledge base retrieval and returning results sorted by similarity; if no local matches, automatically search online (e.g., Baidu search) and summarize the Top 3 results.
- **Subscriber**: When new data is stored or scheduled reports are generated, I want to receive email notifications with custom titles and content.
- **Security & Compliance Officer**: I want the system to comply with website robots standards and the principle of least privilege, with all keys not stored on disk.

## 3. Product Scope & Features

### A. Collection & Storage

- **Scheduled Tasks**: Configurable crawl frequency/time windows; sources support RSS, web scraping (robots compliant), intelligent agent tools for assisted crawling.
- **Data Types**: Structured (Excel/CSV) and unstructured (HTML/PDF/Markdown/TXT).
- **Storage Interface**: Unified API for storage, automatically generate/update vector indexes and metadata.
- **Storage Notifications**: Automatic email notifications after successful storage (templates configurable).
- **Intelligent Agent Tool Crawling**:
  - **Capabilities**: Support pages requiring JavaScript rendering, scrolling/pagination, click-to-expand; can inject custom Headers/UA/Cookies; support proxy pools and throttling; strictly comply with robots and site terms.
  - **Strategy**: Complete "source discovery → link extraction → content extraction → deduplication → normalization" based on rules/prompt chains; failure retry (exponential backoff), maximum retry attempts, timeout and concurrency configurable.
  - **Configuration**: Each site can configure crawl templates (CSS/XPath/regex/custom scripts), maximum concurrency, rate limits, runtime windows; black/whitelist domain control.
  - **Output**: Unified standard structure {title, url, published_at, source, content, tags, meta} for storage.
  - **Audit & Compliance**: Provide detailed crawl logs, task ID correlation, error classification and alerts for troubleshooting and compliance review.

### B. Knowledge Base Management (Post-login)

- **List & Filtering**: Filter by type, time, source, with pagination and sorting.
- **Batch Operations**: Single/batch deletion; batch edit tags, sources and other metadata.
- **Upload Interface**: Page upload of multiple file types, support drag-and-drop, multi-file, progress and failure retry.

### C. Semantic Search & Q&A (Post-login)

- **Local Priority**: Based on vector retrieval and re-ranking, return Top-K and organize answers with LLM, including source citations.
- **Online Fallback**: When local misses, automatically trigger online search (e.g., Baidu search), take Top 3 and output after LLM summarization, clearly labeled as "online results".

### D. Analysis & Reporting (Post-login)

- **Clustering & Keywords**: Generate cluster analysis for knowledge base, display Top 10 keyword distribution (charts).
- **Export**: Export reports as images/CSV (future iterations).

### E. Account & Security

- **Login/Logout**: JWT authentication. Secure password storage.
- **Roles (MVP optional)**: Admin/member; operation audit logs (future iterations).

## 4. Product-Specific AI Requirements

### 4.1 Model Requirements (Functionality, Performance Metrics)

- **LLM**: Ollama local deployment qwen2.5:3b (default), used for answer generation, summarization and induction.
- **Vector Embedding**: all-MiniLM-L6-v2 (text vectorization, good Chinese performance, small size, fast speed).
- **Reranking Model**: ms-marco-MiniLM-L-6-v2 (relevance reranking of Top-K candidates to improve precision).
- **Performance Metrics (MVP recommendations)**:
  - Average retrieval latency (end-to-end) ≤ 2s (Top 5 return);
  - Top 3 relevance click/satisfaction ≥ 70%;
  - Storage vectorization throughput ≥ 20 docs/min (adjustable based on machine performance).

### 4.2 Data Requirements (Sources, Quantity, Quality, Annotation)

- **Sources**: RSS, target website pages, manual upload (Excel/CSV/PDF/MD/TXT).
- **Quantity**: MVP target 10,000 document scale; future support for incremental scaling.
- **Quality**: Crawling complies with robots; deduplication, cleaning (remove scripts/ad blocks); retain title, content, time, source, tags.
- **Annotation**: Optional tags for uploads; system automatically generates keywords (for clustering and analysis).

### 4.3 Algorithm Boundaries & Interpretability

- **Boundaries**: LLM generation is for reference only, must include citations; online results need to indicate source and time.
- **Interpretability**: Display retrieved Top-K segments and similarity; display reranking differences (advanced mode).

### 4.4 Evaluation Standards

- **Retrieval Quality**: Manual evaluation set (10-30 questions), MRR@10, nDCG@10 as observation metrics.
- **Usability**: Task success rate, user completion time, subjective satisfaction (survey questionnaire).
- **Stability**: 7-day availability ≥ 99%.

### 4.5 Ethics & Compliance

- **Data Compliance**: Respect copyright and crawling rules, don't crawl restricted content; external display must indicate sources.
- **Privacy & Security**: Don't upload sensitive data to third parties; secure management of keys and credentials (environment variables/key vault, prohibit plaintext in logs).

### 4.6 Intelligent Agent Tool (Agent) Design

- **Architecture**: Based on LangChain tool chain and prompt templates, including CrawlerAgent (page access/rendering), Extractor (content extraction/cleaning), Normalizer (structuring and deduplication), Scheduler (planning/concurrency control).
- **Trigger**: By scheduled plan/manual API/automatic retry on failure; each run records tasks and logs.
- **Security**: Strictly follow robots.txt; don't enable for restricted sites; headers/cookies and other credentials injected through environment variables and not written to logs; rate limiting and concurrency protection to avoid pressure on target sites.
- **Metrics (MVP)**: Crawl success rate ≥ 95%; JS rendering pages average rendering time ≤ 3s (depending on machine performance); error rate and retry rate observable in monitoring panel.

## 5. Non-Functional Requirements (Performance, Security, Availability)

### Performance
- Backend QPS ≥ 30 (retrieval scenarios, single machine mid-config); retrieval end-to-end P95 ≤ 3s; storage P95 ≤ 10s/document.
- Vector Database: FAISS (memory/disk index, selected based on data volume), support batch construction and parallelization.

### Security
- **Identity Authentication**: JWT; salted hash password storage; CORS minimal access; rate limiting and basic anti-brute force.
- **Crawling Compliance**: Comply with robots; user-configured UA and throttling; black/whitelist mechanism.
- **Configuration Security**: Keys through environment variables; email service SMTP configuration not stored on disk.

### Availability & Operations
- **Logging**: Collection, storage, retrieval, email sending all have structured logs;
- **Alerts**: Crawl/storage failure and critical task exception email alerts;
- **Health Check**: Backend/embedding/LLM/vector database dependency health check interfaces.

## 6. Release Standards & Measurement Metrics

### Functional Acceptance
- **Collection**: Can crawl at least 3 RSS sources on schedule and store successfully;
- **Storage & Notifications**: Structured and unstructured data storage success triggers email notifications;
- **Management**: List filtering, batch deletion, edit metadata, upload multiple file types available;
- **Search**: Local priority, return Top 5 with source citations;
- **Fallback**: Local miss automatically searches online, takes Top 3 and summarizes with LLM;
- **Analysis**: Display Top 10 keyword charts.
- **Intelligent Agent Crawling**: Complete stable crawling and storage of at least 1 site requiring JS rendering/scroll loading; complete task logs, automatic retry on failure works.

### Quality & Performance
- End-to-end retrieval P95 ≤ 3s;
- Storage success rate ≥ 98%;
- Manual evaluation Top 3 satisfaction ≥ 70%.

### Security & Compliance
- JWT login effective;
- Keys and configuration not in plaintext;
- Crawling complies with robots;
- Logs don't contain sensitive information.

## 7. Architecture & Technology Selection (Strongly Related to Implementation)

- **Frontend**: React (login, data management, search Q&A, report visualization).
- **Backend**: Flask (REST API, task orchestration, authentication, logging and alerts).
- **Database**: SQLite (metadata/users/tasks), FAISS (vector database).
- **Framework**: LangChain (RAG construction, retrieval and reranking, Agent orchestration).
- **Models**: Ollama (qwen2.5:3b), all-MiniLM-L6-v2 (Embed), ms-marco-MiniLM-L-6-v2 (Rerank).

## 8. Milestones & Scope Control

- **Milestone M1 (2 weeks)**: Login/JWT, upload storage, vector retrieval (local priority) and answers, list management, email notifications.
- **Milestone M2 (2 weeks)**: RSS/web scheduled collection and compliance, online fallback (Baidu Top 3), Top 10 keyword reports.
- **Milestone M3 (iteration)**: Batch operation optimization, audit logs, more visualization and export, pluggable search engines and model switching.

## 9. Open Items & Risks

- **Third-party Search**: Baidu search API quota and costs, alternative solutions (future pluggable).
- **Vector Scale Expansion**: FAISS index type and resource consumption evaluation; disk index strategy.
- **Legal Compliance**: Scope and ownership boundaries of page crawling; public sharing strategy.
- **Multi-language & Cross-domain**: Future support for English sources; CORS minimal opening strategy.
- **Roles/Permissions**: Whether more fine-grained RBAC is needed; multi-tenant requirements evaluation.
- **Anti-crawling & Proxies**: Some sites have strict rate limiting/anti-crawling, may need proxy pools, dynamic UA and stricter compliance strategies, with cost and uncertainty risks.

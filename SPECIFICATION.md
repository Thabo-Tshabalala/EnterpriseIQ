# SPECIFICATION.md

# EnterpriseIQ — Intelligent Enterprise Knowledge RAG System

---

## 1. Introduction

### 1.1 Project Title
**EnterpriseIQ: An Intelligent Retrieval-Augmented Generation System for Enterprise Knowledge Management**

---

### 1.2 Domain

**Domain: Large-Scale Enterprise Operations & Knowledge Management**

A large enterprise is a complex organisation consisting of multiple business units that each generate, consume, and depend on large volumes of documents, records, and structured data. These units include:

- **Human Resources (HR):** Employee contracts, onboarding packs, leave policies, performance review templates, disciplinary procedures, payroll records, and organisational charts.
- **Finance & Stock:** Financial reports, budget forecasts, stock inventory records, purchase orders, sales transactions, supplier invoices, and asset registers.
- **Legal & Compliance:** Regulatory filings, contract agreements, compliance checklists, audit reports, data protection policies (e.g., GDPR, POPIA), and risk assessments.
- **Operations & Procurement:** Supplier catalogues, procurement requests, service level agreements (SLAs), delivery records, warehouse logs, and operational runbooks.

In a general large enterprise, these departments operate semi-independently but share overlapping information needs. Employees regularly need to locate policies, retrieve records, check stock levels, verify compliance status, or understand contractual obligations — tasks that currently require navigating multiple disconnected systems, emailing colleagues, or manually searching shared drives.

EnterpriseIQ operates within this domain as a unified intelligent knowledge layer that indexes documents and structured data from all departments and allows any authorised employee to query the system using natural language, receiving accurate, citation-backed answers drawn from the relevant enterprise knowledge base.

---

### 1.3 Problem Statement

Large enterprises suffer from **information fragmentation**. Critical knowledge is spread across shared drives, email threads, ERP systems, HR portals, and document management systems. Employees waste hours locating the right document, verifying whether a policy is current, or checking stock availability — all tasks that should take seconds.

Existing enterprise search tools rely on keyword matching, which fails when employees do not know the exact terminology used in a document. General-purpose AI assistants cannot access private enterprise data and are prone to hallucination.

**EnterpriseIQ solves this by:**
- Ingesting documents and structured records from HR, Finance, Legal, and Operations into a unified, secure vector knowledge base
- Allowing employees to ask natural language questions such as *"What is the annual leave policy for permanent staff?"* or *"What is the current stock level for product SKU-4821?"*
- Retrieving the most relevant document passages or database records and generating grounded, cited responses via a large language model (LLM)
- Enforcing role-based access control (RBAC) so employees only retrieve information they are authorised to see
- Reducing time-to-information across the enterprise and eliminating reliance on manual document search

---

### 1.4 Individual Scope & Feasibility Justification

EnterpriseIQ is scoped as an individual semester-long project. The system is decomposed into independently deliverable modules:

| Module | Technology | Feasibility |
|---|---|---|
| Document ingestion (PDFs, DOCX, TXT) | PyMuPDF, python-docx | Well-documented, open-source |
| Structured data ingestion (ERP/DB records) | SQLAlchemy + PostgreSQL | Standard ORM tooling |
| Text chunking & embedding | LangChain + HuggingFace  |
| Vector store (semantic search) | ChromaDB / FAISS |
| LLM response generation | OpenAI API |
| Role-Based Access Control (RBAC) | JWT + role tables in PostgreSQL | Standard enterprise security pattern |
| REST API backend | FastAPI (Python) | Lightweight, production-ready |
| Web frontend (chat + dashboard) | Angular + TailwindCSS | Standard frontend stack |
| Department-specific namespaces | ChromaDB collections per department | Native ChromaDB feature |
| Audit logging | PostgreSQL audit table | Simple insert-on-query pattern |

All technologies are open-source and some have free tiers. The modular design allows incremental delivery with each module testable independently.

---

## 2. System Overview

EnterpriseIQ is a full-stack web application deployed internally within an enterprise. It provides:

1. **A document ingestion pipeline** that processes HR, Finance, Legal, and Operations documents (PDFs, DOCX) and structured database records into a searchable vector knowledge base
2. **A department-aware retrieval engine** that performs semantic search within the appropriate namespace based on the user's query and role
3. **An LLM-powered response layer** that synthesises retrieved context into a coherent, cited natural language answer
4. **A secure web interface** with role-based access, conversation history, and a document management dashboard
5. **An audit trail** logging every query, the documents retrieved, and the response generated — for compliance purposes

---

## 3. Actors & Roles

| Role | Description | Access Level |
|---|---|---|
| Employee | General staff querying their department's knowledge base | Read: own department only |
| HR Manager | HR staff managing HR documents and querying the HR namespace | Read/Write: HR namespace |
| Finance Officer | Finance staff managing financial documents and stock records | Read/Write: Finance namespace |
| Legal Officer | Legal staff managing compliance and contract documents | Read/Write: Legal namespace |
| Operations Manager | Operations staff managing procurement and warehouse records | Read/Write: Operations namespace |
| System Administrator | IT admin managing all namespaces, users, and system configuration | Full access |

---

## 4. Functional Requirements

### 4.1 User Authentication & Role Management

| ID | Requirement |
|---|---|
| FR-01 | Users shall register and log in using corporate email and password |
| FR-02 | The system shall assign roles to users (Employee, HR Manager, Finance Officer, Legal Officer, Operations Manager, Admin) |
| FR-03 | Sessions shall be managed via JWT tokens with configurable expiry |
| FR-04 | Administrators shall be able to create, update, deactivate, and delete user accounts |
| FR-05 | Role assignments shall determine which document namespaces a user can query and manage |

### 4.2 Document Ingestion Pipeline

| ID | Requirement |
|---|---|
| FR-06 | The system shall accept PDF and DOCX document uploads from authorised users |
| FR-07 | The system shall ingest structured records from connected PostgreSQL databases (inventory, payroll, procurement) |
| FR-08 | Documents shall be parsed, cleaned, and split into overlapping text chunks (512 tokens, 64-token overlap) |
| FR-09 | Each chunk shall be embedded into a vector using a sentence embedding model and stored in the vector database |
| FR-10 | Each embedding shall carry metadata: source document name, department namespace, page number, chunk index, and ingestion timestamp |
| FR-11 | The system shall display ingestion status per document: Pending → Processing → Ready / Failed |
| FR-12 | Failed ingestions shall log an error message visible to the document manager |

### 4.3 Department Namespaces

| ID | Requirement |
|---|---|
| FR-13 | The system shall maintain four isolated vector namespaces: HR, Finance, Legal, Operations |
| FR-14 | Each namespace shall only be queryable by users with the corresponding role permission |
| FR-15 | Administrators shall be able to query across all namespaces simultaneously |
| FR-16 | Documents shall be assigned to exactly one namespace at upload time |

### 4.4 RAG Query Pipeline

| ID | Requirement |
|---|---|
| FR-17 | Users shall submit natural language queries via a chat interface |
| FR-18 | The system shall embed the user query and perform semantic similarity search against the user's permitted namespace(s) |
| FR-19 | The top-k most relevant chunks (default k=5, configurable up to k=10) shall be retrieved |
| FR-20 | Retrieved chunks shall be assembled into a structured prompt and submitted to the LLM |
| FR-21 | The LLM shall generate a response grounded exclusively in retrieved context |
| FR-22 | Each response shall include inline citations referencing the source document name and page number |
| FR-23 | If no relevant context is found, the system shall inform the user rather than fabricating an answer |

### 4.5 HR Module

| ID | Requirement |
|---|---|
| FR-24 | The HR namespace shall support ingestion of employee contracts, leave policies, onboarding documents, disciplinary procedures, and organisational charts |
| FR-25 | HR Managers shall query HR policies, procedures, and employee-related documents |
| FR-26 | Employees shall access general HR policies but not other employees' personal contracts |

### 4.6 Finance & Stock Module

| ID | Requirement |
|---|---|
| FR-27 | The Finance namespace shall support ingestion of financial reports, budget documents, purchase orders, and supplier invoices |
| FR-28 | The system shall ingest live stock/inventory records from the enterprise PostgreSQL inventory database |
| FR-29 | Finance Officers shall query budget documents and live stock levels by SKU or product name |
| FR-30 | Stock queries shall return the most recently ingested inventory snapshot with a timestamp |

### 4.7 Legal & Compliance Module

| ID | Requirement |
|---|---|
| FR-31 | The Legal namespace shall support ingestion of regulatory filings, contracts, compliance checklists, audit reports, and data protection policies |
| FR-32 | Legal Officers shall query compliance status, contract terms, and regulatory requirements |
| FR-33 | The system shall flag documents older than a configurable expiry threshold (e.g., policies not reviewed in 12 months) |

### 4.8 Operations & Procurement Module

| ID | Requirement |
|---|---|
| FR-34 | The Operations namespace shall support ingestion of supplier catalogues, SLAs, procurement requests, delivery records, and operational runbooks |
| FR-35 | Operations Managers shall query SLAs, procurement steps, and supplier information |
| FR-36 | The system shall support ingestion of structured procurement records from the enterprise database |

### 4.9 Chat Interface

| ID | Requirement |
|---|---|
| FR-37 | The system shall provide a conversational chat interface for submitting queries and viewing LLM responses |
| FR-38 | The chat interface shall display source document passages used for each response in an expandable panel |
| FR-39 | The system shall maintain multi-turn conversation history within a session |
| FR-40 | Users shall be able to start a new conversation or clear chat history at any time |

### 4.10 Audit & Compliance Logging

| ID | Requirement |
|---|---|
| FR-41 | Every query shall be logged: user ID, timestamp, query text, namespace queried, documents retrieved, and response generated |
| FR-42 | Administrators shall be able to view and export the audit log |
| FR-43 | The audit log shall be stored separately from the application database and retained for a minimum of 12 months |

---

## 5. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Performance | Query responses shall be returned within 10 seconds under normal load |
| NFR-02 | Scalability | The vector store shall support up to 500,000 chunks across all namespaces |
| NFR-03 | Security | All API endpoints shall require a valid JWT token |
| NFR-04 | Security | Namespace isolation shall be enforced at the retrieval layer, not only the UI |
| NFR-05 | Security | All data in transit shall be encrypted using TLS 1.2 or higher |
| NFR-06 | Reliability | The ingestion pipeline shall handle malformed or image-only PDFs gracefully with error reporting |
| NFR-07 | Usability | The chat interface shall be responsive and functional on desktop and mobile browsers |
| NFR-08 | Maintainability | All backend services shall be containerised using Docker |
| NFR-09 | Compliance | The audit log shall be retained for a minimum of 12 months |
| NFR-10 | Availability | The system shall target 99% uptime during business hours |

---

## 6. System Constraints

- The system is a single-developer project scoped for one semester
- LLM API calls are subject to token limits and cost; prompt compression will be applied where possible
- Local embedding models (HuggingFace) will be used by default to reduce external API dependency
- The MVP will support English-language documents only
- Stock and procurement data ingestion assumes an accessible PostgreSQL instance within the enterprise network

---

## 7. Assumptions

- The enterprise has an internal network or VPN through which EnterpriseIQ will be hosted
- Each department has a designated document manager responsible for uploading and maintaining content
- A PostgreSQL database exists for inventory and procurement structured data
- The deployment environment supports Python 3.10+ and Node.js 18+

---

## 8. Glossary

| Term | Definition |
|---|---|
| RAG | Retrieval-Augmented Generation — an AI architecture that retrieves relevant context before generating a response |
| Embedding | A high-dimensional numerical vector representing the semantic meaning of a text chunk |
| Vector Store | A database optimised for storing and performing similarity search on embeddings |
| Chunk | A fixed-size overlapping segment of text extracted from a larger document |
| Namespace | An isolated partition in the vector store scoping documents to a specific department |
| LLM | Large Language Model — an AI model that generates natural language responses |
| RBAC | Role-Based Access Control — restricting system access based on a user's assigned role |
| Top-k | The k most semantically similar document chunks retrieved for a given query |
| JWT | JSON Web Token — a compact, signed token used for stateless authentication |
| SLA | Service Level Agreement — a contract defining the expected level of service between parties |
| SKU | Stock Keeping Unit — a unique identifier for a product in an inventory system |
| ERP | Enterprise Resource Planning — integrated software managing core business processes |
| GDPR | General Data Protection Regulation — EU data privacy law |
| POPIA | Protection of Personal Information Act — South African data privacy law |
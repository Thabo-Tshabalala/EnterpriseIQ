# SRD.md

# EnterpriseIQ - System Requirements Document (SRD)

---

## 1. Introduction

### 1.1 Purpose
This System Requirements Document (SRD) defines the functional and non-functional requirements for EnterpriseIQ — an intelligent Retrieval-Augmented Generation (RAG) system for enterprise knowledge management. All requirements are traceable to the stakeholder concerns identified in `STAKEHOLDERS.md`.

### 1.2 Scope
EnterpriseIQ serves a general large enterprise across four departments: HR, Finance & Stock, Legal & Compliance, and Operations & Procurement. The system ingests documents and structured data, performs semantic retrieval, and generates grounded, cited responses via a large language model (LLM).

### 1.3 Definitions

| Term | Definition |
|---|---|
| RAG | Retrieval-Augmented Generation — retrieves relevant context before generating a response |
| Namespace | An isolated partition in the vector store scoping documents to a specific department |
| LLM | Large Language Model — generates natural language responses from a prompt |
| RBAC | Role-Based Access Control — access restrictions based on assigned user roles |
| SRD | System Requirements Document |
| PII | Personally Identifiable Information |

---

## 2. Functional Requirements

> Each requirement is written as a clear, actionable statement with acceptance criteria and traced to the stakeholder it addresses.

---

### FR-01 — User Authentication

**Requirement:** The system shall allow users to register and log in using their corporate email address and a password.

**Acceptance Criteria:**
- Login must succeed within 3 seconds for a valid credential pair
- Failed login attempts must return a clear error message without revealing whether the email or password was incorrect
- Accounts must be locked after 5 consecutive failed login attempts

**Traced to:** System Administrator, Data Protection Officer

---

### FR-02 — Role-Based Access Control

**Requirement:** The system shall assign roles to users (Employee, HR Manager, Finance Officer, Legal Officer, Operations Manager, Administrator) and restrict namespace access based on role.

**Acceptance Criteria:**
- A user with the Employee role must be blocked from accessing namespaces outside their department
- Role changes made by an Administrator must take effect within 60 seconds without requiring the user to log out
- Unauthorised access attempts must return HTTP 403 and be logged in the audit trail

**Traced to:** System Administrator, Data Protection Officer, HR Manager

---

### FR-03 — Document Upload and Ingestion

**Requirement:** The system shall allow authorised users to upload PDF and DOCX documents to their department namespace, triggering an automated ingestion pipeline.

**Acceptance Criteria:**
- Supported formats: PDF and DOCX only; unsupported formats must be rejected with a clear error
- Ingestion status must update in real time: Pending → Processing → Ready / Failed
- Documents must be fully indexed and queryable within 2 minutes of upload for files under 10MB

**Traced to:** HR Manager, Finance Officer, Legal Officer, Operations Manager

---

### FR-04 — Structured Database Sync

**Requirement:** The system shall connect to the enterprise PostgreSQL ERP database and ingest structured records (inventory, payroll, procurement) as queryable text chunks.

**Acceptance Criteria:**
- Sync must run on a configurable schedule (default: every 60 minutes)
- Each synced record must carry a timestamp of when it was last updated in the ERP
- Sync failures must be logged and an alert sent to the System Administrator

**Traced to:** Finance Officer, Operations Manager, System Administrator

---

### FR-05 — Natural Language Query

**Requirement:** The system shall allow authenticated users to submit natural language queries via a chat interface and receive grounded responses drawn from their permitted namespace.

**Acceptance Criteria:**
- Query response must be returned within 10 seconds under normal load
- If no relevant context is found, the system must respond with "No relevant information found in your knowledge base" rather than generating a speculative answer
- Each response must include at least one inline citation referencing the source document name and page number

**Traced to:** Employee, HR Manager, Finance Officer, Legal Officer, Operations Manager

---

### FR-06 — Citation and Source Display

**Requirement:** The system shall display the source document passages used to generate each response in an expandable panel below the answer.

**Acceptance Criteria:**
- Source panel must show document name, page number, and the exact retrieved text chunk
- Users must be able to expand or collapse the source panel per response
- At least the top-3 retrieved chunks must be shown per response

**Traced to:** Employee, Legal Officer, Finance Officer

---

### FR-07 — Document Expiry Flagging

**Requirement:** The system shall flag documents in the Legal namespace that have not been reviewed within a configurable threshold (default: 12 months) and notify the Legal Officer.

**Acceptance Criteria:**
- Flagged documents must appear with a visible warning indicator in the document management dashboard
- Notifications must be sent via the system's email service at 30 days and 7 days before the expiry threshold
- The threshold must be configurable by the System Administrator without code changes

**Traced to:** Legal & Compliance Officer, Data Protection Officer

---

### FR-08 — Conversation History

**Requirement:** The system shall maintain multi-turn conversation history within a user session, allowing follow-up questions that reference prior context.

**Acceptance Criteria:**
- Conversation history must persist for the duration of the active session
- Users must be able to start a new conversation or clear history at any time
- History must not persist across sessions unless explicitly saved by the user

**Traced to:** Employee, HR Manager, Operations Manager

---

### FR-09 — Audit Log

**Requirement:** The system shall log every query event including: user ID, timestamp, namespace queried, query text, documents retrieved, and LLM response generated.

**Acceptance Criteria:**
- Audit log entries must be written within 5 seconds of a query being completed
- Administrators must be able to filter the audit log by user, namespace, and date range
- Audit log must be exportable as a CSV file
- Log entries must be immutable — no user including administrators may delete individual entries

**Traced to:** System Administrator, Data Protection Officer, Executive Management

---

### FR-10 — User and Role Management Dashboard

**Requirement:** The system shall provide an Administrator dashboard for creating, updating, deactivating, and deleting user accounts and assigning roles.

**Acceptance Criteria:**
- New user accounts must be provisionable within 5 minutes
- Deactivated accounts must immediately lose access to all system functions
- Role assignment changes must be reflected in the user's active session within 60 seconds

**Traced to:** System Administrator, HR Manager

---

### FR-11 — Document Management Dashboard

**Requirement:** The system shall provide department managers with a dashboard to view, upload, and delete documents in their namespace, including ingestion status for each document.

**Acceptance Criteria:**
- Dashboard must display document name, upload date, ingestion status, and namespace for each document
- Deleting a document must also remove all associated embeddings from the vector store within 60 seconds
- Managers must only see documents in their own namespace

**Traced to:** HR Manager, Finance Officer, Legal Officer, Operations Manager

---

### FR-12 — PII Safeguard on LLM Queries

**Requirement:** The system shall detect and redact personally identifiable information (PII) from query prompts before they are transmitted to an external LLM API.

**Acceptance Criteria:**
- PII detection must cover: full names, ID numbers, email addresses, phone numbers, and financial account numbers
- Redacted fields must be replaced with a placeholder (e.g., [REDACTED]) in the prompt
- Any PII detection event must be logged in the audit trail

**Traced to:** Data Protection Officer, HR Manager

---

## 3. Non-Functional Requirements

---

### 3.1 Usability

**NFR-01:** The chat interface shall follow WCAG 2.1 Level AA accessibility standards, ensuring the system is usable by employees with visual or motor impairments.

*Measurable Criteria:* Automated accessibility audit (e.g., Axe) must return zero critical violations.
*Traced to:* Employee (General Staff)

**NFR-02:** New users shall be able to submit their first query without any training, relying solely on onscreen guidance and tooltips.

*Measurable Criteria:* User testing with 5 new employees must show 100% task completion rate for submitting a first query with no assistance.
*Traced to:* Employee, HR Manager, Operations Manager

---

### 3.2 Deployability

**NFR-03:** The system shall be fully deployable on both Windows Server and Ubuntu Linux using Docker Compose with a single command.

*Measurable Criteria:* A clean deployment on a supported OS must complete in under 30 minutes from cloning the repository.
*Traced to:* System Administrator

**NFR-04:** The system shall support deployment in an air-gapped (offline) enterprise environment using a local Ollama LLM instance and locally hosted HuggingFace embedding models.

*Measurable Criteria:* All core RAG features must function without any outbound internet connection when configured for local deployment.
*Traced to:* System Administrator, Data Protection Officer

---

### 3.3 Maintainability

**NFR-05:** The backend API shall be fully documented with an OpenAPI (Swagger) specification accessible at `/docs`, covering all endpoints, request/response schemas, and authentication requirements.

*Measurable Criteria:* 100% of API endpoints must appear in the Swagger UI with request/response examples.
*Traced to:* System Administrator, Executive Management

**NFR-06:** All system components shall be modular and independently replaceable — for example, the vector store (ChromaDB) or LLM provider (OpenAI / Ollama) must be swappable via configuration file without code changes.

*Measurable Criteria:* Switching LLM provider must require only a configuration file edit and system restart, with no code modifications.
*Traced to:* System Administrator

---

### 3.4 Scalability

**NFR-07:** The vector store shall support up to 500,000 document chunks across all namespaces without degradation in query response time.

*Measurable Criteria:* Semantic search query must complete in under 2 seconds at 500,000 chunks under single-user load.
*Traced to:* Finance Officer, System Administrator, Executive Management

**NFR-08:** The system shall support up to 200 concurrent authenticated users during peak business hours without query response time exceeding 15 seconds.

*Measurable Criteria:* Load test simulating 200 concurrent users must show P95 response time under 15 seconds.
*Traced to:* System Administrator, Executive Management

---

### 3.5 Security

**NFR-09:** All data in transit between the client, API gateway, and external services shall be encrypted using TLS 1.2 or higher.

*Measurable Criteria:* SSL Labs scan of the deployed instance must return a minimum grade of A.
*Traced to:* Data Protection Officer, System Administrator

**NFR-10:** All passwords stored in the application database shall be hashed using bcrypt with a minimum cost factor of 12.

*Measurable Criteria:* Code review and database inspection must confirm no plaintext or weakly hashed passwords exist.
*Traced to:* Data Protection Officer, System Administrator

**NFR-11:** Namespace isolation shall be enforced at the vector store retrieval layer, not only at the UI or API routing layer, preventing any possibility of cross-namespace data leakage.

*Measurable Criteria:* Penetration test targeting namespace boundary must return zero successful cross-namespace data retrievals.
*Traced to:* Data Protection Officer, HR Manager, Legal Officer

---

### 3.6 Performance

**NFR-12:** End-to-end query response time — from query submission to LLM response displayed in the UI — shall not exceed 10 seconds under normal single-user load.

*Measurable Criteria:* 95th percentile (P95) response time in performance tests must be under 10 seconds.
*Traced to:* Employee, HR Manager, Finance Officer

**NFR-13:** Document ingestion for files under 10MB shall complete and be available for querying within 2 minutes of upload.

*Measurable Criteria:* Automated ingestion test with a 5MB PDF must confirm Ready status within 120 seconds.
*Traced to:* HR Manager, Legal Officer, Operations Manager

---

## 4. Requirements Traceability Matrix

| Requirement ID | Type | Stakeholder(s) |
|---|---|---|
| FR-01 | Functional | System Administrator, DPO |
| FR-02 | Functional | System Administrator, DPO, HR Manager |
| FR-03 | Functional | HR Manager, Finance Officer, Legal Officer, Ops Manager |
| FR-04 | Functional | Finance Officer, Ops Manager, System Administrator |
| FR-05 | Functional | All end users |
| FR-06 | Functional | Employee, Legal Officer, Finance Officer |
| FR-07 | Functional | Legal Officer, DPO |
| FR-08 | Functional | Employee, HR Manager, Ops Manager |
| FR-09 | Functional | System Administrator, DPO, Executive Management |
| FR-10 | Functional | System Administrator, HR Manager |
| FR-11 | Functional | HR Manager, Finance Officer, Legal Officer, Ops Manager |
| FR-12 | Functional | DPO, HR Manager |
| NFR-01 | Usability | Employee |
| NFR-02 | Usability | Employee, HR Manager, Ops Manager |
| NFR-03 | Deployability | System Administrator |
| NFR-04 | Deployability | System Administrator, DPO |
| NFR-05 | Maintainability | System Administrator, Executive Management |
| NFR-06 | Maintainability | System Administrator |
| NFR-07 | Scalability | Finance Officer, System Administrator, Executive Management |
| NFR-08 | Scalability | System Administrator, Executive Management |
| NFR-09 | Security | DPO, System Administrator |
| NFR-10 | Security | DPO, System Administrator |
| NFR-11 | Security | DPO, HR Manager, Legal Officer |
| NFR-12 | Performance | Employee, HR Manager, Finance Officer |
| NFR-13 | Performance | HR Manager, Legal Officer, Ops Manager |
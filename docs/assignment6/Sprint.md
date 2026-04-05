# SPRINT.md

# EnterpriseIQ — Sprint 1 Plan

---

## 1. Sprint Overview

| Field | Detail |
|---|---|
| **Sprint Number** | Sprint 1 |
| **Duration** | 2 weeks (14 days) |
| **Sprint Start** | Week 1 of development |
| **Sprint End** | Week 2 of development |
| **Total Story Points** | 21 |
| **Methodology** | Scrum |

---

## 2. Sprint Goal

> **"Deliver a working authentication system, role-based access control, document ingestion pipeline, and a functional RAG query endpoint — establishing the secure, working core of EnterpriseIQ that all future features will build upon."**

This sprint directly delivers the **Must-have** foundation of the product. By the end of Sprint 1, an authenticated user with an assigned role will be able to upload a document to their namespace and receive a natural language query response grounded in that document's content, transmitted securely over TLS. This constitutes the minimum viable product (MVP) core.

---

## 3. Selected Stories for Sprint 1

| Story ID | User Story | MoSCoW | Story Points |
|---|---|---|---|
| US-001 | As an Employee, I want to log in using my corporate email and password so that I can securely access my department's knowledge base. | Must-have | 3 |
| US-002 | As a System Administrator, I want to create user accounts and assign roles so that employees only access namespaces relevant to their department. | Must-have | 3 |
| US-003 | As an HR Manager, I want to upload PDF and DOCX documents to the HR namespace so that employees can query our policies and procedures. | Must-have | 5 |
| US-004 | As an Employee, I want to submit natural language questions and receive accurate, cited answers so that I can find information without searching shared drives. | Must-have | 8 |
| US-012 | As a Data Protection Officer, I want all data in transit to be encrypted with TLS 1.2 or higher so that sensitive enterprise information cannot be intercepted. | Must-have | 2 |

**Total Sprint 1 Points: 21**

---

## 4. Sprint Backlog — Task Breakdown

### US-001 — Authentication

| Task ID | Task Description | Assigned To | Estimated Hours | Status |
|---|---|---|---|---|
| T-001 | Set up PostgreSQL schema for users table (id, email, password_hash, role, created_at, is_active) | Dev | 2 | To Do |
| T-002 | Implement bcrypt password hashing (cost factor 12) on registration | Dev | 1 | To Do |
| T-003 | Build `/register` POST endpoint — validate email, hash password, insert user | Dev | 2 | To Do |
| T-004 | Build `/login` POST endpoint — validate credentials, issue signed JWT token | Dev | 2 | To Do |
| T-005 | Implement account lockout after 5 failed login attempts | Dev | 2 | To Do |
| T-006 | Build JWT middleware to validate token on all protected routes | Dev | 2 | To Do |
| T-007 | Write unit tests for login, registration, and lockout flows | Dev | 2 | To Do |

---

### US-002 — Role-Based Access Control

| Task ID | Task Description | Assigned To | Estimated Hours | Status |
|---|---|---|---|---|
| T-008 | Define roles enum (Employee, HR Manager, Finance Officer, Legal Officer, Operations Manager, Admin) in database and codebase | Dev | 1 | To Do |
| T-009 | Build Admin dashboard API endpoints: create user, update role, deactivate user, delete user | Dev | 4 | To Do |
| T-010 | Implement Namespace Access Guard middleware — reads user role from JWT and validates namespace permission on every request | Dev | 3 | To Do |
| T-011 | Write unit tests for RBAC — verify Finance Officer cannot access HR namespace | Dev | 2 | To Do |

---

### US-003 — Document Upload and Ingestion

| Task ID | Task Description | Assigned To | Estimated Hours | Status |
|---|---|---|---|---|
| T-012 | Build `/documents/upload` POST endpoint — validate file type (PDF/DOCX) and size (≤50MB) | Dev | 2 | To Do |
| T-013 | Implement PDF text extraction using PyMuPDF | Dev | 2 | To Do |
| T-014 | Implement DOCX text extraction using python-docx | Dev | 2 | To Do |
| T-015 | Implement text chunking — 512 tokens per chunk, 64-token overlap using LangChain text splitter | Dev | 2 | To Do |
| T-016 | Set up ChromaDB with four namespace collections: HR, Finance, Legal, Operations | Dev | 2 | To Do |
| T-017 | Integrate HuggingFace SentenceTransformer model (all-MiniLM-L6-v2) for local embedding generation | Dev | 3 | To Do |
| T-018 | Write embeddings and metadata (source, page, chunk index, namespace, timestamp) to ChromaDB | Dev | 2 | To Do |
| T-019 | Implement real-time ingestion status tracking in PostgreSQL (Pending → Processing → Ready / Failed) | Dev | 2 | To Do |
| T-020 | Build `/documents/list` GET endpoint — returns documents for the user's namespace with status | Dev | 1 | To Do |
| T-021 | Write integration test for full ingestion flow: upload → chunk → embed → ChromaDB write → status Ready | Dev | 3 | To Do |

---

### US-004 — RAG Query Pipeline

| Task ID | Task Description | Assigned To | Estimated Hours | Status |
|---|---|---|---|---|
| T-022 | Build `/query` POST endpoint — validates JWT, checks namespace permission via Guard | Dev | 2 | To Do |
| T-023 | Implement query embedding using the same SentenceTransformer model as ingestion | Dev | 1 | To Do |
| T-024 | Implement ChromaDB semantic similarity search — top-k=5, scoped to user's namespace | Dev | 2 | To Do |
| T-025 | Implement LLM prompt assembly — system instruction + retrieved chunks + user query + citation instruction | Dev | 2 | To Do |
| T-026 | Integrate OpenAI API client (with Ollama fallback config) for LLM response generation | Dev | 3 | To Do |
| T-027 | Parse LLM response and extract inline citations (document name, page number) | Dev | 2 | To Do |
| T-028 | Implement audit log write on every query event (user ID, timestamp, namespace, query, sources, response) | Dev | 2 | To Do |
| T-029 | Handle edge case: no relevant chunks found — return safe "no information found" message, skip LLM call | Dev | 1 | To Do |
| T-030 | Write end-to-end integration test: upload doc → submit query → verify cited response returned | Dev | 3 | To Do |

---

### US-012 — TLS Encryption

| Task ID | Task Description | Assigned To | Estimated Hours | Status |
|---|---|---|---|---|
| T-031 | Configure FastAPI to run behind an HTTPS reverse proxy (Nginx) with a self-signed cert for development | Dev | 2 | To Do |
| T-032 | Configure all API endpoints to reject HTTP connections and redirect to HTTPS | Dev | 1 | To Do |
| T-033 | Document TLS configuration in the deployment README | Dev | 1 | To Do |

---

## 5. Sprint 1 Summary

| Metric | Value |
|---|---|
| Total Tasks | 33 |
| Total Estimated Hours | ~67 hours |
| Stories Covered | 5 (US-001, US-002, US-003, US-004, US-012) |
| Story Points | 21 |
| Definition of Done | All tasks completed, unit and integration tests passing, endpoints tested via Postman, code pushed to `sprint-1` branch and PR opened against `main` |

---

## 6. Sprint 1 → MVP Contribution

By the end of Sprint 1, EnterpriseIQ will have:

- A working **login system** with JWT authentication and account lockout
- **Role-based access control** enforced at the middleware layer
- A **document upload and ingestion pipeline** supporting PDF and DOCX into namespace-isolated ChromaDB collections
- A **fully functional RAG query endpoint** returning grounded, cited responses from uploaded documents
- **TLS encryption** on all endpoints
- A complete **audit log** recording every query event

This represents the core of the product — everything in Sprint 2 (citation UI, ERP sync, conversation history, audit log viewer) builds on this foundation.

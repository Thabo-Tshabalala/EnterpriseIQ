# BACKLOG.md

# EnterpriseIQ — Prioritized Product Backlog

---

## 1. Overview

This document compiles all user stories from `USERSTORIES.md` into a prioritized product backlog using **MoSCoW prioritization** and **Fibonacci story point estimation** (1, 2, 3, 5, 8, 13).

**Story Points Scale:**
| Points | Effort |
|---|---|
| 1 | Trivial — under 2 hours |
| 2 | Small — half a day |
| 3 | Medium — 1 day |
| 5 | Large — 2–3 days |
| 8 | Very Large — 4–5 days |
| 13 | Epic — needs breaking down |

---

## 2. Product Backlog Table

| Story ID | User Story | MoSCoW Priority | Story Points | Dependencies | Justification |
|---|---|---|---|---|---|
| US-001 | As an Employee, I want to log in using my corporate email and password so that I can securely access my department's knowledge base. | **Must-have** | 3 | None | Authentication is the entry gate to the entire system. Nothing else functions without it. Directly addresses System Administrator and DPO security concerns. |
| US-002 | As a System Administrator, I want to create user accounts and assign roles so that employees only access the namespaces relevant to their department. | **Must-have** | 3 | US-001 | RBAC is a hard security and compliance requirement. Without role management, namespace isolation cannot be enforced. Required before any user can access the system. |
| US-003 | As an HR Manager, I want to upload PDF and DOCX documents to the HR namespace so that employees can query our policies and procedures. | **Must-have** | 5 | US-001, US-002 | Document ingestion is the foundation of the RAG pipeline. Without ingested documents, no queries can be answered. Core to all department stakeholders. |
| US-004 | As an Employee, I want to submit natural language questions and receive accurate, cited answers so that I can find information without searching shared drives. | **Must-have** | 8 | US-003 | This is the primary value proposition of the entire system — the core RAG query pipeline. Every other feature exists to support this one. |
| US-009 | As a Data Protection Officer, I want PII to be automatically redacted from queries before they reach the LLM API so that we comply with GDPR and POPIA. | **Must-have** | 5 | US-004 | A legal and regulatory requirement. Transmitting unredacted PII to an external LLM API without controls would constitute a compliance violation. Cannot go to production without this. |
| US-012 | As a Data Protection Officer, I want all data in transit to be encrypted with TLS 1.2 or higher so that sensitive enterprise information cannot be intercepted. | **Must-have** | 2 | US-001 | A baseline security requirement. Without TLS, all credentials and document content are transmitted in plaintext. Must be in place before any real data is used. |
| US-005 | As a Legal Officer, I want to see the source document passages used for each answer so that I can verify accuracy before acting on it. | **Should-have** | 3 | US-004 | Significantly improves trust and usability of responses, especially for Legal. Without citations, responses cannot be verified — reducing adoption by high-stakes users. |
| US-006 | As a Finance Officer, I want the system to sync stock and inventory data from our ERP database so that I can query live inventory levels. | **Should-have** | 8 | US-003, US-004 | High value for Finance and Operations stakeholders. More complex than document ingestion due to live database connectivity. Should be delivered after the core RAG pipeline is stable. |
| US-008 | As a System Administrator, I want to view and export the full audit log so that I can demonstrate compliance during audits. | **Should-have** | 3 | US-004 | Required for compliance but does not block core functionality. Audit logging writes happen automatically; the viewing and export UI can be delivered in a later sprint. |
| US-010 | As an Employee, I want the system to remember my conversation history within a session so that I can ask follow-up questions without repeating context. | **Should-have** | 3 | US-004 | Meaningfully improves the chat experience and is expected by users familiar with AI assistants. Not blocking for MVP but important for adoption. |
| US-007 | As a Legal Officer, I want the system to flag documents not reviewed in over 12 months so that compliance documents remain current. | **Could-have** | 3 | US-003 | Valuable for the Legal Officer but not essential for MVP. Can be delivered after core ingestion and query features are stable without blocking any other functionality. |
| US-011 | As a System Administrator, I want to deploy EnterpriseIQ using Docker Compose so that I can set it up in under 30 minutes. | **Could-have** | 5 | All US | Improves deployability and handoff significantly. Not required for development-phase testing but essential before a real enterprise deployment. Scheduled for a later sprint. |

---

## 3. MoSCoW Summary

| Category | Stories | Total Story Points |
|---|---|---|
| **Must-have** | US-001, US-002, US-003, US-004, US-009, US-012 | 26 |
| **Should-have** | US-005, US-006, US-008, US-010 | 17 |
| **Could-have** | US-007, US-011 | 8 |
| **Won't-have (this release)** | Cross-system SSO integration, mobile app, multi-language support | — |

---

## 4. Prioritization Justification

**Must-have stories** were determined by asking: *"Would the system be unusable or non-compliant without this?"* Authentication (US-001), role management (US-002), document ingestion (US-003), and the core RAG query pipeline (US-004) form the irreducible MVP. PII redaction (US-009) and TLS encryption (US-012) are regulatory requirements — shipping without them would not be acceptable in an enterprise context regardless of how functional the rest of the system is.

**Should-have stories** deliver the second layer of value. Citation display (US-005) makes responses trustworthy rather than just convenient. ERP sync (US-006) unlocks the Finance and Operations departments' use cases. Audit log UI (US-008) enables compliance reporting. Conversation history (US-010) makes the chat experience feel natural. All of these are planned for Sprint 2.

**Could-have stories** are genuine improvements that no stakeholder would sacrifice the core features for. Document expiry flagging (US-007) is a Legal Officer convenience that requires the ingestion pipeline to already be working. Docker deployment (US-011) is a handoff concern rather than a development concern at this stage.

**Won't-have** items — including SSO integration with enterprise identity providers, a native mobile application, and multi-language document support — are acknowledged as future roadmap items. They were explicitly deferred to avoid scope creep in the initial release.

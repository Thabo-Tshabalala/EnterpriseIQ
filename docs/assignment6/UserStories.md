# USERSTORIES.md

# EnterpriseIQ — Agile User Stories

---

## 1. Overview

This document translates functional requirements from `SRD.md` (Assignment 4) and use cases from `USECASES.md` (Assignment 5) into actionable Agile user stories following the format:

> *"As a [role], I want [action] so that [benefit]."*

All stories follow the **INVEST criteria**: Independent, Negotiable, Valuable, Estimable, Small, Testable.

---

## 2. Traceability Map

| User Story ID | Source Requirement (SRD.md) | Source Use Case (USECASES.md) |
|---|---|---|
| US-001 | FR-01 | UC-01 |
| US-002 | FR-02 | UC-05 |
| US-003 | FR-03 | UC-04 |
| US-004 | FR-05 | UC-02 |
| US-005 | FR-06 | UC-03 |
| US-006 | FR-04 | UC-06 |
| US-007 | FR-07 | UC-08 |
| US-008 | FR-09 | UC-07 |
| US-009 | FR-12 | UC-02 |
| US-010 | FR-08 | UC-02 |
| US-011 | NFR-03 | UC-05 |
| US-012 | NFR-09 | UC-01 |

---

## 3. User Stories Table

| Story ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| US-001 | As an **Employee**, I want to log in using my corporate email and password so that I can securely access my department's knowledge base. | Login succeeds within 3 seconds for valid credentials. Invalid credentials show a generic error without revealing which field is wrong. Account locks after 5 consecutive failed attempts. JWT token is issued on success. | High |
| US-002 | As a **System Administrator**, I want to create user accounts and assign roles so that employees only access the namespaces relevant to their department. | New accounts are provisionable within 5 minutes. Role changes take effect within 60 seconds without requiring the user to re-login. Deactivated accounts immediately lose all system access. | High |
| US-003 | As an **HR Manager**, I want to upload PDF and DOCX documents to the HR namespace so that employees can query our policies and procedures through the system. | Only PDF and DOCX formats accepted; others are rejected with a clear message. Documents under 10MB reach "Ready" status within 2 minutes. Ingestion status (Pending → Processing → Ready / Failed) is visible in real time on the dashboard. | High |
| US-004 | As an **Employee**, I want to submit natural language questions and receive accurate, cited answers so that I can find information without searching through shared drives manually. | Response is returned within 10 seconds. Every response includes at least one citation with document name and page number. If no relevant content exists, the system says so rather than fabricating an answer. | High |
| US-005 | As a **Legal Officer**, I want to see the source document passages used for each answer so that I can verify the accuracy of the response before acting on it. | An expandable "Sources" panel appears below every response. At least 3 source chunks are shown with document name, page number, and passage text. The panel is collapsed by default and expands on click. | High |
| US-006 | As a **Finance Officer**, I want the system to automatically sync stock and inventory data from our ERP database so that I can query live inventory levels without logging into a separate system. | ERP sync runs every 60 minutes by default and can be triggered manually. Each synced record displays a timestamp of when it was last updated. Sync failures generate an alert to the System Administrator. | High |
| US-007 | As a **Legal Officer**, I want the system to flag documents that have not been reviewed in over 12 months so that I can ensure our compliance documents are always current. | Documents approaching expiry are flagged yellow at 30 days and red at 7 days. Email notifications are sent to the Legal Officer at both thresholds. The flag is cleared when the document's review date is updated. | Medium |
| US-008 | As a **System Administrator**, I want to view and export the full audit log of all query events so that I can demonstrate compliance during internal or regulatory audits. | Audit log is filterable by user, namespace, and date range. Export produces a valid CSV file within 10 seconds. Log entries are immutable — no user can delete individual records. | Medium |
| US-009 | As a **Data Protection Officer**, I want personally identifiable information to be automatically redacted from queries before they are sent to the LLM API so that we comply with GDPR and POPIA. | PII (names, ID numbers, emails, phone numbers, account numbers) is detected and replaced with [REDACTED] in the LLM prompt. PII detection events are recorded in the audit log. The user still receives a relevant response based on non-PII context. | High |
| US-010 | As an **Employee**, I want the system to remember my conversation history within a session so that I can ask follow-up questions without repeating context. | Conversation history persists for the duration of the active session. Users can clear history or start a new conversation at any time. History does not persist across sessions unless explicitly saved. | Medium |
| US-011 | As a **System Administrator**, I want to deploy EnterpriseIQ using Docker Compose on both Windows and Linux so that I can set up the system in under 30 minutes without specialised AI expertise. | A single `docker compose up` command starts all services successfully on Ubuntu 22.04 and Windows Server 2022. Full deployment completes in under 30 minutes from a clean environment. A README deployment guide is included. | Medium |
| US-012 | As a **Data Protection Officer**, I want all data in transit to be encrypted with TLS 1.2 or higher so that sensitive enterprise information cannot be intercepted. | SSL Labs scan of the deployed instance returns a minimum grade of A. All API endpoints reject non-HTTPS connections. TLS configuration is documented in the deployment guide. | High |

---

## 4. INVEST Criteria Verification

| Story ID | Independent | Negotiable | Valuable | Estimable | Small | Testable |
|---|---|---|---|---|---|---|
| US-001 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-002 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-003 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-004 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-005 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-006 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-007 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-008 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-009 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-010 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-011 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| US-012 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

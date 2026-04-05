# EnterpriseIQ - Test Case Document

---

## 1. Introduction

This document defines test cases to validate the functional and non-functional requirements of EnterpriseIQ. Each test case is traceable to a requirement defined in `SRD.md` and aligned with the use cases in `USECASES.md`. Test cases cover both happy paths and error/edge scenarios.

---

## 2. Functional Test Cases

| Test Case ID | Requirement ID | Use Case | Description | Test Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|---|
| TC-001 | FR-01 | UC-01 | Valid user login | 1. Navigate to login page. 2. Enter valid corporate email and password. 3. Click Login. | User is authenticated. JWT token is issued. User is redirected to their department dashboard within 3 seconds. | — | — |
| TC-002 | FR-01 | UC-01 | Invalid credentials login attempt | 1. Navigate to login page. 2. Enter a valid email with an incorrect password. 3. Click Login. | System returns "Invalid email or password." No JWT token is issued. Login attempt is logged in audit trail. | — | — |
| TC-003 | FR-01 | UC-01 | Account lockout after 5 failed attempts | 1. Attempt login with incorrect password 5 consecutive times for the same account. | After the 5th failure, system displays "Account locked. Contact your administrator." Further login attempts are blocked for that account. | — | — |
| TC-004 | FR-03 | UC-04 | Successful PDF document upload | 1. Log in as HR Manager. 2. Navigate to Document Management dashboard. 3. Click Upload Document. 4. Select a valid PDF file under 10MB. 5. Confirm upload. | Document appears in the dashboard with status "Pending," transitions to "Processing," then "Ready" within 2 minutes. Document is queryable after status shows "Ready." | — | — |
| TC-005 | FR-03 | UC-04 | Reject unsupported file format | 1. Log in as HR Manager. 2. Navigate to Document Management. 3. Attempt to upload a `.xlsx` file. | System rejects the upload and displays "Only PDF and DOCX files are supported." No ingestion is triggered. | — | — |
| TC-006 | FR-05 | UC-02 | Natural language query returns cited response | 1. Log in as an Employee. 2. Type "What is the annual leave policy?" into the chat interface. 3. Submit query. | System returns a grounded response within 10 seconds. Response includes at least one inline citation referencing a document name and page number. | — | — |
| TC-007 | FR-05 | UC-02 | Query with no relevant documents returns safe response | 1. Log in as an Employee in a namespace with no ingested documents. 2. Submit any natural language query. | System displays "No relevant information found in your knowledge base." No LLM API call is made. No fabricated answer is returned. | — | — |
| TC-008 | FR-02 | UC-05 | Role-based namespace isolation | 1. Log in as a Finance Officer. 2. Attempt to submit a query targeting the HR namespace by manipulating the request payload. | System returns HTTP 403 Forbidden. No HR namespace data is returned. The unauthorised access attempt is logged in the audit trail. | — | — |
| TC-009 | FR-09 | UC-07 | Audit log records query event | 1. Log in as any user. 2. Submit a natural language query. 3. Log in as System Administrator. 4. Navigate to Audit Log. 5. Search for the query by user ID and timestamp. | Audit log entry exists for the query containing: user ID, timestamp, namespace queried, query text, source documents retrieved, and response summary. Entry is immutable. | — | — |
| TC-010 | FR-07 | UC-08 | Expired document flagged in Legal namespace | 1. Upload a document to the Legal namespace with a last-reviewed date of 13 months ago (simulated). 2. Trigger the expiry check manually. | Document is flagged with a red "Urgent Review" indicator in the Legal dashboard. An email notification is sent to the Legal Officer listing the flagged document. | — | — |
| TC-011 | FR-12 | UC-02 | PII redacted before LLM API call | 1. Log in as any user. 2. Submit a query containing a full name and ID number (e.g., "What is John Smith's leave balance, ID: 8901115432086?"). 3. Inspect the assembled LLM prompt (via system logs). | The LLM prompt contains "[REDACTED]" in place of the name and ID number. A PII detection event is recorded in the audit log. The user's response is still generated based on non-PII context. | — | — |
| TC-012 | FR-04 | UC-06 | ERP database sync ingests inventory records | 1. Log in as Finance Officer. 2. Trigger ERP sync manually from the dashboard. 3. After sync completes, query "What is the stock level for SKU-4821?" | Sync completes within 5 minutes. Query returns the current stock level for SKU-4821 with a timestamp of the last sync. | — | — |

---

## 3. Non-Functional Test Cases

### NFR Test 1 — Performance: Query Response Time Under Load

| Field | Detail |
|---|---|
| **Test Case ID** | TC-NFR-001 |
| **Requirement ID** | NFR-12 |
| **Category** | Performance |
| **Description** | Verify that end-to-end query response time does not exceed 10 seconds under normal single-user load, and that the system remains responsive under 200 concurrent users with P95 response time under 15 seconds. |

**Test Steps:**
1. Deploy EnterpriseIQ in a staging environment with a fully populated vector store (minimum 50,000 chunks).
2. **Single-user test:** Submit 20 natural language queries sequentially and record end-to-end response time for each.
3. **Load test:** Use a load testing tool (e.g., Locust or k6) to simulate 200 concurrent authenticated users each submitting a query simultaneously.
4. Record P50, P95, and P99 response times for the load test.
5. Verify no errors (HTTP 500 or timeouts) occur during the load test.

**Expected Results:**
- Single-user: All 20 queries return within 10 seconds.
- Load test: P95 response time is under 15 seconds. P99 is under 20 seconds. Zero HTTP 500 errors.

**Actual Result:** —

**Status:** —

---

### NFR Test 2 — Security: Namespace Isolation Penetration Test

| Field | Detail |
|---|---|
| **Test Case ID** | TC-NFR-002 |
| **Requirement ID** | NFR-11 |
| **Category** | Security |
| **Description** | Verify that namespace isolation is enforced at the vector store retrieval layer, not only the UI, and that an authenticated user cannot retrieve data from a namespace they are not authorised to access — even through direct API manipulation. |

**Test Steps:**
1. Create two test accounts: User A (Finance Officer — Finance namespace only) and User B (HR Manager — HR namespace only).
2. Ingest a unique test document into the HR namespace containing a distinctive phrase (e.g., "SENTINEL-HR-CONFIDENTIAL-XYZ").
3. Authenticate as User A (Finance Officer).
4. Attempt the following attack vectors:
   - Submit a query via the chat UI targeting the HR namespace by modifying the request body namespace parameter.
   - Send a direct API request to `/query` with a manually set `namespace: "HR"` and User A's JWT token.
   - Attempt a ChromaDB direct query bypassing the API (if port is exposed).
5. Check all responses for the sentinel phrase "SENTINEL-HR-CONFIDENTIAL-XYZ".
6. Check audit log for any cross-namespace access attempts.

**Expected Results:**
- All attack vectors return HTTP 403 Forbidden or an empty result set.
- The sentinel phrase does not appear in any response.
- All unauthorised access attempts are recorded in the audit log.

**Actual Result:** —

**Status:** —

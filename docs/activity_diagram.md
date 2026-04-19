# activity_diagrams.md

# EnterpriseIQ - Activity Workflow Modeling

---

## Overview

Model of 8 complex workflows in EnterpriseIQ using UML activity diagrams rendered in Mermaid. Each diagram includes start/end nodes, actions, decision branches, parallel actions, and swimlanes identifying the actor responsible for each step. All diagrams are traceable to functional requirements in `SRD.md` and use cases in `USECASES.md`.

---

## Workflow 1: SSO User Authentication

```mermaid
flowchart TD
    Start([🟢 Start]) --> A

    subgraph User["👤 User"]
        A[Navigate to EnterpriseIQ login page]
        B[Click 'Login with SSO']
        C[Enter corporate credentials\nin SSO provider portal]
    end

    subgraph System["⚙️ System"]
        D{SSO provider\nvalidates credentials}
        E[Receive SSO token\nfrom provider]
        F{Does user account\nexist in system?}
        G[Auto-provision new account\nAssign default Employee role]
        H[Load existing account\nand role assignment]
        I[Generate signed JWT token]
        J[Redirect user to\ndepartment dashboard]
        K[Return error message:\n'Authentication failed']
        L[Increment failed\nattempt counter]
        M{Failed attempts\n≥ 5?}
        N[Lock account\nNotify administrator]
    end

    A --> B --> C --> D
    D -->|Valid| E --> F
    F -->|No — first login| G --> I
    F -->|Yes — returning user| H --> I
    I --> J --> End1([🔴 End — Authenticated])

    D -->|Invalid| L --> M
    M -->|No| K --> End2([🔴 End — Failed])
    M -->|Yes| N --> End3([🔴 End — Account Locked])
```

**Explanation:**
This workflow covers the complete SSO authentication flow. The decision at "Does user account exist?" handles both first-time and returning users — a key requirement since SSO auto-provisions accounts rather than requiring manual registration. Parallel to the happy path, the failure branch tracks consecutive failures and locks the account after 5 attempts. This addresses stakeholder concerns from the **System Administrator** (auditable access) and **DPO** (secure authentication). Maps to **FR-01**, **US-001**, **UC-01**.

---

## Workflow 2: Document Upload and Ingestion

```mermaid
flowchart TD
    Start([🟢 Start]) --> A

    subgraph Manager["👤 Department Manager"]
        A[Navigate to Document\nManagement dashboard]
        B[Click Upload Document\nSelect file from local machine]
    end

    subgraph API["⚙️ API Gateway"]
        C{Validate file format\nPDF or DOCX only}
        D{Validate file size\n≤ 50MB}
        E[Set status: Pending\nDisplay in dashboard]
        F[Return error:\n'Unsupported file format']
        G[Return error:\n'File exceeds 50MB limit']
    end

    subgraph Ingestion["⚙️ Ingestion Pipeline"]
        H[Set status: Processing]
        I[Extract text from file\nPyMuPDF for PDF\npython-docx for DOCX]
        J{Text extraction\nsuccessful?}
        K[Split text into chunks\n512 tokens, 64-token overlap]
        L[Generate embeddings\nHuggingFace SentenceTransformer]
        M[Write vectors and metadata\nto ChromaDB namespace]
        N[Set status: Ready\nNotify manager: success]
        O[Set status: Failed\nLog error\nNotify manager]
    end

    A --> B --> C
    C -->|Invalid format| F --> End1([🔴 End — Rejected])
    C -->|Valid| D
    D -->|Too large| G --> End2([🔴 End — Rejected])
    D -->|Valid| E --> H --> I --> J
    J -->|No| O --> End3([🔴 End — Failed])
    J -->|Yes| K --> L --> M --> N --> End4([🔴 End — Ready])
```

**Explanation:**
Two validation gates (format and size) protect the ingestion pipeline from invalid inputs before any processing begins. The pipeline is modelled as a separate swimlane to reflect that it runs asynchronously after the API responds. The status updates (Pending → Processing → Ready/Failed) are visible to the manager in real time on the dashboard. Maps to **FR-03**, **FR-11**, **US-003**, **UC-04**. Addresses the **HR Manager** concern that only valid, approved documents enter the knowledge base.

---

## Workflow 3: Natural Language Query (RAG Pipeline)

```mermaid
flowchart TD
    Start([🟢 Start]) --> A

    subgraph User["👤 User"]
        A[Type natural language query\nin chat interface]
        B[View cited response\nin chat UI]
    end

    subgraph API["⚙️ API Gateway"]
        C[Validate JWT token]
        D{Token valid?}
        E[Fetch user role\nfrom PostgreSQL]
        F[Check namespace permission\nvia Namespace Guard]
        G{Namespace\naccess permitted?}
        H[Return 403 Forbidden\nLog unauthorised attempt]
        I[Return error:\n'Session expired\nPlease log in again']
    end

    subgraph RAG["⚙️ RAG Orchestrator"]
        J[Scan query for PII\nRedact if found]
        K[Embed query text\nSentenceTransformer]
        L[Semantic search\nChromaDB top-k=5\nscoped to namespace]
        M{Relevant chunks\nfound?}
        N[Return:\n'No relevant information found']
        O[Assemble LLM prompt:\nSystem instruction +\nRetrieved chunks +\nUser query]
        P[Call LLM API]
        Q{LLM response\nreceived?}
        R[Return:\n'Service temporarily unavailable']
        S[Parse response\nExtract citations]
    end

    subgraph Audit["⚙️ Audit Service"]
        T[Log query event:\nuser, timestamp, namespace,\nquery, sources, response]
    end

    A --> C --> D
    D -->|Invalid/Expired| I --> End1([🔴 End])
    D -->|Valid| E --> F --> G
    G -->|Denied| H --> End2([🔴 End])
    G -->|Permitted| J --> K --> L --> M
    M -->|No| N --> T --> End3([🔴 End — No Results])
    M -->|Yes| O --> P --> Q
    Q -->|No — Timeout| R --> T --> End4([🔴 End — Timeout])
    Q -->|Yes| S --> T --> B --> End5([🔴 End — Success])
```

**Explanation:**
This is the most critical workflow in EnterpriseIQ — the complete RAG query pipeline. It covers 5 possible outcomes: expired session, unauthorised namespace access, no results found, LLM timeout, and successful cited response. PII redaction is built into the pipeline before embedding, ensuring compliance. The audit log write occurs in all outcomes — even failures are logged. Maps to **FR-05**, **FR-09**, **FR-12**, **US-004**, **US-009**, **UC-02**. Addresses concerns from all end-user stakeholders and the **DPO**.

---

## Workflow 4: Admin Manages User Accounts and Roles

```mermaid
flowchart TD
    Start([🟢 Start]) --> A

    subgraph Admin["👤 System Administrator"]
        A[Navigate to\nUser Management dashboard]
        B{Select action}
    end

    subgraph System["⚙️ System"]
        C[Display new user form]
        D[Validate email not\nalready registered]
        E{Email unique?}
        F[Create user account\nAssign role\nSend welcome email]
        G[Return error:\n'Email already registered']

        H[Display user edit form\nwith current details]
        I[Update role or\naccount details]
        J[Propagate role change\nto active sessions\nwithin 60 seconds]

        K[Confirm deactivation dialog]
        L[Invalidate active\nJWT token immediately]
        M[Mark account as Deactivated\nin database]

        N[Confirm deletion dialog]
        O[Remove account and\nall session data]
    end

    subgraph AuditLog["⚙️ Audit Service"]
        P[Log all account\nchange events]
    end

    A --> B
    B -->|Create User| C --> D --> E
    E -->|No| G --> End1([🔴 End])
    E -->|Yes| F --> P --> End2([🔴 End — Created])

    B -->|Edit User| H --> I --> J --> P --> End3([🔴 End — Updated])

    B -->|Deactivate User| K --> L --> M --> P --> End4([🔴 End — Deactivated])

    B -->|Delete User| N --> O --> P --> End5([🔴 End — Deleted])
```

**Explanation:**
Four distinct branches from a single decision point model the four user management actions. The deactivation branch immediately invalidates the JWT token — a security requirement ensuring no delay between the admin action and loss of access. Role changes propagate to active sessions within 60 seconds without requiring logout. Maps to **FR-02**, **US-002**, **UC-05**. Directly addresses **System Administrator** concerns about auditable, rapid account control.

---

## Workflow 5: ERP Structured Data Sync

```mermaid
flowchart TD
    Start([🟢 Start — Scheduled trigger\nOR manual trigger by Finance/Ops Manager]) --> A

    subgraph Connector["⚙️ DB Sync Connector"]
        A[Attempt connection\nto ERP PostgreSQL database]
        B{Connection\nsuccessful?}
        C[Increment retry counter]
        D{Retry count\n≥ 3?}
        E[Alert System Administrator\nLog failure\nKeep previous embeddings]
        F[Read updated records\nfrom inventory, procurement,\npayroll tables]
        G[Convert rows to\nstructured text chunks\nwith metadata]
    end

    subgraph Ingestion["⚙️ Ingestion Pipeline"]
        H[Generate embeddings\nfor each text chunk]
        I{Embedding\nsuccessful?}
        J[Update ChromaDB:\nreplace existing records\nadd new records]
        K[Log failed chunk\nContinue with remaining]
    end

    subgraph System["⚙️ System"]
        L[Update sync timestamp\nin dashboard]
        M[Schedule next sync\nin 60 minutes]
    end

    A --> B
    B -->|No| C --> D
    D -->|No| A
    D -->|Yes| E --> End1([🔴 End — Failed])
    B -->|Yes| F --> G --> H --> I
    I -->|No| K --> H
    I -->|Yes| J --> L --> M --> End2([🔴 End — Completed])
```

**Explanation:**
The retry loop (up to 3 attempts) prevents a transient network issue from causing a permanent sync failure. The partial failure path (failed chunk logged, pipeline continues) ensures that one bad record does not block all other records from being updated. The sync timestamp visible in the Finance dashboard addresses the **Finance Officer** stakeholder concern about knowing how current the stock data is. Maps to **FR-04**, **US-006**, **UC-06**.

---

## Workflow 6: Document Expiry Flagging (Legal Namespace)

```mermaid
flowchart TD
    Start([🟢 Start — Daily scheduled check]) --> A

    subgraph System["⚙️ System Scheduler"]
        A[Retrieve all documents\nin Legal namespace]
        B[For each document:\ncalculate days since\nlast reviewed date]
        C{Days since review\n> 12 months?}
        D{Days until\nexpiry threshold}
        E[Flag document RED:\n'Urgent Review'\n≤ 7 days remaining]
        F[Flag document YELLOW:\n'Review Soon'\n8–30 days remaining]
        G[No flag — document current]
    end

    subgraph Email["⚙️ Email Service"]
        H{Email notification\nneeded?}
        I[Send email to Legal Officer\nListing flagged documents]
        J{Email sent\nsuccessfully?}
        K[Log failed notification\nRetry next day]
    end

    subgraph LegalOfficer["👤 Legal Officer"]
        L[Log in to dashboard\nView flagged documents]
        M[Review flagged document]
        N[Update last-reviewed date]
        O[System clears flag\nDocument returns to Ready]
    end

    A --> B --> C
    C -->|No| G --> End1([🔴 End — No action])
    C -->|Yes| D
    D -->|≤ 7 days| E --> H
    D -->|8–30 days| F --> H
    H -->|Yes| I --> J
    J -->|No| K --> End2([🔴 End — Notification failed])
    J -->|Yes| End3([🔴 End — Flagged and notified])
    L --> M --> N --> O --> End4([🔴 End — Flag cleared])
```

**Explanation:**
The daily check iterates over all Legal namespace documents and applies a two-tier flagging system — yellow for approaching expiry and red for urgent review. The email notification path has its own failure handling to ensure a failed email does not prevent the flag from being set on the dashboard. The Legal Officer's response (reviewing and updating the date) closes the loop. Maps to **FR-07**, **US-007**, **UC-08**. Addresses the **Legal Officer** concern about missing regulatory deadlines.

---

## Workflow 7: Audit Log View and Export

```mermaid
flowchart TD
    Start([🟢 Start]) --> A

    subgraph AdminDPO["👤 Administrator / DPO"]
        A[Navigate to\nAudit Log dashboard]
        B[Apply filters:\nuser, namespace, date range]
        C{Export\nrequired?}
        D[Click Export CSV]
        E[Review log entries\nin dashboard]
    end

    subgraph System["⚙️ System"]
        F[Fetch audit records\nfrom PostgreSQL\nmatching filter criteria]
        G{Records found\nfor filter?}
        H[Display paginated\naudit log table]
        I[Return:\n'No records found\nfor selected filters']
        J[Generate CSV file\nfrom filtered records]
        K{CSV generated\nwithin 10 seconds?}
        L[Trigger file download\nto browser]
        M[Return error:\n'Export failed\nPlease try again']
    end

    A --> B --> F --> G
    G -->|No| I --> End1([🔴 End — No results])
    G -->|Yes| H --> C
    C -->|No| E --> End2([🔴 End — Viewed])
    C -->|Yes| D --> J --> K
    K -->|Yes| L --> End3([🔴 End — Exported])
    K -->|No| M --> End4([🔴 End — Export failed])
```

**Explanation:**
The filter-first approach means administrators never download unfiltered data — reducing the risk of exporting more personal data than necessary, a key concern for the **DPO**. The 10-second CSV generation guard addresses the performance NFR. Log entries are read-only — there is no delete or edit path in this workflow, enforcing immutability. Maps to **FR-09**, **US-008**, **UC-07**. Addresses **System Administrator** and **DPO** compliance concerns.

---

## Workflow 8: View Cited Response and Source Passages

```mermaid
flowchart TD
    Start([🟢 Start — Query response returned]) --> A

    subgraph User["👤 User"]
        A[Read LLM response\ndisplayed in chat interface]
        B{Want to verify\nsource passages?}
        C[Click to expand\nSources panel]
        D[Read source passages:\ndocument name, page number,\npassage text]
        E{Source document\nstill in system?}
        F[Read full passage text\nfrom retrieved chunk]
        G[Note: 'Source document\nhas been removed from\nknowledge base']
        H{Satisfied with\nresponse?}
        I[Submit follow-up question\nbased on context]
        J[Start new conversation\nor end session]
    end

    subgraph System["⚙️ System"]
        K[Display collapsed\nSources panel below response]
        L[Expand panel:\nShow top-3 chunks\nwith metadata]
        M{Check if source\ndocument still exists\nin namespace}
        N[Display passage\nwith document reference]
        O[Display passage with\n'Document removed' warning]
    end

    A --> K --> B
    B -->|No| H
    B -->|Yes| C --> L --> M
    M -->|Yes| N --> E
    M -->|No| O --> E
    E -->|Document present| F --> H
    E -->|Document removed| G --> H
    H -->|No — follow up| I --> Start
    H -->|Yes| J --> End([🔴 End])
```

**Explanation:**
The Sources panel is collapsed by default to keep the interface clean for general employees, but expands on demand for users like Legal Officers who need to verify the underlying passages. The document-removed warning prevents confusion when a manager deletes a document after it has already been queried. The follow-up loop reflects the multi-turn conversation capability from FR-08. Maps to **FR-06**, **FR-08**, **US-005**, **US-010**, **UC-03**. Addresses **Legal Officer** and **Employee** concerns about response accuracy and verification.

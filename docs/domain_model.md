# EnterpriseIQ - Domain Model

---

## 1. Overview

This document identifies the core domain entities of EnterpriseIQ, defines their attributes and responsibilities, describes relationships between them, and documents the business rules that govern system behaviour. The domain model forms the foundation for the class diagram and is traceable to functional requirements in `SRD.md`, use cases in `USECASES.md`, and state diagrams in `state_diagrams.md`.

---

## 2. Domain Entities

### Entity 1: UserAccount

Represents a registered enterprise employee who interacts with EnterpriseIQ. Every user has exactly one role that determines which namespaces they can access.

| Attribute | Type | Description |
|---|---|---|
| `userId` | String | Unique identifier for the user |
| `email` | String | Corporate email address (SSO identifier) |
| `role` | Enum | One of: EMPLOYEE, HR_MANAGER, FINANCE_OFFICER, LEGAL_OFFICER, OPS_MANAGER, ADMIN |
| `status` | Enum | One of: PENDING, ACTIVE, LOCKED, DEACTIVATED, DELETED |
| `failedLoginAttempts` | Integer | Counter for consecutive failed SSO attempts |
| `createdAt` | DateTime | Account creation timestamp |
| `lastLoginAt` | DateTime | Most recent successful login timestamp |

| Method | Description |
|---|---|
| `login()` | Initiates SSO authentication flow |
| `logout()` | Invalidates active JWT token |
| `submitQuery(text)` | Sends a natural language query to the RAG pipeline |
| `uploadDocument(file, namespace)` | Uploads a document to the specified namespace (managers only) |
| `deleteDocument(documentId)` | Removes a document and its embeddings from the namespace |
| `getPermittedNamespaces()` | Returns the list of namespaces the user's role is authorised to access |

**Relationships:**
- Submits zero or many `QuerySession` instances
- Uploads zero or many `Document` instances
- Holds one `JWTToken` at a time

**Business Rules:**
- A user may only query namespaces permitted by their assigned role
- An account is automatically locked after 5 consecutive failed login attempts
- Only users with ADMIN role can create, deactivate, or delete other accounts
- A DELETED account cannot be reactivated — a new account must be created

---

### Entity 2: Document

Represents a file (PDF or DOCX) or structured database record ingested into a department namespace. A document is the primary source of knowledge in the system.

| Attribute | Type | Description |
|---|---|---|
| `documentId` | String | Unique identifier for the document |
| `fileName` | String | Original file name as uploaded |
| `fileType` | Enum | PDF or DOCX |
| `fileSizeBytes` | Long | Size of the uploaded file in bytes |
| `namespace` | Enum | HR, FINANCE, LEGAL, or OPERATIONS |
| `status` | Enum | UPLOADED, PENDING, PROCESSING, READY, FAILED, FLAGGED, DELETED |
| `uploadedBy` | String | userId of the manager who uploaded the document |
| `uploadedAt` | DateTime | Timestamp of upload |
| `lastReviewedAt` | DateTime | Last date a manager marked the document as reviewed (Legal namespace) |
| `ingestionError` | String | Error message if ingestion failed (nullable) |

| Method | Description |
|---|---|
| `validate()` | Checks file type and size before ingestion |
| `startIngestion()` | Triggers the ingestion pipeline |
| `markReviewed()` | Updates `lastReviewedAt` to current date and clears expiry flag |
| `isExpired()` | Returns true if `lastReviewedAt` exceeds the configured threshold |
| `delete()` | Removes document record and all associated embeddings |

**Relationships:**
- Belongs to exactly one `Namespace`
- Produces one or many `VectorEmbedding` instances
- Uploaded by one `UserAccount`

**Business Rules:**
- Only PDF and DOCX files are accepted; all other formats are rejected
- Maximum file size is 50MB
- A document in FAILED status may be retried by the manager
- Documents in the LEGAL namespace are automatically flagged if not reviewed within 12 months
- Deleting a document must remove all associated `VectorEmbedding` records from ChromaDB

---

### Entity 3: QuerySession

Represents a single natural language query submitted by a user. It tracks the complete lifecycle of the query from submission through PII redaction, retrieval, LLM generation, and audit logging.

| Attribute | Type | Description |
|---|---|---|
| `queryId` | String | Unique identifier for the query |
| `userId` | String | The user who submitted the query |
| `namespace` | Enum | The namespace queried |
| `rawQueryText` | String | The original query as typed by the user |
| `redactedQueryText` | String | Query text after PII redaction (may equal raw if no PII found) |
| `piiDetected` | Boolean | Whether PII was found in the raw query |
| `status` | Enum | INITIATED, SCANNING, EMBEDDING, RETRIEVING, GENERATING, COMPLETED, FAILED |
| `responseText` | String | The LLM-generated response (nullable until completed) |
| `submittedAt` | DateTime | Timestamp of query submission |
| `completedAt` | DateTime | Timestamp of response delivery (nullable) |

| Method | Description |
|---|---|
| `scanForPII()` | Detects and redacts PII from the raw query text |
| `embed()` | Converts redacted query text to a vector using the embedding service |
| `retrieve(topK)` | Performs semantic search against the permitted namespace |
| `generateResponse()` | Assembles prompt and calls the LLM API |
| `getCitations()` | Returns the list of source chunks used to generate the response |
| `logToAudit()` | Writes the complete query event to the audit log |

**Relationships:**
- Submitted by one `UserAccount`
- Retrieves zero or many `VectorEmbedding` instances as context
- Produces one `AuditLogEntry`
- Associated with one `Namespace`

**Business Rules:**
- Every query must pass through PII scanning before embedding, without exception
- If no relevant chunks are found, the LLM must not be called — a safe fallback message is returned
- Every completed or failed query must produce an `AuditLogEntry`
- A query may only retrieve embeddings from namespaces the user's role permits

---

### Entity 4: VectorEmbedding

Represents a single chunk of text extracted from a document, converted into a high-dimensional vector for semantic search.

| Attribute | Type | Description |
|---|---|---|
| `embeddingId` | String | Unique identifier for the embedding |
| `documentId` | String | The source document this chunk came from |
| `namespace` | Enum | The namespace this embedding belongs to |
| `chunkText` | String | The raw text of the chunk |
| `chunkIndex` | Integer | Position of this chunk within the source document |
| `pageNumber` | Integer | Page number in the source document |
| `vector` | Float[] | The high-dimensional embedding vector |
| `createdAt` | DateTime | When this embedding was generated |
| `isStale` | Boolean | True if the source document has been updated since this embedding was created |

| Method | Description |
|---|---|
| `generate(text)` | Calls the embedding model to produce the vector |
| `store()` | Persists the vector and metadata to ChromaDB |
| `markStale()` | Sets `isStale` to true when the source document is updated |
| `delete()` | Removes the embedding from ChromaDB |
| `getSimilarity(queryVector)` | Returns cosine similarity score against a query vector |

**Relationships:**
- Belongs to one `Document`
- Belongs to one `Namespace`
- Retrieved by zero or many `QuerySession` instances

**Business Rules:**
- Chunk size is fixed at 512 tokens with 64-token overlap
- Stale embeddings must be replaced when the source document is re-ingested
- Embeddings must be deleted when their source document is deleted

---

### Entity 5: AuditLogEntry

Represents a tamper-evident record of a single query event, written for compliance and security auditing purposes.

| Attribute | Type | Description |
|---|---|---|
| `logId` | String | Unique identifier for the log entry |
| `userId` | String | The user who submitted the query |
| `queryId` | String | The associated query session |
| `namespace` | Enum | The namespace that was queried |
| `rawQueryText` | String | The original query text (before redaction) |
| `redactedQueryText` | String | The query text after PII redaction |
| `piiDetected` | Boolean | Whether PII was detected |
| `sourcesRetrieved` | String[] | List of document names and page numbers retrieved |
| `responseText` | String | The LLM-generated response |
| `createdAt` | DateTime | Timestamp of the log entry creation |
| `retentionExpiresAt` | DateTime | Date after which this entry may be purged |

| Method | Description |
|---|---|
| `write()` | Persists the log entry to the PostgreSQL audit table |
| `isRetentionExpired()` | Returns true if the entry has exceeded the 12-month retention period |
| `export()` | Serialises the entry to CSV format for compliance export |

**Relationships:**
- Associated with one `QuerySession`
- Associated with one `UserAccount`

**Business Rules:**
- Audit log entries are immutable — no update or delete operations are permitted by any user including administrators
- Entries must be retained for a minimum of 12 months
- Entries older than 12 months may be archived or purged per the data retention policy
- Every query — including failed queries and no-results queries — must produce an entry

---

### Entity 6: Namespace

Represents an isolated department knowledge base within the vector store. Each namespace corresponds to one enterprise department.

| Attribute | Type | Description |
|---|---|---|
| `namespaceId` | Enum | HR, FINANCE, LEGAL, or OPERATIONS |
| `displayName` | String | Human-readable name (e.g., "Human Resources") |
| `status` | Enum | INITIALISED, EMPTY, ACTIVE, LOCKED |
| `documentCount` | Integer | Number of documents currently in Ready status |
| `embeddingCount` | Integer | Total number of vector embeddings stored |
| `createdAt` | DateTime | When the namespace was initialised |
| `lockedAt` | DateTime | When the namespace was locked (nullable) |

| Method | Description |
|---|---|
| `lock()` | Prevents all ingestion and queries until unlocked |
| `unlock()` | Restores normal operation |
| `getDocuments()` | Returns all documents assigned to this namespace |
| `getEmbeddingCount()` | Returns the total number of stored embeddings |
| `isQueryable()` | Returns true if status is ACTIVE |

**Relationships:**
- Contains zero or many `Document` instances
- Contains zero or many `VectorEmbedding` instances
- Accessible by one or many `UserAccount` instances based on role

**Business Rules:**
- Exactly four namespaces exist: HR, FINANCE, LEGAL, OPERATIONS — they are created at system startup and cannot be created or deleted by users
- A LOCKED namespace cannot accept new documents or answer queries
- A user's role determines which namespaces they may access — this is enforced at the retrieval layer, not only the UI

---

### Entity 7: JWTToken

Represents the authentication token issued to a user after successful SSO login. It carries identity and role claims used to authorise every API request.

| Attribute | Type | Description |
|---|---|---|
| `tokenId` | String | Unique identifier for this token instance |
| `userId` | String | The user this token belongs to |
| `role` | Enum | The role encoded in the token claims |
| `issuedAt` | DateTime | When the token was issued |
| `expiresAt` | DateTime | When the token becomes invalid |
| `status` | Enum | ISSUED, ACTIVE, EXPIRED, REVOKED |

| Method | Description |
|---|---|
| `validate()` | Checks token signature, expiry, and revocation status |
| `revoke()` | Immediately invalidates the token regardless of expiry time |
| `getClaims()` | Returns the decoded userId and role from the token payload |
| `isExpired()` | Returns true if current time exceeds `expiresAt` |

**Relationships:**
- Issued to exactly one `UserAccount`

**Business Rules:**
- A token is revoked immediately when the associated user account is deactivated or deleted
- A user may only hold one active token at a time
- Expired tokens must redirect the user to the SSO login page

---

## 3. Entity Relationship Summary

| Relationship | Type | Multiplicity |
|---|---|---|
| UserAccount submits QuerySession | Association | 1 to 0..* |
| UserAccount uploads Document | Association | 1 to 0..* |
| UserAccount holds JWTToken | Composition | 1 to 0..1 |
| Document belongs to Namespace | Association | 0..* to 1 |
| Document produces VectorEmbedding | Composition | 1 to 1..* |
| QuerySession retrieves VectorEmbedding | Association | 0..* to 0..* |
| QuerySession produces AuditLogEntry | Composition | 1 to 1 |
| Namespace contains Document | Aggregation | 1 to 0..* |
| Namespace contains VectorEmbedding | Aggregation | 1 to 0..* |

---

## 4. Business Rules Summary

| Rule ID | Business Rule |
|---|---|
| BR-01 | A user may only query namespaces permitted by their assigned role |
| BR-02 | An account is locked after 5 consecutive failed login attempts |
| BR-03 | Only PDF and DOCX files are accepted; maximum size 50MB |
| BR-04 | Legal namespace documents not reviewed in 12 months are automatically flagged |
| BR-05 | Deleting a document must also delete all its associated embeddings |
| BR-06 | Every query must pass through PII scanning before embedding |
| BR-07 | If no relevant chunks exist, the LLM must not be called |
| BR-08 | Every query — including failures — must produce an AuditLogEntry |
| BR-09 | Audit log entries are immutable and retained for a minimum of 12 months |
| BR-10 | Exactly four namespaces exist and cannot be created or deleted by users |
| BR-11 | A user may only hold one active JWT token at a time |
| BR-12 | Chunk size is fixed at 512 tokens with 64-token overlap |

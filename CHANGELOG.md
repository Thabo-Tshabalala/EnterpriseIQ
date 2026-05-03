# CHANGELOG.md

# EnterpriseIQ - Change Log

---

##  Class Implementation & Creational Patterns

### Added
- `src/models.py` — Full Python implementation of all 7 domain classes from the Assignment 9 class diagram:
  - `UserAccount` — authentication, role management, account lifecycle
  - `JWTToken` — token issuance, validation, revocation
  - `Document` — upload validation, ingestion lifecycle, expiry detection
  - `VectorEmbedding` — vector generation stub, cosine similarity, cloning
  - `AuditLogEntry` — immutable audit record, CSV export, retention check
  - `Namespace` — department knowledge base, lock/unlock, queryability
  - `QuerySession` — RAG pipeline flow, PII scanning, response generation
- `src/models.py` — All 6 enumerations: `Role`, `AccountStatus`, `DocumentStatus`, `NamespaceId`, `QueryStatus`, `TokenStatus`

- `creational_patterns/simple_factory.py` — `NamespaceFactory` creates all 4 department namespaces from a central point
- `creational_patterns/factory_method.py` — `DocumentParser` abstract base with `PDFParser` and `DOCXParser` subclasses; `DocumentParserFactory` selects the correct parser by file type
- `creational_patterns/abstract_factory.py` — `LLMProviderFactory` abstract factory with `OpenAIProviderFactory` and `OllamaProviderFactory` concrete factories; each creates a matched `EmbeddingService` + `LLMClient` pair
- `creational_patterns/builder.py` — `QuerySessionBuilder` constructs complex `QuerySession` objects step-by-step with validation at each stage and method chaining support
- `creational_patterns/prototype.py` — `EmbeddingPrototypeCache` stores pre-configured `VectorEmbedding` prototypes per namespace and returns deep clones with chunk-specific attributes updated
- `creational_patterns/singleton.py` — `AuditLogger` thread-safe singleton using double-checked locking; ensures one global audit log writer across all query sessions

- `tests/test_all.py`  83 unit tests covering all domain classes and all 6 creational patterns including edge cases and thread safety
- `CHANGELOG.md`  this file

### Language
- Python 3.12

### Test Results
- **83 tests, 83 passed, 0 failed**
- **92% code coverage** across `src/` and `creational_patterns/`

### Pattern Justifications
| Pattern | Applied To | Reason |
|---|---|---|
| Simple Factory | `NamespaceFactory` | Centralises creation of the 4 fixed namespaces; prevents invalid namespaces |
| Factory Method | `DocumentParser` subclasses | PDF and DOCX need different parsers; subclasses decide parsing strategy |
| Abstract Factory | `LLMProviderFactory` | OpenAI and Ollama require matched embedding+LLM pairs to avoid mismatches |
| Builder | `QuerySessionBuilder` | QuerySession has many optional parameters; builder validates each step |
| Prototype | `EmbeddingPrototypeCache` | Cloning pre-configured embeddings avoids expensive repeated model initialisation |
| Singleton | `AuditLogger` | One global audit writer prevents duplicate entries and race conditions |

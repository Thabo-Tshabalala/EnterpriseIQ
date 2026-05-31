# EnterpriseIQ — Project Roadmap

This roadmap outlines planned features and improvements for EnterpriseIQ. Items are grouped by priority. Contributors are welcome to pick up any item — see [CONTRIBUTING.md](./CONTRIBUTING.md) to get started.

---

## ✅ Completed (Assignments 3–13)

| Feature | Status |
|---|---|
| Domain model and class diagram | ✅ Done |
| All 6 creational design patterns | ✅ Done |
| Repository layer (in-memory) | ✅ Done |
| Service layer (UserAccount, Document, QuerySession) | ✅ Done |
| REST API with FastAPI (CRUD + business actions) | ✅ Done |
| Swagger/OpenAPI documentation | ✅ Done |
| CI/CD pipeline with GitHub Actions | ✅ Done |
| Branch protection and PR workflow | ✅ Done |

---

## 🔵 High Priority — Next Sprint

| Feature | Description | Difficulty |
|---|---|---|
| **PostgreSQL repository implementation** | Replace in-memory repositories with real PostgreSQL persistence using SQLAlchemy | Medium |
| **ChromaDB vector store integration** | Connect the embedding pipeline to a real ChromaDB instance for semantic search | Medium |
| **HuggingFace embedding integration** | Replace stub embeddings with real `all-MiniLM-L6-v2` model calls | Medium |
| **JWT authentication middleware** | Implement real JWT token validation on all FastAPI endpoints | Medium |
| **SSO integration (Microsoft Entra ID)** | Connect login to a real corporate SSO provider | Hard |

---

## 🟡 Medium Priority — Future Sprints

| Feature | Description | Difficulty |
|---|---|---|
| **OpenAI LLM integration** | Replace stub LLM responses with real OpenAI GPT-4o API calls | Medium |
| **Ollama local LLM support** | Add air-gapped deployment support using local Ollama models | Medium |
| **PDF text extraction** | Implement real PDF parsing using PyMuPDF instead of stubs | Easy |
| **DOCX text extraction** | Implement real DOCX parsing using python-docx instead of stubs | Easy |
| **ERP database sync** | Build scheduled sync from PostgreSQL ERP tables to vector store | Hard |
| **Document expiry email notifications** | Send automated email alerts for expiring Legal documents | Medium |
| **Redis caching** | Cache frequent query results to reduce LLM API costs | Medium |
| **Audit log export endpoint** | Add CSV export for the audit log via REST API | Easy |

---

## 🟢 Low Priority — Nice to Have

| Feature | Description | Difficulty |
|---|---|---|
| **React frontend** | Build a chat UI with TailwindCSS for submitting queries and viewing responses | Hard |
| **Docker Compose deployment** | Package the full system with Docker Compose for one-command deployment | Medium |
| **Multi-language document support** | Support documents in languages other than English | Hard |
| **Mobile-responsive UI** | Ensure the frontend works on mobile browsers | Medium |
| **Slack integration** | Allow employees to submit queries via a Slack bot | Medium |
| **Rate limiting** | Add per-user API rate limiting to prevent abuse | Easy |
| **Admin analytics dashboard** | Show query volume, popular namespaces, and user activity | Medium |
| **Bulk document upload** | Allow uploading multiple documents at once as a ZIP | Medium |

---

##  Good First Issues for Contributors

These are simple, well-scoped tasks perfect for first-time contributors:

| Issue | Description | Label |
|---|---|---|
| Add `find_by_file_type()` to DocumentRepository | Filter documents by PDF or DOCX | `good-first-issue` |
| Add `count_by_namespace()` to DocumentService | Return document count per namespace | `good-first-issue` |
| Add input validation to API request schemas | Validate email format and file name length | `good-first-issue` |
| Write missing `__init__.py` docstrings | Add module-level docstrings to all packages | `good-first-issue` |
| Add `GET /api/users/role/{role}` endpoint | Filter users by role via REST API | `good-first-issue` |

---

## Release Timeline

| Milestone | Target | Contents |
|---|---|---|
| v1.0.0 — MVP Core | Semester end | Domain model, patterns, repositories, services, API, CI/CD |
| v1.1.0 — Real Persistence | Post-semester | PostgreSQL + ChromaDB integration |
| v1.2.0 — Real RAG | Post-semester | HuggingFace + OpenAI/Ollama integration |
| v2.0.0 — Full Product | Future | React frontend, Docker, SSO, email notifications |

# EnterpriseIQ - Stakeholder Analysis Document

---

## Overview

This document identifies and analyses the key stakeholders of EnterpriseIQ — an intelligent Retrieval-Augmented Generation (RAG) system for enterprise knowledge management. Each stakeholder's role, concerns, pain points, and measurable success metrics are documented to ensure requirements are traceable to real human needs.

---

## Stakeholder Analysis Table

| # | Stakeholder | Role |
|---|---|---|
| 1 | Employee (General Staff) | End user querying the system for departmental knowledge |
| 2 | HR Manager | Manages HR documents and queries the HR knowledge namespace |
| 3 | Finance Officer | Manages financial records and queries stock/inventory data |
| 4 | Legal & Compliance Officer | Manages legal documents and monitors regulatory compliance |
| 5 | Operations Manager | Manages procurement and supplier documentation |
| 6 | System Administrator (IT) | Maintains the system, manages users, roles, and infrastructure |
| 7 | Executive / Senior Management | Oversees enterprise-wide adoption and ROI of the system |
| 8 | Data Protection Officer (DPO) | Ensures the system complies with GDPR, POPIA, and data privacy laws |

---

## Detailed Stakeholder Profiles

---

### 1. Employee (General Staff)

**Role:** The primary end user of EnterpriseIQ. General employees across all departments use the chat interface to ask questions about company policies, procedures, and operational information relevant to their role.

| Attribute | Detail |
|---|---|
| **Key Concerns** | Getting fast, accurate answers to work-related questions without waiting for a manager or searching through drives. Needs answers to be easy to understand and clearly sourced. |
| **Pain Points** | Currently spends 30–60 minutes per week searching shared drives and emailing colleagues for information that should be instantly accessible. Keyword search tools return irrelevant documents. No confidence that retrieved documents are the latest version. |
| **Success Metrics** | Average time-to-answer reduced from 20+ minutes to under 1 minute. Employee satisfaction score with internal knowledge access improves by 40%. 80% of queries resolved without escalation to a manager. |

---

### 2. HR Manager

**Role:** Responsible for uploading, maintaining, and governing all HR documents within the EnterpriseIQ HR namespace. Uses the system to answer employee policy queries and manage onboarding documentation.

| Attribute | Detail |
|---|---|
| **Key Concerns** | Ensuring that only the latest, approved versions of HR policies are accessible to employees. Reducing the volume of repetitive policy questions directed at the HR team. Maintaining confidentiality of personal employee records. |
| **Pain Points** | HR team receives the same policy questions repeatedly (leave, disciplinary process, onboarding). Old document versions circulate on shared drives causing confusion. No way to know if an employee accessed a document or read a policy. |
| **Success Metrics** | 50% reduction in repetitive HR policy queries received by the HR team. 100% of documents in the HR namespace verified as current and approved. Zero incidents of employees accessing other employees' personal records. |

---

### 3. Finance Officer

**Role:** Manages financial reports, budget documents, purchase orders, and live stock/inventory data within the Finance namespace. Uses EnterpriseIQ to query financial records and check real-time stock levels.

| Attribute | Detail |
|---|---|
| **Key Concerns** | Accuracy of stock data — inventory levels must reflect the most recently synced ERP records. Budget and financial documents must be accessible only to authorised finance staff. Queries must return figures with clear source references so they can be verified. |
| **Pain Points** | Currently must log into the ERP system separately to check stock levels, then cross-reference with spreadsheets. Financial reports are stored in multiple locations making it hard to know which version is current. Answering stock queries from operations staff takes significant time. |
| **Success Metrics** | Stock level queries answered within 10 seconds with a timestamp of last sync. Finance namespace accessible only to Finance Officers and above. 30% reduction in time spent answering internal stock and budget queries. |

---

### 4. Legal & Compliance Officer

**Role:** Manages all legal documents, contracts, regulatory filings, and compliance checklists. Uses EnterpriseIQ to verify compliance status, check contract terms, and monitor policy expiry.

| Attribute | Detail |
|---|---|
| **Key Concerns** | Regulatory compliance — the system must never return outdated compliance information. Contract terms must be accurately retrievable with citation to the specific clause and document. Documents nearing expiry must be flagged proactively. |
| **Pain Points** | Manually tracks contract expiry dates in spreadsheets. Compliance audits require significant manual document retrieval. Risk of missing a regulatory deadline due to document being buried in a shared drive. |
| **Success Metrics** | 100% of contracts with expiry dates within 30 days flagged automatically. Compliance queries answered with cited clause references in under 10 seconds. Zero missed regulatory deadlines attributable to document retrieval failure. |

---

### 5. Operations Manager

**Role:** Manages supplier catalogues, SLAs, procurement records, delivery logs, and operational runbooks in the Operations namespace. Uses EnterpriseIQ to answer procurement queries and check supplier terms.

| Attribute | Detail |
|---|---|
| **Key Concerns** | SLA terms must be accurately retrievable so supplier performance can be verified. Procurement procedures must be clearly documented and queryable by operations staff. Delivery records and warehouse logs must be searchable. |
| **Pain Points** | SLA documents are stored in email attachments and are difficult to locate quickly. New operations staff take weeks to learn procurement procedures due to poor documentation access. Supplier disputes require manual retrieval of contract terms. |
| **Success Metrics** | SLA terms retrievable within 10 seconds during supplier disputes. New operations staff onboarding time reduced by 30% through self-service document queries. 90% of procurement procedure queries resolved without manager escalation. |

---

### 6. System Administrator (IT)

**Role:** Responsible for deploying, configuring, and maintaining EnterpriseIQ. Manages user accounts, role assignments, system health monitoring, and infrastructure uptime.

| Attribute | Detail |
|---|---|
| **Key Concerns** | System must be deployable and maintainable without requiring specialised AI/ML expertise. Role-based access must be enforceable and auditable. System must be stable and recoverable in case of failure. |
| **Pain Points** | Managing access permissions across multiple document systems is complex and error-prone. No centralised visibility into who is querying what information. Difficult to onboard new staff to multiple disconnected systems. |
| **Success Metrics** | New user accounts provisioned and role-assigned within 5 minutes. System uptime of 99% during business hours. All access control changes logged and auditable within 24 hours. Full system deployable via Docker Compose in under 30 minutes. |

---

### 7. Executive / Senior Management

**Role:** Sponsors and oversees the EnterpriseIQ initiative. Concerned with organisation-wide productivity gains, return on investment, and strategic value of the system.

| Attribute | Detail |
|---|---|
| **Key Concerns** | Measurable productivity improvement across departments. Reduction in time employees spend searching for information. Assurance that the system is secure and compliant with data regulations. |
| **Pain Points** | No visibility into how much time is lost to information retrieval across the enterprise. Difficult to quantify the cost of information fragmentation. Previous knowledge management tools were underutilised due to poor usability. |
| **Success Metrics** | Documented 30%+ reduction in time-to-information across departments within 6 months of deployment. Executive dashboard showing system usage statistics and query volumes per department. Positive employee satisfaction survey results regarding knowledge access. |

---

### 8. Data Protection Officer (DPO)

**Role:** Ensures EnterpriseIQ complies with applicable data protection legislation including GDPR and POPIA. Reviews data flows, storage practices, and access controls.

| Attribute | Detail |
|---|---|
| **Key Concerns** | Personal employee data (payroll, contracts) must not be accessible outside of authorised namespaces. All query logs containing personal data must be handled in compliance with data retention policies. The LLM API must not be sent personal identifiable information (PII) without appropriate controls. |
| **Pain Points** | Existing systems lack granular audit trails making it difficult to demonstrate compliance during audits. No automated mechanism to detect when PII is included in a query sent to an external LLM. Data retention policies are inconsistently applied across departments. |
| **Success Metrics** | Full audit trail available for all queries within 24 hours of request during a compliance audit. Zero confirmed incidents of PII transmitted to external LLM without authorisation. Data retention policy enforced automatically — audit logs purged after 12 months. |

---

## Stakeholder Priority Matrix

| Stakeholder | Influence | Interest | Priority |
|---|---|---|---|
| Employee (General Staff) | Low | High | High |
| HR Manager | Medium | High | High |
| Finance Officer | Medium | High | High |
| Legal & Compliance Officer | Medium | High | High |
| Operations Manager | Medium | High | High |
| System Administrator | High | Medium | High |
| Executive / Senior Management | High | Medium | High |
| Data Protection Officer | High | High | Critical |
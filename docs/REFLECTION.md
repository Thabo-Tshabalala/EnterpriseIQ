# REFLECTION.md

# EnterpriseIQ - Reflection: Challenges in Balancing Stakeholder Needs

---

## Overview

Building requirements for EnterpriseIQ across eight distinct stakeholders revealed several genuine tensions where one stakeholder's priorities directly conflicted with another's. This reflection documents the most significant trade-offs encountered and how they were resolved.

---

## Challenge 1: Openness vs. Security - Employees vs. Data Protection Officer

The most recurring tension was between **general employees** wanting broad, frictionless access to enterprise knowledge and the **Data Protection Officer** requiring strict data boundaries.

Employees wanted a single query interface that could search across all departments - a finance employee asking about a supplier contract should ideally get the answer regardless of which namespace it lives in. However, the DPO made clear that cross-namespace access would violate data segregation principles, particularly for HR data containing personal employee information governed by POPIA and GDPR.

The resolution was **namespace-aware access tied to role** - employees can only query their own department's namespace, but Administrators can query across all namespaces. This preserved data protection compliance without making the system feel overly restrictive for most users. The challenge was articulating this clearly in the requirements so it could not be accidentally bypassed at the UI layer — which led to NFR-11 explicitly requiring namespace isolation to be enforced at the vector store retrieval layer, not just the front end.

---

## Challenge 2: Real-Time Data vs. System Stability - Finance Officer vs. System Administrator

The **Finance Officer** wanted live, real-time stock inventory data — ideally synced from the ERP every few minutes so that stock queries always reflect the current warehouse state. The **System Administrator**, however, was concerned that frequent ERP polling would strain the enterprise database and increase the risk of system instability, particularly during peak business hours.

The resolution was a **configurable sync schedule** defaulting to every 60 minutes, with each synced record carrying a visible timestamp so Finance Officers know exactly how current the data is. This balanced the Finance Officer's accuracy needs with the System Administrator's stability concerns. The reflection here is that requirements engineers must not simply pick one stakeholder's preference — they must find a mechanism that gives each stakeholder enough of what they need while protecting the overall system.

---

## Challenge 3: Audit Transparency vs. Privacy - Executive Management vs. Data Protection Officer

**Executive Management** wanted a comprehensive audit log with full query text, user identities, and retrieved documents — partly for governance and partly to understand how the system was being used. The **DPO** raised concerns that storing full query text indefinitely could itself constitute a data protection risk, particularly if employees inadvertently included personal information in their queries.

The resolution introduced two specific requirements: FR-12 (PII redaction before LLM transmission) and FR-09 (audit log retained for a maximum of 12 months before automated purging). This satisfied the Executive's need for a traceable audit trail while giving the DPO confidence that data was not retained beyond its legitimate purpose — a core principle of both GDPR and POPIA.

---

## Challenge 4: Simplicity vs. Completeness — Employees vs. Legal Officers

**Employees** wanted short, plain-language answers they could act on immediately. **Legal Officers** wanted complete, clause-level citations with the exact source text visible so they could verify contractual accuracy before making decisions.

A single response format could not satisfy both. The resolution was the **expandable source panel** (FR-06) — responses default to a clean, concise answer for general employees, but any user can expand the panel to see the full retrieved text chunks, document names, and page numbers. Legal Officers use this panel routinely; general employees rarely need to. This taught me that UI design decisions are sometimes requirements engineering decisions in disguise.

---

## Key Lessons

**Stakeholders rarely conflict on goals - they conflict on constraints.** Every stakeholder wants EnterpriseIQ to work well. The tensions arise from what they are willing to trade to make it work. Surfacing these constraints early through structured stakeholder analysis prevented them from becoming unresolved ambiguities in the code.

**Measurable acceptance criteria resolve disagreements faster than prose.** When the Finance Officer and System Administrator disagreed on sync frequency, attaching a specific number (60 minutes, configurable) with a visible timestamp gave both parties something concrete to evaluate and accept, rather than debating abstract principles.

**Security and usability are not opposites - they need thoughtful design.** The temptation in requirements engineering is to treat security requirements as constraints that reduce usability. EnterpriseIQ's namespace isolation actually improved usability for most users by reducing information noise — HR staff only see HR content, which makes their queries faster and more relevant.


# REFLECTION- Assignment 5

# EnterpriseIQ - Reflection: Challenges in Translating Requirements to Use Cases and Test Cases

---

Translating the stakeholder requirements from Assignment 4 into use case diagrams and test cases revealed a layer of complexity that the requirements themselves had neatly hidden. Writing a requirement like "the system shall enforce namespace isolation at the retrieval layer" feels precise on paper. Turning it into a use case with actors, flows, and preconditions — and then into a test case that can actually be executed — forces you to confront everything the requirement quietly assumed.

**The first challenge was deciding what counts as a use case.** Not every functional requirement maps cleanly to a use case. FR-12 (PII redaction before LLM calls) is a system behaviour that happens automatically inside another use case — the user never consciously initiates it. Modelling it as a standalone use case felt artificial, but ignoring it felt irresponsible given the DPO's concerns. The solution was to include it as a mandatory `<<include>>` relationship from the Submit Query use case. This taught me that use case modelling is not just a translation exercise — it requires judgment about what is worth making visible to stakeholders and what belongs in the implementation detail.

**The second challenge was granularity.** The assignment required 8 use cases, but EnterpriseIQ has dozens of user interactions if you zoom in far enough. "Submit Natural Language Query" alone contains embedding, retrieval, prompt assembly, LLM API call, PII redaction, and citation formatting. Modelling each of these as a separate use case would have produced a diagram too complex to communicate to non-technical stakeholders. Keeping them as one use case with internal flows visible in the specification (not the diagram) was the right call — but it required resisting the urge to be exhaustive.

**The third challenge was writing meaningful alternative flows.** Many alternative flows I first drafted were trivial — "if the user is not logged in, redirect to login." These add no analytical value. The more useful alternative flows were the ones that surfaced real system risks: what happens when the LLM API times out mid-query? What if the ERP database is unreachable during a sync? What if a document's source is deleted after its embeddings were already queried? Writing these forced me to think about failure modes the requirements had not explicitly addressed, which will directly inform the error handling implementation.

**The fourth challenge was making test cases genuinely testable.** The first draft of several test cases described what should happen without specifying how to make it happen in a controlled way. TC-NFR-002 (namespace penetration test) required thinking through specific attack vectors — not just "try to access the wrong namespace" but exactly which API endpoints, which request parameters, and which bypass routes to test. Without that specificity, the test case would pass trivially by only checking the happy path through the UI.

**The most important lesson from this assignment** is that use cases and test cases are not documentation artifacts — they are thinking tools. Writing them forces you to find the gaps, ambiguities, and assumptions buried in requirements that seemed complete. Every alternative flow I wrote revealed something the basic flow had glossed over. Every test case I struggled to make specific revealed a requirement that was not as precise as it appeared. That friction is the point.
# REFLECTION6.md

# EnterpriseIQ —Assgignment 6 Reflection: Challenges in Agile Planning as a Solo Developer

---

Agile methodology is designed for teams. Scrum has a Product Owner, a Scrum Master, and a Development Team — three distinct roles filled by different people who bring different perspectives, push back on each other's assumptions, and collectively negotiate what gets built and when. Doing all of this alone for EnterpriseIQ forced me to confront how much Agile's value comes from the friction between people, and how difficult it is to manufacture that friction by yourself.

**The hardest part was prioritization without external pressure.** When I sat down to apply MoSCoW to the backlog, every story felt like a Must-have. I built this system's requirements myself — I know why each feature exists, I know which stakeholder asked for it, and I have a natural attachment to seeing it all delivered. There was no Product Owner to say "the Legal Officer's document expiry flagging can wait" and no Development Team to say "that ERP sync is far more complex than you think." I had to simulate that disagreement internally, asking myself: *"If I could only ship three things, which three would make the system actually usable?"* That question cut through the noise faster than any prioritization framework, and it is what pushed US-004 (the RAG query pipeline) to the top — because without it, nothing else matters.

**Effort estimation was humbling.** I initially estimated the RAG query pipeline (US-004) at 5 story points. When I broke it into tasks for the sprint backlog, I counted 9 tasks totalling over 18 hours. That is closer to 8 points on the Fibonacci scale. The gap between how simple a user story sounds and how much work it actually contains is easy to miss when you are both the person writing the story and the person who will implement it. On a real team, a developer would have pushed back immediately. Alone, the miscalibration only became visible when I forced myself to write individual tasks. This is why sprint planning exists — not as bureaucracy, but as a reality check.

**Splitting the Scrum roles was disorienting.** As Product Owner, I wanted to include everything. As Scrum Master, I wanted the process to be rigorous. As the sole developer, I wanted the sprint to be realistic. These three perspectives genuinely conflict. The Product Owner in me added US-006 (ERP sync) to Sprint 1 because Finance stakeholders care deeply about it. The developer in me removed it because it adds significant complexity — live database connectivity, sync scheduling, and failure handling — on top of an already full sprint. The Scrum Master broke the tie by pointing to the sprint goal: *"establish the secure, working core."* ERP sync is not part of the core. It moved to Sprint 2.

**The most useful resistance I encountered was my own impatience.** Every time I wanted to skip writing acceptance criteria because "I already know what done looks like," I forced myself to write it anyway. Every time I wanted to bundle two stories together, I asked whether they were truly independent. That discipline — resisting the urge to shortcut the process when there is no one watching — is what Agile actually requires. A team enforces it socially. Alone, you have to enforce it on yourself. That is harder than it sounds, and more valuable than I expected.

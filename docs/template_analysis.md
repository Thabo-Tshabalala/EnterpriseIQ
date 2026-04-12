# template_analysis.md

# EnterpriseIQ — GitHub Project Template Analysis and Selection

---

## 1. Overview

GitHub Projects offers several pre-built templates designed to support different software development workflows. As part of Assignment 7, this document evaluates four GitHub project templates, compares them against each other, and justifies the selection of the most suitable template for EnterpriseIQ — an intelligent enterprise RAG system requiring structured sprint tracking, issue linking, and Agile workflow management.

---

## 2. Template Comparison Table

| Feature | Basic Kanban | Automated Kanban | Bug Triage | Team Planning |
|---|---|---|---|---|
| **Default Columns** | To Do, In Progress, Done | To Do, In Progress, Done | Needs Triage, High Priority, Low Priority, Closed | To Do, In Progress, Done, Backlog |
| **Number of Columns** | 3 | 3 (expandable) | 4 | 4 |
| **Automation** | None — all movement is manual | Auto-moves issues to "In Progress" when a PR is opened. Auto-moves to "Done" when PR is merged or issue is closed. | Auto-moves issues to "Closed" when issue is closed. Triage labels trigger column moves. | Minimal — some auto-assignment on issue creation |
| **Issue Linking** | Manual | Automatic via PR and issue events | Automatic via issue labels and close events | Manual with milestone support |
| **Sprint Support** | ❌ No built-in sprint tracking | ✅ Supports sprint cycles via automation | ❌ Focused on bug management not sprints | ✅ Milestone-based sprint planning |
| **WIP Limiting** | ❌ No | ❌ No (must be added manually) | ❌ No | ❌ No (must be added manually) |
| **Custom Columns** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Label Support** | ✅ Yes | ✅ Yes | ✅ Yes (core to workflow) | ✅ Yes |
| **Best For** | Small projects with simple workflows | Agile teams running sprints with PRs | Teams managing bug reports and triage | Teams planning work across milestones |
| **Agile Suitability** | ⭐⭐ Basic | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Limited | ⭐⭐⭐⭐ Good |
| **Complexity** | Low | Medium | Low | Medium |

---

## 3. Detailed Template Descriptions

### 3.1 Basic Kanban
The Basic Kanban template provides three columns: To Do, In Progress, and Done. There is no automation — all card movement is performed manually by the developer. It is suitable for very small projects or solo developers managing simple task lists. It offers no sprint support, no automation, and no built-in WIP limiting. For EnterpriseIQ, which has 12 user stories across multiple sprints and requires traceability to requirements, this template is too simple.

### 3.2 Automated Kanban
The Automated Kanban template extends the Basic Kanban with built-in GitHub automation. When a pull request linked to an issue is opened, the issue automatically moves to "In Progress." When the pull request is merged or the issue is closed, the card automatically moves to "Done." This reduces manual board maintenance and ensures the board reflects the actual state of development at all times. It is the most Agile-aligned template available in GitHub Projects and directly supports the sprint-based workflow established in Assignment 6.

### 3.3 Bug Triage
The Bug Triage template is designed for managing reported defects rather than feature development. Its columns (Needs Triage, High Priority, Low Priority, Closed) reflect a bug management workflow rather than a development sprint. While useful for a QA phase, it does not support user story tracking, sprint planning, or the MoSCoW prioritization structure established in Assignment 6. It is not suitable as the primary project template for EnterpriseIQ.

### 3.4 Team Planning
The Team Planning template adds a Backlog column to the standard three-column layout and integrates with GitHub Milestones for sprint-based planning. It supports assigning issues to team members and tracking progress across milestones. It is well-suited for multi-developer teams. For a solo developer, it adds some overhead but the milestone integration is valuable. It ranks second behind Automated Kanban for EnterpriseIQ's needs.

---

## 4. Selected Template: Automated Kanban

**Chosen Template: Automated Kanban**

### Justification

The Automated Kanban template was selected for EnterpriseIQ for the following reasons:

**1. Automation reduces maintenance overhead.**
As a solo developer, manually moving cards across columns after every commit is time-consuming and error-prone. The Automated Kanban's built-in triggers (PR opened → In Progress, PR merged → Done) ensure the board always reflects the true state of development without additional effort.

**2. Direct alignment with Sprint 1 workflow.**
Sprint 1 (defined in Assignment 6) involves implementing authentication, RBAC, document ingestion, the RAG query pipeline, and TLS encryption — all of which will be delivered via pull requests. The Automated Kanban's PR-linked automation maps directly onto this workflow.

**3. Full issue linking and label support.**
All 12 user stories created in Assignment 6 as GitHub Issues can be linked directly to the board. Labels such as `must-have`, `sprint-1`, and `high-priority` defined in Assignment 6 are fully supported and visible on cards.

**4. Extensible with custom columns.**
The template allows custom columns to be added, enabling the addition of a `Testing` column (for test case validation from Assignment 5) and a `Blocked` column (for surfacing impediments during development) — both of which are required by this assignment.

**5. Agile principle alignment.**
The Automated Kanban supports continuous delivery, iterative development, and visual workflow management — all core Agile principles — more comprehensively than any other available GitHub template.

---

## 5. Customizations Applied to the Selected Template

The following customizations were made to the base Automated Kanban template:

| Customization | Reason |
|---|---|
| Added **"Backlog"** column | To hold Should-have and Could-have stories from Assignment 6 that are not in Sprint 1 |
| Added **"Testing"** column | To track user stories that have been implemented and are undergoing test case validation (from Assignment 5 test cases) |
| Added **"Blocked"** column | To surface tasks that cannot progress due to a dependency or impediment — making blockers visible rather than hidden |
| Applied **MoSCoW labels** | `must-have`, `should-have`, `could-have` labels applied to all cards for priority visibility |
| Applied **sprint labels** | `sprint-1` label applied to the 6 Sprint 1 stories for filtering |
| Linked all ** GitHub Issues** | All user stories from Assignment 6 are linked as cards on the board |
| Assigned all issues to **@Thabo-Tshabalala** | All cards assigned to the sole developer |

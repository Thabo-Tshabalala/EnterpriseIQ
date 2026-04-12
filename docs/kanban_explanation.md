# kanban_explanation.md

# EnterpriseIQ — Kanban Board Definition and Explanation

---

## 1. What is a Kanban Board?

A Kanban board is a visual project management tool that represents the flow of work through a series of defined stages, displayed as columns on a board. Each unit of work — whether a task, user story, or bug fix — is represented as a card that moves from left to right across the columns as it progresses through the workflow, from initial creation to final completion.

The word "Kanban" comes from Japanese and roughly translates to "visual signal" or "card." It was originally developed by Toyota in the 1940s as part of their manufacturing system to control inventory and production flow. It was later adopted by the software industry as a lightweight Agile framework for managing development work.

In the context of software engineering, a Kanban board:

- **Uses columns** to represent distinct stages of the development workflow (e.g., Backlog, To Do, In Progress, Testing, Done)
- **Uses cards** to represent individual work items such as user stories, tasks, or bug reports
- **Limits work-in-progress (WIP)** to prevent team members from taking on more tasks than they can complete, reducing bottlenecks
- **Provides real-time visibility** into what is being worked on, what is blocked, and what has been completed
- **Enhances collaboration** by making responsibilities, priorities, and task statuses clear to all stakeholders at a glance

---

## 2. EnterpriseIQ Kanban Board Structure

### 2.1 Column Definitions

The EnterpriseIQ Kanban board uses six columns, each representing a distinct stage in the development lifecycle:

| Column | Purpose | WIP Limit |
|---|---|---|
| **Backlog** | Holds all user stories not yet scheduled for the current sprint. Contains Should-have (Sprint 2) and Could-have (Sprint 3) stories from the product backlog. | No limit |
| **To Do** | Contains all user stories selected for Sprint 1 that have not yet been started. Cards here are ready to be picked up immediately. | 6 cards (Sprint 1 capacity) |
| **In Progress** | Contains user stories actively being implemented. A card moves here when a developer opens a pull request linked to the issue. | 3 cards (focus limit) |
| **Testing** | Contains user stories whose implementation is complete and are undergoing test case validation against the test cases defined in Assignment 5. | 2 cards |
| **Blocked** | Contains user stories that cannot progress due to an external dependency, missing information, or technical impediment. Cards here are visually flagged for immediate attention. | No limit (any blocked card is urgent) |
| **Done** | Contains user stories that have passed testing and whose pull request has been merged into the main branch. Cards move here automatically when a linked PR is merged. | No limit |

---

### 2.2 How the Board Visualizes Workflow

The EnterpriseIQ board visualizes the complete lifecycle of every user story from the moment it is created to the moment it is delivered. At any point in time, looking at the board answers three critical questions:

- **What is planned?** → Cards in Backlog and To Do
- **What is actively being built?** → Cards in In Progress
- **What is being verified?** → Cards in Testing
- **What is stuck?** → Cards in Blocked
- **What is complete?** → Cards in Done

Each card on the board displays the issue title, assigned developer, labels (priority and MoSCoW category), and linked pull request. This means a stakeholder — or the developer themselves — can assess the state of the entire project in seconds without reading a report or attending a meeting.

The flow from left to right mirrors the natural progression of development work: ideas become planned tasks, planned tasks become active development, active development becomes tested features, and tested features become delivered value.

---

### 2.3 How the Board Limits Work-in-Progress (WIP)

WIP limiting is one of the core principles of Kanban. Without WIP limits, developers take on too many tasks simultaneously, leading to context switching, reduced quality, and longer delivery times.

EnterpriseIQ enforces the following WIP limits:

- **In Progress: maximum 3 cards** — This ensures focused, high-quality implementation. If a fourth task needs to start, a card in In Progress must first move to Testing or Done.
- **Testing: maximum 2 cards** — This prevents a backlog of untested features from accumulating, ensuring test cases are run promptly after implementation.
- **To Do: 6 cards** — Capped at the Sprint 1 capacity, ensuring only committed sprint work is visible here and the backlog remains separate.

When a column reaches its WIP limit, the developer must complete or unblock an existing card before pulling a new one. This discipline keeps the board healthy and delivery predictable.

---

### 2.4 How the Board Supports Agile Principles

The EnterpriseIQ Kanban board supports the following core Agile principles:

**Continuous Delivery:**
By limiting WIP and maintaining a clear Testing column, the board encourages completing and delivering features incrementally rather than building everything before testing anything. Each user story moves through the full pipeline independently.

**Adaptability:**
The Blocked column makes impediments immediately visible. When a card moves to Blocked, it signals that the workflow needs to adapt — whether by resolving a dependency, making a design decision, or re-prioritising. This surfaces problems early rather than hiding them inside a long task description.

**Transparency:**
Every stakeholder — including the lecturer reviewing this project — can see the exact state of every user story at any time by viewing the GitHub Project board. There are no hidden tasks or undocumented decisions.

**Collaboration:**
All 12 user story cards are assigned to @Thabo-Tshabalala with labels, priorities, and sprint assignments visible. In a team context, this makes it immediately clear who is responsible for what and prevents duplicate work.

**Iterative Improvement:**
The separation of Backlog from To Do reflects sprint-based iterative delivery. Sprint 1 items are in To Do. Sprint 2 items remain in Backlog until Sprint 1 is complete. This mirrors the iterative sprint cycle defined in Assignment 6 and allows the backlog to be re-prioritised between sprints based on what was learned.

---

## 3. Comparison: GitHub Projects vs Other Kanban Tools

| Feature | GitHub Projects | Trello | Jira |
|---|---|---|---|
| **Code Integration** | ✅ Native — links directly to issues, PRs, commits | ❌ Requires plugins | ✅ Via integrations |
| **Automation** | ✅ Built-in (PR/issue events) | ⚠️ Power-Up required (paid) | ✅ Advanced automation |
| **Free Tier** | ✅ Full features free for public repos | ✅ Limited free tier | ⚠️ Limited free tier |
| **WIP Limits** | ⚠️ Manual only | ⚠️ Manual only | ✅ Built-in |
| **Sprint Planning** | ✅ Via Milestones | ❌ No native sprints | ✅ Full sprint support |
| **Learning Curve** | Low | Very Low | High |
| **Best For** | Solo/small dev teams on GitHub | Non-technical teams | Large enterprise dev teams |

For EnterpriseIQ, GitHub Projects is the most appropriate tool because the entire codebase, issues, and pull requests already live on GitHub. Using a separate tool like Trello or Jira would break traceability between the board and the actual code.

#  Branch Protection Rules

---

## Overview

This document explains the branch protection rules applied to the `main` branch of the EnterpriseIQ repository and justifies why each rule is necessary for a production-grade software project.

---

## Rules Applied to `main`

| Rule | Setting | Purpose |
|---|---|---|
| Require pull request before merging | ✅ Enabled (1 reviewer) | No direct pushes to main |
| Require status checks to pass | ✅ Enabled (`Run All Tests`) | CI must pass before merge |
| Require branches to be up to date | ✅ Enabled | PR must be current with main |
| Dismiss stale reviews on new commits | ✅ Enabled | Fresh approval required after changes |
| Do not allow bypassing the above settings | ✅ Enabled | Applies to admins too |
| Allow force pushes | ❌ Disabled | Protects commit history |
| Allow deletions | ❌ Disabled | Prevents accidental branch deletion |

---

## Why These Rules Matter

### 1. Require Pull Request Reviews
Every change to `main` must be reviewed before it is merged. In a professional team, this ensures a second pair of eyes catches bugs, logic errors, or security issues that the original developer missed. For EnterpriseIQ — a system handling enterprise HR documents, financial records, and legal compliance data — a bug reaching production could have serious consequences for the organisation using the system.

Even as a solo developer, the PR process forces deliberate thinking about each change. Writing a PR description and reviewing your own diff often surfaces issues that were invisible during development.

### 2. Require Status Checks to Pass (CI)
The GitHub Actions CI workflow (`Run All Tests`) must complete successfully before any PR can be merged. This means all 215+ unit and integration tests across Assignments 10–12 must pass. If any test fails — whether it is a service business rule test, a repository CRUD test, or an API integration test — the merge is blocked automatically.

This is the most important rule. It means that `main` always contains code that has been verified to work correctly. Without this, a developer could accidentally merge broken code and disrupt everyone working from the `main` branch.

### 3. Require Branches to Be Up to Date
Before a PR can be merged, the feature branch must include all recent changes from `main`. This prevents situations where two developers each pass CI on their own branches but their combined changes break the system when merged together.

### 4. Dismiss Stale Reviews on New Commits
If a reviewer approves a PR and then the developer pushes additional commits, the approval is dismissed and a new review is required. This prevents the common anti-pattern of getting approval on a clean version of a PR and then sneaking in unreviewed changes before merging.

### 5. No Bypassing for Administrators
Even repository administrators must follow the same rules. This ensures the protection is genuine and not just symbolic. In regulated industries — which EnterpriseIQ targets — audit trails must show that all changes went through the required review and testing process without exception.

### 6. No Force Pushes or Branch Deletion
Force pushes rewrite Git history, which destroys the audit trail of who changed what and when. For a system subject to compliance requirements (GDPR, POPIA), the integrity of the commit history is important. Disabling branch deletion prevents accidental removal of `main`.

---

## How to Set Up Branch Protection on GitHub

1. Go to your repository → **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Under **Branch name pattern** type: `main`
4. Enable the following:
   - ✅ **Require a pull request before merging** → set Approvals to `1`
   - ✅ **Require status checks to pass before merging**
     - Search for and add: `Run All Tests`
   - ✅ **Require branches to be up to date before merging**
   - ✅ **Dismiss stale pull request approvals when new commits are pushed**
   - ✅ **Do not allow bypassing the above settings**
5. Click **Save changes**

---

## Development Workflow

```
feature-branch  →  PR opened  →  CI runs tests  →  Review approved  →  Merge to main  →  CD builds artifact
```

All development happens on feature branches. No one — including the repository owner — pushes directly to `main`.

# Contributing to EnterpriseIQ

Thank you for your interest in contributing to **EnterpriseIQ** — an Intelligent Retrieval-Augmented Generation (RAG) System for Enterprise Knowledge Management. This guide will help you get set up and make your first contribution.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [How to Pick an Issue](#how-to-pick-an-issue)
6. [How to Submit a Pull Request](#how-to-submit-a-pull-request)
7. [Running Tests](#running-tests)
8. [Getting Help](#getting-help)

---

## Prerequisites

Before you start, make sure you have the following installed:

- **Python 3.12+** — [Download here](https://www.python.org/downloads/)
- **Git** — [Download here](https://git-scm.com/downloads)
- **pip** — comes with Python

---

## Installation & Setup

### Step 1 — Fork the repository

Click the **Fork** button at the top right of this page to create your own copy of EnterpriseIQ.

### Step 2 — Clone your fork

```bash
git clone https://github.com/YOUR-USERNAME/EnterpriseIQ.git
cd EnterpriseIQ
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Verify everything works

```bash
pytest tests/ -v
```

All tests should pass before you start making changes.

### Step 5 — Create a feature branch

Never work directly on `main`. Always create a new branch:

```bash
git checkout -b feature/your-feature-name
```

---

## Project Structure

```
EnterpriseIQ/
├── src/                        # Core domain models
├── creational_patterns/        # Design pattern implementations
├── repositories/               # Repository layer (data persistence)
│   └── inmemory/               # In-memory implementations
├── services/                   # Business logic services
├── api/                        # FastAPI REST endpoints
│   └── routers/                # Route handlers per entity
├── tests/                      # All test files
│   ├── services/               # Service layer tests
│   └── api/                    # API integration tests
├── docs/                       # Assignment documentation
└── .github/workflows/          # CI/CD pipeline
```

---

## Coding Standards

### Style
- Follow **PEP 8** — Python's official style guide
- Use **4 spaces** for indentation (no tabs)
- Keep lines under **100 characters**
- Use **descriptive variable names** — avoid single letters except in loops

### Docstrings
Every class and public method must have a docstring:

```python
class UserService:
    """
    Service class for UserAccount business operations.
    All persistence is delegated to the injected repository.
    """

    def create_user(self, email: str, role: Role) -> UserAccount:
        """
        Create a new user account.
        Business rule: Email must be unique across all accounts.
        """
```

### Type hints
All function signatures must include type hints:

```python
def get_user(self, user_id: str) -> UserAccount:
```

### Testing
- Every new feature must include unit tests
- Every bug fix must include a test that reproduces the bug
- Tests go in the `tests/` directory matching the module they test
- Run tests before submitting: `pytest tests/ -v`

---

## How to Pick an Issue

1. Go to the [Issues tab](../../issues)
2. Filter by label:
   - **`good-first-issue`** — simple tasks, great for first-time contributors
   - **`feature-request`** — new features the project needs
   - **`bug`** — something that is broken and needs fixing
3. Comment on the issue saying **"I'd like to work on this"** so others know it's taken
4. Wait for a maintainer to assign it to you before starting

---

## How to Submit a Pull Request

1. Make your changes on your feature branch
2. Run all tests and make sure they pass:
   ```bash
   pytest tests/ -v
   ```
3. Commit your changes with a clear message:
   ```bash
   git add .
   git commit -m "Add: implement FileSystem repository for Document entity"
   ```
4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Go to the original repo on GitHub and click **"New Pull Request"**
6. Fill in the PR template:
   - **What does this PR do?**
   - **Which issue does it close?** (e.g., `Closes #12`)
   - **How was it tested?**
7. Wait for CI to pass — your PR cannot be merged if tests fail

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_all.py -v

# Run with coverage report
pytest tests/ --cov=src --cov=services --cov=api --cov-report=term-missing
```

---

## Getting Help

- Open a [GitHub Issue](../../issues/new) with the label `question`
- Check existing issues — your question may already be answered
- Read the [README.md](./README.md) for system overview and documentation links

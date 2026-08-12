# Getting Started

Welcome to the **Enterprise AI Engineering Lab**.

This repository is a collection of practical engineering experiments that explore how to build, measure, optimize, and operate enterprise AI applications.

The experiments are intentionally designed to be independent, lightweight, and easy to execute. Each program focuses on answering one engineering question, allowing readers to explore concepts progressively without requiring complex infrastructure.

---

# Before You Begin

To run the experiments in this repository, you should have:

- Python 3.13 or later
- An OpenAI API key
- Basic familiarity with Python
- Git (recommended)

No cloud infrastructure, containers, or external databases are required for the initial experiments.

---

# Clone the Repository

```bash
git clone https://github.com/wali-veer/Enterprise-AI-Engineering-Lab.git

cd Enterprise-AI-Engineering-Lab
```

---

# Create a Virtual Environment (Recommended)

Using a virtual environment keeps project dependencies isolated from other Python projects.

### Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

# Install Project Dependencies

Install all required Python packages.

```bash
pip install -r requirements.txt
```

---

# Configure the Environment

Copy the example environment file.

```text
.env.example
```

to

```text
.env
```

Update the following values.

```text
OPENAI_API_KEY=<your_api-key>

OPENAI_MODEL=gpt-5
```

The API key is never committed to GitHub.

---

# Running an Experiment

Each experiment is an independent Python program.

For example:

```bash
python utilities/01_token_usage.py
```

or

```bash
python utilities/02_pricing.py
```

Every experiment can be executed independently.

---

# Repository Layout

```
Enterprise-AI-Engineering-Lab

common/
    Shared reusable modules

docs/
    Repository documentation

utilities/
    Independent engineering experiments

prompts/
    Sample prompts

reports/
    Generated reports (future)

diagrams/
    Architecture diagrams (future)
```

---

# Development Philosophy

The repository follows a few simple principles.

- Keep experiments independent.
- Keep implementations simple.
- Measure everything.
- Prefer engineering evidence over assumptions.
- Improve incrementally through small iterations.

The objective is not simply to build working code.

The objective is to understand the engineering principles required to build production-ready AI systems.

---

# Documentation Structure

The documentation is divided into two categories.

## Repository Documentation

These documents explain concepts that are common across all experiments.

Examples include:

- Architecture
- Engineering Principles
- Project Structure
- Versioning
- Engineering Decisions

These documents evolve slowly and provide the foundation for the repository.

---

## Experiment Documentation

Every engineering experiment includes its own documentation.

Each document explains:

- The engineering problem
- The implementation
- Architecture
- Practical use cases
- Scaling considerations
- Executive insights
- References

This avoids duplication while keeping every experiment self-contained.

---

# Versioning

The repository follows incremental versioning.

Every completed engineering experiment represents a new repository release.

Example:

```
v0.1.0
Token Usage

v0.2.0
Pricing

v0.3.0
Model Comparison
```

Each release includes:

- Executable code
- Documentation
- Sample output
- Engineering observations

---

# Contributing

Suggestions and constructive feedback are always welcome.

If you discover a bug, have an idea for a new engineering experiment, or identify an improvement, please open an issue or submit a pull request.

---

# Need Help?

If you encounter issues while running an experiment:

1. Verify your Python version.
2. Confirm that your virtual environment is activated.
3. Ensure your OpenAI API key is configured correctly.
4. Verify that all dependencies have been installed.

If the issue persists, please create a GitHub issue with:

- Python version
- Operating system
- Experiment name
- Complete error message

This information helps reproduce and resolve issues more efficiently.

---

# Next Document

After completing the setup, the recommended reading order is:

1. Architecture
2. Engineering Principles
3. Project Structure
4. Engineering Decisions

These documents explain the design philosophy behind the repository before exploring individual engineering experiments.
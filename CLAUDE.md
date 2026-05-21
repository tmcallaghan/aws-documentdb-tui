# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python-based Terminal User Interface (TUI) for Amazon DocumentDB that replicates most functionality of the AWS DocumentDB browser-based console. Licensed under Apache 2.0.

## Design Principles

1. **Keep things simple** — favor straightforward implementations over clever abstractions
2. **Minimal external dependencies** — use Python standard library wherever possible; only add a dependency when it provides significant value that would be impractical to replicate
3. **Console parity** — aim to support the same operations available in the AWS DocumentDB web console

## Core Dependencies

- **Python 3.9+**
- **boto3** — AWS SDK for DocumentDB API calls (required, no alternative)
- **textual** — TUI framework (provides widgets, layout, CSS styling, cross-platform support including Windows)

## Target Feature Set (mirrors AWS DocumentDB console)

### Cluster Management
- [ ] List clusters (with status, engine version, instance count, etc.)
- [ ] Create / delete clusters
- [ ] Modify cluster settings (backup retention, maintenance window, engine version, etc.)
- [ ] Start / stop clusters

### Instance Management
- [ ] List instances per cluster
- [ ] Create / delete instances
- [ ] Modify instance class
- [ ] View instance status and endpoints

### Snapshots
- [ ] List snapshots (manual and automated)
- [ ] Create / restore / delete snapshots
- [ ] Copy snapshots

### Parameter Groups
- [ ] List cluster and instance parameter groups
- [ ] View / modify parameters
- [ ] Create / delete parameter groups

### Subnet Groups
- [ ] List subnet groups
- [ ] Create / modify / delete subnet groups

### Event Subscriptions
- [ ] List recent events
- [ ] Filter by source type, category

### Security
- [ ] Manage cluster security (VPC security groups)
- [ ] View/manage encryption settings

### Monitoring
- [ ] Display CloudWatch metrics (CPU, memory, connections, IOPS)
- [ ] Show cluster/instance logs

## Project Structure

```
aws-documentdb-tui/
├── CLAUDE.md
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── main.py             # entry point (argparse, boto3 session)
│   ├── app.py              # Textual App subclass
│   ├── ui/                 # Textual screens and widgets
│   │   ├── __init__.py
│   │   └── views/          # one module per console section
│   ├── aws/                # boto3 wrappers for DocumentDB/CloudWatch
│   │   ├── __init__.py
│   │   ├── docdb.py
│   │   └── cloudwatch.py
│   └── utils.py
└── tests/
```

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.main

# Run tests
python -m pytest tests/

# Lint
python -m flake8 src/ tests/
```

## Coding Conventions

- Use type hints throughout
- Keep modules small and focused (one responsibility per file)
- AWS calls go in `src/aws/` — never call boto3 directly from UI code
- Handle AWS errors gracefully with user-friendly messages in the TUI
- Use dataclasses for internal data models
- No classes where a function will do
- Docstrings on public functions only (keep them brief)

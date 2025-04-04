# Sumo Logic Chores - Project Plan

## Project Overview
This GitHub Action will help with Sumo Logic administration tasks, packaged as a Docker-based Python GitHub Action that can be published to the GitHub Marketplace.

## Tasks

### 🏗️ Initial Setup
- [x] Create repository structure
- [x] Set up GitHub Actions workflow for testing
- [x] Create Dockerfile with Python 3.13
- [x] Create requirements.txt with httpx and other dependencies
- [x] Set up action.yml with inputs and outputs
- [x] Create comprehensive README.md

### 📦 Core Functionality
- [x] Implement task selection mechanism
- [x] Create main.py entry point
- [x] Set up Sumo Logic API client with httpx
- [x] Set up GitHub API client for issue creation
- [x] Implement error handling and logging
- [x] Create utility functions for common operations

### 👥 Role Checker Feature
- [x] Implement user fetching from Sumo Logic API
- [x] Implement role checking logic
- [x] Add output formatting for role check results
- [x] Add testing for role checker

### 🏷️ Monitor Tag Validator
- [x] Implement monitor fetching from Sumo Logic API
- [x] Implement tag validation against allowlist
- [x] Create GitHub issues for non-compliant monitors
- [x] Add testing for monitor tag validator

### 🧪 Testing
- [x] Create unit tests
- [x] Set up integration tests
- [x] Create test fixtures and mocks
- [x] Add test workflow in GitHub Actions

### 📚 Documentation
- [x] Complete README with usage examples
- [x] Add input parameter documentation
- [x] Document output formats
- [x] Create example workflows

### 🚀 Publishing
- [ ] Create release workflow
- [ ] Prepare for GitHub Marketplace
- [ ] Create release notes template
- [ ] Set up version tagging

### 🛠️ Enhancements & Refactoring
- [x] Create proper Python package structure with setup.py
- [x] Configure code quality tools (Black & flake8)
- [x] Implement flexible import system for local and Docker environments
- [x] Add API version compatibility for different Sumo Logic endpoints
- [ ] Complete monitor validator refactoring
- [x] Improve test coverage and organization

## Technical Decisions

### Python 3.13
- Advantages:
  - Latest async features and optimizations
  - Type hints improvements
  - Better error handling
  - Performance enhancements
  - Longer future support timeline

### HTTPX
- Advantages:
  - Native async/await support for parallel API calls
  - Better timeout handling for production reliability
  - HTTP/2 support for more efficient API communication
  - Modern API design
  - Compatible with Python 3.13's latest async features

### Package Structure
- The project is now organized as a proper Python package
- Benefits:
  - Better import handling for different environments
  - Easier local development with `pip install -e .`
  - Clean separation between source code and tests
  - Follows Python standards for package organization

## Directory Structure
```
sumo-chores/
├── action.yml           # GitHub Action configuration
├── Dockerfile           # Docker configuration
├── requirements.txt     # Dependencies
├── setup.py             # Package setup for development installation
├── setup.cfg            # Configuration for tools like flake8
├── README.md
├── PROJECT_PLAN.md
├── src/                 # Source code
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── role_checker.py  # Role checker implementation
│   ├── monitor_validator.py # Monitor tag validator implementation
│   └── github_utils.py  # GitHub utilities
└── tests/               # Tests
    ├── __init__.py
    ├── conftest.py      # Test fixtures
    ├── integration/     # Integration tests
    │   ├── __init__.py
    │   └── test_main.py
    └── unit/            # Unit tests
        ├── __init__.py
        ├── test_github_utils.py
        ├── test_monitor_validator.py
        └── test_role_checker.py
```

## Action Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `tasks` | Yes | Comma-separated list of tasks to run (role-check, monitor-tags, all) |
| `sumo_access_id` | Yes | Sumo Logic Access ID |
| `sumo_access_key` | Yes | Sumo Logic Access Key |
| `role_id` | For role-check | Role ID to check for |
| `tag_allowlist` | For monitor-tags | Comma-separated list of allowed tags |
| `sumo_api_endpoint` | No | Sumo Logic API endpoint (default: https://api.sumologic.com/api) |
| `github_token` | For monitor-tags | GitHub token for creating issues |

## Action Outputs

| Output | Description |
|--------|-------------|
| `users_with_role` | JSON list of users with the specified role |
| `users_count` | Count of users with the specified role |
| `noncompliant_monitors` | JSON list of monitors with non-compliant tags |
| `noncompliant_count` | Count of monitors with non-compliant tags |
| `issues_created` | JSON list of GitHub issues created |

## Current Status

- ✅ Role Checker: Fully implemented and tested
- 🔄 Monitor Validator: Implemented but needs refactoring (tests temporarily disabled)
- ✅ GitHub Utilities: Fully implemented and tested
- ✅ Package Structure: Properly organized with setup.py
- ✅ Code Quality: Black for formatting and flake8 for linting
- ✅ API Compatibility: Works with different Sumo Logic API versions 
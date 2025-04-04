# Sumo Logic Chores - Project Plan

## Project Overview
This GitHub Action will help with Sumo Logic administration tasks, packaged as a Docker-based Python GitHub Action that can be published to the GitHub Marketplace.

## Tasks

### 🏗️ Initial Setup
- [ ] Create repository structure
- [ ] Set up GitHub Actions workflow for testing
- [ ] Create Dockerfile with Python 3.13
- [ ] Create requirements.txt with httpx and other dependencies
- [ ] Set up action.yml with inputs and outputs
- [ ] Create comprehensive README.md

### 📦 Core Functionality
- [ ] Implement task selection mechanism
- [ ] Create main.py entry point
- [ ] Set up Sumo Logic API client with httpx
- [ ] Set up GitHub API client for issue creation
- [ ] Implement error handling and logging
- [ ] Create utility functions for common operations

### 👥 Role Checker Feature
- [ ] Implement user fetching from Sumo Logic API
- [ ] Implement role checking logic
- [ ] Add output formatting for role check results
- [ ] Add testing for role checker

### 🏷️ Monitor Tag Validator
- [ ] Implement monitor fetching from Sumo Logic API
- [ ] Implement tag validation against allowlist
- [ ] Create GitHub issues for non-compliant monitors
- [ ] Add testing for monitor tag validator

### 🧪 Testing
- [ ] Create unit tests
- [ ] Set up integration tests
- [ ] Create test fixtures and mocks
- [ ] Add test workflow in GitHub Actions

### 📚 Documentation
- [ ] Complete README with usage examples
- [ ] Add input parameter documentation
- [ ] Document output formats
- [ ] Create example workflows

### 🚀 Publishing
- [ ] Create release workflow
- [ ] Prepare for GitHub Marketplace
- [ ] Create release notes template
- [ ] Set up version tagging

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

## Directory Structure
```
.
├── action.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── PROJECT_PLAN.md
└── src/
    ├── main.py
    ├── role_checker.py
    ├── monitor_validator.py
    └── github_utils.py
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
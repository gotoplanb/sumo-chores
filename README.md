# Sumo Logic Chores

A GitHub Action for Sumo Logic administration tasks.

## Features

- **Role Checker**: Check which Sumo Logic users have a specific role attached
- **Monitor Tag Validator**: Validate Sumo Logic monitor tags against an allowlist and create GitHub issues for non-compliant monitors

## Usage

### Basic Usage

```yaml
name: Sumo Logic Chores

on:
  schedule:
    - cron: '0 9 * * 1'  # Run every Monday at 9 AM
  workflow_dispatch:
    inputs:
      tasks:
        description: 'Tasks to run (role-check, monitor-tags, all)'
        required: true
        default: 'all'
      role_id:
        description: 'Role ID to check for'
        required: false
      tag_allowlist:
        description: 'Comma-separated list of allowed tags'
        required: false

jobs:
  sumo-chores:
    runs-on: ubuntu-latest
    steps:
      - name: Run Sumo Logic Chores
        uses: gotoplanb/sumo-chores@v1
        with:
          tasks: ${{ github.event.inputs.tasks || 'all' }}
          sumo_access_id: ${{ secrets.SUMO_ACCESS_ID }}
          sumo_access_key: ${{ secrets.SUMO_ACCESS_KEY }}
          role_id: ${{ github.event.inputs.role_id }}
          tag_allowlist: ${{ github.event.inputs.tag_allowlist || 'prod,dev,staging,test' }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### Role Checker Example

```yaml
name: Check Sumo Logic Roles

on:
  workflow_dispatch:
    inputs:
      role_id:
        description: 'Role ID to check for'
        required: true

jobs:
  check-roles:
    runs-on: ubuntu-latest
    steps:
      - name: Check Sumo Logic Roles
        uses: gotoplanb/sumo-chores@v1
        with:
          tasks: role-check
          sumo_access_id: ${{ secrets.SUMO_ACCESS_ID }}
          sumo_access_key: ${{ secrets.SUMO_ACCESS_KEY }}
          role_id: ${{ github.event.inputs.role_id }}
```

### Monitor Tag Validator Example

```yaml
name: Validate Sumo Logic Monitor Tags

on:
  schedule:
    - cron: '0 9 * * 1'  # Run every Monday at 9 AM

jobs:
  validate-tags:
    runs-on: ubuntu-latest
    steps:
      - name: Validate Sumo Logic Monitor Tags
        uses: gotoplanb/sumo-chores@v1
        id: tag-validator
        with:
          tasks: monitor-tags
          sumo_access_id: ${{ secrets.SUMO_ACCESS_ID }}
          sumo_access_key: ${{ secrets.SUMO_ACCESS_KEY }}
          tag_allowlist: prod,dev,staging,test
          github_token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Display Results
        if: steps.tag-validator.outputs.noncompliant_count > 0
        run: |
          echo "Found ${{ steps.tag-validator.outputs.noncompliant_count }} monitors with non-compliant tags"
```

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `tasks` | Yes | Comma-separated list of tasks to run (role-check, monitor-tags, all) |
| `sumo_access_id` | Yes | Sumo Logic Access ID |
| `sumo_access_key` | Yes | Sumo Logic Access Key |
| `role_id` | For role-check | Role ID to check for |
| `tag_allowlist` | For monitor-tags | Comma-separated list of allowed tags |
| `sumo_api_endpoint` | No | Sumo Logic API endpoint (default: https://api.sumologic.com/api) |
| `github_token` | For monitor-tags | GitHub token for creating issues |

## Outputs

| Output | Description |
|--------|-------------|
| `users_with_role` | JSON list of users with the specified role |
| `users_count` | Count of users with the specified role |
| `noncompliant_monitors` | JSON list of monitors with non-compliant tags |
| `noncompliant_count` | Count of monitors with non-compliant tags |
| `issues_created` | JSON list of GitHub issues created |

## Local Development

This project uses a Makefile to simplify development tasks. Make sure you have Python 3.13 installed, as well as `make` and `uv`.

### Setup Development Environment

```bash
# Install as a development package
pip install -e .

# Or use make
make setup
```

### Run Tasks Locally

```bash
# Run role checker
make run-role-check SUMO_ACCESS_ID=your-id SUMO_ACCESS_KEY=your-key ROLE_ID=your-role-id

# Run monitor tag validator
make run-monitor-tags SUMO_ACCESS_ID=your-id SUMO_ACCESS_KEY=your-key TAG_ALLOWLIST=prod,dev,staging,test

# Run all tasks
make run-all SUMO_ACCESS_ID=your-id SUMO_ACCESS_KEY=your-key ROLE_ID=your-role-id TAG_ALLOWLIST=prod,dev,staging,test
```

### Code Quality

```bash
# Format code with Black
make format

# Lint code with flake8
make lint

# Run tests
make test

# Run tests with coverage
make test-cov
```

### Docker Testing

```bash
# Build Docker image
make docker-build

# Run in Docker container
make docker-run TASKS=all SUMO_ACCESS_ID=your-id SUMO_ACCESS_KEY=your-key ROLE_ID=your-role-id TAG_ALLOWLIST=prod,dev,staging,test
```

## Project Structure

The project is organized as a Python package:

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

### Import Handling

The project uses a flexible import system to handle both local development and Docker/GitHub Actions environments:

```python
# Try importing from src package first (for Docker/GitHub Actions)
try:
    from src.github_utils import create_github_issues
# If that fails, try relative imports (for local development)
except ModuleNotFoundError:
    from github_utils import create_github_issues
```

## Testing

The project includes unit and integration tests using pytest. Mock data is provided to simulate API responses.

### Setup for Testing

1. Create a `.env` file with your testing credentials:

   ```bash
   # Either copy and edit .env.example manually
   cp .env.example .env
   
   # Or use the interactive setup script
   ./create_env.py
   ```

2. Install test dependencies:

   ```bash
   make setup
   ```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/unit/test_role_checker.py -v

# Run with coverage report
python -m pytest --cov=src tests/
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
  - `tests/unit/test_role_checker.py`: Tests for the role checker functionality
  - `tests/unit/test_monitor_validator.py`: Tests for the monitor tag validator
  - `tests/unit/test_github_utils.py`: Tests for GitHub utility functions

- **Integration Tests**: Test components working together
  - `tests/integration/test_main.py`: Tests the main module and task selection

### Test Status

- ✅ Role Checker tests are fully implemented and passing
- ⏸️ Monitor Validator tests are temporarily disabled while that module undergoes refactoring

### Mocking and Fixtures

The tests use pytest fixtures defined in `tests/conftest.py` to mock:
- Sumo Logic API responses
- GitHub API interactions
- Environment variables

This allows for testing without actual API calls or credentials.

## License

MIT
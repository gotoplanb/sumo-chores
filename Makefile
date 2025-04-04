.PHONY: setup test lint format clean run-role-check run-monitor-tags run-all

# Default Python version
PYTHON_VERSION := 3.13

# uv virtual environment path
UV_PATH := .venv

# Task selection variables
TASKS ?= all
ROLE_ID ?= 
TAG_ALLOWLIST ?= 
SUMO_ACCESS_ID ?= 
SUMO_ACCESS_KEY ?= 
SUMO_API_ENDPOINT ?= https://api.sumologic.com/api
GITHUB_TOKEN ?= 

# Setup development environment with uv
setup:
	@echo "Setting up development environment with uv..."
	@pip install uv
	@uv venv $(UV_PATH) --python $(PYTHON_VERSION)
	@uv pip install -r requirements.txt
	@uv pip install black pylint pytest pytest-asyncio pytest-mock
	@echo "Development environment setup complete"

# Run tests with pytest
test:
	@echo "Running tests..."
	@. $(UV_PATH)/bin/activate && pytest tests/

# Format code with black
format:
	@echo "Formatting code with Black..."
	@. $(UV_PATH)/bin/activate && black src/ tests/

# Lint code with pylint
lint:
	@echo "Linting code with pylint..."
	@. $(UV_PATH)/bin/activate && pylint src/ tests/

# Clean up build artifacts and virtual environments
clean:
	@echo "Cleaning up..."
	@rm -rf $(UV_PATH) build/ dist/ *.egg-info .pytest_cache .coverage htmlcov
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

# Run the role checker task locally
run-role-check:
	@if [ -z "$(SUMO_ACCESS_ID)" ] || [ -z "$(SUMO_ACCESS_KEY)" ] || [ -z "$(ROLE_ID)" ]; then \
		echo "Error: SUMO_ACCESS_ID, SUMO_ACCESS_KEY, and ROLE_ID are required"; \
		exit 1; \
	fi
	@echo "Running role checker..."
	@. $(UV_PATH)/bin/activate && python src/main.py \
		--tasks role-check \
		--sumo-access-id "$(SUMO_ACCESS_ID)" \
		--sumo-access-key "$(SUMO_ACCESS_KEY)" \
		--role-id "$(ROLE_ID)" \
		--sumo-api-endpoint "$(SUMO_API_ENDPOINT)"

# Run the monitor tag validator task locally
run-monitor-tags:
	@if [ -z "$(SUMO_ACCESS_ID)" ] || [ -z "$(SUMO_ACCESS_KEY)" ] || [ -z "$(TAG_ALLOWLIST)" ]; then \
		echo "Error: SUMO_ACCESS_ID, SUMO_ACCESS_KEY, and TAG_ALLOWLIST are required"; \
		exit 1; \
	fi
	@echo "Running monitor tag validator..."
	@. $(UV_PATH)/bin/activate && python src/main.py \
		--tasks monitor-tags \
		--sumo-access-id "$(SUMO_ACCESS_ID)" \
		--sumo-access-key "$(SUMO_ACCESS_KEY)" \
		--tag-allowlist "$(TAG_ALLOWLIST)" \
		--sumo-api-endpoint "$(SUMO_API_ENDPOINT)" \
		$(if $(GITHUB_TOKEN),--github-token "$(GITHUB_TOKEN)",)

# Run all tasks locally
run-all:
	@if [ -z "$(SUMO_ACCESS_ID)" ] || [ -z "$(SUMO_ACCESS_KEY)" ] || [ -z "$(ROLE_ID)" ] || [ -z "$(TAG_ALLOWLIST)" ]; then \
		echo "Error: SUMO_ACCESS_ID, SUMO_ACCESS_KEY, ROLE_ID, and TAG_ALLOWLIST are required"; \
		exit 1; \
	fi
	@echo "Running all tasks..."
	@. $(UV_PATH)/bin/activate && python src/main.py \
		--tasks all \
		--sumo-access-id "$(SUMO_ACCESS_ID)" \
		--sumo-access-key "$(SUMO_ACCESS_KEY)" \
		--role-id "$(ROLE_ID)" \
		--tag-allowlist "$(TAG_ALLOWLIST)" \
		--sumo-api-endpoint "$(SUMO_API_ENDPOINT)" \
		$(if $(GITHUB_TOKEN),--github-token "$(GITHUB_TOKEN)",)

# Build Docker image for local testing
docker-build:
	@echo "Building Docker image..."
	@docker build -t sumo-chores:local .

# Run tasks in Docker container
docker-run:
	@if [ -z "$(TASKS)" ]; then \
		echo "Error: TASKS is required"; \
		exit 1; \
	fi
	@if [ "$(TASKS)" = "role-check" ] && [ -z "$(ROLE_ID)" ]; then \
		echo "Error: ROLE_ID is required for role-check task"; \
		exit 1; \
	fi
	@if [ "$(TASKS)" = "monitor-tags" ] && [ -z "$(TAG_ALLOWLIST)" ]; then \
		echo "Error: TAG_ALLOWLIST is required for monitor-tags task"; \
		exit 1; \
	fi
	@if [ "$(TASKS)" = "all" ] && ([ -z "$(ROLE_ID)" ] || [ -z "$(TAG_ALLOWLIST)" ]); then \
		echo "Error: ROLE_ID and TAG_ALLOWLIST are required for all tasks"; \
		exit 1; \
	fi
	@if [ -z "$(SUMO_ACCESS_ID)" ] || [ -z "$(SUMO_ACCESS_KEY)" ]; then \
		echo "Error: SUMO_ACCESS_ID and SUMO_ACCESS_KEY are required"; \
		exit 1; \
	fi
	@echo "Running tasks in Docker container..."
	@docker run --rm \
		-e INPUT_TASKS="$(TASKS)" \
		-e INPUT_SUMO_ACCESS_ID="$(SUMO_ACCESS_ID)" \
		-e INPUT_SUMO_ACCESS_KEY="$(SUMO_ACCESS_KEY)" \
		-e INPUT_ROLE_ID="$(ROLE_ID)" \
		-e INPUT_TAG_ALLOWLIST="$(TAG_ALLOWLIST)" \
		-e INPUT_SUMO_API_ENDPOINT="$(SUMO_API_ENDPOINT)" \
		-e INPUT_GITHUB_TOKEN="$(GITHUB_TOKEN)" \
		sumo-chores:local

# Help target to show available make targets
help:
	@echo "Available targets:"
	@echo "  setup               - Set up development environment with uv"
	@echo "  test                - Run tests with pytest"
	@echo "  format              - Format code with Black"
	@echo "  lint                - Lint code with pylint"
	@echo "  clean               - Clean up build artifacts and virtual environments"
	@echo "  run-role-check      - Run the role checker task locally"
	@echo "  run-monitor-tags    - Run the monitor tag validator task locally"
	@echo "  run-all             - Run all tasks locally"
	@echo "  docker-build        - Build Docker image for local testing"
	@echo "  docker-run          - Run tasks in Docker container"
	@echo ""
	@echo "Environment variables for run targets:"
	@echo "  TASKS               - Comma-separated list of tasks to run (required for docker-run)"
	@echo "  SUMO_ACCESS_ID      - Sumo Logic access ID (required)"
	@echo "  SUMO_ACCESS_KEY     - Sumo Logic access key (required)"
	@echo "  ROLE_ID             - Role ID to check for (required for role-check)"
	@echo "  TAG_ALLOWLIST       - Comma-separated list of allowed tags (required for monitor-tags)"
	@echo "  SUMO_API_ENDPOINT   - Sumo Logic API endpoint (optional)"
	@echo "  GITHUB_TOKEN        - GitHub token for creating issues (optional for monitor-tags)"
	@echo ""
	@echo "Example usage:"
	@echo "  make run-role-check SUMO_ACCESS_ID=your-id SUMO_ACCESS_KEY=your-key ROLE_ID=your-role-id"
	@echo "  make docker-run TASKS=monitor-tags SUMO_ACCESS_ID=your-id SUMO_ACCESS_KEY=your-key TAG_ALLOWLIST=prod,dev"

# Default target
default: help 
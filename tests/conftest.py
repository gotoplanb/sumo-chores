"""
Pytest configuration file with fixtures for Sumo Logic Chores tests
"""

import os
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock

import pytest
import httpx


# --- Environment Setup Fixtures ---


@pytest.fixture
def load_env():
    """Load environment variables from .env file if it exists"""
    # Check if .env file exists
    if os.path.exists(".env"):
        # Read file and set environment variables
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value


# --- Mock Data Fixtures ---


@pytest.fixture
def mock_users_data() -> Dict[str, Any]:
    """Sample users data response from Sumo Logic API"""
    return {
        "data": [
            {
                "id": "0000000000000001",
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "isActive": True,
                "isLocked": False,
                "roleIds": ["0000000000AAAAA1"],
                "createdAt": "2023-01-01T00:00:00.000Z",
                "modifiedAt": "2023-01-01T00:00:00.000Z",
            },
            {
                "id": "0000000000000002",
                "firstName": "Jane",
                "lastName": "Smith",
                "email": "jane.smith@example.com",
                "isActive": True,
                "isLocked": False,
                "roleIds": ["0000000000BBBBB2"],
                "createdAt": "2023-01-02T00:00:00.000Z",
                "modifiedAt": "2023-01-02T00:00:00.000Z",
            },
            {
                "id": "0000000000000003",
                "firstName": "Bob",
                "lastName": "Johnson",
                "email": "bob.johnson@example.com",
                "isActive": True,
                "isLocked": False,
                "roleIds": ["0000000000AAAAA1", "0000000000CCCCC3"],
                "createdAt": "2023-01-03T00:00:00.000Z",
                "modifiedAt": "2023-01-03T00:00:00.000Z",
            },
        ]
    }


@pytest.fixture
def mock_roles_data() -> List[Dict[str, Any]]:
    """Sample role data responses for each user from Sumo Logic API"""
    return [
        {
            "data": [
                {
                    "id": "0000000000AAAAA1",
                    "name": "Administrator",
                    "description": "Full admin access",
                    "filterPredicate": None,
                    "users": [],
                }
            ]
        },
        {
            "data": [
                {
                    "id": "0000000000BBBBB2",
                    "name": "Analyst",
                    "description": "Analytics access",
                    "filterPredicate": None,
                    "users": [],
                }
            ]
        },
        {
            "data": [
                {
                    "id": "0000000000AAAAA1",
                    "name": "Administrator",
                    "description": "Full admin access",
                    "filterPredicate": None,
                    "users": [],
                },
                {
                    "id": "0000000000CCCCC3",
                    "name": "ReadOnly",
                    "description": "Read-only access",
                    "filterPredicate": None,
                    "users": [],
                },
            ]
        },
    ]


@pytest.fixture
def mock_monitors_data() -> Dict[str, Any]:
    """Sample monitors data response from Sumo Logic API"""
    return {
        "data": [
            {
                "id": "0000000000MONITOR1",
                "name": "API Latency Monitor",
                "description": "Monitors API response times",
                "tags": ["prod", "api", "latency"],
                "contentType": {
                    "type": "MonitorsLibraryMonitor",
                },
                "createdAt": "2023-02-01T00:00:00.000Z",
                "createdBy": "0000000000000001",
                "modifiedAt": "2023-02-01T12:00:00.000Z",
                "modifiedBy": "0000000000000001",
                "parentId": "0000000000FOLDER1",
            },
            {
                "id": "0000000000MONITOR2",
                "name": "Database CPU Monitor",
                "description": "Monitors database CPU usage",
                "tags": ["dev", "database", "performance"],
                "contentType": {
                    "type": "MonitorsLibraryMonitor",
                },
                "createdAt": "2023-02-02T00:00:00.000Z",
                "createdBy": "0000000000000002",
                "modifiedAt": "2023-02-02T12:00:00.000Z",
                "modifiedBy": "0000000000000002",
                "parentId": "0000000000FOLDER1",
            },
            {
                "id": "0000000000MONITOR3",
                "name": "Network Traffic Monitor",
                "description": "Monitors network traffic",
                "tags": ["prod", "network", "traffic", "critical"],
                "contentType": {
                    "type": "MonitorsLibraryMonitor",
                },
                "createdAt": "2023-02-03T00:00:00.000Z",
                "createdBy": "0000000000000003",
                "modifiedAt": "2023-02-03T12:00:00.000Z",
                "modifiedBy": "0000000000000003",
                "parentId": "0000000000FOLDER2",
            },
            {
                "id": "0000000000MONITOR4",
                "name": "Memory Usage Monitor",
                "description": "Monitors server memory usage",
                "tags": [],
                "contentType": {"type": "MonitorsLibraryMonitor"},
                "createdAt": "2023-02-04T00:00:00.000Z",
                "createdBy": "0000000000000001",
                "modifiedAt": "2023-02-04T12:00:00.000Z",
                "modifiedBy": "0000000000000001",
                "parentId": "0000000000FOLDER2",
            },
        ]
    }


# --- Mock Client Fixtures ---


@pytest.fixture
def mock_httpx_client(mock_users_data, mock_roles_data, mock_monitors_data):
    """Create a mocked httpx client for testing"""

    class MockResponse:
        def __init__(self, data, status_code=200):
            self.status_code = status_code
            self._data = data

        def json(self):
            return self._data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError(
                    f"HTTP Error {self.status_code}",
                    request=httpx.Request("GET", "https://example.com"),
                    response=self,
                )

    async def mock_get(url, *args, **kwargs):
        if "/v1/users" in url and not url.endswith("/roles"):
            return MockResponse(mock_users_data)
        elif "/v1/users/" in url and url.endswith("/roles"):
            # Extract user ID from URL
            user_id = url.split("/v1/users/")[1].split("/roles")[0]
            # Map user ID to a mock roles response
            user_index = (
                int(user_id[-1]) - 1
            )  # Get last character and convert to zero-based index
            if 0 <= user_index < len(mock_roles_data):
                return MockResponse(mock_roles_data[user_index])
            return MockResponse({"data": []})
        elif "/v1/monitors" in url:
            return MockResponse(mock_monitors_data)
        return MockResponse({"data": []})

    # Create async mock client
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=mock_get)

    # Mock enter/exit for async context manager
    mock_client.__aenter__.return_value = mock_client

    return mock_client


@pytest.fixture
def mock_github_client():
    """Create a mocked github client for testing"""
    mock_repo = MagicMock()

    # Mock issue creation
    mock_issue = MagicMock()
    mock_issue.html_url = "https://github.com/owner/repo/issues/1"
    mock_issue.number = 1
    mock_issue.title = "Test Issue"

    # Mock get_issues to return empty list (no existing issues)
    mock_repo.get_issues.return_value = []

    # Mock create_issue to return mock issue
    mock_repo.create_issue.return_value = mock_issue

    # Mock Github client
    mock_github = MagicMock()
    mock_github.get_repo.return_value = mock_repo

    return mock_github

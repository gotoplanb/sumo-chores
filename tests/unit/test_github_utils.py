"""
Unit tests for github_utils module
"""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock

from src.github_utils import set_github_output, create_github_issues


def test_set_github_output_not_in_github_actions():
    """Test set_github_output when not running in GitHub Actions"""

    # Ensure GITHUB_ACTIONS environment variable is not set
    with patch.dict(os.environ, {}, clear=True):
        # Call set_github_output with sample results
        set_github_output({"test_key": "test_value"})
        # Not much we can assert here, but the function should not raise an exception


def test_set_github_output_without_output_file():
    """Test set_github_output when GITHUB_OUTPUT is not set"""

    # Set GITHUB_ACTIONS to true but don't set GITHUB_OUTPUT
    with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True):
        # Capture print output
        with patch("builtins.print") as mock_print:
            # Call set_github_output with sample results
            set_github_output({"test_key": "test_value"})

            # Check that print was called with the expected output
            mock_print.assert_called_once_with("::set-output name=test_key::test_value")


def test_set_github_output_with_output_file():
    """Test set_github_output when GITHUB_OUTPUT is set"""

    # Create a temporary file to use as GITHUB_OUTPUT
    with tempfile.NamedTemporaryFile(mode="w+") as temp_file:
        # Set environment variables
        with patch.dict(
            os.environ,
            {"GITHUB_ACTIONS": "true", "GITHUB_OUTPUT": temp_file.name},
            clear=True,
        ):
            # Call set_github_output with sample results
            set_github_output(
                {"single_line": "test_value", "multi_line": "line1\nline2\nline3"}
            )

            # Read the output file
            temp_file.seek(0)
            output_content = temp_file.read()

            # Check that the output was written correctly
            assert "single_line=test_value" in output_content
            assert "multi_line<<EOF" in output_content
            assert "line1\nline2\nline3\nEOF" in output_content


@pytest.mark.asyncio
async def test_create_github_issues_success(mock_github_client):
    """Test create_github_issues successful issue creation"""

    # Sample monitor data with non-compliant tags
    monitors = [
        {
            "id": "0000000000MONITOR1",
            "name": "API Latency Monitor",
            "compliant_tags": ["prod"],
            "non_compliant_tags": ["api", "latency"],
            "url": "https://service.api.sumologic.com/ui/#/monitor/edit/0000000000MONITOR1",
        },
        {
            "id": "0000000000MONITOR3",
            "name": "Network Traffic Monitor",
            "compliant_tags": ["prod"],
            "non_compliant_tags": ["network", "traffic", "critical"],
            "url": "https://service.api.sumologic.com/ui/#/monitor/edit/0000000000MONITOR3",
        },
    ]

    # Mock GitHub repository and issue creation
    with patch("github.Github", return_value=mock_github_client):
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/repo"}, clear=True):
            created_issues = await create_github_issues(
                monitors=monitors, github_token="fake_token"
            )

            # Check that issues were created
            assert len(created_issues) == 2

            # Check issue details
            for issue in created_issues:
                assert "url" in issue
                assert "number" in issue
                assert "title" in issue
                assert "monitor_id" in issue
                assert "monitor_name" in issue
                assert issue["status"] == "created"


@pytest.mark.asyncio
async def test_create_github_issues_with_existing_issues(mock_github_client):
    """Test create_github_issues when issues already exist"""

    # Sample monitor data
    monitors = [
        {
            "id": "0000000000MONITOR1",
            "name": "API Latency Monitor",
            "compliant_tags": ["prod"],
            "non_compliant_tags": ["api", "latency"],
            "url": "https://service.api.sumologic.com/ui/#/monitor/edit/0000000000MONITOR1",
        }
    ]

    # Mock existing issues
    mock_issue = MagicMock()
    mock_issue.html_url = "https://github.com/owner/repo/issues/1"
    mock_issue.number = 1
    mock_issue.title = (
        "Non-compliant tags found in Sumo Logic monitor: API Latency Monitor"
    )

    mock_repo = mock_github_client.get_repo.return_value
    mock_repo.get_issues.return_value = [mock_issue]

    # Mock GitHub repository and issue creation
    with patch("github.Github", return_value=mock_github_client):
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/repo"}, clear=True):
            created_issues = await create_github_issues(
                monitors=monitors, github_token="fake_token"
            )

            # Check that issues were found but not created
            assert len(created_issues) == 1
            assert created_issues[0]["status"] == "existing"
            assert created_issues[0]["number"] == 1


@pytest.mark.asyncio
async def test_create_github_issues_missing_repo_info():
    """Test create_github_issues when repository information is missing"""

    # Sample monitor data
    monitors = [
        {
            "id": "0000000000MONITOR1",
            "name": "API Latency Monitor",
            "compliant_tags": ["prod"],
            "non_compliant_tags": ["api", "latency"],
            "url": "https://service.api.sumologic.com/ui/#/monitor/edit/0000000000MONITOR1",
        }
    ]

    # Mock GitHub client
    mock_github = MagicMock()

    # Clear environment and don't provide repo info
    with patch("github.Github", return_value=mock_github):
        with patch.dict(os.environ, {}, clear=True):
            created_issues = await create_github_issues(
                monitors=monitors, github_token="fake_token"
            )

            # Check that no issues were created due to missing repo info
            assert len(created_issues) == 0

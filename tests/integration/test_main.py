"""
Integration tests for main module
"""

import os
import json
import pytest
from unittest.mock import patch, AsyncMock

from src.main import main_async


@pytest.mark.asyncio
async def test_main_async_role_check(mock_httpx_client):
    """Test main_async with role-check task"""

    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        # Mock create_github_issues to prevent actual issue creation
        with patch("src.monitor_validator.create_github_issues", return_value=[]):
            # Run main_async with role-check task
            results = {}

            # Add a capture for set_github_output
            def capture_output(output_results):
                results.update(output_results)
                return None

            with patch("src.main.set_github_output", side_effect=capture_output):
                await main_async(
                    tasks="role-check",
                    sumo_access_id="test_id",
                    sumo_access_key="test_key",
                    role_id="0000000000AAAAA1",
                    tag_allowlist=None,
                    sumo_api_endpoint="https://api.sumologic.com/api",
                )

                # Check that role check results are present
                assert "users_with_role" in results
                assert "users_count" in results

                # Verify the data
                users_with_role = json.loads(results["users_with_role"])
                assert (
                    results["users_count"] == 2
                )  # Users 1 and 3 have the Administrator role
                assert len(users_with_role) == 2

                # But monitor tag results are not present
                assert "non_compliant_monitors" not in results
                assert "non_compliant_count" not in results


@pytest.mark.asyncio
async def test_main_async_monitor_tags(mock_httpx_client):
    """Test main_async with monitor-tags task"""

    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        # Mock create_github_issues to prevent actual issue creation
        with patch("src.monitor_validator.create_github_issues", return_value=[]):
            # Run main_async with monitor-tags task
            results = {}

            # Add a capture for set_github_output
            def capture_output(output_results):
                results.update(output_results)
                return None

            with patch("src.main.set_github_output", side_effect=capture_output):
                await main_async(
                    tasks="monitor-tags",
                    sumo_access_id="test_id",
                    sumo_access_key="test_key",
                    role_id=None,
                    tag_allowlist="prod,dev",
                    sumo_api_endpoint="https://api.sumologic.com/api",
                )

                # Check that monitor tag results are present
                assert "non_compliant_monitors" in results
                assert "non_compliant_count" in results

                # Verify the data
                non_compliant_monitors = json.loads(results["non_compliant_monitors"])
                assert (
                    results["non_compliant_count"] == 3
                )  # Three monitors have non-compliant tags
                assert len(non_compliant_monitors) == 3

                # But role check results are not present
                assert "users_with_role" not in results
                assert "users_count" not in results


@pytest.mark.asyncio
async def test_main_async_all_tasks(mock_httpx_client):
    """Test main_async with all tasks"""

    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        # Mock create_github_issues to prevent actual issue creation
        with patch("src.monitor_validator.create_github_issues", return_value=[]):
            # Run main_async with all tasks
            results = {}

            # Add a capture for set_github_output
            def capture_output(output_results):
                results.update(output_results)
                return None

            with patch("src.main.set_github_output", side_effect=capture_output):
                await main_async(
                    tasks="all",
                    sumo_access_id="test_id",
                    sumo_access_key="test_key",
                    role_id="0000000000AAAAA1",
                    tag_allowlist="prod,dev",
                    sumo_api_endpoint="https://api.sumologic.com/api",
                )

                # Check that both sets of results are present
                assert "users_with_role" in results
                assert "users_count" in results
                assert "non_compliant_monitors" in results
                assert "non_compliant_count" in results

                # Verify the role check data
                users_with_role = json.loads(results["users_with_role"])
                assert results["users_count"] == 2
                assert len(users_with_role) == 2

                # Verify the monitor tag data
                non_compliant_monitors = json.loads(results["non_compliant_monitors"])
                assert results["non_compliant_count"] == 3
                assert len(non_compliant_monitors) == 3


@pytest.mark.asyncio
async def test_main_async_missing_role_id():
    """Test main_async when role-check is selected but role_id is missing"""

    with pytest.raises(SystemExit):
        await main_async(
            tasks="role-check",
            sumo_access_id="test_id",
            sumo_access_key="test_key",
            role_id=None,  # Missing role_id
            tag_allowlist=None,
            sumo_api_endpoint="https://api.sumologic.com/api",
        )


@pytest.mark.asyncio
async def test_main_async_missing_tag_allowlist():
    """Test main_async when monitor-tags is selected but tag_allowlist is missing"""

    with pytest.raises(SystemExit):
        await main_async(
            tasks="monitor-tags",
            sumo_access_id="test_id",
            sumo_access_key="test_key",
            role_id=None,
            tag_allowlist=None,  # Missing tag_allowlist
            sumo_api_endpoint="https://api.sumologic.com/api",
        )

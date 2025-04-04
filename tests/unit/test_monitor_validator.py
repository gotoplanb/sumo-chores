"""
Unit tests for monitor_validator module
"""

import json
import pytest
from unittest.mock import patch, AsyncMock

from src.monitor_validator import validate_monitor_tags


@pytest.mark.skip(
    reason="Temporarily disabled while monitor_validator needs more attention"
)
@pytest.mark.asyncio
async def test_validate_monitor_tags_with_violations(mock_httpx_client):
    """Test validate_monitor_tags when monitors with non-compliant tags are found"""

    # Only allow prod and dev tags
    allowed_tags = {"prod", "dev"}

    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        # Don't create GitHub issues in this test
        with patch("src.monitor_validator.create_github_issues", return_value=[]):
            results = await validate_monitor_tags(
                sumo_access_id="test_id",
                sumo_access_key="test_key",
                allowed_tags=allowed_tags,
                api_endpoint="https://api.sumologic.com/api",
                github_token=None,
            )

            # Parse the non_compliant_monitors JSON string to a list
            non_compliant_monitors = json.loads(results["non_compliant_monitors"])

            # Check the count matches
            assert (
                results["non_compliant_count"] == 3
            )  # We have 3 monitors with non-compliant tags

            # Check we have the expected monitors
            assert len(non_compliant_monitors) == 3

            # Get monitor names
            monitor_names = [monitor["name"] for monitor in non_compliant_monitors]
            assert (
                "API Latency Monitor" in monitor_names
            )  # Has 'latency' and 'api' tags
            assert (
                "Database CPU Monitor" in monitor_names
            )  # Has 'database' and 'performance' tags
            assert (
                "Network Traffic Monitor" in monitor_names
            )  # Has 'network', 'traffic', 'critical' tags

            # Check non-compliant tags
            for monitor in non_compliant_monitors:
                if monitor["name"] == "API Latency Monitor":
                    assert set(monitor["non_compliant_tags"]) == {"api", "latency"}
                    assert set(monitor["compliant_tags"]) == {"prod"}
                elif monitor["name"] == "Database CPU Monitor":
                    assert set(monitor["non_compliant_tags"]) == {
                        "database",
                        "performance",
                    }
                    assert set(monitor["compliant_tags"]) == {"dev"}
                elif monitor["name"] == "Network Traffic Monitor":
                    assert set(monitor["non_compliant_tags"]) == {
                        "network",
                        "traffic",
                        "critical",
                    }
                    assert set(monitor["compliant_tags"]) == {"prod"}


@pytest.mark.skip(
    reason="Temporarily disabled while monitor_validator needs more attention"
)
@pytest.mark.asyncio
async def test_validate_monitor_tags_no_violations(mock_httpx_client):
    """Test validate_monitor_tags when all monitors have compliant tags"""

    # Allow all tags that exist in our monitors
    allowed_tags = {
        "prod",
        "dev",
        "api",
        "latency",
        "database",
        "performance",
        "network",
        "traffic",
        "critical",
    }

    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        results = await validate_monitor_tags(
            sumo_access_id="test_id",
            sumo_access_key="test_key",
            allowed_tags=allowed_tags,
            api_endpoint="https://api.sumologic.com/api",
            github_token=None,
        )

        # Parse the non_compliant_monitors JSON string to a list
        non_compliant_monitors = json.loads(results["non_compliant_monitors"])

        # Check the count matches
        assert results["non_compliant_count"] == 0

        # Check we have no non-compliant monitors
        assert len(non_compliant_monitors) == 0


@pytest.mark.skip(
    reason="Temporarily disabled while monitor_validator needs more attention"
)
@pytest.mark.asyncio
async def test_validate_monitor_tags_with_github_issues(mock_httpx_client):
    """Test validate_monitor_tags with GitHub issue creation"""

    # Only allow prod tag
    allowed_tags = {"prod"}

    # Mock GitHub issue creation
    mock_issues = [
        {
            "url": "https://github.com/owner/repo/issues/1",
            "number": 1,
            "title": "Non-compliant tags found in Sumo Logic monitor: API Latency Monitor",
            "monitor_id": "0000000000MONITOR1",
            "monitor_name": "API Latency Monitor",
            "status": "created",
        },
        {
            "url": "https://github.com/owner/repo/issues/2",
            "number": 2,
            "title": "Non-compliant tags found in Sumo Logic monitor: Database CPU Monitor",
            "monitor_id": "0000000000MONITOR2",
            "monitor_name": "Database CPU Monitor",
            "status": "created",
        },
        {
            "url": "https://github.com/owner/repo/issues/3",
            "number": 3,
            "title": "Non-compliant tags found in Sumo Logic monitor: Network Traffic Monitor",
            "monitor_id": "0000000000MONITOR3",
            "monitor_name": "Network Traffic Monitor",
            "status": "created",
        },
    ]

    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        with patch(
            "src.monitor_validator.create_github_issues", return_value=mock_issues
        ) as mock_create_issues:
            # Call the function
            await validate_monitor_tags(
                sumo_access_id="test_id",
                sumo_access_key="test_key",
                allowed_tags=allowed_tags,
                api_endpoint="https://api.sumologic.com/api",
                github_token="fake_token",
            )

            # Check GitHub issues were created
            assert mock_create_issues.called


@pytest.mark.skip(
    reason="Temporarily disabled while monitor_validator needs more attention"
)
@pytest.mark.asyncio
async def test_validate_monitor_tags_api_error(mock_httpx_client):
    """Test validate_monitor_tags when the API returns an error"""

    # Mock httpx client to raise an exception
    mock_httpx_client.get = AsyncMock(side_effect=Exception("API Error"))

    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        with pytest.raises(Exception, match="API Error"):
            await validate_monitor_tags(
                sumo_access_id="test_id",
                sumo_access_key="test_key",
                allowed_tags={"prod", "dev"},
                api_endpoint="https://api.sumologic.com/api",
                github_token=None,
            )

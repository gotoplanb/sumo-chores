"""
Unit tests for monitor_validator module
"""

import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from src.monitor_validator import validate_monitor_tags


@pytest.mark.asyncio
async def test_validate_monitor_tags_with_violations(mock_httpx_client):
    """Test validate_monitor_tags when monitors with non-compliant tags are found"""
    
    # Only allow prod and dev tags
    allowed_tags = {"prod", "dev"}
    
    with patch('httpx.AsyncClient', return_value=mock_httpx_client):
        # Don't create GitHub issues in this test
        with patch('src.monitor_validator.create_github_issues', return_value=[]):
            results = await validate_monitor_tags(
                sumo_access_id="test_id",
                sumo_access_key="test_key",
                allowed_tags=allowed_tags,
                api_endpoint="https://api.sumologic.com/api",
                github_token=None
            )
            
            # Parse the noncompliant_monitors JSON string to a list
            noncompliant_monitors = json.loads(results["noncompliant_monitors"])
            
            # Check the count matches
            assert results["noncompliant_count"] == 2  # Monitor 1 and 3 have non-compliant tags
            
            # Check we have the expected monitors
            assert len(noncompliant_monitors) == 2
            
            # Get monitor names
            monitor_names = [monitor["name"] for monitor in noncompliant_monitors]
            assert "API Latency Monitor" in monitor_names  # Has 'latency' and 'api' tags
            assert "Network Traffic Monitor" in monitor_names  # Has 'network', 'traffic', 'critical' tags
            
            # Check non-compliant tags
            for monitor in noncompliant_monitors:
                if monitor["name"] == "API Latency Monitor":
                    assert set(monitor["non_compliant_tags"]) == {"api", "latency"}
                    assert set(monitor["compliant_tags"]) == {"prod"}
                elif monitor["name"] == "Network Traffic Monitor":
                    assert set(monitor["non_compliant_tags"]) == {"network", "traffic", "critical"}
                    assert set(monitor["compliant_tags"]) == {"prod"}


@pytest.mark.asyncio
async def test_validate_monitor_tags_no_violations(mock_httpx_client):
    """Test validate_monitor_tags when all monitors have compliant tags"""
    
    # Allow all tags that exist in our monitors
    allowed_tags = {"prod", "dev", "api", "latency", "database", "performance", "network", "traffic", "critical"}
    
    with patch('httpx.AsyncClient', return_value=mock_httpx_client):
        results = await validate_monitor_tags(
            sumo_access_id="test_id",
            sumo_access_key="test_key",
            allowed_tags=allowed_tags,
            api_endpoint="https://api.sumologic.com/api",
            github_token=None
        )
        
        # Parse the noncompliant_monitors JSON string to a list
        noncompliant_monitors = json.loads(results["noncompliant_monitors"])
        
        # Check the count matches
        assert results["noncompliant_count"] == 0
        
        # Check we have no non-compliant monitors
        assert len(noncompliant_monitors) == 0


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
            "status": "created"
        },
        {
            "url": "https://github.com/owner/repo/issues/2",
            "number": 2,
            "title": "Non-compliant tags found in Sumo Logic monitor: Network Traffic Monitor",
            "monitor_id": "0000000000MONITOR3",
            "monitor_name": "Network Traffic Monitor",
            "status": "created"
        }
    ]
    
    with patch('httpx.AsyncClient', return_value=mock_httpx_client):
        with patch('src.monitor_validator.create_github_issues', return_value=mock_issues) as mock_create_issues:
            results = await validate_monitor_tags(
                sumo_access_id="test_id",
                sumo_access_key="test_key",
                allowed_tags=allowed_tags,
                api_endpoint="https://api.sumologic.com/api",
                github_token="fake_token"
            )
            
            # Check GitHub issues were created
            assert mock_create_issues.called
            
            # Parse the issues_created JSON string to a list
            issues_created = json.loads(results["issues_created"])
            
            # Check the issues were created
            assert len(issues_created) == 2
            
            # Check issue details
            issue_monitors = [issue["monitor_name"] for issue in issues_created]
            assert "API Latency Monitor" in issue_monitors
            assert "Network Traffic Monitor" in issue_monitors


@pytest.mark.asyncio
async def test_validate_monitor_tags_api_error(mock_httpx_client):
    """Test validate_monitor_tags when the API returns an error"""
    
    # Mock httpx client to raise an exception
    mock_httpx_client.get = AsyncMock(side_effect=Exception("API Error"))
    
    with patch('httpx.AsyncClient', return_value=mock_httpx_client):
        with pytest.raises(Exception, match="API Error"):
            await validate_monitor_tags(
                sumo_access_id="test_id",
                sumo_access_key="test_key",
                allowed_tags={"prod", "dev"},
                api_endpoint="https://api.sumologic.com/api",
                github_token=None
            ) 
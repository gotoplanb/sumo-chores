"""
Unit tests for role_checker module
"""

import json
import pytest
from unittest.mock import patch, AsyncMock

from src.role_checker import check_user_roles


@pytest.mark.asyncio
async def test_check_user_roles_with_matches(mock_httpx_client):
    """Test check_user_roles when users with the specified role are found"""
    
    # Users 1 and 3 have the Administrator role (0000000000AAAAA1)
    with patch('httpx.AsyncClient', return_value=mock_httpx_client):
        results = await check_user_roles(
            sumo_access_id="test_id",
            sumo_access_key="test_key",
            role_id="0000000000AAAAA1",
            api_endpoint="https://api.sumologic.com/api"
        )
        
        # Parse the users_with_role JSON string to a list
        users_with_role = json.loads(results["users_with_role"])
        
        # Check the count matches
        assert results["users_count"] == 2
        
        # Check we have the expected users
        assert len(users_with_role) == 2
        
        # Check user details
        emails = [user["email"] for user in users_with_role]
        assert "john.doe@example.com" in emails
        assert "bob.johnson@example.com" in emails
        
        # Check role information is included
        for user in users_with_role:
            assert user["role"]["id"] == "0000000000AAAAA1"
            assert user["role"]["name"] == "Administrator"


@pytest.mark.asyncio
async def test_check_user_roles_no_matches(mock_httpx_client):
    """Test check_user_roles when no users with the specified role are found"""
    
    # No users have role ID 0000000000DDDDD4
    with patch('httpx.AsyncClient', return_value=mock_httpx_client):
        results = await check_user_roles(
            sumo_access_id="test_id",
            sumo_access_key="test_key",
            role_id="0000000000DDDDD4",
            api_endpoint="https://api.sumologic.com/api"
        )
        
        # Parse the users_with_role JSON string to a list
        users_with_role = json.loads(results["users_with_role"])
        
        # Check the count matches
        assert results["users_count"] == 0
        
        # Check we have no users
        assert len(users_with_role) == 0


@pytest.mark.asyncio
async def test_check_user_roles_api_error(mock_httpx_client):
    """Test check_user_roles when the API returns an error"""
    
    # Mock httpx client to raise an exception
    mock_httpx_client.get = AsyncMock(side_effect=Exception("API Error"))
    
    with patch('httpx.AsyncClient', return_value=mock_httpx_client):
        with pytest.raises(Exception, match="API Error"):
            await check_user_roles(
                sumo_access_id="test_id",
                sumo_access_key="test_key",
                role_id="0000000000AAAAA1",
                api_endpoint="https://api.sumologic.com/api"
            ) 
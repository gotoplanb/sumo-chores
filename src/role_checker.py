#!/usr/bin/env python3
"""
Role Checker module - Checks Sumo Logic users for a specific role ID
"""

import json
import httpx
from typing import Dict, List, Any
from rich.console import Console

# For potential future imports
# Try importing from src package first (for Docker/GitHub Actions)
# If that fails, try relative imports (for local development)

# Initialize console for rich output
console = Console()

# Type aliases
JsonDict = Dict[str, Any]
User = Dict[str, Any]


async def check_user_roles(
    sumo_access_id: str,
    sumo_access_key: str,
    role_id: str,
    api_endpoint: str = "https://api.sumologic.com/api",
) -> Dict[str, Any]:
    """
    Check which Sumo Logic users have a specific role attached

    Args:
        sumo_access_id: Sumo Logic Access ID
        sumo_access_key: Sumo Logic Access Key
        role_id: Role ID to check for
        api_endpoint: Sumo Logic API endpoint

    Returns:
        Dict containing users with the specified role and count
    """
    # Ensure API endpoint has no trailing slash
    api_endpoint = api_endpoint.rstrip("/")

    # Set up authentication for API requests
    auth = (sumo_access_id, sumo_access_key)

    # Set up headers for API requests
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Create async client for API requests
    async with httpx.AsyncClient(auth=auth, headers=headers, timeout=30.0) as client:
        # Get all users
        # Determine if we're using v2 API endpoint
        if "/v2" in api_endpoint:
            users_endpoint = f"{api_endpoint}/users"
        else:
            users_endpoint = f"{api_endpoint}/v1/users"

        console.print(f"Fetching users from {users_endpoint}")

        try:
            response = await client.get(users_endpoint)
            response.raise_for_status()
            users_data = response.json()
            users = users_data.get("data", [])

            console.print(f"Found {len(users)} users")

            # Check each user for the specified role
            users_with_role: List[User] = []

            for user in users:
                user_id = user.get("id")
                user_email = user.get("email")

                # Check if this user already has the role in their roleIds list
                # This avoids having to make an additional API call for each user
                role_ids = user.get("roleIds", [])

                if role_id in role_ids:
                    user_info = {
                        "id": user_id,
                        "email": user_email,
                        "firstName": user.get("firstName", ""),
                        "lastName": user.get("lastName", ""),
                        "role": {
                            "id": role_id,
                            "name": "Role "
                            + role_id,  # We don't have the role name without an additional API call
                        },
                    }
                    users_with_role.append(user_info)
                    console.print(
                        f"[green]✓[/] User {user_email} has the specified role"
                    )

            # Prepare results
            results = {
                "users_with_role": json.dumps(users_with_role),
                "users_count": len(users_with_role),
            }

            # Print summary
            if users_with_role:
                console.print(
                    f"[bold green]Found {len(users_with_role)} users with the specified role[/]"
                )
                for user in users_with_role:
                    console.print(
                        f"  • {user['email']} ({user['firstName']} {user['lastName']})"
                    )
            else:
                console.print("[bold yellow]No users found with the specified role[/]")

            return results

        except httpx.HTTPStatusError as e:
            console.print(
                f"[bold red]Error:[/] API request failed with status {e.response.status_code}"
            )
            console.print(f"Response: {e.response.text}")
            raise
        except httpx.RequestError as e:
            console.print(f"[bold red]Error:[/] API request failed: {str(e)}")
            raise

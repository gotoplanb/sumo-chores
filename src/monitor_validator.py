#!/usr/bin/env python3
"""
Monitor Tag Validator module - Validates Sumo Logic monitor tags against an allowlist
"""

import json
from typing import Dict, List, Set, Any, Optional

import httpx
from rich.console import Console

# Try importing from src package first (for Docker/GitHub Actions)
# If that fails, try relative imports (for local development)
try:
    from src.github_utils import create_github_issues
except ModuleNotFoundError:
    from github_utils import create_github_issues

# Initialize console for rich output
console = Console()

# Type aliases
JsonDict = Dict[str, Any]
Monitor = Dict[str, Any]


async def validate_monitor_tags(
    sumo_access_id: str,
    sumo_access_key: str,
    allowed_tags: Set[str],
    api_endpoint: str = "https://api.sumologic.com/api",
    github_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Validate Sumo Logic monitor tags against an allowlist

    Args:
        sumo_access_id: Sumo Logic Access ID
        sumo_access_key: Sumo Logic Access Key
        allowed_tags: Set of allowed tags
        api_endpoint: Sumo Logic API endpoint
        github_token: GitHub token for creating issues (optional)

    Returns:
        Dict containing monitors with non-compliant tags and count
    """
    # Ensure API endpoint has no trailing slash
    api_endpoint = api_endpoint.rstrip("/")

    # Set up authentication for API requests
    auth = (sumo_access_id, sumo_access_key)

    # Set up headers for API requests
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Create async client for API requests
    async with httpx.AsyncClient(auth=auth, headers=headers, timeout=30.0) as client:
        # First, get monitor IDs using a different endpoint
        # For API v2
        if "/v2" in api_endpoint:
            # For V2 API, try to use a different approach
            # First get a list of monitor IDs
            list_endpoint = f"{api_endpoint}/monitors/jobs"
            console.print(f"Fetching monitor IDs from {list_endpoint}")

            try:
                response = await client.get(list_endpoint)
                response.raise_for_status()
                monitor_list = response.json()
                monitor_ids = [item.get("id") for item in monitor_list.get("data", [])]

                # If no monitors found, return empty result
                if not monitor_ids:
                    console.print("[yellow]No monitors found[/]")
                    return {
                        "non_compliant_monitors": json.dumps([]),
                        "non_compliant_count": 0,
                    }

                # Now get the details for each monitor
                monitors_endpoint = f"{api_endpoint}/monitors"
                params = {"ids": ",".join(monitor_ids)}

            except httpx.HTTPStatusError as e:
                # If that endpoint doesn't work, try a direct approach
                console.print(
                    f"[yellow]Warning:[/] Could not fetch monitor IDs: {e.response.status_code}"
                )
                console.print("Trying alternative approach...")
                monitors_endpoint = f"{api_endpoint}/monitors"
                params = {}
        else:
            # For V1 API
            # First get a list of all monitors
            list_endpoint = f"{api_endpoint}/v1/monitors/queries"
            console.print(f"Fetching monitor IDs from {list_endpoint}")

            try:
                response = await client.get(list_endpoint)
                response.raise_for_status()
                monitor_list = response.json()
                monitor_ids = [item.get("id") for item in monitor_list.get("data", [])]

                # If no monitors found, return empty result
                if not monitor_ids:
                    console.print("[yellow]No monitors found[/]")
                    return {
                        "non_compliant_monitors": json.dumps([]),
                        "non_compliant_count": 0,
                    }

                # Now get the details for each monitor
                monitors_endpoint = f"{api_endpoint}/v1/monitors"
                params = {"ids": ",".join(monitor_ids)}

            except httpx.HTTPStatusError as e:
                # If that endpoint doesn't work, try a direct approach
                console.print(
                    f"[yellow]Warning:[/] Could not fetch monitor IDs: {e.response.status_code}"
                )
                console.print("Trying alternative approach...")
                monitors_endpoint = f"{api_endpoint}/v1/monitors"
                params = {}

        console.print(f"Fetching monitors from {monitors_endpoint}")

        try:
            response = await client.get(monitors_endpoint, params=params)
            response.raise_for_status()
            monitors_data = response.json()
            monitors = monitors_data.get("data", [])

            console.print(f"Found {len(monitors)} monitors")

            # Check each monitor for non-compliant tags
            non_compliant_monitors: List[Monitor] = []

            for monitor in monitors:
                monitor_id = monitor.get("id")
                monitor_name = monitor.get("name", "Unknown Monitor")

                # Extract monitor tags
                tags = set(monitor.get("tags", []))

                if not tags:
                    console.print(f"Monitor {monitor_name} has no tags")
                    continue

                # Find non-compliant tags
                non_compliant_tags = tags - allowed_tags
                compliant_tags = tags & allowed_tags

                if non_compliant_tags:
                    tags_str = ", ".join(non_compliant_tags)
                    console.print(
                        f"[yellow]⚠[/] Monitor {monitor_name} has non-compliant tags: {tags_str}"
                    )

                    # Extract API path for monitor URL
                    api_host = api_endpoint.split("//")[1].split("/")[0]
                    if "." in api_host:
                        api_region = (
                            api_host.split(".")[0].split("api")[1]
                            if "api" in api_host
                            else ""
                        )
                        service_url = (
                            f"service.{api_region}.sumologic.com"
                            if api_region
                            else "service.sumologic.com"
                        )
                    else:
                        service_url = "service.sumologic.com"

                    # Create monitor info
                    monitor_info = {
                        "id": monitor_id,
                        "name": monitor_name,
                        "non_compliant_tags": list(non_compliant_tags),
                        "compliant_tags": list(compliant_tags),
                        "url": f"https://{service_url}/ui/#/monitor/edit/{monitor_id}",
                    }

                    non_compliant_monitors.append(monitor_info)

            # Create GitHub issues if token is provided
            github_issues = []
            if github_token and non_compliant_monitors:
                console.print("Creating GitHub issues for non-compliant monitors...")
                github_issues = await create_github_issues(
                    monitors=non_compliant_monitors, github_token=github_token
                )

            # Prepare results
            results = {
                "non_compliant_monitors": json.dumps(non_compliant_monitors),
                "non_compliant_count": len(non_compliant_monitors),
            }

            # Add GitHub issues to results if any were created
            if github_issues:
                results["github_issues"] = json.dumps(github_issues)

            # Print summary
            if non_compliant_monitors:
                count = len(non_compliant_monitors)
                console.print(
                    f"[bold yellow]Found {count} monitors with non-compliant tags[/]"
                )
                for monitor in non_compliant_monitors:
                    tag_list = ", ".join(monitor["non_compliant_tags"])
                    console.print(
                        f"  • {monitor['name']} - Non-compliant tags: {tag_list}"
                    )
            else:
                console.print("[bold green]All monitors have compliant tags[/]")

            return results

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            console.print(
                f"[bold red]Error:[/] API request failed with status {status_code}"
            )
            console.print(f"Response: {e.response.text}")
            raise
        except httpx.RequestError as e:
            console.print(f"[bold red]Error:[/] API request failed: {str(e)}")
            raise

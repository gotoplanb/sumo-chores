#!/usr/bin/env python3
"""
Monitor Tag Validator module - Validates Sumo Logic monitor tags against an allowlist
"""

import json
from typing import Dict, List, Set, Any, Optional

import httpx
from rich.console import Console

from src.github_utils import create_github_issues

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
        github_token: GitHub token for creating issues

    Returns:
        Dict containing non-compliant monitors and count
    """
    # Ensure API endpoint has no trailing slash
    api_endpoint = api_endpoint.rstrip("/")
    
    # Set up authentication for API requests
    auth = (sumo_access_id, sumo_access_key)
    
    # Set up headers for API requests
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Create async client for API requests
    async with httpx.AsyncClient(auth=auth, headers=headers, timeout=30.0) as client:
        # Get all monitors
        monitors_endpoint = f"{api_endpoint}/v1/monitors"
        console.print(f"Fetching monitors from {monitors_endpoint}")
        
        try:
            response = await client.get(monitors_endpoint)
            response.raise_for_status()
            monitors_data = response.json()
            monitors = monitors_data.get("data", [])
            
            console.print(f"Found {len(monitors)} monitors")
            
            # Check each monitor for non-compliant tags
            noncompliant_monitors: List[Monitor] = []
            
            for monitor in monitors:
                monitor_id = monitor.get("id")
                monitor_name = monitor.get("name")
                monitor_tags = monitor.get("contentType", {}).get("tags", [])
                
                # Skip monitors without tags
                if not monitor_tags:
                    console.print(f"Monitor {monitor_name} has no tags")
                    continue
                
                # Check tags against allowlist
                non_compliant_tags = []
                for tag in monitor_tags:
                    if tag not in allowed_tags:
                        non_compliant_tags.append(tag)
                
                # If non-compliant tags found, add to list
                if non_compliant_tags:
                    monitor_info = {
                        "id": monitor_id,
                        "name": monitor_name,
                        "compliant_tags": [tag for tag in monitor_tags if tag in allowed_tags],
                        "non_compliant_tags": non_compliant_tags,
                        "url": f"https://service.{api_endpoint.split('//')[1].split('.')[0]}.sumologic.com/ui/#/monitor/edit/{monitor_id}"
                    }
                    noncompliant_monitors.append(monitor_info)
                    console.print(f"[yellow]⚠[/] Monitor {monitor_name} has non-compliant tags: {', '.join(non_compliant_tags)}")
            
            # Create GitHub issues for non-compliant monitors if token provided
            issues_created = []
            if noncompliant_monitors and github_token:
                console.print("[bold blue]Creating GitHub issues for non-compliant monitors...[/]")
                issues_created = await create_github_issues(noncompliant_monitors, github_token)
            
            # Prepare results
            results = {
                "noncompliant_monitors": json.dumps(noncompliant_monitors),
                "noncompliant_count": len(noncompliant_monitors)
            }
            
            if issues_created:
                results["issues_created"] = json.dumps(issues_created)
            
            # Print summary
            if noncompliant_monitors:
                console.print(f"[bold yellow]Found {len(noncompliant_monitors)} monitors with non-compliant tags[/]")
                for monitor in noncompliant_monitors:
                    console.print(f"  • {monitor['name']} - Non-compliant tags: {', '.join(monitor['non_compliant_tags'])}")
            else:
                console.print("[bold green]All monitors have compliant tags[/]")
            
            return results
            
        except httpx.HTTPStatusError as e:
            console.print(f"[bold red]Error:[/] API request failed with status {e.response.status_code}")
            console.print(f"Response: {e.response.text}")
            raise
        except httpx.RequestError as e:
            console.print(f"[bold red]Error:[/] API request failed: {str(e)}")
            raise 
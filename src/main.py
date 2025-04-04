#!/usr/bin/env python3
"""
Sumo Logic Chores - GitHub Action for Sumo Logic administration tasks
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Optional, Set, Any

import typer
from rich.console import Console

from src.role_checker import check_user_roles
from src.monitor_validator import validate_monitor_tags
from src.github_utils import set_github_output

# Initialize console for rich output
console = Console()

# Create a Typer app for command line handling
app = typer.Typer(help="Sumo Logic Chores - GitHub Action for admin tasks")

# Type aliases
JsonDict = Dict[str, Any]


async def main_async(
    tasks: str = "all",
    sumo_access_id: str = "",
    sumo_access_key: str = "",
    role_id: Optional[str] = None,
    tag_allowlist: Optional[str] = None,
    sumo_api_endpoint: str = "https://api.sumologic.com/api",
    github_token: Optional[str] = None,
) -> None:
    """
    Main async function that runs the selected tasks
    """
    # Parse tasks
    task_list = [t.strip() for t in tasks.lower().split(",")]
    if "all" in task_list:
        task_list = ["role-check", "monitor-tags"]

    # Validate required parameters for selected tasks
    if "role-check" in task_list and not role_id:
        console.print("[bold red]Error:[/] role_id is required for role-check task")
        sys.exit(1)

    if "monitor-tags" in task_list and not tag_allowlist:
        console.print("[bold red]Error:[/] tag_allowlist is required for monitor-tags task")
        sys.exit(1)

    # Parse tag allowlist if provided
    allowed_tags: Set[str] = set()
    if tag_allowlist:
        allowed_tags = {tag.strip() for tag in tag_allowlist.split(",")}

    # Track results for GitHub Actions outputs
    results: Dict[str, Any] = {}

    # Execute selected tasks
    if "role-check" in task_list:
        console.print("[bold blue]Running role checker task...[/]")
        role_results = await check_user_roles(
            sumo_access_id=sumo_access_id,
            sumo_access_key=sumo_access_key,
            role_id=role_id,
            api_endpoint=sumo_api_endpoint,
        )
        results.update(role_results)

    if "monitor-tags" in task_list:
        console.print("[bold blue]Running monitor tag validator task...[/]")
        monitor_results = await validate_monitor_tags(
            sumo_access_id=sumo_access_id,
            sumo_access_key=sumo_access_key,
            allowed_tags=allowed_tags,
            api_endpoint=sumo_api_endpoint,
            github_token=github_token,
        )
        results.update(monitor_results)

    # Set GitHub Actions outputs
    set_github_output(results)

    # Print results
    console.print("[bold green]Tasks completed successfully[/]")


@app.command()
def main(
    tasks: str = typer.Option(
        "all",
        "--tasks",
        help="Comma-separated list of tasks to run (role-check, monitor-tags, all)",
    ),
    sumo_access_id: str = typer.Option(
        ..., "--sumo-access-id", envvar="INPUT_SUMO_ACCESS_ID", help="Sumo Logic Access ID"
    ),
    sumo_access_key: str = typer.Option(
        ..., "--sumo-access-key", envvar="INPUT_SUMO_ACCESS_KEY", help="Sumo Logic Access Key"
    ),
    role_id: Optional[str] = typer.Option(
        None,
        "--role-id",
        envvar="INPUT_ROLE_ID",
        help="Role ID to check for (required if role-check task is selected)",
    ),
    tag_allowlist: Optional[str] = typer.Option(
        None,
        "--tag-allowlist",
        envvar="INPUT_TAG_ALLOWLIST",
        help="Comma-separated list of allowed tags (required if monitor-tags task is selected)",
    ),
    sumo_api_endpoint: str = typer.Option(
        "https://api.sumologic.com/api",
        "--sumo-api-endpoint",
        envvar="INPUT_SUMO_API_ENDPOINT",
        help="Sumo Logic API endpoint",
    ),
    github_token: Optional[str] = typer.Option(
        None,
        "--github-token",
        envvar="INPUT_GITHUB_TOKEN",
        help="GitHub token for creating issues",
    ),
) -> None:
    """
    Main entry point that runs the selected tasks
    """
    # Check for GitHub Actions environment
    in_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    
    if in_github_actions:
        console.print("[bold]Running in GitHub Actions environment[/]")
    else:
        console.print("[bold]Running in local environment[/]")

    # Run async main
    asyncio.run(
        main_async(
            tasks=tasks,
            sumo_access_id=sumo_access_id,
            sumo_access_key=sumo_access_key,
            role_id=role_id,
            tag_allowlist=tag_allowlist,
            sumo_api_endpoint=sumo_api_endpoint,
            github_token=github_token,
        )
    )


if __name__ == "__main__":
    app() 
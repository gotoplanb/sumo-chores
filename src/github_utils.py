#!/usr/bin/env python3
"""
GitHub utilities module - Functions for GitHub Actions outputs and issue creation
"""

import os
import json
from typing import Dict, List, Any, Optional

import github
from rich.console import Console

# Initialize console for rich output
console = Console()

# Type aliases
JsonDict = Dict[str, Any]
Monitor = Dict[str, Any]


def set_github_output(results: Dict[str, Any]) -> None:
    """
    Set GitHub Actions outputs from results

    Args:
        results: Dictionary of results to set as outputs
    """
    # Check if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") != "true":
        console.print("[yellow]Not running in GitHub Actions, skipping output setting[/]")
        return
    
    # Get GitHub output file path
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        console.print("[yellow]GITHUB_OUTPUT environment variable not set, using default mechanism[/]")
        for key, value in results.items():
            # Use ::set-output for backward compatibility
            # In newer GitHub Actions, this is deprecated but will work
            print(f"::set-output name={key}::{value}")
        return
    
    # Write to GitHub output file
    with open(output_file, "a") as f:
        for key, value in results.items():
            value_str = str(value)
            # Properly escape multiline values
            if "\n" in value_str:
                f.write(f"{key}<<EOF\n{value_str}\nEOF\n")
            else:
                f.write(f"{key}={value_str}\n")


async def create_github_issues(
    monitors: List[Monitor],
    github_token: str,
    repo_owner: Optional[str] = None,
    repo_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Create GitHub issues for non-compliant monitors

    Args:
        monitors: List of monitors with non-compliant tags
        github_token: GitHub token for authentication
        repo_owner: GitHub repository owner (defaults to current repository from GITHUB_REPOSITORY)
        repo_name: GitHub repository name (defaults to current repository from GITHUB_REPOSITORY)

    Returns:
        List of created issues
    """
    # Determine repository from environment if not provided
    if not (repo_owner and repo_name) and os.environ.get("GITHUB_REPOSITORY"):
        github_repo = os.environ.get("GITHUB_REPOSITORY", "")
        if "/" in github_repo:
            repo_owner, repo_name = github_repo.split("/", 1)
    
    # Validate repository information
    if not repo_owner or not repo_name:
        console.print("[bold red]Error:[/] Repository information not available")
        return []
    
    # Create PyGithub instance
    g = github.Github(github_token)
    
    # Get repository
    try:
        repo = g.get_repo(f"{repo_owner}/{repo_name}")
    except github.GithubException as e:
        console.print(f"[bold red]Error:[/] Failed to access repository: {e}")
        return []
    
    # Create issues for each non-compliant monitor
    created_issues = []
    
    for monitor in monitors:
        # Create issue title
        title = f"Non-compliant tags found in Sumo Logic monitor: {monitor['name']}"
        
        # Create issue body
        body = f"""
## Non-compliant Monitor Tags

A Sumo Logic monitor has been found with non-compliant tags.

### Monitor Details
- **Name**: {monitor['name']}
- **ID**: {monitor['id']}
- **URL**: {monitor['url']}

### Tag Issues
The following tags are not on the allowlist:
{', '.join([f'`{tag}`' for tag in monitor['non_compliant_tags']])}

### Compliant Tags
The following tags on this monitor are compliant:
{', '.join([f'`{tag}`' for tag in monitor['compliant_tags']]) if monitor['compliant_tags'] else 'None'}

Please update the monitor to use only approved tags.
"""
        
        # Create labels
        labels = ["sumo-logic", "monitor-tags", "automated"]
        
        try:
            # Check if issue already exists
            existing_issues = list(repo.get_issues(state="open", labels=labels))
            duplicate_issue = False
            
            for issue in existing_issues:
                if monitor['name'] in issue.title:
                    console.print(f"[yellow]Issue already exists for monitor {monitor['name']}[/]")
                    duplicate_issue = True
                    created_issues.append({
                        "url": issue.html_url,
                        "number": issue.number,
                        "title": issue.title,
                        "monitor_id": monitor['id'],
                        "monitor_name": monitor['name'],
                        "status": "existing"
                    })
                    break
            
            if not duplicate_issue:
                # Create new issue
                issue = repo.create_issue(title=title, body=body, labels=labels)
                console.print(f"[green]Created issue #{issue.number} for monitor {monitor['name']}[/]")
                
                created_issues.append({
                    "url": issue.html_url,
                    "number": issue.number,
                    "title": issue.title,
                    "monitor_id": monitor['id'],
                    "monitor_name": monitor['name'],
                    "status": "created"
                })
                
        except github.GithubException as e:
            console.print(f"[bold red]Error:[/] Failed to create issue for monitor {monitor['name']}: {e}")
    
    return created_issues 
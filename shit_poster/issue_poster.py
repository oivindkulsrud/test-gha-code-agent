#!/usr/bin/env python3
"""
GitHub Issue Poster

This script posts issues to a specified GitHub repository using credentials from a .env file.
"""

import os
import sys
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from github import Github, GithubException


class GitHubIssuePoster:
    """
    A class to handle posting issues to a GitHub repository.
    """
    
    def __init__(self):
        """Initialize the GitHub connection using credentials from .env file."""
        # Load environment variables from .env file
        load_dotenv()
        
        # Get GitHub token and repository from environment variables
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("GITHUB_REPOSITORY")
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in .env file")
        if not self.repo_name:
            raise ValueError("GITHUB_REPOSITORY not found in .env file")
        
        # Initialize GitHub client
        self.github = Github(self.token)
        try:
            self.repo = self.github.get_repo(self.repo_name)
        except GithubException as e:
            raise ValueError(f"Error accessing repository '{self.repo_name}': {str(e)}")
    
    def post_issue(self, title: str, body: str, labels: Optional[list] = None, 
                  assignees: Optional[list] = None) -> Dict[str, Any]:
        """
        Post a new issue to the GitHub repository.
        
        Args:
            title: Issue title
            body: Issue body/description
            labels: List of labels to apply to the issue
            assignees: List of GitHub usernames to assign to the issue
            
        Returns:
            Dictionary containing issue details if successful
        """
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or []
            )
            return {
                "success": True,
                "issue_number": issue.number,
                "issue_url": issue.html_url,
                "title": issue.title
            }
        except GithubException as e:
            return {
                "success": False,
                "error": str(e)
            }


def post_github_issue(title, message, labels=None, assignees=None):
    """
    Simple function to post an issue to GitHub with a title and message.
    
    Args:
        title: The title of the issue
        message: The body/content of the issue
        labels: Optional list of labels to apply to the issue
        assignees: Optional list of GitHub usernames to assign to the issue
        
    Returns:
        Dictionary with issue information if successful
    """
    try:
        poster = GitHubIssuePoster()
        result = poster.post_issue(title, message, labels, assignees)
        
        if result["success"]:
            print(f"Issue #{result['issue_number']} created successfully!")
            print(f"Title: {result['title']}")
            print(f"URL: {result['issue_url']}")
            return result
        else:
            print(f"Failed to create issue: {result['error']}")
            return None
    
    except ValueError as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage: directly post an issue without command-line arguments
    issue_title = "Test Issue"
    issue_message = "This is a test issue created by the issue_poster script."
    
    # Optional: add labels and assignees
    # labels = ["bug", "documentation"]
    # assignees = ["your-github-username"]
    
    # Post the issue
    result = post_github_issue(issue_title, issue_message)

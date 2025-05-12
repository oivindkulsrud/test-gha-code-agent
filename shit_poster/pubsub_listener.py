#!/usr/bin/env python3
"""
PubSub listener module that uses default credentials to subscribe to a topic.
Provides functions for subscribing to and processing messages from Google Cloud Pub/Sub.
Integrated with GitHub issue posting functionality.
"""

import os
import json
from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from google.auth import default
from dotenv import load_dotenv

# Import the GitHub issue posting function
from issue_poster import post_github_issue

def setup_subscriber(project_id, subscription_id):
    """
    Setup a Pub/Sub subscriber client using default credentials.
    
    Args:
        project_id (str): Google Cloud project ID
        subscription_id (str): Pub/Sub subscription ID
        
    Returns:
        subscriber client and subscription path
    """
    # Use default credentials
    credentials, _ = default()
    subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    
    return subscriber, subscription_path

def callback(message):
    """
    Process received message from Pub/Sub and create a GitHub issue.
    
    Args:
        message: The message received from Pub/Sub
    """
    print(f"Received message: {message}")
    data = None
    
    try:
        if message.data:
            data = json.loads(message.data.decode("utf-8"))
            print(f"Message data: {json.dumps(data, indent=2)}")
            
            # Create GitHub issue title and body from the message data
            issue_title = f"PubSub Message: {data.get('subject', 'New Message')}"
            
            # Create a formatted message body
            issue_body = "## PubSub Message Received\n\n"
            issue_body += f"**Timestamp:** {data.get('timestamp', 'N/A')}\n\n"
            issue_body += "### Message Content\n\n```json\n"
            issue_body += json.dumps(data, indent=2)
            issue_body += "\n```\n\n"
            
            # Add attributes to the issue body if they exist
            if message.attributes:
                issue_body += "### Message Attributes\n\n"
                for key, value in message.attributes.items():
                    issue_body += f"* **{key}:** {value}\n"
            
            # Post the GitHub issue
            print(f"Creating GitHub issue with title: {issue_title}")
            result = post_github_issue(issue_title, issue_body)
            
            if result and result.get("success"):
                print(f"Successfully created GitHub issue #{result['issue_number']}")
            else:
                print("Failed to create GitHub issue")
        
        # Acknowledge the message
        message.ack()
        
    except Exception as e:
        print(f"Error processing message: {e}")
        # You can choose to not acknowledge the message if processing fails
        # This will cause the message to be redelivered

def listen_for_messages(project_id, subscription_id):
    """
    Listen for messages on the subscription.
    
    Args:
        project_id (str): Google Cloud project ID
        subscription_id (str): Pub/Sub subscription ID
    """
    subscriber, subscription_path = setup_subscriber(project_id, subscription_id)
    
    print(f"Listening for messages on {subscription_path}...")
    
    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    
    # Wrap subscriber in a 'with' block to automatically call close() when done
    with subscriber:
        try:
            # Result will block indefinitely unless an exception is encountered
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()  # Trigger the shutdown
            print("Listener stopped by user")
        except Exception as e:
            streaming_pull_future.cancel()  # Trigger the shutdown
            print(f"Listening stopped due to exception: {e}")


def start_listener():
    """
    Load configuration from environment variables and start the PubSub listener.
    This is the main entry point for the application, to be called from main.py.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment variables
    project_id = os.getenv("PROJECT_ID")
    subscription_id = os.getenv("SUBSCRIPTION_ID")
    
    # Validate required parameters
    if not project_id:
        print("ERROR: PROJECT_ID must be specified in .env file")
        return False
    if not subscription_id:
        print("ERROR: SUBSCRIPTION_ID must be specified in .env file")
        return False
    if not os.getenv("GITHUB_TOKEN"):
        print("WARNING: GITHUB_TOKEN not found in .env file. GitHub issue creation will fail.")
    if not os.getenv("GITHUB_REPOSITORY"):
        print("WARNING: GITHUB_REPOSITORY not found in .env file. GitHub issue creation will fail.")
    
    print(f"Starting listener for project: {project_id}")
    print(f"Subscription: {subscription_id}")
    
    try:
        # Start listening for messages
        listen_for_messages(project_id, subscription_id)
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

# This module is imported by main.py

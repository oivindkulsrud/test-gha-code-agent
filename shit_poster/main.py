#!/usr/bin/env python3
"""
Main entry point for the PubSub listener application.
Loads environment variables and calls functions from pubsub_listener.py
"""

import os
import sys
import json
from dotenv import load_dotenv
from pubsub_listener import setup_subscriber
from github_issue import create_issue_from_message

def process_message(message):
    """
    Process a message from Pub/Sub and create a GitHub issue
    
    Args:
        message: The message received from Pub/Sub
    """
    print(f"Received message ID: {message.message_id}")
    
    try:
        # Parse the message data
        if message.data:
            data = json.loads(message.data.decode("utf-8"))
            print(f"Message data: {json.dumps(data, indent=2)}")
            
            # Create a GitHub issue from the message data
            issue = create_issue_from_message(data)
            
            if issue:
                print(f"Successfully created issue #{issue.number}")
                message.ack()
            else:
                print("Failed to create issue from message data")
                # You may choose to not acknowledge if processing fails
                # This will cause the message to be redelivered
                message.ack()  # Still ack to avoid infinite retries, change if needed
        else:
            print("Received empty message")
            message.ack()
            
    except Exception as e:
        print(f"Error processing message: {e}")
        # You may choose to not acknowledge if processing fails
        # message.nack()  # Uncomment to reject the message
        message.ack()  # Currently acking to avoid infinite retries

def main():
    """
    Main function that initializes the application and starts the Pub/Sub listener.
    """
    # Load configuration from .env file
    print("Loading configuration from .env file...")
    load_dotenv()
    
    # Get configuration values from environment variables
    project_id = os.getenv("PROJECT_ID")
    subscription_id = os.getenv("SUBSCRIPTION_ID")
    github_token = os.getenv("GITHUB_TOKEN")
    
    # Validate required parameters
    if not project_id:
        print("ERROR: PROJECT_ID must be specified in .env file")
        sys.exit(1)
    if not subscription_id:
        print("ERROR: SUBSCRIPTION_ID must be specified in .env file")
        sys.exit(1)
    if not github_token:
        print("WARNING: GITHUB_TOKEN not found in .env file. GitHub issue creation will fail.")
    
    print(f"Starting listener for project: {project_id}")
    print(f"Subscription: {subscription_id}")
    
    try:
        # Set up subscriber
        subscriber, subscription_path = setup_subscriber(project_id, subscription_id)
        
        # Start listening for messages
        print(f"Listening for messages on {subscription_path}...")
        
        streaming_pull_future = subscriber.subscribe(
            subscription_path, callback=process_message
        )
        
        # Wrap subscriber in a 'with' block to automatically call close() when done
        with subscriber:
            try:
                # Result will block indefinitely unless an exception is encountered
                streaming_pull_future.result()
            except KeyboardInterrupt:
                streaming_pull_future.cancel()  # Trigger the shutdown
                print("\nListener stopped by user")
            except Exception as e:
                streaming_pull_future.cancel()  # Trigger the shutdown
                print(f"Listening stopped due to exception: {e}")
    
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    print("Listener stopped")

if __name__ == "__main__":
    main()

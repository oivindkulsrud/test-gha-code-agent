#!/usr/bin/env python3
"""
PubSub listener module that uses default credentials to subscribe to a topic.
Provides functions for subscribing to and processing messages from Google Cloud Pub/Sub.
"""

import os
import json
from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from google.auth import default
from dotenv import load_dotenv

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
    Process received message from Pub/Sub.
    
    Args:
        message: The message received from Pub/Sub
    """
    print(f"Received message: {message}")
    data = None
    
    try:
        if message.data:
            data = json.loads(message.data.decode("utf-8"))
            print(f"Message data: {json.dumps(data, indent=2)}")
        
        # Print message attributes
        if message.attributes:
            print("Attributes:")
            for key, value in message.attributes.items():
                print(f"{key}: {value}")
        
        # Process the message here
        # Add your custom processing logic
        
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
        timeout (float, optional): How long to listen for messages in seconds
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

# Module is imported by main.py

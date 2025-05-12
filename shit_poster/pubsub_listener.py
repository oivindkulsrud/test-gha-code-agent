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
    credentials, _ = default()
    subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    return subscriber, subscription_path


def create_callback(do_post_issue=True):
    def callback(message):
        print(f"Received message: {message}")
        data = None

        try:
            if message.data:
                data = json.loads(message.data.decode("utf-8"))
                print(f"Message data: {json.dumps(data, indent=2)}")

                if do_post_issue:
                    issue_title = f"PubSub Message: {data.get('subject', 'New Message')}"

                    issue_body = "## PubSub Message Received\n\n"
                    issue_body += f"**Timestamp:** {data.get('timestamp', 'N/A')}\n\n"
                    issue_body += "### Message Content\n\n```json\n"
                    issue_body += json.dumps(data, indent=2)
                    issue_body += "\n```\n\n"

                    if message.attributes:
                        issue_body += "### Message Attributes\n\n"
                        for key, value in message.attributes.items():
                            issue_body += f"* **{key}:** {value}\n"

                    print(f"Creating GitHub issue with title: {issue_title}")
                    result = post_github_issue(issue_title, issue_body)

                    if result and result.get("success"):
                        print(f"Successfully created GitHub issue #{result['issue_number']}")
                    else:
                        print("Failed to create GitHub issue")

            message.ack()

        except Exception as e:
            print(f"Error processing message: {e}")
            # Optionally skip ack to allow redelivery

    return callback


def listen_for_messages(project_id, subscription_id, do_post_issue=True):
    subscriber, subscription_path = setup_subscriber(project_id, subscription_id)
    print(f"Listening for messages on {subscription_path}...")

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=create_callback(do_post_issue)
    )

    with subscriber:
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            print("Listener stopped by user")
        except Exception as e:
            streaming_pull_future.cancel()
            print(f"Listening stopped due to exception: {e}")


def start_listener(do_post_issue=True):
    load_dotenv()

    project_id = os.getenv("PROJECT_ID")
    subscription_id = os.getenv("SUBSCRIPTION_ID")

    if not project_id:
        print("ERROR: PROJECT_ID must be specified in .env file")
        return False
    if not subscription_id:
        print("ERROR: SUBSCRIPTION_ID must be specified in .env file")
        return False
    if do_post_issue and not os.getenv("GITHUB_TOKEN"):
        print("WARNING: GITHUB_TOKEN not found in .env file. GitHub issue creation will fail.")
    if do_post_issue and not os.getenv("GITHUB_REPOSITORY"):
        print("WARNING: GITHUB_REPOSITORY not found in .env file. GitHub issue creation will fail.")

    print(f"Starting listener for project: {project_id}")
    print(f"Subscription: {subscription_id}")

    try:
        listen_for_messages(project_id, subscription_id, do_post_issue=do_post_issue)
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    print("Running in standalone mode with do_post_issue=False")
    start_listener(do_post_issue=False)

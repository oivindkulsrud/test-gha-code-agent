#!/usr/bin/env python3
"""
Main entry point for the PubSub listener application.
Simply calls the start_listener function from pubsub_listener.py.
"""

import sys
from pubsub_listener import start_listener


if __name__ == "__main__":
    # Just call the start_listener function, which handles everything
    if not start_listener():
        sys.exit(1)

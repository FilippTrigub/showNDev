#!/usr/bin/env python3
"""
Example usage of the BlueskyClient

This script demonstrates how to use the BlueskyClient to interact with Bluesky.
Set the following environment variables before running:
    - BLUESKY_IDENTIFIER: Your Bluesky handle (e.g., "user.bsky.social")
    - BLUESKY_APP_PASSWORD: Your Bluesky app password
"""

import asyncio
import logging
import os
from bluesky_client import BlueskyClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function demonstrating BlueskyClient usage."""

    # Get credentials from environment
    identifier = os.getenv("BLUESKY_IDENTIFIER")
    password = os.getenv("BLUESKY_APP_PASSWORD")

    if not identifier or not password:
        logger.error(
            "Please set BLUESKY_IDENTIFIER and BLUESKY_APP_PASSWORD environment variables"
        )
        return

    # Initialize client
    client = BlueskyClient(identifier, password)

    # Login
    logger.info("Attempting to login...")
    if not await client.login():
        logger.error("Login failed, exiting")
        return

    logger.info("Login successful!")

    # Example 1: Get profile
    logger.info("\n--- Getting Profile ---")
    profile_result = await client.get_profile()
    if profile_result["success"]:
        logger.info(f"Handle: {profile_result['handle']}")
        logger.info(f"Display Name: {profile_result['display_name']}")
        logger.info(f"Followers: {profile_result['followers_count']}")
        logger.info(f"Posts: {profile_result['posts_count']}")
    else:
        logger.error(f"Failed to get profile: {profile_result['error']}")

    # Example 2: Create a post
    logger.info("\n--- Creating Post ---")
    post_text = "Hello from the Bluesky Python client! 🚀"
    post_result = await client.create_post(post_text)

    if post_result["success"]:
        logger.info(f"Post created successfully!")
        logger.info(f"URI: {post_result['uri']}")
        logger.info(f"CID: {post_result['cid']}")
        post_uri = post_result['uri']
        post_cid = post_result['cid']
    else:
        logger.error(f"Failed to create post: {post_result['error']}")
        return

    # Example 3: Get timeline
    logger.info("\n--- Getting Timeline (first 10 posts) ---")
    timeline_result = await client.get_timeline(limit=10)

    if timeline_result["success"]:
        logger.info(f"Retrieved {timeline_result['count']} posts")
        for i, post in enumerate(timeline_result['posts'][:3], 1):
            logger.info(f"\nPost {i}:")
            logger.info(f"  Author: {post['author']}")
            logger.info(f"  Text: {post['text'][:100]}...")
            logger.info(f"  Likes: {post['like_count']}, Replies: {post['reply_count']}")
    else:
        logger.error(f"Failed to get timeline: {timeline_result['error']}")

    # Example 4: Reply to our post
    logger.info("\n--- Creating Reply ---")
    reply_result = await client.create_post(
        "This is a reply to my own post!",
        reply_to=post_uri
    )

    if reply_result["success"]:
        logger.info(f"Reply created successfully!")
        logger.info(f"URI: {reply_result['uri']}")
    else:
        logger.error(f"Failed to create reply: {reply_result['error']}")

    # Example 5: Like the post
    logger.info("\n--- Liking Post ---")
    like_result = await client.like_post(post_uri, post_cid)

    if like_result["success"]:
        logger.info("Post liked successfully!")
    else:
        logger.error(f"Failed to like post: {like_result['error']}")

    # Example 6: Clean up - delete the post
    logger.info("\n--- Deleting Test Post ---")
    delete_result = await client.delete_post(post_uri)

    if delete_result["success"]:
        logger.info("Post deleted successfully!")
    else:
        logger.error(f"Failed to delete post: {delete_result['error']}")

    # Logout
    client.logout()
    logger.info("\n--- Logged out ---")


if __name__ == "__main__":
    asyncio.run(main())

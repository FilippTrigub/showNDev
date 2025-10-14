#!/usr/bin/env python3
"""
Example usage of the TwitterClient

This script demonstrates how to use the TwitterClient to interact with Twitter.
Set the following environment variables before running:
    - TWITTER_API_KEY: Your Twitter API Key (Consumer Key)
    - TWITTER_API_SECRET: Your Twitter API Secret (Consumer Secret)
    - TWITTER_ACCESS_TOKEN: Your Access Token
    - TWITTER_ACCESS_TOKEN_SECRET: Your Access Token Secret
    - TWITTER_BEARER_TOKEN: (Optional) Bearer Token
"""

import asyncio
import logging
import os
from twitter_client import TwitterClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function demonstrating TwitterClient usage."""

    # Get credentials from environment
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        logger.error(
            "Please set TWITTER_API_KEY, TWITTER_API_SECRET, "
            "TWITTER_ACCESS_TOKEN, and TWITTER_ACCESS_TOKEN_SECRET environment variables"
        )
        return

    # Initialize client
    client = TwitterClient(
        api_key=api_key,
        api_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        bearer_token=bearer_token
    )

    logger.info("Twitter client initialized!")

    # Example 1: Post a tweet
    logger.info("\n--- Posting Tweet ---")
    tweet_text = "Hello from the Twitter Python client! 🚀 #PythonTwitter"
    post_result = await client.post_tweet(tweet_text)

    if post_result["success"]:
        logger.info(f"Tweet posted successfully!")
        logger.info(f"ID: {post_result['id']}")
        logger.info(f"URL: {post_result['url']}")
        tweet_id = post_result['id']
    else:
        logger.error(f"Failed to post tweet: {post_result['error']}")
        return

    # Example 2: Search for tweets
    logger.info("\n--- Searching Tweets ---")
    search_query = "Python programming -is:retweet lang:en"
    search_result = await client.search_tweets(search_query, max_results=10)

    if search_result["success"]:
        logger.info(f"Found {search_result['count']} tweets")
        for i, tweet in enumerate(search_result['tweets'][:3], 1):
            logger.info(f"\nTweet {i}:")
            logger.info(f"  Text: {tweet['text'][:80]}...")
            logger.info(f"  URL: {tweet['url']}")
            logger.info(f"  Likes: {tweet['metrics']['likes']}, "
                       f"Retweets: {tweet['metrics']['retweets']}")
    else:
        logger.error(f"Failed to search tweets: {search_result['error']}")

    # Example 3: Post a thread
    logger.info("\n--- Posting Thread ---")
    thread_tweets = [
        "🧵 This is the first tweet in a thread! Let me explain something cool...",
        "2/ Twitter threads are great for sharing longer thoughts or stories.",
        "3/ Each tweet can be up to 280 characters, and they're all connected!",
        "4/ That's it! Thanks for reading this demo thread. 🎉"
    ]

    thread_result = await client.post_thread(thread_tweets)

    if thread_result["success"]:
        logger.info(f"Thread posted successfully!")
        logger.info(f"Thread URL: {thread_result['thread_url']}")
        logger.info(f"Number of tweets: {thread_result['count']}")
    else:
        logger.error(f"Failed to post thread: {thread_result['error']}")

    # Example 4: Get user information
    logger.info("\n--- Getting User Info ---")
    user_result = await client.get_user("Twitter")  # Get Twitter's official account

    if user_result["success"]:
        logger.info(f"Username: @{user_result['username']}")
        logger.info(f"Name: {user_result['name']}")
        logger.info(f"Followers: {user_result['followers_count']:,}")
        logger.info(f"Verified: {user_result['verified']}")
    else:
        logger.error(f"Failed to get user: {user_result['error']}")

    # Example 5: Like the tweet we posted
    logger.info("\n--- Liking Tweet ---")
    like_result = await client.like_tweet(tweet_id)

    if like_result["success"]:
        logger.info("Tweet liked successfully!")
    else:
        logger.error(f"Failed to like tweet: {like_result['error']}")

    # Example 6: Clean up - delete the tweet
    logger.info("\n--- Deleting Test Tweet ---")
    delete_result = await client.delete_tweet(tweet_id)

    if delete_result["success"]:
        logger.info("Tweet deleted successfully!")
    else:
        logger.error(f"Failed to delete tweet: {delete_result['error']}")

    logger.info("\n--- Done! ---")


if __name__ == "__main__":
    asyncio.run(main())

"""
Twitter Client

A standalone Python client for interacting with the Twitter API v2 using the tweepy library.
Provides functionality for posting tweets, searching, threads, and more.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

import tweepy
from tweepy import Client as TweepyClient
from tweepy.errors import TweepyException, Forbidden, TooManyRequests


class TwitterError(Exception):
    """Custom Twitter API error."""

    def __init__(self, message: str, code: str, status: Optional[int] = None):
        super().__init__(message)
        self.code = code
        self.status = status

    @staticmethod
    def is_rate_limit(error: Exception) -> bool:
        """Check if error is a rate limit error."""
        return isinstance(error, TwitterError) and error.code == "rate_limit_exceeded"


class TwitterClient:
    """
    A client for interacting with the Twitter API v2.

    Example usage:
        client = TwitterClient(
            api_key="your-api-key",
            api_secret="your-api-secret",
            access_token="your-access-token",
            access_token_secret="your-access-token-secret"
        )
        result = await client.post_tweet("Hello Twitter!")
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
        bearer_token: Optional[str] = None
    ):
        """
        Initialize the Twitter client.

        Args:
            api_key: Twitter API Key (Consumer Key)
            api_secret: Twitter API Secret Key (Consumer Secret)
            access_token: Access Token
            access_token_secret: Access Token Secret
            bearer_token: Optional Bearer Token for app-only auth
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.bearer_token = bearer_token

        # Initialize tweepy client with OAuth 1.0a User Context
        self.client = TweepyClient(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            bearer_token=bearer_token
        )

        # Rate limiting
        self.rate_limit_map: Dict[str, float] = {}
        self.rate_limit_window = 1.0  # seconds between requests

        self.logger = logging.getLogger(__name__)
        self.logger.info("Twitter API client initialized")

    async def post_tweet(self, text: str) -> Dict[str, Any]:
        """
        Post a tweet to Twitter.

        Args:
            text: The content of the tweet (max 280 characters)

        Returns:
            Dict containing:
                - success (bool): Whether the tweet was posted successfully
                - id (str): Tweet ID (if successful)
                - text (str): Tweet text (if successful)
                - url (str): Tweet URL (if successful)
                - error (str): Error message (if failed)
        """
        endpoint = "tweets/create"
        await self._check_rate_limit(endpoint)

        if len(text) > 280:
            return {
                "success": False,
                "error": "Tweet cannot exceed 280 characters"
            }

        try:
            response = self.client.create_tweet(text=text)

            tweet_id = response.data["id"]
            self.logger.info(f"Tweet posted successfully with ID: {tweet_id}")

            return {
                "success": True,
                "id": tweet_id,
                "text": text,
                "url": f"https://twitter.com/status/{tweet_id}",
                "created_at": datetime.now(timezone.utc).isoformat()
            }

        except TooManyRequests as e:
            self.logger.error(f"Rate limit exceeded: {str(e)}")
            return {
                "success": False,
                "error": "Rate limit exceeded. Please wait before trying again.",
                "code": "rate_limit_exceeded"
            }
        except Forbidden as e:
            self.logger.error(f"Forbidden error: {str(e)}")
            return {
                "success": False,
                "error": f"Access forbidden: {str(e)}",
                "code": "forbidden"
            }
        except TweepyException as e:
            self.logger.error(f"Twitter API error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "code": "twitter_api_error"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "code": "internal_error"
            }

    async def search_tweets(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for tweets on Twitter.

        Args:
            query: Search query (supports Twitter search operators)
            max_results: Number of tweets to return (10-100, default 10)

        Returns:
            Dict containing:
                - success (bool): Whether the search was successful
                - tweets (list): List of tweet dictionaries
                - users (dict): Dictionary of users by ID
                - count (int): Number of tweets returned
                - error (str): Error message (if failed)
        """
        endpoint = "tweets/search"
        await self._check_rate_limit(endpoint)

        if max_results < 10 or max_results > 100:
            return {
                "success": False,
                "error": "max_results must be between 10 and 100"
            }

        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                expansions=["author_id"],
                tweet_fields=["public_metrics", "created_at"],
                user_fields=["username", "name", "verified"]
            )

            if not response.data:
                return {
                    "success": True,
                    "tweets": [],
                    "users": {},
                    "count": 0,
                    "query": query
                }

            # Process tweets
            tweets = []
            for tweet in response.data:
                tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "metrics": {
                        "likes": tweet.public_metrics.get("like_count", 0),
                        "retweets": tweet.public_metrics.get("retweet_count", 0),
                        "replies": tweet.public_metrics.get("reply_count", 0),
                        "quotes": tweet.public_metrics.get("quote_count", 0)
                    },
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "url": f"https://twitter.com/status/{tweet.id}"
                })

            # Process users
            users = {}
            if response.includes and "users" in response.includes:
                for user in response.includes["users"]:
                    users[user.id] = {
                        "id": user.id,
                        "username": user.username,
                        "name": user.name,
                        "verified": getattr(user, "verified", False)
                    }

            self.logger.info(f"Fetched {len(tweets)} tweets for query: '{query}'")

            return {
                "success": True,
                "tweets": tweets,
                "users": users,
                "count": len(tweets),
                "query": query
            }

        except TooManyRequests as e:
            self.logger.error(f"Rate limit exceeded: {str(e)}")
            return {
                "success": False,
                "error": "Rate limit exceeded. Please wait before trying again.",
                "code": "rate_limit_exceeded"
            }
        except TweepyException as e:
            self.logger.error(f"Twitter API error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "code": "twitter_api_error"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "code": "internal_error"
            }

    async def post_thread(self, tweets: List[str]) -> Dict[str, Any]:
        """
        Post a thread of tweets to Twitter.

        Args:
            tweets: List of tweet texts (each max 280 characters)

        Returns:
            Dict containing:
                - success (bool): Whether the thread was posted successfully
                - tweets (list): List of posted tweet dictionaries
                - thread_url (str): URL to the first tweet in the thread
                - count (int): Number of tweets in the thread
                - error (str): Error message (if failed)
        """
        endpoint = "tweets/create"
        await self._check_rate_limit(endpoint)

        if not tweets:
            return {
                "success": False,
                "error": "Thread must contain at least one tweet"
            }

        for i, tweet_text in enumerate(tweets):
            if len(tweet_text) > 280:
                return {
                    "success": False,
                    "error": f"Tweet {i + 1} exceeds 280 characters"
                }

        try:
            posted_tweets = []
            previous_tweet_id = None

            for tweet_text in tweets:
                # Create tweet with reply to previous if exists
                if previous_tweet_id:
                    response = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                else:
                    response = self.client.create_tweet(text=tweet_text)

                tweet_id = response.data["id"]
                posted_tweets.append({
                    "id": tweet_id,
                    "text": tweet_text,
                    "url": f"https://twitter.com/status/{tweet_id}"
                })

                previous_tweet_id = tweet_id

                # Add delay to prevent rate limiting
                time.sleep(1)

            thread_url = posted_tweets[0]["url"] if posted_tweets else ""

            self.logger.info(f"Thread posted successfully with {len(posted_tweets)} tweets")

            return {
                "success": True,
                "tweets": posted_tweets,
                "thread_url": thread_url,
                "count": len(posted_tweets),
                "created_at": datetime.now(timezone.utc).isoformat()
            }

        except TooManyRequests as e:
            self.logger.error(f"Rate limit exceeded: {str(e)}")
            return {
                "success": False,
                "error": "Rate limit exceeded. Please wait before trying again.",
                "code": "rate_limit_exceeded"
            }
        except TweepyException as e:
            self.logger.error(f"Twitter API error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "code": "twitter_api_error"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "code": "internal_error"
            }

    async def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Delete a tweet by ID.

        Args:
            tweet_id: ID of the tweet to delete

        Returns:
            Dict indicating success or failure
        """
        try:
            self.client.delete_tweet(tweet_id)
            self.logger.info(f"Successfully deleted tweet: {tweet_id}")
            return {"success": True, "id": tweet_id}
        except TweepyException as e:
            self.logger.error(f"Failed to delete tweet: {str(e)}")
            return {"success": False, "error": str(e)}

    async def like_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Like a tweet.

        Args:
            tweet_id: ID of the tweet to like

        Returns:
            Dict indicating success or failure
        """
        try:
            response = self.client.like(tweet_id)
            return {"success": True, "liked": response.data["liked"]}
        except TweepyException as e:
            self.logger.error(f"Failed to like tweet: {str(e)}")
            return {"success": False, "error": str(e)}

    async def retweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Retweet a tweet.

        Args:
            tweet_id: ID of the tweet to retweet

        Returns:
            Dict indicating success or failure
        """
        try:
            response = self.client.retweet(tweet_id)
            return {"success": True, "retweeted": response.data["retweeted"]}
        except TweepyException as e:
            self.logger.error(f"Failed to retweet: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_user(self, username: str) -> Dict[str, Any]:
        """
        Get user information by username.

        Args:
            username: Twitter username (without @)

        Returns:
            Dict containing user information or error
        """
        try:
            response = self.client.get_user(
                username=username,
                user_fields=["public_metrics", "description", "verified", "created_at"]
            )

            if not response.data:
                return {"success": False, "error": "User not found"}

            user = response.data
            return {
                "success": True,
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "description": user.description,
                "verified": getattr(user, "verified", False),
                "followers_count": user.public_metrics.get("followers_count", 0),
                "following_count": user.public_metrics.get("following_count", 0),
                "tweet_count": user.public_metrics.get("tweet_count", 0),
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        except TweepyException as e:
            self.logger.error(f"Failed to get user: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _check_rate_limit(self, endpoint: str) -> None:
        """
        Check and enforce rate limiting.

        Args:
            endpoint: API endpoint identifier

        Raises:
            TwitterError: If rate limit would be exceeded
        """
        last_request = self.rate_limit_map.get(endpoint)
        if last_request:
            time_since_last = time.time() - last_request
            if time_since_last < self.rate_limit_window:
                raise TwitterError(
                    "Rate limit exceeded",
                    "rate_limit_exceeded",
                    429
                )
        self.rate_limit_map[endpoint] = time.time()

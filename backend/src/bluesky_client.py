"""
Bluesky Client

A standalone Python client for interacting with the Bluesky API using the atproto library.
Provides functionality for authentication, posting, and managing Bluesky content.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from atproto import Client
from atproto.exceptions import AtProtocolError


class BlueskyClient:
    """
    A client for interacting with the Bluesky social network via the AT Protocol.

    Example usage:
        client = BlueskyClient("user.bsky.social", "app-password")
        await client.login()
        result = await client.create_post("Hello Bluesky!")
    """

    def __init__(
        self,
        identifier: str,
        password: str,
        service_url: str = "https://bsky.social"
    ):
        """
        Initialize the Bluesky client.

        Args:
            identifier: Bluesky handle (e.g., "user.bsky.social") or DID
            password: App password (not your main password!)
            service_url: Bluesky service URL, defaults to https://bsky.social
        """
        self.identifier = identifier
        self.password = password
        self.service_url = service_url
        self.client = Client(base_url=service_url)
        self.logged_in = False
        self.profile = None
        self.logger = logging.getLogger(__name__)

    async def login(self) -> bool:
        """
        Login to Bluesky using credentials.

        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.profile = self.client.login(self.identifier, self.password)
            self.logged_in = True
            self.logger.info(
                f"Successfully logged in as {self.profile.handle} ({self.profile.did})"
            )
            return True
        except AtProtocolError as e:
            self.logger.error(f"Login failed with AT Protocol error: {str(e)}")
            self.logged_in = False
            return False
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            self.logged_in = False
            return False

    async def ensure_logged_in(self) -> bool:
        """
        Ensure the client is logged in, attempt login if not.

        Returns:
            bool: True if logged in (or login successful), False otherwise
        """
        if not self.logged_in:
            return await self.login()
        return True

    async def create_post(
        self,
        text: str,
        reply_to: Optional[str] = None,
        images: Optional[List[str]] = None,
        langs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a post on Bluesky.

        Args:
            text: The content of the post (max 300 characters)
            reply_to: Optional URI of the post to reply to
            images: Optional list of image paths or URLs to attach
            langs: Optional list of language codes (e.g., ["en", "es"])

        Returns:
            Dict containing:
                - success (bool): Whether the post was created successfully
                - uri (str): URI of the created post (if successful)
                - cid (str): CID of the created post (if successful)
                - error (str): Error message (if failed)
        """
        if not await self.ensure_logged_in():
            return {"success": False, "error": "Failed to login"}

        if len(text) > 300:
            return {
                "success": False,
                "error": "Post text cannot exceed 300 characters"
            }

        try:
            # Handle reply if specified
            reply_ref = None
            if reply_to:
                try:
                    reply_thread = self.client.get_post_thread(reply_to)
                    if reply_thread and reply_thread.thread:
                        reply_ref = {
                            "root": {
                                "uri": reply_to,
                                "cid": reply_thread.thread.post.cid
                            },
                            "parent": {
                                "uri": reply_to,
                                "cid": reply_thread.thread.post.cid
                            }
                        }
                except Exception as e:
                    self.logger.warning(f"Could not set up reply: {str(e)}")

            # Create the post using atproto client
            response = self.client.send_post(
                text=text,
                reply_to=reply_ref if reply_ref else None,
                langs=langs
            )

            result = {
                "success": True,
                "uri": response.uri,
                "cid": response.cid,
                "text": text,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            self.logger.info(f"Successfully posted to Bluesky: {text[:50]}...")
            return result

        except AtProtocolError as e:
            self.logger.error(f"Failed to post with AT Protocol error: {str(e)}")
            return {"success": False, "error": f"AT Protocol error: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Failed to post: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_profile(self, handle: Optional[str] = None) -> Dict[str, Any]:
        """
        Get profile information for a user.

        Args:
            handle: Handle of the user (defaults to authenticated user)

        Returns:
            Dict containing profile information or error
        """
        if not await self.ensure_logged_in():
            return {"success": False, "error": "Failed to login"}

        try:
            target_handle = handle or self.profile.handle
            profile = self.client.get_profile(target_handle)

            return {
                "success": True,
                "handle": profile.handle,
                "display_name": profile.display_name,
                "description": profile.description,
                "followers_count": profile.followers_count,
                "follows_count": profile.follows_count,
                "posts_count": profile.posts_count,
                "did": profile.did
            }
        except Exception as e:
            self.logger.error(f"Failed to get profile: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_timeline(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get the authenticated user's timeline.

        Args:
            limit: Maximum number of posts to retrieve (default 50)

        Returns:
            Dict containing timeline posts or error
        """
        if not await self.ensure_logged_in():
            return {"success": False, "error": "Failed to login"}

        try:
            timeline = self.client.get_timeline(limit=limit)

            posts = []
            for feed_view in timeline.feed:
                post = feed_view.post
                posts.append({
                    "uri": post.uri,
                    "cid": post.cid,
                    "author": post.author.handle,
                    "text": post.record.text if hasattr(post.record, "text") else "",
                    "created_at": post.record.created_at if hasattr(post.record, "created_at") else None,
                    "like_count": post.like_count,
                    "reply_count": post.reply_count,
                    "repost_count": post.repost_count
                })

            return {
                "success": True,
                "posts": posts,
                "count": len(posts)
            }
        except Exception as e:
            self.logger.error(f"Failed to get timeline: {str(e)}")
            return {"success": False, "error": str(e)}

    async def delete_post(self, post_uri: str) -> Dict[str, Any]:
        """
        Delete a post by URI.

        Args:
            post_uri: URI of the post to delete

        Returns:
            Dict indicating success or failure
        """
        if not await self.ensure_logged_in():
            return {"success": False, "error": "Failed to login"}

        try:
            self.client.delete_post(post_uri)
            self.logger.info(f"Successfully deleted post: {post_uri}")
            return {"success": True, "uri": post_uri}
        except Exception as e:
            self.logger.error(f"Failed to delete post: {str(e)}")
            return {"success": False, "error": str(e)}

    async def like_post(self, post_uri: str, post_cid: str) -> Dict[str, Any]:
        """
        Like a post.

        Args:
            post_uri: URI of the post to like
            post_cid: CID of the post to like

        Returns:
            Dict indicating success or failure
        """
        if not await self.ensure_logged_in():
            return {"success": False, "error": "Failed to login"}

        try:
            response = self.client.like(post_uri, post_cid)
            return {
                "success": True,
                "uri": response.uri,
                "cid": response.cid
            }
        except Exception as e:
            self.logger.error(f"Failed to like post: {str(e)}")
            return {"success": False, "error": str(e)}

    async def repost(self, post_uri: str, post_cid: str) -> Dict[str, Any]:
        """
        Repost a post.

        Args:
            post_uri: URI of the post to repost
            post_cid: CID of the post to repost

        Returns:
            Dict indicating success or failure
        """
        if not await self.ensure_logged_in():
            return {"success": False, "error": "Failed to login"}

        try:
            response = self.client.repost(post_uri, post_cid)
            return {
                "success": True,
                "uri": response.uri,
                "cid": response.cid
            }
        except Exception as e:
            self.logger.error(f"Failed to repost: {str(e)}")
            return {"success": False, "error": str(e)}

    async def follow(self, did: str) -> Dict[str, Any]:
        """
        Follow a user by their DID.

        Args:
            did: DID of the user to follow

        Returns:
            Dict indicating success or failure
        """
        if not await self.ensure_logged_in():
            return {"success": False, "error": "Failed to login"}

        try:
            response = self.client.follow(did)
            return {
                "success": True,
                "uri": response.uri,
                "cid": response.cid
            }
        except Exception as e:
            self.logger.error(f"Failed to follow user: {str(e)}")
            return {"success": False, "error": str(e)}

    def logout(self) -> None:
        """Logout and clear session."""
        self.logged_in = False
        self.profile = None
        self.logger.info("Logged out successfully")

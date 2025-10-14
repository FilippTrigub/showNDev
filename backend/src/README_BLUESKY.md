# Bluesky Client

A standalone Python client for interacting with the Bluesky social network using the AT Protocol.

## Installation

The client requires the `atproto` library:

```bash
pip install atproto
```

Or add to your `pyproject.toml`:

```toml
dependencies = [
    "atproto>=0.0.62"
]
```

## Setup

### Getting App Password

1. Go to Bluesky Settings → App Passwords
2. Create a new app password
3. Save it securely (you won't be able to see it again)

### Environment Variables

Set these environment variables:

```bash
export BLUESKY_IDENTIFIER="your-handle.bsky.social"
export BLUESKY_APP_PASSWORD="your-app-password"
```

## Usage

### Basic Example

```python
import asyncio
from bluesky_client import BlueskyClient

async def main():
    # Initialize client
    client = BlueskyClient(
        identifier="your-handle.bsky.social",
        password="your-app-password"
    )

    # Login
    if await client.login():
        print("Login successful!")

        # Create a post
        result = await client.create_post("Hello Bluesky! 🚀")

        if result["success"]:
            print(f"Post created: {result['uri']}")
        else:
            print(f"Error: {result['error']}")

        # Logout
        client.logout()

asyncio.run(main())
```

### Available Methods

#### Authentication

```python
# Login (returns bool)
await client.login()

# Ensure logged in (auto-login if needed)
await client.ensure_logged_in()

# Logout
client.logout()
```

#### Creating Posts

```python
# Simple post
result = await client.create_post("Hello world!")

# Reply to a post
result = await client.create_post(
    text="This is a reply",
    reply_to="at://did:plc:xyz/app.bsky.feed.post/abc123"
)

# Post with language tags
result = await client.create_post(
    text="Hello!",
    langs=["en", "es"]
)
```

#### Profile Management

```python
# Get your profile
profile = await client.get_profile()

# Get another user's profile
profile = await client.get_profile(handle="other-user.bsky.social")
```

#### Timeline & Feed

```python
# Get timeline (default 50 posts)
timeline = await client.get_timeline()

# Get limited number of posts
timeline = await client.get_timeline(limit=20)
```

#### Post Interactions

```python
# Like a post
result = await client.like_post(post_uri, post_cid)

# Repost
result = await client.repost(post_uri, post_cid)

# Delete a post
result = await client.delete_post(post_uri)
```

#### Following

```python
# Follow a user by DID
result = await client.follow(user_did)
```

## Response Format

All methods return dictionaries with the following structure:

### Success Response

```python
{
    "success": True,
    "uri": "at://did:plc:xyz/app.bsky.feed.post/abc123",
    "cid": "bafyreiabc123...",
    # ... other relevant fields
}
```

### Error Response

```python
{
    "success": False,
    "error": "Error message describing what went wrong"
}
```

## Example Script

Run the example script to see all features in action:

```bash
cd backend/src
python bluesky_example.py
```

This will:
1. Login to Bluesky
2. Get your profile
3. Create a test post
4. Retrieve your timeline
5. Reply to the test post
6. Like the post
7. Delete the test post
8. Logout

## Error Handling

The client uses comprehensive error handling:

```python
result = await client.create_post("Hello!")

if not result["success"]:
    print(f"Error: {result['error']}")
    # Handle error appropriately
```

## Logging

The client uses Python's logging module. Configure it in your application:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Integration with MongoDB

You can easily integrate this client with your MongoDB storage:

```python
from bluesky_client import BlueskyClient
from mongodb.content import content_controller, ContentModel
from datetime import datetime, timezone

async def post_and_store(text: str, repository: str, commit_sha: str):
    client = BlueskyClient(identifier, password)
    await client.login()

    # Create post
    result = await client.create_post(text)

    if result["success"]:
        # Store in MongoDB
        content = ContentModel(
            repository=repository,
            commit_sha=commit_sha,
            branch="main",
            summary="Posted to Bluesky",
            timestamp=datetime.now(timezone.utc).isoformat(),
            platform="bluesky",
            status="published",
            content=text,
            image_content=[],
            audio_content=[],
            video_content=[],
            bluesky_uri=result["uri"],
            bluesky_cid=result["cid"]
        )

        content_id = await content_controller.create(content)
        return {"success": True, "content_id": content_id, "uri": result["uri"]}

    return result
```

## Best Practices

1. **Use App Passwords**: Never use your main password. Always create app-specific passwords.

2. **Rate Limiting**: Bluesky has rate limits. Be mindful of API usage.

3. **Error Handling**: Always check the `success` field in responses.

4. **Session Management**: Login once and reuse the client instance.

5. **Text Length**: Posts are limited to 300 characters.

6. **Async Context**: All methods are async, use within async functions.

## Architecture Notes

This client is extracted from the Bluesky MCP server (`bluesky-mcp-python`) and follows these patterns:

- **AT Protocol**: Uses the `atproto` library for all Bluesky interactions
- **Async/Await**: All operations are asynchronous
- **Error Handling**: Comprehensive exception handling with detailed error messages
- **Logging**: Built-in logging for debugging and monitoring
- **Type Hints**: Full type annotations for better IDE support

## Related Files

- `bluesky_client.py` - Main client implementation
- `bluesky_example.py` - Example usage script
- `../servers/bluesky-mcp-python/` - Original MCP server implementation

## References

- [AT Protocol Documentation](https://atproto.com/docs)
- [atproto Python Library](https://github.com/MarshalX/atproto)
- [Bluesky Social](https://bsky.social)

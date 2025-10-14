## Twitter Client

A standalone Python client for interacting with the Twitter API v2 using the tweepy library.

## Installation

The client requires the `tweepy` library:

```bash
pip install tweepy
```

Or add to your `pyproject.toml`:

```toml
dependencies = [
    "tweepy>=4.16.0"
]
```

## Setup

### Getting Twitter API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use an existing one
3. Navigate to "Keys and tokens"
4. Generate the following credentials:
   - **API Key** (Consumer Key)
   - **API Secret Key** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**
   - **Bearer Token** (optional, for app-only auth)

### Required Permissions

Make sure your app has the following permissions:
- **Read and Write** - For posting tweets
- **Read** - For searching tweets

### Environment Variables

Set these environment variables:

```bash
export TWITTER_API_KEY="your-api-key"
export TWITTER_API_SECRET="your-api-secret"
export TWITTER_ACCESS_TOKEN="your-access-token"
export TWITTER_ACCESS_TOKEN_SECRET="your-access-token-secret"
export TWITTER_BEARER_TOKEN="your-bearer-token"  # Optional
```

## Usage

### Basic Example

```python
import asyncio
from twitter_client import TwitterClient

async def main():
    # Initialize client
    client = TwitterClient(
        api_key="your-api-key",
        api_secret="your-api-secret",
        access_token="your-access-token",
        access_token_secret="your-access-token-secret"
    )

    # Post a tweet
    result = await client.post_tweet("Hello Twitter! 🚀")

    if result["success"]:
        print(f"Tweet posted: {result['url']}")
    else:
        print(f"Error: {result['error']}")

asyncio.run(main())
```

### Available Methods

#### Posting Tweets

```python
# Simple tweet
result = await client.post_tweet("Hello world!")

# Tweet with hashtags and mentions
result = await client.post_tweet("Hello @Twitter! #Python #API")
```

#### Posting Threads

```python
# Post a thread of tweets
thread_tweets = [
    "🧵 First tweet in the thread...",
    "2/ Second tweet continues the thread...",
    "3/ Final tweet wraps up!"
]

result = await client.post_thread(thread_tweets)

if result["success"]:
    print(f"Thread posted: {result['thread_url']}")
    print(f"Number of tweets: {result['count']}")
```

#### Searching Tweets

```python
# Search with query
result = await client.search_tweets(
    query="Python programming -is:retweet",
    max_results=20
)

if result["success"]:
    for tweet in result["tweets"]:
        print(f"{tweet['text']}")
        print(f"Likes: {tweet['metrics']['likes']}")
        print(f"URL: {tweet['url']}\n")
```

**Search Query Operators:**
- `"exact phrase"` - Search for exact phrase
- `#hashtag` - Search for hashtag
- `@username` - Search for mentions
- `-term` - Exclude term
- `is:retweet` - Only retweets
- `-is:retweet` - Exclude retweets
- `lang:en` - Filter by language
- `from:username` - From specific user

#### Tweet Interactions

```python
# Like a tweet
result = await client.like_tweet(tweet_id)

# Retweet
result = await client.retweet(tweet_id)

# Delete a tweet
result = await client.delete_tweet(tweet_id)
```

#### User Information

```python
# Get user profile
result = await client.get_user(username="Twitter")

if result["success"]:
    print(f"Name: {result['name']}")
    print(f"Username: @{result['username']}")
    print(f"Followers: {result['followers_count']}")
    print(f"Verified: {result['verified']}")
```

## Response Format

All methods return dictionaries with the following structure:

### Success Response

```python
{
    "success": True,
    "id": "1234567890",  # Tweet/resource ID
    "url": "https://twitter.com/status/1234567890",
    # ... other relevant fields
}
```

### Error Response

```python
{
    "success": False,
    "error": "Error message describing what went wrong",
    "code": "error_code"  # e.g., "rate_limit_exceeded", "forbidden"
}
```

## Rate Limiting

The client includes built-in rate limiting protection:

- **Basic rate limiting**: 1 second between requests to same endpoint
- **Twitter API limits**: The client respects Twitter's rate limits
- **Rate limit errors**: Returns error with `code: "rate_limit_exceeded"`

### Handling Rate Limits

```python
result = await client.post_tweet("Hello!")

if not result["success"] and result.get("code") == "rate_limit_exceeded":
    print("Rate limit exceeded, waiting...")
    await asyncio.sleep(60)  # Wait 1 minute
    result = await client.post_tweet("Hello!")
```

## Error Handling

The client uses comprehensive error handling:

```python
result = await client.post_tweet("Hello!")

if not result["success"]:
    error_code = result.get("code", "unknown")

    if error_code == "rate_limit_exceeded":
        # Handle rate limit
        pass
    elif error_code == "forbidden":
        # Handle permission error
        pass
    elif error_code == "twitter_api_error":
        # Handle Twitter API error
        pass
    else:
        # Handle other errors
        pass
```

## Example Script

Run the comprehensive example script:

```bash
cd backend/src
python twitter_example.py
```

This will:
1. Post a tweet
2. Search for tweets
3. Post a thread
4. Get user information
5. Like a tweet
6. Delete the test tweet

## Integration with MongoDB

Integrate the client with MongoDB for content tracking:

```python
from twitter_client import TwitterClient
from mongodb.content import content_controller, ContentModel
from datetime import datetime, timezone

async def post_and_store(text: str, repository: str, commit_sha: str):
    client = TwitterClient(api_key, api_secret, access_token, access_token_secret)

    # Post to Twitter
    result = await client.post_tweet(text)

    if result["success"]:
        # Store in MongoDB
        content = ContentModel(
            repository=repository,
            commit_sha=commit_sha,
            branch="main",
            summary="Posted to Twitter",
            timestamp=datetime.now(timezone.utc).isoformat(),
            platform="twitter",
            status="published",
            content=text,
            image_content=[],
            audio_content=[],
            video_content=[],
            twitter_id=result["id"],
            twitter_url=result["url"]
        )

        content_id = await content_controller.create(content)
        return {
            "success": True,
            "content_id": content_id,
            "twitter_url": result["url"]
        }

    return result
```

## Best Practices

1. **API Credentials**: Store credentials securely in environment variables, never in code.

2. **Rate Limiting**: The client includes basic rate limiting, but be mindful of Twitter's limits.

3. **Error Handling**: Always check the `success` field in responses.

4. **Tweet Length**: Tweets are limited to 280 characters. The client validates this.

5. **Thread Posting**: Include delay between thread tweets (built-in 1 second delay).

6. **Search Queries**: Use Twitter's search operators for more precise results.

7. **Async Context**: All methods are async, use within async functions.

## Twitter API v2 Features

This client uses Twitter API v2 which provides:

- **Enhanced tweet metrics**: Like, retweet, reply, and quote counts
- **Better search**: More precise search with operators
- **User context**: OAuth 1.0a for user-authenticated requests
- **Thread support**: Reply chaining for threads

## Common Use Cases

### Content Publishing

```python
# Post announcement
result = await client.post_tweet(
    "🚀 New release v2.0 is now live! Check it out: https://example.com #release"
)
```

### Social Monitoring

```python
# Monitor mentions
result = await client.search_tweets(
    query="@YourBrand -is:retweet",
    max_results=50
)

for tweet in result["tweets"]:
    # Process mentions
    print(f"Mention from @{tweet['author_id']}: {tweet['text']}")
```

### Engagement Automation

```python
# Auto-engage with relevant content
result = await client.search_tweets(
    query="Python programming lang:en",
    max_results=10
)

for tweet in result["tweets"]:
    # Like relevant tweets
    await client.like_tweet(tweet["id"])
```

## Troubleshooting

### Authentication Errors

```
Error: Access forbidden
```
- Check your API credentials
- Verify app permissions in Twitter Developer Portal
- Ensure access tokens are generated with correct permissions

### Rate Limit Errors

```
Error: Rate limit exceeded
```
- Wait before retrying (usually 15 minutes)
- Implement exponential backoff
- Check Twitter's rate limit documentation

### Tweet Length Errors

```
Error: Tweet cannot exceed 280 characters
```
- Validate tweet length before posting
- Consider splitting into a thread
- URLs count as 23 characters regardless of length

## Architecture Notes

This client is based on the Twitter MCP server (`twitter-mcp`) and follows these patterns:

- **Tweepy Library**: Uses tweepy for Twitter API v2 interactions
- **Async/Await**: All operations are asynchronous
- **Rate Limiting**: Built-in rate limiting with endpoint tracking
- **Error Handling**: Comprehensive exception handling with error codes
- **Type Hints**: Full type annotations for better IDE support

## Related Files

- `twitter_client.py` - Main client implementation
- `twitter_example.py` - Example usage script
- `../servers/twitter-mcp/` - Original TypeScript MCP server implementation

## References

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- [Twitter API Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)

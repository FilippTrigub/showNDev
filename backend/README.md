## API Usage

### Generate Content

**Endpoint:** `POST /generate-content`

**Request Body:**
```json
{
  "repository": "owner/repo",
  "event": "push",
  "commit_sha": "abc123",
  "branch": "main"
}
```

**Response:**
```json
{
  "message": "Content generated and saved to MongoDB.",
  "content_id": "object_id"
}
```

The backend can call this endpoint to trigger content generation.

## Configuration

- `config.yml`: General configuration
- `prompts.yml`: Prompts for content generation

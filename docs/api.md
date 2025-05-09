# API Documentation

## Endpoints

### Submit URLs for Scraping

#### Single URL

```http
POST /api/tasks/urls/single
```

Request body:
```json
{
    "url": "https://example.com",
    "target_keywords": ["keyword1", "keyword2"]  // Optional
}
```

Response:
```json
{
    "task_id": "uuid-string",
    "status": "PENDING"
}
```

#### Batch URLs

```http
POST /api/tasks/urls/batch
```

Request body:
```json
{
    "urls": ["https://example1.com", "https://example2.com"],
    "target_keywords": ["keyword1", "keyword2"]  // Optional
}
```

Response:
```json
{
    "task_ids": ["uuid-string-1", "uuid-string-2"],
    "status": "PENDING"
}
```

### Check Task Status

```http
GET /api/tasks/{task_id}
```

Response:
```json
{
    "task_id": "uuid-string",
    "status": "SUCCESS|FAILURE|PENDING",
    "result": {
        "status": "success",
        "result_count": 5
    }
}
```

### Retrieve Source Pages

#### Get All Source Pages

```http
GET /api/source-pages
```

Response:
```json
[
    {
        "uid": "uuid-string",
        "url": "https://example.com",
        "status": "SUCCESS",
        "created_at": "2025-05-09T10:00:00Z",
        "targets": [...]
    }
]
```

#### Get Specific Source Page

```http
GET /api/source-pages/{page_uid}
```

Response:
```json
{
    "uid": "uuid-string",
    "url": "https://example.com",
    "status": "SUCCESS",
    "created_at": "2025-05-09T10:00:00Z",
    "targets": [
        {
            "id": "uuid-string",
            "target_url": "https://example.com/page",
            "file_type": "html",
            "relevance_score": 0.85,
            "matched_keywords": ["keyword1", "keyword2"],
            "text": "Extracted content...",
            "created_at": "2025-05-09T10:00:00Z"
        }
    ]
}
```

## Status Codes

- 202 Accepted: Task successfully queued
- 200 OK: Successful request
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server error

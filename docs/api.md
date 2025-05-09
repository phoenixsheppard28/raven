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

### Retrieve Target Pages

#### Get All Target Pages

```http
GET /api/target-pages
```

Query Parameters:
- `file_type` (optional): Filter by file type (e.g., 'text/html', 'application/pdf')
- `min_relevance` (optional): Minimum relevance score (0-10)
- `keyword` (optional): Filter by matched keyword
- `source_uid` (optional): Filter by source page UUID
- `limit` (optional, default: 100): Maximum number of records to return
- `offset` (optional, default: 0): Number of records to skip

Response:
```json
[
    {
        "id": "uuid-string",
        "job_uid": "source-uuid-string",
        "target_url": "https://example.com/page",
        "file_type": "text/html",
        "relevance_score": 8.5,
        "matched_keywords": ["keyword1", "keyword2"],
        "text": "Extracted content...",
        "created_at": "2025-05-09T10:00:00Z"
    }
]
```

#### Get Specific Target Page

```http
GET /api/target-pages/{page_id}
```

Response:
```json
{
    "id": "uuid-string",
    "job_uid": "source-uuid-string",
    "target_url": "https://example.com/page",
    "file_type": "text/html",
    "relevance_score": 8.5,
    "matched_keywords": ["keyword1", "keyword2"],
    "text": "Extracted content...",
    "created_at": "2025-05-09T10:00:00Z"
}
```

### Search

```http
GET /api/search
```

Query Parameters:
- `q` (required): Search query text (min length: 2)
- `min_score` (optional, default: 5.0): Minimum relevance score threshold (0-10)
- `file_types` (optional): List of file types to include

Response:
```json
{
    "query": "search term",
    "count": 5,
    "min_score": 5.0,
    "file_types": ["text/html", "application/pdf"],
    "results": [
        {
            "id": "uuid-string",
            "url": "https://example.com/page",
            "relevance_score": 8.5,
            "file_type": "text/html",
            "matched_keywords": ["keyword1", "keyword2"],
            "snippet": "Relevant text excerpt..."
        }
    ]
}
```

### Statistics

```http
GET /api/statistics
```

Response:
```json
{
    "source_pages": {
        "total": 100,
        "by_status": {
            "COMPLETE": 80,
            "PENDING": 15,
            "FAILED": 5
        }
    },
    "target_pages": {
        "total": 500,
        "avg_relevance_score": 6.1,
        "file_types": {
            "text/html": 450,
            "application/pdf": 50
        },
        "top_keywords": {
            "keyword1": 200,
            "keyword2": 150
        }
    },
    "timestamp": "2025-05-09T10:00:00Z"
}
```

### Administration

#### Reset Database

```http
DELETE /api/admin/reset-database
```

Response:
- On success: Confirmation with status code 200


#### Delete Source Page

```http
DELETE /api/source-pages/{page_uid}
```

Response:
- On success: Confirmation with status code 200
- On failure: 404 Not Found if page doesn't exist

Notes:
-  The deletion of a SourcePage will cascade and delete the TagetPages it was linked to via its primary key

## Status Codes

- 202 Accepted: Task successfully queued
- 200 OK: Successful request
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server error

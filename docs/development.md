# Development Guide

## Local Development Setup

1. Clone the repository
2. Navigate to the project root directory
3. Create and configure environment variables:
   ```bash
   cd app/
   touch .env
   ```
   Add to `.env`:
   ```
   OPENAI_API_KEY=your-api-key
   REDIS_URL="redis://redis:6379/0"
   ```

## Running with Docker

1. Ensure Docker is installed
2. Start the Docker daemon
3. Build and run the containers:
   ```bash
   cd raven/
   docker compose build
   docker compose up
   ```
4. Access the API at `http://localhost:8000` or `http://0.0.0.0:8000`
5. View API documentation at `http://localhost:8000/docs`

## Project Structure

```
app/
├── __init__.py
├── celeryconfig.py      # Celery configuration
├── main.py             # FastAPI application and routes
├── tasks.py            # Celery tasks
├── crawler/
│   ├── spiders/
│   │   └── high_value_link_spider.py  # Main spider implementation
│   ├── middlewares.py  # implement in the future!
│   ├── pipelines.py    # Result collection pipeline
│   ├── run_spider.py   # Spider runner
│   └── settings.py     # Scrapy settings
└── internal/
    ├── db_setup.py     # Database configuration
    ├── models.py       # SQLModel definitions
    └── secrets.py      # Environment configuration
```

## Configuration

### Spider Settings (`crawler/settings.py`)
- `DEPTH_LIMIT`: Controls how deep the spider crawls (default: 2)
- `DOWNLOAD_DELAY`: Delay between requests (default: 0.1s)
- `DEFAULT_TARGET_KEYWORDS`: Default keywords for relevance scoring

### Celery Settings (`celeryconfig.py`)
- `worker_max_tasks_per_child`: Tasks per worker (default: 1)
- `worker_concurrency`: Number of concurrent workers (default: 8)
- `task_time_limit`: Hard time limit for tasks (default: 480s)

## Database Schema

### SourcePage
- `uid`: UUID (Primary Key)
- `url`: Source URL
- `status`: Task status
- `created_at`: Timestamp
- `targets`: Relationship to TargetPage

### TargetPage
- `id`: UUID (Primary Key)
- `job_uid`: Foreign key to SourcePage
- `target_url`: URL of found link
- `file_type`: Content type
- `relevance_score`: AI-computed relevance
- `matched_keywords`: List of matched keywords
- `text`: Extracted content
- `created_at`: Timestamp

## Adding New Features

1. **New Spider Features**
   - Modify `high_value_link_spider.py`
   - Update relevance scoring in `rank_relevance()`
   - Add new extraction methods as needed

2. **API Endpoints**
   - Add routes in `main.py`
   - Create new Pydantic models for request/response
   - Update documentation

3. **Database Changes**
   - Modify models in `models.py`
   - Update database schema
   - Add migrations if needed



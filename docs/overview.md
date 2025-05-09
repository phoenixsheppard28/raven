# Project Overview


## Key Features

- **Smart Link Analysis**: Analyzes web pages and extracts links based on relevance to specified keywords
- **Customizable Keywords**: Supports custom keyword sets for targeted scraping
- **AI-Powered Scoring**: Uses OpenAI's GPT models to evaluate content relevance
- **Asynchronous Processing**: Handles scraping tasks in the background using Celery
- **RESTful API**: Provides easy access to scraping functionality and results
- **Docker Support**: Full containerization for easy deployment

## Architecture Components

- FastAPI web server for API endpoints
- Celery for asynchronous task processing
- Redis for task queue management
- SQLite database (can be upgraded to PostgreSQL for production)
- Scrapy for efficient web crawling
- OpenAI integration for content analysis

## Technology Stack

- Python 3.13
- FastAPI
- Celery
- Redis
- SQLModel/SQLAlchemy
- Scrapy
- OpenAI GPT-3.5
- Docker

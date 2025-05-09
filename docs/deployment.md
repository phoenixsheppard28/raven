# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Redis instance (local or hosted)
- Database (SQLite for development, PostgreSQL recommended for production)

## Production Deployment Considerations

### 1. Database Migration

For production, it's recommended to migrate from SQLite to PostgreSQL:

1. Update database URL in `db_setup.py`
2. Install PostgreSQL dependencies
3. Create initial migration
4. Set up backup strategy

### 2. Security Considerations

- Use proper API authentication
- Implement rate limiting
- Set up HTTPS
- Secure Redis instance
- Store secrets in a secure vault
- Implement proper logging

### 3. Scaling

#### Horizontal Scaling
- Increase Celery workers (`worker_concurrency`)
- Use load balancer for API servers
- Scale Redis with Redis Cluster
- Consider using a CDN

#### Vertical Scaling
- Optimize database queries
- Implement caching
- Tune crawler settings
- Adjust memory allocation

### 4. Monitoring

Implement monitoring for:
- API endpoints health
- Celery task queue
- Redis performance
- Database performance
- Spider success rates
- Rate limiting status

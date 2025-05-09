from fastapi import FastAPI, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
from app.tasks import scrape_and_store
from celery.result import AsyncResult
from app.internal.db_setup import engine, SourcePage, TargetPage
from sqlmodel import Session, select, delete, or_, and_
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from uuid import UUID

# Response models for better documentation
class TaskResponse(BaseModel):
    task_id: UUID
    status: str

class BatchTaskResponse(BaseModel):
    task_ids: List[UUID]
    count: int

class SourcePageResponse(BaseModel):
    uid: UUID
    url: str
    status: str
    created_at: datetime

class TargetPageResponse(BaseModel):
    id: UUID
    job_uid: UUID
    target_url: str
    file_type: str
    relevance_score: float
    matched_keywords: List[str]
    text: Optional[str] = None
    created_at: datetime

# Request models
class ScrapeUrlRequest(BaseModel):
    url: HttpUrl
    target_keywords: Optional[List[str]] = None

class BatchScrapeRequest(BaseModel):
    urls: List[HttpUrl]
    target_keywords: Optional[List[str]] = None


def add_tasks(urls: List[str], target_keywords: List[str]) -> List[AsyncResult]:
    """
    Add scraping tasks to the Celery queue and return task results.

    Args:
        urls (List[str]): List of URLs to scrape.
        target_keywords (Optional[List[str]]): Optional list of keywords to prioritize during scraping.

    Returns:
        List[AsyncResult]: List of task results corresponding to the scraping jobs.
    """
    results = []
    for url in urls:
        result: AsyncResult = scrape_and_store.delay(url, target_keywords)
        results.append(result)
    return results


def get_session():
    """
    Create and yield a database session.
    """
    with Session(engine) as session:
        yield session


app = FastAPI(
    title="Web Scraping API",
    description="API for managing web scraping tasks and accessing scraped data",
    version="1.0.0",
)

# Organize endpoints by tags
@app.post(
    "/api/tasks/urls/single",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Tasks"],
    summary="Submit a single URL for scraping"
)
async def submit_scrape(request: ScrapeUrlRequest, session: Session = Depends(get_session)):
    """
    Submit a single URL to be scraped.
    
    Args:
        request (ScrapeUrlRequest): Request object containing the URL and optional target keywords.
        session (Session): Database session dependency.
    
    Returns:
        TaskResponse: Contains the task ID and initial status.
    """
    # Start the Celery task but don't try to access its status
    result = scrape_and_store.delay(str(request.url), request.target_keywords)
    
    # Return a fixed status since we can't access Celery's status
    return {"task_id": result.id, "status": "PENDING"}



@app.post(
    "/api/tasks/urls/batch",
    response_model=BatchTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Tasks"],
    summary="Submit a batch of URLs for scraping"
)
async def submit_batch_scrape(request: BatchScrapeRequest):
    """
    Submit a batch of URLs to be scraped in parallel.
    
    Args:
        request (BatchScrapeRequest): Request object containing list of URLs and optional target keywords.
    
    Returns:
        BatchTaskResponse: Contains list of task IDs and count of jobs submitted.
    """
    url_strings = [str(url) for url in request.urls]
    results = add_tasks(url_strings, request.target_keywords)
    task_ids = [task.id for task in results]
    return {"task_ids": task_ids, "count": len(task_ids)}


@app.get("/api/tasks/{task_id}")
async def get_task_status(
    task_id: str = Path(..., description="The ID of the scraping task"),
    session: Session = Depends(get_session)
):
    try:
        uid_obj = UUID(task_id)        
        source_page = session.exec(
            select(SourcePage).where(SourcePage.uid == uid_obj)
        ).first()
    except ValueError:
        # Handle invalid UUID format
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    if not source_page:
        return {
            "task_id": task_id,
            "status": "PENDING"  # Default status if not found
        }
    response = {
        "task_id": task_id,
        "status": source_page.status
    }
    if source_page.status == "COMPLETED":
        target_pages = session.exec(
            select(TargetPage).where(TargetPage.job_uid == source_page.uid)
        ).all()
        response["result"] = {
            "url": source_page.url,
            "scraped_at": source_page.scraped_at,
            "target_count": len(target_pages)
        }
    return response





@app.get(
    "/api/source-pages",
    response_model=List[SourcePageResponse],
    tags=["Source Pages"],
    summary="Get all source pages"
)
async def list_source_pages(
    status: Optional[str] = Query(None, description="Filter by status (PENDING, COMPLETED, FAILURE)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    session: Session = Depends(get_session)
):
    """
    Retrieve all scraped source pages stored in the database with optional filtering.
    
    Args:
        status (Optional[str]): Filter pages by their status.
        limit (int): Maximum number of records to return (default: 100).
        offset (int): Number of records to skip for pagination (default: 0).
        session (Session): Database session dependency.
    
    Returns:
        List[SourcePageResponse]: List of stored source page entries.
    """
    query = select(SourcePage)
    
    if status:
        query = query.where(SourcePage.status == status)
    
    pages = session.exec(query.offset(offset).limit(limit)).all()
    return pages


@app.get(
    "/api/source-pages/{page_uid}",
    response_model=SourcePageResponse,
    tags=["Source Pages"],
    summary="Get a specific source page"
)
async def get_source_page(
    page_uid: str = Path(..., description="UUID of the source page"),
    session: Session = Depends(get_session)
):
    """
    Get details of a specific source page by its UUID.
    
    Args:
        page_uid (str): The UUID of the source page.
        session (Session): Database session dependency.
    
    Returns:
        SourcePageResponse: Details of the requested source page.
        
    Raises:
        HTTPException: If the source page is not found.
    """
    try:
        uid_obj = UUID(page_uid)
        page = session.exec(select(SourcePage).where(SourcePage.uid == uid_obj)).first()
        if not page:
            raise HTTPException(status_code=404, detail="Source page not found")
        return page
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


@app.get(
    "/api/target-pages",
    response_model=List[TargetPageResponse],
    tags=["Target Pages"],
    summary="Get all target pages with optional filtering"
)
async def list_target_pages(
    file_type: Optional[str] = Query(None, description="Filter by file type (e.g., 'text/html', 'application/pdf')"),
    min_relevance: Optional[float] = Query(None, ge=0, le=10, description="Minimum relevance score (0-10)"),
    keyword: Optional[str] = Query(None, description="Filter by matched keyword"),
    source_uid: Optional[str] = Query(None, description="Filter by source page UUID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    session: Session = Depends(get_session)
):
    """
    Retrieve target pages with optional filtering by various criteria.
    
    Args:
        file_type (Optional[str]): Filter pages by file type.
        min_relevance (Optional[float]): Filter pages by minimum relevance score.
        keyword (Optional[str]): Filter pages that contain a specific keyword.
        source_uid (Optional[str]): Filter pages by their source page UUID.
        limit (int): Maximum number of records to return (default: 100).
        offset (int): Number of records to skip for pagination (default: 0).
        session (Session): Database session dependency.
    
    Returns:
        List[TargetPageResponse]: List of filtered target pages.
    """
    query = select(TargetPage)
    filters = []
    
    if file_type:
        filters.append(TargetPage.file_type == file_type)
    
    if min_relevance is not None:
        filters.append(TargetPage.relevance_score >= min_relevance)
    
    if keyword:
        # This requires JSON querying capability which differs by database
        # For SQLite, this may not work directly and might need a different approach
        # This is a simplified approach assuming matched_keywords is queryable
        filters.append(TargetPage.matched_keywords.contains([keyword]))
    
    if source_uid:
        try:
            uid_obj = UUID(source_uid)
            filters.append(TargetPage.job_uid == uid_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    if filters:
        query = query.where(and_(*filters))
    
    pages = session.exec(query.offset(offset).limit(limit)).all()
    return pages


@app.get(
    "/api/target-pages/{page_id}",
    response_model=TargetPageResponse,
    tags=["Target Pages"],
    summary="Get a specific target page"
)
async def get_target_page(
    page_id: str = Path(..., description="UUID of the target page"),
    session: Session = Depends(get_session)
):
    """
    Get details of a specific target page by its UUID.
    
    Args:
        page_id (str): The UUID of the target page.
        session (Session): Database session dependency.
    
    Returns:
        TargetPageResponse: Details of the requested target page.
        
    Raises:
        HTTPException: If the target page is not found.
    """
    try:
        id_obj = UUID(page_id)
        page = session.exec(select(TargetPage).where(TargetPage.id == id_obj)).first()
        if not page:
            raise HTTPException(status_code=404, detail="Target page not found")
        return page
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


@app.get(
    "/api/search",
    tags=["Search"],
    summary="Search across target pages"
)
async def search_target_pages(
    q: str = Query(..., min_length=2, description="Search query text"),
    min_score: float = Query(5.0, ge=0, le=10, description="Minimum relevance score threshold"),
    file_types: List[str] = Query(None, description="List of file types to include"),
    session: Session = Depends(get_session)
):
    """
    Search functionality across target pages with filtering options.
    
    Args:
        q (str): Search query text (searches in matched keywords and text content).
        min_score (float): Minimum relevance score to include in results (default: 5.0).
        file_types (List[str]): Optional list of file types to include in search.
        session (Session): Database session dependency.
    
    Returns:
        dict: Search results with metadata.
    """
    # Base query with minimum score
    query = select(TargetPage).where(TargetPage.relevance_score >= min_score)
    
    # Add filters
    filters = []
    
    # Filter for text search in content and keywords
    # Note: This is a simplified approach that may need adaptation based on your DB
    filters.append(or_(
        TargetPage.text.contains(q),
        TargetPage.matched_keywords.contains([q])
    ))
    
    # Add file type filter if specified
    if file_types:
        filters.append(TargetPage.file_type.in_(file_types))
    
    # Apply all filters
    if filters:
        query = query.where(and_(*filters))
    
    # Execute query
    results = session.exec(query.limit(100)).all()
    
    # Prepare response
    return {
        "query": q,
        "count": len(results),
        "min_score": min_score,
        "file_types": file_types,
        "results": [
            {
                "id": str(page.id),
                "url": page.target_url,
                "relevance_score": page.relevance_score,
                "file_type": page.file_type,
                "matched_keywords": page.matched_keywords,
                # Include a snippet of text if available
                "snippet": page.text[:200] + "..." if page.text and len(page.text) > 200 else page.text
            }
            for page in results
        ]
    }


@app.get(
    "/api/statistics",
    tags=["Analytics"],
    summary="Get statistics about scraped data"
)
async def get_scraping_statistics(session: Session = Depends(get_session)):
    """
    Get statistical information about the scraped data.
    
    Args:
        session (Session): Database session dependency.
    
    Returns:
        dict: Statistics about source pages and target pages.
    """
    # Count source pages by status
    source_pages_total = session.exec(select(SourcePage)).all()
    status_counts = {}
    for page in source_pages_total:
        status_counts[page.status] = status_counts.get(page.status, 0) + 1
    
    # Get target pages summary
    target_pages = session.exec(select(TargetPage)).all()
    
    # Calculate average relevance score
    avg_score = sum(page.relevance_score for page in target_pages) / len(target_pages) if target_pages else 0
    
    # Count file types
    file_type_counts = {}
    for page in target_pages:
        file_type_counts[page.file_type] = file_type_counts.get(page.file_type, 0) + 1
    
    # Get top keywords
    keyword_counts = {}
    for page in target_pages:
        for keyword in page.matched_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "source_pages": {
            "total": len(source_pages_total),
            "by_status": status_counts
        },
        "target_pages": {
            "total": len(target_pages),
            "avg_relevance_score": avg_score,
            "file_types": file_type_counts,
            "top_keywords": dict(top_keywords)
        },
        "timestamp": datetime.utcnow()
    }


@app.delete(
    "/api/admin/reset-database",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Administration"],
    summary="Reset the database"
)
async def reset_database(session: Session = Depends(get_session)):
    """
    Reset the database by deleting all entries in SourcePage and TargetPage tables.
    This is useful for clearing out old data and starting fresh.
    
    Args:
        session (Session): Database session dependency.
    
    Returns:
        Response with 200 on success.
    """
    session.exec(delete(TargetPage))
    session.exec(delete(SourcePage))
    session.commit()
    return JSONResponse(content={"message": "Successfully deleted all data in database"}, status_code=200)


@app.delete(
    "/api/source-pages/{page_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Source Pages"],
    summary="Delete a source page and its target pages"
)
async def delete_source_page(
    page_uid: str = Path(..., description="UUID of the source page to delete"),
    session: Session = Depends(get_session)
):
    """
    Delete a specific source page and all its associated target pages.
    
    Args:
        page_uid (str): The UUID of the source page to delete.
        session (Session): Database session dependency.
    
    Returns:
        Response with 204 No Content status code on success.
        
    Raises:
        HTTPException: If the source page is not found or if there's an error.
    """
    try:
        uid_obj = UUID(page_uid)
        
        # First delete related target pages
        session.exec(delete(TargetPage).where(TargetPage.job_uid == uid_obj))
        
        # Then delete the source page
        result = session.exec(delete(SourcePage).where(SourcePage.uid == uid_obj))
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Source page not found")
            
        session.commit()
        return JSONResponse(content={"message": "Source page and related target pages deleted"}, status_code=200)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting page: {str(e)}")

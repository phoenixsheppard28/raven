from sqlmodel import Field, SQLModel, Relationship
import uuid
from typing import Optional, List
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy import Column
from datetime import datetime



class SourcePage(SQLModel,table=True):
    uid: uuid.UUID = Field(nullable=False, primary_key=True)
    url: str 
    status: str = Field(default="PENDING") # -- SUCCESS, FAILURE, PENDING, COMPLETED derived from celery status 
    created_at: datetime = Field(default_factory=datetime.utcnow())
    targets: List["TargetPage"] = Relationship(back_populates="source") 


class TargetPage(SQLModel,table=True):
    id: uuid.UUID = Field(nullable=False, primary_key=True)
    job_uid: uuid.UUID = Field(foreign_key="sourcepage.uid")  
    target_url: str
    file_type: str
    relevance_score: float
    matched_keywords: List[str] = Field(sa_column=Column(JSON))
    text: Optional[str] = Field(default=None) 
    created_at: datetime = Field(default_factory=datetime.utcnow())
    source: Optional[SourcePage] = Relationship(back_populates="targets") 
 
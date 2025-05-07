import sqlite3
from sqlmodel import Field, SQLModel, create_engine, select
import uuid


class Page(SQLModel,table=True):
    uid: uuid.UUID = Field(nullable=False, primary_key=True)
    url: str 
    status: str = Field(default="PENDING") # -- SUCCESS, FAILURE, PENDING, COMPLETED derived from celery status 
    result: str

engine = create_engine("sqlite:///database.db") # should be swapped for postgresql upon higher throughput for higher write capacity
SQLModel.metadata.create_all(engine)

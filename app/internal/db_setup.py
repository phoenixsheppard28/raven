from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import delete
from app.internal.models import SourcePage, TargetPage



engine = create_engine("sqlite:///app/database.db") # should be swapped for postgresql in production
SQLModel.metadata.create_all(engine)

def reset_db():
    with Session(engine) as session:
        session.exec(delete(SourcePage))
        session.exec(delete(TargetPage))
        session.commit()

if __name__=="__main__":
    reset_db()
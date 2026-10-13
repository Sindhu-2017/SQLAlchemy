from collections.abc import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from database.session import get_db

def get_database(db: Session = Depends(get_db),) -> Generator[Session, None, None]:
    yield db

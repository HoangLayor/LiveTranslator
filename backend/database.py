from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Create database directory if it doesn't exist
DB_DIR = "data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# SQLite database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_DIR}/livetranslator.db"

# Create SQLite engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
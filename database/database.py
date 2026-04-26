from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 👉 password simple rakho (no @)
DATABASE_URL = "postgresql://postgres:civik8780@localhost:5432/civicsense_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# SQLALCHEMY_DATABASE_URL="sqlite:///./login.db"
SQLALCHEMY_DATABASE_URL="postgresql://sachin21:1354@localhost/todos"

engine=create_engine(
    SQLALCHEMY_DATABASE_URL)
SessionLocal=sessionmaker(
    autocommit=False,bind=engine
)
Base=declarative_base()

from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
# from database import Base, engine, SessionLocal
from flask_sqlalchemy import SQLAlchemy

database_url = "postgresql://sachin21:1354@localhost/todos"

async def connect_to_db():
    return await asyncpg.connect(database_url)

app=FastAPI()

@app.on_event("startup")
async def startup():
    app.state.db = await connect_to_db()
    print("Connected to PostgreSQL")

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()
    print("Disconnected from PostgreSQL")
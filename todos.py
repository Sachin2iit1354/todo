from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from database import Base, engine, SessionLocal
from flask_sqlalchemy import SQLAlchemy


class TodoItem(BaseModel):
    id: int
    title: str
    description: str

app = FastAPI()
todo_items = []

# PostgreSQL connection details
database_url = "postgresql://sachin21:1354@localhost/todos"

async def connect_to_db():
    return await asyncpg.connect(database_url)

@app.on_event("startup")
async def startup():
    app.state.db = await connect_to_db()
    print("Connected to PostgreSQL")

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()
    print("Disconnected from PostgreSQL")

@app.get("/todos")
async def get_todos():
    query = "SELECT id, title, description FROM todos"
    todos = await app.state.db.fetch(query)
    return todos

@app.get("/todos/{todo_id}")
async def get_todo_by_id(todo_id: int):
    query = "SELECT id, title, description FROM todos WHERE id = $1"
    todo = await app.state.db.fetchrow(query, todo_id)
    if todo:
        return todo
    return {"error": "Todo not found"}

@app.post("/todos")
async def create_todo(todo: TodoItem):
    query = "INSERT INTO todos (id, title, description) VALUES ($1, $2, $3)"
    await app.state.db.execute(query, todo.id, todo.title, todo.description)
    return {"message": "Todo created successfully"}

@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, updated_todo: TodoItem):
    query = "UPDATE todos SET title = $1, description = $2 WHERE id = $3"
    result = await app.state.db.execute(query, updated_todo.title, updated_todo.description, todo_id)
    if result == "UPDATE 1":
        return {"message": "Todo updated successfully"}
    return {"error": "Todo not found"}

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    query = "DELETE FROM todos WHERE id = $1"
    result = await app.state.db.execute(query, todo_id)
    if result == "DELETE 1":
        return {"message": "Todo deleted successfully"}
    return {"error": "Todo not found"}


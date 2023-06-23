from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
# ...

app = FastAPI()
database_url = "postgresql://sachin21:1354@localhost/todos"
async def connect_to_db():
    return await asyncpg.connect(database_url)

# app=FastAPI()
@app.on_event("startup")
async def startup():
    app.state.db = await connect_to_db()
    print("Connected to PostgreSQL")

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()
    print("Disconnected from PostgreSQL")

SECRET_KEY = "a113722bc11930b83db28cbcfe951667389930ed96a63adeb204f084025d7e67"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TodoItem(BaseModel):
    title: str
    description: str


todo_items = []
# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ...

class User(BaseModel):
    username: str
    password: str

# In a real application, user information should be stored in a database
# For simplicity, we'll use a hardcoded user here
print(1)
fake_users_db = {
    "username": "admin",
    "hashed_password": "",  # Hashed password for "password123"
}
print(2)
# print(fake_users_db["hashed_password"])
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
    # return "sachin@21"

def get_user(username: str):
    # print(username)
    if fake_users_db["username"]:
        # print("Yadav")
        user_dict = fake_users_db["username"]
        return User(username=fake_users_db["username"], password=fake_users_db["hashed_password"])

def authenticate_user(username: str, password: str):
    # print(username+" "+password)
    user = get_user(username)
    # print(user)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@app.post("/token",tags=["User"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    # print(form_data.username+" Yadav "+form_data.password)
    # print(user)
    if not user:
        # print("Yadav")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/testapi",tags=["User"])
async def test(name:str):
    # user = authenticate_user(form_data.username, form_data.password)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Invalid username or password")
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = create_access_token(
    #     data={"sub": user.username}, expires_delta=access_token_expires
    # )
    # return {"access_token": access_token, "token_type": "bearer"}
    return {"name":name}

@app.get("/todos",tags=["Todo"])
async def get_todos(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # You can perform additional checks here based on the payload if needed
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token signature invalid")
    
    # Your existing code to fetch todos
    query = "SELECT id, title, description FROM todos"
    todos = await app.state.db.fetch(query)
    return todos

# Modify other routes in a similar way

# ...
@app.get("/todos/{todo_id}",tags=["Todo"])
async def get_todo_by_id(todo_id: int,token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # You can perform additional checks here based on the payload if needed
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token signature invalid")
    query = "SELECT id, title, description FROM todos WHERE id = $1"
    todo = await app.state.db.fetchrow(query, todo_id)
    if todo:
        return todo
    return {"error": "Todo not found"}

@app.post("/todos",tags=["Todo"])
async def create_todo(todo: TodoItem,token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # You can perform additional checks here based on the payload if needed
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token signature invalid")
    query = "INSERT INTO todos (title, description) VALUES ($1, $2)"
    await app.state.db.execute(query, todo.title, todo.description)
    return {"message": "Todo created successfully"}

@app.put("/todos/{todo_id}",tags=["Todo"])
async def update_todo(todo_id: int, updated_todo: TodoItem,token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # You can perform additional checks here based on the payload if needed
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token signature invalid")
    query = "UPDATE todos SET title = $1, description = $2 WHERE id = $3"
    result = await app.state.db.execute(query, updated_todo.title, updated_todo.description, todo_id)
    try:
        result == "UPDATE 1"
        return {"message": "Todo updated successfully"}
    except:
        return {"error": "Todo not found"}

@app.delete("/todos/{todo_id}",tags=["Todo"])
async def delete_todo(todo_id: int,token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # You can perform additional checks here based on the payload if needed
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token signature invalid")
    query = "DELETE FROM todos WHERE id = $1"
    result = await app.state.db.execute(query, todo_id)
    try:
        result == "DELETE 1"
        return {"message": "Todo deleted successfully"}
    except:
        return {"error": "Todo not found"}

x= get_password_hash("sachin@21")
print("*"+x+"*")
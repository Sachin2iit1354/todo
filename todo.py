from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
from fastapi import HTTPException
from pydantic import BaseModel, Field, EmailStr
from fastapi import FastAPI, Body
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request
# from app.model import PostSchema, UserSchema, UserLoginSchema
# from app.auth.auth_handler import signJWT
# from app import PostSchema
import time
from typing import Dict
import os
import jwt
from decouple import config
from passlib.context import CryptContext
from fastapi import FastAPI, Body, Depends

JWT_SECRET = "pleasepleasekuchhbhi12343"
JWT_ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TodoItem(BaseModel):
    username:str
    first_name:str
    last_name:str
    email:str
    password:str

class login_schema(BaseModel):
    email:str
    password:str

def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            cred = self.verify_jwt(credentials.credentials)
            # print(cred)
            request.state.payload = cred[1]
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not cred[0]:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )

            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid, payload

def token_response(token: str):
    return {
        "access_token": token
    }


app = FastAPI(debug=True)

users=[]

database_url = "postgresql://sachin21:1354@localhost/test"

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

posts=[]

@app.post("/user/signup",tags=["user"])
async def create_columns(item:TodoItem):
    query = "INSERT INTO person (username,first_name,last_name,email,password) VALUES ($1,$2,$3,$4,$5)"
    await app.state.db.execute(query,item.username,item.first_name,item.last_name,item.email,item.password)
    return {"message": "User signed-up successfully!"}

@app.post("/user/login",tags=["user"])
async def user_login(request:Request,user:login_schema):
    # payload=request.state.payload
    # x=payload["user_id"]
    # return x
    query="SELECT email,password FROM person WHERE email=$1 AND password=$2"
    results=await app.state.db.fetch(query,user.email,user.password)
    if results:
        return signJWT(user.email)
    return "User doesn't exist!"

@app.get('/user/get/{}',dependencies=[Depends(JWTBearer())],tags=['Get'])
async def get_details():
    query = "SELECT * FROM person"
    todos = await app.state.db.fetch(query)
    return todos

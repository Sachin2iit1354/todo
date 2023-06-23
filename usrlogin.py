from fastapi import FastAPI, Depends,File,UploadFile
from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from database import Base, engine, SessionLocal
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "login"
    email = Column(String, primary_key=True)
    First_Name = Column(String,unique=False)
    Last_Name = Column(String,unique=False)
    City = Column(String,unique=False)
    Password = Column(String,unique=False)

class UserSchema(BaseModel):
    First_Name: str
    Last_Name: str
    City: str
    email: str
    Password: str

    class Config:
        orm_mode = True

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
web_hook_url='https://hooks.slack.com/services/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'
current_time = datetime.now().time()
@app.post('/signup')
async def signup(user: UserSchema, db: Session = Depends(get_db)):
    if '@gmail.com' not in user.email:
        return {"Email ID is Invalid"}
    
    user_exists = db.query(User).filter(User.email == user.email).first()
    if user_exists:
        return {"status": "Email id already exists"}
    
    hashed_password = pwd_context.hash(user.Password)
    new_user = User(
        email=user.email,
        First_Name=user.First_Name,
        Last_Name=user.Last_Name,
        City=user.City,
        Password=hashed_password
    )
    db.add(new_user)
    db.commit()
    slack_mess={'text':f'{user.First_Name} {user.Last_Name} has successfully signed up at {current_time}.'}
    requests.post(web_hook_url,data=json.dumps(slack_mess))
    return new_user

@app.get('/users')
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

import requests
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/post-thumbnail")
async def post_thumbnail_to_slack(thumbnail_url: str):
    # Assuming you have a Slack webhook URL
    slack_webhook_url = "https://hooks.slack.com/services/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"

    # Construct the Slack message payload
    payload = {
        "text": f"New thumbnail from Facebook: {thumbnail_url}",
        "attachments": [
            {
                "image_url": thumbnail_url
            }
        ]
    }

    # Send the payload to Slack
    response = requests.post(slack_webhook_url, json=payload)
    if response.status_code == 200:
        return {"message": "Thumbnail posted to Slack successfully"}
    else:
        return {"message": "Error posting thumbnail to Slack"}

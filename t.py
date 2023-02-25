from fastapi import FastAPI, HTTPException, status,Depends
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasic, HTTPBasicCredentials
from passlib.hash import bcrypt
from tortoise import fields 
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model 
import jwt

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

#JWT_SECRET = 'myjwtsecret'

client = MongoClient("mongodb+srv://goyalaryan:goyalaryan@cluster0.6mnaomm.mongodb.net/test")
db = client["todo_db"]
collection = db["todo_collection"]

class TodoItem(BaseModel):
    title: str
    description : str

class TodoItemWithStatus(BaseModel):
    status: bool
users = {
    "user1": "password1",
    "user2": "password2",
}

# Define a Pydantic model for user authentication
class UserCredentials(BaseModel):
    username: str
    password: str

# Create a basic HTTP authentication object
security = HTTPBasic()

# Define a dependency to get the current user based on their credentials
async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if username in users and users[username] == password:
        return {"username": username}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

# Define a protected endpoint that requires authentication
@app.get("/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['username']}!"}
@app.get("/items/")
async def read_items(current_user: dict = Depends(get_current_user)):
    items = []
    for item in collection.find():
        item["_id"] = str(item["_id"])
        items.append(item)
    return items

@app.post("/items/")
async def create_item(item: TodoItem,current_user: dict = Depends(get_current_user)):
    item_data = {"title": item.title,"description": item.description, "status": False}
    result = collection.insert_one(item_data)  
    item_data["_id"] = str(result.inserted_id)
    return item_data

@app.put("/items/{item_id}")
async def update_item(item_id: str,item: TodoItemWithStatus,current_user: dict = Depends(get_current_user)):
    result = collection.update_one({"_id": ObjectId(item_id)}, {"$set": {"status": item.status}})
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"message": "Item updated"}

@app.delete("/items/{item_id}")
async def delete_item(item_id: str,current_user: dict = Depends(get_current_user)):
    result = collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"message": "Item deleted"}

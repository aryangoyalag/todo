from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel

app = FastAPI()

client = MongoClient("mongodb+srv://goyalaryan:goyalaryan@cluster0.6mnaomm.mongodb.net/test")
db = client["todo_db"]
collection = db["todo_collection"]

class TodoItem(BaseModel):
    title: str

class TodoItemWithStatus(BaseModel):
    status: bool

@app.get("/items/")
async def read_items():
    items = []
    for item in collection.find():
        item["_id"] = str(item["_id"])
        items.append(item)
    return items

@app.post("/items/")
async def create_item(item: TodoItem):
    item_data = {"title": item.title, "status": False}
    result = collection.insert_one(item_data)
    item_data["_id"] = str(result.inserted_id)
    return item_data

@app.put("/items/{item_id}")
async def update_item(item_id: str, item: TodoItemWithStatus):
    result = collection.update_one({"_id": ObjectId(item_id)}, {"$set": {"status": item.status}})
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"message": "Item updated"}

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"message": "Item deleted"}

from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from uuid import UUID
from src.api.dto import User

app = FastAPI(title="Profile Service API",)

@app.get("/who_i_am")
def who_i_am():
    return {"message": "I am profile service!"}

# @app.get("/profile")
@app.get("")
def get_profiles(skip: int = 0, limit: int = 10):   # query params
    return {
        "message": "Return List Of Users",
        "skip": skip,
        "limit": limit
    }

@app.get("/{id}")
def get_profile(id: UUID):
    return {"id": id, "name": "Your Name"}

@app.put("/{id}")
def update_profile(user: User):
    return {"message": "User Updated"}

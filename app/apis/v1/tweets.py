# app/api/api_v1/endpoints/tweets.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_tweets():
    return [{"content": "Hello World"}, {"content": "FastAPI is awesome"}]
from fastapi import APIRouter
from app.apis.v1.auth import router as auth
from app.apis.v1.tweets import router as tweets

router = APIRouter()

api_v1_router = APIRouter()
api_v1_router.include_router(auth, prefix="/auth", tags=["auth"])
api_v1_router.include_router(tweets, prefix="/tweets", tags=["tweets"])

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.twitter_clone

# ================== Users collections ============
userCollection = db.users
userCircleCollection = db.userCircles
postCollection = db.posts
postUserCollection = db.postUsers

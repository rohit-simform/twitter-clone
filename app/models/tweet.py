from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Post DB Modal


class Post(BaseModel):
    description: str
    imageURL: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


# Post_User DB Modal
class PostUser(BaseModel):
    userId: str
    postId: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

# Timeline DB Model --> Post Cache DB


class Timeline(BaseModel):
    userId: str
    postUserIds: List[str] = Field(default=[])
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


# =============== Req/Res payload models ===================

# new tweet Payload
class NewTweetPayload(Post):
    userId: Optional[str] = None

# Tweet feed


class TweetFeedPayload(BaseModel):
    fromDate: Optional[str] = None
    searchUserFeed: Optional[str] = None

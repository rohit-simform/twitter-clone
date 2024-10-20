from pydantic import BaseModel, Field
from typing import List, Optional

# Post DB Modal


class Post(BaseModel):
    description: str
    imageURL: Optional[str] = None


# Post_User DB Modal
class PostUser(BaseModel):
    userId: str
    postId: str


# =============== Req/Res payload models ===================

# new tweet Payload
class NewTweetPayload(Post):
    userId: Optional[str] = None

# Tweet feed


class TweetFeedPayload(BaseModel):
    fromDate: Optional[str] = None
    searchUserFeed: Optional[str] = None

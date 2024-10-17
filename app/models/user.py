from pydantic import BaseModel, Field
from typing import List

# UserCircle DB Modal


class UserCircle(BaseModel):
    userId: str
    followers: List[str] = Field(default=[])
    following: List[str] = Field(default=[])


# =============== Req/Res payload models ===================

# followed user Payload
class FollowUserPayload(BaseModel):
    userId: str

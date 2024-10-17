
from fastapi import HTTPException, status
from fastapi import APIRouter
router = APIRouter()

# follow user api


@router.get("/follow/:follow_user_id")
async def follow_user():
    # fetch userId from jwt
    # check follow_user_id is already exists or not in db
    # if exists then remove [from userId and follow_user_id doc otherwise add.
    # for adding --
    # add follow_user_id into following field as respect to userId
    # similary add userId into followers field as respect to follow_userId

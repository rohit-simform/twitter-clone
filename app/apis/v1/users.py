
from fastapi import HTTPException, status
from fastapi import APIRouter, Request
from app.db.mongo_conn import userCollection, userCircleCollection

from app.utils.utils import verify_token
router = APIRouter()

# follow user api


@router.get("/follow/{follow_user_id}")
async def follow_user(follow_user_id: str, request: Request):
    # fetch userId from jwt
    access_token = request.headers.get('Authorization')
    print(access_token)
    access_token = access_token.split(" ")

    # HTTPException Error response format
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print(access_token[1])

    token_data = verify_token(access_token[1], credentials_exception)

    if token_data is None:
        return {
            "success": False,
            "msg": "Token is invalid or expired."
        }

    userId = token_data.userId

    userCircle = await userCircleCollection.find_one({"userId": userId})
    followUserCircle = await userCircleCollection.find_one({"userId": follow_user_id})

    print(userCircle)
    print(followUserCircle)
    if userCircle is None or followUserCircle is None:
        return {
            "success": False,
            "msg": "Unknown or missing Ids."
        }

    isAlreadyFollowedUser = follow_user_id in userCircle["following"]

    print(isAlreadyFollowedUser)
    if isAlreadyFollowedUser:
        # already following user then unfollow here
        userCircle["following"].remove(follow_user_id)
        followUserCircle["followers"].remove(userId)
    else:
        # add follow_user_id into following list
        userCircle["following"].append(follow_user_id)
        followUserCircle["followers"].append(userId)

    print(userCircle)
    print(follow_user_id)

    # update following
    result = await userCircleCollection.update_one(
        {"userId": userId},  # Filter to match the document
        {"$set": {"following": userCircle["following"]}}  # Update operation
    )

    if result is None:
        return {
            "success": False,
            "msg": "Something went wrong."
        }

    # once following updation is done successfully then
    # update followers list of follow user cricle
    await userCircleCollection.update_one(
        {"userId": follow_user_id},  # Filter to match the document
        # Update operation
        {"$set": {"followers": followUserCircle["followers"]}}
    )

    print(result)
    return {
        "success": True,
        "msg": "You are now following this user."
    }

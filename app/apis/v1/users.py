
from fastapi import HTTPException, status
from fastapi import APIRouter, Request
from app.db.mongo_conn import userCollection, userCircleCollection
from bson import ObjectId

from app.utils.utils import get_current_user, verify_token
router = APIRouter()

# follow user api


@router.get("/follow/{follow_user_id}")
async def follow_user(follow_user_id: str, request: Request):
    # fetch userId from jwt
    token_data = get_current_user(request)

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

    msg = ""

    print(isAlreadyFollowedUser)
    if isAlreadyFollowedUser:
        # already following user then unfollow here
        userCircle["following"].remove(follow_user_id)
        followUserCircle["followers"].remove(userId)
        msg = "You are unfollowed this user."
    else:
        # add follow_user_id into following list
        userCircle["following"].append(follow_user_id)
        followUserCircle["followers"].append(userId)
        msg = "You are now following this user."

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
        "msg": msg
    }


# GET followers/following users
@router.get("/user-circle/{circle_type}")
async def follow_user(circle_type: str, request: Request):
    if circle_type not in ["followers", "following"]:
        return {
            "success": False,
            "msg": "Incorrect circle type."
        }

    # fetch userId from jwt
    token_data = get_current_user(request)

    if token_data is None:
        return {
            "success": False,
            "msg": "Token is invalid or expired."
        }

    userId = token_data.userId

    userCircle = await userCircleCollection.find_one({"userId": userId})

    results = []
    if (circle_type == "followers"):
        followers = userCircle["followers"]
        for uId in followers:
            user = await userCollection.find_one({"_id": ObjectId(uId)})
            data = {
                "id": uId,
                "name": user["name"],
                "gender": user["gender"],
                "avatarURL": user["avatarURL"]
            }
            results.append(data)
    else:
        following = userCircle["following"]
        for uId in following:
            user = await userCollection.find_one({"_id": ObjectId(uId)})
            data = {
                "id": uId,
                "name": user["name"],
                "gender": user["gender"],
                "avatarURL": user["avatarURL"]
            }
            results.append(data)

    return {
        "success": True,
        "data": results
    }

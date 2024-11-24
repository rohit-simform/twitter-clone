# app/api/api_v1/endpoints/tweets.py
from fastapi import APIRouter, Request, HTTPException, status, BackgroundTasks

from app.models.tweet import NewTweetPayload, Post, PostUser, TweetFeedPayload
from app.models.user import UserCircle
from app.utils.async_process import add_users_timeline
from app.utils.utils import get_current_user, verify_token
from bson import ObjectId
from datetime import datetime

from app.db.mongo_conn import userCollection, postCollection, postUserCollection, userCircleCollection


router = APIRouter()


@router.post("/")
async def get_tweets(tweet_feed_payload: TweetFeedPayload, request: Request):
    # fetch userId from jwt

    token_data = get_current_user(request)

    if token_data is None:
        return {
            "success": False,
            "msg": "Token is invalid or expired."
        }

    userId = token_data.userId

    searchUserFeed = None
    fromDate = None

    if tweet_feed_payload is not None:
        if tweet_feed_payload.searchUserFeed is not None:
            searchUserFeed = tweet_feed_payload.searchUserFeed

        if tweet_feed_payload.fromDate is not None:
            fromDate = tweet_feed_payload.fromDate

    filteredUsers = [userId]  # search feeds of list of filtered users
    results = []

    # if search by user
    if searchUserFeed is not None:
        # list feeds of specific user
        filteredUsers = [searchUserFeed]
    else:
        # list feeds of all following users including you.
        user_circle = await userCircleCollection.find_one({"userId": userId})
        following_userIds = user_circle["following"]
        filteredUsers.extend(following_userIds)

    print(filteredUsers)

    startDateFrom = fromDate

    if startDateFrom is None:
        startDateFrom = datetime.utcnow()

    # Perform the aggregation
    pipeline = [
        # match userId of filteredUsers along with updatedAt (less than startDateFrom)
        {"$match": {"userId": {"$in": filteredUsers},
                    "updatedAt": {"$lte": startDateFrom}}},
        {"$sort": {"updatedAt": 1}},  # Sort by date ascending
        {"$limit": 10}  # Limit to 10 records
    ]

    # fetch tweets or filter tweets
    async for document in postUserCollection.aggregate(pipeline):
        results.append(document)

    print(results)

    if not results:
        return {
            "success": True,
            "is_last_post": True,
            "results": []
        }

    metaData = []
    for pu in results:
        post_user_info = await userCollection.find_one(
            {"_id": ObjectId(pu["userId"])})
        print(post_user_info)
        post_info = await postCollection.find_one({"_id": ObjectId(pu["postId"])})
        print(post_info)

        data = {
            "postId": pu["postId"],
            "description": post_info["description"],
            "imageURL": post_info["imageURL"],
            "owner": post_user_info["name"],
            "avatarURL": post_user_info["avatarURL"],
            "userId": pu["userId"],
            "createdAt": post_info["createdAt"],
            "updatedAt": post_info["updatedAt"]
        }

        metaData.append(data)

    return {
        "success": True,
        "results": metaData
    }


# # Fetch Posts timeline
# @router.post("/feed")
# async def tweets_feed(tweet_feed_payload: TweetFeedPayload, request: Request):
#     # fetch userId from jwt

#     token_data = get_current_user(request)

#     if token_data is None:
#         return {
#             "success": False,
#             "msg": "Token is invalid or expired."
#         }

#     userId = token_data.userId

#     searchUserFeed = None
#     fromDate = None


# Post a new Tweet
@router.post("/create")
async def post_tweet(tweet_payload: NewTweetPayload, request: Request, background_tasks: BackgroundTasks):
    # fetch userId from jwt
    token_data = get_current_user(request)

    if token_data is None:
        return {
            "success": False,
            "msg": "Token is invalid or expired."
        }

    userId = token_data.userId

    new_tweet = Post(
        description=tweet_payload.description,
        imageURL=tweet_payload.imageURL
    )

    result = await postCollection.insert_one(new_tweet.dict())
    print(result)

    if result is None:
        return {
            "success": False,
            "msg": "Unable to create a new tweet."
        }

    # Entries on postUser collection
    new_post_user = PostUser(
        postId=str(result.inserted_id),
        userId=userId
    )

    post_user_result = await postUserCollection.insert_one(new_post_user.dict())
    post_user_id = str(post_user_result.inserted_id)
    print(post_user_id)
    # add post into your followers time line
    # Adding the background task
    background_tasks.add_task(
        add_users_timeline, userId, post_user_id)

    response = {
        "success": True,
        "msg": "Tweet has been created successfully."
    }

    return response

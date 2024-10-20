# app/api/api_v1/endpoints/tweets.py
from fastapi import APIRouter, Request, HTTPException, status

from app.models.tweet import NewTweetPayload, Post, PostUser, TweetFeedPayload
from app.models.user import UserCircle
from app.utils.utils import verify_token
from bson import ObjectId


from app.db.mongo_conn import userCollection, postCollection, postUserCollection, userCircleCollection


router = APIRouter()


@router.post("/")
async def get_tweets(tweet_feed_payload: TweetFeedPayload, request: Request):
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

    searchUserFeed = None
    fromDate = None

    if tweet_feed_payload is not None:
        if tweet_feed_payload.searchUserFeed is not None:
            searchUserFeed = tweet_feed_payload.searchUserFeed

        if tweet_feed_payload.fromDate is not None:
            fromDate = tweet_feed_payload.fromDate

    filteredUsers = [userId]
    results = []

    # if search by user
    if searchUserFeed is not None:
        filteredUsers = [searchUserFeed]
    else:
        user_circle = await userCircleCollection.find_one({"userId": userId})
        following_userIds = user_circle["following"]
        filteredUsers.extend(following_userIds)

    print(filteredUsers)

    # fetch tweets or filter tweets
    if fromDate:
        # Find documents where userId is in the filteredUsers list
        async for document in postUserCollection.find({"userId": {"$in": filteredUsers}, "updatedAt": {"$lte": fromDate}}):
            results.append(document)

    else:
        # Find documents where userId is in the filteredUsers list along with from date
        async for document in postUserCollection.find({"userId": {"$in": filteredUsers}}):
            results.append(document)

    print(results)

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
            "userId": pu["userId"]
        }

        metaData.append(data)

    return {
        "success": True,
        "results": metaData
    }


# Post a new Tweet
@router.post("/create")
async def post_tweet(tweet_payload: NewTweetPayload, request: Request):
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

    await postUserCollection.insert_one(new_post_user.dict())

    response = {
        "success": True,
        "msg": "Tweet has been created successfully."
    }

    return response

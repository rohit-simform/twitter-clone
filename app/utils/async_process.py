from app.db.mongo_conn import timelineCollection, userCircleCollection
from app.models.tweet import Timeline


async def add_users_timeline(userId, postUserId):
    # Timeline Cache DB --> insert post all followers users timeline (asynchronousaly)
    # step-1 --> Retrieve all followers list
    print(userId, postUserId)
    userCircle = await userCircleCollection.find_one({"userId": userId})
    followers = userCircle["followers"]

    for follower in followers:
        user = await timelineCollection.find_one({"userId": follower})
        if user is not None:
            postUserIds = user["postUserIds"]
            postUserIds.append(postUserId)
            await timelineCollection.update_one({"userId": follower},  # Filter to match the document
                                                # Update operation
                                                {"$set": {"postUserIds": postUserIds}}
                                                )
        else:
            newUserTimeline = Timeline(
                userId=follower,
                postUserIds=[postUserId]
            )

            await timelineCollection.insert_one(newUserTimeline.dict())

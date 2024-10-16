# app/api/api_v1/endpoints/users.py
from fastapi import APIRouter

from app.models.auth import LoginPayload, SignupPayload, User
from app.utils.utils import hash_password, verify_password
from app.db.mongo_conn import userCollection

router = APIRouter()

# =====================Auth API=========================================


@router.post("/signup")
async def create_user(user: SignupPayload):
    result = await userCollection.find_one(
        {"email": user.email})
    if result is not None:
        return {
            "success": False,
            "msg": "User already exists."
        }

    hasedPassword = hash_password(user.password)
    newUser = User(
        name=user.name,
        email=user.email,
        password=hasedPassword,
        gender=user.gender,
        age=user.age
    )

    result = userCollection.insert_one(newUser.dict())
    print(result)

    if result is None:
        return {
            "success": False,
            "msg": "User is not registered."
        }

    response = {
        "success": True,
        "msg": "You are successfully registered."
    }

    return response


@router.post("/login")
async def create_user(user: LoginPayload):
    result = await userCollection.find_one(
        {"email": user.email})
    if result is None:
        return {
            "success": False,
            "msg": "Incorrect credentials"
        }

    print(result)
    isPasswordMatched = verify_password(result['password'], user.password)

    if isPasswordMatched is False:
        return {
            "success": False,
            "msg": "Incorrect credentials"
        }

    user = {
        "userId": str(result['_id']),
        "name": result["name"],
        "email": result["email"],
        "gender": result["gender"],
        "age": result["age"],
        "avatarURL": result["avatarURL"]
    }

    response = {
        "success": True,
        "data": user
    }
    return response

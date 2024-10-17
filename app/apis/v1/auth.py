# app/api/api_v1/endpoints/users.py
from fastapi import HTTPException, status
from fastapi import APIRouter

from app.models.auth import LoginPayload, SignupPayload, User, Token
from app.models.user import UserCircle
from app.utils.utils import create_token, hash_password, verify_password, verify_token
from app.db.mongo_conn import userCollection, userCircleCollection

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

    result = await userCollection.insert_one(newUser.dict())
    print(result)

    if result is None:
        return {
            "success": False,
            "msg": "User is not registered."
        }

    # Entries on userCircle collection
    newUserCircle = UserCircle(
        userId=str(result.inserted_id)
    )

    await userCircleCollection.insert_one(newUserCircle.dict())

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

    token_data = {
        "userId": str(result['_id']),
        "email": result["email"]
    }
    # create access token
    access_token = create_token(token_data, 24 * 60)
    refresh_token = create_token(token_data, None)
    user = {
        "userId": str(result['_id']),
        "name": result["name"],
        "email": result["email"],
        "gender": result["gender"],
        "age": result["age"],
        "avatarURL": result["avatarURL"],
        "accessToken": access_token,
        "refreshToken": refresh_token
    }

    response = {
        "success": True,
        "data": user
    }
    return response


# Refresh token
@router.post("/refresh-token")
async def refresh_token(refToken: Token):
    if refToken.token is None:
        return {
            "success": False,
            "msg": "Token is missing."
        }

    # HTTPException Error response format
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(refToken.token, credentials_exception)

    if token_data is None:
        return {
            "success": False,
            "msg": "Token is invalid or expired."
        }
    # create new fresh tokens
    new_token_data = {
        "userId": token_data.userId,
        "email": token_data.email
    }
    access_token = create_token(new_token_data, 24 * 60)
    refresh_token = create_token(new_token_data, None)

    return {
        "success": True,
        "accessToken": access_token,
        "refreshToken": refresh_token
    }

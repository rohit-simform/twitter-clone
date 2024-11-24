import bcrypt
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from app.models.auth import TokenData
from jose import JWTError, jwt
from const.errors import unauthorized_exception


def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password


def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())


# =============== JWT functions =====================


SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # for 7 Days


def create_token(data: dict, token_expiry_minutes):
    to_encode = data.copy()
    expire = datetime.utcnow() + \
        timedelta(minutes=token_expiry_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if user is None:
            raise credentials_exception
        token_data = TokenData(email=user["email"], userId=user["userId"])
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(request: Request):
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        raise unauthorized_exception
    token = authorization.split(" ")[1]
    return verify_token(token, unauthorized_exception)

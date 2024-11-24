from fastapi import HTTPException, status

unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authorization header missing",
    headers={"WWW-Authenticate": "Bearer"},
)

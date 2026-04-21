from shared.db_manager import get_user
from API.core.security import verify_password, create_access_token
from fastapi import HTTPException, status

def login(username: str, password: str) -> dict:
    user = get_user(username)
    
    if user is None or not verify_password(password, user["Password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forkert brugernavn eller password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token({"sub": user["Username"]})
    return {"access_token": token, "token_type": "bearer"}
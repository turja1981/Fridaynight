from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError
from modules.rbac import authenticate_user, create_access_token, verify_token

router = APIRouter(tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
async def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer", "role": user.role.value, "username": user.username}


@router.post("/auth/me")
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(_bearer)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        token_data = verify_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": token_data.username, "role": token_data.role.value}

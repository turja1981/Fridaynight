from __future__ import annotations
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from modules.rbac import authenticate_user, create_access_token
from modules.logging_obs.exceptions import AuthException

router = APIRouter(tags=["auth"])

@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise AuthException("Invalid username or password")
    token = create_access_token({"sub": user.username, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer", "role": user.role.value, "username": user.username}

@router.post("/auth/me")
async def get_me():
    return {"status": "ok"}

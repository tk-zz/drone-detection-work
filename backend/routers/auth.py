from fastapi import APIRouter, Depends, Header

from backend.core.dependencies import get_current_user
from backend.schemas.user import ChangePasswordRequest, LoginRequest
from backend.services.user_service import (
    authenticate_user,
    change_password,
    create_session,
    get_user_by_id,
    logout_session,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    token, expires_at = create_session(user["id"])
    return {
        "token": token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
        "user": get_user_by_id(user["id"]),
    }


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {"user": get_user_by_id(current_user["id"])}


@router.post("/change-password")
def change_password_api(payload: ChangePasswordRequest, current_user=Depends(get_current_user)):
    return change_password(current_user["id"], payload.current_password, payload.new_password)


@router.post("/logout")
def logout(authorization: str = Header(default="")):
    if authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        logout_session(token)
    return {"message": "已退出登录"}

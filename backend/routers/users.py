from fastapi import APIRouter, Depends

from backend.core.constants import ROLE_NORMAL
from backend.core.dependencies import require_admin
from backend.schemas.user import CreateUserRequest, RegisterRequest, UpdateUserRequest
from backend.services.user_service import create_user, delete_user, list_users, update_user

router = APIRouter(tags=["users"])


@router.post("/register")
def register(payload: RegisterRequest):
    user = create_user(payload.username, payload.password, ROLE_NORMAL)
    return {"user": user}


@router.get("/users")
def get_users(current_user=Depends(require_admin)):
    return {"users": list_users()}


@router.post("/users")
def create_user_api(payload: CreateUserRequest, current_user=Depends(require_admin)):
    user = create_user(payload.username, payload.password, payload.role)
    return {"user": user}


@router.patch("/users/{user_id}")
def update_user_api(user_id: int, payload: UpdateUserRequest, current_user=Depends(require_admin)):
    user = update_user(
        user_id,
        {
            "password": payload.password,
            "role": payload.role,
            "status": payload.status,
        },
        current_user["id"],
    )
    return {"user": user}


@router.delete("/users/{user_id}")
def delete_user_api(user_id: int, current_user=Depends(require_admin)):
    delete_user(user_id, current_user["id"])
    return {"message": "用户已删除"}

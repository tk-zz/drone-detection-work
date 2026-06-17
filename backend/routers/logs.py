from fastapi import APIRouter, Depends

from backend.core.dependencies import get_current_user
from backend.services.log_service import list_detection_logs

router = APIRouter(tags=["logs"])


@router.get("/logs")
@router.get("/detection-logs")
@router.get("/detection_logs")
def get_logs(current_user=Depends(get_current_user)):
    return {"logs": list_detection_logs(current_user)}

from fastapi import APIRouter
from models.auth import LoginRequest, TokenResponse
from controllers.auth_controller import login

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login_route(request: LoginRequest):
    return login(request.username, request.password)
"""
Main API router that includes all endpoint routers
"""
from fastapi import APIRouter  # type: ignore

from .endpoints import auth, learning, questions, practice

# Create the main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    learning.router,
    prefix="/learning",
    tags=["learning"]
)

api_router.include_router(
    questions.router,
    prefix="/questions",
    tags=["questions"]
)

api_router.include_router(
    practice.router,
    prefix="/practice",
    tags=["practice"]
)

# Additional routers will be added here as they are implemented
# Example:
# api_router.include_router(
#     users.router,
#     prefix="/users",
#     tags=["users"]
# )
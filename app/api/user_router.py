"""
This module contains all the required http endpoints for user management
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi import status
from app.services.user.user_service import UserService
from app.schemas.schemas import UserSetup


user_router = APIRouter()


@user_router.post("/user")
def register_user(user: UserSetup, user_service: UserService = Depends()):
    """
    This endpoint creates the local user onto the database

    :param user: Description
    :type user: UserSetup
    :param user_service: Description
    :type user_service: UserService
    """
    user_service.register_user(user)
    return {"success": True, "message": "User created successfully"}


@user_router.put("/user")
def update_user(user: UserSetup, user_service: UserService = Depends()):
    """
    This endpoint updates the local user

    :param user: Description
    :type user: UserSetup
    :param user_service: Description
    :type user_service: UserService
    """
    user_service.update_user_info(user)
    return {"success": True, "message": "User updated successfully"}


@user_router.get("/user")
def get_user(user_service: UserService = Depends()):
    """
    This endpoint gest all the user data

    :param user_service: Description
    :type user_service: UserService
    """
    data = user_service.get_user_data()
    return {"success": True, "data": data}


@user_router.get("/user/verifyRegistered")
def verify_registered_user(user_service: UserService = Depends()):
    """
    This endpoint verifies if theres already a user on the local database

    :param user_service: Description
    :type user_service: UserService
    """
    if user_service.is_user_regitered():
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "User is already registered"}
        )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"success": False, "message": "There's no any user on database"}
    )


@user_router.get("/user/getInstalledModels")
def get_installed_models(user_service: UserService = Depends()):
    """
    This endpoint returns all available ollama local models

    :param user_service: Description
    :type user_service: UserService
    """
    if user_service.is_ollama_installed():
        available_models = user_service.retrieve_ollama_models_list()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"succes": True, "message": available_models}
        )
    return JSONResponse(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        content={"succes": False,
                 "message": "You don't have ollama installed on your machine"}
    )

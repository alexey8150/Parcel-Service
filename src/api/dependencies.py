from typing import Annotated
from uuid import uuid4
from fastapi import Request, Response, Depends
from src.services.package import PackageService

package_services = Annotated[PackageService, Depends(lambda: PackageService())]


def get_or_create_user_uuid(request: Request, response: Response) -> str:
    user_uuid = request.cookies.get("user_uuid")
    if not user_uuid:
        user_uuid = str(uuid4())
        response.set_cookie(key="user_uuid", value=user_uuid, httponly=True)
    return user_uuid


uuid = Depends(get_or_create_user_uuid)

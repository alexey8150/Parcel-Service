from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.schemas.delivery import DeliveryCompanySchema
from src.schemas.package import PackageCreateSchema, PackagePaginationResponse
from src.schemas.package import PackageReadSchema
from src.utils.common import cache_response
from .dependencies import package_services, uuid

package_router = APIRouter(prefix='/package', tags=['Package'])


@package_router.post('')
async def add_package(package_data: PackageCreateSchema,
                      package_service: package_services,
                      user_uuid: str = uuid):
    package_id = await package_service.add_package(package_data.model_dump(), user_uuid)
    return JSONResponse(status_code=201, content={'package_id': package_id})


@package_router.get('', response_model=list[PackageReadSchema])
@cache_response(ttl=30, namespace='package')
async def get_all_packages(package_service: package_services):
    packages = await package_service.get_all_packages()
    if not packages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Packages not found"}],
        )
    return packages


@package_router.get('/my-packages',
                    response_model=PackagePaginationResponse,
                    description="Returns a list of packages for the specified user with optional filtering and pagination.")
async def get_user_packages(package_service: package_services, offset: int = 0, count: int = 10,
                            package_type: Optional[str] = Query(None, description="Package type",
                                                                pattern="^(clothes|electronics|other)$"),
                            is_calculated: Optional[bool] = Query(None, description="Is shipping calculated"),
                            user_uuid: str = uuid):
    packages = await package_service.get_user_packages(user_uuid, package_type, is_calculated, offset, count)

    if not packages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Packages with this parameters not found"}],
        )

    return PackagePaginationResponse(
        packages=packages,
        offset=offset,
        count=count
    )


@package_router.post('/{package_id}/bind-delivery')
async def bind_delivery_company(package_id: int, delivery_data: DeliveryCompanySchema,
                                package_service: package_services):
    is_tied = await package_service.bind_delivery_company(package_id, delivery_data.model_dump())

    if is_tied:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": "This package already has delivery company"}],
        )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"msg": 'Successful tied'})


@package_router.get('/{package_id}', response_model=PackageReadSchema)
@cache_response(ttl=30, namespace='package')
async def get_one_package(package_id: int, package_service: package_services):
    package = await package_service.get_one_package(package_id)
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Packages with this id not found"}],
        )
    return package

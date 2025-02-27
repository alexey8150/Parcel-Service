from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Literal
from .package_type import PackageTypeSchema


class PackageCreateSchema(BaseModel):
    name: str
    weight: float = Field(..., title="Вес в граммах", description="Вес в граммах. Укажите значение в граммах.", gt=100)
    content_price: float = Field(..., title="Цена в долларах США(USD)",
                                 description="Укажите цену содержимого в долларах США(USD).")
    type: Literal['clothes', 'electronics', 'other']

    model_config = ConfigDict(from_attributes=True)


class PackageReadSchema(BaseModel):
    id: int
    name: str
    weight: float
    content_price: float
    shipping_price: float | str = Field(..., title="Цена доставки в Российских рублях(RUB)",
                                        description="Цена доставки в Российских рублях(RUB).")
    type: PackageTypeSchema

    model_config = ConfigDict(from_attributes=True)

    @field_validator("shipping_price", mode="before")
    def normalize_email(cls, value: str) -> str:
        return 'Not calculated' if value is None else value


class PackagePaginationResponse(BaseModel):
    packages: list[PackageReadSchema]
    offset: int
    count: int

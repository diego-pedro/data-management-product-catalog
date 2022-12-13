from typing import List, Union

from pydantic import BaseModel


class NewProductInput(BaseModel):
    name: str
    category: str
    sub_category: str
    count: int
    value: float

    class Config:
        """Enable object relational mapping"""
        orm_mode = True


class PaginatedProductListOutput(BaseModel):
    current_page: int
    page_size: int
    page_count: int
    total: int
    products: List


class ProductView(BaseModel):
    service_uuid: str
    product_uuid: str
    product_name: str
    product_category: str
    product_count: int


class ProductUpdateInput(BaseModel):
    field_name: str
    value: Union[str, int]

"""Product management implementation."""

import pydantic
import uuid
from fastapi import APIRouter, Query, status, Depends
from fastapi_jwt_auth import AuthJWT
from datetime import datetime
from bson.objectid import ObjectId
from math import ceil
from typing import List
from db.mongodb import data_db
from schemas.product import PaginatedProductListOutput, ProductView, ProductUpdateInput, NewProductInput
from utility.api_response import http_exception
from utility.search_motor import MongoDBQuery
from prettyconf import config

product_service_uuid = config("PRODUCT_SERVICE_UUID")

# Fix ObjectId & FastApi conflict
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

router = APIRouter(tags=["Products"])


@router.get("/products",
            response_model=PaginatedProductListOutput)
async def get_products(
        page: int = Query(1, title="Page",
                          description="The requested page"),
        page_size: int = Query(100, title="Page size",
                               description="The max quantity of records to be"
                                           " returned in a single page"),
        filters: List[str] = Query(
            default=None),
        sorts: List[str] = Query(None),
        search: str = Query(
            "/*",
            description="Specify a string to search for."
        ),
        jwt_token: AuthJWT = Depends(),
):
    """Get filtered and sorted products.
    """
    jwt_token.jwt_required()

    # Segregate time-related filters from the rest
    time_range_filters = ["start_date", "end_date"]
    time_filters = {}

    if filters:
        for _filter in filters:
            if _filter.split("=")[0] in time_range_filters:

                # Validate if filter field is already listed
                # or multiple dates are given for the same parameter
                if len(_filter.split("=")[1].split(',')) > 1 \
                        or time_filters.get(_filter.split("=")[0]):
                    raise http_exception("Invalid Filter",
                                         status.HTTP_400_BAD_REQUEST)

                else:
                    time_filters[_filter.split("=")[0]] = _filter.split("=")[1]

    query_sorts = []
    if sorts:
        for sort in sorts:
            try:
                if sort.split(":")[1] in ["desc", "DESC"]:
                    query_sorts.append((f'content.{sort.split(":")[0]}', -1))
                elif sort.split(":")[1] in ["asc", "ASC"]:
                    query_sorts.append((f'content.{sort.split(":")[0]}', 1))
            except IndexError:
                # If ASC or DESC is not specified, apply ASC
                query_sorts.append((f'content.{sort}', 1))

    query_manager = MongoDBQuery(
        collection=data_db["products"],
        search_string=search,
        sorting_fields=query_sorts,
        time_range=time_filters)

    results = await query_manager.query()

    total_records = len(results)

    query_items = {
        "current_page": page,
        "page_size": page_size,
        "page_count": ceil(total_records / page_size),
        "total": total_records,
        "products": [result["content"]
                     for result in results]
    }

    return query_items


@router.post("/product")
async def post_new_product(new_product: NewProductInput):
    timestamp = datetime.now()
    product_uuid = str(uuid.uuid4())

    new_product_document = {
        "content": {
            "service_uuid": product_service_uuid,
            "product_uuid": product_uuid,
            "timestamp": timestamp,
            "active": True,
            "product_category": new_product.category,
            "product_sub_category": new_product.sub_category,
            "product_name": new_product.name,
            "product_count": new_product.count,
            "product_value": new_product.value
        }
    }

    await data_db.products.insert_one(new_product_document)

    users = await data_db.users.find().to_list(100)

    relevant_users = [user for user in users if new_product.category in user["preferences"]["category_list"]]

    for user in relevant_users:
        new_message_document = {
            "content": {
                "service_uuid": product_service_uuid,
                "message_uuid": str(uuid.uuid4()),
                "username": user["auth"]["username"],
                "timestamp": timestamp,
                "active": True,
                "detail": f'{new_product.count} new product(s) {new_product.name} of {new_product.category}'
            }
        }

        await data_db.messages.insert_one(new_message_document)

    return {"product_uuid": product_uuid}


@router.get("/product/{product_uuid}",
            response_model=ProductView)
async def get_product(product_uuid: str):
    product = await data_db.products.find_one(
        {"content.product_uuid": product_uuid,
         "content.active": True}
    )

    return product["content"]


@router.put("/product/{product_uuid}")
async def update_product(
        product_uuid: str,
        update_payload: ProductUpdateInput
):

    try:
        update_payload.value = int(update_payload.value)
    except TypeError:
        pass

    await data_db.products.update_one(
        {"content.product_uuid": product_uuid,
         "content.active": True
         },
        {
            "$set": {f"content.{update_payload.field_name}": update_payload.value}
        }
    )

    return {"detail": "Product Updated"}

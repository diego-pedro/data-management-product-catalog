"""Authentication management implementation."""

from fastapi import APIRouter, status, Depends
from fastapi_jwt_auth import AuthJWT
import pydantic
from bson.objectid import ObjectId
from schemas.authentication import Authentication
from schemas.user_profile import UserProfileCategoryInput, UserProfileInput, UserAddressInput
from db.mongodb import data_db
from utility.api_response import http_exception

# Fix ObjectId & FastApi conflict
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

router = APIRouter(tags=["Authentication"])


@router.post("/authenticate")
async def authenticate_user(manage_auth: Authentication,
                            jwt_token: AuthJWT = Depends()):
    user = await data_db.users.find_one(
        {"auth.username": manage_auth.username,
         "auth.password": manage_auth.password}
    )

    if user:
        return {"Authentication": "Success",
                "access_token": jwt_token.create_access_token(subject=manage_auth.username)}
    else:
        raise http_exception(message="Check your credentials.", status=status.HTTP_401_UNAUTHORIZED)


@router.put("/user-profile/category")
async def add_user_favorite(update_info: UserProfileCategoryInput,
                            jwt_token: AuthJWT = Depends()):
    jwt_token.jwt_required()

    user = await data_db.users.find_one({"auth.username": update_info.username})

    user_favorites = user["preferences"]["category_list"]

    new_category = update_info.category

    if new_category not in user_favorites:
        user_favorites.append(new_category)

    await data_db.users.find_one_and_update(
        {"auth.username": update_info.username},
        {"$set":
             {"preferences.category_list": user_favorites}}
    )

    return user_favorites


@router.delete("/user-profile/category")
async def remove_user_favorite(update_info: UserProfileCategoryInput,
                               jwt_token: AuthJWT = Depends()):
    jwt_token.jwt_required()

    user = await data_db.users.find_one({"auth.username": update_info.username})

    user_favorites = user["preferences"]["category_list"]

    new_category = update_info.category

    if new_category in user_favorites:
        user_favorites.remove(new_category)

    await data_db.users.find_one_and_update(
        {"auth.username": update_info.username},
        {"$set":
             {"preferences.category_list": user_favorites}}
    )

    return user_favorites


@router.put("/user-profile/cart/add/{product_uuid}")
async def add_product_to_cart(product_uuid: str,
                              update_info: UserProfileInput,
                              jwt_token: AuthJWT = Depends()):
    jwt_token.jwt_required()

    user = await data_db.users.find_one({"auth.username": update_info.username})

    user_cart = user["preferences"]["current_cart"]

    product = await data_db.products.find_one({"content.product_uuid": product_uuid})

    if product is not None and product["content"]["product_count"] > 0:
        if not user_cart.get(product["content"]["product_category"]):
            user_cart[product["content"]["product_category"]] = []

        user_cart[product["content"]["product_category"]].append(product)

        await data_db.users.find_one_and_update(
            {"auth.username": update_info.username},
            {"$set":
                 {"preferences.current_cart": user_cart}}
        )
        return {"detail": f'{product["content"]["product_name"]} added to cart.'}

    raise http_exception(message="Product not in stock.", status=status.HTTP_406_NOT_ACCEPTABLE)


@router.delete("/user-profile/cart/remove/{product_uuid}")
async def remove_product_from_cart(product_uuid: str,
                                   update_info: UserProfileInput,
                                   jwt_token: AuthJWT = Depends()):
    jwt_token.jwt_required()

    user = await data_db.users.find_one({"auth.username": update_info.username})

    user_cart = user["preferences"]["current_cart"]

    product = await data_db.products.find_one({"content.product_uuid": product_uuid})

    if product is not None:
        if user_cart.get(product["content"]["product_category"]):
            try:
                user_cart[product["content"]["product_category"]].remove(product)

                if len(user_cart[product["content"]["product_category"]]) == 0:
                    del user_cart[product["content"]["product_category"]]

            except Exception as e:
                return {"detail": "Product is not in the cart.",
                        "error": e}

            await data_db.users.find_one_and_update(
                {"auth.username": update_info.username},
                {"$set":
                     {"preferences.current_cart": user_cart}}
            )
            return {"detail": f'{product["content"]["product_name"]} removed from cart.'}

    return {"detail": "Product is not in the cart."}


@router.post("/user-profile/cart")
async def get_user_cart(update_info: UserProfileInput,
                        jwt_token: AuthJWT = Depends()):
    jwt_token.jwt_required()

    user = await data_db.users.find_one({"auth.username": update_info.username})

    user_cart = user["preferences"]["current_cart"]

    return user_cart


@router.post("/user-profile/cart/checkout/address")
async def validate_user_address(address_info: UserAddressInput,
                                jwt_token: AuthJWT = Depends()):
    jwt_token.jwt_required()

    user = await data_db.users.find_one({"auth.username": address_info.username})

    if address_info.address is not None:
        await data_db.users.find_one_and_update(
            {"auth.username": address_info.username},
            {"$set":
                 {"preferences.address": address_info.address, "validated_address": True},
             }
        )
    else:
        if user["preferences"]["address"] is None:
            await data_db.users.find_one_and_update(
                {"auth.username": address_info.username},
                {"$set":
                     {"preferences.address": address_info.address, "validated_address": False},
                 }
            )

    return {"Authorized"}


@router.post("/user-profile/cart/checkout/payment")
async def validate_user_payment(user_info: UserProfileInput,
                                jwt_token: AuthJWT = Depends()):
    jwt_token.jwt_required()

    user = await data_db.users.find_one({"auth.username": user_info.username})

    if user["preferences"]["payment_settings"] is None or user["preferences"]["payment_settings"] == " ":
        await data_db.users.find_one_and_update(
            {"auth.username": user_info.username},
            {"$set":
                 {"validated_payment": False}}
        )

    else:
        await data_db.users.find_one_and_update(
            {"auth.username": user_info.username},
            {"$set":
                 {"validated_payment": True}}
        )

    return {"Authorized"}


@router.post("/user-profile/cart/checkout/review-order")
async def validate_user_checkout(user_info: UserProfileInput,
                                 jwt_token: AuthJWT = Depends()):
    jwt_token.jwt_required()

    user = await data_db.users.find_one({"auth.username": user_info.username})

    receipt_result = user["validated_payment"] and user["validated_address"]

    return {
            "confirmed_items": user["preferences"]["current_cart"],
            "address": user["preferences"]["address"],
            "payment": user["preferences"]["payment_settings"],
            "receipt": receipt_result
            }

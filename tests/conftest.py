"""Test configuration files."""
from db.mongodb import data_db
from fastapi_jwt_auth import AuthJWT
from schemas.jwt import Settings
import requests

product_catalog = data_db.products
test_product_service_uuid = '08009f3b-1c05-4aa3-9ad9-cb68eed038e3'

management_url = 'http://127.0.0.1:7000'

catalog_url = 'http://127.0.0.1:7002'

test_user = "test@email.com.br"
user_authentication = {
    "username": "test@email.com.br",
    'password': "Test#1234"
}


@AuthJWT.load_config
def get_config():
    return Settings()


jwt_token_handler = AuthJWT()
user_access_token = jwt_token_handler.create_access_token(subject=test_user)


def api_product_insert(category: str,
                       sub_category: str,
                       name: str,
                       initial_count: int,
                       value: float = 1.0):
    payload = {
        "name": name,
        "category": category,
        "sub_category": sub_category,
        "count": initial_count,
        "value": value
    }

    response = requests.post(url=management_url + "/manage/product",
                             json=payload)

    assert response.status_code == 200


def api_clear_test_scenario(username):
    data_db.users.find_one_and_update(
        {"auth.username": username},
        {"$set":
             {"preferences.current_cart": None, "validated_address": False, "validated_payment": False,
              "preferences.address": None, "preferences.payment_settings": None}}
    )


def api_add_favorite_category(username: str,
                              category: str):
    payload = {
        "username": username,
        "category": category
    }

    response = requests.post(url=management_url + "/manage/user-profile/category",
                             json=payload,
                             headers={"Authorization": f"Bearer {user_access_token}"})

    assert response.status_code == 200


def api_get_notification(username: str):
    payload = {
        "username": username,
    }

    response = requests.post(url=catalog_url + "/api/notification",
                             json=payload)

    assert response.status_code == 200


def api_set_payment(username):
    data_db.users.find_one_and_update(
        {"auth.username": username},
        {"$set":
             {"preferences.payment_settings": "pm01"}}
    )


def api_set_no_payment(username):
    data_db.users.find_one_and_update(
        {"auth.username": username},
        {"$set":
             {"preferences.payment_settings": None}}
    )


def api_set_test_cart(username):
    data_db.users.find_one_and_update(
        {"auth.username": username},
        {"$set":
             {"preferences.current_cart": ["product_test"]}}
    )

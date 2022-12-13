from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import parse
from tests.conftest import *
import json


@scenario("../features/user_product_browse.feature", "Remove products from his cart")
def test_cart_product_remove_interaction():
    pass


@given(parse("access to the system with {username} and {password}"), target_fixture="access")
@given("access to the system with <username> and <password>", target_fixture="access")
def test_user_initial_cart(username, password):
    credentials = {
        "username": username,
        'password': password
    }

    response = requests.post(url=catalog_url + "/api/login",
                             json=credentials)

    status = response.status_code

    try:
        invalid_credentials = json.loads(response.content)["detail"]

        if invalid_credentials == "Check your credentials.":
            status = 401

    except KeyError:
        pass

    try:
        jwt = json.loads(response.content)["access_token"]
    except KeyError:
        jwt = None

    return {
        "username": username,
        "access_token": jwt,
        "response_status": status
    }


@when(parse("they search for a {existing} product in his cart"))
@when("they search for a <existing> product in his cart")
def test_user_cart_setup(access, existing):
    if access["response_status"] == 200:

        username = access["username"]
        token = access['access_token']

        product = {
            "name": "product 1",
            "category": "software",
            "sub_category": "security",
            "count": 1,
            "value": 78.99
        }

        response = requests.post(url=management_url + '/manage/product',
                                 json=product)

        product = json.loads(response.content)

        if existing == 'True':
            response = requests.put(url=management_url + '/manage/user-profile/cart/add/' + product["product_uuid"],
                                    json={"username": username},
                                    headers={"Authorization": f"Bearer {token}"})

            access["product_uuid"] = product["product_uuid"]
            access["response_status"] = response.status_code

        else:
            access["product_uuid"] = product["product_uuid"]

    else:
        pass


@then(parse("receives {response_status}"))
@then("receives <response_status>")
def test_remove_product_from_cart(access, response_status):
    if access["response_status"] == 200:
        product_uuid = access["product_uuid"]
        username = access["username"]
        token = access['access_token']

        response = requests.delete(url=management_url + '/manage/user-profile/cart/remove/' + product_uuid,
                                   json={"username": username},
                                   headers={"Authorization": f"Bearer {token}"})

        operation_result = json.loads(response.content)

        if operation_result["detail"] == "Product is not in the cart.":
            response.status_code = 406

        access["response_status"] = response.status_code

    assert access["response_status"] == int(response_status)

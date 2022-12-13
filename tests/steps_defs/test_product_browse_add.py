from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import parse
from tests.conftest import *
import json


@scenario("../features/user_product_browse.feature", "Add products to his cart")
def test_catalog_product_add_interaction():
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


@when(parse("they search for a {existing} product with {stock}"))
@when("they search for a <existing> product with <stock>")
def test_product_selection(access, existing, stock):
    if access["response_status"] == 200:

        product = {
            "name": "product 1",
            "category": "software",
            "sub_category": "security",
            "count": int(stock),
            "value": 89.00
            }

        if existing == 'False':
            product = {
                "name": "product 1",
                "category": "software",
                "sub_category": "security",
                "count": 0,
                "value": 89.00
            }

        response = requests.post(url=management_url + '/manage/product',
                                 json=product)

        product = json.loads(response.content)

        access["response_status"] = response.status_code
        access["product_uuid"] = product["product_uuid"]

    else:
        pass


@then(parse("receives {response_status}"))
@then("receives <response_status>")
def test_add_product_to_cart(access, response_status):
    if access["response_status"] == 200:
        product_uuid = access["product_uuid"]
        username = access["username"]
        token = access['access_token']

        response = requests.put(url=management_url + '/manage/user-profile/cart/add/' + product_uuid,
                                json={"username": username},
                                headers={"Authorization": f"Bearer {token}"})

        access["response_status"] = response.status_code

    assert access["response_status"] == int(response_status)

from pytest_bdd import scenario, given, when, then
from pytest_bdd.parsers import parse
from tests.conftest import *
import json


@scenario("../features/user_cart_checkout.feature", "Checkout user cart")
def test_user_cart_checkout():
    pass


@given(parse("resolve {address}"), target_fixture="resolve")
@given("resolve <address>", target_fixture="resolve")
def test_user_address_confirmation(address):
    api_clear_test_scenario(user_authentication["username"])

    credentials = {
        "username": user_authentication["username"],
        'password': user_authentication["password"]
    }

    response = requests.post(url=catalog_url + "/api/login",
                             json=credentials)

    jwt = json.loads(response.content)["access_token"]

    if address == "None":
        address = None

    requests.post(url=management_url + '/manage/user-profile/cart/checkout/address',
                  json={"username": user_authentication["username"],
                        "address": address},
                  headers={"Authorization": f"Bearer {jwt}"})


@when(parse("resolve payment {p_status}"))
@when("resolve payment <p_status>")
def test_user_payment_settings(p_status):
    credentials = {
        "username": user_authentication["username"],
        'password': user_authentication["password"]
    }

    response = requests.post(url=catalog_url + "/api/login",
                             json=credentials)

    jwt = json.loads(response.content)["access_token"]

    if p_status == "True":
        api_set_payment(user_authentication["username"])
    else:
        api_set_no_payment(user_authentication["username"])

    requests.post(url=management_url + '/manage/user-profile/cart/checkout/payment',
                  json={"username": user_authentication["username"]},
                  headers={"Authorization": f"Bearer {jwt}"})


@then(parse("resolve delivery {receipt}"))
@then("resolve delivery <receipt>")
def test_user_order_review(receipt):
    credentials = {
        "username": user_authentication["username"],
        'password': user_authentication["password"]
    }

    response = requests.post(url=catalog_url + "/api/login",
                             json=credentials)

    jwt = json.loads(response.content)["access_token"]

    response = requests.post(url=management_url + '/manage/user-profile/cart/checkout/review-order',
                             json={"username": user_authentication["username"]},
                             headers={"Authorization": f"Bearer {jwt}"})

    checkout_receipt = json.loads(response.content)
    api_clear_test_scenario(user_authentication["username"])

    assert receipt == str(checkout_receipt["receipt"])

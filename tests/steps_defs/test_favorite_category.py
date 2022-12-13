from pytest_bdd import scenario, given, when, then
from tests.conftest import *


@scenario("../features/user_favorite.feature", "User adds new favorite category")
def test_product_categories():
    pass


@given("the user wants to be notified when new products of a favorite category arrive")
def test_user_check_notifications():
    api_clear_test_scenario()
    response = requests.post(url=catalog_url + "/api/notification",
                             json={"email": test_user})

    user_response = response.json()
    assert user_response == {
        "detail": "Notifications up to date."
    }


@when("the user views a product that belongs to a desired category and add that category to his list")
def test_search_product_selecting_category():
    api_product_insert(category="category 1",
                       sub_category="sub category 1",
                       name="product 1",
                       initial_count=1)

    response = requests.get(url=management_url + '/manage/products?&search=product 1',
                            headers={"Authorization": f"Bearer {user_access_token}"})

    desired_product_list = response.json()

    category = desired_product_list["products"][0]["product_category"]

    payload = {
        "username": test_user,
        "category": category
    }

    response = requests.put(url=management_url + '/manage/user-profile/category',
                            json=payload,
                            headers={"Authorization": f"Bearer {user_access_token}"})

    category_list = response.json()

    assert category_list == [category]


@then("the user is notified when a new product of that category is added")
def test_get_new_product_notification():
    api_product_insert(category="category 1",
                       sub_category="sub category 1",
                       name="product 1",
                       initial_count=1)

    response = requests.post(url=catalog_url + "/api/notification",
                             json={"email": test_user})

    user_response = response.json()
    assert user_response == {
        "Latest Message": "1 new product(s) product 1 of category 1"
    }

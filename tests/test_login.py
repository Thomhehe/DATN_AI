import os

import pytest
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage

test_data = [
    ("phamhongthom249@gmail.com", "Thom24924", "https://teelab.vn/account"),
    ("", "Thom24924", "Please fill out this field."),
    ("phamhongthom@gmail.com", "Thom24", "Thông tin đăng nhập không chính xác.")
]
ids = ["Login-1", "Login-2", "Login-3"]

@pytest.fixture(scope="session")
def page():
    with sync_playwright() as pw:
        user_data_dir = os.path.abspath("./user_data")
        context = pw.chromium.launch_persistent_context(user_data_dir, headless=False, args=["--start-maximized"], no_viewport=True)
        pages = context.pages
        page = pages[0] if pages else context.new_page()
        yield page
        context.close()

@pytest.mark.parametrize("email,password,expected", test_data, ids=ids)
def test_login(page, email, password, expected):
    page.goto("https://teelab.vn/account/login?ReturnUrl=%2Faccount")
    login_page = LoginPage(page)
    login_page.perform_actions(email, password)
    result = login_page.get_result(expected)
    assert expected == result
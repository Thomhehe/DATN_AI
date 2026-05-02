import pytest
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from pages.login_page import LoginPage

# Test data and ids as required
test_data = [
    # Login-1: Successful login -> expect URL change to https://teelab.vn/account
    ("phamhongthom249@gmail.com", "Thom24924", 'Display url "https://teelab.vn/account"'),
    # Login-2: Empty email -> expect browser validation message
    ("", "Thom24924", 'Error message "Please fill out this field."'),
    # Login-3: Wrong email & password -> expect inline error message
    ("phamhongthom@gmail.com", "Thom24", 'Error message "Thông tin đăng nhập không chính xác."'),
]

ids = ["Login-1", "Login-2", "Login-3"]


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


@pytest.mark.parametrize("email,password,expected", test_data, ids=ids)
def test_login_flows(driver, email, password, expected):
    page = LoginPage(driver)

    # Perform actions defined in the page object (navigates and performs steps)
    page.perform_actions(email, password)

    # Get result using the dynamic extraction logic in the page
    result = page.get_result(expected)

    # Parsing Expected in Assertion as required
    expected_texts = re.findall(r'"([^"]*)"', expected)
    if expected_texts:
        assert any(text == result for text in expected_texts), f"Expected one of {expected_texts}, got: {result}"
    else:
        assert result == expected, f"Expected '{expected}', got: '{result}'"
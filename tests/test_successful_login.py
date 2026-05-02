import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from pages.successful_login_page import SuccessfulLoginPage

URL = "https://teelab.vn/account/login?ReturnUrl=%2Faccount"

@pytest.fixture
def driver():
    options = Options()
    # Exactly one argument as required
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

# Test data and ids
test_data = [
    # TC-001 Successful login with valid credentials
    ("phamhongthom249@gmail.com", "Thom24924", "Tài khoản"),
    # TC-002 Attempt login with empty email field
    ("", "Thom24924", "Please fill out this field."),
    # TC-005 Attempt login with valid email, incorrect password
    ("phamhongthom249@gmail.com", "WrongPassword123!", "Thông tin đăng nhập không chính xác."),
    # TC-010 Attempt login with email having leading whitespace
    ("   phamhongthom249@gmail.com", "Thom24924", ""),
    # TC-012 Attempt login with password consisting only of whitespace
    ("phamhongthom249@gmail.com", "     ", ["Thông tin đăng nhập không chính xác.", "Please fill out this field."]),
    # TC-013 Attempt login with email exceeding maximum length (>255 chars)
    ("longemail12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345@gmail.com", "AnyPassword123!", ""),
    # TC-014 Attempt login with password exceeding maximum length (>255 chars)
    ("phamhongthom249@gmail.com", "LongPassword123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456!", "")
]

ids = ["TC-001", "TC-002", "TC-005", "TC-010", "TC-012", "TC-013", "TC-014"]

@pytest.mark.parametrize("email,password,expected", test_data, ids=ids)
def test_login_flow(driver, email, password, expected):
    driver.get(URL)
    page = SuccessfulLoginPage(driver)
    # Perform the actions as per test steps
    page.perform_actions(email, password)
    result = page.get_result(expected)
    # Assertion logic as required: exact match
    if isinstance(expected, list):
        assert any(text == result for text in expected)
    else:
        assert result == expected
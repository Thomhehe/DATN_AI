import pytest
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from pages.successful_login_page import SuccessfulLoginPage

URL = "https://teelab.vn/account/login?ReturnUrl=%2Faccount"

# Test data: list of tuples (email, password, expected)
test_data = [
    # TC-001: successful login -> expect page header "Tài khoản"
    ("phamhongthom249@gmail.com", "Thom24924", '"Tài khoản"'),
    # TC-002: empty email -> browser native message
    ("", "Thom24924", '"Please fill out this field."'),
    # TC-005: valid email, incorrect password -> site error message
    ("phamhongthom249@gmail.com", "WrongPassword123!", '"Thông tin đăng nhập không chính xác."'),
    # TC-010: email with leading whitespace -> either login success or invalid email
    ("   phamhongthom249@gmail.com", "Thom24924", '"Tài khoản" "invalid email format"'),
    # TC-012: password whitespace only -> incorrect login or empty field message
    ("phamhongthom249@gmail.com", "     ", '"Thông tin đăng nhập không chính xác." "Please fill out this field."'),
    # TC-013: email exceeding 255 chars
    ("longemail12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345@gmail.com", "AnyPassword123!", '"email too long" "invalid email"'),
    # TC-014: password exceeding 255 chars
    ("phamhongthom249@gmail.com", "LongPassword123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456!", '"password too long" "invalid password"'),
]

ids = ["TC-001", "TC-002", "TC-005", "TC-010", "TC-012", "TC-013", "TC-014"]

@pytest.fixture
def driver():
    options = Options()
    # EXACTLY one argument as required
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    try:
        driver.quit()
    except Exception:
        pass

@pytest.mark.parametrize("email,password,expected", test_data, ids=ids)
def test_login_flow(driver, email, password, expected):
    driver.get(URL)
    page = SuccessfulLoginPage(driver)
    # perform steps: input email, input password, click login
    page.perform_actions(email, password)
    # get result based on expected description
    result = page.get_result(expected)

    # Parse expected double-quoted strings per strict rule and assert
    expected_texts = re.findall(r'"([^"]*)"', expected or "")
    if expected_texts:
        assert any(text == result for text in expected_texts)
    else:
        assert expected == result
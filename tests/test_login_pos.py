import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pages.login_pos_page import LoginPosPage

URL = "https://app.easypos.vn/login"

test_data = [
    ("demopro", "12345678", "https://app.easypos.vn"),  # Login_Pos-1
    ("", "12345678", "Tên đăng nhập không được bỏ trống"),  # Login_Pos-2 (clear email)
    ("demo", "12345", "Mật khẩu không hợp lệ"),  # Login_Pos-3
]

ids = ["Login_Pos-1", "Login_Pos-2", "Login_Pos-3"]


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Use webdriver-manager Service (no local driver)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    try:
        driver.quit()
    except Exception:
        pass


@pytest.mark.parametrize("email,password,expected", test_data, ids=ids)
def test_login_pos(driver, email, password, expected):
    driver.get(URL)
    page = LoginPosPage(driver)
    page.perform_actions(email, password)
    result = page.get_result(expected)
    assert result == expected
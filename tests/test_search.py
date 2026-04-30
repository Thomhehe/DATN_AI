import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from pages.search_page import SearchPage

URL = "https://teelab.vn/"

# Test data and ids per RULE 1
test_data = [
    ("", "Nhập từ khóa để tìm kiếm"),
    ("TÚI", "Có 16 kết quả tìm kiếm phù hợp"),
    ("dép", "Có 1 kết quả tìm kiếm phù hợp"),
]
ids = ["Search-1", "Search-2", "Search-3"]

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Use webdriver-manager Service (no local driver binary assumption)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

@pytest.mark.parametrize("input_value, expected", test_data, ids=ids)
def test_search(input_value, expected, driver):
    driver.get(URL)
    page = SearchPage(driver)
    page.perform_actions(input_value)
    result = page.get_result(expected)
    assert result == expected
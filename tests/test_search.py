import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from pages.search_page import SearchPage

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
    # Use webdriver-manager Service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    try:
        driver.quit()
    except Exception:
        pass

@pytest.mark.parametrize("keyword,expected", test_data, ids=ids)
def test_search_flow(driver, keyword, expected):
    url = "https://teelab.vn/"
    driver.get(url)
    page = SearchPage(driver)
    page.perform_actions(keyword)
    result = page.get_result(expected)
    assert result == expected
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from pages.search_page import SearchPage

URL = "https://teelab.vn/"

test_data = [
    ("", "Nhập từ khóa để tìm kiếm"),
    ("TÚI", "Có 16 kết quả tìm kiếm phù hợp"),
    ("dép", "Có 1 kết quả tìm kiếm phù hợp"),
]

ids = ["Search-1", "Search-2", "Search-3"]


@pytest.fixture
def driver():
    options = Options()
    # Exactly one argument as required
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


@pytest.mark.parametrize("keyword,expected", test_data, ids=ids)
def test_search(keyword, expected, request, driver):
    # Determine whether this test uses icon click or normal click based on test id
    # test_id = request.node.callspec.id if hasattr(request.node, "callspec") else None
    # If test id corresponds to Search-3, steps specify "Click search" (no 'icon') -> use normal click
    use_icon = True

    driver.get(URL)
    page = SearchPage(driver)
    page.perform_actions(keyword, use_icon=use_icon)
    result = page.get_result(expected)
    assert result == expected
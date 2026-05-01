import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from pages.search_mixishop_page import SearchMixiShopPage

TEST_URL = "https://shop.mixigaming.com/"

test_data = [
    ("", "Please fill out this field."),
    ("ÁO", "CÓ 29 KẾT QUẢ TÌM KIÉM PHÙ HỢP"),
    ("q", "KHÔNG TÌM THẤY BẤT KỲ KẾT QUẢ NÀO VỚI TỪ KHÓA TRÊN."),
]
ids = ["Search_MixiShop-1", "Search_MixiShop-2", "Search_MixiShop-3"]


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield driver
    driver.quit()


@pytest.mark.parametrize("keyword,expected", test_data, ids=ids)
def test_search_mixishop(driver, keyword, expected):
    driver.get(TEST_URL)
    page = SearchMixiShopPage(driver)
    page.perform_actions(keyword)
    result = page.get_result(expected)
    assert result == expected
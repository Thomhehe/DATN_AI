import os
import re

def build_prompt_all(testcases, url):
    content = ""

    for tc in testcases:
        content += f"""
ID: {tc['id']}
Steps:
{tc['steps']}
Expected: "{tc['expected']}"
"""

    return f"""
You are an automation tester.

URL: {url}

TEST CASE:
{content}

====================
GOAL
====================
Generate automation test using Pytest + Selenium (data-driven).

Output EXACTLY 2 files:
###FILE:data_test/data_<feature>.py
###FILE:tests/test_<feature>.py

<feature> = from first test case ID (lowercase, remove [], remove -1)

====================
RULES
====================

1. DATA:
- test_data = [(input1, input2, ..., expected)]

2. STEP PARSING:
- Enter "x" → input value
- Clear → empty input
- Click → click()
- Press Enter → send_keys(Keys.ENTER)
- Open search → click search icon

3. LOCATOR:
- Locator is defined ONLY in first test case
- Reuse locator for all other test cases
- [id=] → By.ID
- [name=] → By.NAME
- [xpath=] → By.XPATH
- [css=] → By.CSS_SELECTOR

4. PAGE:
class Page:
    def __init__(self, driver):
        self.driver = driver

def perform_actions(self, inputs):
    # use index mapping

def get_result(self, expected):
    - ưu tiên lấy text từ *_locator
    - fallback: validationMessage

5. TEST:
@pytest.mark.parametrize("data", test_data)
def test_auto(data):
    driver = webdriver.Chrome()
    driver.get("{url}")
    inputs = data[:-1]
    expected = data[-1]

    page = Page(driver)
    page.perform_actions(inputs)
    actual = page.get_result(expected)

    assert actual.strip() == expected.strip()
    driver.quit()

====================
IMPORTANT
====================
- Do NOT create extra locator
- Do NOT hardcode text
- Output ONLY code
- MUST have exactly 2 files with ###FILE
"""

def save_test(code):
    files = re.findall(r"###FILE:(.+?)\n(.*?)(?=###FILE:|$)", code, re.S)

    if len(files) < 2:
        raise ValueError("Sai format: không đủ 2 file")

    for name, content in files[:2]:
        name = name.strip()
        os.makedirs(os.path.dirname(name), exist_ok=True)

        with open(name, "w", encoding="utf-8") as f:
            f.write(content.strip())
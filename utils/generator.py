import os
import re

def build_prompt_all(testcases, url, framework, feature_name):
    feature_name = re.sub(r'[^a-zA-Z0-9]+', '_', feature_name).lower()

    content = ""
    for tc in testcases:
        content += f"""
ID: {tc['id']}
STEPS:{tc.get('steps', '')}
LOCATOR:{tc.get('locator', '')}
DATA:{tc.get('data', {})}
EXPECTED:{tc.get('expected', '')}
"""

    return f"""
You are a Senior QA Automation Engineer.

URL: {url}
FRAMEWORK: {framework}

TEST CASES:
{content}

1. TASK & OUTPUT
Generate EXACTLY 4 files for Pytest Data-driven POM testing.
DO NOT use markdown blocks, generate extra files, or change filenames.
###FILE:pages/{feature_name}_page.py
###FILE:tests/test_{feature_name}.py
###FILE:data/{feature_name}_data.json
###FILE:pytest.ini

2. FRAMEWORK RULES
If selenium: Use selenium.webdriver, WebDriverWait, expected_conditions, webdriver-manager. Use self.driver. Start maximized.
If playwright: Use playwright.sync_api, page.locator(), sync_playwright. DO NOT use launch_persistent_context. Use standard chromium.launch(). Use self.page. DO NOT mix with Selenium APIs.

3. PAGE & ACTION RULES
- Class: Create ONE Page class with methods: __init__, perform_actions, get_result. NO extra methods or testcase-specific logic.
- Locators: Declare directly in __init__. When extracting locator values from the LOCATOR section (which may be in formats like `key=type=value` or `type=value`, e.g., `qmk=id=btn-forget-password`), you MUST intelligently parse it to extract the correct locator type (e.g., `id`) and actual value (e.g., `btn-forget-password`). DO NOT include the key (e.g., `qmk=`) or raw type string (e.g., `id=`) in the final locator value. If Selenium: MUST import `By` (`from selenium.webdriver.common.by import By`) and define locators using `By.ID`, `By.CSS_SELECTOR`, `By.XPATH`, `By.NAME`, etc. as tuples based on the parsed type and value (e.g., `(By.ID, 'btn-forget-password')`). If Playwright: declare locators as simple strings appropriately. Reuse locators. DO NOT use parse_locator().
- Input: wait visibility -> clear -> send_keys (Selenium) / locator().fill() (Playwright).
- Click: If locator is img/icon/svg, you MUST ONLY use JS click directly, use presence_of_element_located (DO NOT use normal click). Otherwise, use normal click with JS fallback if it fails.
    + For Playwright JS click: wait using locator.wait_for(state="attached"). ensure hidden classes/styles are removed before clicking. use locator.evaluate(...) with DOM click
- Dropdown/Select: If the step implies selecting an option (e.g., "select", "chọn", "dropdown"), use `Select(element).select_by_visible_text(value)` for Selenium (MUST `from selenium.webdriver.support.ui import Select`), or `locator.select_option(label=value)` for Playwright.
- Verify/Check Displayed: If the step implies verifying or checking that an element is displayed/visible (e.g., "Verify", "Check", "xác minh"), you MUST ONLY wait for the element to be visible using an explicit wait (Selenium: WebDriverWait with visibility_of_element_located) or wait_for(state="visible") (Playwright). DO NOT perform any click, input, or return actions for this step.
- perform_actions(data): Reusable, strictly follows test steps. If all test cases have the EXACT same steps, DO NOT separate them; code actions sequentially. If test cases have DIFFERENT steps (e.g., TC-1 requires login but TC-2 does not), you MUST branch the logic based on data availability (e.g., `if data.get("username"):` or `if data.get("search_query"):`) instead of hardcoding test case IDs, while keeping common steps shared and unbranched.

4. VALIDATION RULES (get_result)
- parameter: get_result() only. DO NOT pass base_url or expected.
- Empty Expected / Missing Result Locator: If 'expected' is empty, DO NOT automatically invent or create a new locator to capture the result; assume a matching locator already exists and DO NOT create additional ones. If 'expected' contains data but the result element/locator is empty or missing, you MUST reuse the locator from the immediately preceding action step to extract the result. DO NOT raise exceptions or invent new locators.
- Priority 1 - Result Locator (Text): If there is an element/locator in the LOCATOR section that does not correspond to any action in the STEPS, you MUST use it FIRST to extract the actual result (visible text). Wait for visibility before extracting.
- Priority 2 - Alert ('alert' locator): ONLY generate alert handling logic IF the LOCATOR explicitly mentions 'alert'. Wait, get text, accept (Selenium: alert_is_present; Playwright: page.on('dialog')).
- Priority 3 - Toast/Message ('toast', 'snackbar'): Wait for visibility before extracting text.
- Priority 4 - URL Redirect: IF the LOCATOR explicitly mentions 'url', you MUST generate URL validation logic to capture and return the current URL. DO NOT capture URL before text.
- Priority 5 - HTML5 ('html5' locator): Wait for the input element to be visible and ensure the HTML5 validation message is actively displayed before capturing. Extract its `validationMessage` (Selenium: get_attribute("validationMessage"), Playwright: evaluate("node => node.validationMessage")). Only return if not empty.
- You MUST call `.strip()` on ALL actual results before returning them.
- Compare actual result with expected using EXACT match only.
- Compare visible text line-by-line using exact equality.
- If multiple result locators exist, check ALL visible text locators first and return the first exact match.
- HTML5 validation must always be checked LAST.
- NO contains(), partial match, expected text as locator, or hardcoded text. EXACT match only.

5. TEST & DATA RULES
- Data JSON: Flat structure. DO NOT nest objects. For 'expected' value: if it contains quotes ("" or ''), you MUST extract ONLY the exact text inside the quotes. If there are multiple quoted strings separated by 'or' (e.g., "A" or "B"), extract them as a list of strings ["A", "B"]. If it does NOT contain quotes ("" or ''), you MUST set its value to an empty string ("").
- Paths: MUST load data file STRICTLY using: `data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "{feature_name}_data.json")`. DO NOT use ROOT, pathlib, or any other path structure. NO hardcoded relative paths.
- Test Flow: Open URL -> Init Page -> perform_actions -> result = get_result -> assert.
- Parametrize: MUST set ids=[d["id"] for d in test_data].
- Assert: If string, exact match. If list, assert any match (e.g., any(result.strip() == str(item).strip() for item in expected)).
- Fixture (Function scope): You MUST use the EXACT following fixture structures to ensure consistency:
  If selenium:
    + use pytest fixture with Chrome driver
    + use webdriver-manager with Service (no local driver)
    + Browser must start maximized
  
  If Playwright:
  + use pytest fixture (session)
    + use sync_playwright
    + use chromium.launch(headless=False, args=["--start-maximized"])
    + use browser.new_context(no_viewport=True)
    + create fresh isolated context/page per test
    + use page object
    + fully close browser/context after each test
    
- Reporting: Configure pytest.ini exactly with the following content:
[pytest]
addopts = --alluredir=allure-results
DO NOT create separate report dirs per feature.

6. CONSTRAINTS
- No time.sleep().
- No explanatory comments.
- Code must be concise and maintainable.
"""

def save_test(code):
    files = re.findall(r"###FILE:(.+?)\n(.*?)(?=###FILE:|$)", code, re.S)

    if len(files) < 4:
        raise ValueError("Sai format: không đủ 4 file")

    for name, content in files:
        name = name.strip()
        dir_name = os.path.dirname(name)

        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(name, "w", encoding="utf-8") as f:
            f.write(content.strip())
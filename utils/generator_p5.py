import os
import re

def build_prompt_all(testcases, url, framework, feature_name):
    feature_name = re.sub(r'[^a-zA-Z0-9]+', '_', feature_name).lower()

    content = ""
    for tc in testcases:
        content += f"""
ID: {tc['id']}
PRECONDITION: {tc.get('precondition', '')}
STEPS:{tc.get('steps', '')}
LOCATOR:{tc.get('locator', '')}
DATA:{tc.get('data', {})}
EXPECTED:{tc.get('expected', '')}
"""

    if framework.strip().lower() == "selenium":
        framework_rules = """
- Use selenium.webdriver, WebDriverWait, expected_conditions, webdriver-manager. Use self.driver. Start maximized.
- Locators: MUST import `By` (`from selenium.webdriver.common.by import By`) and define locators using `By.ID`, `By.CSS_SELECTOR`, `By.XPATH`, `By.NAME`, etc. as tuples (e.g., `(By.ID, 'btn')`).
- Action Helpers: To keep code extremely concise, MUST generate `_click(self, locator)` and `_input(self, locator, text)` methods in the Page class.
  + `_input`: wait visibility -> try native `el.click()`, fallback to javascript click if intercepted -> clear -> send_keys. DO NOT use `scrollIntoView`.
  + `_click`: MUST handle lazy-loaded/hidden elements and StaleElementReferenceException. `for attempt in range(2):` 1. `el_present = wait presence_of_element_located` 2. `execute_script("arguments[0].scrollIntoView({block: 'center'});", el_present)` 3. `import time; time.sleep(0.5)` 4. `el = wait element_to_be_clickable` 5. Check `tag = el.tag_name.lower()`. If tag in ("button", "input"), MUST use js click directly (`execute_script("arguments[0].click();", el)`). Otherwise, try native `el.click()` first, and fallback to js click. Catch `StaleElementReferenceException` (MUST import from `selenium.common.exceptions`) to retry.
- Dropdown/Select: use `Select(element).select_by_visible_text(value)` (MUST `from selenium.webdriver.support.ui import Select`).
- Verify/Check Displayed: wait using WebDriverWait with visibility_of_element_located.
- HTML5 Validation: get_attribute("validationMessage").
- Fixture (Function scope): use pytest fixture with Chrome driver, webdriver-manager with Service, browser must start maximized.
"""
    else:
        framework_rules = """
- Use playwright.sync_api, page.locator(), sync_playwright. DO NOT use launch_persistent_context. Use standard chromium.launch(). Use self.page. DO NOT mix with Selenium APIs.
- Locators: declare locators as simple strings appropriately. Reuse locators. DO NOT use parse_locator().
- Input: locator().fill() (Playwright auto-scrolls natively).
- Click/Open: locator().click() (Playwright auto-scrolls natively). If locator is img/icon/svg, wait using locator.wait_for(state="attached"), ensure hidden classes/styles are removed, use locator.evaluate("node => node.click()").
- Dropdown/Select: use `locator.select_option(label=value)`.
- Verify/Check Displayed: wait using wait_for(state="visible").
- HTML5 Validation: evaluate("node => node.validationMessage").
- Fixture (Function scope): use pytest fixture (session) with sync_playwright, chromium.launch(headless=False, args=["--start-maximized"]), create fresh isolated context/page per test using browser.new_context(no_viewport=True), fully close browser/context after each test.
"""

    return f"""
You are a Senior QA Automation Engineer.

URL: {url}
FRAMEWORK: {framework}

TEST CASES:
{content}

1. TASK & OUTPUT
Generate EXACTLY 3 files for Pytest Data-driven POM testing.
DO NOT use markdown blocks, generate extra files, or change filenames.
###FILE:pages/{feature_name}_page.py
###FILE:tests/test_{feature_name}.py
###FILE:data/{feature_name}_data.json

2. FRAMEWORK RULES
{framework_rules.strip()}

3. PAGE & ACTION RULES
- Class: Create ONE Page class with methods: __init__, action methods, get_result. NO extra methods or testcase-specific logic, UNLESS required by PRECONDITION.
- Precondition Handling: ONLY if a test case requires a LOGIN precondition (e.g., 'Login successful', 'Đăng nhập thành công'), find its matching setup case (the Login test case) and:
  1. Extract ONLY the locators required to perform the login action (e.g., username/email, password, login button) from its `LOCATOR:` section to `__init__`. STRICTLY EXCLUDE any notification, alert, or error message locators! DO NOT guess or invent locators for the setup method!
  2. Create a parameterless setup method (e.g., `setup_login(self)`). You MUST use the exact valid credentials provided in the DATA section of the setup case (the Login testcase). DO NOT invent or make up fake data like "valid@example.com", extract the actual data from the setup testcase!
  3. STRICTLY EXCLUDE this setup case from `data.json` and `perform_actions()`.
  4. For test cases requiring it, add `"requires_login": true` in `data.json`.
  5. In test file: `if d.get("requires_login"): page.setup_login()` else `driver.get(url)`.
  6. `perform_actions()` MUST continue from the setup's final state without reloading the page.
  7. DO NOT apply this extraction or generate setup methods/flags for non-login preconditions.
- Locators: Declare directly in __init__. When extracting locator values from the LOCATOR section (e.g., `id=btn-forget-password`), intelligently parse it to extract the correct locator type and actual value. DO NOT include the key or raw type string in the final locator value. **CRITICAL**: If the locator is a `CSS_SELECTOR` and the value provided in the test case looks like a raw class name or a list of classes (e.g., `btn btn-pri` or `custom-logo-link`), you MUST convert it into a valid CSS class selector by adding a leading dot and replacing spaces with dots (e.g., `.btn.btn-pri`, `.custom-logo-link`). Do not leave them as raw strings. Ensure locators for the setup method are also extracted and declared.
- Action Methods: Reusable, strictly follows test steps. If test cases have DIFFERENT sequences of steps, DO NOT combine them blindly using generic `try...except pass`. Instead, use `if data["id"] in [...]` inside the main `perform_actions` method to execute specific steps ONLY for the test cases that require them (e.g., clicking a banner only for TC-012). This ensures no test case executes redundant steps.
- Bulk Input Handling: If a step implies filling remaining fields, automatically check the DATA section and generate corresponding inputs if the key exists in data.

4. VALIDATION RULES (get_result)
- parameter: `get_result(self, expected)` MUST accept `expected`.
- STRICTLY NO DUPLICATED CODE: DO NOT write separate logic for string and list! FIRST normalize: `is_list = isinstance(expected, list); expected_list = expected if is_list else [expected]`. Then write a SINGLE `for exp in expected_list:` loop.
- INSIDE THE LOOP, generate ONLY the validation checks REQUIRED BY THE TEST CASES:
  + URL Check: ONLY generate `if exp.startswith("http"):` check if at least one test case expects a URL.
  + HTML5 Validation: ONLY generate `validationMessage` check if a testcase's LOCATOR explicitly specifies "html5". You MUST ensure it's truly triggered by checking `!el.validity.valid` and `el === document.activeElement`. Then, MUST call `self.driver.execute_script("arguments[0].reportValidity();", el)` to force the browser to visually display the tooltip, then append the message.
  + Explicit Locators: Collect ONLY the validation locators you actually defined in `__init__` into a list and check them (`try...except` independent WebDriverWait). DO NOT reference attributes (like `self.warning` or `self.error`) if you did not explicitly define them in `__init__`.
  + Body Text Fallback: If a test case lacks a specific message locator (and is NOT an html5 case), ONLY generate a check for `body.text` or `//*[contains(text(), f"{{exp}}")]`. DO NOT generate html5 checks here. DO NOT generate this fallback if all test cases have explicit locators.
  + If alert is expected: check alert.
- Append found text to a `results` list.
- AT THE END: return `results` if `is_list` is True, else return `results[0] if results else ""`
- You MUST call `.strip()` on ALL actual string results before returning them.
- NO expected text as locator, or hardcoded text.
5. TEST & DATA RULES
- Data JSON: Flat structure. DO NOT nest objects. For the 'expected' field: 
  + If the expected description contains quotes ('' or ""), extract ALL exact texts inside the quotes.
  + If it ALSO implies a URL redirect, predict the expected URL.
  + Combine BOTH the quoted texts and the expected URL into a single list of strings in the JSON. (e.g. `["Thành công", "Sản phẩm đã được thêm vào giỏ hàng.", "https://laluz.vn/thanh-toan/"]`).
  + If it ONLY has texts, store as a list of texts. If it ONLY has a URL, store as a string URL.
- IMPORTANT FOR DATA EXTRACTION: ONLY use the exact values provided in the DATA section. If a key is provided in the DATA section but has an empty value (e.g., `email: ` or `email:`), keep it empty in the JSON (`"email": ""`). DO NOT extract input values from the test STEPS to override the DATA section. The STEPS are just instructions; the DATA section is the strict source of truth for input values. The data file must ONLY contain data fields for the specific actions that the test case actually performs.
- Paths: MUST load data file STRICTLY using: `data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "{feature_name}_data.json")`. DO NOT use ROOT, pathlib, or any other path structure.
- Test Flow: Init Page -> If `requires_login` is True, call `setup_login()`, ELSE call `driver.get(d.get("url", ...))`. Do NOT call `driver.get()` if `requires_login` is True, as it will reload the page and destroy the session. -> perform_actions -> result = get_result -> assert. The assertion must handle lists: `if isinstance(d["expected"], list): assert any(e in r and r != "" for e, r in zip(d["expected"], result))` else `assert d["expected"] in result or result == d["expected"]`. DO NOT use `if d["id"] == ...` blocks in the test file to branch logic. The test function must be purely data-driven.
- Parametrize: MUST set ids=[d["id"] for d in test_data].
6. CONSTRAINTS
- No time.sleep().
- No explanatory comments.
- Code must be concise and maintainable.
"""

def save_test(code):
    files = re.findall(r"###FILE:(.+?)\n(.*?)(?=###FILE:|$)", code, re.S)

    if len(files) < 3:
        raise ValueError("Sai format: không đủ 3 file")

    for name, content in files:
        name = name.strip()
        dir_name = os.path.dirname(name)

        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(name, "w", encoding="utf-8") as f:
            f.write(content.strip())
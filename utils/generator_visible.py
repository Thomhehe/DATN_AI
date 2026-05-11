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

1. TASK

Generate automation test code using:
- Pytest
- Data-driven testing
- Page Object Model

Generate exactly 4 files only.

2. OUTPUT

###FILE:pages/{feature_name}_page.py
###FILE:tests/test_{feature_name}.py
###FILE:data/{feature_name}_data.json
###FILE:pytest.ini

IMPORTANT:
- Use FEATURE_NAME exactly as provided
- DO NOT change filenames
- DO NOT generate additional files
- DO NOT use markdown code blocks

3. FRAMEWORK RULES

If framework == "selenium":
- Use selenium.webdriver
- Use WebDriverWait and expected_conditions
- Use webdriver-manager
- Use self.driver
- Browser must start maximized

If framework == "playwright":
- Use playwright.sync_api
- Use page.locator()
- Use self.page
- Use sync_playwright
- Use launch_persistent_context(
    user_data_dir,
    args=["--start-maximized"],
    no_viewport=True
    )
- Reuse existing page if available
- DO NOT use Selenium APIs

4. PAGE & ACTION RULES

STRUCTURE:
- Create only ONE Page class
- Methods allowed:
    + __init__
    + perform_actions
    + get_result
    
- get_result() must accept only expected parameter
- DO NOT pass base_url into get_result()

- DO NOT create additional methods
- DO NOT create testcase-specific logic
- DO NOT hardcode flows using testcase IDs
- perform_actions() must be reusable and data-driven

LOCATORS:
- Declare locators directly in __init__
- DO NOT use parse_locator()
- Use locators from test cases if available
- Store reusable locators only

ACTIONS:
- Follow test steps strictly
- Reuse waited elements
- Avoid duplicate find_element calls

INPUT:
If selenium:
- use visibility_of_element_located
- use clear() + send_keys()

If playwright:
- use locator().fill()

CLICK:
- If locator targets img/icon/svg elements:
    + use presence_of_element_located
    + use JavaScript click directly
    + DO NOT use normal click
    + DO NOT use try-except fallback
- Otherwise:
    + use normal click
    + If click fails, use framework-native JavaScript click fallback

5. VALIDATION RULES

- Validate ONLY AFTER all actions are completed
- Store start_url before actions
- Generate a FIXED, universal validation block in get_result() that ALWAYS tries to catch errors in this STRICT order using try-except blocks:
    1. Browser Alert: if present, return its text.
    2. HTML5 Validation: loop through inputted elements, if get_attribute("validationMessage") exists, return it (normalize quotes).
    3. Toast/Snackbar: try to find elements using generic locators like CSS ".toast, .snackbar, [role='alert'], .message". If visible, return its text.
    4. Visible Page Text: If no errors above AND expected value is NOT a URL format, DO NOT use XPath. Instead, search for the text within the body. Iterate through visible elements to find one whose text exactly matches the expected value (text == expected) and return its text. DO NOT extract and return the entire body.text.
    5. URL Redirect: compare current_url with stored start_url. If expected value is a URL format, return current_url.

- Compare actual result with expected using EXACT match only
- Compare visible text line-by-line using exact equality

- DO NOT use:
    + contains()
    + partial match
    + fuzzy match
    + hidden DOM text
    + expected text as locator
    + page_source

If selenium:
    - use alert.text
    - DO NOT use XPath to locate text. Iterate through body elements to find text that exactly matches expected.
    - use get_attribute("validationMessage")

If playwright:
    - use page.get_by_text(expected, exact=True) or exact XPath

6. TEST RULES

FILE PATH:
   - Always build paths from project root using __file__
   - Use os.path.dirname(__file__)
   - Use os.path.abspath and os.path.join
   - DO NOT use hardcoded relative paths
- MUST use pytest.mark.parametrize and ALWAYS set 'ids' parameter to display testcase ID (e.g., ids=[d["id"] for d in test_data])
- Load test data from: data/{feature_name}_data.json
DATA FILE RULES:
- Keep original flat data structure
- DO NOT create nested objects like:
    + actions
    + expected.type
    + expected.value
- DO NOT include 'url' in the generated JSON data file.
- Keep expected as plain string or list
- URL must be opened before page object actions
- Page class must not contain navigation logic

TEST FLOW:
- Open URL before every testcase
- Create page object
- Call perform_actions(data)
- Call get_result(expected)

ASSERT:
If expected is string:
    - assert result.strip() == expected.strip()

If expected is list:
    - Check == từng dữ liệu 1 (ví dụ: assert any(result.strip() == str(item).strip() for item in expected))
    
SELENIUM FIXTURE:
- Use function scope fixture
- Create fresh browser for every testcase
- Quit browser after each testcase
- Use webdriver-manager with Service

PLAYWRIGHT FIXTURE:
- Use function scope fixture
- Create fresh browser/page for every testcase

REPORT:
- Use Allure reporting only
- Configure pytest.ini with `addopts = --alluredir=reports/allure-results` to automatically generate reports.
- DO NOT configure separate report directory per feature.
- DO NOT add code to clean or delete the report directory in fixtures (this causes data loss).
- DO NOT use allure.step()

7. CONSTRAINTS

- No sleep
- Only 4 files
- DO NOT mix Selenium and Playwright APIs
- DO NOT generate explanatory comments
- Generate concise and maintainable code
- DO NOT mix Selenium and Playwright APIs
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
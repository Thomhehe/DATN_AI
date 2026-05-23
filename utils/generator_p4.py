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
- Use Python, Pytest and Selenium WebDriver.
- Use Page Object Model.
- Use WebDriverWait and expected_conditions.
- Use the provided LOCATOR values to identify UI elements when available.
- Convert locator information into Selenium By strategies: By.ID, By.NAME, By.CSS_SELECTOR, or By.XPATH.
- If a locator needed for action or assertion is missing, infer a suitable locator from STEPS, EXPECTED, and common page text.
- Use pytest fixture with Chrome driver, webdriver-manager with Service, browser must start maximized and headless=False.
"""
    else:
        framework_rules = """
- Use Python, Pytest and Playwright.
- Use Page Object Model.
- Use the provided LOCATOR values to identify UI elements when available.
- Convert locator information into Playwright locator strings.
- If a locator needed for action or assertion is missing, infer a suitable locator from STEPS, EXPECTED, and common page text.
- Use pytest fixture with sync_playwright, browser must run headless=False.
"""

    return f"""
You are an Automation Engineer.

Generate automation test scripts from locator-aware structured test cases.

URL: {url}
FRAMEWORK: {framework}

Each test case contains:
- ID
- PRECONDITION
- STEPS
- LOCATOR
- DATA
- EXPECTED

TEST CASES:
{content}

Generate EXACTLY 3 files:
###FILE:pages/{feature_name}_page.py
###FILE:tests/test_{feature_name}.py
###FILE:data/{feature_name}_data.json

Rules:
{framework_rules.strip()}

1. Test Case Mapping
- PRECONDITION: setup before test if needed.
- STEPS: actions to perform.
- LOCATOR: use provided locators to interact with UI elements.
- DATA: input values.
- EXPECTED: expected result for assertion.

2. Locator Rules
- Define provided locators inside the Page class.
- Do not invent locators if a matching locator is provided.
- If multiple locator types are provided, prefer stable locators in this order: id, name, css selector, xpath.
- Use provided locators to retrieve result elements for assertion when possible.
- If no matching locator is provided for the assertion target, infer a reasonable result locator from EXPECTED, page text, breadcrumb, product title, product brand, or message text.
- For search features, successful results may be verified using result title, breadcrumb text, product name, product brand, or visible page text.

3. Page Object Rules
- Create one Page class.
- Create action methods based on test steps.
- Page class MUST include `perform_actions(data)` to execute actions from the test case.
- Page class MUST include `get_result(expected)` to retrieve the actual result for assertion.
- Use waits before interacting with elements.

4. Data & Test Flow Rules
- Store test data in a flat JSON list.
- Load data file using:
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "{feature_name}_data.json")
- Use pytest parametrize with ids=[d["id"] for d in test_data].
- Test flow: open URL -> perform_actions(data) -> get_result(expected) -> assert expected.
- Test function must be data-driven and should not write separate assertion blocks for each test case ID.

Do not use markdown blocks.
Do not generate extra files.
Do not generate explanations.
Keep code concise and maintainable.
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
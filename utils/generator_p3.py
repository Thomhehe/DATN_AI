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
DATA:{tc.get('data', {})}
EXPECTED:{tc.get('expected', '')}
"""

    if framework.strip().lower() == "selenium":
        framework_rules = """
- Use Python, Pytest and Selenium WebDriver.
- Use Page Object Model.
- Use WebDriverWait and expected_conditions.
- Since locators are not provided, infer simple locators from visible labels, input names, placeholders, button text, link text, or common attributes.
- Use simple locator strategies when possible: id, name, css selector, xpath.
- Use pytest fixture with Chrome driver, webdriver-manager with Service.
- Browser must start maximized and headless=False.
"""
    else:
        framework_rules = """
- Use Python, Pytest and Playwright.
- Use Page Object Model.
- Since locators are not provided, infer simple locators from visible labels, input names, placeholders, button text, link text, or common attributes.
- Use pytest fixture with sync_playwright.
- Browser must run headless=False.
"""

    return f"""
You are an Automation Engineer.

Generate automation test scripts from structured test cases.

URL: {url}
FRAMEWORK: {framework}

Each test case contains:
- ID
- PRECONDITION
- STEPS
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
- DATA: input values.
- EXPECTED: expected result for assertion.

2. Page Object Rules
- Create ONE Page class.
- Define inferred locators inside the Page class.
- Create reusable action methods based on test steps.
- Page class MUST include `perform_actions(data)`.
- Page class MUST include `get_result(expected)`.
- Use waits before interacting with elements.
- Use EXPECTED values to verify the result.
- Keep Page methods reusable and concise.

3. Data & Test Flow Rules
- Store test data in a flat JSON list.
- Load data file using:
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "{feature_name}_data.json")
- Use pytest parametrize with:
ids=[d["id"] for d in test_data]
- Test flow:
open URL -> perform_actions(data) -> get_result(expected) -> assert expected
- Test function must be data-driven.
- Do not write separate assertion blocks for each test case ID.

4. Assertion Rules
- Use EXPECTED values for assertions.
- If EXPECTED is a URL, verify current URL.
- If EXPECTED is text, verify visible page text or message text.
- Use simple and reusable assertion logic.
- Do not hardcode expected values as locators.

5. Constraints
- Do not use markdown blocks.
- Do not generate extra files.
- Do not generate explanations.
- Keep code concise and maintainable.
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
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

    return f"""
You are a QA Automation Engineer.

URL: {url}
FRAMEWORK: {framework}

TEST CASES:
{content}

Generate automation test scripts using Page Object Model.
Return files using EXACTLY this format:
###FILE:pages/{feature_name}_page.py
###FILE:tests/test_{feature_name}.py
###FILE:data/{feature_name}_data.json

Do not generate explanations or extra text.
Only return file contents.
DO NOT use markdown code blocks.

Each test case contains:
- ID
- PRECONDITION
- STEPS
- LOCATOR
- DATA
- EXPECTED

Framework Rules:
- If selenium: use selenium webdriver with WebDriverWait and expected_conditions
- If playwright: use playwright.sync_api and page.locator()

Locator Rules:
- Use the LOCATOR section as the primary source for locating elements
- Parse locator type and value correctly
- Support id, name, css, xpath, class
- Reuse locators when possible

Action Rules:
- Input: wait for visibility -> clear then enter text
- Click: if normal click fails, use JavaScript click
- Dropdown: select by visible text
- Verification: wait until visible before reading text

Validation Rules:
- If expected is URL, return current URL
- Otherwise return visible text from result element
- Compare actual and expected result

Constraints:
- No time.sleep()
- Keep code concise and reusable
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
import os
import re

def build_prompt_all(testcases, url, framework, feature_name):
    feature_name = re.sub(r'[^a-zA-Z0-9]+', '_', feature_name).lower()
    
    content = ""
    for tc in testcases:
        content += f"""
ID: {tc['id']}
STEPS:{tc.get('steps', '')}
DATA:{tc.get('data', {})}
EXPECTED:{tc.get('expected', '')}
"""

    if framework.strip().lower() == "selenium":
        framework_rules = """
- Use Python with Pytest and Selenium WebDriver.
- Use selenium.webdriver, WebDriverWait, expected_conditions.
- Follow Page Object Model (POM) design pattern.
"""
    else:
        framework_rules = """
- Use Python with Pytest and Playwright.
- Use playwright.sync_api, sync_playwright.
- Follow Page Object Model (POM) design pattern.
"""
    return f"""
You are an Automation Engineer.

Generate {framework} automation test scripts.

URL: {url}
FRAMEWORK: {framework}

TEST CASES:
{content}

Generate EXACTLY 3 files:
###FILE:pages/{feature_name}_page.py
###FILE:tests/test_{feature_name}.py
###FILE:data/{feature_name}_data.json

Rules:
{framework_rules.strip()}

Do not use markdown blocks.
Do not generate extra files.
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
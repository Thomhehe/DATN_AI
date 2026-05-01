import os
import re


def build_prompt_all(testcases, url, framework):
    first_feature = testcases[0].get("feature", "test").lower()
    first_feature = re.sub(r'[^a-z0-9_]', '_', first_feature).strip('_')
    if not first_feature:
        first_feature = "test"

    content = ""
    for tc in testcases:
        data_section = ""
        if tc.get("test_data"):
            data_lines = []
            for data in tc["test_data"]:
                row_text = ", ".join(f"{key}: {value}" for key, value in data.items())
                data_lines.append(f"- {row_text}")
            data_section = "\nTEST DATA:\n" + "\n".join(data_lines)

        content += f"""
ID: {tc['id']}
DESCRIPTION: {tc.get('description', '')}
STEPS:
{tc['steps']}
EXPECTED: {tc['expected']}{data_section}
"""

    return f"""
You are a QA Automation Engineer.

URL: {url}
TEST CASES:
{content}

TASK:
Generate Pytest automation using {framework} (data-driven)
OUTPUT (STRICT):
###FILE:pages/{first_feature}_page.py
###FILE:tests/test_{first_feature}.py

FRAMEWORK:

- If framework == "selenium":
    + Use selenium.webdriver
    + Use WebDriverWait and expected_conditions
    + Use webdriver-manager
    + Use driver.find_element

- If framework == "playwright":
    + Use playwright.sync_api
    + Use page.locator()
    + Use page.fill(), page.click()
    + Use page.text_content()
    + Use sync_playwright
    + DO NOT use Selenium APIs

RULES:

1. DATA:
- test_data = [(input1, input2, ..., expected)]
- ids = [test case IDs]
- Inputs are SINGLE values (NOT list)

2. STRUCTURE:
- One Page class only
- Methods: __init__, perform_actions, get_result
- No extra methods
- Page class must use self.driver (selenium) OR self.page (playwright)
- DO NOT pass driver/page into methods

3. LOCATOR:
- Define locators in __init__
- Since you DO NOT have a real browser and CANNOT see the HTML DOM, DO NOT guess specific `id`, `name`, or `css` classes unless they are explicitly mentioned in the TEST CASES.
- Build locators that are broad enough to be robust, but keep them concise and avoid excessively long union chains. Prefer compact composite predicates over many repeated fallback branches.
- For XPaths, use `translate()` to handle case-insensitivity for both text and attributes (e.g., lowercasing all text before comparison).
- Combine multiple possible node types and attribute conditions using the `|` (union) operator and `or` logical conditions only when needed to cover realistic matching variants.
- For buttons/actions: ALWAYS generate a comprehensive union locator `|` that covers multiple possible HTML implementations. You MUST include `//button`, `//a`, AND `//input[@type='submit' or @type='button']` in your XPath.
- Build precise locators matching the EXACT text or action keyword derived from the TEST CASES steps. Use case-insensitive matching on `normalize-space(.)` for `button`/`a`, and `@value` for `input`. Example: `//button[contains(translate(normalize-space(.), '...', '...'), 'login')] | //input[@type='submit' or @type='button'][contains(translate(@value, '...', '...'), 'login')] | //a[contains(translate(normalize-space(.), '...', '...'), 'login')]`.
- Include `*[@role='button']` or elements with `class` containing 'btn' or 'button' as fallbacks to ensure compatibility across different UI frameworks.
- WARNING: DO NOT use generic `div`, `span`, `p`, `h1`-`h6`, or `td` in button locators just by matching text, because you might accidentally match an unclickable parent container. ONLY fallback to `div` or `span` if they have a `class` containing `btn`, `button`, or `role='button'`.
- For action icons: prioritize the outer clickable wrapper (`button`, `a`, `*[@role='button']`) matching by `title`, `aria-label`, or class containing the action keyword (e.g., `search`, `delete`). Allow nested icon nodes (`svg`, `i`, `path`, `img`) only if targeting the icon directly.
- For tooltip or hover-triggered controls, include `@title`, `@aria-label`, `@data-tooltip`, `@data-title` matching the action keyword.
- For inputs: Exhaustively include checks for `@placeholder`, `@name`, `@aria-label`, `@type`, and `contains(@class, ...)`, while still allowing flexible locators on `span`/`div` wrappers when input fields are visually grouped.
- Even if a step mentions "icon", you MUST STILL generate a comprehensive locator covering the wrapper element, button, link, or the icon itself based on the action intent. The "icon" keyword merely indicates the click method to use.
- For EXPECTED results, you MUST NOT hardcode static locators if you can extract the expected text dynamically.
- INSTEAD, build a precise, case-insensitive XPath inside `get_result()` that dynamically searches for the extracted quoted texts. If multiple quoted texts exist, iterate over them to check.
- To avoid capturing the entire page text from generic structural elements (`body`, `html`, `main`, etc.), your XPath MUST target the DEEPEST element containing the text. Use this XPath pattern: `//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{{lower_text}}') and not(*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{{lower_text}}')])]"`. This guarantees you catch the exact element (toast, span, div, p) holding the message, whether on the current page or a new page.
- If playwright: Chain multiple broad text, role, and generic locator queries using `.or_()`.

4. ACTION
- Steps must follow TEST CASES strictly. You MUST generate code that explicitly performs EACH step listed in the TEST CASES sequentially. Do not skip steps or combine them inappropriately. Ensure you wait for the necessary elements to be interactable before each step to avoid missing actions.
- Input:
    If selenium:
        use visibility_of_element_located for input fields.
        clear() + send_keys(value)

    If playwright:
        use page.locator(...).fill(value)
- Click:
    - For ALL buttons, links, icons, and actions:
        + If selenium: DO NOT use `element_to_be_clickable` because it causes TimeoutExceptions if the element is slightly obscured or unclickable. ALWAYS use `presence_of_element_located` to wait for the clickable element in the DOM. Then, ALWAYS use JavaScript click: `self.driver.execute_script("arguments[0].click();", element)` to ensure the click is successful and bypass intercepts.
        + If playwright: use normal `.click(force=True)`.

5. WAIT
- If selenium:
    use WebDriverWait. If an action causes a page navigation/redirect, ensure you explicitly wait for the new page or the new element to load before interacting.

- If playwright:
    use auto-wait (DO NOT use WebDriverWait). Playwright handles navigation waits automatically.

6. RESULT (IMPORTANT):
- EXTRACT QUOTED TEXT: If the `EXPECTED` value contains text inside double quotes (e.g. `Hiển thị lỗi "Email trống" hoặc "Sai định dạng"`), you MUST use `re.findall(r'"([^"]*)"', expected)` inside `get_result()` to dynamically extract a list of ALL quoted substrings.
- In `get_result()`, if quoted texts exist, iterate through them and build dynamic XPaths to find the element. If no quotes exist, use the full `expected` string.
- get_result() returns final result text. The logic MUST be strictly tailored to the extracted expected value(s).
- To catch messages (errors, success, notifications) reliably whether on the CURRENT PAGE or ANOTHER PAGE, you MUST explicitly WAIT for the expected text to appear in the DOM.
- The dynamic XPath MUST find the deepest element containing the text to avoid grabbing large containers. Use this exact pattern:
  `xpath = f"//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{{lower_text}}') and not(*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{{lower_text}}')])]"`. Ensure you lowercase `text` in Python before inserting it into the XPath.
- Wait Strategy for Messages:
  * If selenium: Use `WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))` to explicitly wait for the message element.
  * If playwright: Use `self.page.locator(xpath).first.wait_for(state="attached", timeout=10000)` to wait for the element.
- By waiting for this dynamic XPath, the script will automatically pause for AJAX requests, toasts, or page transitions to finish and display the message. You do NOT need to hardcode specific container classes or page transition checks.
- Detection Layers Reference:
  + Layer 1 (Native Alerts): Handle browser alerts/dialogs first if applicable.
  + Layer 2 (DOM Text Search): Use the wait strategy and dynamic XPath described above. This handles toasts, inline errors, and cross-page messages seamlessly. Return the `.text` (Selenium) or `.inner_text()` (Playwright) of the matched element.
  + Layer 3 (JS Runtime Analysis): Extract HTML5 input validationMessage (`element.validationMessage`). STRICT RULE: ONLY use this as a fallback if Layer 2 fails (e.g., inside the `except` block).
- Use try-except blocks (Selenium) or error-handling (Playwright) when waiting for elements so the script does not crash immediately, allowing fallback to Layer 3 or returning an empty string/URL if everything fails.
- Return ONLY the normalized, stripped visible text content of the SPECIFIC detected element. Do NOT return the text content of the entire page, body, or large containers.
- If expected is empty or indicates purely a URL change: wait for navigation and return the current URL.
- Do not fallback to URL when expected is a specific text message.
7. TEST:
- parametrize data
- open URL
- call Page methods
- call get_result(expected)
- Parsing Expected in Assertion: You MUST extract quoted strings from `expected` inside the test function to perform an exact match assertion:
  `expected_texts = re.findall(r'"([^"]*)"', expected)`
  `if expected_texts:`
  `    assert any(text == result for text in expected_texts)`
  `else:`
  `    assert expected == result`
- This ensures that if 1 of 2 expected outcomes in double quotes matches the result EXACTLY, the test PASSES. DO NOT use `in` for comparison.

- If selenium:
    + use pytest fixture with Chrome driver
    + use webdriver-manager with Service (no local driver)
    + ChromeOptions MUST contain EXACTLY one argument: "--start-maximized"

- If playwright:
    + use pytest fixture (session)
    + use sync_playwright
    + launch_persistent_context (user_data_dir, args=["--start-maximized"], no_viewport=True)
    + reuse context
    + use existing page: context.pages[0] if exists else new_page()
    + use page object

CONSTRAINT:
- No sleep
- Only 2 files
- DO NOT mix Selenium and Playwright
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
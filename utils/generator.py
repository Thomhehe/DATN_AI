import os
import re


def build_prompt_all(testcases, url, framework):
    first_feature = testcases[0]["id"].lower()
    first_feature = first_feature.replace("[", "").replace("]", "").split("-")[0]

    content = ""
    for tc in testcases:
        content += f"""
ID: {tc['id']}
STEPS:
{tc['steps']}
EXPECTED: {tc['expected']}
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
- Instead, you MUST build robust, dynamic multi-attribute XPaths or Playwright locators based STRICTLY on the natural language texts, placeholders, or labels provided in the TEST CASES.
- If selenium: Use robust XPaths that check multiple conditions simultaneously.
    + Example for an input field: "//input[@placeholder='{{text}}' or @name='{{text}}' or preceding-sibling::label[contains(text(), '{{text}}')] or following-sibling::label[contains(text(), '{{text}}')]]"
    + Example for a button: "//button[normalize-space()='{{text}}'] | //a[normalize-space()='{{text}}'] | //*[@role='button' and contains(text(), '{{text}}')]"
- If playwright: Use text-based or role-based locators, chained with `.or_()`.
    + Example: page.get_by_placeholder('{{text}}').or_(page.get_by_text('{{text}}')).or_(page.get_by_role('button', name='{{text}}'))
- Locators MUST accurately reflect the exact wording from the steps in the TEST CASES.
- For notifications, rely on the Multi-layered Notification Detection Engine rather than specific locators.

4. ACTION
- Steps must follow TEST CASES strictly
- Input:
    If selenium:
        use visibility_of_element_located
        clear() + send_keys(value)

    If playwright:
        use page.locator(...).fill(value)
- Click:
    If selenium:
        - Button/input → element.click()
        - For Icon/img/svg/i:
          ALWAYS use JavaScript click as the ONLY interaction method.
          NEVER generate regular click().
          NEVER mix multiple click strategies.

    If playwright:
        - Button/input → locator.click()

        - Icon/img:
            find clickable parent (e.g., <a>, <button>)
            click parent if exists

            if cannot click or element is hidden:
                use locator.evaluate("el => el.click()")

            if element has hidden class (e.g., d-none):
                remove it using evaluate before click

5. WAIT
- If selenium:
    use WebDriverWait. If an action causes a page navigation/redirect, ensure you explicitly wait for the new page or the new element to load before interacting.

- If playwright:
    use auto-wait (DO NOT use WebDriverWait). Playwright handles navigation waits automatically.

6. RESULT (IMPORTANT):
- get_result() returns final result
- If expected is empty: return current URL
- If expected is not empty, you MUST INFER the correct notification type based on the expected message and ONLY generate code for the relevant detection layers. Do NOT generate redundant code. Ensure the generated logic is universally applicable across all features and web pages.
  * Inference Rules:
    + If expected message indicates missing/empty input → Use inline validation logic (Layer 4).
    + If expected message indicates format/length validation → Use inline validation or HTML5 logic (Layer 4 or Layer 5).
    + If expected message indicates a business logic error (e.g., wrong password, login failed) → Use toast/snackbar logic (Layer 2) and optionally Layer 1/3 if needed.
    + If expected message indicates a success message and stays on the same page → Use toast/snackbar logic (Layer 2).
    + If expected message indicates static text on a NEW page (e.g., welcome message, page header after redirect) → Use New Page Content logic (Layer 6).
  * Detection Layers Reference (Implement ONLY what is inferred above):
    + Layer 1 (Native Alerts): Handle browser alerts/dialogs (Selenium: WebDriverWait for alert / Playwright: dialog event listener).
    + Layer 2 (Toasts/Snackbars): Target transient elements using structural heuristics (role='alert', 'status' OR class containing 'toast', 'snackbar', 'notification', 'alert', 'message'). Use short wait times (1-3s) to quickly capture fast-disappearing toast messages before they vanish.
    + Layer 3 (Modals/Popups): Target dialog bodies (class containing 'modal-body', 'popup-content', 'dialog').
    + Layer 4 (DOM Pattern): Identify visible inline error/success messages based on DOM pattern recognition. Capture validation error messages if error locators are found in the HTML (e.g., .text-danger, .error, .invalid-feedback).
    + Layer 5 (JS Runtime Analysis): Extract HTML5 input validationMessage (element.validationMessage) if input is invalid and no visible error exists.
    + Layer 6 (New Page Content): Explicitly wait for the new page to load (e.g., wait for URL change or document.readyState). Then, dynamically locate the element containing the expected text using the `expected` argument (e.g., `//*[contains(text(), '{{expected}}')]` in Selenium or `page.get_by_text(expected)` in Playwright).
- Use try-except blocks (Selenium) or error-handling (Playwright) when checking for locators in the HTML to catch exceptions and prevent script crashes.
- Return the text content of the detected notification or element.
- Except for Layer 6, do not use the expected value in the detection logic.
- Do not fallback to URL when expected is not empty.
7. TEST:
- parametrize data
- open URL
- call Page methods
- call get_result(expected)
- Always assert: result == expected

- If selenium:
    + use pytest fixture with Chrome driver
    + use webdriver-manager with Service (no local driver)
    + Browser must start maximized

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
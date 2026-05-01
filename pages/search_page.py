from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SearchPage:
    def __init__(self, driver):
        self.driver = driver
        # Upper/lower for translate() to handle case-insensitivity (ASCII A-Z)
        UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        LOWER = "abcdefghijklmnopqrstuvwxyz"

        # Broad, case-insensitive locator for search icon/wrapper (button/a/*[@role='button'])
        # Matches title, aria-label, class or inner text containing 'search' (Vietnamese sites often mix languages)
        self.search_icon_locator = (
            By.XPATH,
            (
                "//button["
                "contains(translate(normalize-space(string(.)), '{U}', '{L}'), 'search') "
                "or contains(translate(@title, '{U}', '{L}'), 'search') "
                "or contains(translate(@aria-label, '{U}', '{L}'), 'search') "
                "or contains(translate(@class, '{U}', '{L}'), 'search')"
                "]"
                " | //a["
                "contains(translate(normalize-space(string(.)), '{U}', '{L}'), 'search') "
                "or contains(translate(@title, '{U}', '{L}'), 'search') "
                "or contains(translate(@aria-label, '{U}', '{L}'), 'search') "
                "or contains(translate(@class, '{U}', '{L}'), 'search')"
                "]"
                " | //*[@role='button' and ("
                "contains(translate(normalize-space(string(.)), '{U}', '{L}'), 'search') "
                "or contains(translate(@title, '{U}', '{L}'), 'search') "
                "or contains(translate(@aria-label, '{U}', '{L}'), 'search') "
                "or contains(translate(@class, '{U}', '{L}'), 'search')"
                ")]"
            ).format(U=UPPER, L=LOWER),
        )

        # Broad, case-insensitive locator for input search field (input or textarea)
        self.search_input_locator = (
            By.XPATH,
            (
                "//input["
                "contains(translate(@type, '{U}', '{L}'), 'search') "
                "or contains(translate(@placeholder, '{U}', '{L}'), 'tìm') "
                "or contains(translate(@placeholder, '{U}', '{L}'), 'tim') "
                "or contains(translate(@name, '{U}', '{L}'), 'search') "
                "or contains(translate(@aria-label, '{U}', '{L}'), 'search') "
                "or contains(translate(@class, '{U}', '{L}'), 'search')"
                "]"
                " | //textarea["
                "contains(translate(@placeholder, '{U}', '{L}'), 'tìm') "
                "or contains(translate(@placeholder, '{U}', '{L}'), 'tim') "
                "or contains(translate(@name, '{U}', '{L}'), 'search') "
                "or contains(translate(@aria-label, '{U}', '{L}'), 'search') "
                "or contains(translate(@class, '{U}', '{L}'), 'search')"
                "]"
            ).format(U=UPPER, L=LOWER),
        )

        # Generic broad element locator used as fallback to click a visible 'search' textual control
        self.search_text_button_locator = (
            By.XPATH,
            (
                "//*["
                "(translate(normalize-space(string(.)), '{U}', '{L}') = 'search' or contains(translate(normalize-space(string(.)), '{U}', '{L}'), 'search')) "
                "and (self::button or self::a or @role='button')"
                "]"
            ).format(U=UPPER, L=LOWER),
        )

        # Note: result locators are built dynamically in get_result() to incorporate exact expected text.

    def perform_actions(self, keyword, use_icon=True):
        """
        Steps implemented strictly:
        1. Click icon/search control (JS click if use_icon True; presence wait)
        2. Wait for input visibility, clear, enter keyword, press Enter
        """
        wait = WebDriverWait(self.driver, 10)

        # Step: Click icon/search control
        if use_icon:
            # Per rules: for icon-based actions, wait for PRESENCE and use JS click
            try:
                elem = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(self.search_icon_locator)
                )
                # JavaScript click
                self.driver.execute_script("arguments[0].click();", elem)
            except TimeoutException:
                # Fallback: try to find a textual search button and JS click it
                try:
                    elem = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(self.search_text_button_locator)
                    )
                    self.driver.execute_script("arguments[0].click();", elem)
                except TimeoutException:
                    # No clickable icon found; continue - input may already be visible
                    pass
        else:
            # Normal click (visibility)
            try:
                elem = wait.until(EC.visibility_of_element_located(self.search_text_button_locator))
                elem.click()
            except TimeoutException:
                # Fallback: try icon locator with normal click
                try:
                    elem = wait.until(EC.visibility_of_element_located(self.search_icon_locator))
                    elem.click()
                except TimeoutException:
                    pass

        # Step: Enter keyword into input
        try:
            input_elem = wait.until(EC.visibility_of_element_located(self.search_input_locator))
            try:
                input_elem.clear()
            except Exception:
                # Some inputs may not support clear; ignore
                pass
            # If keyword is empty string, still perform clear and press Enter
            if keyword is not None and keyword != "":
                input_elem.send_keys(keyword)
            # Press Enter as final step
            input_elem.send_keys(Keys.ENTER)
        except TimeoutException:
            # If input not found, attempt to send ENTER to focused element via JS
            try:
                self.driver.execute_script("document.activeElement && document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {'key':'Enter'}));")
            except Exception:
                pass

    def get_result(self, expected):
        """
        Returns the text of the element containing the exact expected message.
        Implements Layer inference:
        - If expected implies missing/empty input -> Layer 4 (inline validation)
        - If expected implies search results -> Layer 6 (page content)
        Uses precise, case-insensitive XPath with translate() and normalize-space() incorporating the expected text.
        """
        wait_short = WebDriverWait(self.driver, 3)
        wait_long = WebDriverWait(self.driver, 10)
        UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        LOWER = "abcdefghijklmnopqrstuvwxyz"

        # Prepare expected in XPath literal (use double quotes)
        expected_escaped = expected.replace('"', "'")  # simplistic escape for XPath; tests do not contain quotes

        # Build Layer 4 XPath (inline validation near inputs)
        xpath_layer4 = (
            "//*["  # any element
            " (translate(normalize-space(string(.)), '{U}', '{L}') = translate(\"{exp}\", '{U}', '{L}')) and "
            "("
            "local-name() = 'small' or local-name() = 'label' or local-name() = 'span' or local-name() = 'div' or local-name() = 'p'"
            ") and ("
            "contains(translate(@class, '{U}', '{L}'), 'error') or contains(translate(@class, '{U}', '{L}'), 'help') "
            "or contains(translate(@class, '{U}', '{L}'), 'message') or contains(translate(@class, '{U}', '{L}'), 'notice') "
            ")"
            "]"
        ).format(U=UPPER, L=LOWER, exp=expected_escaped)

        # Build Layer 2 XPath (toasts/snackbars, transient)
        xpath_layer2 = (
            "//*["  # any element
            "(translate(normalize-space(string(.)), '{U}', '{L}') = translate(\"{exp}\", '{U}', '{L}')) and ("
            "@role='alert' or @role='status' or contains(translate(@class, '{U}', '{L}'), 'toast') "
            "or contains(translate(@class, '{U}', '{L}'), 'snack') or contains(translate(@class, '{U}', '{L}'), 'notification') "
            "or contains(translate(@class, '{U}', '{L}'), 'alert') or contains(translate(@class, '{U}', '{L}'), 'message')"
            ")"
            "]"
        ).format(U=UPPER, L=LOWER, exp=expected_escaped)

        # Build Layer 6 XPath (page content, full search results or messages)
        xpath_layer6 = (
            "//*[" 
            "translate(normalize-space(string(.)), '{U}', '{L}') = translate(\"{exp}\", '{U}', '{L}')"
            "]"
        ).format(U=UPPER, L=LOWER, exp=expected_escaped)

        # Determine inference: missing/empty input vs search results
        # Heuristic: if expected contains Vietnamese word 'Nhập' (enter/input) -> inline validation
        try:
            if "nhập" in expected.lower() or "vui lòng" in expected.lower() or "nhập từ khóa" in expected.lower():
                # Layer 4 only
                try:
                    el = wait_long.until(EC.presence_of_element_located((By.XPATH, xpath_layer4)))
                    return el.text.strip()
                except TimeoutException:
                    # As a secondary attempt check for layer2 (some sites show as toast) quickly
                    try:
                        el = wait_short.until(EC.presence_of_element_located((By.XPATH, xpath_layer2)))
                        return el.text.strip()
                    except TimeoutException:
                        # Lastly check any element with exact text (layer6) to be safe
                        try:
                            el = wait_long.until(EC.presence_of_element_located((By.XPATH, xpath_layer6)))
                            return el.text.strip()
                        except TimeoutException:
                            return ""
            else:
                # Assume search result message -> Layer 6 (page content). Wait for page/content to load.
                try:
                    el = wait_long.until(EC.presence_of_element_located((By.XPATH, xpath_layer6)))
                    return el.text.strip()
                except TimeoutException:
                    # Try toast/snackbar briefly
                    try:
                        el = wait_short.until(EC.presence_of_element_located((By.XPATH, xpath_layer2)))
                        return el.text.strip()
                    except TimeoutException:
                        # As last resort, try inline
                        try:
                            el = wait_long.until(EC.presence_of_element_located((By.XPATH, xpath_layer4)))
                            return el.text.strip()
                        except TimeoutException:
                            return ""
        except Exception:
            return ""
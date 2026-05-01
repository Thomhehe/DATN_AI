import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException


class SearchMixiShopPage:
    def __init__(self, driver):
        self.driver = driver
        # Broad but targeted clickable wrappers for a "search" icon/button (case-insensitive)
        cond = (
            "contains(translate(normalize-space(string(.)),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
            " or contains(translate(@title,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
            " or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
            " or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
            " or .//svg or .//i"
        )
        self.search_icon_locator = (
            By.XPATH,
            "/html/body/header[1]/div/div[4]/div/span",
        )

        # Flexible locator for search input fields (type, placeholder, name, aria-label, class, or nested inside search wrappers)
        inp_cond = (
            "@type='search' or @type='text' or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
            " or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'tìm')"
            " or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
            " or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
            " or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
        )
        self.search_input_locator = (
            By.XPATH,
            f"//input[{inp_cond}] | //input[@role='search'] | //div[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')]//input",
        )

    def perform_actions(self, keyword):
        # Step 2: Click icon search
        icon = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.search_icon_locator))
        try:
            tag = icon.tag_name.lower()
        except Exception:
            tag = ""
        # If the clickable node is an image element, use JS click; otherwise normal click
        if tag == "img":
            try:
                self.driver.execute_script("arguments[0].click();", icon)
            except JavascriptException:
                icon.click()
        else:
            icon.click()

        # Step 3: Press search box (focus it)
        search_input = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.search_input_locator))
        search_input.click()

        # Step 4: Clear keyword or enter keyword
        search_input.clear()
        if keyword:
            # enter keyword then press Enter
            from selenium.webdriver.common.keys import Keys

            search_input.send_keys(keyword + Keys.ENTER)
        else:
            # clear already done; press Enter to trigger native validation
            from selenium.webdriver.common.keys import Keys

            time.sleep(3)
            search_input.send_keys(Keys.ENTER)

    def get_result(self, expected):
        # First, try to capture HTML5 validationMessage from the search input (Layer 5)
        try:
            search_input = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(self.search_input_locator))
            try:
                validation = self.driver.execute_script("return arguments[0].validationMessage || '';", search_input)
                if validation and validation.strip():
                    return validation.strip()
            except JavascriptException:
                # ignore and continue to page-level checks
                pass
        except TimeoutException:
            # no input found quickly; continue to page-level checks
            pass

        # Layer 6: page content - find smallest element whose normalized text equals expected (case-insensitive)
        # Build case-insensitive XPath that matches the exact normalized visible text
        expected_norm = expected.strip()
        # Escape single quotes in expected for XPath literal: use concat if necessary
        if "'" in expected_norm:
            parts = expected_norm.split("'")
            xpath_literal = "concat(" + ", \"'\", ".join(f"'{p}'" for p in parts) + ")"
        else:
            xpath_literal = f"'{expected_norm}'"
        xpath = (
            "//*[translate(normalize-space(string(.)),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')="
            f"translate(normalize-space({xpath_literal}),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')]"
        )
        try:
            elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            text = elem.text or ""
            return " ".join(text.split()).strip()
        except TimeoutException:
            # If not found, return empty string to allow test to assert and fail
            return ""
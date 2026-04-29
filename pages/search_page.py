from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SearchPage:
    def __init__(self, driver):
        self.driver = driver
        # Locators inferred by visible text / placeholder / name / generic patterns
        self.search_button = (By.XPATH, "//button[contains(., 'Tìm') or contains(., 'tìm') or contains(@aria-label,'search') or contains(@class,'search')]")
        self.search_input = (By.XPATH, "//input[@type='search' or contains(@placeholder,'Tìm') or contains(@placeholder,'tìm') or @name='s' or contains(@class,'search')]")
        # Inline validation candidates (Layer 4)
        self.inline_error_locators = [
            (By.XPATH, "//*[contains(@class,'text-danger') and normalize-space(.)!='']"),
            (By.XPATH, "//*[contains(@class,'invalid-feedback') and normalize-space(.)!='']"),
            (By.XPATH, "//*[contains(@class,'error') and normalize-space(.)!='']"),
            (By.XPATH, "//*[contains(@class,'help-block') and normalize-space(.)!='']"),
            (By.XPATH, "//span[contains(@class,'error') and normalize-space(.)!='']"),
        ]
        # Toast/snackbar/result candidates (Layer 2)
        self.toast_locators = [
            (By.XPATH, "//*[@role='alert' and normalize-space(.)!='']"),
            (By.XPATH, "//*[@role='status' and normalize-space(.)!='']"),
            (By.XPATH, "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'toast') and normalize-space(.)!='']"),
            (By.XPATH, "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'snackbar') and normalize-space(.)!='']"),
            (By.XPATH, "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'notification') and normalize-space(.)!='']"),
            (By.XPATH, "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'alert') and normalize-space(.)!='']"),
            (By.XPATH, "//*[contains(@class,'woocommerce-result-count') and normalize-space(.)!='']"),
            (By.XPATH, "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'result') and normalize-space(.)!='']"),
            (By.XPATH, "//*[@id='search' or contains(@class,'search-results') or contains(@class,'search-result')][normalize-space(.)!='']"),
        ]

    def perform_actions(self, value):
        # 1. Click search (button/icon). Use visibility_of_element_located for button/input click.
        try:
            btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.search_button))
            btn.click()
        except Exception:
            # fallback: try JS click if normal click fails or element is not interactable
            try:
                btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.search_button))
                self.driver.execute_script("arguments[0].click();", btn)
            except Exception:
                pass

        # 2. Find input, clear, enter value
        input_el = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.search_input))
        try:
            input_el.clear()
        except Exception:
            # Some inputs may not support clear(); set empty via JS
            try:
                self.driver.execute_script("arguments[0].value = '';", input_el)
            except Exception:
                pass

        if value is not None:
            if value != "":
                input_el.send_keys(value)
            # Press Enter
            input_el.send_keys(Keys.ENTER)

    def get_result(self, expected):
        # If expected is empty string, return current URL (not used by these tests)
        if not expected:
            return self.driver.current_url

        # Infer detection layer from expected
        exp_lower = expected.lower() if expected else ""
        # If expected indicates missing/empty input -> Layer 4 (inline validation)
        if "nhập" in exp_lower or "vui lòng nhập" in exp_lower or "không được để trống" in exp_lower:
            for locator in self.inline_error_locators:
                try:
                    el = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(locator))
                    text = el.text.strip()
                    if text:
                        return text
                except Exception:
                    continue
            # If no inline message found, return empty string to fail the assert in test
            return ""

        # Otherwise treat as informational/result message -> Layer 2 (toasts/snackbars) or result area
        for locator in self.toast_locators:
            try:
                el = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(locator))
                text = el.text.strip()
                if text:
                    return text
            except Exception:
                continue

        # As a last resort (still within Layer 2 heuristics), try broader search for visible non-empty elements under body
        try:
            candidates = self.driver.find_elements(By.XPATH, "//body//*[normalize-space(text())!='' and (contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'notice') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'kq') )]")
            for c in candidates:
                try:
                    t = c.text.strip()
                    if t:
                        return t
                except Exception:
                    continue
        except Exception:
            pass

        return ""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SearchPage:
    def __init__(self, driver):
        self.driver = driver
        # Locator for the search trigger (button/link/icon) - robust, text/aria/title based on the word "search"
        self.search_trigger = (
            By.CSS_SELECTOR, 'a[title="Tìm kiếm"]')
        # Locator for the search input - robustly target inputs that look like a search/keyword field
        self.search_input = (By.XPATH,
            "//input["
            " @type='search' "
            " or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'tìm')"
            " or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'từ khóa')"
            " or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'keyword')"
            " or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'tìm')"
            " or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'từ khóa')"
            " or contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
            " or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')"
            "]")
        # Generic inline error locator patterns (Layer 4)
        self.inline_error_xpath = (
            "//div[contains(@class,'text-danger') or contains(@class,'error') or contains(@class,'invalid-feedback') or "
            "contains(@class,'form-error') or contains(@class,'help-block') or contains(@class,'field-error') or "
            "contains(@class,'input-error') or contains(@class,'error-message') or contains(@class,'invalid') ]"
        )
        # Generic toast/snackbar locator patterns (Layer 2)
        self.toast_xpath = (
            "//*[( @role='alert' or @role='status' or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'toast') "
            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'snackbar') "
            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'notification') "
            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'alert') "
            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message') ) and string-length(normalize-space(.))>0]"
        )

    def perform_actions(self, keyword):
        wait = WebDriverWait(self.driver, 10)
        # Step 2: Click search trigger
        try:
            el = wait.until(EC.visibility_of_element_located(self.search_trigger))
            tag = el.tag_name.lower()
            # If the trigger looks like an icon element, use JS click; otherwise use normal click
            if tag in ("i", "svg", "img") or ('icon' in (el.get_attribute('class') or '').lower()):
                self.driver.execute_script("arguments[0].click();", el)
            else:
                el.click()
        except Exception:
            # As a fallback, try clicking any element that has role=button and contains 'search' in aria/title/class
            try:
                fallback = self.driver.find_element(By.XPATH,
                    "//*[@role='button' and (contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search') "
                    "or contains(translate(@title,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search') "
                    "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search'))]")
                fallback.click()
            except Exception:
                pass

        # Step 3 & 4: Locate search input, clear and press Enter (with or without keyword)
        try:
            inp = wait.until(EC.visibility_of_element_located(self.search_input))
            # Use clear() then send_keys
            inp.clear()
            if keyword:
                inp.send_keys(keyword)
            # Press Enter to submit search
            inp.send_keys(Keys.ENTER)
        except Exception:
            # If explicit search input not found, try a generic input box near the search trigger
            try:
                generic = self.driver.find_element(By.XPATH, "//input")
                generic.clear()
                if keyword:
                    generic.send_keys(keyword)
                generic.send_keys(Keys.ENTER)
            except Exception:
                pass

    def get_result(self, expected):
        """
        Return the detected message according to inferred detection layer:
         - If expected indicates missing/empty input -> Layer 4 (inline validation)
         - Else -> Layer 2 (toasts/snackbars)
        """
        # Decide layer based on expected message wording
        expected_lower = expected.lower() if expected else ""
        wait_short = WebDriverWait(self.driver, 3)
        # Layer 4: inline validation (for messages like "Nhập từ khóa để tìm kiếm")
        if "nhập" in expected_lower or "vui lòng" in expected_lower or expected_lower.strip() == "":
            try:
                # Try common inline error selectors first
                el = wait_short.until(EC.visibility_of_element_located((By.XPATH, self.inline_error_xpath)))
                return el.text.strip()
            except Exception:
                # Try nearby text nodes around input field (following-sibling or parent)
                try:
                    inp = self.driver.find_element(*self.search_input)
                    # following sibling
                    try:
                        sib = inp.find_element(By.XPATH, "following-sibling::*[string-length(normalize-space(.))>0][1]")
                        if sib and sib.is_displayed():
                            return sib.text.strip()
                    except Exception:
                        pass
                    # parent
                    try:
                        parent_msg = inp.find_element(By.XPATH, "ancestor::*[1]//*[contains(@class,'error') or contains(@class,'text-danger') or string-length(normalize-space(.))>0]")
                        if parent_msg and parent_msg.is_displayed():
                            return parent_msg.text.strip()
                    except Exception:
                        pass
                except Exception:
                    pass
            # If nothing found, attempt HTML5 validationMessage (Layer 5 fallback not primary for inline but safe)
            try:
                inp = self.driver.find_element(*self.search_input)
                vm = self.driver.execute_script("return arguments[0].validationMessage || '';", inp)
                return vm.strip()
            except Exception:
                return ""
        else:
            # Layer 2: toasts/snackbars - short wait for transient messages
            try:
                toast = wait_short.until(EC.visibility_of_element_located((By.XPATH, self.toast_xpath)))
                return toast.text.strip()
            except Exception:
                # Try to capture any persistent area that might show result counts (e.g., headings or summaries)
                try:
                    summary = self.driver.find_element(By.XPATH,
                        "//*[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'kết quả') or contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'kết quả tìm kiếm') or contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'kết quả phù hợp')]")
                    if summary and summary.is_displayed():
                        return summary.text.strip()
                except Exception:
                    pass
            return ""
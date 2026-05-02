from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://teelab.vn/account/login?ReturnUrl=%2Faccount"

        # Input locators: include checks for placeholder, name, aria-label, type, and class hints (case-insensitive)
        self.email_locator = (
            By.XPATH,
            "//input[("
            "translate(@type,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='email' "
            "or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email') "
            "or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'e-mail') "
            "or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email') "
            "or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email') "
            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email') "
            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'form-control')"
            ")]",
        )

        self.password_locator = (
            By.XPATH,
            "//input[("
            "translate(@type,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='password' "
            "or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'password') "
            "or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'mật') "
            "or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'password') "
            "or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'password') "
            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'password') "
            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'form-control')"
            ")]",
        )

        # Universal button XPath pattern for case-insensitive matching including Vietnamese diacritics.
        btn_pattern = (
            "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            "'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}')] | "
            "//input[(@type='submit' or @type='button') and contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            "'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}')] | "
            "//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            "'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}')] | "
            "//*[contains(@class, 'btn') or contains(@class, 'button') or @role='button'][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            "'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}') or contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            "'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}') or contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            "'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}')]"
        )

        # Use Vietnamese lowercase 'đăng nhập' as the action keyword for login
        self.login_button_locator = (By.XPATH, btn_pattern.format(keyword="đăng nhập"))

    def perform_actions(self, email, password):
        # Step 1: Navigate to login page
        self.driver.get(self.url)

        # Step 2: Handle email input (clear or enter)
        try:
            email_el = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.email_locator)
            )
        except Exception:
            # If email input not found, re-raise to allow test to fail with meaningful info
            raise

        # If the test case expects clearing the email, calling with empty string will just clear
        email_el.clear()
        if email:
            email_el.send_keys(email)

        # Step 3: Enter password
        password_el = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.password_locator)
        )
        password_el.clear()
        if password:
            password_el.send_keys(password)

        # Step 4: Click login using universal button XPath (presence + JS click)
        login_btn_el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.login_button_locator)
        )
        element = self.driver.find_element(*self.login_button_locator)
        # Use JS click to bypass intercepts
        self.driver.execute_script("arguments[0].click();", element)

    def get_result(self, expected):
        """
        - Extract quoted texts from expected using re.findall.
        - For each quoted text:
            - If it looks like a URL (starts with http), wait for navigation and return current URL.
            - Else, build dynamic deepest-element XPath and wait for presence, then return element.text.
        - If no quoted texts found, treat expected as full text; if it contains http-like substring, wait for URL change.
        - Fallback: check HTML5 validationMessage on email/password inputs.
        """
        expected_texts = re.findall(r'"([^"]*)"', expected)
        # XPath template to find the deepest element containing the text (case-insensitive)
        xpath_template = "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{lower_text}') and not(*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{lower_text}')])]"

        # Layer 1 & 2 handling
        try:
            if expected_texts:
                for text in expected_texts:
                    if text.strip().lower().startswith("http"):
                        # Wait for navigation to include the expected URL
                        WebDriverWait(self.driver, 10).until(lambda d: text in d.current_url)
                        return self.driver.current_url.strip()
                    lower_text = text.strip().lower()
                    xpath = xpath_template.format(lower_text=lower_text)
                    try:
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                        el = self.driver.find_element(By.XPATH, xpath)
                        return el.text.strip()
                    except Exception:
                        # Try next quoted text or fallback to Layer 3
                        continue
            else:
                # No quoted texts: consider full expected string
                cleaned = expected.strip()
                if cleaned.lower().startswith("display url") or "http" in cleaned:
                    # Wait for navigation and return current URL
                    WebDriverWait(self.driver, 10).until(lambda d: d.current_url and d.current_url != self.url)
                    return self.driver.current_url.strip()
                lower_text = cleaned.lower()
                xpath = xpath_template.format(lower_text=lower_text)
                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                    el = self.driver.find_element(By.XPATH, xpath)
                    return el.text.strip()
                except Exception:
                    pass
        except Exception:
            # Continue to fallback
            pass

        # Layer 3 fallback: HTML5 validationMessage for inputs
        try:
            email_el = self.driver.find_element(*self.email_locator)
            val_msg = self.driver.execute_script("return arguments[0].validationMessage;", email_el)
            if val_msg:
                return val_msg.strip()
        except Exception:
            pass

        try:
            password_el = self.driver.find_element(*self.password_locator)
            val_msg = self.driver.execute_script("return arguments[0].validationMessage;", password_el)
            if val_msg:
                return val_msg.strip()
        except Exception:
            pass

        # If all fails, return empty string
        return ""
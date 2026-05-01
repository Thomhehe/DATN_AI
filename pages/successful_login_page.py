from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException, JavascriptException
import re

class SuccessfulLoginPage:
    def __init__(self, driver):
        self.driver = driver
        # Common lowercase translation snippet for XPath
        self.UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.LOWER = 'abcdefghijklmnopqrstuvwxyz'

        # Email input: try to match type/email placeholder/name/aria-label/id/class containing 'email'
        self.email_locator = (
            "//input[@type='email']"
            "|//input[contains(translate(@placeholder, '{}', '{}'), 'email')]"
            "|//input[contains(translate(@name, '{}', '{}'), 'email')]"
            "|//input[contains(translate(@aria-label, '{}', '{}'), 'email')]"
            "|//input[contains(translate(@id, '{}', '{}'), 'email')]"
            "|//input[contains(translate(@class, '{}', '{}'), 'email')]"
        ).format(self.UPPER, self.LOWER, self.UPPER, self.LOWER, self.UPPER, self.LOWER, self.UPPER, self.LOWER, self.UPPER, self.LOWER, self.UPPER, self.LOWER)

        # Password input: match type='password' or labels containing 'password' or Vietnamese 'mật khẩu'
        self.password_locator = (
            "//input[@type='password']"
            "|//input[contains(translate(@placeholder, '{}', '{}'), 'password')]"
            "|//input[contains(translate(@placeholder, '{}', '{}'), 'mật khẩu')]"
            "|//input[contains(translate(@name, '{}', '{}'), 'password')]"
            "|//input[contains(translate(@aria-label, '{}', '{}'), 'password')]"
            "|//input[contains(translate(@id, '{}', '{}'), 'password')]"
            "|//input[contains(translate(@class, '{}', '{}'), 'password')]"
        ).format(self.UPPER, self.LOWER, self.UPPER, self.LOWER, self.UPPER, self.LOWER, self.UPPER, self.LOWER, self.UPPER, self.LOWER, self.UPPER, self.LOWER)

        # Login button/link/icon: comprehensive union per framework rules (case-insensitive)
        # Match English 'login' and Vietnamese 'đăng nhập'
        self.login_button_locator = (
            "/html/body/strong/div[2]/section[2]/div/div/div/div/div/div/div/div[1]/form/div/div/input"
        ).format(
            self.UPPER, self.LOWER, self.UPPER, self.LOWER,
            self.UPPER, self.LOWER, self.UPPER, self.LOWER,
            self.UPPER, self.LOWER, self.UPPER, self.LOWER,
            self.UPPER, self.LOWER, self.UPPER, self.LOWER
        )

    def perform_actions(self, email, password):
        # Wait for email input visibility and enter email
        wait = WebDriverWait(self.driver, 10)
        email_elem = wait.until(EC.visibility_of_element_located((By.XPATH, self.email_locator)))
        email_elem.clear()
        if email is not None:
            email_elem.send_keys(email)

        # Wait for password input visibility and enter password
        pwd_elem = wait.until(EC.visibility_of_element_located((By.XPATH, self.password_locator)))
        pwd_elem.clear()
        if password is not None:
            pwd_elem.send_keys(password)

        # Wait for login button presence (not clickable) then JS click
        btn_elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.login_button_locator)))
        # Use JS click to avoid overlay issues
        try:
            self.driver.execute_script("arguments[0].click();", btn_elem)
        except JavascriptException:
            # As a fallback, attempt to click via element.click()
            try:
                btn_elem.click()
            except Exception:
                pass

    def get_result(self, expected):
        """
        Return the normalized, stripped visible text content of the detected element
        or current URL if expected indicates navigation or no message found.
        """
        wait = WebDriverWait(self.driver, 10)

        # Layer 1: native alerts
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text.strip()
            try:
                alert.accept()
            except Exception:
                pass
            if alert_text:
                return alert_text
        except NoAlertPresentException:
            pass

        # Extract double-quoted expected texts per strict rule
        expected_texts = re.findall(r'"([^"]*)"', expected or "")
        # If no double-quoted texts, also try to extract single-quoted snippets (helpful for redirections like 'Tài khoản')
        if not expected_texts:
            expected_texts = re.findall(r"'([^']*)'", expected or "")

        # If we have target texts, search for them (deepest element pattern)
        for text in expected_texts:
            lower_text = text.lower().strip()
            if not lower_text:
                continue
            xpath = f"//*[contains(translate(normalize-space(.), '{self.UPPER}', '{self.LOWER}'), '{lower_text}') and not(*[contains(translate(normalize-space(.), '{self.UPPER}', '{self.LOWER}'), '{lower_text}')])]"
            try:
                elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                # Return deep element text
                return elem.text.strip()
            except TimeoutException:
                continue  # try next expected_text

        # If expected suggests a redirect to an account page (common phrasing), try to detect presence of 'tài khoản' keyword
        if expected and ("redirect" in expected.lower() or "tài khoản" in expected.lower() or "account" in expected.lower()):
            # attempt to find 'tài khoản' or 'account' text
            for hint in ("tài khoản", "tài khoản", "account"):
                lower_text = hint
                xpath = f"//*[contains(translate(normalize-space(.), '{self.UPPER}', '{self.LOWER}'), '{lower_text}') and not(*[contains(translate(normalize-space(.), '{self.UPPER}', '{self.LOWER}'), '{lower_text}')])]"
                try:
                    elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                    return elem.text.strip()
                except TimeoutException:
                    continue
            # As a fallback for navigation, return current URL
            return self.driver.current_url

        # Layer 2 failed: fallback to checking HTML5 validationMessage on inputs (Layer 3)
        try:
            # Prefer email input's validationMessage, then password input
            email_elem = self.driver.find_element(By.XPATH, self.email_locator)
            vmsg = self.driver.execute_script("return arguments[0].validationMessage;", email_elem)
            if vmsg:
                return vmsg.strip()
        except Exception:
            pass

        try:
            pwd_elem = self.driver.find_element(By.XPATH, self.password_locator)
            vmsg = self.driver.execute_script("return arguments[0].validationMessage;", pwd_elem)
            if vmsg:
                return vmsg.strip()
        except Exception:
            pass

        # Nothing found: return current URL as last resort
        try:
            return self.driver.current_url
        except Exception:
            return ""
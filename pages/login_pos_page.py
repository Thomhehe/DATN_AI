from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


class LoginPosPage:
    def __init__(self, driver):
        self.driver = driver
        # Dynamic locators with priority: visible text > placeholder > name > generic
        # Email / username input
        self.email_locator = (
            By.XPATH,
            "//input[@placeholder='Tên đăng nhập' or @placeholder='Email' or @name='username' or @name='email' or contains(@id,'email') or contains(@placeholder,'tên') or contains(@aria-label,'email')]"
        )
        # Password input
        self.password_locator = (
            By.XPATH,
            "//input[@placeholder='Mật khẩu' or @placeholder='Password' or @name='password' or contains(@id,'password') or contains(@aria-label,'password') or @type='password']"
        )
        # Login button: prioritize visible text variants
        self.login_button_locator = (
            By.XPATH,
            "//button[normalize-space()='Đăng nhập' or normalize-space()='Đăng nhập hệ thống' or normalize-space()='Login' or normalize-space()='Log in' or @type='submit' or contains(.,'Đăng nhập') or contains(.,'Login')]"
        )

    def perform_actions(self, email, password):
        # Wait for email field visibility and interact
        try:
            email_el = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.email_locator)
            )
        except TimeoutException:
            # As fallback try a generic input field (first input)
            try:
                email_el = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@type='text' or not(@type)]"))
                )
            except TimeoutException:
                email_el = None

        if email_el:
            try:
                email_el.clear()
            except WebDriverException:
                pass
            if email is not None and email != "":
                email_el.send_keys(email)

        # Wait for password field visibility and interact
        try:
            pwd_el = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.password_locator)
            )
        except TimeoutException:
            # fallback to any password input
            try:
                pwd_el = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@type='password']"))
                )
            except TimeoutException:
                pwd_el = None

        if pwd_el:
            try:
                pwd_el.clear()
            except WebDriverException:
                pass
            if password is not None and password != "":
                pwd_el.send_keys(password)

        # Click the login button
        try:
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.login_button_locator)
            )
            login_btn.click()
        except TimeoutException:
            # try to find clickable parent if button is an icon or hidden
            try:
                login_btn = self.driver.find_element(By.XPATH, "//button[@type='submit' or contains(.,'Đăng nhập') or contains(.,'Login')]")
                login_btn.click()
            except Exception:
                # last resort: try to submit the form containing the password field
                try:
                    form = None
                    if pwd_el:
                        form = pwd_el.find_element(By.XPATH, "./ancestor::form")
                    if not form and email_el:
                        form = email_el.find_element(By.XPATH, "./ancestor::form")
                    if form:
                        self.driver.execute_script("arguments[0].submit()", form)
                except Exception:
                    pass

    def get_result(self, expected):
        """
        Multi-layered Notification Detection Engine.
        Returns first detected notification text.
        Special-case: if expected appears to be a full URL (starts with http),
        detect navigation and return current URL.
        """
        # Capture initial URL to detect navigation
        try:
            initial_url = self.driver.current_url
        except Exception:
            initial_url = ""

        # If expected looks like a URL, wait briefly for navigation and return current URL
        if expected and isinstance(expected, str) and expected.strip().lower().startswith("http"):
            try:
                WebDriverWait(self.driver, 8).until(lambda d: d.current_url and d.current_url != initial_url)
            except Exception:
                # proceed anyway
                pass
            try:
                return self.driver.current_url
            except Exception:
                return ""

        # Layer 1: Native Alerts
        try:
            alert = WebDriverWait(self.driver, 2).until(EC.alert_is_present())
            try:
                text = alert.text
            except Exception:
                text = ""
            try:
                alert.dismiss()
            except Exception:
                pass
            if text:
                return text.strip()
        except TimeoutException:
            pass
        except Exception:
            pass

        # Layer 2: Toasts / Snackbars (fast, transient). Use short waits.
        toast_xpaths = [
            "//*[@role='alert' or @role='status']",
            "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'toast')]",
            "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'snackbar')]",
            "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'notification')]",
            "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'alert') and not(self::button)]",
            "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
        ]
        for xp in toast_xpaths:
            try:
                elements = WebDriverWait(self.driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, xp)))
            except TimeoutException:
                elements = []
            except Exception:
                elements = []
            for el in elements:
                try:
                    if el.is_displayed():
                        text = el.text.strip()
                        if text:
                            return text
                except Exception:
                    continue

        # Layer 3: Modals / Popups
        modal_xp = "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'modal-body') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'popup-content') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'dialog') or @role='dialog']"
        try:
            modals = self.driver.find_elements(By.XPATH, modal_xp)
        except Exception:
            modals = []
        for m in modals:
            try:
                if m.is_displayed():
                    txt = m.text.strip()
                    if txt:
                        return txt
            except Exception:
                continue

        # Layer 4: Inline validation / error messages
        inline_xp = "//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'text-danger') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'invalid-feedback') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'error') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'field-error') or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'help-block')]"
        try:
            inlines = self.driver.find_elements(By.XPATH, inline_xp)
        except Exception:
            inlines = []
        for e in inlines:
            try:
                if e.is_displayed():
                    t = e.text.strip()
                    if t:
                        return t
            except Exception:
                continue

        # Also check common elements near inputs (labels, small tags)
        adjacent_xp = "//input[(@type='text' or @type='email' or contains(@name,'user'))]/following-sibling::*[1] | //input[@type='password']/following-sibling::*[1]"
        try:
            adj = self.driver.find_elements(By.XPATH, adjacent_xp)
        except Exception:
            adj = []
        for a in adj:
            try:
                if a.is_displayed():
                    t = a.text.strip()
                    if t:
                        return t
            except Exception:
                continue

        # Layer 5: JS Runtime Analysis - HTML5 validationMessage
        try:
            # Try email and password elements
            candidates = []
            try:
                candidates.append(self.driver.find_element(*self.email_locator))
            except Exception:
                pass
            try:
                candidates.append(self.driver.find_element(*self.password_locator))
            except Exception:
                pass
            # Remove duplicates
            seen = set()
            for elem in candidates:
                try:
                    oid = elem.id
                except Exception:
                    oid = None
                if oid and oid in seen:
                    continue
                if oid:
                    seen.add(oid)
                try:
                    msg = self.driver.execute_script("return arguments[0].validationMessage || '';", elem)
                    if msg and msg.strip():
                        return msg.strip()
                except Exception:
                    continue
        except Exception:
            pass

        # Final heuristic: search for any visible text nodes that look like errors (strings in Vietnamese)
        heuristic_phrases = ["không được bỏ trống", "không hợp lệ", "sai", "vui lòng", "lỗi", "thành công"]
        try:
            bodies = self.driver.find_elements(By.XPATH, "//*[string-length(normalize-space(text()))>0]")
        except Exception:
            bodies = []
        for b in bodies[:50]:  # limit traversal
            try:
                if not b.is_displayed():
                    continue
                t = b.text.strip()
                if not t:
                    continue
                lower = t.lower()
                for ph in heuristic_phrases:
                    if ph in lower:
                        return t
            except Exception:
                continue

        # If nothing found, return empty string
        return ""
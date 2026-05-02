from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SuccessfulLoginPage:
    def __init__(self, driver):
        self.driver = driver
        # Broad input locators covering placeholder, name, aria-label, type, and class hints for email
        self.email_xpath = (
            "//input[("
            "translate(@type, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='email' or "
            "contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email') or "
            "contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email') or "
            "contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email') or "
            "contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email')"
            ")]"
        )
        # Broad input locators for password
        self.password_xpath = (
            "//input[("
            "translate(@type, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='password' or "
            "contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'password') or "
            "contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'password') or "
            "contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'password') or "
            "contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'password')"
            ")]"
        )
        # Universal login button XPath using the required robust pattern targeting 'đăng nhập'
        keyword = "đăng nhập"
        self.login_button_xpath = (
            f"//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            f"'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}')] | "
            f"//input[(@type='submit' or @type='button') and contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            f"'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}')] | "
            f"//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            f"'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}')] | "
            f"//*[contains(@class, 'btn') or contains(@class, 'button') or @role='button'][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            f"'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}') or contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            f"'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}') or contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ', "
            f"'abcdefghijklmnopqrstuvwxyzáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'), '{keyword}')]"
        )

    def perform_actions(self, email_value, password_value):
        # Step: wait for, clear, and input email
        email_elem = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, self.email_xpath))
        )
        email_elem.clear()
        # send_keys even if empty or whitespace to follow steps strictly
        email_elem.send_keys(email_value)

        # Step: wait for, clear, and input password
        password_elem = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, self.password_xpath))
        )
        password_elem.clear()
        password_elem.send_keys(password_value)

        # Step: click the login button using presence_of_element_located and JS click
        login_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, self.login_button_xpath))
        )
        self.driver.execute_script("arguments[0].click();", login_btn)

    def get_result(self, expected):
        # Layer 1: handle native alerts/dialogs
        try:
            alert = WebDriverWait(self.driver, 1).until(EC.alert_is_present())
            text = alert.text.strip()
            try:
                alert.dismiss()
            except:
                pass
            return text
        except:
            pass

        # If expected is empty string: wait for navigation (URL change) and return current URL
        if expected == "":
            start_url = self.driver.current_url
            try:
                WebDriverWait(self.driver, 10).until(lambda d: d.current_url != start_url)
            except:
                # timeout - no navigation occurred; still return current URL
                pass
            return self.driver.current_url

        # Layer 2: DOM text search for deepest element(s)
        def find_text(target_text):
            lower_text = target_text.lower()
            # Pattern that finds the deepest element containing the text (case-insensitive)
            xpath = (
                "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
                f"'{lower_text}') and not(*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{lower_text}')])]"
            )
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                el = self.driver.find_element(By.XPATH, xpath)
                return el.text.strip()
            except:
                return None

        # If expected is a list, check any
        if isinstance(expected, list):
            for exp in expected:
                res = find_text(exp)
                if res is not None and res != "":
                    return res
        else:
            res = find_text(expected)
            if res is not None and res != "":
                return res

        # Layer 3 fallback: HTML5 validationMessage from inputs
        try:
            email_elem = self.driver.find_element(By.XPATH, self.email_xpath)
            vmsg = self.driver.execute_script("return arguments[0].validationMessage;", email_elem)
            if vmsg and vmsg.strip():
                return vmsg.strip()
        except:
            pass

        try:
            pwd_elem = self.driver.find_element(By.XPATH, self.password_xpath)
            vmsg = self.driver.execute_script("return arguments[0].validationMessage;", pwd_elem)
            if vmsg and vmsg.strip():
                return vmsg.strip()
        except:
            pass

        # Nothing found
        return ""
from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        # locators (use HTML ids and css)
        self.email = self.page.locator("#customer_email")
        self.password = self.page.locator("#customer_password")
        self.submit = self.page.locator('form#customer_login input[type="submit"][value="Đăng nhập"]')
        # possible message containers inside the login form
        self.inline_span = self.page.locator('form#customer_login span.form-signup')
        self.form_messages = self.page.locator('form#customer_login .form-signup')

    def perform_actions(self, email_value, password_value):
        # fill email (fills with empty string to clear if needed)
        self.email.fill(email_value)
        self.password.fill(password_value)
        self.submit.click()

    def get_result(self, expected):
        # 1) Check visible inline span message inside the login form
        if self.inline_span.count() > 0:
            txt = self.inline_span.text_content() or ""
            txt = txt.strip()
            if txt:
                return txt
        # 2) Check any other form message container inside the login form
        if self.form_messages.count() > 0:
            txt = self.form_messages.first.text_content() or ""
            txt = txt.strip()
            if txt:
                return txt
        # 3) If no visible messages, check the email input's validationMessage (browser built-in)
        vm = self.email.evaluate("el => el.validationMessage")
        if vm:
            return vm
        # 4) No messages or validation messages found -> return current URL
        return self.page.url
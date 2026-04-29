import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get('https://app.easypos.vn/login')
time.sleep(2)

driver.find_element(By.XPATH, "//input[@name='username']").send_keys("demo")
driver.find_element(By.XPATH, "//input[@type='password']").send_keys("12345")
driver.find_element(By.XPATH, "//button[@type='submit']").click()

start = time.time()
try:
    alert = WebDriverWait(driver, 2).until(lambda d: d.switch_to.alert)
except:
    pass
print("Layer 1 took:", time.time() - start)

driver.quit()

import os
import shutil

def pytest_sessionfinish(session, exitstatus):
    os.system("allure generate allure-results -o allure-report --clean")

    if os.path.exists("allure-results"):
        shutil.rmtree("allure-results")
# import streamlit as st
#
# st.write("Hello test")

from selenium import webdriver

driver = webdriver.Chrome()
print(driver.capabilities)
driver.quit()
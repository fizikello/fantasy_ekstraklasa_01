import time

from selenium import webdriver
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
# driver = webdriver.Edge()
driver = webdriver.Chrome()

driver.get("https://fantasy.ekstraklasa.org/player/1221")

name = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/section/div/div[2]/div/h1").text
price = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]").text


print(f"name: {name}, price: {price}")

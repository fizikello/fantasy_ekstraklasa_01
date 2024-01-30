import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from secrets import Secrets
from marks import Marks

s = Secrets()
m = Marks()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
# driver = webdriver.Edge()
driver = webdriver.Chrome()

driver.get(s.url)
scratched_values = list()

for mark in m.marks.values():
    scratched_values.append(driver.find_element(By.XPATH, mark).text)



print(f"{scratched_values}")

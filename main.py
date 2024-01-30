import time

import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from hidden_values import Secrets
from marks import Marks


s = Secrets()
m = Marks()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
# driver = webdriver.Edge()
driver = webdriver.Chrome()

driver.get(s.url)
scratched_values = list()

for key, mark in m.marks.items():
    try:
        scratched_values.append(driver.find_element(By.XPATH, mark).text)
    except NoSuchElementException:
        print(f"Not found {key} markup")

try:
    table_xpath = driver.find_element(By.XPATH, m.table)
    rows = table_xpath.find_elements(By.TAG_NAME, "tr")

    data = []
    col_data = rows[0].find_elements(By.TAG_NAME, "td")
    column_names = [col.text for col in col_data]
    column_names[-3] = "Yellow_Cards"
    column_names[-2] = "Red_Cards"

    for row in rows[1:]:
        cols = row.find_elements(By.TAG_NAME, "td")
        row_data = [col.text for col in cols]
        data.append(row_data)
except NoSuchElementException:
    print("table not found")

df = pd.DataFrame(data, columns=column_names)
print(df)

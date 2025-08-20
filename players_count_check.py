from bs4 import BeautifulSoup
import requests
import warnings
import re
from collections import Counter
import time
from datetime import datetime
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from hidden_values import Secrets
import psycopg2
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import requests
import warnings
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options

#html = "https://fantasy.ekstraklasa.org/user-team/view/tragarze-taktyki/5"

MAIN_URL = "https://fantasy.ekstraklasa.org/"
MAIN_PATH = "C:\\Users\\arek9\\Documents\\fantasy\\team_check\\"
GAMEWEEK_RANGE = list(range(1,6))
only_analyse = True

def create_url(team, gameweek, main_url=MAIN_URL):
    #print(main_url + "user-team/view/" + team + '/' + str(gameweek))
    return main_url + "user-team/view/" + team + '/' + str(gameweek)

def create_filename(team, gameweek, main_url=MAIN_URL):
    string_gameweek = str(gameweek) if gameweek > 9 else "0" + str(gameweek)
    return MAIN_PATH + "\\" + team + "_" + string_gameweek + ".html"

def open_url():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    start_date = time.time()
    driver.get(s.login_url)
    button_cookies = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.LINK_TEXT, "ZAPISZ"))).click()
    # live section
    button_login = WebDriverWait(driver, 100).until(EC.element_to_be_clickable(
        (By.LINK_TEXT, "ZALOGUJ SIĘ"))).click()

    username = driver.find_element(By.ID,
                                   "mat-input-0")
    username.send_keys(s.fantasy_login)
    password = driver.find_element(By.ID,
                                   "mat-input-1")
    password.send_keys(s.fantasy_password)

    button_login = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
        (By.CLASS_NAME, "mdc-button__label"))).click()

    time.sleep(1) # check to load -> test second loading page
    next_link = MAIN_URL
    driver.get(next_link)
    print(f'response from {next_link}')
    time.sleep(5)

def save_html(url, filename):
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    with open(filename, "w", encoding="utf-8") as file:
        file.write(str(soup))

# TODO 1: login to main page
# TODO 2: get to your league's page
# TODO 3: get all teams
# TODO 5: go to page and save html

s = Secrets()
TEAMS_NAMES = s.teams

if not only_analyse:
    driver = webdriver.Chrome()
    open_url()

    for team in tqdm(TEAMS_NAMES):
        for gw in GAMEWEEK_RANGE:
            driver.get(create_url(team=team, gameweek=gw))
            filename = create_filename(team=team, gameweek=gw)
            time.sleep(2)
            save_html(create_url(team=team, gameweek=gw), filename)

    driver.quit()

for team in TEAMS_NAMES:
    for gw in GAMEWEEK_RANGE:
        filename = create_filename(team=team, gameweek=gw)
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        clubs = []

     # znajdź wszystkie div.player
        for div in soup.select("div.player"):
            style = div.get("style", "")
            match = re.search(r"/kits/25-26/(\d+_[^.]+)\.png", style)
            if match:
                club_code = match.group(1)  # np. '02_termalica_nieciecza1'
                clubs.append(club_code)
        clubs.sort()

     # policz wystąpienia
        counts = Counter(clubs)

        #print("Wszystkie kluby:")
        #print(clubs)

        for club, cnt in counts.items():
            if cnt > 1:
                print(f"drużyna: {team}, kolejka: {gw} ")
                print("Powtarzające się:")
                print(f"{club}: {cnt} razy")
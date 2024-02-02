import time
from datetime import date
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from hidden_values import Secrets
from marks import Marks
import psycopg2

get_real_data = False

def add_players_to_database(row_data):
    try:
        connection = psycopg2.connect(dbname=s.dbname, user=s.user, password=s.password, host=s.host, port=s.port)
        # print(f"Connected to the database {s.dbname}")
        cursor = connection.cursor()
        sql_command = f'INSERT INTO players ("ID", "LAST_NAME", "YOUNG_PLAYER", "UPDATE_DATE") VALUES (%s, %s, %s, %s);'
        cursor.execute(sql_command, row_data)
        connection.commit()


    except psycopg2.Error as e:
        print(f"Unable to connect to the database {s.dbname}")
        print(e)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
           # print(f"Connection closed {s.dbname}")


def update_players_to_database(row_data):
    try:
        connection = psycopg2.connect(dbname=s.dbname, user=s.user, password=s.password, host=s.host, port=s.port)
        # print(f"Connected to the database {s.dbname}")
        cursor = connection.cursor()
        sql_command = f'UPDATE players SET "LAST_NAME"= %s, "YOUNG_PLAYER"=%s, "UPDATE_DATE"=%s WHERE "ID"=%s;'
        cursor.execute(sql_command, row_data)
        connection.commit()
        #sql_command = "SELECT * FROM players;"
        #cursor.execute(sql_command)
        #results = cursor.fetchall()
        #for row in results:
        #    print(row)

    except psycopg2.Error as e:
        print(f"Unable to connect to the database {s.dbname}")
        print(e)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            #print(f"Connection closed {s.dbname}")

def get_players_from_database():

    try:
        connection = psycopg2.connect(dbname=s.dbname, user=s.user, password=s.password, host=s.host, port=s.port)
        print(f"Connected to the database {s.dbname}")
        cursor = connection.cursor()
        sql_command = 'SELECT DISTINCT "ID" FROM players;'
        cursor.execute(sql_command)
        results = [entry[0] for entry in cursor.fetchall()]
        return results

    except psycopg2.Error as e:
        print(f"Unable to connect to the database {s.dbname}")
        print(e)
        return list()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print(f"Connection closed {s.dbname}")

def connect_to_database():
    try:
        connection = psycopg2.connect(dbname=s.dbname, user=s.user, password=s.password, host=s.host, port=s.port)
        print(f"Connected to the database {s.dbname}")
        cursor = connection.cursor()
        sql_command = "SELECT * FROM players;"
        cursor.execute(sql_command)
        results = cursor.fetchall()
        for row in results:
            print(row)

        test_row = (8, 'test player', 'false')
        sql_command = f'INSERT INTO players ("ID", "LAST_NAME", "YOUNG_PLAYER") VALUES (%s, %s, %s)';
        cursor.execute(sql_command, test_row)
        connection.commit()
        sql_command = "SELECT * FROM players;"
        cursor.execute(sql_command)
        results = cursor.fetchall()
        for row in results:
            print(row)

    except psycopg2.Error as e:
        print(f"Unable to connect to the database {s.dbname}")
        print(e)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print(f"Connection closed {s.dbname}")


def get_new_players():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    # driver = webdriver.Edge()
    driver = webdriver.Chrome()
    start_date = time.time()
    driver.get(s.login_url)
    # test section
    # button_login = driver.find_element(By.CLASS_NAME,  ".btn btn-tertiary login btn-block pull-right")

    # live section
    button_login = WebDriverWait(driver, 50).until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div[1]/div[2]/header/div/div/div/div[2]/div/div/div[1]/a[1]"))).click()
    username = driver.find_element(By.XPATH,
                                   "/html/body/app-root/app-sign-in/div/app-sign-in-form/form/mat-form-field[1]/div/div[1]/div/input")
    username.send_keys(s.fantasy_login)
    password = driver.find_element(By.XPATH,
                                   "/html/body/app-root/app-sign-in/div/app-sign-in-form/form/mat-form-field[2]/div/div[1]/div[1]/input")
    password.send_keys(s.fantasy_password)
    driver.find_element(By.XPATH, "/html/body/app-root/app-sign-in/div/app-sign-in-form/form/button[1]").click()
    make_transfer_button = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH,
                                                                                       "/html/body/div[1]/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/div/button"))).click()
    players_table = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[1]")
    # players_table = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/div/button")))
    time.sleep(5)
    players_list = []
    rows = players_table.find_elements(By.TAG_NAME, "tr")
    for row in rows[1:]:
        element_button = row.find_element(By.CSS_SELECTOR, 'button[data-action="player-info"]')
        data_info_id = element_button.get_attribute('data-info-id')
        players_list.append(f"{row.text}:{data_info_id}")

    print(f"get_players_id time: {time.time() - start_date}")
    time.sleep(1)
    driver.quit()

    print(f"Liczba graczy: {len(players_list)}")
    return players_list


def scrap_data():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    # driver = webdriver.Edge()
    driver = webdriver.Chrome()
    start_time = time.time()
    for key, mark in m.marks.items():
        try:
            scratched_values.append(driver.find_element(By.XPATH, mark).text)
        except NoSuchElementException:
            print(f"Not found {key} markup")
            exit()

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

    print(column_names)
    print(f"time: {time.time() - start_time}")
    return pd.DataFrame(data, columns=column_names)


def get_test_list():

    with open('test_players.txt', 'r', encoding='utf-8') as file:
        file_content = file.read().splitlines()

    restored_list = list(map(str, file_content))
    return restored_list


def compare_lists(current_list, archive_list):
    unique_values = set(current_list) - set(archive_list)
    result_list = list(unique_values)
    return result_list


# connect_to_database()
m = Marks()
s = Secrets()
#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_experimental_option("detach", True)
# driver = webdriver.Edge()
#driver = webdriver.Chrome()

archive_players_list = get_players_from_database()
print(archive_players_list)
current_players_list = get_new_players() if get_real_data else get_test_list()
print(current_players_list)

current_indexes = [int(row.split(':')[1]) for row in current_players_list]
print(current_indexes)

cp = compare_lists(current_list=current_indexes, archive_list=archive_players_list)

# transform current_players_list -> SHORT_NAME, IS_YOUNG, ID
current_players = [(re.split(r'\d', row)[0].split("(")[0][:-1], True if "(M)" in row else False, int(row.split(':')[1])) for row in current_players_list]
print(current_players)

today = date.today()
formatted_date = today.strftime('%Y%m%d')
print(formatted_date)


for player in current_players:
    if player[2] in cp:
        add_players_to_database([player[2], player[0], player[1], formatted_date])
    else:
        update_players_to_database([player[0], player[1], formatted_date, player[2]])



#driver.get(s.test_url)
scratched_values = list()

"""
df = scrap_data()
print(df)
"""
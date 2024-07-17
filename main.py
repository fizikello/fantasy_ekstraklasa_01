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
from marks import Marks
import psycopg2
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import requests
import warnings
from selenium.webdriver.chrome.options import Options

get_real_data = True

def update_scrap_performance(df):
    engine = create_engine(f'postgresql+psycopg2://{s.user}:{s.password}@{s.host}:{s.port}/{s.dbname}')
    df.to_sql(name='scrap_performance', con=engine, if_exists='append', index=False)

def add_or_update_details(df):

    engine = create_engine(f'postgresql+psycopg2://{s.user}:{s.password}@{s.host}:{s.port}/{s.dbname}')
    df.to_sql(name='details_t01', con=engine, if_exists='append', index=False)
    print("details_ok")


def add_or_update_popularity(df):

    engine = create_engine(f'postgresql+psycopg2://{s.user}:{s.password}@{s.host}:{s.port}/{s.dbname}')
    df.to_sql(name='popularity', con=engine, if_exists='append', index=False)


def add_details_to_database(row_data):
    try:
        connection = psycopg2.connect(dbname=s.dbname, user=s.user, password=s.password, host=s.host, port=s.port)
        # print(f"Connected to the database {s.dbname}")
        cursor = connection.cursor()
        sql_command = f'INSERT INTO details_t01 ("WEEKDAY","OPPOSITE_TEAM","MINUTES_PLAYED","GOALS_SCORED","ASSISTS",' \
                      f'"ASSISTS_LOTTO","OWN_GOALS","PENALTIES_SCORED","PENALTIES_GAINED","PENALTIES_LOST",' \
                      f'"PENALTIES_MISSED","PENALTIES_SAVED","BEST_XI","YELLOW_CARDS","RED_CARDS","POINTS",' \
                      f'"PLAYER_INDEX", "DATE") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
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

        if cursor.rowcount == 0:
            return False

        return True
        #sql_command = "SELECT * FROM players;"
        #cursor.execute(sql_command)
        #results = cursor.fetchall()
        #for row in results:
        #    print(row)

    except psycopg2.Error as e:
        print(f"Unable to connect to the database {s.dbname}")
        print(e)
        return False

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
        sql_command = 'SELECT DISTINCT "ID" from players where "UPDATE_DATE" = (SELECT MAX("UPDATE_DATE") as m_ FROM players);'
        # sql_command = 'SELECT DISTINCT "ID" from players;  # where "UPDATE_DATE" = (SELECT MAX("UPDATE_DATE") as m_ FROM players);'
        cursor.execute(sql_command)
        results = [entry[0] for entry in cursor.fetchall()]
        print(f"archive player list equals {len(results)} players")
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
    # chrome_options.add_argument('window-size=1920x1080')
    # driver = webdriver.Edge()
    # driver = webdriver.Chrome()
    #driver.set_window_size(690,912)
    start_date = time.time()
    driver.get(s.login_url)
    # test section
    # button_login = driver.find_element(By.CLASS_NAME,  ".btn btn-tertiary login btn-block pull-right")

    # live section
    button_login = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div[1]/div[2]/header/div/div/div/div[2]/div/div/div[1]/a[1]"))).click()

    #button_login = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,
    #                                                            "//button[contains(text(),'Zaloguj się')]"))).click()

    username = driver.find_element(By.XPATH,
                                   "/html/body/app-root/app-sign-in/div/app-sign-in-form/form/mat-form-field[1]/div/div[1]/div/input")
    username.send_keys(s.fantasy_login)
    password = driver.find_element(By.XPATH,
                                   "/html/body/app-root/app-sign-in/div/app-sign-in-form/form/mat-form-field[2]/div/div[1]/div[1]/input")
    password.send_keys(s.fantasy_password)
    driver.find_element(By.XPATH, "/html/body/app-root/app-sign-in/div/app-sign-in-form/form/button[1]").click()

    time.sleep(5) # check to load -> test second loading page
    next_link = s.login_url + "user-team/transfer"
    driver.get(next_link)
    print(f'response from {next_link}')
    driver.get(next_link)

    check_player_table = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[1]")))
    players_table = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[1]")
    time.sleep(5)
    players_list = []
    rows = players_table.find_elements(By.TAG_NAME, "tr")
    for row in rows[1:]:
        element_button = row.find_element(By.CSS_SELECTOR, 'button[data-action="player-info"]')
        data_info_id = element_button.get_attribute('data-info-id')
        players_list.append(f"{row.text}:{data_info_id}")

    print(f"get_players_id time: {round(time.time() - start_date, 2)}")
    driver.quit()

    print(f"# of players: {len(players_list)}")
    return players_list


def scrap_data(path):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_experimental_option("detach", True)
    # driver = webdriver.Edge()
    driver = webdriver.Chrome()
    driver.get(path)
    scrapped_values = dict()
    start_time = time.time()
    for key, mark in m.marks.items():
        try:
            # scrapped_values[key] = driver.find_element(By.XPATH, mark).text
            scrapped_values[key] = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, mark))).text
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

        # first row contains header
        for row in rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "td")
            row_data = [col.text for col in cols]
            # add new table -> archive_stats
            if len(row_data) == 15:
                row_data.insert(1, 'EMPTY')
            data.append(row_data)

    except NoSuchElementException:
        print("table not found")

    spdf = pd.DataFrame(data, columns=column_names)

    return spdf, scrapped_values


def scrap_data_b(path, index):
    warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    response = requests.get(path, verify=False)
    if response.status_code != 200:
        print("Failed to fetch the page")
        return None, None

    soup = BeautifulSoup(response.content, 'html.parser')
    scrapped_values = dict()
    scrapped_values['club_position'] = soup.find('div', class_='post-meta').text.strip()
    scrapped_values['name'] = soup.find('h1').text.strip()
    prize_check = soup.find_all('td', class_='sec')
    scrapped_values['price'] = prize_check[0].text.strip()
    scrapped_values['popularity'] = prize_check[1].text.strip()
    scrapped_values['country'] = prize_check[2].text.strip()
    scrapped_values['previous_club'] = prize_check[3].text.strip()
    numbers_check = soup.find_all('div', class_='col-sm-7 col-xs-7 text-left')
    scrapped_values['sum_points'] = numbers_check[0].text.strip().split('\n')[0]
    scrapped_values['sum_goals'] = numbers_check[1].text.strip().split('\n')[0]
    scrapped_values['sum_assists'] = numbers_check[2].text.strip().split('\n')[0]

    data = []
    table_rows = soup.find_all('tr')

    column_names = []
    for row in table_rows[4:5]:
        cells = row.find_all('td')
        column_names = [cell.get_text(strip=True) for cell in cells]
    column_names[-3] = "Yellow_Cards"
    column_names[-2] = "Red_Cards"

    for row in table_rows[5:]:
        cells = row.find_all('td')
        row_data = [cell.get_text(strip=True) for cell in cells]
        if len(row_data) == 15:
            row_data.insert(1, 'EMPTY')
        data.append(row_data)

    spdf = pd.DataFrame(data, columns=column_names)
    return spdf, scrapped_values

def get_test_list():

    with open('test_players.txt', 'r', encoding='utf-8') as file:
        file_content = file.read().splitlines()

    restored_list = list(map(str, file_content))
    return restored_list


def compare_lists(current_list, archive_list):
    unique_values = set(current_list) - set(archive_list)
    result_list = list(unique_values)
    return result_list


def check_number_of_players(players_list):
    if len(players_list) < 400:
        print(f"Only {len(players_list)} found")
        exit()


def progress_bar(current, total, bar_length=20):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '

    return f'Progress: [{arrow}{padding}] {int(fraction*100)}% '


# connect_to_database()
m = Marks()
s = Secrets()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
# driver = webdriver.Edge()
driver = webdriver.Chrome()
#driver.set_window_size(1300, 800)
archive_players_list = get_players_from_database()
current_player_list = []
current_player_indexes = []
archive_loader = False
try:
    current_players_list = get_new_players() if get_real_data else get_test_list()
    current_indexes = [int(row.split(':')[1]) for row in current_players_list]
except (TimeoutException, NoSuchElementException) as e1:
    archive_loader = True
    current_indexes = archive_players_list
    print("Could not to update update transfer list. Archive list has been loaded.")

if archive_loader and input("Continue? (Y/n)") != "Y":
    exit()

cp = compare_lists(current_list=current_indexes, archive_list=archive_players_list)

# transform current_players_list -> SHORT_NAME, IS_YOUNG, ID
current_players = []
if archive_loader is False:
    current_players = [(re.split(r'\d', row)[0].split("(")[0][:-1], True if "(M)" in row else False, int(row.split(':')[1])) for row in current_players_list]

if get_real_data and archive_loader is False:
    check_number_of_players(current_players)

today = datetime.now()
formatted_date = today.strftime('%Y%m%d%H%M')
# formatted_date = today.strftime('%Y%m%d')

df = pd.DataFrame()
df2 = pd.DataFrame(columns=['name', 'price', 'club_position', 'popularity', 'country', 'previous_club', 'sum_points', 'sum_goals', 'sum_assists'])
time_df = pd.DataFrame(columns=['PLAYER_ID', 'TIME', 'DATE', 'TECHNOLOGY'])

get_real_data_2 = True
if get_real_data_2:
    for index in current_indexes:
        # print(f'{current_indexes.index(index)} : {index} ')
        print(f"\r{index} : {progress_bar(current_indexes.index(index), len(current_indexes))}", end='', flush=True)
        path = s.login_url + "player/" + str(index)
        time_0 = time.time()
        tmp_df, tmp_pop_database = scrap_data_b(path, index)
        time_df.loc[len(time_df)] = [index, time.time() - time_0, formatted_date, 'beautiful soup']
        new_column_names = {'Kol.':'WEEKDAY', 'Vs':"OPPOSITE_TEAM", 'Min.':"MINUTES_PLAYED", 'Br.':"GOALS_SCORED",
                            'As.':'ASSISTS', 'AL.':"ASSISTS_LOTTO", 'Br. sam.':'OWN_GOALS', 'Kar. wyk.':"PENALTIES_SCORED", 'Kar. wyw.':'PENALTIES_GAINED',
                            'Kar. spo.':'PENALTIES_LOST', 'Kar. zmar.':'PENALTIES_MISSED', 'Kar. obr.':'PENALTIES_SAVED', '11 kol.':"BEST_XI",
                            'Yellow_Cards':"YELLOW_CARDS", 'Red_Cards':'RED_CARDS', 'Pkt.':"POINTS"}
        tmp_df=tmp_df.rename(columns=new_column_names)
        tmp_df['PLAYER_INDEX'] = index
        tmp_df['BEST_XI'] = 0
        tmp_df["DATE"] = formatted_date
        df = pd.concat([df, tmp_df], ignore_index=True)
        tmp_pop_database["PLAYER_INDEX"] = int(index)
        df2 = pd.concat([df2, pd.DataFrame(tmp_pop_database, index=[index])], ignore_index=True)

else:
    df = pd.read_csv(filepath_or_buffer="dataframe-test.csv")

if not get_real_data:
    df.to_csv("dataframe-test.csv", index=False)

# transform
print("Cleaning data")
df2[["CLUB", "POSITION"]] = df2['club_position'].str.split(',', expand=True)
df2["POSITION"] = df2["POSITION"].str.strip()
df2["POPULARITY"] = df2['popularity'].str.split(')', n=1).str[0]
df2["POPULARITY"] = df2['POPULARITY'].str.split('(', n=1).str[1]
df2["DATE"] = formatted_date
del df2["popularity"]
del df2["club_position"]
df2=df2.rename(columns={"name": "NAME", "price" : "PRICE", "country" : "COUNTRY", "previous_club" : "PREVIOUS_CLUB", "sum_points" : "SUM_POINTS",
                        "sum_goals" : "SUM_GOALS", "sum_assists" : "SUM_ASSISSTS"})
df2.to_csv("dataframe2-test.csv", index=False)

# LOAD
print("Loading data to database")
if get_real_data:

    """for player in current_players:
        if player[2] in cp:
            add_players_to_database([player[2], player[0], player[1], formatted_date])
        else:
            update_players_to_database([player[0], player[1], formatted_date, player[2]])
            """
    for player in current_players:
        update_successful = update_players_to_database([player[0], player[1], formatted_date, player[2]])

        if not update_successful:
            add_players_to_database([player[2], player[0], player[1], formatted_date])

    add_or_update_details(df)
    add_or_update_popularity(df2)
    print("popularity ok")
    update_scrap_performance(time_df)
    print("scrap performance stats ok")

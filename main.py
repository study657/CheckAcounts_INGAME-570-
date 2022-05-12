import steam.webauth as wa
from bs4 import BeautifulSoup
import requests
import datetime
import time
import re

Accounts_with_time = []
Accounts_without_time_INGAME = []
Accounts_without_SESSION_INGAME = []
Statistic_info = []

with open("Accounts.txt", "r") as file:
    for line in file:
        loginAndPass = re.split(':', line.strip(), maxsplit=0)

        user = wa.WebAuth(loginAndPass[0])
        session = user.cli_login(loginAndPass[1])
        print(loginAndPass[0])

        response = requests.get('https://steamcommunity.com/profiles/' + str(user.steam_id) + '/gcpd/570/?category=Account&tab=GameSessionData', cookies=user.session.cookies)

        if response.status_code == 200:
            text = response.text.encode()
            with open('parsing_file.txt', 'w') as file:
                file.write(str(text))

            positions = None

            with open('parsing_file.txt', "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                table = soup.find('table', class_=('generic_kv_table'))
                if table != None:
                    trs = table.find_all('tr')
                    for tr in trs:
                        positions = tr.find_all('td')
                    
                    exiting_game = positions[0].get_text()
                    data_Year_and_Month_exiting_game = re.split('-', exiting_game.strip(), maxsplit=0)
                    day_exiting_game = re.split('\s', data_Year_and_Month_exiting_game[2].strip(), maxsplit=0)
                    time_exiting_game = re.split(':', day_exiting_game[1].strip(), maxsplit=0)

                    logged_into_game = positions[2].get_text()
                    data_Year_and_Month_logged_into_game = re.split('-', logged_into_game.strip(), maxsplit=0)
                    day_logged_into_game = re.split('\s', data_Year_and_Month_logged_into_game[2].strip(), maxsplit=0)
                    time_logged_into_game = re.split(':', day_logged_into_game[1].strip(), maxsplit=0)

                    data_exiting_game = datetime.datetime(int(data_Year_and_Month_exiting_game[0]), int(data_Year_and_Month_exiting_game[1]), int(day_exiting_game[0]), int(time_exiting_game[0]), int(time_exiting_game[1]), int(time_exiting_game[2]))
                    data_logged_into_game = datetime.datetime(int(data_Year_and_Month_logged_into_game[0]), int(data_Year_and_Month_logged_into_game[1]), int(day_logged_into_game[0]), int(time_logged_into_game[0]), int(time_logged_into_game[1]), int(time_logged_into_game[2]))
                    
                    delta = data_exiting_game - data_logged_into_game

                    seconds = delta.total_seconds()
                    minutes = seconds // 60
                    seconds = (seconds % 60)

                    if minutes > 10:
                        Accounts_with_time.append(loginAndPass[0] + ':' + loginAndPass[1])

                    if minutes < 10:
                        Accounts_without_time_INGAME.append(loginAndPass[0] + ':' + loginAndPass[1])

                    Statistic_info.append({
                        'account': loginAndPass[0] + ':' + loginAndPass[1],
                        'time_inGame_minutes': minutes,
                        'time_inGame_seconds': seconds,
                    })
                else:
                    Accounts_without_SESSION_INGAME.append(loginAndPass[0] + ':' + loginAndPass[1])
        time.sleep(3)

with open('Accounts_with_time.txt', "w") as file:
    file.writelines("%s\n" % line for line in Accounts_with_time)

with open('Accounts_without_time_INGAME.txt', "w") as file:
    file.writelines("%s\n" % line for line in Accounts_without_time_INGAME)

with open('Accounts_without_SESSION_INGAME.txt', "w") as file:
    file.writelines("%s\n" % line for line in Accounts_without_SESSION_INGAME)

with open('Statistic.txt', "w") as file:
    for item in Statistic_info:
        file.writelines('Аккаунт ' + item['account'] + ' провел в игре ' + str(item['time_inGame_minutes']) + ' минут ' + str(item['time_inGame_seconds']) + ' секунд' + '\n')

print('Ножки завершили свою работу^_^')
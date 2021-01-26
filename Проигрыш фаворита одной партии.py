from selenium import webdriver
import time
import traceback
from bs4 import BeautifulSoup
from functools import wraps
from threading import Timer
import requests
import json
import datetime
from ast import literal_eval as make_list

URL = 'https://api.telegram.org/bot' + '923504923:AAHGPj3NCGLeRUnTSCsWD_udAwPXxiNtO0c' + '/'
chatID = '-1001439707933'

  
#PROXY = '81.201.60.130:80' # только HTTPS прокси

#proxies = {
#  "https": "https://" + PROXY
#}

chrome_option = webdriver.ChromeOptions()
#chrome_option.add_argument('--proxy-server=%s' % PROXY)
chrome_option.add_argument('disable-infobars')
driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_option)
driver.get('https://1xstavka.ru/live/Table-Tennis/')

def periodic(delay):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            f(*args, **kwargs)
            Timer(delay, wrapper, args=args, kwargs=kwargs).start()
        return wrapper
    return decorator

def write_file(link, file):
    file = file+'.txt'
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            if str(link) in line:
                link = ""
                return False
                break
        if link:
            return True

def write_file2(link, file):
    file = file+'.txt'
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            if str(link) in line:
                link = ""
                return False
                break
        if link:
            f.close()
            with open(file, 'a', encoding='utf-8') as f:
                f.writelines(str(link) +"\n")
                return True

@periodic(5)
def main():
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        matches = soup.find_all('div', 'c-events__item_col')
        for match in matches:
            try:
                name = match.find('span', 'c-events__teams').get_text().strip()
                score1 = match.find('span', 'c-events-scoreboard__cell--all').get_text().strip()
                score2 = match.find_all('span', 'c-events-scoreboard__cell--all')[1].get_text().strip()
                coef1 = match.find('div', 'c-bets').find_all('class', class_='c-bets__bet c-bets__bet_coef c-bets__bet_sm')[0].get_text().strip()
                coef2 = match.find('div', 'c-bets').find_all('class', class_='c-bets__bet c-bets__bet_coef c-bets__bet_sm')[2].get_text().strip()
                link = match.find('a', 'c-events__name').get('href')
                link = 'https://1xstavka.ru/' + link
                print(name, score1, score2, coef1, coef2)

                result = write_file(link, 'prematch_coefs1') #запись в файл с пре-кэфами 
                text = link, coef1, coef2
                if(result):
                    with open('prematch_coefs1.txt', 'a', encoding='utf-8') as f:
                        f.writelines(str(text) +"\n")

                if(score1 == '0') and ((score2 == '1') or (score2 == '2')):
                    with open('prematch_coefs1.txt', 'r', encoding='utf-8') as f:
                        for line in f:
                            if(link in line):
                                cur_lst = make_list(line)
                                prematch_coef1 = cur_lst[1]
                                prematch_coef2 = cur_lst[2]
                                if(coef1 != '-') and (coef2 != '-')  and (prematch_coef1 != '-') :
                                    if(float(coef1) > 1.8) and (1.1 <= float(prematch_coef1) <= 1.5):
                                        result = write_file2(link, 'signals1')
                                        if(result):
                                            send_message(chatID, 'Алгоритм 1.1\n' + str(name) + '\nКФ до матча: ' + str(prematch_coef1) + ' - ' + str(prematch_coef2) + '\nLive КФ: ' + str(coef1) + ' - ' + str(coef2) + '\nРекомендация:' + ' Победа в следующей партии ', link)

                if(score2 == '0') and ((score1 == '1') or (score1 == '2')):
                    with open('prematch_coefs1.txt', 'r', encoding='utf-8') as f:
                        for line in f:
                            if(link in line):
                                cur_lst = make_list(line)
                                prematch_coef1 = cur_lst[1]
                                prematch_coef2 = cur_lst[2]
                                if(coef1 != '-') and (coef2 != '-') and (prematch_coef2 != '-'):
                                    if(float(coef2) > 1.8) and (1.1 <= float(prematch_coef2) <= 1.5):
                                        result = write_file2(link, 'signals1')
                                        if(result):
                                            send_message(chatID, 'Алгоритм 1.1\n' + str(name) + '\nКФ до матча: ' + str(prematch_coef1) + ' - ' + str(prematch_coef2) + '\nLive КФ: ' + str(coef1) + ' - ' + str(coef2) + '\nРекомендация:' + ' Победа в следующей партии ', link)
            except Exception as e:
                print('Ошибка:\n', traceback.format_exc()) 
    except Exception as e:
        print('Ошибка:\n', traceback.format_exc()) 


def send_message(chat_id, text, link):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text )
    #reply_markup = {'inline_keyboard': [[{'text': 'Матч в 1хBet', 'url': link}]]}
    #data = {'reply_markup': json.dumps(reply_markup)}
    requests.post(url)


@periodic(300)
def reload():
    driver.get('https://1xstavka.ru/live/Table-Tennis/')


if __name__ == '__main__':
    reload()
    main()

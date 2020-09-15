import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

FORMAT = u'%(filename)s[LINE:%(lineno)d]#%(levelname)-8s[%(asctime)s]%(message)s'
logging.basicConfig(filename='sample.log', format=FORMAT, level=logging.INFO)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRACTICUM_API_URL = 'https://praktikum.yandex.ru/api'
METHOD_URL = '/user_api/homework_statuses/'
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework.get('status') == 'approved':
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        )
    else:
        return 'Что то поломалось =('
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        return 'Дата задана неверно'
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            (PRACTICUM_API_URL+METHOD_URL),
            params=params,
            headers=headers)
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка запроса{homework_statuses}: {e}')
        None
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()

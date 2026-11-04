import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv, find_dotenv
from typing import Any, Dict, List, Optional
import time

load_dotenv(find_dotenv(), encoding='utf-16')
YANDEX_TOKEN = os.getenv('YANDEX_WEATHER_TOKEN')
token = os.getenv('TOKEN')
BASE_URL = f'https://api.telegram.org/bot{token}'


def get_me() -> Optional[Dict[str, Any]]:
    """
    Проверяет работоспособность бота через Telegram API
    getMe. Делает get-запрос, и возвращает ответ в виде json.
    Если произошла ошибка сети, возвращает None.
    """
    url = f'{BASE_URL}/getMe'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            return None
        if not data.get('ok'):
            print('Ошибка в getMe', data)
        return data
    except Exception as e:
        print('Ошибка в getMe: ', e)
        return None


def send_message(chat_id: str | int, text: str) -> None:
    """
    Отправляет сообщение в чат с помощью метода sendMessage.
    Делает post-запрос к sendMessage, передавая chat_id
    и text (то что нужно отправить) в json-е.
    """
    url = f'{BASE_URL}/sendMessage'
    try:
        resp = requests.post(url, json={'chat_id': chat_id,
                                        'text': text}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data.get('ok'):
            print('Ошибка sendMessage', data)
    except Exception as e:
        print('Ошибка в sendMessage ', e)


def get_updates(offset: int | None = None, timeout: int = 30) \
        -> List[Dict[str, Any]]:
    """
    Получает обновления для бота через getUpdates. Использует
    timeout для long polling, и благодаря этому сервер может держать
    соединение открытым в ожидании новых сообщений.
    """
    url = f'{BASE_URL}/getUpdates'
    params = {'timeout': timeout}
    if offset is not None:
        params['offset'] = offset
    try:
        resp = requests.get(url, params=params, timeout=timeout+5)
        resp.raise_for_status()
        data = resp.json()
        if not data.get('ok'):
            print('Ошибка getUpdates')
            return []
        result = data.get('result', [])
        if not isinstance(result, list):
            return []
        return result
    except Exception as e:
        print('Ошибка getUpdates: ', e)
        return []


def get_quotes() -> str:
    """
    Скрапит случайную цитату. С помощью get-запроса получает содержимое
    https://citaty.info/random, парсит HTML через BeautifulSoup,
    извлекает саму цитату и источник (если есть)
    """
    url = 'https://citaty.info/random'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception:
        return 'Не удалось получить цитату из-за ошибки в сети'
    html = resp.text
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.select_one('div.random__quote')
    if not block:
        return 'Не удалось найти цитату'
    quote = block.select_one('.field-name-body p')
    if quote:
        quote_text = quote.get_text(' ', strip=True)
    else:
        quote_text = ''
    source = block.select_one('.quote__source a')
    if source:
        source_text = source.get_text(' ', strip=True)
    else:
        source_text = ''
    if not quote_text:
        return 'Пустая цитата'
    parts = [f'"{quote_text}"']
    if source_text:
        parts.append(f'{source_text}')
    return '\n'.join(parts)


def main() -> None:
    """
    Основной цикл синхронного бота. В бесконечном цикле запрашивает
    обновления через get_updates(). В зависимости от сообщения, которое
    отправил пользователь, отправляет:
    - обратно полученный текст
    - цитату (если сообщение пользователя - команда /quote)

    Обновляет offset, чтобы не обрабатывать одни и те же изменения
    """
    offset = None
    while True:
        updates = get_updates(offset=offset, timeout=30)
        if not updates:
            time.sleep(1)
            continue
        for update in updates:
            offset = update['update_id'] + 1
            message = update.get('message')
            if not message:
                continue
            chat_id = message['chat']['id']
            text = message['text']
            if text == '/quote':
                quote = get_quotes()
                send_message(chat_id, quote)
            else:
                send_message(chat_id, text)
            offset = update['update_id'] + 1


if __name__ == '__main__':
    main()

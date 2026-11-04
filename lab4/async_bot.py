import os
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv, find_dotenv
import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup
import random

load_dotenv(find_dotenv(), encoding='utf-16')
YANDEX_TOKEN = os.getenv('YANDEX_WEATHER_TOKEN')
token = os.getenv('TOKEN')
BASE_URL = f'https://api.telegram.org/bot{token}'


async def send_message(session: aiohttp.ClientSession,
                       chat_id: str, text: str) -> None:
    """
    Асинхронно отправляет сообщение через Telegram API
    (метод sendMessage). При отправке запроса программа не блокируется,
    вместо этого мы ждем ответ через await.
    """
    url = f'{BASE_URL}/sendMessage'
    try:
        async with session.post(url, json={'chat_id': chat_id,
                                           'text': text}) as resp:
            if resp.status == 404:
                print('Ошибка 404. Проверьте токен и ссылку')
                return None
            elif resp.status != 200:
                print('Ошибка: ', resp.status)
                return None
            data = await resp.json()
            if not data.get('ok'):
                print('Ошибка в sendMessage')
    except Exception as e:
        print('Ошибка в sendMessage ', e)


async def get_updates(session: aiohttp.ClientSession,
                      offset: int | None = None, timeout_int: int = 30)\
                      -> List[Dict[str, Any]]:
    """
    Асинхронно получает обновления через getUpdates.
    Сервер держит соединение открытым до timeout_int сек, пока
    не появятся новые сообщения
    """
    url = f'{BASE_URL}/getUpdates'
    params: Dict[str, int] = {'timeout': timeout_int}
    if offset is not None:
        params['offset'] = offset
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_int+5)
        async with session.get(url, params=params, timeout=timeout) as resp:
            if resp.status == 404:
                print('Ошибка 404, getUpdates не найден', resp.status)
                return []
            elif resp.status != 200:
                print('Ошибка: ', resp.status)
                return []
            data = await resp.json()
    except Exception as e:
        print('Ошибка getUpdates', e)
        return []
    if not data.get('ok'):
        print('Ошибка в getUpdates')
        return []
    result = data.get('result', [])
    if not isinstance(result, list):
        return []
    return result


def get_quote_sync() -> str:
    """
    Синхронно получает цитату с сайта с цитатами (та же функция, что
    и в синхронном боте)
    """
    url = 'https://citaty.info/random'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException:
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
        source_text = ' '
    if not quote_text:
        return 'Пустая цитата'
    parts = [f'"{quote_text}"']
    if source_text:
        parts.append(f'{source_text}')
    return '\n'.join(parts)


async def scrape_site(session: aiohttp.ClientSession,
                      url: str, source: str, title_offset: int) -> List[str]:
    """
    Скрапит xml (rss-ленту) и возвращает несколько заголовков
    новостей. Загружает RSS по ссылке url через aiohttp,
    парсит xml через BeautifulSoup
    """
    try:
        timeout = aiohttp.ClientTimeout(total=10.0)
        async with session.get(url, timeout=timeout) as resp:
            xml = await resp.text()
    except Exception as e:
        return [f'{source}: ошибка загрузки: {e}']

    soup = BeautifulSoup(xml, 'xml')
    items = list(soup.find_all('item'))
    items = items[title_offset:title_offset+3]
    titles = []
    for item in items:
        title = item.find('title')
        link = item.find('link')
        if title:
            title_text = title.get_text(strip=True)
        else:
            title_text = ''
        if link:
            link_text = link.get_text(strip=True)
        else:
            link_text = ''
        if title_text:
            titles.append(f'{source}: {title_text}' + f'\n{link_text}')
    if not titles:
        return [f'{source}: заголовки не найдены']
    return titles


async def lenta_headlines(session: aiohttp.ClientSession) -> List[str]:
    """
    Получает заголовки Lenta.ru. Делает случайный сдвиг,
    чтобы заголовки при вызове команды не были каждый раз одинаковыми
    """
    title_offset = random.randint(0, 100)
    return await scrape_site(session, 'https://lenta.ru/rss/news',
                             'Lenta.ru', title_offset)


async def meduza_headlines(session: aiohttp.ClientSession) -> List[str]:
    """
    Получает заголовки Meduza.io. Делает случайный сдвиг,
    чтобы заголовки при вызове команды не были каждый раз одинаковыми
    """
    title_offset = random.randint(0, 20)
    return await scrape_site(session, 'https://meduza.io/rss/news',
                             'Meduza.io', title_offset)


async def coordinates_by_city(session: aiohttp.ClientSession,
                              city: str) -> Tuple[float, float, str] | None:
    """
    Находит координаты города с помощью Nominatim /search.
    Делает get-запрос и берет первый результат.
    Возвращает широту, долготу и имя места
    """
    url = 'https://nominatim.openstreetmap.org/search'
    headers = {'User-Agent': 'mariia-tg-bot/1.0',
               'Accept-Language': 'ru'}
    params: Dict[str, str] = {'q': city, 'format': 'json', 'limit': '1'}
    timeout = aiohttp.ClientTimeout(total=10.0)
    async with session.get(url, params=params,
                           headers=headers, timeout=timeout) as resp:
        data = await resp.json()
    if not isinstance(data, list):
        return None
    if not data:
        return None
    lat = float(data[0]['lat'])
    lon = float(data[0]['lon'])
    display_name = data[0].get('display_name', city)
    if not isinstance(display_name, str):
        return None
    return lat, lon, display_name


async def get_weather(session: aiohttp.ClientSession, city: str) -> str:
    """
    Получает текущую температуру для города через Яндекс Погоду.
    Сначала с помощью coordinates_by_city получает координаты,
    затем отправляет GraphQL запрос в API Яндекс Погоды
    """
    if not YANDEX_TOKEN:
        return 'Не настроен токен Яндекс Погоды'
    coords = await coordinates_by_city(session, city)
    if not coords:
        return 'Попробуйте снова, город не найден'

    lat, lon, place = coords
    url = 'https://api.weather.yandex.ru/graphql/query'
    headers = {'X-Yandex-Weather-Key': YANDEX_TOKEN}

    query = f"""{{
      weatherByPoint(request: {{ lat: {lat}, lon: {lon} }}) {{
        now {{
          temperature
        }}
      }}
    }}"""

    try:
        timeout = aiohttp.ClientTimeout(total=10.0)
        async with session.post(url, headers=headers, json={"query": query},
                                timeout=timeout) as resp:
            data = await resp.json()
    except Exception:
        return 'Не удалось получить погоду'

    if 'errors' in data:
        return 'Ошибка API погоды'

    try:
        temp = data['data']['weatherByPoint']['now']['temperature']
    except Exception:
        return 'Не удалось разобрать ответ погоды'

    return f'Место: {place}\nТемпература: {temp}°C'


user_states: Dict[int, str] = {}


async def main() -> None:
    """
    Главный асинхронный цикл.
    С его помощью бот:
    - отправляет эхо-ответ на обычный текст
    - отправляет случайную цитату на /quote (asyncio.to_thread)
    - отправляет новости, параллельно собранные с нескольких
    источников в ответ на /headlines
    - устанавливает пользователю состояние ожидания города, затем
    отправляет температуру в городе, который ввел пользователь
    в ответ на /weather
    """
    offset = None
    async with aiohttp.ClientSession() as session:
        while True:
            updates = await get_updates(session, offset=offset, timeout_int=30)
            for update in updates:
                message = update['message']
                if not message or 'text' not in message:
                    offset = update['update_id'] + 1
                    continue
                chat_id = message['chat']['id']
                text = message['text']
                user_id = message['from']['id']

                if user_id in user_states:
                    if user_states[user_id] == 'waiting_for_city':
                        city = text
                        weather = await get_weather(session, city)
                        await send_message(session, chat_id, weather)
                        del user_states[user_id]

                elif text == '/quote':
                    quote = await asyncio.to_thread(get_quote_sync)
                    await send_message(session, chat_id, quote)
                elif text == '/headlines':
                    a, b = await asyncio.gather(
                        lenta_headlines(session),
                        meduza_headlines(session))
                    lines = a + b
                    await send_message(session, chat_id, 'Заголовки:\n' +
                                       '\n'.join(' ' + x for x in lines))
                elif text == '/weather':
                    await send_message(session, chat_id,
                                       'Пожалуйста, введите название города')
                    user_states[user_id] = 'waiting_for_city'
                else:
                    await send_message(session, chat_id, text)
                offset = update['update_id'] + 1
            if not updates:
                await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())

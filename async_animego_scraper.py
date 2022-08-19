import logging
import re
from random import choice
import asyncio

from bs4 import BeautifulSoup
import lxml
import cfscrape


cfscraper = cfscrape.create_scraper(delay=12)
user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36']


keys = {
    'тип': "type",
    'эпизоды': "episodes",
    'статус': "status",
    'жанр': "genres",
    'студия': "studio",
    'рейтинг mpaa': "mpaa_rate",
    'возрастные ограничения': "age_restriction",
    'главные герои': "main_characters",
    'длительность': "duration",
}


def randomUserAgent():
    return {
        'user-agent': choice(user_agents)
    }


async def getPageItemsLinks(session, page=1):
    """ returns links to all anime on a page """
    async with session.get(url='https://animego.org/anime/{}'.format(page), headers=randomUserAgent()) as response:
        try:
            html_file = await response.text()
            soup = BeautifulSoup(html_file, 'lxml')
            page_items_list = soup.find_all('div', class_='animes-list-item media')
            page_items_links = []
            for item in page_items_list:
                page_items_links.append(item.find('a').get('href'))
            logging.info(f" page number {page} received")
            return page_items_links
        except Exception as ex:
            logging.error(f" error {ex}")
            return []


async def getAnimeInfo(session, url):
    """ returns dictionary with info about anime from link """
    async with session.get(url=url, headers=randomUserAgent()) as response:
        html_file = await response.text()
        try:
            soup = BeautifulSoup(html_file, 'lxml')
            main_title = soup.find('div', class_='anime-title').find('h1').text
            soup_titles = soup.find('div', class_='synonyms').find_all('li')
            info_block = soup.find('div', class_='anime-info')
            info_keys = info_block.find_all('dt', class_=re.compile('col-6 col-sm-4'))
            info_items = info_block.find_all('dd', class_=re.compile('col-6 col-sm-8'))
            soup_desc = soup.find('div', class_=re.compile('description'))
            info = {
                'title': main_title,
                'synonyms': getSynonyms(soup_titles),
                'description': soup_desc.text.strip(),
            }
            for i in range(len(info_keys)):
                key = re.sub('\W+', ' ', info_keys[i].text).strip().lower()
                value = re.sub('\W+', ' ', info_items[i].text).strip()
                if key in keys.keys():
                    key = keys[key]
                    if key == "genres":
                        info[key] = value.split(' ')
                    elif key == "studio":
                        info[key] = getStudios(info_items[i])
                    elif key == "main_characters":
                        info[key] = getCharacterLinks(info_items[i])
                    else:
                        info[key] = value
            logging.info(" info successfully received")
            return info
        except:
            logging.error(" response code is 200")
            return {}
        # with open('result_a.json', 'w', encoding='utf-8') as file:
        #    json.dump(info, file, indent=4, ensure_ascii=False)


def getSynonyms(soup_titles):
    return [t.text for t in soup_titles]


def getStudios(soup_studios):
    a_tag = soup_studios.find_all('a')
    return [s.find('span').text for s in a_tag]


def getCharacterLinks(soup_characters):
    div_tag = soup_characters.find_all('div')
    return [d.find('span').find('a').get('href') for d in div_tag]


async def getCharacterInfo(session, url):
    """ returns a dictionary with info about character from url """
    async with session.get(url=url, headers=randomUserAgent()) as response:
        html_file = await response.content
        soup = BeautifulSoup(html_file, 'lxml')
        title = soup.find('div', class_=re.compile('character-title')).find('h1').text
        soup_synonyms = soup.find('div', class_='synonyms').find_all('li')
        desc = soup.find('div', itemprop='description').text.strip()
        info = {
            'title': title,
            'synonyms': getSynonyms(soup_synonyms),
            'description': desc,
        }
        # with open('result_c.json', 'w', encoding='utf-8') as file:
        #    json.dump(info, file, indent=4, ensure_ascii=False)
        return info


async def getPerson(session, url):
    """ returns a dictionary with info about person from url """
    async with session.get(url=url, headers=randomUserAgent()) as response:
        html_file = await response.content
        soup = BeautifulSoup(html_file, 'lxml')
        title = soup.find('div', class_=re.compile('people-title')).find('h1').text
        soup_synonyms = soup.find('div', class_='synonyms').find_all('li')
        info_block = soup.find('div', class_='people-info')
        info_keys = info_block.find_all('dt', class_=re.compile('col-12 col-sm-4'))
        info_items = info_block.find_all('dd', class_=re.compile('col-12 col-sm-8'))
        info = {
            'title': title,
            'synonyms': getSynonyms(soup_synonyms)
        }
        for i in range(len(info_keys)):
            key = re.sub('\W+', ' ', info_keys[i].text).strip().lower()
            value = re.sub('\W+', ' ', info_items[i].text).strip()
            info[key] = value
        # with open('result_p.json', 'w', encoding='utf-8') as file:
        #    json.dump(info, file, indent=4, ensure_ascii=False)
        return info

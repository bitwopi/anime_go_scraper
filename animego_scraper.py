import logging
import re

from bs4 import BeautifulSoup
import lxml
import cfscrape
from fake_useragent import UserAgent

ua = UserAgent()
cfscraper = cfscrape.create_scraper(delay=12)


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
    'дата рождения': "birth_date",
    'карьера': "career",
    'авторы': "authors",
    'главы': "chapters",
    'тома': "tomes",
    'издательство': "publisher",
    'выпуск': "release",
    'снят по манге': "source",
    'снят по ранобэ': "source",
}


def getPageItemsLinks(keyword="anime", page=1):
    """ returns links to all anime on a page """
    response = cfscraper.get('https://animego.org/{}/{}'.format(keyword, page),
                             headers={'User-Agent': ua.random})
    if response.status_code != 200:
        logging.info(" page response code isn't 200")
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'lxml')
    page_items_list = soup.find_all('div', class_='animes-list-item media')
    page_items_links = []
    for item in page_items_list:
        page_items_links.append(item.find('a').get('href'))
    logging.info(f" page number {page} received")
    return page_items_links


def getAnimeInfo(url):
    """ returns dictionary with info about anime from link """
    try:
        response = cfscraper.get(url, headers={'User-Agent': ua.random})
        if response.status_code != 200:
            logging.info(" anime response code isn't 200")
            return {}
        html_file = response.content
        soup = BeautifulSoup(html_file, 'lxml')
        title = soup.find('div', class_='anime-title').find('h1').text
        soup_synonyms = soup.find('div', class_='synonyms').find_all('li')
        info_block = soup.find('div', class_='anime-info')
        info_keys = info_block.find_all('dt', class_=re.compile('col-6 col-sm-4'))
        info_items = info_block.find_all('dd', class_=re.compile('col-6 col-sm-8'))
        soup_desc = soup.find('div', class_=re.compile('description'))
        cover = soup.find('div', class_=re.compile('anime-poster')).find('img').get('src')
        try:
            rate = float(soup.find('span', class_='rating-value').text.replace(',', '.'))
        except Exception as ex:
            logging.error(ex)
            rate = 0.0
        info = {
            'title': title,
            'synonyms': getSynonyms(soup_synonyms),
            'slug': getSlug(url),
            'description': soup_desc.text.strip(),
            'rate': rate,
            'cover': cover,
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
                elif key == "episodes":
                    info[key] = int(value)
                elif key == "source":
                    info[key] = info_items[i].find('a').get('href')
                else:
                    info[key] = value
        logging.info(" anime info successfully received")
        return info
    except Exception as ex:
        logging.error(ex)
        return {}


def getCharacterInfo(url):
    """ returns a dictionary with info about character from url """
    response = cfscraper.get(url, headers={'User-Agent': ua.random})
    if response.status_code != 200:
        logging.error(" status code isn't 200")
        return {}
    try:
        html_file = response.content
        soup = BeautifulSoup(html_file, 'lxml')
        name = soup.find('div', class_=re.compile('character-title')).find('h1').text
        soup_synonyms = soup.find('div', class_='synonyms').find_all('li')
        try:
            voice_actor = soup.find('div', class_='col-md-4 mb-2').find('a').get('href')
        except:
            voice_actor = ''
        try:
            desc = soup.find('div', itemprop='description').text.strip()
        except:
            desc = ''
        cover = soup.find('div', class_=re.compile('character-poster')).find('img').get('src')
        info = {
            'name': name,
            'synonyms': getSynonyms(soup_synonyms),
            'slug': getSlug(url),
            'cover': cover,
            'description': desc,
            'voice_actor': voice_actor,
        }
        logging.info(" character info successfully received")
        return info
    except Exception as ex:
        logging.error(ex)
        return {}


def getPerson(url):
    """ returns a dictionary with info about person from url """
    response = cfscraper.get(url, headers={'User-Agent': ua.random})
    if response.status_code != 200:
        logging.info(" person response code isn't 200")
        return {}
    html_file = response.content
    soup = BeautifulSoup(html_file, 'lxml')
    name = soup.find('div', class_=re.compile('people-title')).find('h1').text
    soup_synonyms = soup.find('div', class_='synonyms').find_all('li')
    info_block = soup.find('div', class_='people-info')
    info_keys = info_block.find_all('dt', class_=re.compile('col-12 col-sm-4'))
    info_items = info_block.find_all('dd', class_=re.compile('col-12 col-sm-8'))
    cover = soup.find('div', class_=re.compile('people-poster')).find('img').get('src')
    info = {
        'name': name,
        'synonyms': getSynonyms(soup_synonyms),
        'slug': getSlug(url),
        'cover': cover,
    }
    for i in range(len(info_keys)):
        key = re.sub('\W+', ' ', info_keys[i].text).strip().lower()
        value = re.sub('\W+', ' ', info_items[i].text).strip()
        if key in keys.keys():
            key = keys[key]
            info[key] = value
    logging.info(" person info successfully received")
    return info


def getMangaInfo(url):
    """ returns a dictionary with info about manga from url """
    response = cfscraper.get(url, headers={'User-Agent': ua.random})
    if response.status_code != 200:
        logging.info(" manga response code isn't 200")
        return {}
    html_file = response.content
    soup = BeautifulSoup(html_file, 'lxml')
    title = soup.find('div', class_='manga-title').find('h1').text
    soup_synonyms = soup.find('div', class_='synonyms').find_all('li')
    info_block = soup.find('div', class_=re.compile('manga-info'))
    info_keys = info_block.find_all('dt', class_=re.compile('col-5 col-sm-4'))
    info_items = info_block.find_all('dd', class_=re.compile('col-7 col-sm-8'))
    soup_desc = soup.find('div', class_=re.compile('description'))
    cover = soup.find('div', class_=re.compile('manga-poster')).find('img').get('src')
    info = {
        'title': title,
        'synonyms': getSynonyms(soup_synonyms),
        'slug': getSlug(url),
        'description': soup_desc.text.strip(),
        'cover': cover,

    }
    try:
        soup_characters = soup.find('dd', class_=re.compile('col-6 col-sm-8'))
        info['main_characters'] = getCharacterLinks(soup_characters)
    except Exception as ex:
        logging.error(str(ex) + ", there are no main characters")
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
            elif key == "authors":
                info[key] = getAuthorsLinks(info_items[i])
            else:
                info[key] = value
    logging.info(" manga info successfully received")
    return info


def getSynonyms(soup_titles):
    return [t.text for t in soup_titles]


def getStudios(soup_studios):
    a_tag = soup_studios.find_all('a')
    return [s.find('span').text for s in a_tag]


def getCharacterLinks(soup_characters):
    div_tag = soup_characters.find_all('div')
    return [d.find('span').find('a').get('href') for d in div_tag]


def getAuthorsLinks(soup_authors):
    span_tag = soup_authors.find_all('span', itemprop='author')
    return [s.find('a').get('href') for s in span_tag]


def getSlug(url):
    return url.split('/')[4]


import json
import logging
import os

from animego_scraper import getAnimeInfo, getPageItemsLinks, getCharacterInfo, getPerson, getMangaInfo
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import asyncio
import aiohttp
from dotenv import load_dotenv

result = []
load_dotenv()


def insert_character(character: dict):
    try:
        insert_query = "INSERT INTO main_app_character (name, synonyms, slug, description) VALUES (%s, %s, %s, %s)"
        insert_data = (character['name'], ' '.join(character['synonyms']), character['slug'], character['description'],)
        insert(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def insert_person(person: dict):
    try:
        insert_query = "INSERT INTO main_app_person (name, synonyms, slug) VALUES (%s, %s, %s)"
        insert_data = (person['name'], ' '.join(person['synonyms']), person['slug'],)
        insert(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def insert_career(career):
    insert_query = "INSERT INTO main_app_career (name) VALUES (%s)"
    insert_data = (career,)
    insert(insert_query, insert_data)


def insert(insert_query, insert_data):
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(user=os.environ.get("USER"),
                                      password=os.environ.get("PASSWORD"),
                                      host=os.environ.get("HOST"),
                                      port="5432",
                                      database=os.environ.get("DB_NAME"),
                                      )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(insert_query, insert_data)
    except (Exception, Error) as ex:
        print(ex)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Connection is closed")


def main():
    logging.basicConfig(level=logging.INFO)
    try:
        links = getPageItemsLinks(keyword="anime", page=100)
        for link in links:
            a = getAnimeInfo(link)
            for c in a['main_characters']:
                character = getCharacterInfo(c)
                insert_character(character)
    except Exception as ex:
        print(ex)

    # m = getMangaInfo('https://animego.org/manga/sozdannyy-v-bezdne-110')

    # with open("final.json", 'w', encoding='utf-8') as file:
    #     json.dump(result, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
    # loop = asyncio.get_event_loop()
    # logging.basicConfig(level='INFO')
    # try:
    #     loop.run_until_complete(async_main())
    #     with open("final.json", 'w', encoding='utf-8') as file:
    #         json.dump(result, file, indent=4, ensure_ascii=False)
    # finally:
    #     loop.stop()


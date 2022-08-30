import json
import logging
import os
import re
import time

from fake_useragent import UserAgent

from shikimori_studio_scraper import getStudiosInfo
from animego_scraper import getAnimeInfo, getPageItemsLinks, getCharacterInfo, getPerson, getMangaInfo
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from transliterate import translit

import requests
from dotenv import load_dotenv

result = []
load_dotenv()
ua = UserAgent()


def insert_studio(studio: dict):
    try:
        insert_query = "INSERT INTO main_app_studio (name, slug, logo) VALUES (%s, %s, %s)"
        insert_data = (studio['name'],
                       '-'.join(re.findall(r"[\w']+", studio['name'].lower())),
                       f"/studios/logos/{studio['name']}.png")
        execute_sql_script(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def select_type(type_name: str):
    query = "SELECT id from main_app_type WHERE name = %s"
    data = (type_name,)
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
        cursor.execute(query, data)
        return cursor.fetchone()
    except (Exception, Error) as ex:
        print(ex)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Connection is closed")


def select_source(slug: str):
    query = "SELECT id from main_app_manga WHERE slug = %s"
    data = (slug,)
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
        cursor.execute(query, data)
        return cursor.fetchone()
    except (Exception, Error) as ex:
        print(ex)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Connection is closed")


def insert_anime(anime: dict):
    try:
        insert_query = "INSERT INTO main_app_anime (title, synonyms, slug, description, rate, is_out, episodes_now, " \
                       "cover, type_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            if anime['status'] == "Вышел":
                is_out = True
            else:
                is_out = False
        except:
            is_out = False
        name = '-'.join(re.findall(r"[\w']+", anime['title'].lower()))
        fpath = f"/animes/covers/{name}.jpg"
        type_id = select_type(anime['type'])[0]
        if type_id == 2:
            episodes = None
        else:
            episodes = anime['episodes']
        insert_data = (anime['title'], ' '.join(anime['synonyms']), anime['slug'], anime['description'], anime['rate'],
                       is_out, episodes, fpath, type_id)
        execute_sql_script(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def update_anime(anime: dict, slug: str):
    try:
        insert_query = "UPDATE main_app_anime SET source_id = %s WHERE slug = %s"
        source_id = select_source(slug)
        insert_data = (source_id, anime['slug'],)
        execute_sql_script(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def insert_manga(manga: dict):
    try:
        insert_query = "INSERT INTO main_app_manga (title, synonyms, slug, description, cover, type_id) " \
                       "VALUES (%s, %s, %s, %s, %s, %s)"
        name = '-'.join(re.findall(r"[\w']+", manga['title'].lower()))
        fpath = f"/manga/covers/{name}.jpg"
        type_id = select_type(manga['type'])[0]
        insert_data = (manga['title'], ' '.join(manga['synonyms']), manga['slug'], manga['description'], fpath, type_id)
        execute_sql_script(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def insert_character(character: dict):
    try:
        insert_query = "INSERT INTO main_app_character (name, synonyms, slug, description) VALUES (%s, %s, %s, %s)"
        insert_data = (character['name'], ' '.join(character['synonyms']), character['slug'], character['description'],)
        execute_sql_script(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def update_character(character: dict):
    try:
        insert_query = "UPDATE main_app_character SET photo = %s WHERE name = %s"
        name = '-'.join(re.findall(r"[\w']+", character['name'].lower()))
        fpath = f"/character/photos/{name}.jpg"
        insert_data = (fpath, character['name'],)
        execute_sql_script(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def insert_category(category: str):
    insert_query = "INSERT INTO main_app_category (name, slug) VALUES (%s, %s)"
    insert_data = (category, translit(category, reversed=True).lower())
    execute_sql_script(insert_query, insert_data)


def insert_person(person: dict):
    try:
        insert_query = "INSERT INTO main_app_person (name, synonyms, slug) VALUES (%s, %s, %s)"
        insert_data = (person['name'], ' '.join(person['synonyms']), person['slug'],)
        execute_sql_script(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def update_person(person: dict):
    try:
        insert_query = "UPDATE main_app_person SET photo = %s WHERE name = %s"
        name = '-'.join(re.findall(r"[\w']+", person['name'].lower()))
        fpath = f"/persons/photos/{name}.jpg"
        insert_data = (fpath, person['name'])
        execute_sql_script(insert_query, insert_data)
    except Exception as ex:
        logging.error(ex)


def insert_career(career):
    insert_query = "INSERT INTO main_app_career (name) VALUES (%s)"
    insert_data = (career,)
    execute_sql_script(insert_query, insert_data)


def execute_sql_script(query, data):
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
        cursor.execute(query, data)
        return cursor.fetchone()
    except (Exception, Error) as ex:
        print(ex)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Connection is closed")


def main():
    logging.basicConfig(level=logging.INFO)
    links = getPageItemsLinks(keyword="anime", page=101)
    try:
        for link in links:
            print(link)
            a = getAnimeInfo(link)
            name_a = '-'.join(re.findall(r"[\w']+", a['title'].lower()))
            with open(f"/home/bitwopi/Desktop/MyFirstSite/mysite/media/animes/covers/{name_a}.jpg", 'wb') as file:
                file.write(requests.get(a['cover']).content)
                time.sleep(2)
            insert_anime(a)
            try:
                manga = getMangaInfo(a['source'])
                print(manga['type'])
            except:
                continue
            name_m = '-'.join(re.findall(r"[\w']+", manga['title'].lower()))
            with open(f"/home/bitwopi/Desktop/MyFirstSite/mysite/media/manga/covers/{name_m}.jpg", 'wb') as file:
                file.write(requests.get(manga['cover']).content)
                time.sleep(2)
            insert_manga(manga)
            update_anime(a, manga['slug'])
            # for c in a['main_characters']:
            #     if c != '':
            #         print(c)
            #         character = getCharacterInfo(c)
            #         voice_actor = getPerson(character['voice_actor'])
                    # insert_character(character)
                    # insert_person(voice_actor)
                    # name_c = '-'.join(re.findall(r"[\w']+", character['name'].lower()))
                    # name_p = '-'.join(re.findall(r"[\w']+", voice_actor['name'].lower()))
                    # with open(f"/home/bitwopi/Desktop/MyFirstSite/mysite/media/characters/photos/{name_c}.jpg", 'wb') as file:
                    #     file.write(requests.get(character['cover']).content)
                    #     time.sleep(2)
                    # with open(f"/home/bitwopi/Desktop/MyFirstSite/mysite/media/persons/photos/{name_p}.jpg", 'wb') as file:
                    #     file.write(requests.get(voice_actor['cover']).content)
                    #     time.sleep(2)
                    # update_character(character)
                    # update_person(voice_actor)
    except Exception as ex:
        logging.error(ex)
            # voice_actor = getPerson(character['voice_actor'])
            # name = '-'.join(re.findall(r"[\w']+", voice_actor['name'].lower()))
            # with open(f"/home/bitwopi/Desktop/MyFirstSite/mysite/media/persons/photos/{name}.jpg", 'wb') as file:
            #     file.write(requests.get(voice_actor['cover']).content)
            #     time.sleep(3)
            # insert_character(character)
            # insert_person(voice_actor)

                # insert_character(character)
    # studios = getStudiosInfo()
    # for s in studios:
    #     insert_studio(s)
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

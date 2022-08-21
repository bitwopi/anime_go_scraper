import json
import logging

from animego_scraper import getAnimeInfo, getPageItemsLinks, getCharacterInfo, getPerson, getMangaInfo


import asyncio
import aiohttp

result = []


async def async_main():
    async with aiohttp.ClientSession() as session:
        for i in range(1, 15):
            links = getPageItemsLinks(i)
            for link in links:
                a = await getAnimeInfo(session, link)
                if len(a):
                    result.append(a)
                else:
                    await asyncio.sleep(5)


def main():
    logging.basicConfig(level=logging.INFO)
    """    for i in range(1, 6):
        links = getPageItemsLinks(i)
        for link in links:
            a = getAnimeInfo(link)"""
    a = getAnimeInfo('https://animego.org/anime/sozdannyy-v-bezdne-solnce-vspyhnuvshee-v-zolotom-gorode-s2085')
    m = getMangaInfo('https://animego.org/manga/detektivy-futo-1482')
    result.append(m)
    result.append(a)
    for a in m['authors']:
        result.append(getPerson(a))

    with open("final.json", 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
    """
    loop = asyncio.get_event_loop()
    logging.basicConfig(level='INFO')
    try:
        loop.run_until_complete(async_main())
        with open("final.json", 'w', encoding='utf-8') as file:
            json.dump(result, file, indent=4, ensure_ascii=False)
    finally:
        loop.stop()
    """


from random import sample

import requests
from bs4 import BeautifulSoup
import re
import time
# from googlesearch import search
from duckduckgo_search import DDGS

DUCK = DDGS()

# FIXME jakiś błąd z rozwiązaniem tego `from googlesearch import search`
#   Rozwiązania:
#       1. Zmienić to na duckduckgo. Problem: praktycznie taki sam
#       2. Zgłębić, o co chodzi z tym search-em.
#   Wybieram rozwiązanie 2.

CHESS_SITE_URL = 'https://www.thechesswebsite.com/chess-openings/'
SUBSITE_SRC_CLASS = 'grid-65 mobile-grid-100 nopadding normal-left-col cb-post-grid'
_HTML_TAG_PATTERN = re.compile(r'^\s*<[^>]+>')
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  "Chrome/133.0.0.0 Safari/537.36"
}
_SEPARATOR = '\n================================================================================\n'

_albin = 'https://www.thechesswebsite.com/albin-counter-gambit/'
_belgrade = 'https://www.thechesswebsite.com/belgrade-gambit/'
_benoni = 'https://www.thechesswebsite.com/benoni-defense/'
_bird = 'https://www.thechesswebsite.com/birds-opening/'
_bishop = 'https://www.thechesswebsite.com/bishops-opening/'

def get_src(link):
    chess_request = requests.get(link, headers=_HEADERS)
    assert chess_request.status_code == 200
    return chess_request.text

class OpeningInformation:
    def __init__(self, name, desc, picture):
        self.name = name
        self.desc = desc
        self.picture = picture

    def __str__(self):
        return (
            f"OpeningInformation object:\n"
            f"\tname: {self.name}\n"
            f"\tdesc: {self.desc}\n"
            f"\tpicture: {self.picture}"
        )

class WebsiteInformation:
    def __init__(self, title, desc, openings):
        self.title = title
        self.desc = desc
        self.openings = openings

def scrape_title_and_desc(soup):
    t = soup.find_all('div', class_='elementor-widget-container')
    title = t[6].get_text(strip=True)
    desc = t[7].get_text()
    first_paragraph = re.split('\n', desc)[1]
    fp_short = '.'.join(re.split(r'\.', first_paragraph)[:3]) + '.'
    return title, fp_short

def get_desc(link):
    soup = BeautifulSoup(get_src(link), features='html.parser')
    div = soup.find('div', class_=SUBSITE_SRC_CLASS)
    par = div.find_all('p')
    desc = ''
    for i in range(1, 4):
        if _HTML_TAG_PATTERN.match(par[i].decode_contents()):
            break
        desc += par[i].get_text() + '\n'
    return desc

def gather_openings_information(soup):
    openings_div = soup.find_all('div', id='cb-container')[1]
    raw_openings = list(openings_div.find_all('a'))

    def is_access_granted(opening):
        span = opening.find('span')
        return span is None or span.get_text() != 'MEMBERS ONLY'

    return [
        OpeningInformation(
            opening.find('h5').get_text(),
            get_desc(opening['href']),
            opening.find('img')['src']
        )
        for opening in raw_openings
        if is_access_granted(opening)
    ]

def gather_website_information(src):
    soup = BeautifulSoup(src, features='html.parser')
    title, desc = scrape_title_and_desc(soup)
    openings = gather_openings_information(soup)
    return WebsiteInformation(title, desc, openings)

def assemble_basic_markdown(desc, info):
    basic_md = f"# {info.title}\n\n{desc}\n\n"

    for opening in info.openings[:5]: # FIXME zmienić na całość po testach
        basic_md += f"## {opening.name}\n\n"
        basic_md += f"![{opening.name}]({opening.picture})\n\n"
        basic_md += f"{opening.desc}\n\n"

    return basic_md

def assemble_enhanced_markdown(desc, info):
    enhanced_md = f"# {info.title}\n\n{desc}\n\n"

    for opening in info.openings[:5]: # FIXME zmienić na całość po testach
        enhanced_md += f"## {opening.name}\n\n"
        enhanced_md += f"![{opening.name}]({opening.picture})\n\n"
        enhanced_md += f"{opening.desc}\n\n"

        ddg_text = DUCK.text(opening.name, max_results=1)[0]
        if (opening.name == "Belgrade Gambit"):
            ddg_text_link = ddg_text['href']
        ddg_text = ddg_text['body']
        ddg_video = DUCK.videos(opening.name, max_results=1)[0]
        ddg_video_link = ddg_video['content']
        ddg_video_image = ddg_video['images']['medium']

        enhanced_md += f"### Duckduckgo results about {opening.name}\n\n"
        enhanced_md += f"{ddg_text}\n\n"
        enhanced_md += f"Video:\n[![]({ddg_video_image})]({ddg_video_link})\n\n"

    return enhanced_md

def create_basic_markdown(chess_website_information):
    desc = f"#### {chess_website_information.desc}\n\n"
    return assemble_basic_markdown(desc, chess_website_information)

def create_enhanced_markdown(chess_website_information):
    desc = f'#### {chess_website_information.desc}\n\n'
    return assemble_enhanced_markdown(desc, chess_website_information)

def mdsave(mdfile, name):
    with open(f"{name}.md", "w", encoding="utf-8") as file:
        file.write(mdfile)

def main():
    chess_website_information = gather_website_information(get_src(CHESS_SITE_URL))
    basic_markdown = create_basic_markdown(chess_website_information)
    enhanced_markdown = create_enhanced_markdown(chess_website_information)
    mdsave(basic_markdown, 'basic_markdown')
    mdsave(enhanced_markdown, 'enhanced_markdown')

def _check_ddg_text(query):
    """
    APPROVED 20:09.
    """
    print(f'DDGS().text("{query}", max_results=3)\n')
    results = DUCK.text(query, max_results=3)

    for result in results:
        print('Type:',  type(result))
        print('Keys:',  result.keys())
        print('Title:', result['title'])
        print('Body:',  result['body'])
        print(_SEPARATOR)


def _check_ddq_video(query):
    """
    APPROVED 20:33
    """
    print(f'DDGS().videos("{query}", max_results=3)\n')
    results = DUCK.videos(query, max_results=3)

    for result in results:
        print('Type:',  type(result))
        print('Keys:',  result.keys())
        print('Title:', result['title'])
        print('content:', result['content'])
        print('image_token:', result['image_token'])
        print('medium image:', result['images']['medium'])
        print('description:', result['description'])
        print(_SEPARATOR)


def check_ddg():
    """
    APPROVED 20:33
    """
    query = "polska niemcy francja"
    _check_ddg_text(query)
    # _check_ddq_video(query)

if __name__ == '__main__':
    start_time = time.time()
    main()
    # check_ddg()
    print(f'Execution time: {time.time() - start_time} seconds.')
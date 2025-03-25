import os
import enum
import sys
import requests
from bs4 import BeautifulSoup
import re
import time
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException
import yaml

class Mode(enum.Enum):
    GENTLE = 1 # Create markdown files only if they don't exist
    BRUTAL = 2 # Create markdown files regardless of their existence

# Global variables
DUCK = DDGS() # Global DuckDuckGo search object
ERROR_COUNT = 0 # DuckDuckGo search error count
DATE = '2025-03-24' # Date of the post
mode = Mode.GENTLE # Mode of the script

CHESS_SITE_URL = 'https://www.thechesswebsite.com/chess-openings/'
SUBSITE_SRC_CLASS = 'grid-65 mobile-grid-100 nopadding normal-left-col cb-post-grid'
_HTML_TAG_PATTERN = re.compile(r'^\s*<[^>]+>')

class OpeningInformation:
    """
    Class representing information about a chess opening scraped from the main chess iste.
    """
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
    """
    Class representing information about a main chess openings website.
    """
    def __init__(self, title, desc, openings):
        self.title = title
        self.desc = desc
        self.openings = openings

def get_src(link):
    """
    Get the html source code of the website.
    :param link: URL of the website
    :return: Source code of the website in html
    """
    chess_request = requests.get(link)
    assert chess_request.status_code == 200
    return chess_request.text

def scrape_title_and_desc(soup):
    """
    Scrape the title and description of the website.
    This function is an exaggeration, but it's here as a scraping exercise.
    :param soup: BeautifulSoup object
    :return: (title, first paragraph) tuple
    """
    t = soup.find_all('div', class_='elementor-widget-container')
    title = t[6].get_text(strip=True)
    desc = t[7].get_text()
    first_paragraph = re.split('\n', desc)[1]
    fp_short = '.'.join(re.split(r'\.', first_paragraph)[:3]) + '.'
    return title, fp_short

def get_desc(link):
    """
    Scrape the description of the opening from a particular opening page.
    :param link: URL of the opening page
    :return: Description of the opening
    """
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
    """
    Gather information about the openings from the website source given as a BeautifulSoup object.
    :param soup: BeautifulSoup object
    :return: List of OpeningInformation objects
    """
    openings_div = soup.find_all('div', id='cb-container')[1]
    raw_openings = list(openings_div.find_all('a'))

    def is_access_granted(opening):
        """
        Determines whether the opening is available in non-premium mode.
        :param opening: opening name
        :return: True if the opening is available in non-premium mode, False otherwise
        """
        span = opening.find('span')
        return span is None or span.get_text() != 'MEMBERS ONLY'

    return [
        OpeningInformation(
            opening.find('h5').get_text(),
            get_desc(opening['href']),
            opening.find('img')['src']
        )
        for opening in raw_openings
        if is_access_granted(opening) # Not all openings are available in non-premium mode
    ]

def gather_website_information(src):
    """
    Gathers information about the website from the source code.
    :param src: Source code of the website (html)
    :return:
    """
    print("Gathering website information...", file=sys.stderr)

    soup = BeautifulSoup(src, features='html.parser')
    title, desc = scrape_title_and_desc(soup)
    openings = gather_openings_information(soup)

    # Save title and description to Jekyll catalog
    with open('ip-chess-openings/_data/site_info.yml', 'w') as file:
        yaml.dump({
            'title': title,
            'desc': desc
        }, file)

    return WebsiteInformation(title, desc, openings)

def assemble_basic_markdown(desc, info):
    basic_md = f"# {info.title}\n\n{desc}\n\n"

    for opening in info.openings: # FIXME zmienić na całość po testach
        basic_md += f"## {opening.name}\n\n"
        basic_md += f"![{opening.name}]({opening.picture})\n\n"
        basic_md += f"{opening.desc}\n\n"

    return basic_md

def jekylled_md(opening_name, md_text):
    md = f"""---
layout: post
title:  {opening_name}
---\n\n"""
    md += '\n'.join(md_text.split('\n')[1:]) # First line removed
    return md

def jekylled_post_name(opening_name):
    return f"{DATE}-{opening_name.replace(' ', '-').lower()}"

def assemble_enhanced_markdown(desc, info):
    enhanced_md = f"# {info.title}\n\n{desc}\n\n"
    openings_sorted = []

    for opening in info.openings: # FIXME zmienić na całość po testach
        global ERROR_COUNT

        # Add basic information
        s = f"## {opening.name}\n\n"
        s += f"![{opening.name}]({opening.picture})\n\n"
        s += f"{opening.desc}\n\n"

        # Search for information with DuckDuckGo
        while True:
            try:
                ddg_text = DUCK.text(opening.name, backend='html')[0]['body']
                if ddg_text.endswith('...'):  # Handle weird search results
                    sentences = ddg_text.split('.')
                    if len(sentences) > 2:
                        ddg_text = '.'.join(sentences[:-3]) + '.'
                break
            except DuckDuckGoSearchException as e:
                ERROR_COUNT += 1
                if ERROR_COUNT == 10:
                    print("Too many errors. Exiting...")
                    exit(1)
                print(f"Error: {e}. Retrying in 10 seconds...")
                time.sleep(10)

        # Search for video with DuckDuckGo
        while True:
            try:
                ddg_video = DUCK.videos(opening.name)[0]
                ddg_video_views = ddg_video['statistics']['viewCount']
                ddg_video_link = ddg_video['content']
                ddg_video_image = ddg_video['images']['medium']
                break
            except DuckDuckGoSearchException as e:
                ERROR_COUNT += 1
                if ERROR_COUNT == 10:
                    print("Too many errors. Exiting...")
                    exit(1)
                print(f"Error: {e}. Retrying in 10 seconds...")
                time.sleep(10)

        # Add DuckDuckGo information
        s += f"### Duckduckgo results about {opening.name}\n\n"
        s += f"{ddg_text}\n\n"
        s += f"Video:  \n[![]({ddg_video_image})]({ddg_video_link})\n\n"

        t = (s, ddg_video_views)
        openings_sorted.append(t)

        # Add the opening md to _posts
        mdsave(jekylled_md(opening.name, s), f'ip-chess-openings/_posts/' + jekylled_post_name(opening.name))

    def sort_key(el): # Sort by views with None values equal to -inf
        return el[1] if el[1] is not None else float('-inf')
    openings_sorted = sorted(openings_sorted, key=sort_key, reverse=True)

    for opening in openings_sorted:
        enhanced_md += opening[0]

    return enhanced_md

def create_basic_markdown(chess_website_information):
    """
    Create basic markdown from the gathered information.
    Basic markdown consists of the title, description, and basic information about the openings.
    :param chess_website_information:
    :return: Basic markdown text
    """
    print("Creating basic markdown...", file=sys.stderr)

    desc = f"#### {chess_website_information.desc}\n\n"
    return assemble_basic_markdown(desc, chess_website_information)

def create_enhanced_markdown(chess_website_information):
    """
    Create enhanced markdown from the gathered information.
    Enhanced markdown consists of the title, description, basic information about the openings,
    and DuckDuckGo search results: additional information and a video link.
    Openings are sorted by the number of views of the corresponding video.
    :param chess_website_information:
    :return: Enhanced markdown text
    """
    print("Creating enhanced markdown...", file=sys.stderr)

    desc = f'#### {chess_website_information.desc}\n\n'
    return assemble_enhanced_markdown(desc, chess_website_information)

def mdsave(md_text: str, name: str):
    """
    Save the markdown text to a file.
    :param md_text: markdown text
    :param name: name of the file
    """
    with open(f"{name}.md", "w", encoding="utf-8") as file:
        file.write(md_text)

def ask_for_mode():
    m = input("""Please choose the mode:
        1. Create markdown files only if they don't exist.
        2. Create markdown files regardless of their existence.
        Type "1" or "2" (skip for default - 1): """)

    if m is not None and m not in ['1', '2']:
        print("Invalid mode. Exiting...")
        exit(1)

    return Mode.GENTLE if m is None or m == '1' else Mode.BRUTAL

def main():
    """
    Main function of the script.
    Creates basic and enhanced markdown files with information about chess openings, while saving important information
    in the Jekyll project catalog.
    :return:
    """
    global mode
    mode = ask_for_mode()
    print(mode)

    if mode == Mode.BRUTAL:
        chess_website_information = gather_website_information(get_src(CHESS_SITE_URL))
        basic_markdown = create_basic_markdown(chess_website_information)
        mdsave(basic_markdown, 'basic_markdown')
        enhanced_markdown = create_enhanced_markdown(chess_website_information)
        mdsave(enhanced_markdown, 'enhanced_markdown')
    else:
        if not os.path.isfile('basic_markdown.md') or not os.path.isfile('enhanced_markdown.md'):
            chess_website_information = gather_website_information(get_src(CHESS_SITE_URL))

            if not os.path.isfile('basic_markdown.md'):
                basic_markdown = create_basic_markdown(chess_website_information)
                mdsave(basic_markdown, 'basic_markdown')

            if not os.path.isfile('enhanced_markdown.md'):
                enhanced_markdown = create_enhanced_markdown(chess_website_information)
                mdsave(enhanced_markdown, 'enhanced_markdown')

if __name__ == '__main__':
    start_time = time.time()
    main()
    print(f'Execution time: {time.time() - start_time} seconds.')
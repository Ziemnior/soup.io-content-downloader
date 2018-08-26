from bs4 import BeautifulSoup
import os, requests
from time import sleep


url = 'http://sturmunddrang.soup.io'


def prepare_dir_absolute_path(url):
    dir_name = url.split('.')[0].split('/')[2]
    return os.getcwd() + '/' + dir_name + '\'s soup'


def create_dir(url):
    dir_name = prepare_dir_absolute_path(url)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def get_website(url):
    return BeautifulSoup(requests.get(url).content, 'html.parser')


def gather_links_from_page(url):
    media_links = get_website(url).findAll(name='div', attrs={'class': 'content'})
    media_links_raw = [media_link.find('video') or media_link.find('img') for media_link in media_links]
    return [media_link_raw.get('src') for media_link_raw in media_links_raw]


def get_next_page_url(url):
    return url + get_website(url).find(name='a', attrs={'class': 'more keephash'}).get('href')


# def update_url(next_page_url):
#     global url
#     url = next_page_url

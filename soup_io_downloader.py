import logging
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tenacity import retry, wait_fixed, stop_after_attempt, RetryError

def request_exceptions(f):
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except requests.exceptions.Timeout as t_error:
            self.logger.error(f'TimeoutError while fetching website \n traceback: {t_error}')
        except requests.exceptions.ConnectionError as conn_error:
            self.logger.error(f'ConnectionError while fetching website \n traceback: {conn_error}')
        except RetryError as retry_error:
            self.logger.error(f'Number of retries exceeded \n traceback: {retry_error}')
    return wrapper

def regex_exceptions(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IndexError:
            return 'Wrong url provided'
    return wrapper

def https_wrapper(f):
    def wrapper(*args, **kwargs):
        url_ = f(*args, **kwargs)
        if 'http' not in url_:
            return f'https://{url_}'
        return url_
    return wrapper


class SoupDownloader:
    def __init__(self, url):
        self.url = self._get_url(url)
        self.base_url = self._get_base_url(url)
        self.website_content = None
        self.__setup_logger()
        self.logger = logging.getLogger('soup_downloader')

    def __setup_logger(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s.%(msecs)03d %(levelname)-5s %(message)s',
                            datefmt='%d-%m-%Y %H-%M-%S',
                            filename='soup_io_downloader.log',
                            filemode='w')

    @https_wrapper
    def _get_url(self, url):
        return url

    @regex_exceptions
    @https_wrapper
    def _get_base_url(self, given_url):
        re_url = re.match('(?P<url>(http(s|)://|)\w+.soup.io)', given_url)
        url = re_url.group('url')
        return url

    def __prepare_dir_absolute_path(self):
        name = re.match('^((http|https)://)(?P<name>\w+).soup.io', self.base_url)
        return os.path.join(os.path.dirname(__file__), f'{name.group("name")} soup')

    def __create_dir(self):
        dir_name = self.__prepare_dir_absolute_path()
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            self.logger.info(f'created \'{dir_name}\' directory')

    def __get_file_extension(self, url):
        ext = re.search('\w+', os.path.splitext(url)[1])
        return ext.group(0)

    @request_exceptions
    @retry(stop=stop_after_attempt(10), wait=wait_fixed(30))
    def _get_website(self):
        website = requests.get(self.url, timeout=10)
        return BeautifulSoup(website.content, 'html.parser')

    def __get_html_tags_from_page(self):
        """Returns extracted 'content' html tags from page"""
        return self.website_content.findAll(name='div', attrs={'class': 'content'})

    def __extract_media_tags(self):
        """Returns extracted img/video tag from content tag"""
        return [media_link.find('video') or
                media_link.find(name='a', attrs={'class': 'lightbox'})
                or media_link.find('img')
                for media_link in self.__get_html_tags_from_page()]

    def __extract_urls_to_media(self):
        """Returns extracted url from img/video tag"""
        return [
            media_link_raw.get('src') or
            media_link_raw.get('href')
            for media_link_raw in self.__extract_media_tags() if media_link_raw]

    @staticmethod
    def __validate_media_link(url):
        """Validates if url leads to file, i.e. has extension"""
        if os.path.splitext(url)[1]:
            return url

    def _gather_links_from_page(self):
        media_links = filter(None, self.__extract_urls_to_media())
        return [self.__validate_media_link(link) for link in media_links]

    def __create_filename(self, url):
        if not url:
            return None
        file_extension = self.__get_file_extension(url)
        return os.path.join(self.__prepare_dir_absolute_path(), '{}.{}'.format(
            datetime.now().strftime('%d-%m-%Y %H-%M-%S-%f'), file_extension
        ))

    @request_exceptions
    @retry(stop=stop_after_attempt(10), wait=wait_fixed(30))
    def _get_response(self, url):
        return requests.get(url, timeout=10)

    def _save_file(self, response, file_name):
        with open(file_name, 'wb') as f:
            self.logger.info(f'saving {file_name}')
            f.write(response.content)

    def _download_images_from_one_page(self):
        for url in self._gather_links_from_page():
            response = self._get_response(url)
            file_name = self.__create_filename(url)
            if response and file_name:
                self._save_file(response, file_name)

    @regex_exceptions
    def __strip_url(self, url):
        base_url = re.search('(?:http(?:s|)://|)\w+.soup.io', url)
        return base_url.group(0)

    def __get_next_page_url(self):
        try:
            return self.base_url + self.website_content.find(name='a', attrs={'class': 'more keephash'}).get('href')
        except AttributeError:
            pass

    def _set_var(self, var, func):
        setattr(self, var, func)

    def download(self):
        self.__create_dir()
        while self.url:
            self._set_var('website_content', self._get_website())
            if not self.website_content:
                self.logger.info(f'Couldn\'t fetch from {self.url}')
                break
            self.logger.info('downloading images from {}'.format(self.url))
            self._download_images_from_one_page()
            self._set_var('url', self.__get_next_page_url())
        self.logger.info('all images were downloaded')


if __name__ == '__main__':
    url = input('Provide url to soup in one of the following manners: \n '
                '- http://YOUR_SOUP.soup.io \n'
                '- http://YOUR_SOUP.soup.io \n'
                '- YOUR_SOUP.soup.io \n\n'
                'If you wish to resume from given point, check log file to retrieve last fetched page url '
                '(it will look similar to https://YOUR_SOUP.soup.io/since/123456789?mode=own) \n'
                'your url: ')
    print('To track the progress of downloading, check log file')
    SoupDownloader(url).download()

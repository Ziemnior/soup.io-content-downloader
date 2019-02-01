import os, requests, re, logging
from bs4 import BeautifulSoup
from datetime import datetime


class SoupIODownloader:
    def __init__(self, url):
        self.url = url
        self.base_url = url
        self.__setup_logger()
        self.logger = logging.getLogger('soup_io_downloader')
        self.logger.info('creating an instance of SoupIODownloader')

    def __setup_logger(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d-%y %H:%M',
                            filename='soup_io_downloader.log',
                            filemode='w')

    def __prepare_dir_absolute_path(self):
        dir_name = self.url.split('.')[0].split('/')[2]
        return os.getcwd() + '\\' + dir_name + ' soup'

    def __create_dir(self):
        dir_name = self.__prepare_dir_absolute_path()
        if not os.path.exists(dir_name):
            self.logger.info('created \'{}\' directory'.format(dir_name))
            os.makedirs(dir_name)

    def __get_file_extension(self, url):
        f = re.search('\w+', os.path.splitext(url)[1])
        return f.group(0)

    def __create_filename(self, url):
        date_format = '%d-%m-%Y %H-%M-%S-%f'
        file_extension = self.__get_file_extension(url)
        return os.path.join(self.__prepare_dir_absolute_path(), '{}.{}'.format(
            datetime.now().strftime(date_format),
            file_extension
        ))

    def _get_website(self):
        return BeautifulSoup(requests.get(self.url).content, 'html.parser')

    def _gather_links_from_page(self):
        media_links = self._get_website().findAll(name='div', attrs={'class': 'content'})
        media_links_raw = [media_link.find('video') or media_link.find('img') for media_link in media_links]
        return [media_link_raw.get('src') for media_link_raw in media_links_raw]

    def _download_images_from_one_page(self):
        for url in self._gather_links_from_page():
            response = self._save_content(url)
            file_name = self.__create_filename(url)
            with open(file_name, 'wb') as f:
                self.logger.info('saving {}'.format(file_name))
                f.write(response.content)

    def _save_content(self, url):
        try:
            return requests.get(url)
        except TimeoutError:
            self.logger.error('error while fetching {}'.format(url))

    def __get_next_page_url(self):
        return self.base_url + self._get_website().find(name='a', attrs={'class': 'more keephash'}).get('href') or None

    def set_new_url(self):
        setattr(self, 'url', self.__get_next_page_url())

    def download(self):
        self.__create_dir()
        while self.url:
            self.logger.info('downloading images from {} page'.format(self.url))
            self._download_images_from_one_page()
            self.set_new_url()
        self.logger.info('all images were downloaded')

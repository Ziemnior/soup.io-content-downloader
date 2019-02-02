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
                            format='%(asctime)s.%(msecs)03d %(levelname)-5s %(message)s',
                            datefmt='%d-%m-%Y %H-%M-%S',
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
        file_extension = self.__get_file_extension(url)
        return os.path.join(self.__prepare_dir_absolute_path(), '{}.{}'.format(
            datetime.now().strftime('%d-%m-%Y %H-%M-%S-%f'), file_extension
        ))

    def _get_website(self):
        try:
            website = requests.get(self.url, timeout=10)
        except requests.exceptions.Timeout as t_error:
            self.logger.error('TimeoutError while fetching website \n traceback: {}'.format(t_error))
            pass
        except requests.exceptions.ConnectionError as conn_error:
            self.logger.error('ConnectionError while fetching website \n traceback: {}'.format(conn_error))
            pass
        else:
            return BeautifulSoup(website.content, 'html.parser')

    def _gather_links_from_page(self):
        media_links = self._get_website().findAll(name='div', attrs={'class': 'content'})
        media_links_raw = [media_link.find('video') or media_link.find('img') for media_link in media_links]
        return [media_link_raw.get('src') for media_link_raw in media_links_raw]

    def _download_images_from_one_page(self):
        for url in self._gather_links_from_page():
            response = self._get_response(url)
            file_name = self.__create_filename(url)
            self._save_file(file_name, response)

    def _get_response(self, url):
        try:
            return requests.get(url, timeout=10)
        except requests.exceptions.Timeout as t_error:
            self.logger.error('TimeoutError while fetching {} \n traceback: {}'.format(url, t_error))
            pass
        except requests.exceptions.ConnectionError as conn_error:
            self.logger.error('ConnectionError while fetching {} \n traceback: {}'.format(url, conn_error))
            pass

    def _save_file(self, file_name, response):
        if response:
            with open(file_name, 'wb') as f:
                self.logger.info('saving {}'.format(file_name))
                f.write(response.content)

    def __get_next_page_url(self):
        return self.base_url + self._get_website().find(name='a', attrs={'class': 'more keephash'}).get('href') or None

    def _set_new_url(self):
        setattr(self, 'url', self.__get_next_page_url())

    def download(self):
        self.__create_dir()
        while self.url:
            self.logger.info('downloading images from {}'.format(self.url))
            self._download_images_from_one_page()
            self._set_new_url()
        self.logger.info('all images were downloaded')
        self.logger.shutdown()

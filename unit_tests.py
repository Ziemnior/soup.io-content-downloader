import unittest
import os
from soup_io_downloader import prepare_dir_absolute_path, create_dir, get_website


class TestSoupDownloader(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSoupDownloader, self).__init__(*args, **kwargs)
        self.url = 'http://sturmunddrang.soup.io'

    def test_dir_name_preparation(self):
        self.assertEqual(prepare_dir_absolute_path(self.url), os.getcwd() + '/sturmunddrang\'s soup')

    def test_dir_creation(self):
        create_dir(self.url)
        self.assertTrue(os.path.exists(os.getcwd() + '/sturmunddrang\'s soup'))

    def test_if_website_content_is_not_empty(self):
        self.assertTrue(len(get_website(self.url)) > 0)

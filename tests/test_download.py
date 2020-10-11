import unittest
from unittest import mock
from instapull import PostDownloader
from tests.mock_util import mock_save_file
from tests.mock_requests import mock_instagram_api


@mock.patch('instapull.requests.get', side_effect=mock_instagram_api)
class RetrieveHashTest(unittest.TestCase):
    def test_retrieve_user_query_hash(self, mock_get):
        downloader = PostDownloader(user="test")
        hash = downloader.retrieve_user_query_hash()
        self.assertEquals('56a7068fea504063273cc2120ffd54f3', hash)
    
    def test_retrieve_tag_query_hash(self, mock_get):
        downloader = PostDownloader(tag="test")
        hash = downloader.retrieve_tag_query_hash()
        self.assertEquals('9b498c08113f1e09617a1703c22b2f32', hash)


@mock.patch('instapull.PostDownloader._save_file', side_effect=mock_save_file)
@mock.patch('instapull.requests.get', side_effect=mock_instagram_api)
class FileTests(unittest.TestCase):
    def test_filename_parser(self, mock_save, mock_get):
        s = "https://www.dummy.me/stuff/1234/abc/file.jpg?hash=1234"
        downloader = PostDownloader()
        filename = downloader._get_filename(s)
        self.assertEquals(filename, 'file.jpg')

    def test_save(self, mock_save, mock_get):
        downloader = PostDownloader()

        downloader.download_file("https://www.dummy.me/stuff/1234/abc/file.jpg?hash=1234")

if __name__ == "__main__":
    unittest.main()
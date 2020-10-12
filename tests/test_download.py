import unittest
from unittest import mock
from instapull import PostDownloader
from tests import mock_response


class DownloadTests(unittest.TestCase):
    def test_download_by_user(self):
        pass

    def test_download_by_tag(self):
        pass

    @mock.patch('instapull.requests.get', side_effect=mock_response)
    def test_load_user_posts(self, mock_get):
        download = PostDownloader()
        feed = download._load_user_feed("frodehus")
        self.assertIsNotNone(feed)
        self.assertIn("posts", feed)
        self.assertIn("page", feed)
        self.assertTrue(len(feed["posts"]) == 12)
    
    @mock.patch('instapull.requests.get', side_effect=mock_response)
    def test_load_next_page(self, mock_get):
        download = PostDownloader()
        feed = download._load_user_feed("frodehus")
        page_info = feed["page"]
        download._get_next_page(page_info)
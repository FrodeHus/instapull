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
        posts = download._load_user_feed("frodehus")
        self.assertIsNotNone(posts)
        self.assertTrue(len(posts) == 12)
        
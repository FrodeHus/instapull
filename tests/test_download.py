from instapull.classes import UserDownload
import unittest
from unittest import mock
from instapull import PostDownloader, PageInfo
from tests import mock_response

class DownloadTests(unittest.TestCase):
    def test_download_by_user(self):
        pass

    def test_download_by_tag(self):
        pass

    @mock.patch('instapull.requests.get', side_effect=mock_response)
    def test_load_user_posts(self, mock_get):
        download = PostDownloader()
        feed = download._load_feed("frodehus", UserDownload())
        self.assertIsNotNone(feed)
        self.assertIn("posts", feed)
        self.assertIn("page", feed)
        self.assertTrue(len(feed["posts"]) == 12)
    
    @mock.patch('instapull.requests.get', side_effect=mock_response)
    def test_load_next_page(self, mock_get):
        download = PostDownloader()
        page_info = PageInfo({
                "has_next_page": True,
                "end_cursor": "QVFEMGVEeTBjY0d1M2V1cmxmSnBNT0lPclI1MHdPTXc5RG9UU0NHcjNUWGxFU1pyNWpQVy1adEtkVGl0WGFXXzRqeXg2SHQ1VG9fZHRmazdQY0c5T2M0VQ=="
                })
        query_hash = "56a7068fea504063273cc2120ffd54f3"
        type = UserDownload()
        feed_page = download._get_next_page("123", page_info, type)
        self.assertIsNotNone(feed_page)
        self.assertIn("posts", feed_page)
        self.assertIn("page", feed_page)
    
    def test_generate_user_page_request(self):
        download = PostDownloader()
        page_info = PageInfo({
                        "has_next_page": True,
                        "end_cursor": "QVFEMGVEeTBjY0d1M2V1cmxmSnBNT0lPclI1MHdPTXc5RG9UU0NHcjNUWGxFU1pyNWpQVy1adEtkVGl0WGFXXzRqeXg2SHQ1VG9fZHRmazdQY0c5T2M0VQ=="
                        })
        expected = "%7B%22id%22%3A%22123%22%2C%22first%22%3A12%2C%22after%22%3A%22QVFEMGVEeTBjY0d1M2V1cmxmSnBNT0lPclI1MHdPTXc5RG9UU0NHcjNUWGxFU1pyNWpQVy1adEtkVGl0WGFXXzRqeXg2SHQ1VG9fZHRmazdQY0c5T2M0VQ%3D%3D%22%7D"
        actual = download._generate_page_request("id", "123", page_info)
        self.assertEqual(expected, actual)

    def test_generate_tag_page_request(self):
        download = PostDownloader()
        page_info = PageInfo({
                        "has_next_page": True,
                        "end_cursor": "QVFEMGVEeTBjY0d1M2V1cmxmSnBNT0lPclI1MHdPTXc5RG9UU0NHcjNUWGxFU1pyNWpQVy1adEtkVGl0WGFXXzRqeXg2SHQ1VG9fZHRmazdQY0c5T2M0VQ=="
                        })
        expected = "%7B%22tag_name%22%3A%22instagram%22%2C%22first%22%3A12%2C%22after%22%3A%22QVFEMGVEeTBjY0d1M2V1cmxmSnBNT0lPclI1MHdPTXc5RG9UU0NHcjNUWGxFU1pyNWpQVy1adEtkVGl0WGFXXzRqeXg2SHQ1VG9fZHRmazdQY0c5T2M0VQ%3D%3D%22%7D"
        actual = download._generate_page_request("tag_name", "instagram", page_info)
        self.assertEqual(expected, actual)
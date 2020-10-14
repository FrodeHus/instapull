from instapull.classes import TagDownload, UserDownload
import unittest
from unittest import mock
from instapull import PostDownloader
from tests import mock_response

@mock.patch('instapull.requests.get', side_effect=mock_response)
class RetrieveHashTest(unittest.TestCase):
    def test_retrieve_user_query_hash(self, mock_get):
        userDownload = UserDownload()
        self.assertEqual('56a7068fea504063273cc2120ffd54f3', userDownload.query_hash)
    
    def test_retrieve_tag_query_hash(self, mock_get):
        tagDownload = TagDownload()
        self.assertEqual('9b498c08113f1e09617a1703c22b2f32', tagDownload.query_hash)


@mock.patch('instapull.PostDownloader._save_file')
@mock.patch('instapull.requests.get', side_effect=mock_response)
class FileTests(unittest.TestCase):
    def test_filename_parser(self, mock_get, mock_save):
        s = "https://www.dummy.me/stuff/1234/abc/file.jpg?hash=1234"
        downloader = PostDownloader()
        filename = downloader._get_filename(s)
        self.assertEqual(filename, 'file.jpg')

    def test_save(self, mock_get, mock_save):
        downloader = PostDownloader()
        downloader._download_file("https://www.dummy.me/stuff/1234/abc/file.jpg?hash=1234")
        mock_save.assert_has_calls([mock.call("file.jpg", "testfilecontent")])

if __name__ == "__main__":
    unittest.main()
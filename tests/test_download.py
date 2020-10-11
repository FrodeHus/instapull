import unittest
from unittest import mock
from instapull.downloader import PostDownloader

class RetrieveHashTest(unittest.TestCase):
    def test_retrieve_user_query_hash(self):
        downloader = PostDownloader(user="test")
        hash = downloader.retrieve_user_query_hash()
        self.assertEquals('56a7068fea504063273cc2120ffd54f3', hash)
    
    def test_retrieve_tag_query_hash(self):
        downloader = PostDownloader(tag="test")
        hash = downloader.retrieve_tag_query_hash()
        self.assertEquals('9b498c08113f1e09617a1703c22b2f32', hash)

class FileTests(unittest.TestCase):
    def test_filename_parser(self):
        s = "https://www.dummy.me/stuff/1234/abc/file.jpg?hash=1234"
        downloader = PostDownloader()
        filename = downloader._get_filename(s)
        self.assertEquals(filename, 'file.jpg')
        
if __name__ == "__main__":
    unittest.main()
import unittest
from unittest import mock
from instapull import PostDownloader
from tests.mock_util import load_mock_data
from tests.mock_requests import MockResponse

request_mock = None
mock_responses = {}
def setUpModule():
    global mock_responses
    instagram_html = load_mock_data("instagram_html.gz")
    tag_html = load_mock_data("instagram_tag_html.gz")
    consumer_js = load_mock_data('consumer_js.gz')
    tagpage_js = load_mock_data('tagpage_js.gz')
    mock_responses['https://www.instagram.com'] = instagram_html
    mock_responses['https://www.instagram.com/explore/tags'] = tag_html
    mock_responses['https://www.instagram.com/static/bundles/metro/Consumer.js/0c9bf11a8e5b.js'] = consumer_js
    mock_responses['https://www.instagram.com/static/bundles/metro/TagPageContainer.js/4c6d41a24709.js'] = tagpage_js
    mock_responses['https://www.dummy.me/stuff/1234/abc/file.jpg?hash=1234'] = "testfilecontent"

def mock_response(*args, **kwargs):
    global mock_responses
    url = args[0]
    if url in mock_responses:
        return MockResponse(mock_responses[url], 200)
    return MockResponse(None, 404)

@mock.patch('instapull.requests.get', side_effect=mock_response)
class RetrieveHashTest(unittest.TestCase):
    def test_retrieve_user_query_hash(self, mock_get):
        downloader = PostDownloader()
        hash = downloader._retrieve_user_query_hash()
        self.assertEquals('56a7068fea504063273cc2120ffd54f3', hash)
    
    def test_retrieve_tag_query_hash(self, mock_get):
        downloader = PostDownloader()
        hash = downloader._retrieve_tag_query_hash()
        self.assertEquals('9b498c08113f1e09617a1703c22b2f32', hash)


@mock.patch('instapull.PostDownloader._save_file')
@mock.patch('instapull.requests.get', side_effect=mock_response)
class FileTests(unittest.TestCase):
    def test_filename_parser(self, mock_get, mock_save):
        s = "https://www.dummy.me/stuff/1234/abc/file.jpg?hash=1234"
        downloader = PostDownloader()
        filename = downloader._get_filename(s)
        self.assertEquals(filename, 'file.jpg')

    def test_save(self, mock_get, mock_save):
        downloader = PostDownloader()
        downloader._download_file("https://www.dummy.me/stuff/1234/abc/file.jpg?hash=1234")
        mock_save.assert_has_calls([mock.call("file.jpg", "testfilecontent")])

if __name__ == "__main__":
    unittest.main()
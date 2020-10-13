import os
import gzip
from tests.mock_requests import MockResponse


def load_mock_data(filename):
    """Load a gzip test data file."""
    cur_fp = os.path.realpath(__file__)
    cur_dir = os.path.dirname(cur_fp)
    fp = os.path.join(cur_dir, "mocks", filename)
    with gzip.open(fp, "rb") as fh:
        content = fh.read().decode("utf-8")
        return content


mock_responses = {}


def load_mock_responses():
    instagram_html = load_mock_data("instagram_html.gz")
    tag_html = load_mock_data("instagram_tag_html.gz")
    consumer_js = load_mock_data("consumer_js.gz")
    tagpage_js = load_mock_data("tagpage_js.gz")
    mock_responses["https://www.instagram.com"] = instagram_html
    mock_responses["https://www.instagram.com/explore/tags"] = tag_html
    mock_responses[
        "https://www.instagram.com/static/bundles/metro/Consumer.js/0c9bf11a8e5b.js"
    ] = consumer_js
    mock_responses[
        "https://www.instagram.com/static/bundles/metro/TagPageContainer.js/4c6d41a24709.js"
    ] = tagpage_js
    mock_responses[
        "https://www.dummy.me/stuff/1234/abc/file.jpg?hash=1234"
    ] = "testfilecontent"
    mock_responses["https://www.instagram.com/frodehus/?__a=1"] = load_mock_data(
        "user_feed.gz"
    )
    mock_responses[
        "https://www.instagram.com/graphql/query/?query_hash=56a7068fea504063273cc2120ffd54f3&variables=%7B%22id%22%3A%22123%22%2C%22first%22%3A12%2C%22after%22%3A%22QVFEMGVEeTBjY0d1M2V1cmxmSnBNT0lPclI1MHdPTXc5RG9UU0NHcjNUWGxFU1pyNWpQVy1adEtkVGl0WGFXXzRqeXg2SHQ1VG9fZHRmazdQY0c5T2M0VQ%3D%3D%22%7D"
    ] = load_mock_data("user_feed_page.gz")


def mock_response(*args, **kwargs):
    global mock_responses
    url = args[0]
    if url in mock_responses:
        return MockResponse(mock_responses[url], 200)
    return MockResponse(None, 404)


load_mock_responses()

import unittest
from unittest import mock
from instapull.downloader import PostDownloader

def mocked_request_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code
        
        def text(self):
            return self.text
        
    if args[0] == "https://www.instagram.com":
        html = """
                <link rel="preload" href="/static/bundles/metro/ConsumerUICommons.css/bae63654c3c6.css" as="style" type="text/css" crossorigin="anonymous" />
<link rel="preload" href="/static/bundles/metro/Consumer.js/0c9bf11a8e5b.js" as="script" type="text/javascript" crossorigin="anonymous" />
<link rel="preload" href="/static/bundles/metro/FeedPageContainer.js/f14562f11696.js" as="script" type="text/javascript" crossorigin="anonymous" />
        """
        return MockResponse(html, 200)
    elif args[0] == "https://www.instagram.com/explore/tags":
        html = """
        <link rel="preload" href="/static/bundles/metro/ConsumerAsyncCommons.js/c4ca4238a0b9.js" as="script" type="text/javascript" crossorigin="anonymous" />
<link rel="preload" href="/static/bundles/metro/Consumer.js/0c9bf11a8e5b.js" as="script" type="text/javascript" crossorigin="anonymous" />
<link rel="preload" href="/static/bundles/metro/TagPageContainer.js/4c6d41a24709.js" as="script" type="text/javascript" crossorigin="anonymous" />
        <script type="text/javascript">
        """
        return MockResponse(html, 200)
    elif args[0] == "https://www.instagram.com/static/bundles/metro/Consumer.js/0c9bf11a8e5b.js":
        js = """
            return u ? null : null === (s = t.profilePosts.byUserId.get(n)) || void 0 === s ? void 0 : s.pagination
        },
        queryId: "56a7068fea504063273cc2120ffd54f3",
        queryParams: function(t) {
            return {
                id: t
        """
        return MockResponse(js, 200)
    elif args[0] == "https://www.instagram.com/static/bundles/metro/TagPageContainer.js/4c6d41a24709.js":
        js = 'getState:function(t,n){return i(d[2])(t.tagMedia.byTagName.get(n)).pagination},queryId:"9b498c08113f1e09617a1703c22b2f32",queryParams:function(t){return{tag_name:t}},onUpdate:function(t,n,o){var u,_=[];if(n){var c=i(d[2])(n.h'
        return MockResponse(js, 200)
    return MockResponse(None, 404)
    

class RetrieveHashTest(unittest.TestCase):
    @mock.patch('requests.get', side_effect=mocked_request_get)
    def test_retrieve_user_query_hash(self, mock_get):
        downloader = PostDownloader(user="test")
        hash = downloader.retrieve_user_query_hash()
        self.assertEquals('56a7068fea504063273cc2120ffd54f3', hash)
    
    @mock.patch('requests.get', side_effect=mocked_request_get)
    def test_retrieve_tag_query_hash(self, mock_get):
        downloader = PostDownloader(tag="test")
        hash = downloader.retrieve_tag_query_hash()
        self.assertEquals('9b498c08113f1e09617a1703c22b2f32', hash)


if __name__ == "__main__":
    unittest.main()
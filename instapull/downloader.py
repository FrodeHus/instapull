import requests
import re
class PostDownloader:
    def __init__(self, user = None, tag = None):
        self.user = user
        self.tag = tag
    
    def retrieve_user_query_hash(self):
        return self._retrieve_query_hash("https://www.instagram.com", r"static\/bundles\/.+\/Consumer\.js\/.+\.js", "profilePosts.byUserId")

    def retrieve_tag_query_hash(self):
        return self._retrieve_query_hash("https://www.instagram.com/explore/tags", r"static\/bundles\/metro\/TagPageContainer\.js\/[a-z0-9]+\.js", "tagMedia.byTagName")

    def _retrieve_query_hash(self, url : str, bundleSearcher: str, functionName: str):
        response = requests.get(url)
        html = response.text
        scripts = re.findall(bundleSearcher, html)
        response = requests.get(f"https://www.instagram.com/{scripts[0]}")
        js = response.text
        js = js[js.index(f"{functionName}.get") :]
        match = re.findall(r"([a-fA-F\d]{32})", js)
        return match[0]
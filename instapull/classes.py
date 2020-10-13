from requests.api import post
import re
import requests

class Post:
    def __init__(self, data : dict):
        node = data["node"]
        self.type = node["__typename"]
        self.id = node["id"]
        self.display_url = node["display_url"]
        self.is_video = bool(node["is_video"])
        self.is_media_collection = self.type == "GraphSidecar"
        self.media = []
        if "edge_sidecar_to_children" in node:
            self.media = list(map(Post,node["edge_sidecar_to_children"]["edges"]))

class PageInfo:
    def __init__(self, data : dict):
        self.has_next_page = bool(data["has_next_page"])
        self.cursor = data["end_cursor"]

class DownloadType:
    def __init__(self, page_id_property : str, post_property : str, metadata_property : str, feed_url : str):
        self.page_id_property = page_id_property
        self.post_property = post_property
        self.metadata_property = metadata_property
        self.feed_url = feed_url
        self.query_hash = None

    def _retrieve_user_query_hash(self):
        return self._retrieve_query_hash(
            "https://www.instagram.com",
            r"static\/bundles\/.+\/Consumer\.js\/.+\.js",
            "profilePosts.byUserId",
        )

    def _retrieve_tag_query_hash(self):
        return self._retrieve_query_hash(
            "https://www.instagram.com/explore/tags",
            r"static\/bundles\/metro\/TagPageContainer\.js\/[a-z0-9]+\.js",
            "tagMedia.byTagName",
        )

    def _retrieve_query_hash(self, url: str, bundleSearcher: str, functionName: str):
        response = requests.get(url)
        html = response.text
        scripts = re.findall(bundleSearcher, html)
        response = requests.get(f"https://www.instagram.com/{scripts[0]}")
        js = response.text
        js = js[js.index(f"{functionName}.get") :]
        match = re.findall(r"([a-fA-F\d]{32})", js)
        return match[0]

class TagDownload(DownloadType):
    def __init__(self) -> None:
        super().__init__("tag_name", "edge_hashtag_to_media", "hashtag", "https://www.instagram.com/explore/tags/{}/?__a=1")
        self.query_hash = self._retrieve_tag_query_hash()

class UserDownload(DownloadType):
    def __init__(self) -> None:
        super().__init__("id", "edge_owner_to_timeline_media", "user", "https://www.instagram.com/{}/?__a=1")
        self.query_hash = self._retrieve_user_query_hash()        
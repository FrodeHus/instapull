from requests.api import post


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

class TagDownload(DownloadType):
    def __init__(self) -> None:
        super().__init__("tag_name", "edge_hashtag_to_media", "hashtag", "https://www.instagram.com/explore/tags/{}/?__a=1")

class UserDownload(DownloadType):
    def __init__(self) -> None:
        super().__init__("id", "edge_owner_to_timeline_media", "user", "https://www.instagram.com/{}/?__a=1")
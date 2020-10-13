import requests
import re
import os
import urllib
from .exceptions import DownloadFailed
from .classes import Post, PageInfo


class PostDownloader:
    def __init__(self, download_directory=""):
        self.current_download_count = 0
        self.total_post_count = 0
        self.max_posts_to_download = 12
        self.download_directory = download_directory
        self._query_hash = None

    def download_by_user(self, user_name: str, max_posts: int = 12):
        self._query_hash = self._retrieve_user_query_hash()
        feed = self._load_user_feed(user_name)
        page = feed["page"]
        posts = feed["posts"]
        id = feed["id"]
        self._download_posts(id, posts, page)

    def download_by_tag(self, hash_tag: str):
        self._query_hash = self._retrieve_tag_query_hash()

    def _download_posts(self, id: str, posts: list, page_info: PageInfo):
        for post in posts:
            self._download_file(post.display_url)

        if page_info.has_next_page:
            feed = self._get_next_page(id, page)
            page_info = feed["page"]
            posts = feed["posts"]

    def _load_user_feed(self, user_name: str):
        url = f"https://www.instagram.com/{user_name}/?__a=1"
        response = requests.get(url)
        if response.status_code != 200:
            raise DownloadFailed()

        metadata = response.json()
        user_data = metadata["graphql"]["user"]
        timeline_media = user_data["edge_owner_to_timeline_media"]
        edges = timeline_media["edges"]
        page_info = PageInfo(timeline_media["page_info"])
        posts = map(Post, edges)
        return {"id": user_data["id"], "page": page_info, "posts": list(posts)}

    def _get_next_page(self, id: str, page_info: PageInfo):
        url = (
            f"https://www.instagram.com/graphql/query/?query_hash={self._query_hash}&variables="
            + self._generate_page_request("id", id, page_info)
        )

        response = requests.get(url)
        if response.status_code != 200:
            raise DownloadFailed()

        data = response.json()["data"]["user"]["edge_owner_to_timeline_media"]
        page_info = PageInfo(data["page_info"])
        posts = map(Post, data["edges"])
        return {"page": page_info, "posts": list(posts)}

    def _generate_page_request(
        self, page_id_property: str, id: str, page_info: PageInfo
    ):
        urlparams = (
            f'{{"{page_id_property}":"{id}","first":12,"after":"{page_info.cursor}"}}'
        )
        return urllib.parse.quote(urlparams)

    def _download_file(self, url: str):
        self.current_download_count += 1
        filename = self._get_filename(url)
        response = requests.get(url)
        if response.status_code == 200:
            self._save_file(filename, response.content)
        else:
            raise DownloadFailed()

    def _save_file(self, filename: str, content: bytes):
        with open(filename, "wb") as file:
            file.write(content)

    def _get_filename(self, url: str):
        segments = url.split("/")
        filename = segments[-1]
        filename = filename[: filename.index("?")]
        filename = os.path.join(self.download_directory, filename)
        return filename

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

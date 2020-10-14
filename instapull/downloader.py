import sys
import requests
import os
import urllib
from .exceptions import DownloadFailed
from .classes import DownloadType, Post, PageInfo, TagDownload, UserDownload

def callback(downloadedPost : Post):
    pass

class PostDownloader:
    def __init__(self, download_directory=""):
        self.current_download_count = 0
        self.total_post_count = 0
        self.max_posts_to_download = 12
        self.download_directory = download_directory
        self._query_hash = None
        self._download_count = 0

    def _download_posts(self, id: str, posts: list, page_info: PageInfo, type : DownloadType, max_posts : int, callback = None):
        for post in posts:
            if self._download_count > max_posts:
                return

            try:
                if post.is_media_collection:
                    for media in post.media:
                        self._download_file(media.display_url)
                else:
                    self._download_file(post.display_url)
                self._download_count += 1
                if(callback):
                    callback(post)
            except DownloadFailed as exc:
                print("Error: " + exc.message)
                sys.exit(1)

        if page_info.has_next_page:
            feed = self._get_next_page(id, page_info, type)
            page_info = feed["page"]
            posts = feed["posts"]
            self._download_posts(id, posts, page_info, type, max_posts, callback)

    def _load_feed(self, identifier : str, type : DownloadType):
        url = type.feed_url.format(identifier)
        response = requests.get(url)
        if response.status_code != 200:
            raise DownloadFailed("Could not get feed - probably does not exist")

        metadata = response.json()
        feed_data = metadata["graphql"][type.metadata_property]
        timeline_media = feed_data[type.post_property]
        edges = timeline_media["edges"]
        page_info = PageInfo(timeline_media["page_info"])
        posts = map(Post, edges)
        return {"id": feed_data["id"], "page": page_info, "posts": list(posts), "count": timeline_media["count"]}

    def _get_next_page(self, id: str, page_info: PageInfo, type : DownloadType):
        url = (
            f"https://www.instagram.com/graphql/query/?query_hash={type.query_hash}&variables="
            + self._generate_page_request(type.page_id_property, id, page_info)
        )

        response = requests.get(url)
        if response.status_code != 200:
            raise DownloadFailed(f"Failed to retrieve next page of feed: {response.status_code} - {response.reason}")

        data = response.json()["data"][type.metadata_property][type.post_property]
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
            raise DownloadFailed(f"Failed to download file (status code: {response.status_code})")

    def _save_file(self, filename: str, content: bytes):
        with open(filename, "wb") as file:
            file.write(content)

    def _get_filename(self, url: str):
        segments = url.split("/")
        filename = segments[-1]
        filename = filename[: filename.index("?")]
        filename = os.path.join(self.download_directory, filename)
        return filename

class UserFeedDownload(PostDownloader):
    def __init__(self, user_name : str, download_directory : str = "") -> None:
        super().__init__(download_directory)
        self._user_name = user_name
        self._download_type = UserDownload()

    def post_count(self):
        feed = self._load_feed(self._user_name, self._download_type)
        return feed["count"]        

    def download(self, max_posts: int = 12, callback = None):
        feed = self._load_feed(self._user_name, self._download_type)
        if max_posts > feed["count"]:
            max_posts = feed["count"]
        page = feed["page"]
        posts = feed["posts"]
        id = feed["id"]
        self._download_posts(id, posts, page, self._download_type, max_posts, callback)

class HashTagFeedDownload(PostDownloader):
    def __init__(self, hash_tag : str, download_directory : str = "") -> None:
        super().__init__(download_directory)
        self._hash_tag = hash_tag
        self._download_type = TagDownload()

    def post_count(self):
        feed = self._load_feed(self._hash_tag, self._download_type)
        return feed["count"]        


    def download(self,max_posts: int = 12, callback = None):
        feed = self._load_feed(self._hash_tag, self._download_type)
        if max_posts > feed["count"]:
            max_posts = feed["count"]
        page = feed["page"]
        posts = feed["posts"]        
        self._download_posts(self._hash_tag, posts, page, self._download_type, max_posts, callback)
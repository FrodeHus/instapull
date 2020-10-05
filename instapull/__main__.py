import requests
import json
import urllib.parse
import re
import argparse
import sys

current_page_count = 0
max_pages = 0
media_count = 0
current_download_count = 0

parser = argparse.ArgumentParser(
    prog="instapull",
    usage="%(prog)s [options] instagram-user",
    description="Pull images from a Instagram feed",
)

parser.add_argument(
    "instagram_user",
    type=str,
    help="User name of the Instagram feed to pull images from",
)
parser.add_argument(
    "-m",
    "--max-pages",
    action="store",
    type=int,
    help="Pull a maximum number of pages (12 images per page)",
)
args = parser.parse_args()


def main():
    global max_pages, args
    user = args.instagram_user
    if "max_pages" in args:
        max_pages = args.max_pages

    pull_feed_images(user)


def pull_feed_images(user: str):
    print(f"* Looking up {user}")
    response = requests.get(f"https://www.instagram.com/{user}/?__a=1")
    metadata = response.json()
    user_data = metadata["graphql"]["user"]
    print(f"* Bio: {user_data['biography']}")
    timeline_media = user_data["edge_owner_to_timeline_media"]
    global media_count
    media_count = timeline_media["count"]
    print(f"* Found {media_count} images in timeline")
    page_info = timeline_media["page_info"]
    cursor_token = page_info["end_cursor"]
    has_next_page = page_info["has_next_page"]
    user_id = user_data["id"]
    edges = timeline_media["edges"]
    download(edges)

    if has_next_page:
        query_hash = retrieve_query_hash()
        get_next_page(query_hash, user_id, cursor_token)


def get_next_page(query_hash: str, user_id: str, cursor_token: str):
    urlparams = f'{{"id":"{user_id}","first":12,"after":"{cursor_token}"}}'
    url = (
        f"https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables="
        + urllib.parse.quote(urlparams)
    )
    response = requests.get(url)
    if response.status_code != 200:
        print(f"- Failed retrieving next page: {response.reason}")
        sys.exit(1)

    data = response.json()["data"]["user"]["edge_owner_to_timeline_media"]
    cursor_token = data["page_info"]["end_cursor"]
    has_next_page = data["page_info"]["has_next_page"]
    download(data["edges"])
    global max_pages, current_page_count
    current_page_count += 1
    if max_pages != 0 and current_page_count >= max_pages:
        print("* Reached max page count, stopping...")
        sys.exit(0)

    if has_next_page:
        get_next_page(query_hash, user_id, cursor_token)


def download(media_data: dict):
    for edge in media_data:
        url = edge["node"]["display_url"]
        download_file(url)


def download_file(url: str):
    global current_download_count, media_count
    current_download_count += 1
    filename = get_filename(url)
    print(f"* [{current_download_count}/{media_count}] Downloading {filename}...")
    response = requests.get(url)
    with open(filename, "wb") as file:
        file.write(response.content)


def retrieve_query_hash():
    response = requests.get("https://www.instagram.com")
    html = response.text
    scripts = re.findall(r"static\/bundles\/.+\/Consumer\.js\/.+\.js", html)
    response = requests.get(f"https://www.instagram.com/{scripts[0]}")
    js = response.text
    js = js[js.index("profilePosts.byUserId.get") :]
    match = re.findall(r"([a-fA-F\d]{32})", js)
    return match[0]


def get_filename(url: str):
    segments = url.split("/")
    filename = segments[-1]
    filename = filename[: filename.index("?")]
    return filename


if __name__ == "__main__":
    main()

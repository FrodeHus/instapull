import requests
import json
import urllib.parse
import re
import argparse
import sys
import os
from alive_progress import alive_bar

media_count = 0
current_download_count = 0
max_posts = 12
download_directory = ""
query_hash = None

parser = argparse.ArgumentParser(
    prog="instapull",
    description="Pull posts from Instagram",
)

group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-u",
    "--user",
    type=str,
    help="User name of the Instagram feed to pull images from",
)
group.add_argument("-t", "--tag", help="Download posts with this tag", type=str)

parser.add_argument(
    "--videos",
    action="store_true",
    help="Download videos (default is to just download the video thumbnail)",
)

group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-a",
    "--all",
    action="store_true",
    help="Download entire feed",
)
group.add_argument(
    "-n",
    "--num-posts",
    type=int,
    action="store",
    help="Set the max number of posts to download (default: 12)",
)

group = parser.add_mutually_exclusive_group()
group.add_argument("-c", "--create-dir", help="Create directory <instagram_user>", action="store_true")
group.add_argument(
    "-o",
    "--output-dir",
    type=str,
    help="Save downloads to specified directory (will create directory if it does not exist)",
)


args = parser.parse_args()


def main():
    global max_posts, args, user, hashtag
    if args.num_posts:
        max_posts = args.num_posts

    create_directory(args)
    pull_feed(args)

def create_directory(args):
    global download_directory

    if args.user and args.create_dir:
        os.makedirs(args.user, exist_ok=True)
        download_directory = args.user

    elif args.tag and args.create_dir:
        os.makedirs(args.tag, exist_ok=True)
        download_directory = args.tag

    elif args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        download_directory = args.output_dir

def pull_feed(args):
    global query_hash
    url = None
    if args.user:
        query_hash = retrieve_user_query_hash()
        pull_user_posts(args.user)
    elif args.tag:
        query_hash = retrieve_tag_query_hash()
        pull_tagged_posts(args.tag)

def pull_user_posts(user):
    url = f"https://www.instagram.com/{user}/?__a=1"
    response = requests.get(url)
    if response.status_code != 200:
        print("- Target was not found")
        sys.exit(1)

    global max_posts, current_download_count
    metadata = response.json()
    user_data = metadata["graphql"]["user"]
    print(f"Bio: {user_data['biography']}")
    timeline_media = user_data["edge_owner_to_timeline_media"]
    global media_count, args
    media_count = get_post_count(timeline_media)
    
    pull_posts(user_data["id"], timeline_media)

def pull_posts(identifier, timeline_media):
    global max_posts
    if args.all:
        max_posts = media_count

    with alive_bar(max_posts, bar='blocks') as bar:
        page_info = timeline_media["page_info"]
        cursor_token = page_info["end_cursor"]
        has_next_page = page_info["has_next_page"]
        edges = timeline_media["edges"]
        download_post(edges, bar)

        if has_next_page:
            get_next_page(identifier, cursor_token, bar)

def pull_tagged_posts(tag):
    url = f"https://www.instagram.com/explore/tags/{tag}/?__a=1"
    response = requests.get(url)
    if response.status_code != 200:
        print("- Target was not found")
        sys.exit(1)

    global max_posts, current_download_count
    metadata = response.json()
    user_data = metadata["graphql"]["hashtag"]
    timeline_media = user_data["edge_hashtag_to_media"]
    global media_count
    media_count = get_post_count(timeline_media)

    pull_posts(tag, timeline_media)

def get_post_count(data):
    return data["count"]

def get_next_page(identifier: str, cursor_token: str, progress):
    global args, query_hash
    idprop = "id"
    if args.tag:
        idprop = "tag_name"
    urlparams = f'{{"{idprop}":"{identifier}","first":12,"after":"{cursor_token}"}}'
    url = (
        f"https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables="
        + urllib.parse.quote(urlparams)
    )
    response = requests.get(url)
    if response.status_code != 200:
        print(f"- Failed retrieving next page: {response.reason}")
        sys.exit(1)
    data = None
    if args.user:
        data = response.json()["data"]["user"]["edge_owner_to_timeline_media"]
    elif args.tag:
        data = response.json()["data"]["hashtag"]["edge_hashtag_to_media"]
    cursor_token = data["page_info"]["end_cursor"]
    has_next_page = data["page_info"]["has_next_page"]
    download_post(data["edges"], progress)

    if has_next_page:
        get_next_page(identifier, cursor_token, progress)


def download_post(media_data: dict, progress):
    global args, current_download_count, max_posts
    for edge in media_data:
        node = edge["node"]
        if node["is_video"] and args.videos:
            url = node["video_url"]
        else:
            url = node["display_url"]

        download_file(url)

        if not args.tag and node["__typename"] == "GraphSidecar":
            # should probably group these together somehow as they are posted as a group
            sidecar_children = node["edge_sidecar_to_children"]
            download_post(sidecar_children["edges"], progress)

        progress()
        if current_download_count >= max_posts and not args.all:
            print("Done.")
            sys.exit(0)



def download_file(url: str):
    global current_download_count, media_count, max_posts, args, download_directory
    current_download_count += 1
    filename = get_filename(url)
    response = requests.get(url)
    with open(filename, "wb") as file:
        file.write(response.content)


def retrieve_user_query_hash():
    return _retrieve_query_hash("https://www.instagram.com", r"static\/bundles\/.+\/Consumer\.js\/.+\.js", "profilePosts.byUserId")

def retrieve_tag_query_hash():
    return _retrieve_query_hash("https://www.instagram.com/explore/tags", r"static\/bundles\/metro\/TagPageContainer\.js\/[a-z0-9]+\.js", "tagMedia.byTagName")

def _retrieve_query_hash(url : str, bundleSearcher: str, functionName: str):
    response = requests.get(url)
    html = response.text
    scripts = re.findall(bundleSearcher, html)
    response = requests.get(f"https://www.instagram.com/{scripts[0]}")
    js = response.text
    js = js[js.index(f"{functionName}.get") :]
    match = re.findall(r"([a-fA-F\d]{32})", js)
    return match[0]

def get_filename(url: str):
    global download_directory
    segments = url.split("/")
    filename = segments[-1]
    filename = filename[: filename.index("?")]
    filename = os.path.join(download_directory, filename)
    return filename


if __name__ == "__main__":
    main()

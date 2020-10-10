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
max_files = 12

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
    "--num-files",
    type=int,
    action="store",
    help="Set the max number of files to download (default: 12)",
)

group = parser.add_mutually_exclusive_group()
group.add_argument("-c", "--create-dir", help="Create directory <instagram_user>", action="store_true")
group.add_argument(
    "-o",
    "--output-dir",
    type=str,
    help="Save downloads to specified directory (will create directory if it does not exist",
)


args = parser.parse_args()


def main():
    global max_files, args
    if args.num_files:
        max_files = args.num_files

    user = args.instagram_user
    if args.create_dir and not os.path.exists(user):
        os.makedirs(user)

    if args.output_dir and not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    pull_feed_images(user)


def pull_feed_images(user: str):
    response = requests.get(f"https://www.instagram.com/{user}/?__a=1")
    if response.status_code != 200:
        print("- User was not found")
        sys.exit(1)

    global max_files, current_download_count
    with alive_bar(max_files, bar='blocks') as bar:
        metadata = response.json()
        user_data = metadata["graphql"]["user"]
        bar.text(f"Bio: {user_data['biography']}")
        timeline_media = user_data["edge_owner_to_timeline_media"]
        global media_count
        media_count = timeline_media["count"]
        bar.text(f"Found {media_count} images in timeline")
        page_info = timeline_media["page_info"]
        cursor_token = page_info["end_cursor"]
        has_next_page = page_info["has_next_page"]
        user_id = user_data["id"]
        edges = timeline_media["edges"]
        bar.text(f"Downloading feed from {user}")
        download(edges, bar)

        if has_next_page:
            query_hash = retrieve_query_hash()
            get_next_page(query_hash, user_id, cursor_token, bar)


def get_next_page(query_hash: str, user_id: str, cursor_token: str, progress):
    global args

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
    download(data["edges"], progress)

    if has_next_page:
        get_next_page(query_hash, user_id, cursor_token, progress)


def download(media_data: dict, progress):
    global args
    for edge in media_data:
        node = edge["node"]
        if node["is_video"] and args.videos:
            url = node["video_url"]
        else:
            url = node["display_url"]

        download_file(url, progress)

        if node["__typename"] == "GraphSidecar":
            # should probably group these together somehow as they are posted as a group
            sidecar_children = node["edge_sidecar_to_children"]
            download(sidecar_children["edges"], progress)


def download_file(url: str, progress):
    global current_download_count, media_count, max_files, args
    current_download_count += 1
    filename = get_filename(url)
    if args.output_dir:
        directory = args.output_dir
    if args.create_dir:
        directory = args.instagram_user

    filename = os.path.join(directory, get_filename(url))

    response = requests.get(url)
    with open(filename, "wb") as file:
        file.write(response.content)
    progress()
    if current_download_count >= max_files and not args.all:
        print("Done.")
        sys.exit(0)


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

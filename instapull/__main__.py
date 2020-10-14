from instapull.classes import TagDownload
import argparse
import os
from alive_progress import alive_bar
from .downloader import HashTagFeedDownload, PostDownloader, UserFeedDownload

max_posts = 12
download_directory = ""

parser = argparse.ArgumentParser(
    prog="instapull", description="Pull posts from Instagram",
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
    "-a", "--all", action="store_true", help="Download entire feed",
)
group.add_argument(
    "-n",
    "--num-posts",
    type=int,
    action="store",
    help="Set the max number of posts to download (default: 12)",
)

group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-c", "--create-dir", help="Create directory <instagram_user>", action="store_true"
)
group.add_argument(
    "-o",
    "--output-dir",
    type=str,
    help="Save downloads to specified directory (will create directory if it does not exist)",
)


args = parser.parse_args()


def main():
    global max_posts, args
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
    global download_directory, max_posts
    if args.user:
        downloader = UserFeedDownload(args.user, download_directory=download_directory)
        ensure_post_count(downloader, args)
        with alive_bar(max_posts, bar="blocks") as bar:
            downloader.download(max_posts, lambda post: bar())
    elif args.tag:
        downloader = HashTagFeedDownload(args.tag, download_directory=download_directory)
        ensure_post_count(downloader, args)


        with alive_bar(max_posts, bar="blocks") as bar:
            downloader.download(max_posts, lambda post: bar())

def ensure_post_count(downloader : PostDownloader, args):
    global max_posts
    post_count = downloader.post_count()        
    if args.all:
        max_posts = post_count
    elif max_posts > post_count:
        max_posts = post_count


if __name__ == "__main__":
    main()

# instapull
Simple tool to dump images from a Instagram timeline

![Upload Python Package](https://github.com/FrodeHus/instapull/workflows/Upload%20Python%20Package/badge.svg)


## Install

from cloned repo: `pip3 install .`

from package: `pip3 install instapull`

## Usage

```
usage: instapull [-h] [-u USER | -t TAG] [--videos] [-a | -n NUM_POSTS] [-c | -o OUTPUT_DIR]

Pull posts from Instagram

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  User name of the Instagram feed to pull images from
  -t TAG, --tag TAG     Download posts with this tag
  --videos              Download videos (default is to just download the video thumbnail)
  -a, --all             Download entire feed
  -n NUM_POSTS, --num-posts NUM_POSTS
                        Set the max number of posts to download (default: 12)
  -c, --create-dir      Create directory <instagram_user>
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Save downloads to specified directory (will create directory if it does not exist)
         
```

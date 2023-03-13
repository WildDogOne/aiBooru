import argparse
import json
from pprint import pprint

from content.config import config
from content.danbooru import danbooru
import os
from content.general import logger
import re
import yaml
from yaml.loader import SafeLoader
import hashlib


def check_description_yaml(file: str):
    """
    Check if description yaml exists

    :param file: Image file to check for description yaml
    :return: Returns true if description yaml exists
    """
    t = re.sub(r"\.([^.]*?)$", ".yaml", file, count=0, flags=0)
    if os.path.exists(t):
        return True
    else:
        return False


def hash_file(directory: str, file: str, logdir="data/"):
    """
    Appends hash to json file

    :param directory: Directory where the image files are situated
    :param file: File to hash
    :param logdir: Optional directory where to store the hashes
    :return: Returns 1 if hash is already known, meaning there is no need to push the image
    """
    known_hash = 0
    if check_description_yaml(file):
        # Make sha256 hash of file
        with open(file, 'rb', buffering=0) as f:
            bytes = f.read()
            hash = hashlib.sha256(bytes).hexdigest()
        # Dirty hack in case the script is run on Windows
        logfile = directory.replace("\\", "/")
        logfile = logdir + logfile.split("/")[-1].replace(" ", "_") + ".json"
        # Check if logfile exists
        # Load if exists
        # Else create it
        if os.path.exists(logfile):
            with open(logfile) as db_file:
                hashes = json.load(db_file)
            for x in hashes:
                for key in x:
                    if key == hash:
                        known_hash = 1
            if known_hash != 1:
                hashes.append({hash: file})
        else:
            hashes = [{hash: file}]
        with open(logfile, 'w') as db_file:
            db_file.write(json.dumps(hashes, indent=2))
    else:
        logger.warning(f"File {file} has no description yaml, will be skipped")
    return known_hash


def get_images(path: str, logdir="data/"):
    """
    Get images from path, and yield them if they are ready to be uploaded and not already sent

    :param path: Path of the directory to check for images to upload
    :param logdir: Optional directory for logdata used to track if images where alread uploaded
    :return: Yields a list of images in a generator
    """
    ext = [".png", ".jpg"]
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and file.endswith(tuple(ext)):
            f = os.path.join(path, file)
            if hash_file(path, f, logdir=logdir) == 0:
                t = re.sub(r"\.([^.]*?)$", ".yaml", f, count=0, flags=0)
                if os.path.exists(t):
                    yield f, t
                else:
                    defaults = {"rating": "s", "tags": ""}
                    with open(t, 'w') as outfile:
                        yaml.dump(defaults, outfile, default_flow_style=False)


def read_description_file(file: str):
    """
    Reads description file, and extracts information if possible.

    :param file: Description yaml of an image
    :return: Returns Tags and Rating if possible
    """
    rating = None
    tags = None
    with open(file) as f:
        data = yaml.load(f, Loader=SafeLoader)
    if data:
        if "rating" in data:
            rating = data["rating"]
        else:
            rating = None
        if "tags" in data:
            tags = []
            if type(data["tags"]) == list:
                for x in data["tags"]:
                    x = x.replace(" ", "_")
                    if x not in tags:
                        tags.append(x)
                tags = " ".join(tags)
            else:
                tags = data["tags"]
    return rating, tags


def upload_directory(directory: str):
    """
    This function is used to upload images from a directory to Danbooru

    :param directory: Directory to scan for Images and upload them
    :return: Nothing
    """
    db = danbooru(config)

    for file, description in get_images(directory):
        tags = ""
        rating = "s"
        if description:
            x, y = read_description_file(description)
            if x:
                rating = x
            if y:
                tags = y
        logger.info(file)
        logger.info(tags)
        logger.info(rating)
        db.create_post(filename=file, tag_string=tags, rating=rating)
    logger.info("Done Processing Images")

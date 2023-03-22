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

from content.tagger import evaluate_image


def hash_file(directory: str, file: str, logdir: str = "data/"):
    """
    Appends hash to json file

    :param directory: Directory where the image files are situated
    :param file: File to hash
    :param logdir: Optional directory where to store the hashes
    :return: Returns 1 if hash is already known, meaning there is no need to push the image
    """
    known_hash = 0
    known_description_hash = 0
    description_file = re.sub(r"\.([^.]*?)$", ".yaml", file, count=0, flags=0)
    if os.path.exists(description_file):
        # Make sha256 hash of file
        with open(file, 'rb', buffering=0) as f:
            bytes = f.read()
            file_hash = hashlib.sha256(bytes).hexdigest()
        with open(description_file, 'rb', buffering=0) as f:
            bytes = f.read()
            description_file_hash = hashlib.sha256(bytes).hexdigest()

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
                    if key == file_hash:
                        known_hash = 1
                    if key == description_file_hash:
                        known_description_hash = 1
            if known_hash != 1:
                hashes.append({file_hash: file})
            if known_description_hash != 1:
                hashes.append({description_file_hash: description_file})
        else:
            hashes = [{file_hash: file, description_file_hash: description_file}]
        with open(logfile, 'w') as db_file:
            db_file.write(json.dumps(hashes, indent=2))
    else:
        logger.warning(f"File {file} has no description yaml, will be skipped")
    if known_hash == 1 and known_description_hash == 1:
        logger.debug(f"File {file} does not need to be synced")
        return False
    else:
        logger.debug(f"File {file} needs to be synced")
        return True


def get_images(path: str, force: bool, logdir: str = "data/", tagging: bool = False):
    """
    Get images from path, and yield them if they are ready to be uploaded and not already sent

    :param path: Path of the directory to check for images to upload
    :param force: Boolean value, if true the upload of all images will be enforced
    :param logdir: Optional directory for logdata used to track if images where alread uploaded
    :param tagging: Boolean value, if true DeepBooru will be used to make a guess of what tags could be used
    :return: Yields a list of images in a generator
    """
    ext = [".png", ".jpg"]
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and file.endswith(tuple(ext)):
            f = os.path.join(path, file)
            if hash_file(path, f, logdir=logdir) or force:
                t = re.sub(r"\.([^.]*?)$", ".yaml", f, count=0, flags=0)
                if os.path.exists(t):
                    yield f, t
                else:
                    if tagging:
                        tags, rating = evaluate_image(f)
                        if rating == "rating:safe":
                            rating = "g"  # General
                        elif rating == "rating:questionable":
                            rating = "q"  # Questionable
                        elif rating == "rating:explicit":
                            rating = "e"  # Explicit
                        else:
                            logger.error(f"Don't know what to do with {rating}")
                            quit()
                        logger.info(f"Guessing tags for Image {file}")
                        defaults = {"rating": rating, "tags": tags}
                        # quit()
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


def upload_directory(directory: str = None, force: bool = False, tagging: bool = False):
    """
    This function is used to upload images from a directory to Danbooru

    :param directory: Directory to scan for Images and upload them
    :param force: Boolean value, if true the upload of all images will be enforced
    :param tagging: Boolean value, if true DeepBooru will be used to make a guess of what tags could be used
    :return: Nothing
    """
    db = danbooru(config)

    for file, description in get_images(directory, force, tagging=tagging):
        tags = ""
        rating = "s"
        if description:
            x, y = read_description_file(description)
            if x:
                rating = x
            if y:
                tags = y
        logger.debug(file)
        logger.debug(tags)
        logger.debug(rating)
        db.create_post(filename=file, tag_string=tags, rating=rating)
    logger.info("Done Processing Images")

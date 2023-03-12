import argparse
from pprint import pprint

from content.config import config
from content.danbooru import danbooru
import os
from content.general import logger
import re
import yaml
from yaml.loader import SafeLoader
import hashlib


def hash_file(directory, file):
    unknown_hash = 0
    with open(file, 'rb', buffering=0) as f:
        bytes = f.read()
        hash = hashlib.sha256(bytes).hexdigest()
    #print(file.name)
    logfile = directory.replace("\\", "/")
    logfile = "data/" + logfile.split("/")[-1].replace(" ", "_") + ".log"
    if os.path.exists(logfile):
        with open(logfile) as file:
            hashes = [line.rstrip() for line in file]
        if hash not in hashes:
            hashes.append(hash)
            unknown_hash = 1
    else:
        hashes = [hash]
        unknown_hash = 1
    with open(logfile, 'w') as outfile:
        for hash in hashes:
            outfile.write(hash + '\n')
    return unknown_hash


def get_images(path):
    ext = [".png", ".jpg"]
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and file.endswith(tuple(ext)):
            f = os.path.join(path, file)
            if hash_file(path, f) == 1:
                t = re.sub(r"\.([^.]*?)$", ".yaml", f, count=0, flags=0)
                if os.path.exists(t):
                    yield f, t
                else:
                    defaults = {"rating": "s", "tags": ""}
                    with open(t, 'w') as outfile:
                        yaml.dump(defaults, outfile, default_flow_style=False)
                    yield f, None


def read_description_file(file):
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
        else:
            tags = None
        return rating, tags
    else:
        return None, None


def upload_directory(directory=None):
    db = danbooru(config)

    for file, description in get_images(directory):
        if description:
            x, y = read_description_file(description)
            if x:
                rating = x
            if y:
                tags = y
        else:
            tags = ""
            rating = "s"
        logger.info(file)
        logger.info(rating)
        db.create_post(filename=file, tag_string=tags, rating=rating)
    logger.info("done")

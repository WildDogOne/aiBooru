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


def check_description_yaml(file):
    t = re.sub(r"\.([^.]*?)$", ".yaml", file, count=0, flags=0)
    if os.path.exists(t):
        return True
    else:
        return False


def hash_file(directory, file, logdir="data/"):
    known_hash = 0
    if check_description_yaml(file):
        with open(file, 'rb', buffering=0) as f:
            bytes = f.read()
            hash = hashlib.sha256(bytes).hexdigest()
        logfile = directory.replace("\\", "/")
        logfile = logdir + logfile.split("/")[-1].replace(" ", "_") + ".json"
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
            db_file.write(json.dumps(hashes, indent=4))
            # for hash in hashes:
            # outfile.write(hash + '\n')
    return known_hash


def get_images(path, logdir="data/"):
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

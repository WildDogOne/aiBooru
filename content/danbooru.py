from pprint import pprint

import requests
from requests.auth import HTTPBasicAuth
from content.general import logger


class danbooru():
    def __init__(self, config):
        """
        :param config: Config File with username, password and Base URL
        {
        "username":"admin",
        "password":"1234",
        "base_url":"topdesk.host"
        }
        """
        self.username = config["username"]
        self.api_key = config["api_key"]
        self.base_url = config["base_url"]
        self.basic = HTTPBasicAuth(self.username, self.api_key)

    def create_post(self, filename=None, tag_string="", rating="s", source=None):
        image_id = self._upload_image(filename=filename)
        self._upload_to_post(tag_string=tag_string, rating=rating, image_id=image_id)

    def _upload_image(self, filename=None):
        files = {'upload[files][0]': open(filename, 'rb')}
        url = self.base_url + "/uploads.json"
        response = requests.request("POST", url, auth=self.basic, files=files)
        if response.status_code == 201:
            return response.json()["id"]
        else:
            pprint(response.json())
            quit(1)

    def _upload_to_post(self, image_id=None, tag_string="", rating="s", source=None):
        url = self.base_url + "/posts"
        params = {"post[tag_string]": tag_string,
                  "post[rating]": rating,
                  "post[source]": source,
                  "upload_media_asset_id": image_id}
        # authenticity_token=Fb51Dq8Rarb5SCLzs5NQCxR-EJDpBJLwLv3Kb-z2RI5dq6QXSlpk4NUiHKXIVS2Sbelv5ZszbfmCwCawIgsWyg
        # media_asset_id=4
        # upload_media_asset_id=17
        # post[source]=file://linus_happy.png
        # post[rating]=
        # post[rating]=g
        # post[parent_id]=
        # post[artist_commentary_title]=
        # post[artist_commentary_desc]=
        # post[translated_commentary_title]=
        # post[translated_commentary_desc]=
        # post[tag_string]=furry
        # commit=Post
        # post[is_pending]=0
        response = requests.request("POST", url, auth=self.basic, params=params)
        if response.status_code == 200:
            logger.info("Post Creation Success")
        else:
            logger.error("Failed to create post")
            pprint(logger.json())


def get_user(self):
    url = self.base_url + "/profile.json"
    response = requests.request("GET", url, auth=self.basic)
    pprint(response.json())

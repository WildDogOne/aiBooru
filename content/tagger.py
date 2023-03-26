import os
import requests
import numpy as np
import deepdanbooru as dd
import tensorflow as tf
from PIL import Image


def download_model(model_url, model_zip):
    r = requests.get(model_url, allow_redirects=True)
    with open(model_zip, 'wb') as f:
        f.write(r.content)


def extract_model(model_zip, project):
    import zipfile

    with zipfile.ZipFile(model_zip, 'r') as zip_ref:
        zip_ref.extractall(project)


def prepare_image(input_image, model):
    pil_image = Image.open(input_image)

    width = model.input_shape[2]
    height = model.input_shape[1]
    image = np.array(pil_image)
    image = tf.image.resize(
        image,
        size=(height, width),
        method=tf.image.ResizeMethod.AREA,
        preserve_aspect_ratio=True,
    )
    image = image.numpy()  # EagerTensor to np.array
    image = dd.image.transform_and_pad_image(image, width, height)
    image = image / 255.0
    image_shape = image.shape
    image = image.reshape((1, image_shape[0], image_shape[1], image_shape[2]))
    return image


def evaluate_image(input_image: str = None, model_url: str = None, project: str = None, threshold: float = None):
    if model_url is None:
        model_url = "https://github.com/KichangKim/DeepDanbooru/releases/download/v3-20211112-sgd-e28/deepdanbooru-v3-20211112-sgd-e28.zip"
    if project is None:
        project = "./deepbooru"
    if threshold is None:
        threshold = 0.5
    model_zip = os.path.join(project, "model.zip")

    if not os.path.exists(project):
        os.makedirs(project)
    if not os.path.exists(model_zip):
        download_model(model_url, model_zip)
    if not os.path.exists(os.path.join(project, "project.json")):
        extract_model(model_zip, project)

    tags = dd.project.load_tags_from_project(project)
    model = dd.project.load_model_from_project(project, compile_model=False)

    image = prepare_image(input_image, model)
    y = model.predict(image)[0]

    result_dict = {}

    for i, tag in enumerate(tags):
        result_dict[tag] = y[i]

    result_tags_out = []
    result_tags = []
    rating = "s"

    for tag in tags:
        if result_dict[tag] >= threshold:
            if tag.startswith("rating:"):
                rating = tag
                continue
            result_tags_out.append(tag.replace('_', ' ').replace(':', ' '))
            result_tags.append({tag.replace('_', ' ').replace(':', ' '): result_dict[tag]})

    return result_tags_out, rating

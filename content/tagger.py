import os
import requests
import numpy as np
import deepdanbooru as dd
import tensorflow as tf
from PIL import Image


def evaluate_image(input_image: str = None, model_url: str = None, project: str = None, threshold: float = None):
    if model_url is None:
        model_url = "https://github.com/KichangKim/DeepDanbooru/releases/download/v3-20211112-sgd-e28/deepdanbooru-v3-20211112-sgd-e28.zip"
    if project is None:
        project = "./deepbooru"
    if threshold is None:
        threshold = 0.5
    model_zip = project + "/model.zip"
    if not os.path.exists(project):
        os.makedirs(project)
    if not os.path.exists(model_zip):
        r = requests.get(model_url, allow_redirects=True)
        open(model_zip, 'wb').write(r.content)
    if not os.path.exists(project + "/project.json"):
        import zipfile

        with zipfile.ZipFile(model_zip, 'r') as zip_ref:
            zip_ref.extractall(project)

    pil_image = Image.open(input_image)
    tags = dd.project.load_tags_from_project(project)
    model = dd.project.load_model_from_project(project, compile_model=False)

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

    y = model.predict(image)[0]

    result_dict = {}

    for i, tag in enumerate(tags):
        result_dict[tag] = y[i]
    result_tags_out = []
    # result_tags_print = []
    result_tags = []
    for tag in tags:
        if result_dict[tag] >= threshold:
            if tag.startswith("rating:"):
                continue
            result_tags_out.append(tag.replace('_', ' ').replace(':', ' '))
            # result_tags_print.append(f'{result_dict[tag]} {tag}')
            result_tags.append({tag.replace('_', ' ').replace(':', ' '): result_dict[tag]})

    # print('\n'.join(sorted(result_tags_print, reverse=True)))
    # pprint(result_tags_print)

    return result_tags_out

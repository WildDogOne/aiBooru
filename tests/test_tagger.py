from unittest import TestCase

from content.tagger import evaluate_image


class Test(TestCase):
    def test_evaluate_image(self):
        tags, rating = evaluate_image(input_image="./ytbheadeer.webp", project="../deepbooru")
        expected = ['1boy',
                    'ball',
                    'earth (planet)',
                    'green eyes',
                    'green hair',
                    'hat',
                    'holding',
                    'hood',
                    'hood down',
                    'hoodie',
                    'marker (medium)',
                    'millipen (medium)',
                    'painting (medium)',
                    'planet',
                    'solo',
                    'traditional media',
                    'watercolor (medium)',
                    'window']
        self.assertEqual(expected, tags)
        self.assertEqual("rating:safe", rating)


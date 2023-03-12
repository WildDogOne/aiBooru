from unittest import TestCase

from content.functions import get_images


class Test(TestCase):
    def test_get_images(self):
        for x, y in get_images("./"):
            self.assertEqual("./test.jpg", x)
            self.assertEqual("./test.yaml", y)

from unittest import TestCase

from content.functions import get_images, read_description_file


class Test(TestCase):
    def test_get_images(self):
        for x, y in get_images("./"):
            self.assertEqual("./test.jpg", x)
            self.assertEqual("./test.yaml", y)

    def test_read_description_file(self):
        actual = read_description_file("./test.yaml")
        expected = ('s', 'black_box')
        self.assertEqual(expected, actual)

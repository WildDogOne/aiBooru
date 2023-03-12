from unittest import TestCase

from content.functions import get_images, read_description_file, hash_file


class Test(TestCase):
    def test_get_images(self):
        for x, y in get_images("../tests", logdir="../data/"):
            self.assertEqual("./test.jpg", x)
            self.assertEqual("./test.yaml", y)

    def test_read_description_file(self):
        actual = read_description_file("./test.yaml")
        expected = ('s', 'black_box')
        self.assertEqual(expected, actual)
    def test_hash_file(self):
        directory = "../tests"
        file = "./test.jpg"
        actual = hash_file(directory, file, logdir="../data/")
        expected = 1
        self.assertEqual(expected, actual)

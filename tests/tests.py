import string
import unittest
import os
import random


class TestTailCLI(unittest.TestCase):
    TESTS_RUNNING_DIR = 'tests_sandbox'
    TEST_FILE_NAME = 'file.txt'

    def _create_test_sandbox(self):
        tests_dir = self.TESTS_RUNNING_DIR
        if not os.path.exists(tests_dir):
            os.makedirs(tests_dir)

    def _get_random_content(self, lines_number):
        content = []
        for i in range(lines_number):
            random_line = ''.join(random.choice(string.ascii_uppercase + string.digits) for j in range(20))
            content.append(random_line)
        return content

    def _create_reading_file_and_get_its_path_and_content(self):
        content_liner_number = 20
        self._create_test_sandbox()

        reading_file_path = '{dir}/{name}'.format(dir=self.TESTS_RUNNING_DIR, name=self.TEST_FILE_NAME)
        content = self._get_random_content(lines_number=content_liner_number)
        with open(reading_file_path, "w") as reading_file:
            for line in content:
                reading_file.write(line)
        return reading_file_path, content

    def test_it_reads_n_last_lines_of_file(self):
        file_path = self._create_reading_file_and_get_its_path()
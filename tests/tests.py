import shutil
import string
import unittest
import os
import random
from unittest.mock import patch, call, Mock

from click.testing import CliRunner

from app import main


class TestTailCLI(unittest.TestCase):
    TESTS_RUNNING_DIR = 'tests_sandbox'
    TEST_FILE_NAME = 'file.txt'

    def setUp(self):
        self.file_path, self.content = self._create_reading_file_and_get_its_path_and_content()

    def tearDown(self):
        try:
            shutil.rmtree(self.TESTS_RUNNING_DIR)
        except OSError as e:
            print("An error occurred: {} - {}.".format(e.filename, e.strerror))

    def _create_test_sandbox(self):
        tests_dir = self.TESTS_RUNNING_DIR
        if not os.path.exists(tests_dir):
            os.makedirs(tests_dir)

    def _get_random_line(self):
        random_line = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
        return '{}\n'.format(random_line)

    def _get_random_content(self, lines_number):
        content = []
        for _ in range(lines_number):
            random_line = self._get_random_line()
            content.append(random_line)
        return content

    def _create_reading_file_and_get_its_path_and_content(self):
        content_lines_number = 20
        self._create_test_sandbox()

        reading_file_path = os.path.join(self.TESTS_RUNNING_DIR, self.TEST_FILE_NAME)
        content = self._get_random_content(lines_number=content_lines_number)
        with open(reading_file_path, "w") as reading_file:
            for line in content:
                reading_file.write(line)

        return reading_file_path, content

    # @unittest.skip('dev')
    @patch('app.print_line')
    def test_it_reads_n_last_lines_of_file(self, print_line_mock):
        runner = CliRunner()
        runner.invoke(main, [self.file_path, '-n', 10])
        expected = self.content[-10:]

        print_line_mock.assert_has_calls(
            call(value) for value in expected
        )

    @patch('app.print_line')
    @patch('app.time')
    def test_it_watches_new_lines_in_file(self, time_mock, print_line_mock):
        reading_lines = 5
        watch_file_loop_number = 5
        runner = CliRunner()
        reading_file_path = self.file_path
        time_mock.sleep.side_effect = ErrorAfter(watch_file_loop_number)
        with open(reading_file_path, "w") as reading_file:
            expected = []
            for _ in range(reading_lines):
                # CallableExhausted exception should appear in invoke output in 'exception' property
                runner.invoke(main, [reading_file_path, '-f'])

                random_line = self._get_random_line()
                reading_file.write(random_line)
                expected.append(random_line)

        print_line_mock.assert_has_calls(
            call(value) for value in expected
        )


class ErrorAfter:
    """
    Callable that will raise `CallableExhausted` exception after `limit` calls
    Is used here to test while loops
    """

    def __init__(self, limit):
        self.limit = limit
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        if self.calls > self.limit:
            raise CallableExhausted


class CallableExhausted(Exception):
    pass

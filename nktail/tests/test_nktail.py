import shutil
import string
import time
import unittest
import os
import random
import multiprocessing
from unittest.mock import patch, call

from click.testing import CliRunner

from nktail.tests.sharedmock import SharedMock
from nktail.command_line import main


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

    @patch('nktail.command_line._write_to_stdin')
    def test_it_reads_n_last_lines_of_file(self, output_writer_mock):
        lines_to_display_count = 10
        runner = CliRunner()
        runner.invoke(main, [self.file_path, '-n', lines_to_display_count])
        expected = self.content[-lines_to_display_count:]

        output_writer_mock.assert_has_calls(
            [call(value) for value in expected]
        )

    @patch('nktail.command_line._write_to_stdin')
    @patch('nktail.tail.time')
    def test_it_runs_file_watcher(self, time_mock, output_writer_mock):
        new_lines_to_add_count = 5
        lines_to_display_count = 10
        reading_file_path = self.file_path
        new_lines = [self._get_random_line() for _ in range(new_lines_to_add_count)]

        output_mock = SharedMock()
        output_writer_mock.side_effect = output_mock

        stop_adding_new_lines_event = multiprocessing.Event()

        def cli_worker(path):
            runner = CliRunner()
            runner.invoke(main, [path, '-f', '-n', lines_to_display_count])
            return

        def writer_worker(path, lines):
            time.sleep(0.1)  # let the tail app display 10 lines as it starts
            with open(path, 'a') as reading_file:
                for line in lines:
                    reading_file.write(line)
            time.sleep(0.1)  # let the tail app recognize new added lines and handle it
            stop_adding_new_lines_event.set()
            return

        cli_thread = multiprocessing.Process(target=cli_worker, args=(reading_file_path,))
        cli_thread.start()
        writer_thread = multiprocessing.Process(target=writer_worker, args=(reading_file_path, new_lines))
        writer_thread.start()

        expected = []
        last_lines = self.content[-lines_to_display_count:]
        expected.extend(last_lines)
        expected.extend(new_lines)

        stop_adding_new_lines_event.wait()
        if stop_adding_new_lines_event.is_set():
            cli_thread.terminate()

            output_mock.assert_has_calls(
                [call(value) for value in expected]
            )

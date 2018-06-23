import shutil
import string
import unittest
import os
import random
from unittest.mock import patch, call, Mock

from click.testing import CliRunner

from nktail.command_line import main
from nktail.tail import _watch_new_lines


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
    def test_it_reads_n_last_lines_of_file(self, print_line_mock):
        runner = CliRunner()
        runner.invoke(main, [self.file_path, '-n', 10])
        expected = self.content[-10:]

        print_line_mock.assert_has_calls(
            [call(value) for value in expected]
        )

    @patch('nktail.command_line.open')
    @patch('nktail.tail._read_last_lines')
    @patch('nktail.tail._watch_new_lines')
    @patch('nktail.command_line._write_to_stdin')
    def test_it_runs_file_watcher(self,
                                  write_to_stdin_mock,
                                  watch_new_lines_mock,
                                  read_last_lines_mock,
                                  open_mock):
        file_handler = Mock()
        open_mock.return_value.__enter__.return_value = file_handler

        runner = CliRunner()
        runner.invoke(main, [self.file_path, '-f'])

        watch_new_lines_mock.assert_called_with(file_handler=file_handler, callback=write_to_stdin_mock)


class TestTailFileWatcher(unittest.TestCase):
    def test_it_watches_new_lines_in_file(self):
        input_strings = [
            b'',
            b'QL5UUCPBQ35A2PBZAV27\n',
            b'',
            b'KSDD2BP7HYHAR1OXHWGK\n',
            b'',
            b'',
            b'',
            b'PBQ35A2PP35QNR1OXIKD\n',
            b'',
            b'',
        ]
        output_writer = Mock()

        file_handler = Mock()
        file_handler.readline.side_effect = input_strings
        watch_file_loop_number = len(input_strings)
        file_handler.tell.side_effect = ErrorAfter(watch_file_loop_number)

        with self.assertRaises(CallableExhausted):
            _watch_new_lines(file_handler=file_handler, callback=output_writer)

        empty_lines_count = len([line for line in input_strings if not line])
        self.assertTrue(file_handler.seek.call_count > empty_lines_count,
                        msg='The loop of seeking to the end of the file to '
                            'watch new added lines is not working correctly')

        lines_with_content = (line for line in input_strings if line)
        output_writer.assert_has_calls(
            [call(value.decode('utf-8')) for value in lines_with_content]
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import click
from typing import Callable, BinaryIO, Iterable


@click.command()
@click.argument('file_path')
@click.option('--follow', '-f', is_flag=True, help='allows a file to be monitored')
@click.option('--number_of_lines', '-n', default=10, help='the amount of output lines')
def main(file_path: str, follow: bool, number_of_lines: str) -> None:
    try:
        with open(file_path, 'rb') as file_handler:
            tail(file_handler=file_handler,
                 is_following=follow,
                 number_of_lines=number_of_lines,
                 output_writer=_write_to_stdin)
    except (IOError, OSError):
        sys.exit("Can not open file {}".format(file_path))


def tail(file_handler, is_following, number_of_lines, output_writer):
    for line in _read_last_lines(file_handler=file_handler,
                                 lines_number=int(number_of_lines)):
        output_writer(line)
    if is_following:
        _watch_new_lines(file_handler=file_handler, callback=output_writer)


def _read_last_lines(file_handler: BinaryIO, lines_number: int) -> Iterable[str]:
    file_handler.seek(-2, 2)  # go to the second last byte
    found_lines_number = 0
    current_position = file_handler.tell()
    last_lines = []
    while found_lines_number < lines_number or current_position < 0:
        if file_handler.read(1) == b'\n':
            new_line = file_handler.readline()
            new_line_decoded = new_line.decode('utf-8', 'replace')
            last_lines.append(new_line_decoded)
            found_lines_number += 1
        else:
            current_position -= 1
            file_handler.seek(current_position)

    return reversed(last_lines)


def _watch_new_lines(file_handler: BinaryIO, callback: Callable[[str], None]) -> None:
    file_handler.seek(0, 2)  # go to the end of the file
    while True:
        current_position = file_handler.tell()
        new_line = file_handler.readline()
        if not new_line:
            file_handler.seek(current_position)
            time.sleep(0.5)
        else:
            new_line_decoded = new_line.decode('utf-8', 'replace')
            callback(new_line_decoded)


def _write_to_stdin(line: str) -> None:
    print(line)


if __name__ == '__main__':
    main()

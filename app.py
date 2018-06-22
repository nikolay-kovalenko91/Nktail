#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import click
import os
from typing import Generator


@click.command()
@click.argument('file_path')
@click.option('--follow', '-f', is_flag=True, help='allows a file to be monitored')
@click.option('--lines_number', '-n', help='the amount of output lines')
def main(file_path: str, follow: bool, lines_number: str) -> None:
    print('Hey!!!{} is {}'.format(file_path, follow))

    # for line in read_last_lines(file_path=file_path, lines_number=int(lines_number)):
    #     print_line(line)

    if follow:
        for line in read_following_lines(file_path=file_path):
            print_line(line)


def print_line(line):
    print(line)


def read_last_lines(file_path: str, lines_number: int) -> Generator[str, None, None]:
    buffer_to_iterate = 8192
    file_size = os.path.getsize(file_path)


def read_following_lines(file_path: str) -> Generator[str, None, None]:
    with open(file_path) as file_handler:
        file_handler.seek(0, 2)  # go to the end of the file
        while True:
            current_position = file_handler.tell()
            new_line = file_handler.readline()
            if not new_line:
                file_handler.seek(current_position)
                time.sleep(0.5)
            else:
                yield new_line


if __name__ == '__main__':
    main()

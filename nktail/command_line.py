#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import click

from nktail.tail import tail


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


def _write_to_stdin(line: str) -> None:
    print(line)


if __name__ == '__main__':
    main()

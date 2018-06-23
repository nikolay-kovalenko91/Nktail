import time
from typing import BinaryIO, Iterable, Callable


def tail(file_handler: BinaryIO, is_following: bool, number_of_lines: int, output_writer: Callable[[str], None]) -> None:
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

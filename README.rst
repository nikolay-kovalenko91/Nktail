---- nktail ----

Usage:
$ nktail [options] <filename>

Options:
By default, nktail will output the last 10 lines of the passed file. You can set any count of output lines using '-n' option.

$ nktail -n 100 <filename>

If you run nktail with '-f' option, it displays the lines and then monitors the file. As new lines are added to the file by another process, tail updates the display.

$ nktail -f <filename>

As a module:

from nktail.tail import tail
tail(file_handler: BinaryIO, is_following: bool, number_of_lines: int, output_writer: Callable[[str], None])

Enjoy!!!

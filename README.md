# Nktail
A command line tool used to display the tail end of a text file or piped data. I.e. it is kind of custom analogue for Unix tail program.

## Install
```$ pip install nktail```

## Usage
```$ nktail [options] <filename>```

### Options

By default, nktail will output the last 10 lines of the passed file. You can set any count of output lines using ```-n``` option.

```$ nktail -n 100 <filename>```

If you run nktail with ```-f``` option, it displays the lines and then monitors the file. As new lines are added to the file by another process, tail updates the display.

```$ nktail -f <filename>```

## Running tests
1) ```$ pip install requirements -r requirements.txt```
2) ```$ nosetests``` or ```$ python setup.py test```

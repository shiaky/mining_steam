import sys

# thanks to Amith Koujalgi  for the code inspiration
# url:
# https://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting


class Logger(object):
    def __init__(self, sLogFile):
        self.terminal = sys.stdout
        self.logfile = sLogFile

    def write(self, message):
        self.terminal.write(message)
        with open(self.logfile, 'a') as file:
            file.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass

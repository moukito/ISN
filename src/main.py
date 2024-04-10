import os
import sys

from vue.Core import Core


def exodus():
    verifying_path()
    game = Core()
    game.run()


def verifying_path():
    path = sys.argv[0]
    keyword = path.split("/")
    path = path[:-(len(keyword[-1]) + len(keyword[-2]) + 2)]
    if path != os.getcwd():
        os.chdir(path)


if __name__ == "__main__":
    exodus()

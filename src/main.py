import os
import sys
import platform

SYSTEM = platform.system()

from src.vue.Core import Core


def exodus():
    """
        Launches the Exodus game.
        Verifies the path and initializes the Core instance to start the game.
    """
    verifying_path()
    game = Core()
    game.setup_parameter()
    game.run()
    sys.exit(0)


def verifying_path():
    """
        Verifies the current path and adjusts the working directory if necessary based on the platform.
xvg()
        This function checks the current path to determine if it matches the directory containing the running script.
        If the current path does not match, it adjusts the working directory to match the script's directory.
        The adjustment is based on the platform: Linux and macOS use forward slashes ("/"), while Windows uses backslashes ("\").
    """
    path = sys.argv[0]
    if SYSTEM == "Linux" or SYSTEM == "Darwin":
        keyword = path.split("/")
        path = path[:-(len(keyword[-1]) + len(keyword[-2]) + 2)]
        if path != os.getcwd():
            os.chdir(path)
    elif SYSTEM == "Windows":
        keyword = path.split("\\")
        path = path[:-(len(keyword[-1]) + len(keyword[-2]) + 2)]
        if path != os.getcwd():
            os.chdir(path)


if __name__ == "__main__":
    exodus()

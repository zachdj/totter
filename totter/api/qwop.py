""" API to load and play games of QWOP """

import webview
import pyautogui
import time
from multiprocessing import Process

# constants
_QWOP_URL = "http://foddy.net/Athletics.html?webgl=true"  # Note that it should be the HTML version
_QWOP_HEIGHT = 450
_QWOP_WIDTH = 700

# module-private variables
_qwop_process = None

# module-public variables


def _open_qwop_window():
    webview.create_window(title="Totter QWOP Instance",
                          url="http://foddy.net/Athletics.html?webgl=true",
                          width=_QWOP_WIDTH,
                          height=_QWOP_HEIGHT,
                          resizable=False)


def start():
    _qwop_process = Process(target=_open_qwop_window)
    _qwop_process.start()
    # wait until the game has (probably) loaded
    time.sleep(4)
    # the qwop window will always be in the center of the primary monitor
    screen_width, screen_height = pyautogui.size()
    # correct for double-monitor setup
    if screen_width > 1920:
        screen_width = screen_width // 2
    # move the mouse to the qwop window, and click to start the game
    pyautogui.moveTo(screen_width//2, screen_height//2, duration=0.25)
    pyautogui.click()

    return _qwop_process

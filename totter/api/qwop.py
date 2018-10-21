import webview
import pyautogui

# determine size of screen
screen_width, screen_height = pyautogui.size()
# correct for double-monitor setup
if screen_width > 1920:
    screen_width = screen_width // 2

# qwop-related constants
_QWOP_URL = "http://foddy.net/Athletics.html?webgl=true"  # Note that it should be the HTML5 version
_QWOP_WIDTH = 700
_QWOP_HEIGHT = 450
QWOP_CENTER = (screen_width // 2, screen_height // 2)
QWOP_BOUNDING_BOX = (
    QWOP_CENTER[0] - _QWOP_WIDTH // 2,  # left
    QWOP_CENTER[1] - _QWOP_HEIGHT // 2,  # top
    _QWOP_WIDTH,  # width
    _QWOP_HEIGHT  # height
)


def open_qwop_window():
    """ Opens a webview and loads the HTML5 version of QWOP """
    webview.create_window(title="Totter QWOP Instance", url=_QWOP_URL,
                          width=_QWOP_WIDTH, height=_QWOP_HEIGHT, resizable=False)


def close_qwop_window():
    """ Kills the open webview """
    webview.destroy_window()

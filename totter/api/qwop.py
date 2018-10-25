import pyautogui
import os
import platform
from selenium import webdriver

# determine size of screen
screen_width, screen_height = pyautogui.size()
# correct for double-monitor setup
if screen_width > 1920:
    screen_width = screen_width // 2

# qwop-related constants
_QWOP_URL = "http://foddy.net/Athletics.html?webgl=true"  # Note that it should be the HTML5 version
_QWOP_WIDTH = 700
_QWOP_HEIGHT = 500
QWOP_CENTER = (screen_width // 2, screen_height // 2)
QWOP_BOUNDING_BOX = (
    QWOP_CENTER[0] - _QWOP_WIDTH // 2,  # left
    QWOP_CENTER[1] - _QWOP_HEIGHT // 2,  # top
    _QWOP_WIDTH,  # width
    _QWOP_HEIGHT  # height
)

# create a selenium driver to open web pages
current_dir = os.path.dirname(os.path.abspath(__file__))
driver_dir = os.path.join(current_dir, 'drivers')
# find the appropriate geckodriver for the current platform
if platform.system() == 'Linux':
    geckopath = os.path.join(driver_dir, 'nix', 'geckodriver')
elif platform.system() == 'Darwin':
    geckopath = os.path.join(driver_dir, 'osx', 'geckodriver')
else:
    geckopath = os.path.join(driver_dir, 'win', 'geckodriver.exe')

geckopath = os.path.abspath(geckopath)

browser = webdriver.Firefox(executable_path=geckopath)
# move the browser window to a fixed and predictable location
browser.set_window_size(width=QWOP_BOUNDING_BOX[2], height=QWOP_BOUNDING_BOX[3])
browser.set_window_position(x=QWOP_BOUNDING_BOX[0], y=QWOP_BOUNDING_BOX[1])


def open_qwop_window():
    """ Opens a browser tab with the HTML5 version of QWOP """
    browser.get(_QWOP_URL)


def close_qwop_window():
    """ Kills the open webview """
    browser.quit()

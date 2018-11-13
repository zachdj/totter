""" Functions for creating and positioning a webview with the QWOP game """

import os
import platform
import pyautogui
import threading
import time

from datetime import timedelta
from selenium import webdriver

from totter.api.image_processing import ImageProcessor
from totter.utils.time import WallTimer

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

_browser = None


def _open_qwop_window():
    """ Opens a browser tab with the HTML5 version of QWOP """
    global _browser
    _browser = webdriver.Firefox(executable_path=geckopath)
    # move the browser window to a fixed and predictable location
    _browser.set_window_size(width=QWOP_BOUNDING_BOX[2]+100, height=QWOP_BOUNDING_BOX[3]+100)
    _browser.set_window_position(x=QWOP_BOUNDING_BOX[0]-50, y=QWOP_BOUNDING_BOX[1]-50)

    _browser.get(_QWOP_URL)


def _close_qwop_window():
    """ Kills the open webview """
    global _browser
    _browser.quit()


def _end_game_manually():
    """ Performs a series of bad keystrokes that probably ends the game """
    pyautogui.keyDown('w')
    time.sleep(1)
    pyautogui.keyUp('w')
    pyautogui.keyDown('q')
    pyautogui.keyDown('p')
    time.sleep(3)
    pyautogui.keyUp('q')
    pyautogui.keyUp('p')


def start_qwop():
    """ Create a QWOP instance and wait for it to load """
    _open_qwop_window()
    time.sleep(5)


def stop_qwop():
    """ Stop the QWOP instance if one is open """
    global _browser
    if _browser is not None:
        _close_qwop_window()


class QwopSimulator(object):
    def __init__(self, time_limit, buffer_size=16):
        """ Initialize a QwopSimulator
        QwopSimulator provides a method for running a QwopStrategy object in an instance of the QWOP game

        Args:
            time_limit (float): time limit in seconds for the simulation
            buffer_size (int):
                number of checks to perform in the same-history ending condition.
                If the distance run is the same for `buffer_size` checks in a row, then the simulation is terminated.
                Checks are performed 3-4 times per second depending on processor speed.
        """
        self.time_limit = time_limit
        self.timer = WallTimer()
        self.image_processor = ImageProcessor(buffer_size=buffer_size)

    def _loop_gameover_check(self, interval=0.25):
        """ Checks if the game has ended every `interval` seconds.
        Terminates when the game ends or after the simulator's time limit is reached.

        Args:
            interval (float): time in seconds between game over checks

        Returns: None
        """
        while self.timer.since() < timedelta(seconds=self.time_limit):
            screen = pyautogui.screenshot(region=QWOP_BOUNDING_BOX)
            self.image_processor.update(screen)
            if self.image_processor.is_game_over():
                break
            time.sleep(interval)

    def is_game_over(self):
        return self.image_processor.is_game_over()

    def simulate(self, strategy, qwop_started=False):
        """ Run the given QwopStrategy

        Args:
            strategy (QwopStrategy): the strategy to execute
            qwop_started (bool): if set, the simulator will assume that a QWOP window has already been opened

        Returns:
            (float, float): distance run, time taken

        """
        if not qwop_started:
            start_qwop()

        # click the qwop window to give it keyboard focus
        pyautogui.moveTo(QWOP_CENTER[0], QWOP_CENTER[1], duration=0.1)
        pyautogui.click()

        # press spacebar to restart the simulator if necessary
        pyautogui.press('space')

        # prep for a new run
        self.timer.restart()
        self.image_processor.reset()

        # start a thread to check if the game is over:
        game_over_checker = threading.Thread(target=self._loop_gameover_check, args=(0.25,))
        game_over_checker.start()

        # loop the strategy until the game ends or we hit the time limit
        while self.timer.since() < timedelta(seconds=self.time_limit) and not self.image_processor.is_game_over():
            strategy.execute()

        strategy.cleanup()

        # wait for the game over thread to finish its thing
        game_over_checker.join()

        distance_run = self.image_processor.get_final_distance()
        run_time = self.timer.since().seconds

        # if the simulator started its own QWOP window, then it should be destroyed
        if not qwop_started:
            stop_qwop()

        return distance_run, run_time


class QwopEvaluator(object):
    def __init__(self, time_limit):
        """ Initialize a QwopEvaluator
        QwopEvaluator objects run QwopStrategy objects and report the distance run and time taken.

        Args:
            time_limit (float): time limit in seconds for each evaluation
        """
        self.evaluations = 0
        self.simulator = QwopSimulator(time_limit=time_limit)
        # create an instance of QWOP
        start_qwop()

    def evaluate(self, strategies):
        """ Evaluates a QwopStrategy or a set of QwopStrategy objects

        Args:
            strategies (QwopStrategy or Iterable<QwopStrategy>): set of strategies to evaluate

        Returns:
            ((distance1, time1), (distance2, time2), ...): distance,time pairs achieved by each QwopStrategy
        """
        # check if a single strategy has been passed
        try:
            num_strategies = len(strategies)
        except TypeError:  # raised if a single QwopStrategy was passed
            strategies = [strategies]
            num_strategies = len(strategies)

        # create a vector to hold fitness values (initially filled with zeros)
        fitness_values = [(0, 0) for i in range(0, num_strategies)]

        # evaluate the strategies
        for index, strategy in enumerate(strategies):
            distance_run, time_taken = self.simulator.simulate(strategy, qwop_started=True)

            fitness_values[index] = (distance_run, time_taken)

            # if the strategy didn't end the game, end it manually
            if not self.simulator.is_game_over():
                _end_game_manually()

        return tuple(fitness_values)


class QwopStrategy:
    def __init__(self, execution_function):
        """ Class representing QWOP strategies

        A QWOP Strategy is a sequence of keystrokes that plays QWOP.
        Each Strategy must implement an `execute` method, which executes the keystrokes for the strategy with the correct timing.
        When evaluating the strategy, `execute` will automatically be looped until the game ends.

        Args:
            execution_function (function): function that implements the strategy

        """
        self.execute = execution_function

    def cleanup(self):
        """ Cleans up after strategy execution

        This method will be called after the game has ended or the evaluation time limit has been reached

        Returns: None
        """
        # ensure all keys are up
        for key in ('q', 'w', 'o', 'p', 'space'):
            pyautogui.keyUp(key)

""" API to evaluate QwopStrategy objects by playing QWOP """

import time
from datetime import timedelta
import threading
import pyautogui
import totter.api.qwop as qwop_api
import totter.api.image_processing as image_processing

from totter.utils.time import WallTimer


def _check_game_over():
    # TODO: this should probably also check if the game state hasn't changed for several seconds
    screen = pyautogui.screenshot(region=qwop_api.QWOP_BOUNDING_BOX)
    return image_processing.is_game_over(screen)


class QwopEvaluator(object):
    def __init__(self):
        self.evaluations = 0
        self.game_over = False  # tracks when the game ends for each evaluation
        self.timer = WallTimer()
        # create an instance of QWOP
        qwop_api.open_qwop_window()
        time.sleep(7)  # make sure QWOP has loaded

    def _loop_gameover_check(self, interval=0.25, time_limit=120):
        """ Checks if the game has ended every `interval` seconds until the specified time limit is reached

        Sets `self.game_over` when the game-over condition is detected.

        Args:
            interval (float): time in between game over checks, in seconds

        Returns: None

        """
        while self.timer.since() < timedelta(seconds=time_limit):
            self.game_over = _check_game_over()
            if self.game_over:
                break
            time.sleep(interval)

    def _end_game_manually(self):
        """ Performs a series of bad keystrokes that probably ends the game """
        pyautogui.keyDown('w')
        pyautogui.keyDown('o')
        time.sleep(1)
        pyautogui.keyUp('w')
        pyautogui.keyUp('o')
        pyautogui.keyDown('q')
        pyautogui.keyDown('p')
        time.sleep(3)
        pyautogui.keyUp('q')
        pyautogui.keyUp('p')

    def evaluate(self, strategies, time_limit=120):
        """ Evaluates a QwopStrategy or a set of QwopStrategy objects

        Args:
            strategies (QwopStrategy or Iterable<QwopStrategy>): set of strategies to evaluate
            time_limit (float): time limit in seconds for each evaluation

        Returns:
            (float, float, etc.): tuple of fitness values. The ith fitness value is the fitness of the ith QwopStrategy.

        """
        # click the qwop window to give it keyboard focus
        pyautogui.moveTo(qwop_api.QWOP_CENTER[0], qwop_api.QWOP_CENTER[1], duration=0.1)
        pyautogui.click()

        # check if a single strategy has been passed
        try:
            num_strategies = len(strategies)
        except TypeError:  # raised if a single QwopStrategy was passed
            strategies = [strategies]
            num_strategies = len(strategies)

        # create a vector to hold fitness values (initially filled with zeros)
        fitness_values = [0 for i in range(0, num_strategies)]

        # evaluate the strategies
        for index, strategy in enumerate(strategies):
            # hit space to reset the game
            pyautogui.press('space')

            # prep for a new run
            self.timer.restart()
            self.game_over = False

            # start a thread to check if the game is over:
            game_over_checker = threading.Thread(target=self._loop_gameover_check, args=(0.25, time_limit))
            game_over_checker.start()

            # loop the strategy until the game ends or we hit the time limit
            while self.timer.since() < timedelta(seconds=time_limit) and not self.game_over:
                strategy.execute()

            strategy.cleanup()

            # wait for the game over thread to finish its thing
            game_over_checker.join()

            # TODO: take a screen shot and determine score
            fitness_values[index] = 0  # TODO: replace 0 with score

            # if the strategy didn't end the game, end it manually
            # if not self.game_over:
            #     self._end_game_manually()
            #     self.game_over = _check_game_over()

        return tuple(fitness_values)

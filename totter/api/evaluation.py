""" API to evaluate QwopStrategy objects by playing QWOP """

import time
import threading
import pyautogui

from totter.utils.time import WallTimer


class QwopEvaluator(object):
    def __init__(self):
        self.evaluations = 0
        self.timer = WallTimer()

    def _loop_gameover_check(self, delay=0.25, time_limit=120):
        """ loops self.is_game_over until the game is over or time_limit is reached

        Args:
            delay (float): delay in seconds between is_game_over checks
            time_limit (float): time limit in seconds

        Returns: None

        """
        while not self._is_game_over() and self.timer.since() > time_limit:
            time.sleep(delay)

    def _is_game_over(self):
        """ Analyses a screenshot to determine if the game is over

        # TODO: this should probably also check if the game has been the same for several checks

        Returns:
            bool: True if the game is over, False otherwise

        """
        # take a screenshot
        screen = pyautogui.screenshot()

        # TODO: decide if game is over

        return False

    def evaluate(self, strategies, time_limit=120):
        """ Evaluates a QwopStrategy or a set of QwopStrategy objects

        Args:
            strategies (QwopStrategy or Iterable<QwopStrategy>): set of strategies to evaluate
            time_limit (float): time limit in seconds for each evaluation

        Returns:
            (float, float, etc.): tuple of fitness values. The ith fitness value is the fitness of the ith QwopStrategy.

        """
        # if this is the first evaluation, wait a few seconds to make sure QWOP has loaded
        if self.evaluations == 0:
            time.sleep(5)

        # click the qwop window to give it keyboard focus
        # the qwop window should always be in the center of the primary monitor
        screen_width, screen_height = pyautogui.size()
        # correct for double-monitor setup
        if screen_width > 1920:
            screen_width = screen_width // 2
        # move the mouse to the qwop window, and click to start the game
        pyautogui.moveTo(screen_width // 2, screen_height // 2, duration=0.25)
        pyautogui.click()

        # check if a single strategy has been passed
        try:
            num_strategies = len(strategies)
        except ValueError:  # raised if a single QwopStrategy was passed
            strategies = [strategies]
            num_strategies = len(strategies)

        # create a vector to hold fitness values (initially filled with zeros)
        fitness_values = [0 for i in range(0, num_strategies)]

        # evaluate the strategies
        for index, strategy in enumerate(strategies):
            # hit space to reset the game
            pyautogui.press('space')

            # reset the timer
            self.timer.start()

            # start a thread to execute the strategy
            strategy_execution_thread = threading.Thread(target=strategy.run)
            strategy_execution_thread.start()

            # start a thread to periodically check if the game is over
            game_over_checker = threading.Thread(target=self._loop_gameover_check, args=(0.25, time_limit))
            game_over_checker.start()

            # the game_over thread terminates when the game is over or the time limit has elapsed
            game_over_checker.join()
            print('game over checker joined!')

            # stop execution of the strategy being evaluated
            strategy.stop()
            strategy_execution_thread.join()
            print('strategy execution thread joined!')

            # TODO: take a screen shot and determine score
            fitness_values[index] = 0  # TODO: replace 0 with score

            self.evaluations += 1

        return tuple(fitness_values)

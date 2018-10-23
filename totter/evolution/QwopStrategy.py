from abc import abstractmethod
import pyautogui


class QwopStrategy:
    def __init__(self):
        """ Abstract base class representing QWOP strategies

        A QWOP Strategy is a sequence of keystrokes that plays QWOP.
        Each Strategy must implement an `execute` method, which executes the keystrokes for the strategy with the correct timing.
        When evaluating the strategy, `execute` will automatically be looped until the game ends.

        """
        pass

    def cleanup(self):
        """ Cleans up after strategy execution

        This method will be called after the game has ended or the evaluation time limit has been reached

        Returns: None
        """
        # ensure all keys are up
        for key in ('q', 'w', 'o', 'p', 'space'):
            pyautogui.keyUp(key)

    @abstractmethod
    def execute(self):
        pass

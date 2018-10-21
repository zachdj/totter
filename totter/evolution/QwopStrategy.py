from abc import abstractmethod
import pyautogui


class QwopStrategy:
    def __init__(self):
        """ Abstract base class representing QWOP strategies

        A QWOP Strategy is a sequence of keystrokes that plays QWOP.
        Each Strategy must implement an `execute` method, which executes the keystrokes for the strategy with the correct timing.
        When evaluating the strategy, `execute` will automatically be looped until `stop` is called.

        """
        self.stopped = False

    def stop(self):
        self.stopped = True

    def run(self):
        # runs execute until stop is called
        while not self.stopped:
            self.execute()

        # ensure all keys are up
        for key in ('q', 'w', 'o', 'p', 'space'):
            pyautogui.keyUp(key)

    @abstractmethod
    def execute(self):
        pass

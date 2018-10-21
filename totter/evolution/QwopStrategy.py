from abc import abstractmethod
import multiprocessing
import time
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

    def _run_execute(self):
        while True:
            self.execute()

    def run(self):
        # spawn a process to run `execute` on a loop
        execution_process = multiprocessing.Process(target=self._run_execute)
        execution_process.start()

        # check for the stopping condition every 100 ms
        while not self.stopped:
            time.sleep(0.1)

        execution_process.terminate()

        # ensure all keys are up
        for key in ('q', 'w', 'o', 'p', 'space'):
            pyautogui.keyUp(key)

    @abstractmethod
    def execute(self):
        pass

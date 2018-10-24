import threading
import time
import pyautogui
from totter.evolution.QwopStrategy import QwopStrategy
from totter.api.evaluation import QwopEvaluator
import totter.api.qwop as qwop_api

def takeStep(leg, stepTime):
    ''' Takes a step on the leg that was passed
        leg: string, either left or right
        time: float, number of seconds to step
    '''

    if leg == 'left':
        pyautogui.keyDown('w')
        pyautogui.keyDown('o')

    if leg == 'right':
        pyautogui.keyDown('q')
        pyautogui.keyDown('p')

    time.sleep(stepTime/2)

    pyautogui.keyUp('q')
    pyautogui.keyUp('w')
    pyautogui.keyUp('o')
    pyautogui.keyUp('p')

    time.sleep(stepTime/2)


class QwopWinner(QwopStrategy):
    def execute(self):
        # First step is special
        pyautogui.keyDown('o')
        time.sleep(0.2)
        pyautogui.keyDown('w')
        time.sleep(0.5)
        pyautogui.keyUp('o')
        pyautogui.keyUp('w')

        # Then just walk it out
        stepTime = 3.0
        for i in range(5):
            takeStep("left", stepTime)
            takeStep("right", stepTime)


class WHitter(QwopStrategy):
    def execute(self):
        pyautogui.keyDown('w')
        time.sleep(2)
        pyautogui.keyUp('w')


class Popper(QwopStrategy):
    def execute(self):
        print('popping')
        time.sleep(2)


evaluator = QwopEvaluator()
w = WHitter()
p = Popper()
winner = QwopWinner()
fitness_vals = evaluator.evaluate((p), time_limit=200)
print(fitness_vals)
# time.sleep(1)  # wait for everything to finish up
qwop_api.close_qwop_window()


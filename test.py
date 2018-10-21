import threading
import time
from totter.evolution.QwopStrategy import QwopStrategy

"""
TODO: idea about app architecture:
    `evolution.algorithm` - ABC for a GA
    
    - spin up a separate thread that runs the GA - does xover, mutation, etc
    - in the main thread, create the qwop window
    - when the GA thread wants to evaluate:
        - translates individuals into `QwopStrategy` objects
        - calls `QwopEvaluator.evaluate` with the strategies
        - `evaluate` blocks thread execution while evaluating each individual
            - each QwopStrategy executes until the game has ended
            - when the game has ended, the result is saved, and the evaluator presses space to start a new game
    
    - the GA thread kills the webview when it's done

"""


class Qwopper(QwopStrategy):
    def execute(self):
        print('qwopping')
        time.sleep(0.5)


qwopper = Qwopper()
qwopping_thread = threading.Thread(target=qwopper.run)
qwopping_thread.start()

time.sleep(2)
qwopper.stop()
qwopping_thread.join()

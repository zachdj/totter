import threading
import time
from totter.evolution.QwopStrategy import QwopStrategy

"""
TODO: idea about app architecture:
    `evolution.algorithm` - ABC for a GA
    
    - main process runs a `evolution.algorithm` GA.
    - spawns population, does xover, mutation, etc
    - When time for evaluation:
        - create an `evolution.QwopStrategy` that represents the individual 
        - spin up an `api.QwopEvaluator`
            - QwopEvaluator create a QWOP webview in the main thread
            - QwopEvaluator creates a different thread to start the game, then run the QwopStrategy
            - QwopEvaluator creates a different thread to periodically check if the game is over
                - when the game ends, thread 3 calls `stop` the QwopStrategy then waits for it to join
                - thread 3 kills the webview then terminates
        
    - GA execution continues
    
ALTERNATIVELY:
    - QwopEvaluator could evaluate a set of QwopStrategies using a single QWOP instance

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

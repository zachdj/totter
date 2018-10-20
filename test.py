import threading
import time
from totter.evolution.QwopStrategy import QwopStrategy


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

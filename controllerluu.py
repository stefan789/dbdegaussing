import time

class DegaussingController():
    def __init__(self):
        self._running = False

    def run_deg(self, t):
        self._running = True
        print(t)
        time.sleep(5)
        self._running = False

    def isrunning(self):
        return self._running

    def interrupt_deg(self):
        print("interrupting")

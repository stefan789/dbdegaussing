import time
import pynedm



class DegaussingController():
    def __init__(self):
        self._running = False
        _db = "nedm%2Fdegaussing"
        po = pynedm.ProcessObject("http://localhost:5984",
            "stefan",
            "root",
        _db)

    def run_deg(self, t):
        self._running = True
        print(t)
        time.sleep(5)
        self._running = False

    def isrunning(self):
        return self._running

    def interrupt_deg(self):
        print("interrupting")

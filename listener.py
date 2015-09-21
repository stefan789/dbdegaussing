import pynedm
import controllerluu as controller

_db = "nedm%2Fdegaussing"
po = pynedm.ProcessObject("http://localhost:5984",
        "stefan",
        "root")

_dg = controller.DegaussingController()
_dgprocess = None


def run_deg(t):
    global _dg, _dgprocess
    
    def f():
        print(_dg.isrunning())
        print("run_deg called with t = {}".format(t))
        _dg.run_deg(t)
        print("run_deg done")

    if _dgprocess is not None:
        print("in progress")
        raise Exception("Degaussing in progress")

    _dgprocess = pynedm.start_process(f)
    return True

def isrunning():
    global _dg
    print("isrunning called")
    print(_dg.isrunning())
    return _dg.isrunning()

def interrupt_deg():
    global _dg, _dgprocess
    if _dgprocess is None:
        print("not in progress")
        raise Exception("Degaussing not in progress")
    _dg.interrupt_deg()

adict =  {
    "run_deg": run_deg,
    "isrunning": isrunning,
    "interrupt_deg": interrupt_deg
    }

pylisten = pynedm.listen(adict, "nedm%2Fdegaussing",
                username="stefan",
                password="root",
                uri="http://localhost:5984")

pylisten.wait()

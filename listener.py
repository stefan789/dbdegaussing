import pynedm
import controller
import logging
logging.basicConfig(level=logging.DEBUG)
print pynedm.__file__

_db = "nedm%2Fdegaussing"
po = pynedm.ProcessObject("http://raid.nedm1:5984",
        "stefan",
        "hanger",
	_db)

_dg = controller.DegaussingController()


def run_deg(t):
    print("listener run_deg called")
    
    def f():
        print(_dg.isrunning())
        print("run_deg called with t = {}".format(t))
        print(po.write_document_to_db({ "type": "data", "value": {"degaussing_state": 1} }))
        _dg.run_deg(t)
        print(po.write_document_to_db({ "type": "data", "value": {"degaussing_state": 0} }))
        print("run_deg done")

    if _dg.isrunning():
        print("in progress")
        raise Exception("Degaussing in progress")


    pynedm.start_process(f)
    return True

def isrunning():
    print("isrunning called")
    print(_dg.isrunning())
    return _dg.isrunning()

def interrupt_deg():
    print("interrupt called")
    if not _dg.isrunning():
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
                password="hanger",
                uri="http://raid.nedm1:5984", verbose=True)

pylisten.wait()
print "Finished"

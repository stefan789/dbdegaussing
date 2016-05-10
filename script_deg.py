import pynedm
import time

_server = "http://raid.nedm1:5984/"
_un = "stefan"
_pw = "hanger"
_db = "nedm%2Fdegaussing"

po = pynedm.ProcessObject(uri=_server, username=_un, password=_pw, adb=_db)

def is_running():
    adoc = {
        "type": "command",
        "execute": "isrunning",
        "arguments": []
        }
    r = po.write_document_to_db(adoc)
    time.sleep(1)
    try:
        rdoc = po.acct[po.db][r["id"]].get().json()
    except:
        time.sleep(1)
        rdoc = po.acct[po.db][r["id"]].get().json()
    return rdoc["response"]["return"]

def rundeg(t):
    """ posts run_deg command to database """
    adoc = {
            "type": "command",
            "execute": "run_deg",
            "arguments" : [t]
            }
    r = po.write_document_to_db(adoc)
    print(r)

def interrupt_deg():
    adoc = {
        "type": "command",
        "execute": "interrupt_deg",
        "arguments": []
        }
    r = po.write_document_to_db(adoc)
    print(r)

def block_while_running():
    """ 
    checks if degaussing is running and waits 

    call after rundeg(t) when using in a script
    script will then wait until degaussing is finished.
    """
    runs = is_running()
    while runs:
        runs = is_running()
        time.sleep(10)



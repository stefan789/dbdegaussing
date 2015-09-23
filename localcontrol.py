import cloudant 
import json
import time

acct = cloudant.Account(uri="http://raid.nedm1:5984")
res = acct.login("stefan", "hanger")
assert res.status_code == 200

db = acct["nedm%2Fdegaussing"]
des = db.design("nedm_default")

the_view = des.view("latest_value")

def isrunning():
    adoc = {
        "type": "command",
        "execute": "isrunning",
        "arguments": []
        }
    r = des.post("_update/insert_with_timestamp", params=adoc).json()
    print(r)

def rundeg(t):
    adoc = {
        "type": "command",
        "execute": "run_deg",
        "arguments": [t]
        }
    r = des.post("_update/insert_with_timestamp", params=adoc).json()
    print(r)

def interrupt_deg():
    adoc = {
        "type": "command",
        "execute": "interrupt_deg",
        "arguments": [t]
        }
    r = des.post("_update/insert_with_timestamp", params=adoc).json()
    print(r)



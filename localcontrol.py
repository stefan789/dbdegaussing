import cloudant 
import json
import time

acct = cloudant.Account(uri="http://localhost:5984")
res = acct.login("stefan", "root")
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

rundeg("insert_inner")
time.sleep(2)
isrunning()


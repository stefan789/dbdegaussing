import cloudant
import json
import argparse

def readconfig(conf):
    """ Reads configurations from file conf and return dictionary."""
    with open(str(conf), "r") as f:
        sources = json.loads(f.read())
    return sources

parser = argparse.ArgumentParser()
parser.add_argument("fname", help=".dict settings file to be uploaded to db")
args = parser.parse_args()

settings = readconfig(args.fname)

acct = cloudant.Account(uri="http://raid.nedm1")
res = acct.login("stefan", "hanger")
#acct = cloudant.Account(uri="http://localhost:5984")
#res = acct.login("stefan", "root")
assert res.status_code == 200

# Grab the correct database
db = acct["nedm%2Fdegaussing"]
des = db.design("nedm_default")

adoc = {
            "_id" : args.fname[:-5],
            "type": "deg_config",
            "value": settings
            }
orig_data_doc = des.post("_update/insert_with_timestamp",params=adoc).json()
print orig_data_doc

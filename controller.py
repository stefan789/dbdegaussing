import cloudant
import json
import pynedm
import numpy as np
import digiports as dg
import waveformthread as wft
import matplotlib.pyplot as plt
import nidaqmx
from wx.lib.pubsub import pub

class DegaussingController():
    def __init__(self):
        _db = "nedm%2Fdegaussing"
        self.po = pynedm.ProcessObject("http://raid.nedm1:5984",
            "stefan",
            "hanger",
	    _db)

        self.configs = self._getconfigs()
        self.settings = self._getsettings()
        self.voltagedivider = dg.VoltageDivider("Dev1")
        self.coilswitcher = dg.SwitchCoil("Dev1")
    	self._running = False
        pub.subscribe(self.poststatus, "relay.update")

    def poststatus(self, status):
        print(status)
        status = [int(i) for i in status[1:-1].split(" ")]
        adoc = {
                    "type" : "data", 
                    "value" : dict(
                    [("relay_{}".format(i), status[i]) for i in range(4)])
                }
        
        print(adoc)
        print(self.po.write_document_to_db(adoc))

    def _getconfigs(self):
        acct = cloudant.Account(uri="http://raid.nedm1")
        res = acct.login("stefan", "hanger")
        #acct = cloudant.Account(uri="http://localhost:5984")
        #res = acct.login("stefan", "root")
        assert res.status_code == 200

        db = acct["nedm%2Fdegaussing"]
        des = db.design("document_type")
        the_view = des.view("document_type")
        results = the_view.get(params=dict(descending=True,
                            reduce=False,
                            include_docs=True,
                            endkey = ['deg_config'] ,
                            startkey = ['deg_config', {}]
                            )).json()

        confs = {row["doc"]["_id"]: row["doc"]["value"] for row in results["rows"]}
        return confs

    def _getsettings(self):
        acct = cloudant.Account(uri="http://raid.nedm1")
        res = acct.login("stefan", "hanger")

        #acct = cloudant.Account(uri="http://localhost:5984")
        #res = acct.login("stefan", "root")
        assert res.status_code == 200

        db = acct["nedm%2Fdegaussing"]
        des = db.design("document_type")
        the_view = des.view("document_type")
        results = the_view.get(params=dict(descending=True,
                            reduce=False,
                            include_docs=True,
                            endkey = ['deg_setting'] ,
                            startkey = ['deg_setting', {}]
                            )).json()
        settings = {row["doc"]["_id"]: {"Config": row["doc"]["value"]["Config"],
                                        "Sequence" : row["doc"]["value"]["Sequence"]}
                    for row in results["rows"]}

        return settings

    def createWaveform(self, amp, freq, offset, duration, keeptime, sampleRate=1000):
        '''create waveform from given parameters'''
        t = np.linspace(0, duration, duration*sampleRate + 1)
        x = offset + ( (-1) * np.sin( 2*np.math.pi * freq * t ) * np.piecewise(t, [t<keeptime, t>=keeptime], [amp, lambda t: -((t-keeptime) * amp/(duration-keeptime))+amp]))
        periodLength = len( x )
        data = np.zeros( (periodLength, ), dtype = np.float64)
        data = x
        return np.asarray(list(zip(t,data)), dtype=np.float64)

    def playWaveform(self, device, amp, freq, duration, keeptime, offset, sampleRate=10000.0):
        t = np.linspace(0, duration, duration*sampleRate + 1)
        x = np.asarray(offset + ( (-1) * np.sin( 2*np.math.pi * freq * t ) * np.piecewise(t, [t<keeptime, t>=keeptime], [amp, lambda t: -((t-keeptime) * amp/(duration-keeptime))+amp])), dtype=np.float64)
        self.task = nidaqmx.AnalogOutputTask()
        self.task.create_voltage_channel("Dev1/ao0", min_val=-10.0, max_val=10.0)
        self.task.configure_timing_sample_clock(rate=sampleRate, sample_mode = 'finite' , samples_per_channel = len(x))
        self.task.write(x, auto_start=False, layout='group_by_channel')
        self.task.start()
        self.task.wait_until_done(duration + 5)
        self.task.stop()
        del self.task

    def interrupt_deg(self):
    	print("controller interrupt")
        self._running = False
        self.task.clear()
        print("task deleted")

    def run_deg(self, sett):
        self._running = True
        dev = self.configs[self.settings[sett]["Config"]]["Device"]
        print("controller run_deg called: {}".format(self.settings[sett]))
        for coil in self.settings[sett]["Sequence"]:
            if self._running:
                cs = self.configs[self.settings[sett]["Config"]][coil]
                print (coil, cs)
                # all coils off
                print("all coils off")
                self.coilswitcher.alloff()
                # set vd
                print("setting voltagedivider {}".format(cs["VoltageDivider"]))
                self.voltagedivider.setnr(cs["VoltageDivider"])
                # activate coil
                print("setting relay {}".format(cs["RelayPort"]))
                self.coilswitcher.activate(cs["RelayPort"])
                
                # play waveform
                print("start waveform")
                self.playWaveform(dev, cs['Amp'], cs['Freq'] ,cs['Dur'], cs['Keep'], 0)
                # deactivate coil
                print("deactivate coil")
                self.coilswitcher.deactivate(cs["RelayPort"])
                # vd.resetall()
                print("voltagedivider reset all")
                self.voltagedivider.resetall()
            else:
	    	self._running = False
                self.coilswitcher.alloff()
                self.voltagedivider.resetall()
        self._running = False


    def isrunning(self):
        return self._running

import cloudant
import json
import pynedm
import numpy as np
import digiports as dg
import waveformthread as wft
import matplotlib.pyplot as plt

class DegaussingController():
    def __init__(self):
        self.configs = self._getconfigs()
        self.settings = self._getsettings()
        self.voltagedivider = dg.VoltageDivider("Dev1")
        self.coilswitcher = dg.SwitchCoil("Dev1")

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
        res = acct.login("internal_coils_writer", "clu$terXz")

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

    def createWaveform(self, amp, freq, offset, duration, keeptime, sampleRate=20000):
        '''create waveform from given parameters'''
        t = np.linspace(0, duration, duration*sampleRate + 1)
        data = offset + ( (-1) * np.sin( 2*np.math.pi * freq * t ) * np.piecewise(t, [t<keeptime, t>=keeptime], [amp, lambda t: -((t-keeptime) * amp/(duration-keeptime))+amp]))
        #periodLength = len( data )
        #data = np.zeros( (periodLength, ), dtype = np.float64)
        return np.asarray(list(zip(t,data)))

    def playWaveform(self, device, waveform, sampleRate=20000):
        self.mythread = wft.WaveformThread(device, waveform, sampleRate)
        self.mythread.start()
        self.mythread.join()
        self.mythread.__del__()
        self.mythread = None

    def abortWaveform(self):
        if self.mythread:
            self._running = False
            self.mythread.stop()

    def run_deg(self, sett):
        self._running = True
        dev = self.configs[self.settings[sett]["Config"]]["Device"]
        print(self.settings[sett])
        for coil in self.settings[sett]["Sequence"]:
            if self._running:
                cs = self.configs[self.settings[sett]["Config"]][coil]
                print (coil, cs)
                # create wv
                print("Creating waveform with Amp = {0}, Freq = {1}, Dur = {2}, Keep = {3}".format(cs['Amp'], cs['Freq'],cs['Dur'], cs['Keep']))
                wv = self.createWaveform(cs['Amp'], cs['Freq'], 0 ,cs['Dur'], cs['Keep'])
                plt.plot(wv[:,1])
                plt.show()
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
                self.playWaveform(dev, wv)
                # deactivate coil
                print("deactivate coil")
                self.coilswitcher.deactivate(cs["RelayPort"])
                # vd.resetall()
                print("voltagedivider reset all")
                self.voltagedivider.resetall()
            else:
                self.coilswitcher.alloff()
                self.voltagedivider.resetall()


import controller

c = controller.DegaussingController()
c.voltagedivider.setnr(5)

#self.playWaveform(dev, cs['Amp'], cs['Freq'] ,cs['Dur'], cs['Keep'], 0)
c.playWaveform("Dev1", 7, 10 , 100, 10, 0)

c.voltagedivider.resetall()
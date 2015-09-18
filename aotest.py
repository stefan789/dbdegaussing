import nidaqmx
import numpy as np
import matplotlib.pyplot as plt

data = 9.95*np.sin(np.arange(1000, dtype=np.float64)*2*np.pi/1000)

duration = 8
sampleRate = 10000
offset = 0
freq = 10
keeptime = 1
amp = 2.0
t = np.linspace(0, duration, duration*sampleRate + 1)
x = np.asarray(offset + ( (-1) * np.sin( 2*np.math.pi * freq * t ) * np.piecewise(t, [t<keeptime, t>=keeptime], [amp, lambda t: -((t-keeptime) * amp/(duration-keeptime))+amp])), dtype=np.float64)

print data.dtype
print x.dtype
task = nidaqmx.AnalogOutputTask()
task.create_voltage_channel("Dev1/ao0", min_val=-10.0, max_val=10.0)
task.configure_timing_sample_clock(rate=10000.0, sample_mode = 'finite' , samples_per_channel = len(x))
task.write(x, auto_start=False, layout='group_by_channel')
task.start()
task.wait_until_done(duration + 5)
task.stop()
del task

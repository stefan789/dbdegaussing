import nidaqmx
import numpy as np

data = 9.95*np.sin(np.arange(1000, dtype=np.float64)*2*np.pi/1000)
task = nidaqmx.AnalogOutputTask()
task.create_voltage_channel("Dev1/ao0", min_val=-10.0, max_val=10.0)
task.configure_timing_sample_clock(rate=1000.0)
task.write(data, auto_start=False)
task.start()
raw_input("Generating")
task.stop()
del task

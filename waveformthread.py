import threading
import time
import ctypes
nidaq = ctypes.windll.nicaiu

int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
bool32 = uInt32
TaskHandle = uInt32

DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_ContSamps = 10123
DAQmx_Val_GroupByChannel = 0

class WaveformThread(threading.Thread):
    def __init__(self, device, waveform, samplerate):
        self.running = True
        self.device = device
        #self.chnnr = chnnr
        self.data = waveform[:,1]
        self.sampleRate = samplerate
        self.periodLength = len( self.data )
        self.time = waveform[:,0]
        self.taskHandle = TaskHandle( 0 )
        dev = str(self.device)
        dev = "Dev1/ao0"
        self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref( self.taskHandle )))
        self.CHK(nidaq.DAQmxCreateAOVoltageChan( self.taskHandle, dev, "", float64(-10.0), float64(10.0), DAQmx_Val_Volts, None))
        self.CHK(nidaq.DAQmxCfgSampClkTiming( self.taskHandle, "", float64(self.sampleRate), DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, uInt64(self.periodLength)))
        self.CHK(nidaq.DAQmxWriteAnalogF64( self.taskHandle, int32(self.periodLength), 0, float64(-1), DAQmx_Val_GroupByChannel, self.data.ctypes.data, None, None))
        threading.Thread.__init__(self)

    def CHK(self, err):
        '''a simple error checking routine'''
        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
            raise RuntimeError('nidaq failed with error %d: %s'%(err, repr(buf.value)))
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
            raise RuntimeError('nidaq generated waring %d: %s'%(err, repr(buf.value)))

    def run(self):
        self.CHK(nidaq.DAQmxStartTask( self.taskHandle ))
        ret_bool = bool32()
        self.CHK(nidaq.DAQmxIsTaskDone( self.taskHandle, ctypes.byref(ret_bool)))
        while( ret_bool.value == 0 ):
            time.sleep(2)
            nidaq.DAQmxIsTaskDone( self.taskHandle, ctypes.byref(ret_bool))
            #print ret_bool.value
        time.sleep(2)

    def stop(self):
        self.running = False
        nidaq.DAQmxStopTask( self.taskHandle )

    def __del__(self):
        nidaq.DAQmxClearTask( self.taskHandle )

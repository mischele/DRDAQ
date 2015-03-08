# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 12:26:44 2015

@author: mbeltle
"""

import sys
import ctypes
import time
import numpy as np

LIBNAME = 'C:\Program Files (x86)\Pico Technology\PicoScope6\\USBDrDAQ.dll'

recording_block = ctypes.c_int16(200000)
wanted_no_of_samples= ctypes.c_int16(20000)
channel = ctypes.c_int16(4)
no_of_active_channels=ctypes.c_int16(1)
measurement_results = (ctypes.c_short * 20000)()



VERBOSE = 1


class DRDAQ:
    def __init__(self):
        self.handle = None   
        self.lib = ctypes.windll.LoadLibrary(LIBNAME)
        self.handle = self.open_unit()
        #self.get_DAQ_vertical_scaling()
        self.set_DAQ_interval()
    
    def open_unit(self):
        if VERBOSE: 
                print('===Connecting to DRDAQ====')
        try:
            self.handle=ctypes.c_int16() 
            DrDaqStatus = self.lib.UsbDrDaqOpenUnit(ctypes.byref(self.handle))
        except OSError:
            print('\nNo Picoscope library found, switching to fake data mode\n')
        
        
        if VERBOSE:
            print(' PicoStatus: '+str(DrDaqStatus))
            print(' Handle is '+str(self.handle.value))
        return self.handle
            
    def close_unit(self):
        if VERBOSE:
            print('\n ===Closing Connection to DRDAQ====')
        try:
            res= self.lib.UsbDrDaqCloseUnit(self.handle)
            if VERBOSE:
                print(' PicoStatus: '+str(res))
        except OSError:
            print('Closing failed')
        
    def get_DAQ_info(self):
        print('Not yet implemented')
        
    def set_DAQ_interval(self):
        if VERBOSE:
            print('\n ===Setting Sampling Rate===')
        res = self.lib.UsbDrDaqSetInterval(self.handle,ctypes.byref(recording_block),wanted_no_of_samples,ctypes.byref(channel),no_of_active_channels)
        if VERBOSE:
            print(' Status of interval setting: '+str(res))
    
    def run_single_shot(self):
        res= self.lib.UsbDrDaqRun(self.handle,wanted_no_of_samples,ctypes.c_int16(1))
        if VERBOSE:
            print('\n Initialising single shot measurement')
            print(' Status of single shot run: '+str(res))
    
    def sampling_done(self):
        done = ctypes.c_bool(0)
        res = self.lib.UsbDrDaqReady(self.handle,ctypes.byref(done))
        if VERBOSE:
            print('\n Checking if sampling is done')            
            print(' PicoStatus: '+str(res))
            print(' Sampling done is: '+str(done))
            
    def stop_sampling(self):
        res= self.lib.UsbDrDaqStop(self.handle)
        if VERBOSE:
            print('\n ===Stopping Sampling===')
            print('PicoStatus: '+str(res))
    
    def get_sampled_values(self):
        noOfValues = wanted_no_of_samples
        Overflow = ctypes.c_int16(0)
        res= self.lib.UsbDrDaqGetValues(self.handle,ctypes.byref(measurement_results),ctypes.byref(noOfValues),ctypes.byref(Overflow),None)
        if VERBOSE:
            print(' \n PicoStatus sampling: '+str(res))
            print(' Number of Samples measured: '+str(noOfValues))
            print(' Channel with Overflow: '+str(Overflow))
            if res == 0:
                samples= np.ctypeslib.as_array(measurement_results)
                print(str(samples))
            return samples
            
    def get_DAQ_vertical_scaling(self):
        print('\n ===Getting vertical scaling===')
        available_scalings= ctypes.c_int16()
        current_scaling=ctypes.c_int16()
        scaling_names_indices= (ctypes.c_char*1000)()
        name_size = ctypes.c_int16()
        res= self.lib.UsbDrDaqGetScalings(self.handle,channel,ctypes.byref(available_scalings),ctypes.byref(current_scaling),ctypes.byref(scaling_names_indices),name_size)
        if VERBOSE:
            print('\n ===Getting vertical scaling===')
            print('PicoStatus of vertical scaling aquisition: '+str(res))
            print('current scaling: '+str(current_scaling)) 
            print('available scalings: '+str(available_scalings))
            print('PicoStatus: '+str(name_size))
        
if __name__ == '__main__':
        try:
            DRDAQ = DRDAQ()
        except:
            print('Error opening Picoscope')
        DRDAQ.run_single_shot()
        DRDAQ.sampling_done()
        time.sleep(1)
        DRDAQ.sampling_done()
        samples= DRDAQ.get_sampled_values()
        
        DRDAQ.stop_sampling()
        #DRDAQ.close_unit()



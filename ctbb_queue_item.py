import sys
import os
import shutil
import logging
import random
import tempfile
from hashlib import md5
from time import strftime

from ctbb_pipeline_library import ctbb_pipeline_library as ctbb_plib
from ctbb_pipeline_library import mutex

from enum import Enum

class qi_status(Enum):
    SUCCESS              = 0
    NO_RAW               = 1
    DOSE_REDUCTION_ERROR = 2
    RECONSTRUCTION_ERROR = 3

class ctbb_queue_item:

    filepath        = None
    dose            = None
    slice_thickness = None
    kernel          = None
    current_library = None
    device          = None
    device_mutex    = None

    def __init__(self,qi,device,library):
        self.qi_raw          = qi;
        
        qi=qi.split(',')

        self.filepath        = qi[0]
        self.dose            = qi[1]
        self.kernel          = qi[2]
        self.slice_thickness = qi[3]
        self.current_library = ctbb_plib(library)
        self.device          = mutex(device,self.current_library.mutex_dir)

        exit_status=qi_status.SUCCESS

    def __enter__(self):
        self.device.lock()
        return self

    def __exit__(self,type,value,traceback):
        self.device.unlock()

    def get_raw_data(self):
        exit_status=qi_status.SUCCESS;
        logging.info('Making sure we have raw data files')
        self.current_library.locate_raw_data(self.filepath)
        return exit_status

    def simulate_reduced_dose(self):
        exit_status=qi_status.SUCCESS;
        logging.info('Simulating reduced dose data')
        return exit_status

    def make_final_prm(self):
        exit_status=qi_status.SUCCESS;        
        logging.info('Assembling final PRM file')
        return exit_status
        
    def dispatch_recon(self):
        exit_status=qi_status.SUCCESS;        
        logging.info('Launching reconstruction')    
        return exit_status
        
    def clean_up(self,exit_status):
        # Move job into ".proc/done" or ".proc/error" files

        if exit_status == qi_status.SUCCESS:
            done_mutex=mutex('done',self.current_library.mutex_dir)
            done_mutex.lock()

            with open(os.path.join(self.current_library.path,'.proc','done'),'a') as f:
                f.write("%s\n" % self.qi_raw)

            done_mutex.unlock()
        else:
            error_mutex=mutex('error',self.current_library.mutex_dir)
            error_mutex.lock()

            with open(os.path.join(self.current_library.path,'.proc','error'),'a') as f:
                f.write("%s:%s\n" % (self.qi_raw,exit_status.name))

            error_mutex.unlock()
        
        logging.info('Cleaning up queue item')
            
if __name__=="__main__":

    logdir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'log');
    logfile=os.path.join(logdir,('%s_qi.log' % (strftime('%y%m%d_%H%M%S'))))

    if not os.path.isdir(logdir):
        os.mkdir(logdir);

    logging.basicConfig(format=('%(asctime)s %(message)s'), filename=logfile, level=logging.DEBUG)
                        
    qi=sys.argv[1]
    dev=sys.argv[2]
    lib=sys.argv[3]

    with ctbb_queue_item(qi,dev,lib) as queue_item:    
        exit_status=qi_status.SUCCESS
        
        # Check for (and acquire if needed) 100% raw data
        if exit_status==qi_status.SUCCESS:
            exit_status=queue_item.get_raw_data()
        
        # If doing reduced dose, check for (and simulate if needed) reduced-dose data
        if exit_status==qi_status.SUCCESS:    
            if str(queue_item.dose) != '100':        
                exit_status=queue_item.simulate_reduced_dose()
        
        # Assemble final parameter file
        if exit_status==qi_status.SUCCESS:        
            exit_status=queue_item.make_final_prm()
        
        # Launch reconstruction
        if exit_status==qi_status.SUCCESS:        
            exit_status=queue_item.dispatch_recon()
        
        # Clean up after ourselves
        queue_item.clean_up(exit_status)

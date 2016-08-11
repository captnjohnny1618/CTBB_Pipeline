import sys
import os
import shutil
import logging
import random
import tempfile
from hashlib import md5

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

    def __init__(self,qi,device,library):
        qi=qi.split(',')
        
        self.filepath        = qi[0]
        self.dose            = qi[1]
        self.kernel          = qi[2]
        self.slice_thickness = qi[3]
        self.device          = device
        self.current_library = library

        exit_status=qi_status.SUCCESS

    def get_100_data(self):
        logging.info('Checking for full-dose raw data')
        
        # Check for 100% raw data
        found=self.current_library.have_raw_data(self.filepath)
        
        if not found:
            # Signal to library to fetch/simulate requested file
            logging.info("Full-dose raw data file not found");
            exit_status=qi_status.NO_RAW;
        else:
            # Have raw data exactly listed in case list:
            if found == True:
                logging.info("Full-dose raw data found in library")
            else:
                # File not yet in library, copy and add to case list
                if os.path.exists(found):
                    self.current_library.add_raw_data(found,self.dose)


    def clean_up(self,exit_status):
        logging.info('Cleaning up queue item')

            

if __name__=="__main__":

    qi=sys.argv[1]
    dev=sys.argv[2]
    lib=sys.argv[3]
    
    queue_item=ctbb_queue_item(qi,dev,lib)

    exit_status=qi_status.SUCCESS
    
    # Check for (and acquire if needed) 100% raw data
    if exit_status==qi.SUCCESS:
        exit_status=queue_item.get_100_data()

    # If doing reduced dose, check for (and simulate if needed) reduced-dose data
    if exit_status==qi.SUCCESS:    
        if str(queue_item.dose) != '100':        
            exit_status=queue_item.simulate_reduced_dose()

    # Assemble final parameter file
    if exit_status==qi.SUCCESS:        
        exit_status=queue_item.make_final_prm()

    # Launch reconstruction
    if exit_status==qi.SUCCESS:        
        exit_status=queue_item.dispatch_recon()

    # Clean up after ourselves
    queue_item.clean_up(exit_status)

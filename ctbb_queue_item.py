import sys
import os
import shutil
import logging
import random
import tempfile
from hashlib import md5

from ctbb_pipeline_library import ctbb_pipeline_library as ctbb_plib
from ctbb_pipeline_library import mutex

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

        # Create dose level directories for raw data
        raw_dest_dir=os.path.join(self.current_library.raw_dir,self.dose)
        if not os.path.exists(raw_dest_dir):
            os.mkdir(raw_dest_dir)
        

    def get_raw_data(self):
        # Lock case list 
        case_list_mutex=mutex('case_list',self.current_library.mutex_dir)
        case_list_mutex.lock()

        # Read the current list of cases imported to library
        with open(os.path.join(self.current_library.path,'case_list.txt')) as f:
            case_list=f.read().splitlines();
            for i in range(len(case_list)):
                if case_list:
                    curr_case=case_list[i].split(',')
                    tmp_dict['filepath']=curr_case[0]
                    tmp_dict['hash']=curr_case[1]
                    case_list[i]=tmp_dict

        # Check if exact filepath occurs, assume we already have file if so

        # If filepath does not occur, compute hash 
        tmp_filepath=os.path.join(tempfile.mkdtemp,random.getrandbits(128))
        shutil.copy(filepath,tmp_filepath)
        logging.info("Computing hash of %s" % filepath)
    
        with open(tmp_filepath,'rb') as f:
            digest=md5(f.read()).hexdigest()

        # If simulating reduced dose, checks for existing file, otherwise runs simulation


        
        case_list_mutex.unlock()

if __name__=="__main__":
    



    

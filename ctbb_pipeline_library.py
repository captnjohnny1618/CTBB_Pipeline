import sys
import os
import shutil
import logging
from subprocess import call
import time
from time import strftime

import random
import tempfile
from hashlib import md5

class mutex:
    name=None;
    mutex_dir=None;
    mutex_file=None;
    
    def __init__(self,name,mutex_dir):
        self.name=name
        self.mutex_dir=mutex_dir;
        self.mutex_file=os.path.join(mutex_dir,name);
        
    def lock(self):
        # If mutex alread locked, wait for other process to unlock
        while os.path.exists(self.mutex_file):
            logging.debug('Mutex ' + self.name  + ' locked. Sleeping and trying again')
            time.sleep(5)
        touch(self.mutex_file)            

    def unlock(self):
        os.remove(self.mutex_file);

    def check_state(self):
        state=os.path.exists(self.mutex_file)

        if state==True:
            logging.debug('Mutex file: %s LOCKED' % str(self.mutex_file))
        else:
            logging.debug('Mutex file: %s UNLOCKED' % str(self.mutex_file))

        return state
            
class ctbb_pipeline_library:
    path=None;
    mutex_dir=None;    
    raw_dir=None;
    recon_dir=None;

    def __init__(self,path):
        self.path=path;
        self.mutex_dir=os.path.join(path,'.proc','mutex');
        self.raw_dir=os.path.join(path,'raw');
        self.recon_dir=os.path.join(path,'recon');

        if not self.is_library():
            self.initialize_new_library()
        else:
            if not self.is_valid():
                self.repair()

            self.load()                
        
    def initialize_new_library(self):
        touch(os.path.join(self.path,'.ctbb_pipeline_lib'))
        touch(os.path.join(self.path,'case_list.txt'))
        touch(os.path.join(self.path,'recons.csv'))
        touch(os.path.join(self.path,'README.txt'))
        os.mkdir(os.path.join(self.path,'raw'))
        os.mkdir(os.path.join(self.path,'recon'))
        os.mkdir(os.path.join(self.path,'.proc'))
        os.mkdir(os.path.join(self.path,'.proc','mutex'))        
        touch(os.path.join(self.path,'.proc','queue'))
        touch(os.path.join(self.path,'.proc','done'))
        touch(os.path.join(self.path,'.proc','error'))
        
    def is_library(self):
        if os.path.exists(os.path.join(self.path,'.ctbb_pipeline_lib')):
            tf=True
        else:
            tf=False            
        return tf

    def is_valid(self):

        tf = True;

        tf = tf and os.path.exists(os.path.join(self.path,'.ctbb_pipeline'))
        tf = tf and os.path.exists(os.path.join(self.path,'case_list.txt'))
        tf = tf and os.path.exists(os.path.join(self.path,'recons.csv'))
        tf = tf and os.path.exists(os.path.join(self.path,'README.txt'))
        tf = tf and os.path.isdir(os.path.join(self.path,'raw'))
        tf = tf and os.path.isdir(os.path.join(self.path,'recon'))
        tf = tf and os.path.isdir(os.path.join(self.path,'.proc'))
        tf = tf and os.path.isdir(os.path.join(self.path,'.proc','mutex'))        
        tf = tf and os.path.exists(os.path.join(self.path,'.proc','queue'))
        tf = tf and os.path.exists(os.path.join(self.path,'.proc','done'))
        tf = tf and os.path.exists(os.path.join(self.path,'.proc','error'))
                                  
        return tf;

    def load(self):
        logging.debug('Nothing to be done to load library currently');
                                                           
    def repair(self):
        touch(os.path.join(self.path,'.ctbb_pipeline_lib'))
        touch(os.path.join(self.path,'case_list.txt'))
        touch(os.path.join(self.path,'recons.csv'))
        touch(os.path.join(self.path,'README.txt'))
        
        if not os.path.isdir(os.path.join(self.path,'raw')):
            os.mkdir(os.path.join(self.path,'raw'))
        if not os.path.isdir(os.path.join(self.path,'recon')):            
            os.mkdir(os.path.join(self.path,'recon'))
        if not os.path.isdir(os.path.join(self.path,'.proc')):            
            os.mkdir(os.path.join(self.path,'.proc'))
        if not os.path.isdir(os.path.join(self.path,'.proc','mutex')):            
            os.mkdir(os.path.join(self.path,'.proc','mutex'))
            
        touch(os.path.join(self.path,'.proc','queue'))
        touch(os.path.join(self.path,'.proc','done'))
        touch(os.path.join(self.path,'.proc','error'))

    def locate_raw_data(self,filepath):
        case_list_mutex=mutex('case_list',self.mutex_dir)
        case_list_mutex.lock()
        
        # Returns either a hash value (of raw file) or "False" if raw data unavailable
        case_list=self.__get_case_list__()

        # Check if we already have file in library
        if filepath in case_list.keys():
            logging.info('File %s (%s) found case library' % (filepath,case_list[filepath]))
            case_id=case_list[filepath]
        else:
            if os.path.exists(filepath):
                local_file_info=self.__get_local_file_hash__(filepath)
                digest=local_file_info[0]
                tmp_path=local_file_info[1]
                if not (digest in case_list.keys()):
                    logging.info('Adding raw data file to library')
                    self.__add_raw_data__(filepath,tmp_path,digest)
                case_id=digest;
            else:
                # Requested file does not exist
                logging.info('Requested raw data file does not exist')
                case_id=False

        case_list_mutex.unlock();
        
        return case_id
    
    def __add_raw_data__(self,filepath_org,filepath_tmp,digest):
        out_dir=os.path.join(self.path,'raw','100')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        
        os.rename(filepath_tmp,os.path.join(out_dir,digest))
        self.__add_to_case_list__(filepath_org,digest)

    def __add_to_case_list__(self,filepath,digest):
        logging.info("Adding %s:%s to case list" % (digest,filepath))
        with open(os.path.join(self.path,'case_list.txt'),'a') as f:
            f.write("%s,%s\n" % (filepath,digest))
        
    def __get_case_list__(self):
        # Returns current case list as dictionary with filepaths as keys and file hashes as values
        case_list_dict={}
        
        with open(os.path.join(self.path,'case_list.txt'),'r') as f:
            case_list=f.read().splitlines()
            for i in range(len(case_list)):
                if case_list:
                    curr_case=case_list[i].split(',')
                    digest=curr_case[1]
                    filepath=curr_case[0]
                    case_list_dict[digest]=filepath;
                    case_list_dict[filepath]=digest;

        return case_list_dict

    def __get_local_file_hash__(self,filepath):
        # Copy file to temporary location
        tmp_filepath=os.path.join(tempfile.mkdtemp(),str(random.getrandbits(128)))
        logging.debug('Temporary path to file: %s' % tmp_filepath)
        shutil.copy(filepath,tmp_filepath)
        logging.info("Computing hash of %s" % filepath)
        
        with open(tmp_filepath,'rb') as f:
            digest=md5(f.read()).hexdigest()

        return (digest,tmp_filepath)
                  

def touch(path):
    with open(path,'a'):
        os.utime(path,None);

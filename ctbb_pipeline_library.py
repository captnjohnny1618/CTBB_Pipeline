import sys
import os
import logging
from subprocess import call
import time
from time import strftime

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


def touch(path):
    with open(path,'a'):
        os.utime(path,None);
                                  

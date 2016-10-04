# Pypeline.py: Class library for items common to multiple pipeline tools

import sys
import os

import logging
import yaml

from subprocess import call

def touch(path):
    with open(path,'a'):
        os.utime(path,None);

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

class case_list:
    filepath=None;
    case_list=None;
    prmbs=[];
    prmbs_raw=[];

    def __init__(self,filepath):
        self.filepath=filepath
        accepted_filetypes=['.ctd','.ptr','.ima','.txt']
        # Get file type and open accordingly
        ext=os.path.splitext(self.filepath)
        ext=ext[1].lower();

        logging.info('Detected file extension: ' + ext)

        self.case_list=[];
        
        if (ext in accepted_filetypes):
            logging.info('File extension accepted')
            
            if ext == '.txt':
                with open(self.filepath,'r') as f:
                    self.case_list=f.read().splitlines()
            else:
                self.case_list.append(self.filepath)
        else:
            self.error_dialog('Unrecognized filetype.  Accepted filetypes are IMA, PTR, CTD, and TXT')
            logging.error('User tried to load an unrecognized filetype:' + self.filepath)
            return;
        
    def get_prmbs(self):
        logging.info('Generating parameter files and reading into pipeline');

        prmbs=[];

        for f in self.case_list:
    
            if not f:
                continue
            
            # Generate the parameter file
            devnull=open(os.devnull,'w')
            call(['ctbb_info','-b',f],stdout=devnull,stderr=devnull);
    
            # Open the parameter file and read into pipeline
            with open(f+'.prmb') as f_prmb:
                self.prmbs_raw.append(f_prmb.read())
                prmbs.append(f_prmb.read())

        # Sanitize and parse into dictionaries
        for s in prmbs:
            s=s.replace('\t','  ')
            s=s.replace('%','#')
            self.prmbs.append(yaml.load(s))

            
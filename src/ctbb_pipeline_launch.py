import sys
import os

import yaml
import logging

import pypeline as pype 

def usage():
    logging.info('usage: ctbb_pipeline_launch.py /path/to/config/file.yaml')
    logging.info('    Copyright (c) John Hoffman 2016')

def load_config(filepath):

    logging.info('Loading configuration file: %s' % filepath)

    # Load pipeline run from YAML configuration file 
    with open(sys.argv[1],'r') as f:
        yml_string=f.read();

    config_dict=yaml.load(yml_string)

    # We only require that a case list and output library be defined
    if ('case_list' not in config_dict.keys()) or ('library' not in config_dict.keys()):
        logging.error('"case_list" and "library" are required fields in ctbb_pipeline configuration file and one or the other was not found. Exiting."')
        config_dict={}

    else:
        # Check for optional fields. Set to defaults as needed.
        # Doses
        if ('doses' not in config_dict.keys()):
            config_dict['doses']=[100,10]
        
        # Slice Thickness
        if ('slice_thickness' not in config_dict.keys()):
            config_dict['slice_thickness']=[0.6,5.0]

        # Kernel
        if ('kernels' not in config_dict.keys()):
            config_dict['kernels']=[1,3]

        if not os.path.isdir(config_dict['library']):
            os.makedirs(config_dict['library'])
            logging.warning('Library directory does not exist, creating.')
            
        # Verify that the case list and library directory exist
        if not os.path.exists(config_dict['case_list']):
            logging.error('Specified case_list does not exist. Exiting.')
            config_dict={}
            
    return config_dict
        
if __name__=='__main__':
    status = 0
    
    if (len(sys.argv) < 2):
        usage()
    else:
        filepath=sys.argv[1]
                 
    if not os.path.exists(filepath):        
        logging.error('Configuration file not found! Exiting.')
        status=1
    else:
        config=load_config(filepath)

        # Configuration loaded properly
        if config:
            # Get PRMBs from raw files
            cases=pype.case_list(config['case_list'])
            cases.get_prmbs()

            # Flush PRMBs to pipeline library

            # Flush new jobs to the queue

            # Launch the daemon in the background
            
        # Configuration didn't load properly
        else:
            logging.error('Something went wrong parsing pipeline configuration file') 
            status=1

    sys.exit(status)

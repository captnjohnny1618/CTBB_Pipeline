import sys
import os
import logging

from ctbb_pipeline_library import ctbb_pipeline_library as ctbb_plib
from ctbb_pipeline_library import mutex 

class ctbb_daemon:

    daemon_mutex=None
    pipeline_lib=None

    def __init__(self,path):
        logging.info('CTBB Pipeline Daemon: launching')
        self.pipeline_lib=ctbb_plib(path)
        self.daemon_mutex=mutex('daemon',self.pipeline_lib.mutex_dir)

    def __enter__(self):
        self.daemon_mutex.lock()
        return self

    def __exit__(self):        
        logging.info('CTBB Pipeline Daemon: exiting')
        self.daemon_mutex.unlock()

    def run(self):
        logging.info('CTBB Pipeline Daemon: RUNNING')
        logging.debug('CTBB Pipeline Daemon: run method not implemented, sleeping for 5 seconds.')
        time.sleep(5);
        
    def idle(self):
        logging.info('CTBB Pipeline Daemon: going idle')

    def grab_next_job(self)
        
if __name__=="__main__":
    m=mutex('daemon',os.path.join(sys.argv[1],'.proc','mutex'))

    # If not running on current directory launch an instance of our daemon
    if m.check_state():
        with ctbb_daemon(sys.argv[1]) as ctbb_pd:
            ctbb_pd.run();
    # If instance already running on current dir, exit
    else:
        sys.exit()

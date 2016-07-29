import sys
import os
import logging
import time
from time import strftime

import csv

from ctbb_pipeline_library import ctbb_pipeline_library as ctbb_plib
from ctbb_pipeline_library import mutex         

class ctbb_daemon:

    daemon_mutex=None
    queue_mutex=None
    pipeline_lib=None
    devices=[]
    queue=None

    def __init__(self,path):
        logging.info('CTBB Pipeline Daemon: launching')
        self.pipeline_lib=ctbb_plib(path)
        self.daemon_mutex=mutex('daemon',self.pipeline_lib.mutex_dir)
        self.queue_mutex=mutex('queue',self.pipeline_lib.mutex_dir)
        self.get_devices()

    def __enter__(self):
        self.daemon_mutex.lock()
        return self

    def __exit__(self,type,value,traceback):
        logging.info('CTBB Pipeline Daemon: exiting')
        self.daemon_mutex.unlock()

    def __child_process__(self,c):
        os.system("nohup %s >/dev/null 2>&1 &" % c);

    def get_devices(self):
        import pycuda.autoinit
        import pycuda.driver as cuda

        n_devices=cuda.Device.count();

        logging.info('%d CUDA devices found' % n_devices);

        for i in range(n_devices):            
            self.devices.append(mutex(('dev%d' % i),self.pipeline_lib.mutex_dir))

            device=cuda.Device(i)
            attrs=device.get_attributes()

            if attrs[pycuda._driver.device_attribute.KERNEL_EXEC_TIMEOUT]:
                logging.info('Display attached to DEVICE %d' % i)

    def run(self):
        logging.info('CTBB Pipeline Daemon: RUNNING')

        i=0
        
        while i==0:
            self.queue_mutex.lock(); 
        
            self.refresh_queue()
            self.check_devices()

        #    for dev in empty_devices:        
        #        process_next_queue_item(dev);

            self.queue_mutex.unlock()
            time.sleep(10)
            i+=1

    def refresh_queue(self):
        with open(os.path.join(self.pipeline_lib.path,'.proc','queue')) as f:
            self.queue=f.read().splitlines();
        logging.debug('Queue is:\n%s' % str(self.queue))
            
    def check_devices(self):
        logging.info('Checking for device availability')
        empty_devices=[]
        for i in range(len(self.devices)):
            dev=self.devices[i]
            if not dev.check_state():
                logging.info('Device %d available for next job' % i)
                empty_devices.append(dev)

        return empty_devices
        
    def idle(self):
        logging.info('CTBB Pipeline Daemon: going idle')

    def grab_next_job(self):
        logging.info('CTBB Pipeline Daemon: Starting next queue item')
        
if __name__=="__main__":
    m=mutex('daemon',os.path.join(sys.argv[1],'.proc','mutex'))

    logdir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'log');
    logfile=os.path.join(logdir,('%s_daemon.log' % strftime('%y%m%d_%H%M%S')))

    if not os.path.isdir(logdir):
        os.mkdir(logdir);

    logging.basicConfig(format=('%(asctime)s %(message)s'),filename=logfile, level=logging.DEBUG)

    # If not running on current directory launch an instance of our daemon
    if not m.check_state():
        logging.info('No instance of CTBB Pipeline Daemon found for library')
        with ctbb_daemon(sys.argv[1]) as ctbb_pd:
            ctbb_pd.run();

    # If instance already running on current dir, exit    
    else:
        logging.info('Instance of CTBB Pipeline Daemon already running.')
        # Clean up unneeded logfile if we're not debugging
        #if logging.getLogger().getEffectiveLevel() != logging.DEBUG:
        #    os.remove(logfile);
        sys.exit()

# A script to mine queue item logs for data 

import sys
import os

import csv
from datetime import datetime

def mine_qi_logfile(filepath):

    # Mine for the following key phrases:
    #     START/END: QUEUE ITEM
    #     START/END: FETCH RAW
    #     START/END: DOSE REDUCTION
    #     START/END: RECON

    metrics={}

    metrics['filename']=filepath
    
    # Grab the logfile
    with open(filepath,'r') as f:
        logfile=f.read().splitlines()

    def extract_logfile_time(keyphrase):
        for line in logfile:
            if keyphrase in line:
                s=line.split(',')
                t=datetime.strptime(s[0],"%Y-%m-%d %H:%M:%S")

        return t

    # Total execution time:
    tdelta=extract_logfile_time('END: QUEUE ITEM')-extract_logfile_time('START: QUEUE ITEM')
    #print('Total time: %.2f' % tdelta.total_seconds());
    metrics['time_total']=tdelta.total_seconds()

    # Fetch time:
    tdelta=extract_logfile_time('END: FETCH RAW')-extract_logfile_time('START: FETCH RAW')
    #print('Time to retrieve raw data: %.2f' % tdelta.total_seconds());
    metrics['time_fetch_raw']=tdelta.total_seconds()    

    # Simdose execution time:
    tdelta=extract_logfile_time('END: DOSE REDUCTION')-extract_logfile_time('START: DOSE REDUCTION')
    #print('Dose reduction time: %.2f' % tdelta.total_seconds()); 
    metrics['time_dose_reduction']=tdelta.total_seconds()       

    # Recon execution time:
    tdelta=extract_logfile_time('END: RECON')-extract_logfile_time('START: RECON')
    #print('Recon time: %.2f' % tdelta.total_seconds());
    metrics['time_recon']=tdelta.total_seconds()

    return metrics

if __name__=="__main__":

    # CL input should be the "log" directory of a pipeline library

    logdir=sys.argv[1]
    files=[f for f in os.listdir(logdir) if os.path.isfile(os.path.join(logdir,f))]
    files=[os.path.join(logdir,f) for f in files]

    header_written=False
    with open(os.path.join(logdir,'metrics.csv'),'wb') as f:
        for filename in files:
            if 'qi' in filename:
                metrics_dict=mine_qi_logfile(filename)
                w=csv.DictWriter(f,metrics_dict.keys())

                if not header_written:
                    header_written=True
                    w.writeheader()

                w.writerow(metrics_dict);
                
    ## Our final product should be a CSV file containing all of the raw data
    ## as well as a line summarizing the totals and averages for each process

    ## Desired summary data
    # Total time
    # Total recon time
    # Total simdose time
    # Total data fetch time

    # Average fetch time
    # Average time per recon
    # Average time per dose reduction
    # Average total time per 

    
    

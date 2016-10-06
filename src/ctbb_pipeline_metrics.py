# A script to mine queue item logs for data 

import sys
import os

from datetime import datetime

def mine_qi_logfile(filepath):

    # Mine for the following key phrases:
    #     START/END: QUEUE ITEM
    #     START/END: FETCH RAW
    #     START/END: DOSE REDUCTION
    #     START/END: RECON

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
    print('Total time: %.2f' % tdelta.total_seconds());

    # Fetch time:
    tdelta=extract_logfile_time('END: FETCH RAW')-extract_logfile_time('START: FETCH RAW')
    print('Time to retrieve raw data: %.2f' % tdelta.total_seconds());

    # Simdose execution time:
    tdelta=extract_logfile_time('END: DOSE REDUCTION')-extract_logfile_time('START: DOSE REDUCTION')
    print('Dose reduction time: %.2f' % tdelta.total_seconds());

    # Recon execution time:
    tdelta=extract_logfile_time('END: RECON')-extract_logfile_time('START: RECON')
    print('Recon time: %.2f' % tdelta.total_seconds());

if __name__=="__main__":
    mine_qi_logfile(sys.argv[1]);

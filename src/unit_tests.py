import os
import sys

import pypeline as pype

if __name__=='__main__':
    cl=pype.case_list('/PechinTest2/pre-pilot_pipeline/case_list.txt')
    cl.get_prmbs();
    


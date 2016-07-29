import sys
import os
import logging
from subprocess import call
from time import strftime
from PyQt4 import QtGui, uic

from ctbb_pipeline_library import ctbb_pipeline_library as ctbb_plib
from ctbb_pipeline_library import mutex 

class MyWindow(QtGui.QMainWindow):

    ui=None;
    current_cases=None; # Python list of raw data filepaths
    current_library=None; # Path to currently loaded library
    
    def __init__(self):
        logging.getLogger("PyQt4").setLevel(logging.WARNING)

        logging.info('GUI Initialization initiated')
        
        super(MyWindow,self).__init__()
        self.ui=uic.loadUi('ctbb_pipeline.ui',self)
        self.show()

        # Connect Callbacks
        self.ui.selectCases_pushButton.clicked.connect(self.select_cases_callback)
        self.ui.selectLibrary_pushButton.clicked.connect(self.select_library_callback);
        self.ui.queueNormal_pushButton.clicked.connect(self.queue_normal_callback);
        self.ui.queueHighPriority_pushButton.clicked.connect(self.queue_high_priority_callback);

        logging.info('GUI Initialization finished')

    def testCallback(self):
        print('Test worked!');

    def select_cases_callback(self):
        logging.info('Select cases callback active')
        
        accepted_filetypes=['.ctd','.ptr','.ima','.txt']

        # File selection dialog
        fname=QtGui.QFileDialog.getOpenFileName(self,'Open file','/home');

        # Return if user cancelled
        if not fname:
            return;
        else:
            fname=str(fname)

        # Get file type and open accordingly
        ext=os.path.splitext(fname)
        ext=ext[1].lower();

        logging.info('Detected file extension: ' + ext)

        case_list=[];
        
        if (ext in accepted_filetypes):
            logging.info('File extension accepted')
            
            if ext == '.txt':
                with open(fname,'r') as f:
                    case_list=f.read().splitlines()
            else:
                case_list.append(fname)
        else:
            self.error_dialog('Unrecognized filetype.  Accepted filetypes are IMA, PTR, CTD, and TXT')
            logging.error('User tried to load an unrecognized filetype:' + fname)
            return;

        # Set lineEdit string to file path
        self.ui.selectCases_edit.setText(fname)

        # If text file, load into memory and display in box
        # Run ctbb_info to generate base parameter files
        prmb_string=get_base_parameter_files(case_list)

        for i in range(0,len(prmb_string)):
            self.ui.PRMEditor_textEdit.insertPlainText('#####! DO NOT EDIT THIS LINE !#####\n');
            self.ui.PRMEditor_textEdit.insertPlainText('%%% Edit below for file: ' + case_list[i] + ' %%%\n\n');
            self.ui.PRMEditor_textEdit.insertPlainText(prmb_string[i]);
            self.ui.PRMEditor_textEdit.insertPlainText('\n\n');

        self.current_cases=case_list;
            
    def select_library_callback(self):
        logging.info('Select library callback active')
        dirname=QtGui.QFileDialog.getExistingDirectory(self,'Open Directory','/home');
        if not dirname:
            return;
        else:
            dirname=str(dirname)

        pipeline_lib=ctbb_plib(dirname)
            
        self.ui.selectLibrary_edit.setText(dirname)
        self.current_library=pipeline_lib

    def queue_normal_callback(self):
        logging.info('Queue normal callback active')        
        self.flush_prmbs()
        ds,sts,ks=self.gather_run_parameters()
        self.flush_jobs_to_queue('normal',ds,sts,ks);
        self.dispatch_ctbb_pipeline_daemon()

    def queue_high_priority_callback(self):
        logging.info('Queue high priority callback active')
        self.flush_prmbs()
        ds,sts,ks=self.gather_run_parameters()
        self.flush_jobs_to_queue('high',ds,sts,ks);
        self.dispatch_ctbb_pipeline_daemon()

    def dispatch_ctbb_pipeline_daemon():
        call(['python',]
       
    

    def keyPressEvent(self,e):
        if e.matches(QtGui.QKeySequence.Close) or e.matches(QtGui.QKeySequence.Quit):
            sys.exit('User quit via keystroke')

    def flush_jobs_to_queue(self,priority,ds,sts,ks):
        logging.info('Sending jobs to queue')

        queue_strings=[]
        
        m=mutex('queue',self.current_library.mutex_dir)
        m.lock()

        # Form the strings to be written
        for c in self.current_cases:
            if not c:
                continue
            for dose in ds:
                for st in sts:
                    for kernel in ks:
                        queue_strings.append(('%s,%s,%s,%s\n') % (c,dose,kernel,st));


        queue_file=os.path.join(self.current_library.path,'.proc','queue')
        
        # If priority "normal" write to end of file
        if priority == 'normal':
            with open(queue_file,'a') as f:
                for q_string in queue_strings:
                    f.write(q_string)

        # If priority "high" write to beginning of file
        # Read queue into memory
        elif priority == 'high':
            with open(queue_file,'r') as f:
                existing_queue=f.read()
            
            # Pop new items into beginning of queue and then write rest of queue back
            with open(queue_file,'w') as f:
                for q_string in queue_strings:
                    f.write(q_string)
                f.write(existing_queue)

        # Handle any weirdness
        else:
            logging.error('Unknown queue priority request')

        m.unlock()
        
    def error_dialog(self,s):
        msg = QtGui.QMessageBox();
        msg.setIcon(QtGui.QMessageBox.Critical)
        msg.setInformativeText(s)
        msg.setWindowTitle('Error')
        msg.setStandardButtons(QtGui.QMessageBox.Close)
        msg.exec_()

    def flush_prmbs(self):
        raw_prm_text=str(self.ui.PRMEditor_textEdit.toPlainText())
        prmb_text=raw_prm_text.split('#####! DO NOT EDIT THIS LINE !#####\n')
        for i in range(1,len(prmb_text)):

            output_file_name=os.path.basename(self.current_cases[i-1])+'.prmb'
            output_dir_name=os.path.join(self.current_library.path,'raw')
            output_fullpath=os.path.join(output_dir_name,output_file_name);
            
            with open(output_fullpath,'w') as f:
                f.write(prmb_text[i])
        
    def gather_run_parameters(self):

        doses=[];
        slice_thicknesses=[];
        kernels=[];
        
        # Dose
        if self.ui.dose100_checkBox.checkState():
            doses.append('100')
        if self.ui.dose75_checkBox.checkState():
            doses.append('75')
        if self.ui.dose50_checkBox.checkState():
            doses.append('50')
        if self.ui.dose25_checkBox.checkState():
            doses.append('25')
        if self.ui.dose10_checkBox.checkState():
            doses.append('10')
        if self.ui.dose5_checkBox.checkState():
            doses.append('5')

        # Slice thickness
        if self.ui.sliceThickness0p6_checkBox.checkState():
            slice_thicknesses.append('0.6')
        if self.ui.sliceThickness1_checkBox.checkState():
            slice_thicknesses.append('1.0')
        if self.ui.sliceThickness1p5_checkBox.checkState():
            slice_thicknesses.append('1.5')
        if self.ui.sliceThickness2_checkBox.checkState():
            slice_thicknesses.append('2.0')
        if self.ui.sliceThickness3_checkBox.checkState():
            slice_thicknesses.append('3.0')
        if self.ui.sliceThickness5_checkBox.checkState():
            slice_thicknesses.append('5.0')
            
        # kernel
        if self.ui.kernel1_checkBox.checkState():
            kernels.append('1')
        if self.ui.kernel2_checkBox.checkState():
            kernels.append('2')
        if self.ui.kernel3_checkBox.checkState():
            kernels.append('3')

        logging.debug('            Doses checked: ' + str(doses))
        logging.debug('Slice thicknesses checked: ' + str(slice_thicknesses))
        logging.debug('          Kernels checked: ' + str(kernels))

        return doses,slice_thicknesses,kernels

def get_base_parameter_files(file_list):    
    logging.info('Generating parameter files and reading into pipeline');

    prmbs=[];
    
    for f in file_list:

        if not f:
            continue
        
        # Generate the parameter file
        devnull=open(os.devnull,'w')
        call(['ctbb_info','-b',f],stdout=devnull,stderr=devnull);

        # Open the parameter file and read into pipeline
        with open(f+'.prmb') as f_prmb:
            prmbs.append(f_prmb.read());

    return prmbs

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    if (len(sys.argv)>1) and (sys.argv[1]=='--debug'):
        logging.basicConfig(format=('%(asctime)s %(message)s'), level=logging.DEBUG)
    else:
        logdir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'log');
        logfile=os.path.join(logdir,('%s.log' % strftime('%y%m%d_%H%M%S')))

        if not os.path.isdir(logdir):
            os.mkdir(logdir);

        logging.basicConfig(format=('%(asctime)s %(message)s'),filename=logfile, level=logging.DEBUG)

    window = MyWindow()
    sys.exit(app.exec_())

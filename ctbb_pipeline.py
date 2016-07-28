import sys
import os
import logging
from subprocess import call
from time import strftime
from PyQt4 import QtGui, uic

class MyWindow(QtGui.QMainWindow):

    ui=None;
    
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
            self.ui.PRMEditor_textEdit.insertPlainText('%%% Edit below for file: ' + case_list[i] + ' %%%\n\n');
            self.ui.PRMEditor_textEdit.insertPlainText(prmb_string[i]);
            self.ui.PRMEditor_textEdit.insertPlainText('\n\n');
            
    def select_library_callback(self):
        logging.info('Select library callback active')
        dirname=QtGui.QFileDialog.getExistingDirectory(self,'Open Directory','/home');
        if not dirname:
            return;
        else:
            dirname=str(dirname)

        if not is_ctbb_pipeline_library(dirname):
            init_ctbb_pipeline_library(dirname)
        else:
            load_ctbb_pipeline_library(dirname)
            
        self.ui.selectLibrary_edit.setText(dirname)

    def queue_normal_callback(self):
        logging.info('Queue normal callback active');
        self.flush_prmbs();
        ctbb_pipeline_library
        
        ds,sts,ks=self.gather_run_parameters();


        
        
    def queue_high_priority_callback(self):
        print('Queue high priority callback active');

    def keyPressEvent(self,e):
        if e.matches(QtGui.QKeySequence.Close) or e.matches(QtGui.QKeySequence.Quit):
            sys.exit('User quit via keystroke')

    def queue(self):
        print('Select cases callback active');

    def error_dialog(self,s):
        msg = QtGui.QMessageBox();
        msg.setIcon(QtGui.QMessageBox.Critical)
        msg.setInformativeText(s)
        msg.setWindowTitle('Error')
        msg.setStandardButtons(QtGui.QMessageBox.Close)
        msg.exec_()

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
        call(['ctbb_info','-b',f]);

        # Open the parameter file and read into pipeline
        with open(f+'.prmb') as f_prmb:
            prmbs.append(f_prmb.read());

    return prmbs

def is_ctbb_pipeline_library(path):
    if os.path.exists(os.path.join(path,'.ctbb_pipeline_lib')):
        tf=True
    else:
        tf=False
        
    return tf
    
def init_ctbb_pipeline_library(path):
    logging.info('Initializing pipeline library for directory: ' + path)
    touch(os.path.join(path,'.ctbb_pipeline_lib'))
    touch(os.path.join(path,'case_list.txt'))
    touch(os.path.join(path,'recons.csv'))
    touch(os.path.join(path,'README.txt'))
    os.mkdir(os.path.join(path,'raw'))
    os.mkdir(os.path.join(path,'recon'))
    os.mkdir(os.path.join(path,'.proc'))
    touch(os.path.join(path,'.proc','queue'))
    touch(os.path.join(path,'.proc','mutex'))
    touch(os.path.join(path,'.proc','done'))

def load_ctbb_pipeline_library(path):
    logging.info('Loading a prexisting library (although not actually implemented yet..)');
    
def touch(path):
    with open(path,'a'):
        os.utime(path,None);
    
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

    

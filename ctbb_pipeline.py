import sys
import os
import logging
from subprocess import call
from time import strftime
from PyQt4 import QtGui, QtCore, uic

from ctbb_pipeline_library import ctbb_pipeline_library as ctbb_plib
from ctbb_pipeline_library import mutex 

class MyWindow(QtGui.QMainWindow):

    ui=None;
    current_cases=None; # Python list of raw data filepaths
    current_library=None; # Path to currently loaded library
    test_cases=None;
    test_library=None;

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

        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            self.run_tests();

    def run_tests(self):
        logging.debug('Running in TESTING mode');        
        self.test_cases = '/home/john/Code/CTBangBang_Pipeline/sample_case_list.txt';
        self.test_library = '/home/john/Desktop/pipeline_test_dir/';

        logging.debug('Test case list: ' + self.test_cases)
        logging.debug('Test library: ' + self.test_library)

        logging.debug('Running case load callback...')
        self.select_cases_callback()
        logging.debug('Running case load callback... DONE')

        logging.debug('Running case load callback...')
        self.select_library_callback()
        logging.debug('Running case load callback... DONE')

        logging.debug('Setting some checkboxes for testing...')
        self.ui.dose100_checkBox.setCheckState(True);
        self.ui.kernel3_checkBox.setCheckState(True);
        self.ui.sliceThickness5_checkBox.setCheckState(True);                
        logging.debug('Setting some checkboxes for testing... DONE')

        logging.debug('Running queue NORMAL callback...');
        self.queue_normal_callback();
        logging.debug('Running queue NORMAL callback... DONE');
        
        logging.debug('Current level of testing completed!');
        
    def testCallback(self):
        print('Test worked!');

    def select_cases_callback(self):
        logging.info('Select cases callback active')
        
        accepted_filetypes=['.ctd','.ptr','.ima','.txt']

        # File selection dialog
        if not self.test_cases:
            fname=QtGui.QFileDialog.getOpenFileName(self,'Open file','/home');
        else:
            fname=self.test_cases

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

        if not self.test_library:        
            dirname=QtGui.QFileDialog.getExistingDirectory(self,'Open Directory','/home');
        else:
            dirname=self.test_library

        if not dirname:
            return;
        else:
            dirname=str(dirname)

        pipeline_lib=ctbb_plib(dirname)
            
        self.ui.selectLibrary_edit.setText(dirname)
        self.current_library=pipeline_lib

        self.refresh_library_tab()

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

    def dispatch_ctbb_pipeline_daemon(self):
        logging.info('Launching pipeline daemon')
        command="python ctbb_pipeline_daemon.py %s" % self.current_library.path
        os.system("nohup %s >/dev/null 2>&1 &" % command);

    def keyPressEvent(self,e):
        if e.matches(QtGui.QKeySequence.Close) or e.matches(QtGui.QKeySequence.Quit):
            logging.info('User quit via keystroke')
            sys.exit()

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

    def refresh_library_tab(self):
        logging.info('Refreshing library tab')
        self.current_library.refresh_recon_list()
        with open(os.path.join(self.current_library.path,'recons.csv'),'r') as f:
            recon_list=f.read().splitlines();
            
        for i in range(len(recon_list)):
            recon_list[i]=recon_list[i].split(',')

        table_model=MyTableModel(recon_list)
        self.ui.library_tableView.setModel(table_model)

class MyTableModel(QtCore.QAbstractTableModel):
    header_labels=['File','Case ID','Dose','Kernel','Slice Thickness','Recon Path']
    
    def __init__(self, datain, parent=None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self,section,orientation,role=QtCore.Qt.DisplayRole):

        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.header_labels[section]
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def sort(self, Ncol, order):
        import operator
        self.emit(QtCore.SIGNAL("layouAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == QtCore.Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
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
        logfile=os.path.join(logdir,('%s_interface.log' % strftime('%y%m%d_%H%M%S')))

        if not os.path.isdir(logdir):
            os.mkdir(logdir);

        logging.basicConfig(format=('%(asctime)s %(message)s'),filename=logfile, level=logging.INFO)

    window = MyWindow()
    sys.exit(app.exec_())

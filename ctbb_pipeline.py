import sys
import os
import logging
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

        if (ext in accepted_filetypes):
            logging.info('File extension accepted')
            if ext is 'txt':
                with open(fname,'r') as f:
                    case_list=f.read()
            else:
                case_list=fname;
        else:
            #QtGui.QMessageBox.error('Unrecognized filetype.  Accepted filetypes are IMA, PTR, CTD, and TXT')
            self.error_dialog('Unrecognized filetype.  Accepted filetypes are IMA, PTR, CTD, and TXT')
            logging.error('User tried to load an unrecognized filetype:' + fname)
            return;

    def select_library_callback(self):
        print('Select library callback active');    

    def queue_normal_callback(self):
        print('Queue normal callback active');

    def queue_high_priority_callback(self):
        print('Queue high priority callback active');

    def keyPressEvent(self,e):
        if e.matches(QtGui.QKeySequence.Close) or e.matches(QtGui.QKeySequence.Quit):
            sys.exit('User quit via keystroke')
        else:
            print("No command for keystroke:" + chr(e.key()))

    def queue(self):
        print('Select cases callback active');

    def error_dialog(self,s):
        msg = QtGui.QMessageBox();
        msg.setIcon(QtGui.QMessageBox.Critical)
        msg.setInformativeText(s)
        msg.setWindowTitle('Error')
        msg.setStandardButtons(QtGui.QMessageBox.Close)
        msg.exec_()

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

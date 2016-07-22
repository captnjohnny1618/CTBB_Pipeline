import sys
import os
from PyQt4 import QtGui, uic

class MyWindow(QtGui.QMainWindow):

    ui=None;

    
    def __init__(self):
        super(MyWindow,self).__init__()
        self.ui=uic.loadUi('ctbb_pipeline.ui',self)
        self.show()

        # Connect Callbacks
        self.ui.selectCases_pushButton.clicked.connect(self.testCallback)

        print('GUI Initialization finished');

    def testCallback(self):
        print('Test worked!');
    

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())

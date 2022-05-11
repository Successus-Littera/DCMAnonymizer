import sys
import os
import traceback

from PyQt5.QtWidgets import QWidget, QMessageBox, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QGridLayout, QMainWindow, QStatusBar, QProgressBar, QApplication
from PyQt5.QtCore import pyqtSignal


from DCMReader import DCMGroup
from TreeWidget import TreeWidget
from EditForm import EditForm
from Anonymizer import Anonymizer

def Alert(msg):
    msgbox = QMessageBox()
    msgbox.setText(msg)
    msgbox.exec()


class SourcePathToolBar(QWidget):
    executeSearch = pyqtSignal(str)
    def __init__(self, parent):
        super(SourcePathToolBar, self).__init__(parent)
        self.__lastWorkingDirectory = os.path.join(os.path.expanduser('~'),'Desktop')
        self.__layout = QHBoxLayout(self)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__pathEdit = QLineEdit()

        self.__openDirectoryButton = QPushButton('Select Directory')
        self.__openDirectoryButton.clicked.connect(self.__openDirectoryDialog)
        self.__searchButton = QPushButton('Search')
        self.__searchButton.clicked.connect(self.__search)

        self.__layout.addWidget(QLabel('Source Directory (ROOT)'))
        self.__layout.addWidget(self.__pathEdit)
        self.__layout.addWidget(self.__openDirectoryButton)
        self.__layout.addWidget(self.__searchButton)

    def __openDirectoryDialog(self):
        dlg = QFileDialog()
        fn = dlg.getExistingDirectory(self, "Select Source Directory", self.__lastWorkingDirectory)
        if fn == "":
            return
        self.__lastWorkingDirectory = fn
        self.__pathEdit.setText(fn)

    def __search(self):
        if os.path.exists(self.__pathEdit.text()):
            self.executeSearch.emit(self.__pathEdit.text())
        else:
            Alert('Could not find path.')


class TargetPathToolBar(QWidget):
    executeAnonymize = pyqtSignal(str)
    def __init__(self, parent):
        super(TargetPathToolBar, self).__init__(parent)
        self.__lastWorkingDirectory = os.path.join(os.path.expanduser('~'), 'Desktop\\DCM_Anonymize_Result')
        self.__layout = QHBoxLayout(self)
        self.__layout.setContentsMargins(0, 0, 0, 0)

        self.__pathEdit = QLineEdit()
        self.__pathEdit.setText(self.__lastWorkingDirectory)
        self.__openDirectoryButton = QPushButton('Select Directory')
        self.__openDirectoryButton.clicked.connect(self.__openDirectoryDialog)
        self.__executeButton = QPushButton('Execute')
        self.__executeButton.clicked.connect(self.__execute)

        self.__layout.addWidget(QLabel('Target Directory (SAVE)'))
        self.__layout.addWidget(self.__pathEdit)
        self.__layout.addWidget(self.__openDirectoryButton)
        self.__layout.addWidget(self.__executeButton)

    def GetTargetPath(self):
        return self.__pathEdit.text()

    def __openDirectoryDialog(self):
        dlg = QFileDialog()
        fn = dlg.getExistingDirectory(self, "Select Target Directory", self.__lastWorkingDirectory)
        if fn == "":
            return
        self.__lastWorkingDirectory = fn
        self.__pathEdit.setText(fn)

    def __execute(self):
        self.executeAnonymize.emit(self.__pathEdit.text())


class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        sys.excepthook = self.except_hook
        self.__dpiScaleFactor = self.window().screen().logicalDotsPerInch() / 96
        self.__dcmGroup = DCMGroup()
        self.__dcmGroup.progressed.connect(self.__parsingProgressed)
        self.__dcmGroup.parsingFinished.connect(self.__taskFinished)

        self.__centralWidget = QWidget()
        self.__layout = QGridLayout(self.__centralWidget)
        self.setCentralWidget(self.__centralWidget)

        self.statusbar = QStatusBar()
        self.statusbar.showMessage('Ready')
        self.setStatusBar(self.statusbar)

        self.__statusProgressbar = QProgressBar()
        self.__statusProgressbar.setVisible(False)
        self.__statusProgressbar.setMaximum(100)
        self.statusbar.addPermanentWidget(self.__statusProgressbar)

        self.__treeWidget = TreeWidget(self, self.__dcmGroup)
        self.__editForm = EditForm(self, self.__dcmGroup)
        self.__pathToolBar = SourcePathToolBar(self)
        self.__pathToolBar.executeSearch.connect(lambda x: self.__statusProgressbar.setVisible(True))
        self.__pathToolBar.executeSearch.connect(self.__dcmGroup.SetRootDirectory)
        self.__pathToolBar.setMinimumSize(self.GetScaledSize(1200), self.GetScaledSize(40))

        self.__targetPathToolBar = TargetPathToolBar(self)
        self.__targetPathToolBar.executeAnonymize.connect(self.__executeAnonymize)

        self.__layout.addWidget(self.__pathToolBar, 0, 0, 1, 2)
        self.__layout.addWidget(self.__treeWidget, 1, 0, 1, 1)
        self.__layout.addWidget(self.__editForm, 1, 1, 1, 1)

        self.__layout.addWidget(self.__targetPathToolBar, 2, 0, 1, 2)

    def __parsingProgressed(self, progress, processed, length):
        self.__statusProgressbar.setValue(int(progress * 100))
        self.statusbar.showMessage(f'Searching DCM Files... {processed} / {length}')

    def __anonymizeProgressed(self, progress, processed, length):
        self.__statusProgressbar.setValue(int(progress * 100))
        self.statusbar.showMessage(f'Anonymize is in progress... {processed} / {length}')

    def __taskFinished(self):
        self.statusbar.showMessage('Ready')
        self.__statusProgressbar.setVisible(False)

    def GetScaledSize(self, val: int):
        return round(val * self.__dpiScaleFactor)

    def __executeAnonymize(self):
        self.__statusProgressbar.setValue(0)
        self.__statusProgressbar.setVisible(True)
        prefix, startNumber, numberOfDigits = self.__editForm.GetNamingRule()
        c = Anonymizer(self,
                       self.__dcmGroup,
                       self.__targetPathToolBar.GetTargetPath(),
                       self.__editForm.GetDistinctionRule(),
                       prefix, startNumber, numberOfDigits,
                       self.__editForm.GetAnonymizeOption())
        c.progressed.connect(self.__anonymizeProgressed)
        c.finished.connect(self.__taskFinished)
        c.start()

    def except_hook(self, cls, exception, tb):
        sys.__excepthook__(cls, exception, tb)
        tb_str = "".join(traceback.format_tb(tb))
        msg = f"Unhandled exception thrown.\n\n{exception}\n\n{tb_str}"
        print(msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Main()
    window.show()

    sys.exit(app.exec_())
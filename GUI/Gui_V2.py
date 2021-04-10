from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
import mainfile


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        MainWindow.setMinimumSize(QtCore.QSize(640, 480))
        MainWindow.setMaximumSize(QtCore.QSize(640, 480))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 621, 421))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_Overview = QtWidgets.QWidget()
        self.tab_Overview.setObjectName("tab_Overview")
        self.pushButton_Stop = QtWidgets.QPushButton(self.tab_Overview)
        self.pushButton_Stop.setGeometry(QtCore.QRect(540, 40, 75, 23))
        self.pushButton_Stop.setObjectName("pushButton_Stop")
        self.graphicsView_Mode2 = QtWidgets.QGraphicsView(self.tab_Overview)
        self.graphicsView_Mode2.setGeometry(QtCore.QRect(280, 0, 256, 192))
        self.graphicsView_Mode2.setObjectName("graphicsView_Mode2")
        self.Line_Edit_Path = QtWidgets.QLineEdit(self.tab_Overview)
        self.Line_Edit_Path.setGeometry(QtCore.QRect(280, 370, 171, 20))
        self.Line_Edit_Path.setObjectName("Line_Edit_Path")
        self.graphicsView_Mode1 = QtWidgets.QGraphicsView(self.tab_Overview)
        self.graphicsView_Mode1.setGeometry(QtCore.QRect(20, 0, 256, 192))
        self.graphicsView_Mode1.setObjectName("graphicsView_Mode1")
        self.graphicsView_Mode3 = QtWidgets.QGraphicsView(self.tab_Overview)
        self.graphicsView_Mode3.setGeometry(QtCore.QRect(20, 200, 256, 192))
        self.graphicsView_Mode3.setObjectName("graphicsView_Mode3")
        self.Button_Start = QtWidgets.QPushButton(self.tab_Overview)
        self.Button_Start.setGeometry(QtCore.QRect(540, 10, 75, 23))
        self.Button_Start.setObjectName("Button_Start")
        self.textBrowser = QtWidgets.QTextBrowser(self.tab_Overview)
        self.textBrowser.setGeometry(QtCore.QRect(280, 200, 256, 161))
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton_Browse = QtWidgets.QPushButton(self.tab_Overview)
        self.pushButton_Browse.setGeometry(QtCore.QRect(460, 370, 75, 23))
        self.pushButton_Browse.setObjectName("pushButton_Browse")
        self.tabWidget.addTab(self.tab_Overview, "")
        self.tab_Settings = QtWidgets.QWidget()
        self.tab_Settings.setObjectName("tab_Settings")
        self.Radio_RunningMode = QtWidgets.QRadioButton(self.tab_Settings)
        self.Radio_RunningMode.setGeometry(QtCore.QRect(100, 10, 101, 17))
        self.Radio_RunningMode.setObjectName("Radio_RunningMode")
        self.label1 = QtWidgets.QLabel(self.tab_Settings)
        self.label1.setGeometry(QtCore.QRect(10, 10, 71, 16))
        self.label1.setObjectName("label1")
        self.tabWidget.addTab(self.tab_Settings, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

# Custom_________________________________________________________________________________
        self.Radio_RunningMode.clicked.connect(self.Radio_Button_Set)

        self.Main_Thread = mainfile.MainFunction_Thread()
        self.Main_Thread.StrSignal.connect(self.printConsole)
        self.Button_Start.clicked.connect(self.System_Start)

        self.pushButton_Browse.clicked.connect(self.Browse_path)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_Stop.setText(_translate("MainWindow", "Stop"))
        self.Button_Start.setText(_translate("MainWindow", "Start"))
        self.pushButton_Browse.setText(_translate("MainWindow", "Browse"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_Overview), _translate("MainWindow", "Overview"))
        self.Radio_RunningMode.setText(_translate("MainWindow", "Online"))
        self.label1.setText(_translate("MainWindow", "Running Mode"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_Settings), _translate("MainWindow", "Settings"))

# Function_______________________
    def System_Start(self):
        if self.Radio_RunningMode.isChecked() == True:
            self.Main_Thread.RunningState = 'Offline'
        else:
            self.Main_Thread.RunningState = 'Online'
        self.Main_Thread.path = self.Line_Edit_Path.text()
        self.Main_Thread.start()

    def Browse_path(self):
        dialog = QtWidgets.QFileDialog()                                # Open Windows explorer
        path = dialog.getExistingDirectory(self.centralwidget, "Select Directory")
        self.Line_Edit_Path.setText(path)

    def Radio_Button_Set(self):
        if self.Radio_RunningMode.isChecked() == True:
            self.Radio_RunningMode.setText('Offline')
        else:
            self.Radio_RunningMode.setText('Online')

    def printConsole(self, result):
        self.textBrowser.append(result)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

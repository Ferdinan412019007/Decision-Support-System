from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication,QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog , QLabel, QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont
import sys
import pandas as pd
import minizinc

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.title = "Scheduling"
        self.top = 200
        self.left = 500
        self.width = 550
        self.height = 350
        self.index = 0

        self.InitWindow()
    
    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()

        self.setLayout(vbox)

        self.lblInfo = QLabel("Masukan Jam Kegiatan (Excel) :")
        self.lblInfo.setAlignment(QtCore.Qt.AlignLeft)
        vbox.addWidget(self.lblInfo)

        self.fileName =  QTextEdit()
        self.fileName.setReadOnly(True)
        self.fileName.setMaximumHeight(30)
        self.fileName.setAlignment(QtCore.Qt.AlignLeft)
        hbox1.addWidget(self.fileName)

        self.btnUpload = QPushButton("Browse")
        self.btnUpload.clicked.connect(self.getData)

        hbox1.addWidget(self.btnUpload)
        vbox.addLayout(hbox1)

        self.lblInfo2 = QLabel("Masukan Jumlah Schedule yang Diinginkan :")
        self.lblInfo2.setAlignment(QtCore.Qt.AlignCenter)
        hbox2.addWidget(self.lblInfo2)

        self.total =  QLineEdit()
        self.total.setMaximumHeight(30)
        self.total.setValidator(QtGui.QIntValidator())
        self.total.setMaxLength(2)
        hbox2.addWidget(self.total)
        vbox.addLayout(hbox2)

        self.resLabel = QLabel('Hasil Schedule')
        vbox.addWidget(self.resLabel)

        self.tbl = QTableWidget()
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        vbox.addWidget(self.tbl)

        self.btnPrev = QPushButton("Previous")
        self.btnPrev.clicked.connect(self.prev)
        
        self.btnNext = QPushButton("Next")
        self.btnNext.clicked.connect(self.next)
        
        self.btnPrev.setEnabled(False)
        self.btnNext.setEnabled(False)

        hbox3.addWidget(self.btnPrev)
        hbox3.addWidget(self.btnNext)
        
        vbox.addLayout(hbox3)

        self.btnConfirm = QPushButton("Confirm")
        self.btnConfirm.clicked.connect(self.showSchedule)
        
        self.btnExit = QPushButton("Exit")
        self.btnExit.clicked.connect(self.close)
        
        hbox4.addWidget(self.btnConfirm)
        hbox4.addWidget(self.btnExit)

        vbox.addLayout(hbox4)

        self.show()
    
    def getData(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file','', "Excel (*.xls *.xlsx)")
        self.fileName.setText(fname[0])
        # apa yang telah terjadi setelah upload data

    def showSchedule(self):
        self.btnPrev.setEnabled(False)
        self.btnNext.setEnabled(False)
        
        getSchedule(self.fileName.toPlainText(), int(self.total.text()), self)
        
        self.tbl.setRowCount(len(self.works)) 
        self.tbl.setColumnCount(len(self.days))
        self.tbl.setHorizontalHeaderLabels(self.days)
        self.tbl.setVerticalHeaderLabels(self.works)

        self.populateTable()
        if(int(self.total.text())>1):
            self.btnNext.setEnabled(True)

    def populateTable(self):
        for i in range(len(self.data[self.index])):
            for j in range(len(self.data[self.index][i])):
                self.tbl.setItem(i,j, QTableWidgetItem(
                    str(self.data[self.index][i][j])))

    def next(self):
        self.btnPrev.setEnabled(True)
        self.index = self.index + 1
        if(self.index == int(self.total.text())-1):
            self.btnNext.setEnabled(False)
        self.populateTable()

    def prev(self):
        self.btnNext.setEnabled(True)
        self.index = self.index - 1
        if(self.index == 0):
            self.btnPrev.setEnabled(False)
        self.populateTable()

def getSchedule(filename, total, self):
    df = pd.read_excel(filename, engine='openpyxl', dtype=object, header=None)
    
    days = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]

    self.days = days

    total_task = len(df)

    works = df.iloc[1:total_task, 0] 
    works = works.tolist()

    self.works = works

    work_times = df.iloc[1:total_task, 1]
    work_times = work_times.values.tolist()

    minimum = df.iloc[1:total_task, 2]
    minimum = minimum.values.tolist()

    maximum = df.iloc[1:total_task, 3]
    maximum = maximum.values.tolist()

    weekend = df.iloc[1:total_task, 4]
    weekend = weekend.values.tolist()

    model = minizinc.Model("./schedule.mzn")

    gecode = minizinc.Solver.lookup("gecode")
    inst = minizinc.Instance(gecode, model)
    inst["total_task"] = total_task-1
    inst["task_time"] = work_times
    inst["min"] = minimum
    inst["max"] = maximum
    inst["weekend"] = weekend

    result = inst.solve(nr_solutions = total, all_solutions=False)

    data = []

    for i in range(total):
        data.append(result.solution[i].schedule)
        self.data = data

App = QApplication(sys.argv)
#App.setStyleSheet("QLabel{font-size: 18pt; font-weight:800;} QPushButton{font-size: 12pt; font-weight:500; border: 2px solid #6D8B74; border-radius: 5px; background-color: #BDE6F1!important;}")
window = Window()
sys.exit(App.exec())

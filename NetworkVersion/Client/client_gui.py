# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(850, 671)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 70, 54, 12))
        self.label.setObjectName("label")
        self.pc1 = QtWidgets.QLabel(self.centralwidget)
        self.pc1.setGeometry(QtCore.QRect(10, 90, 111, 151))
        self.pc1.setText("")
        self.pc1.setPixmap(QtGui.QPixmap("Pic/53.GIF"))
        self.pc1.setObjectName("pc1")
        self.pc2 = QtWidgets.QLabel(self.centralwidget)
        self.pc2.setGeometry(QtCore.QRect(140, 90, 111, 151))
        self.pc2.setText("")
        self.pc2.setPixmap(QtGui.QPixmap("Pic/53.GIF"))
        self.pc2.setObjectName("pc2")
        self.pc3 = QtWidgets.QLabel(self.centralwidget)
        self.pc3.setGeometry(QtCore.QRect(270, 90, 111, 151))
        self.pc3.setText("")
        self.pc3.setPixmap(QtGui.QPixmap("Pic/53.GIF"))
        self.pc3.setObjectName("pc3")
        self.pc4 = QtWidgets.QLabel(self.centralwidget)
        self.pc4.setGeometry(QtCore.QRect(400, 90, 111, 151))
        self.pc4.setText("")
        self.pc4.setPixmap(QtGui.QPixmap("Pic/53.GIF"))
        self.pc4.setObjectName("pc4")
        self.pc5 = QtWidgets.QLabel(self.centralwidget)
        self.pc5.setGeometry(QtCore.QRect(530, 90, 111, 151))
        self.pc5.setText("")
        self.pc5.setPixmap(QtGui.QPixmap("Pic/53.GIF"))
        self.pc5.setObjectName("pc5")
        self.public_cards = [self.pc1, self.pc2, self.pc3, self.pc4, self.pc5]
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 290, 711, 331))
        self.tableWidget.setAutoFillBackground(False)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setHorizontalHeaderLabels(['昵称', 'id', '状态', '下注', '财富', '牌1', '牌2', '最大牌型'])

        self.label_bb = QtWidgets.QLabel(self.centralwidget)
        self.label_bb.setGeometry(QtCore.QRect(20, 30, 71, 16))
        self.label_bb.setObjectName("label_bb")
        self.label_leftplayers = QtWidgets.QLabel(self.centralwidget)
        self.label_leftplayers.setGeometry(QtCore.QRect(140, 30, 101, 16))
        self.label_leftplayers.setObjectName("label_leftplayers")
        self.label_pot = QtWidgets.QLabel(self.centralwidget)
        self.label_pot.setGeometry(QtCore.QRect(280, 30, 101, 16))
        self.label_pot.setObjectName("label_pot")
        self.label_maxbet = QtWidgets.QLabel(self.centralwidget)
        self.label_maxbet.setGeometry(QtCore.QRect(390, 30, 101, 16))
        self.label_maxbet.setObjectName("label_maxbet")

        self.label_timer = QtWidgets.QLabel(self.centralwidget)
        self.label_timer.setStyleSheet("font:30pt '楷体';color: rgb(255, 255, 255);")
        self.label_timer.setAlignment(QtCore.Qt.AlignCenter)
        self.label_timer.setGeometry(QtCore.QRect(730, 20, 40, 50))

        self.widget_action = QtWidgets.QWidget(self.centralwidget)
        self.widget_action.setGeometry(QtCore.QRect(660, 90, 191, 141))
        self.widget_action.setObjectName("widget_action")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.widget_action)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 40, 171, 91))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_fold = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_fold.setObjectName("pushButton_fold")
        self.verticalLayout.addWidget(self.pushButton_fold)
        self.pushButton_checkcall = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_checkcall.setObjectName("pushButton_checkcall")
        self.verticalLayout.addWidget(self.pushButton_checkcall)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit_raise = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_raise.setObjectName("lineEdit_raise")
        self.horizontalLayout.addWidget(self.lineEdit_raise)
        self.pushButton_raise = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_raise.setObjectName("pushButton_raise")
        self.horizontalLayout.addWidget(self.pushButton_raise)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtWidgets.QLabel(self.widget_action)
        self.label_2.setGeometry(QtCore.QRect(70, 10, 48, 20))
        self.label_2.setObjectName("label_2")

        font = QtGui.QFont()
        font.setPointSize(20)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 850, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def update_table(self, row_num):
        width = 50
        height = 60
        self.tableWidget.setRowCount(row_num)
        self.tableWidget.setIconSize(QtCore.QSize(width, height))
        for i in range(5, 7):  # 让列宽和图片相同
            self.tableWidget.setColumnWidth(i, width)
        for i in range(row_num):  # 让行高和图片相同
            self.tableWidget.setRowHeight(i, height)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "德州扑克好友版"))
        self.label.setText(_translate("MainWindow", "公共牌"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setSortingEnabled(__sortingEnabled)
        self.label_bb.setText(_translate("MainWindow", "大盲位id:"))
        self.label_leftplayers.setText(_translate("MainWindow", "剩余玩家数:"))
        self.label_pot.setText(_translate("MainWindow", "底池:"))
        self.label_maxbet.setText(_translate("MainWindow", "当前最大下注:"))
        self.pushButton_fold.setText(_translate("MainWindow", "弃牌"))
        self.pushButton_checkcall.setText(_translate("MainWindow", "跟注/Check"))
        self.pushButton_raise.setText(_translate("MainWindow", "加注"))
        self.label_2.setText(_translate("MainWindow", "采取动作"))

        self.widget_action.setVisible(False)


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":
    #固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    #初始化
    myWin = MyMainForm()
    palette1 = QtGui.QPalette()
    palette1.setColor(QtGui.QPalette.Background, QtGui.QColor(192, 253, 123))  # 设置背景颜色
    # palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('../../../Document/images/17_big.jpg')))   # 设置背景图片
    myWin.setPalette(palette1)
    #将窗口控件显示在屏幕上
    myWin.show()
    #程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())
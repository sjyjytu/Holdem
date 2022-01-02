import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.flag = False
        self.step = 30

        self.lab = QLabel(self)
        self.lab.setStyleSheet("font:200pt '楷体';color: rgb(255, 255, 255);")
        self.lab.setText(str(self.step))  # 设定起始数字
        self.lab.setAlignment(Qt.AlignCenter)
        self.lab.move(200, 150)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_func)

        self.timer_2 = QTimer(self)
        self.timer_2.timeout.connect(self.interpurt_even)
        self.timer_2.start(100)

        self.resize(700, 700)
        self.setWindowTitle('倒计时')
        self.show()

    #定时器2
    def interpurt_even(self):
        if self.step < 6:
            self.lab.setStyleSheet("font:200pt '楷体';color: rgb(255, 0, 0);")
        else:
            self.lab.setStyleSheet("font:200pt '楷体';color: rgb(255, 255, 255);")

    #定时器1
    def update_func(self):
        if self.step > 0:
            self.step -= 1

        else:
            self.timer.stop()
        self.lab.setText(str(self.step))

    # 检测键盘按键
    def keyPressEvent(self, event):

        print("按下：" + str(event.key()))

        if(event.key() == 16777220):
            self.flag = False
            self.timer.stop()
            self.step = 30
            self.lab.setText(str(self.step))

        if(event.key() == Qt.Key_Space):
            self.flag= bool(1-self.flag)
            if self.flag == True:
                self.timer.start(1000)
            else:
                self.timer.stop()

        #按下加号
        if(event.key() == 61):
            self.flag = False
            self.timer.stop()
            self.step+=10
            self.lab.setText(str(self.step))

        #按下减号
        if(event.key() == 45):
            self.flag = False
            self.timer.stop()
            self.step -= 10
            self.lab.setText(str(self.step))
    #窗口居中
    def center(self):
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(newLeft,newTop)

    #设置背景颜色
    def paintEvent(self, event):
        painter = QPainter(self)
        #todo 1 设置背景颜色
        painter.setBrush(QColor(0,0,0))
        painter.drawRect(self.rect())


if __name__ == '__main__':
    # 创建应用程序和对象
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

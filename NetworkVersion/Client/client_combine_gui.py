# -*- coding: utf-8 -*-
import sys

print(sys.path[0])
sys.path.append(sys.path[0] + '/../..')

# import pygame
import socket  # 导入 socket 模块

from NetworkVersion.Client.protocal import Protocol

from NetworkVersion.utils import *

g_role = None  # 玩家操作的角色

g_players = {}  # 所有玩家

g_client = socket.socket()  # 创建 socket 对象

env = LocalEnvInfo()

TIMEOUT = 90


class Role:
    def __init__(self, name):
        self.id = -1
        self.name = name


class PlayerPublicInfo:
    def __init__(self, name):
        self.name = name
        self.possess = 0
        self.cur_bet = 0
        self.current_state = Player_State.NORMAL
        self.card = []  # TODO: 记得每局结束后要清理
        self.best_card_info = ""


def register():
    """
    告诉服务端有新玩家加入
    """
    # 构建数据包
    p = Protocol()
    p.add_str("register")
    p.add_str(g_role.name)
    data = p.get_pck_has_head()
    # 发送数据包
    g_client.sendall(data)


def send_get_ready():
    """
    告诉服务端玩家准备好了
    """
    # 构建数据包
    p = Protocol()
    p.add_str("ready")
    data = p.get_pck_has_head()
    # 发送数据包
    g_client.sendall(data)


def send_action(action_type, money):
    """
    告诉服务端玩家准备好了
    """
    # 构建数据包
    p = Protocol()
    p.add_str("action")
    p.add_int32(action_type)
    p.add_int32(money)
    data = p.get_pck_has_head()
    # 发送数据包
    g_client.sendall(data)
    print("id: %d sent action" % g_role.id)


def send_mysterious_msg(msg):
    """
        操作服务器的命令，为了方便玩耍
    """
    exit_after_send = False
    if msg == 'clear':
        exit_after_send = True
    # 构建数据包
    secret_code = '#ilhth '
    msg = secret_code + msg
    p = Protocol()
    p.add_str(msg)
    data = p.get_pck_has_head()
    # 发送数据包
    g_client.sendall(data)

    if exit_after_send:
        exit(0)


from NetworkVersion.Client.client_gui import Ui_MainWindow
from NetworkVersion.Client.login_gui import Ui_Login_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDockWidget, QListWidget
from PyQt5.QtGui import *


class Login_window(QtWidgets.QMainWindow, Ui_Login_MainWindow):
    # __init__: 析构函数，也就是类被创建后就会预先加载的项目。
    # 马上运行，这个方法可以用来对你的对象做一些你希望的初始化。
    def __init__(self):
        # 这里需要重载一下Login_window，同时也包含了QtWidgets.QMainWindow的预加载项。
        super(Login_window, self).__init__()
        self.setupUi(self)

        # 将点击事件与槽函数进行连接
        self.pushButton.clicked.connect(self.login)
        self.is_connected = False

    def login(self):
        if not self.is_connected:
            ip = self.lineEdit.text()
            port = self.lineEdit_2.text()
            name = self.lineEdit_3.text()
            if name != '':
                # 1打开新窗口
                print('connecting...')
                myWin.init_game(ip, int(port), name)
                self.is_connected = True
                self.pushButton.setText('开始游戏')
            else:
                reply = QMessageBox.warning(self, "警告", "昵称不能为空！")
        else:
            # 准备
            send_get_ready()
            self.pushButton.setText('已准备，等待其他玩家开始游戏...')
            self.pushButton.setEnabled(False)


class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, login_win=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)

        self.msg_handler = MSG_Handler()
        self.pushButton_fold.clicked.connect(self.fold)
        self.pushButton_checkcall.clicked.connect(self.checkcall)
        self.pushButton_raise.clicked.connect(self.raisemoney)

        self.login_win = login_win

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timeout = TIMEOUT

    def update_timer(self):
        if self.timeout > 0:
            self.timeout -= 1
        else:
            self.timer.stop()
        self.label_timer.setText(str(self.timeout))

    def fold(self):
        money = 0
        send_action(1, money)
        self.executed_action()

    def checkcall(self):
        money = 0
        send_action(2, money)
        self.executed_action()

    def raisemoney(self):
        money = self.lineEdit_raise.text()
        if not money.isdigit() or int(money) < 0:
            reply = QMessageBox.warning(self, "警告", "请输入正确的加注金额！")
        else:
            send_action(3, int(money))
            self.executed_action()

    def ask_for_action(self):
        self.timeout = TIMEOUT
        self.timer.start(1000)
        self.label_timer.setText(str(self.timeout))
        self.label_timer.setVisible(True)
        self.widget_action.setVisible(True)

    def executed_action(self):
        self.timer.stop()
        self.label_timer.setVisible(False)
        self.widget_action.setVisible(False)

    def init_game(self, ip, port, name):
        global g_role, g_players
        ADDRESS = (ip, port)
        g_role = Role(name)

        # 与服务器建立连接
        g_client.connect(ADDRESS)
        # 启动消息处理线程
        self.msg_handler.start()
        # 线程自定义信号连接的槽函数
        self.msg_handler.trigger.connect(self.pck_handler)

        # 告诉服务端有新玩家
        register()

    def pck_handler(self, pck):
        global g_players, g_role, env
        p = Protocol(pck)
        pck_type = p.get_str()

        if pck_type == 'game_start':
            # print('*' * 10 + 'Game Start!' + '*' * 10)
            for k in g_players.keys():
                g_players[k].card = []
                g_players[k].best_card_info = ""
        elif pck_type == 'init_players':  # 玩家移动的数据包
            player_num = p.get_int32()
            g_role.id = p.get_int32()
            g_players = {i: PlayerPublicInfo(p.get_str()) for i in range(player_num)}

            self.login_win.close()
            self.update_table(player_num)
            self.show()

        elif pck_type == 'public_info':  # 新玩家数据包
            player_num = p.get_int32()
            for i in range(player_num):
                pid = p.get_int32()
                possess = p.get_int32()
                cur_bet = p.get_int32()
                current_state_value = p.get_int32()
                g_players[pid].possess = possess
                g_players[pid].cur_bet = cur_bet
                g_players[pid].current_state = Player_State(current_state_value)
            self.update_info()

        elif pck_type == 'private_info':
            str_cards = p.get_str()
            g_players[g_role.id].card = str_cards.split(' ')
            self.update_info()

        elif pck_type == 'env_info':
            str_public_cards = p.get_str()
            if str_public_cards == '':
                public_cards = []
            else:
                public_cards = str_public_cards.split(' ')
            env.update(public_cards, p.get_int32(), p.get_int32(), p.get_int32(), p.get_int32())
            self.update_info()

        elif pck_type == 'ask_for_action':
            acting_pid = p.get_int32()
            if acting_pid == g_role.id:
                # 我自己
                self.ask_for_action()
            else:
                self.highlight_player(acting_pid)

        elif pck_type == 'open_card':
            num = p.get_int32()
            for i in range(num):
                pid = p.get_int32()
                str_cards = p.get_str()
                g_players[pid].card = str_cards.split(' ')
                g_players[pid].best_card_info = p.get_str()
            self.update_info()

        elif pck_type == 'game_over':
            if g_players[g_role.id].current_state != Player_State.OUT:
                reply = QMessageBox.warning(self, "请准备", "游戏结束！请按OK准备下一局")
                send_get_ready()

        elif pck_type == 'logout':  # 玩家掉线
            pass

    def card2card_pic_idx(self, card):
        suit2num = {'♠': 1, '♥': 2, '♣': 3, '◆': 4}
        suit = suit2num[card[0]]
        rank = card[1:]
        if rank == 'A':
            rank = 1
        elif rank == 'J':
            rank = 11
        elif rank == 'Q':
            rank = 12
        elif rank == 'K':
            rank = 13
        else:
            rank = int(rank)
        card_id = (rank - 1) * 4 + suit
        return card_id

    def update_info(self):
        self.label_bb.setText(f"大盲位id:{env.BB_id}")
        self.label_leftplayers.setText(f"剩余玩家数:{env.current_left_player_num}")
        self.label_pot.setText(f"底池:{env.pool_possess}")
        self.label_maxbet.setText(f"当前最大下注:{env.current_max_bet}")

        # 公共牌
        for i, card in enumerate(env.public_cards):
            card_id = self.card2card_pic_idx(card)
            self.public_cards[i].setPixmap(QtGui.QPixmap(f"Pic/{card_id}.GIF"))
        for i in range(len(env.public_cards), 5):
            self.public_cards[i].setPixmap(QtGui.QPixmap("Pic/53.GIF"))

        # 玩家信息
        for i, pid in enumerate(g_players.keys()):
            gp = g_players[pid]
            name = gp.name
            if pid == g_role.id:
                # 自己
                item = QtWidgets.QTableWidgetItem(chinglish_align(name, 9))
                item.setForeground(QBrush(QColor(255, 0, 0)))
                self.tableWidget.setItem(i, 0, item)
            else:
                item = QtWidgets.QTableWidgetItem(chinglish_align(name, 9))
                self.tableWidget.setItem(i, 0, item)

            item = QtWidgets.QTableWidgetItem(str(pid))
            self.tableWidget.setItem(i, 1, item)
            item = QtWidgets.QTableWidgetItem(gp.current_state.name)
            self.tableWidget.setItem(i, 2, item)
            item = QtWidgets.QTableWidgetItem(str(gp.cur_bet))
            self.tableWidget.setItem(i, 3, item)
            item = QtWidgets.QTableWidgetItem(str(gp.possess))
            self.tableWidget.setItem(i, 4, item)
            item = QtWidgets.QTableWidgetItem(gp.best_card_info)
            self.tableWidget.setItem(i, 7, item)

            for j in range(2):
                if j < len(gp.card):
                    card_id = self.card2card_pic_idx(gp.card[j])
                else:
                    card_id = 53
                item = QtWidgets.QTableWidgetItem()
                icon = QtGui.QIcon(f'Pic/{card_id}.GIF')
                item.setIcon(QtGui.QIcon(icon))
                self.tableWidget.setItem(i, 5 + j, item)

    def highlight_player(self, playerid):
        for i, pid in enumerate(g_players.keys()):
            if pid == playerid:
                name = g_players[pid].name
                item = QtWidgets.QTableWidgetItem(chinglish_align(name, 9))
                # item.setForeground(QBrush(QColor(0, 0, 255)))
                item.setBackground(QBrush(QColor(0, 255, 255)))
                self.tableWidget.setItem(i, 0, item)

    def ready(self):
        pass


class MSG_Handler(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    trigger = pyqtSignal(bytes)

    def __int__(self):
        # 初始化函数
        super(MSG_Handler, self).__init__()

    def run(self):
        """
            处理服务端返回的消息
            """
        while True:
            bytes = g_client.recv(1024)
            # 以包长度切割封包
            while True:
                # 读取包长度
                length_pck = int.from_bytes(bytes[:4], byteorder='little')
                # 截取封包
                pck = bytes[4:4 + length_pck]
                # 删除已经读取的字节
                bytes = bytes[4 + length_pck:]
                # 把封包交给处理函数
                self.trigger.emit(pck)
                # 如果bytes没数据了，就跳出循环
                if len(bytes) == 0:
                    break


if __name__ == "__main__":
    #固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    #初始化
    login_window = Login_window()
    myWin = MyMainForm(login_win=login_window)
    palette1 = QtGui.QPalette()
    palette1.setColor(QtGui.QPalette.Background, QtGui.QColor(192, 253, 123))  # 设置背景颜色
    # palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('../../../Document/images/17_big.jpg')))   # 设置背景图片
    myWin.setPalette(palette1)
    #将窗口控件显示在屏幕上
    login_window.show()
    #程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())
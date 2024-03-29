import sys

print(sys.path[0])
sys.path.append(sys.path[0] + '/../..')

import os
from threading import Thread, Event

# import pygame
import socket  # 导入 socket 模块

from NetworkVersion.Client.protocal import Protocol

from NetworkVersion.utils import *

g_role = None  # 玩家操作的角色

g_players = {}  # 所有玩家

g_client = socket.socket()  # 创建 socket 对象

env = LocalEnvInfo()

ask_for_instr = Event()


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


def print_info(clear=False):
    if clear:
        os.system("cls")  # 如果你用的是mac，把这行改为os.system("clear")
    # TODO 打印玩家信息，环境信息。每次收到server的刷新都重新调用一下
    # 应该在主线程（显示线程中）调用，但是有个问题就是消息处理线程在索要动作的时候会被input阻塞
    print('大盲位id: ', env.BB_id, ' 剩余玩家数: ', env.current_left_player_num,
          ' 底池: ', env.pool_possess, ' 当前最大下注: ', env.current_max_bet)
    print('公共牌: ')
    print_card_small(env.public_cards)

    print('|', chinglish_align('name', 9), ' |', 'id'.center(3), '|', 'state'.center(6),
          '|', 'bet'.center(8), '|', 'possess'.center(8), '|', 'card'.center(10))
    for pid in g_players.keys():
        gp = g_players[pid]
        name = gp.name
        my_self_token = '*|' if pid == g_role.id else ' |'
        print('|', chinglish_align(name, 9), my_self_token, str(pid).center(3), '|', gp.current_state.name.center(6),
              '|', str(gp.cur_bet).center(8), '|', str(gp.possess).center(8), '|', str(gp.card).center(10),
              '|', gp.best_card_info)


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


def pck_handler(pck):
    global g_players, g_role, env
    p = Protocol(pck)
    pck_type = p.get_str()

    if pck_type == 'game_start':
        print('*' * 10 + 'Game Start!' + '*' * 10)
        for k in g_players.keys():
            g_players[k].card = []
            g_players[k].best_card_info = ""
    elif pck_type == 'init_players':  # 玩家移动的数据包
        player_num = p.get_int32()
        g_role.id = p.get_int32()
        g_players = {i: PlayerPublicInfo(p.get_str()) for i in range(player_num)}

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
        print_info(True)

    elif pck_type == 'private_info':
        str_cards = p.get_str()
        g_players[g_role.id].card = str_cards.split(' ')
        print_info(True)

    elif pck_type == 'env_info':
        str_public_cards = p.get_str()
        if str_public_cards == '':
            public_cards = []
        else:
            public_cards = str_public_cards.split(' ')
        env.update(public_cards, p.get_int32(), p.get_int32(), p.get_int32(), p.get_int32())
        print_info(True)

    elif pck_type == 'ask_for_action':
        acting_pid = p.get_int32()
        if acting_pid == g_role.id:
            # 我自己
            a = input('玩家请采取动作（1弃牌，2check或call，3加注 加注金额）: ')
            a = a.strip(' ').split(' ')
            money = 0
            if len(a) > 1 and a[1].isdigit():
                money = int(a[1])
            while a[0] not in ['1', '2', '3'] or money < 0:
                print('输入不合法！')
                a = input('玩家请采取动作（1弃牌，2check或call，3加注 加注金额）: ')
                a = a.strip(' ').split(' ')
                money = 0
                if len(a) > 1 and a[1].isdigit():
                    money = int(a[1])
            send_action(int(a[0]), money)
        else:
            # 别的玩家在采取动作
            print("正在等待玩家 %s 下注..." % g_players[acting_pid].name)

    elif pck_type == 'open_card':
        num = p.get_int32()
        for i in range(num):
            pid = p.get_int32()
            str_cards = p.get_str()
            g_players[pid].card = str_cards.split(' ')
            g_players[pid].best_card_info = p.get_str()
        print_info(True)

    elif pck_type == 'game_over':
        print('*' * 10 + 'Game Over!' + '*' * 10)
        ask_for_instr.set()

    elif pck_type == 'logout':  # 玩家掉线
        # name = p.get_str()
        # for r in g_other_player:
        #     if r.name == name:
        #         g_other_player.remove(r)
        #         break
        # 按理来说 只有在游戏没开始阶段离开会有影响，游戏中别人跑了关我屁事
        pass


def msg_handler():
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
            pck_handler(pck)
            # 如果bytes没数据了，就跳出循环
            if len(bytes) == 0:
                break


def init_game():
    """
    初始化游戏
    """
    global g_role, g_players
    name = input('输入你的昵称：')[:9]
    g_role = Role(name)

    # 与服务器建立连接
    g_client.connect(ADDRESS)
    # 开始接受服务端消息
    thead = Thread(target=msg_handler)
    thead.setDaemon(True)
    thead.start()
    # 告诉服务端有新玩家
    register()


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


def main_loop():
    """
    游戏主循环
    """
    while True:
        # 游戏没开始，输入命令来准备、退出之类的
        instr = input('输入命令（r准备，q退出）：')
        while instr not in ['q', 'r']:
            if instr.startswith('code:'):
                print('正在发送神秘命令...')
                send_mysterious_msg(instr[5:])
            else:
                print('命令不正确！')
            instr = input('输入命令（r准备，q退出）：')
        if instr == 'q':
            sys.exit()
        elif instr == 'r':
            # 准备开始游戏
            ask_for_instr.clear()
            send_get_ready()

        # 游戏正在运行中，把控制权转移给另一个线程
        print('等待其他玩家准备...')
        ask_for_instr.wait()  # 等待set为止，也就是在游戏结束的时候set
        
        
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=23456, help='端口号')
    args = parser.parse_args()
    port = args.port
    # ADDRESS = ('1.15.135.219', port)  # 如果服务端在本机，请使用('127.0.0.1', port)
    ADDRESS = ('192.168.1.112', port)
    ADDRESS = ('127.0.0.1', port)
    # 初始化
    init_game()
    # 游戏循环
    main_loop()

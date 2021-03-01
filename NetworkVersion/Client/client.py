import random
import sys
import time
from random import randint
from threading import Thread

import pygame
import socket  # 导入 socket 模块

from NetworkVersion.Client.protocal import Protocol

from NetworkVersion.utils import *

ADDRESS = ('127.0.0.1', 8712)  # ('foxyball.cn', 8712)  # 如果服务端在本机，请使用('127.0.0.1', 8712)

# WIDTH, HEIGHT = 640, 480  # 窗口大小
#
# g_font = None
#
# g_screen = None  # 窗口的surface
#
# g_sur_role = None  # 人物的role

g_role = None  # 玩家操作的角色

g_players = {}  # 所有玩家

g_client = socket.socket()  # 创建 socket 对象

env = LocalEnvInfo()


class Role:
    def __init__(self, name):
        self.id = -1
        self.name = name
        self.card = []  # TODO: 记得每局结束后要清理


class PlayerPublicInfo:
    def __init__(self):
        self.possess = 0
        self.cur_bet = 0
        self.current_state = Player_State.NORMAL


def send_role_move():
    """
    发送角色的坐标给服务端
    """
    # 构建数据包
    p = Protocol()
    p.add_str("move")
    p.add_int32(g_player.x)
    p.add_int32(g_player.y)
    data = p.get_pck_has_head()
    # 发送数据包
    g_client.sendall(data)


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
    p.add_int32(g_role.id)
    p.add_int32(action_type)
    p.add_int32(money)
    data = p.get_pck_has_head()
    # 发送数据包
    g_client.sendall(data)


def pck_handler(pck):
    global g_players, g_role, env
    p = Protocol(pck)
    pck_type = p.get_str()

    if pck_type == 'init_players':  # 玩家移动的数据包
        player_num = p.get_int32()
        g_players = {i: PlayerPublicInfo() for i in range(player_num)}
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
    elif pck_type == 'private_info':
        str_cards = p.get_str()
        g_role.card = str_cards.split(' ')
    elif pck_type == 'env_info':
        str_public_cards = p.get_str()
        public_cards = str_public_cards.split(' ')
        env.update(public_cards, p.get_int32(), p.get_int32(), p.get_int32(), p.get_int32())
    elif pck_type == 'ask_for_action':
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
    # global g_screen, g_sur_role, g_player, g_font
    global g_role, g_players
    # # 初始化pygame
    # pygame.init()
    # pygame.display.set_caption('网络游戏Demo')
    # g_screen = pygame.display.set_mode([WIDTH, HEIGHT])
    # g_sur_role = pygame.image.load("./role.png").convert_alpha()  # 人物图片
    # g_font = pygame.font.SysFont("fangsong", 24)
    # # 初始化随机种子
    # random.seed(int(time.time()))
    # 创建角色
    # 随机生成一个名字
    # last_name = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫',
    #              '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许', '何', '吕', '施', '张',
    #              '孔', '曹', '严', '华', '金', '魏', '陶', '姜', '戚', '谢', '邹', '喻', ]
    # first_name = ['梦琪', '忆柳', '之桃', '慕青', '问兰', '尔岚', '元香', '初夏', '沛菡',
    #               '傲珊', '曼文', '乐菱', '痴珊', '孤风', '雅彤', '宛筠', '飞松', '初瑶',
    #               '夜云', '乐珍']
    # name = random.choice(last_name) + random.choice(first_name)
    name = input('输入你的昵称：')
    g_role = Role(name)

    # 与服务器建立连接
    g_client.connect(ADDRESS)
    # 开始接受服务端消息
    thead = Thread(target=msg_handler)
    thead.setDaemon(True)
    thead.start()
    # 告诉服务端有新玩家
    register()


def handler_event():
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_9:
                send_get_ready()
            # elif event.key == pygame.K_s:
            #     g_player.y += 5
            # elif event.key == pygame.K_a:
            #     g_player.x -= 5
            # elif event.key == pygame.K_d:
            #     g_player.x += 5
            # send_role_move()  # 告诉服务器，自己移动了


def update_logic():
    """
    逻辑更新
    """
    # 事件处理
    handler_event()


def update_view():
    """
    视图更新
    """
    # g_screen.fill((0, 0, 0))
    # # 画角色
    # g_screen.blit(g_player.sur_name, (g_player.x, g_player.y - 20))
    # g_screen.blit(g_sur_role, (g_player.x, g_player.y))
    # # 画其他角色
    # for r in g_other_player:
    #     g_screen.blit(r.sur_name, (r.x, r.y - 20))
    #     g_screen.blit(g_sur_role, (r.x, r.y))
    # # 刷新
    # pygame.display.flip()
    pass


def main_loop():
    """
    游戏主循环
    """
    while True:
        # FPS=60
        # pygame.time.delay(32)
        # 逻辑更新
        update_logic()
        # 视图更新
        update_view()


if __name__ == '__main__':
    # 初始化
    init_game()
    # 游戏循环
    main_loop()


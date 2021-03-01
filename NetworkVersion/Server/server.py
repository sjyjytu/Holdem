import socketserver
import threading
from time import sleep

from NetworkVersion.Server.protocal import Protocol

from NetworkVersion.game_manager import GameManager
from NetworkVersion.utils import Action

ADDRESS = ('127.0.0.1', 8712)  # 绑定地址

g_conn_pool = []  # 连接池

ready_num = 0  # TODO: 记得清零
gm = None


class Conn:
    def __init__(self, conn):
        self.conn = conn
        self.name = None
        self.id = -1
        self.is_ready = False


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def setup(self):
        self.request.sendall("连接服务器成功!".encode(encoding='utf8'))
        # 加入连接池
        conn = Conn(self.request)
        g_conn_pool.append(conn)

    def handle(self):
        while True:
            try:
                # 读取数据包
                bytes = self.request.recv(1024)
                # 切割数据包
                while True:
                    # 读取包长度
                    length_pck = int.from_bytes(bytes[:4], byteorder='little')
                    # 截取封包
                    pck = bytes[4:4 + length_pck]
                    # 删除已经读取的字节
                    bytes = bytes[4 + length_pck:]
                    # 把封包交给处理函数
                    self.pck_handler(pck)
                    # 如果bytes没数据了，就跳出循环
                    if len(bytes) == 0:
                        break
                    # print("客户端消息：", bytes.decode(encoding="utf8"))
            except Exception as e:  # 意外掉线
                print("---------------------------")
                print("玩家：【%s】掉线啦。" % self.get_conn().name)
                self.remove()
                break

    def finish(self):
        pass

    def get_conn(self):
        for conn in g_conn_pool:
            if conn.conn == self.request:
                return conn

    def new_role(self):
        # 告诉各个客户端有新玩家加入
        ret = Protocol()
        ret.add_str("newplayer")
        ret.add_int32(self.get_conn().x)
        ret.add_int32(self.get_conn().y)
        ret.add_str(self.get_conn().name)
        for r in g_conn_pool:
            if r != self.get_conn():
                r.conn.sendall(ret.get_pck_has_head())

    def other_role(self):
        # 告诉当前玩家，其他玩家的信息
        for conn in g_conn_pool:
            if conn != self.get_conn():
                ret = Protocol()
                ret.add_str("newplayer")
                ret.add_int32(conn.x)
                ret.add_int32(conn.y)
                ret.add_str(conn.name)
                self.request.sendall(ret.get_pck_has_head())

    def move_role(self):
        # 告诉各个客户端有玩家移动了
        ret = Protocol()
        ret.add_str("playermove")
        ret.add_int32(self.get_conn().x)
        ret.add_int32(self.get_conn().y)
        ret.add_str(self.get_conn().name)
        for r in g_conn_pool:
            if r != self.get_conn():
                r.conn.sendall(ret.get_pck_has_head())

    def init_client_players(self):
        # gm刚建立时，要每个client初始化一个player_num大小的PlayerPublicInfo列表
        ret = Protocol()
        ret.add_str("init_players")
        player_num = len(g_conn_pool)
        ret.add_int32(player_num)
        for r in g_conn_pool:
            r.conn.sendall(ret.get_pck_has_head())

    def refresh_player_public_info(self):
        global gm
        # TODO：把player的公开信息发送给client，每个client通过id判断哪个是自己
        # TODO：可以优化成只更新指定pid的人的信息
        ret = Protocol()
        # 要发送的信息是一个列表[(pid, possess, cur_bet, current_state)]
        ret.add_str("public_info")
        num = len(g_conn_pool)
        ret.add_int32(num)
        for r in g_conn_pool:
            pid = r.id
            public_info = gm.get_public_info_by_pid(pid)
            ret.add_int32(pid)
            ret.add_int32(public_info[0])
            ret.add_int32(public_info[1])
            ret.add_int32(public_info[2].value)
        for r in g_conn_pool:
            r.conn.sendall(ret.get_pck_has_head())

    def refresh_player_private_info(self, pidx):
        global gm
        # TODO：向指定id的client发送私密信息（card）
        for r in g_conn_pool:
            if r.id == pidx:
                ret = Protocol()
                ret.add_str("private_info")
                str_cards = " ".join(gm.get_player_card_by_pid(pidx))
                ret.add_str(str_cards)
                r.conn.sendall(ret.get_pck_has_head())
                break

    def refresh_env_info(self):
        global gm
        # 向所有人发送env信息：公共牌、最大下注、大盲位置啥的
        public_card, pool_possess, BB_id, current_max_bet, current_left_player_num = gm.get_env_info()
        str_public_card = " ".join(public_card)
        ret = Protocol()
        ret.add_str("env_info")
        ret.add_str(str_public_card)
        ret.add_int32(pool_possess)
        ret.add_int32(BB_id)
        ret.add_int32(current_max_bet)
        ret.add_int32(current_left_player_num)
        for r in g_conn_pool:
            r.conn.sendall(ret.get_pck_has_head())

    def ask_for_action(self):
        # TODO: 向指定id的client索取action，超时则返回默认action（弃牌）。
        # TODO: 应该重写utils中Player的take_action函数，输入action应该搬到client端的Player去
        pass

    def play_a_game(self):
        # 把GameManager的play_a_game移到这里来实现，方便穿插向client发消息，以及判断游戏状态
        global gm
        gm = GameManager()  # TODO: 删除这一行
        # 返回一局的赢家，-1表示人数不足了，游戏结束
        # 开始前默认确定好大小盲位置，且场上玩家大于两位
        if gm.alive_player_num < 2:
            return -1
        gm.poker.reset_card()

        # TODO: 开局即allin
        gm.init_env(gm.BB_pos, len(gm.alive_player_id))

        # 下盲注
        gm.env.pool_possess += gm.players[gm.alive_player_id[gm.BB_pos]].bet(2 * gm.base_chip)
        gm.env.pool_possess += gm.players[gm.alive_player_id[gm.SB_pos]].bet(gm.base_chip)

        # 更新玩家信息和环境信息
        self.refresh_env_info()
        self.refresh_player_public_info()

        # 开始发两张底牌
        for pidx in gm.alive_player_id:
            gm.players[pidx].card += gm.poker.deal(2)
            self.refresh_player_private_info(pidx)
        gm.update_env()

        # self.print_info(current_player_idx)
        # 第一轮下注
        if not gm.a_round_of_bet(g_conn_pool):
            return

        # 发三张公共牌
        gm.env.public_cards += gm.poker.deal(3)
        gm.update_env()
        self.refresh_env_info()

        # 第二轮下注
        if not gm.a_round_of_bet(g_conn_pool):
            return

        # 发一张公共牌
        gm.env.public_cards += gm.poker.deal(1)
        gm.update_env()
        self.refresh_env_info()

        # 第三轮下注
        if not gm.a_round_of_bet(g_conn_pool):
            return

        # 发一张公共牌
        gm.env.public_cards += gm.poker.deal(1)
        gm.update_env()
        self.refresh_env_info()

        # 最后一轮下注
        if not gm.a_round_of_bet(g_conn_pool):
            return

        # 开牌比大小，分赃
        gm.compare_card()

        # 更新玩家信息和环境信息
        self.refresh_env_info()
        self.refresh_player_public_info()

    def pck_handler(self, pck):
        """
        解析数据包
        """
        p = Protocol(pck)
        pck_type = p.get_str()

        if pck_type == 'register':
            self.get_conn().name = p.get_str()

        elif pck_type == 'ready':
            self.get_conn().is_ready = True  # TODO: 结束后要重置
            global ready_num, gm
            ready_num += 1
            if len(g_conn_pool) >= 3 and len(g_conn_pool) == ready_num:
                # 最后一个按准备的人，对应的线程有点房主的意思
                # 游戏开始
                if gm is None:
                    # 如果是第一次开始游戏，先初始化牌桌的游戏管理器
                    gm = GameManager(player_num=ready_num)
                    self.init_client_players()
                    # 为每个玩家分配id（按顺序就行）
                    for i, conn in enumerate(g_conn_pool):
                        conn.id = i
                else:
                    # TODO: 如果前面已经玩过游戏了，开始第k局怎么办？要不要清理玩家，重置状态，检查在不在线，有新加入玩家啊什么的
                    pass

                self.play_a_game()

        elif pck_type == 'action':
            pid = p.get_int32()
            action_type = p.get_int32()
            money = p.get_int32()
            no2action = {1: 'FOLD', 2: 'CHECK_OR_CALL', 3: 'CALL_AND_RAISE'}
            action = Action(no2action[action_type], money)
            # 设置gm的对应玩家采取的action
            gm.player_actions[pid] = action
            gm.player_action_flag[pid] = True

    def remove(self):
        # # 告诉各个客户端有玩家离线
        # ret = Protocol()
        # ret.add_str("logout")
        # ret.add_str(self.get_conn().name)
        # for r in g_conn_pool:
        #     if r != self.get_conn():
        #         r.conn.sendall(ret.get_pck_has_head())
        # g_conn_pool.remove(self.get_conn())
        pass


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == '__main__':
    server = ThreadedTCPServer(ADDRESS, ThreadedTCPRequestHandler)
    # 新开一个线程运行服务端
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # 主线程逻辑
    while True:
        sleep(3)
# linux下后台运行不能使用input
#         cmd = input("""--------------------------
# 输入1:查看当前在线人数
# 输入2:关闭服务端
# """)
#         if cmd == '1':
#             print("--------------------------")
#             print("当前在线人数：", len(g_conn_pool))
#         elif cmd == '2':
#             server.shutdown()
#             server.server_close()
#             exit()

from Game.utils import *
from random import choice


class GameManager:
    def __init__(self, player_num=6, base_chip=10):
        self.env = None
        self.player_num = player_num
        self.players = [Player(pos=i) for i in range(player_num)]
        self.alive_player_idx = list(range(player_num)) # 筹码没输光的玩家
        self.alive_player_num = player_num
        self.poker = Poker()
        self.base_chip = base_chip

        # 初始化大小盲注位置，注意这个pos是针对alive_player的
        self.BB_pos = choice(range(self.alive_player_num))
        self.SB_pos = (self.BB_pos - 1 + self.alive_player_num) % self.alive_player_num

        self.public_cards = []

    # def _next_idx(self, i):
    #     return (i + 1) % self.alive_player_num
    #
    # def _prev_idx(self, i):
    #     return (i - 1 + self.alive_player_num) % self.alive_player_num

    def print_info(self, current_player_idx):
        print('公共牌：', self.public_cards)
        for pidx in current_player_idx:
            player = self.players[pidx]
            print('玩家%d | 底牌: ' % pidx, player.card, ' | 本局下注: %d | 总筹码: %d' % (player.current_bet, player.possess))

    def init_env(self, current_player_idx):
        self.env = Env(current_player_idx, self.base_chip)

    def update_env(self):
        pass

    def check_match_state(self):
        current_player_num = len(self.env.current_player_idx)
        if current_player_num == 1:
            self.end_match(self.env.current_player_idx[0], self.env.pool_possess)
            return self.env.current_player_idx[0]

    def end_match(self, winner, win_chip):
        pass

    def a_round_of_bet(self, round_num):
        for pos, pidx in enumerate(self.env.current_player_idx):
            action = self.players[pidx].take_action(pos, self.env, 1)  # 先默认遵守规则来，但实际上可能乱了
            self.update_env()

            if action == Action.FOLD:
                # 弃牌
                self.env.current_player_idx = [x for x in self.env.current_player_idx if x != pidx]
                self.players[pidx].calc_chip(0)
                self.check_match_state()
            elif action == Action.CHECK:
                pass

    def compare_card(self):
        for pidx in self.env.current_player_idx:
            self.players

    def play_a_game(self):
        # 返回一局的赢家，-1表示人数不足了，游戏结束
        # 开始前默认确定好大小盲位置，且场上玩家大于两位
        if self.alive_player_num < 2:
            return -1
        self.poker.reset_card()
        pool_possess = 0 # 底池奖励

        # 当前牌局的玩家，位置从大盲下家开始
        current_player_idx = self.alive_player_idx[self.BB_pos+1:] + self.alive_player_idx[:self.BB_pos+1]

        # 下盲注
        self.players[self.alive_player_idx[self.BB_pos]].bet(2*self.base_chip)
        self.players[self.alive_player_idx[self.SB_pos]].bet(self.base_chip)
        self.init_env(current_player_idx)

        # 开始发两张底牌
        for i in range(2):
            for pidx in self.env.current_player_idx:
                self.players[pidx].card += self.poker.deal()
        self.update_env()

        # self.print_info(current_player_idx)
        # 第一轮下注
        self.a_round_of_bet(1)

        # 发三张公共牌
        self.public_cards += self.poker.deal(3)
        self.update_env()

        # 第二轮下注
        self.a_round_of_bet(2)

        # 发一张公共牌
        self.public_cards += self.poker.deal(1)
        self.update_env()

        # 第三轮下注
        self.a_round_of_bet(3)

        # 发一张公共牌
        self.public_cards += self.poker.deal(1)
        self.update_env()

        # 最后一轮下注
        self.a_round_of_bet(4)

        # 开牌比大小
        self.compare_card()


gm = GameManager()
gm.play_a_game()












from random import choice
import functools
from Game.utils import *
from Game.evaluate_card import choose_own_biggest_card, compare_hands


class GameManager:
    def __init__(self, player_num=6, base_chip=10):
        self.env = None
        self.player_num = player_num
        self.players = [Player(pos=i) for i in range(player_num)]
        self.alive_player_id = list(range(player_num)) # 筹码没输光的玩家
        self.alive_player_num = player_num
        self.poker = Poker()
        self.base_chip = base_chip

        # 初始化大小盲注位置，注意这个pos是针对alive_player的
        self.BB_pos = choice(range(self.alive_player_num))
        self.SB_pos = (self.BB_pos - 1 + self.alive_player_num) % self.alive_player_num

    def _next_idx(self, i):
        return (i + 1) % self.alive_player_num

    def _next_left_idx(self, i):
        ni = self._next_idx(i)
        while self.players[self.alive_player_id[ni]].current_state == Player_State.FOLD:
            ni = self._next_idx(ni)
        return ni

    def _next_bet_available_idx(self, i):
        ni = self._next_idx(i)
        while self.players[self.alive_player_id[ni]].current_state != Player_State.NORMAL:
            ni = self._next_idx(ni)
        return ni

    def _prev_idx(self, i):
        return (i - 1 + self.alive_player_num) % self.alive_player_num

    def _prev_bet_available_idx(self, i):
        pi = self._prev_idx(i)
        while self.players[self.alive_player_id[pi]].current_state != Player_State.NORMAL:
            pi = self._next_idx(pi)
        return pi

    def print_info(self):
        print('公共牌：', self.env.public_cards)
        for pid in self.alive_player_id:
            player = self.players[pid]
            print('玩家%d | 底牌: ' % pid, player.card, ' | 状态: ', player.current_state,
                  ' | 本局下注: %d | 总筹码: %d' % (player.current_bet, player.possess))

    def init_env(self, BB_pos, current_left_player_num):
        self.env = Env(BB_pos, current_left_player_num, self.base_chip)

    def update_env(self):
        pass

    def check_match_state(self):
        if self.env.current_left_player_num == 1:
            for pidx in self.alive_player_id:
                if self.players[pidx].current_state != Player_State.FOLD:
                    self.end_match([pidx])
                    return [pidx]

    def end_match(self, winners):
        # 分赃，清理没钱的人，重新分配大盲位置
        pass

    def a_round_of_bet(self, round_num):
        idx = self._next_bet_available_idx(self.env.BB_pos)  # 大盲下家能加注（除去弃牌和allin的人）开始操作
        eidx = self._prev_bet_available_idx(idx)  # 第一家操作的人的上一个能加注的人最后操作
        # 按顺序轮询这些玩家的操作，一旦有玩家的操作使得本局最大加注筹码发生改变，则刷新eidx为该玩家的上一家
        bet_count = 1
        while True:
            while idx != eidx:
                pid = self.alive_player_id[idx]
                cur_player = self.players[pid]
                # 当前玩家的下注与最大下注的差距
                bet_dist = self.env.current_max_bet - cur_player.current_bet
                if bet_dist > 0:
                    availble_actions = [Action.FOLD, Action.CHECK]
                action = cur_player.take_action(-1, self.env, bet_count)

                self.update_env()

                # 刷新
                if cur_player.current_bet > self.env.current_max_bet:
                    self.env.current_max_bet = cur_player.current_bet
                    eidx = self._prev_bet_available_idx(idx)
                idx = self._next_bet_available_idx(idx)
            # 最后一个玩家的操作，若刷新，则继续，否则，break结束本轮加注
            last_bet_more = True
            if last_bet_more:
                bet_count += 1
                eidx = self._prev_bet_available_idx(idx)
                idx = self._next_bet_available_idx(eidx)
            else:
                break

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

    @staticmethod
    def my_cmp(a, b):
        res = compare_hands(a[1][1], b[1][1])
        if res[0] == 'LEFT':
            return 1
        elif res[0] == 'RIGHT':
            return -1
        return 0

    def get_next_rank_pidxes(self, current_pidx_and_best_card, si):
        assert si < len(current_pidx_and_best_card)
        get_card = current_pidx_and_best_card[si][1][1]
        winners = [current_pidx_and_best_card[si][0]]
        si += 1
        while si < len(current_pidx_and_best_card) and compare_hands(get_card, current_pidx_and_best_card[si][1][1]) == "TIE":
            winners.append(current_pidx_and_best_card[si][0])
            si += 1
        return winners, si

    def compare_card(self):
        current_pidx_and_best_card = []
        for pidx in self.env.current_player_idx:
            self.players[pidx].current_chosen_card_info = choose_own_biggest_card(self.players[pidx].card + self.env.public_cards)
            current_pidx_and_best_card.append((pidx, self.players[pidx].current_chosen_card_info))
        # 按大小排序，最大的排第一，可能会有并列的情况
        current_pidx_and_best_card = sorted(current_pidx_and_best_card, key=functools.cmp_to_key(self.my_cmp))

        # 开始分赃，要考虑有人ALL-IN吃不下所有，以及牌一样大平分的情况
        start_index = 0
        while self.env.pool_possess > 0:
            winners, start_index = self.get_next_rank_pidxes(current_pidx_and_best_card, start_index)

        # 清理没钱的人，重新分配大盲位置

    def play_a_game(self):
        # 返回一局的赢家，-1表示人数不足了，游戏结束
        # 开始前默认确定好大小盲位置，且场上玩家大于两位
        if self.alive_player_num < 2:
            return -1
        self.poker.reset_card()

        # 当前牌局的玩家，位置从大盲下家开始
        current_player_idx = self.alive_player_id[self.BB_pos+1:] + self.alive_player_id[:self.BB_pos+1]

        # 下盲注
        self.players[self.alive_player_id[self.BB_pos]].bet(2*self.base_chip)
        self.players[self.alive_player_id[self.SB_pos]].bet(self.base_chip)
        self.init_env(current_player_idx, len(self.alive_player_id))

        # 开始发两张底牌
        for i in range(2):
            for pidx in self.env.current_player_idx:
                self.players[pidx].card += self.poker.deal()
        self.update_env()

        # self.print_info(current_player_idx)
        # 第一轮下注
        self.a_round_of_bet(1)

        # 发三张公共牌
        self.env.public_cards += self.poker.deal(3)
        self.update_env()

        # 第二轮下注
        self.a_round_of_bet(2)

        # 发一张公共牌
        self.env.public_cards += self.poker.deal(1)
        self.update_env()

        # 第三轮下注
        self.a_round_of_bet(3)

        # 发一张公共牌
        self.env.public_cards += self.poker.deal(1)
        self.update_env()

        # 最后一轮下注
        self.a_round_of_bet(4)

        # 开牌比大小，分赃
        self.compare_card()


gm = GameManager()
gm.play_a_game()












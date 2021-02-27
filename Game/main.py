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
        return None

    def end_match(self, winners):
        # 分赃，清理没钱的人，重新分配大盲位置
        pass

    def process_action(self, idx):
        pid = self.alive_player_id[idx]
        cur_player = self.players[pid]
        # 当前玩家的下注与最大下注的差距
        bet_dist = self.env.current_max_bet - cur_player.current_bet
        # if bet_dist > 0:
        #     availble_actions = [Action.FOLD, Action.CALL]
        action = cur_player.take_action(-1, self.env)
        if action.is_FOLD():
            # 弃牌
            self.env.current_left_player_num -= 1
            cur_player.current_state = Player_State.FOLD
            winners = self.check_match_state()
            if winners is not None:
                # TODO: 结算
                pass
        elif action.is_CHECK_OR_CALL():
            if bet_dist >= cur_player.possess:
                # 筹码不够跟了，要跟就只能allin了
                self.env.pool_possess += cur_player.bet(cur_player.possess)
                cur_player.current_state = Player_State.ALLIN
            else:
                # check或者跟上
                self.env.pool_possess += cur_player.bet(bet_dist)
        elif action.is_CALL_AND_RAISE():
            if bet_dist >= cur_player.possess or bet_dist + action.money >= cur_player.possess:
                # 筹码不够跟了，要跟就只能allin了，或者要加的超了自己财产了
                self.env.pool_possess += cur_player.bet(cur_player.possess)
                cur_player.current_state = Player_State.ALLIN
            else:
                self.env.pool_possess += cur_player.bet(bet_dist + action.money)
        else:
            print("invalid action")

        self.update_env()

        # 刷新
        FLUSH_FLAG = False
        if cur_player.current_bet > self.env.current_max_bet:
            self.env.current_max_bet = cur_player.current_bet
            eidx = self._prev_bet_available_idx(idx)
            FLUSH_FLAG = True
        idx = self._next_bet_available_idx(idx)
        return idx, eidx, FLUSH_FLAG

    def a_round_of_bet(self):
        idx = self._next_bet_available_idx(self.env.BB_pos)  # 大盲下家能加注（除去弃牌和allin的人）开始操作
        eidx = self._prev_bet_available_idx(idx)  # 第一家操作的人的上一个能加注的人最后操作
        # 按顺序轮询这些玩家的操作，一旦有玩家的操作使得本局最大加注筹码发生改变，则刷新eidx为该玩家的上一家
        while True:
            while idx != eidx:
                idx, eidx, _ = self.process_action(idx)
            # 最后一个玩家的操作，若刷新，则继续，否则，break结束本轮加注
            idx, edix, last_bet_more = self.process_action(idx)
            if not last_bet_more:
                # 本轮加注结束
                break

    @staticmethod
    def my_cmp(a, b):
        res = compare_hands(a[1][1], b[1][1])
        if res[0] == 'LEFT':
            return 1
        elif res[0] == 'RIGHT':
            return -1
        return 0

    def compare_card(self):
        # 遍历，找出弃牌的人，把他们的钱加入到底池，记录出要比牌的人
        buttom_pool = 0
        fold_pidx = []
        candidate_pidx_and_bet = []
        for pidx in self.alive_player_id:
            cur_bet = self.players[pidx].current_bet
            if self.players[pidx].current_state == Player_State.FOLD:
                buttom_pool += cur_bet
                fold_pidx.append(pidx)
            else:
                candidate_pidx_and_bet.append((pidx, cur_bet))
        sorted(candidate_pidx_and_bet, key=lambda x:(x[1], x[0]))

        # current_pidx_and_best_card = []
        # for pidx in self.env.current_player_idx:
        #     self.players[pidx].current_chosen_card_info = choose_own_biggest_card(self.players[pidx].card + self.env.public_cards)
        #     current_pidx_and_best_card.append((pidx, self.players[pidx].current_chosen_card_info))
        # 按大小排序，最大的排第一，可能会有并列的情况
        # current_pidx_and_best_card = sorted(current_pidx_and_best_card, key=functools.cmp_to_key(self.my_cmp))

        # 开始分赃，要考虑有人ALL-IN吃不下所有，以及牌一样大平分的情况
        # 想通过一次排序就确认不太行，还是要先根据下注排序，然后划分底池和边池，然后对每个池的玩家牌大小排序，选出牌最好的人把那个池吃了

        # 清理没钱的人，重新分配大盲位置

    def play_a_game(self):
        # 返回一局的赢家，-1表示人数不足了，游戏结束
        # 开始前默认确定好大小盲位置，且场上玩家大于两位
        if self.alive_player_num < 2:
            return -1
        self.poker.reset_card()

        # 当前牌局的玩家，位置从大盲下家开始
        # current_player_idx = self.alive_player_id[self.BB_pos+1:] + self.alive_player_id[:self.BB_pos+1]

        # 下盲注
        self.env.pool_possess += self.players[self.alive_player_id[self.BB_pos]].bet(2*self.base_chip)
        self.env.pool_possess += self.players[self.alive_player_id[self.SB_pos]].bet(self.base_chip)
        # TODO: 开局即allin
        self.init_env(self.BB_pos, len(self.alive_player_id))

        # 开始发两张底牌
        for pidx in self.alive_player_id:
            self.players[pidx].card += self.poker.deal(2)
        self.update_env()

        # self.print_info(current_player_idx)
        # 第一轮下注
        self.a_round_of_bet()

        # 发三张公共牌
        self.env.public_cards += self.poker.deal(3)
        self.update_env()

        # 第二轮下注
        self.a_round_of_bet()

        # 发一张公共牌
        self.env.public_cards += self.poker.deal(1)
        self.update_env()

        # 第三轮下注
        self.a_round_of_bet()

        # 发一张公共牌
        self.env.public_cards += self.poker.deal(1)
        self.update_env()

        # 最后一轮下注
        self.a_round_of_bet()

        # 开牌比大小，分赃
        self.compare_card()


gm = GameManager()
gm.play_a_game()












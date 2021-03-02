from NetworkVersion.utils import *
from NetworkVersion.evaluate_card import choose_own_biggest_card, compare_hands
from NetworkVersion.Server.protocal import Protocol
import time


class GameManager:
    def __init__(self, player_num=6, base_chip=10):
        self.env = None
        self.player_num = player_num
        self.players = [Player(id=i) for i in range(player_num)]
        self.alive_player_id = list(range(player_num))  # 筹码没输光的玩家
        self.alive_player_num = player_num
        self.poker = Poker()
        self.base_chip = base_chip

        self.player_actions = [Action("FOLD") for i in range(player_num)]
        self.player_action_flag = [False for i in range(player_num)]

        # 初始化大小盲注位置，注意这个pos是针对alive_player的
        self.BB_pos = choice(range(self.alive_player_num))
        self.SB_pos = (self.BB_pos - 1 + self.alive_player_num) % self.alive_player_num

    def get_public_info_by_pid(self, pid):
        return self.players[pid].possess, self.players[pid].current_bet, self.players[pid].current_state

    def get_player_card_by_pid(self, pid):
        suit2word = {'spades': '黑桃', 'hearts': '红心', 'clubs': '梅花', 'diamonds': '方片'}
        return [suit2word[card.suit] + card.rank for card in self.players[pid].card]

    def get_env_info(self):
        suit2word = {'spades': '黑桃', 'hearts': '红心', 'clubs': '梅花', 'diamonds': '方片'}
        public_card = [suit2word[card.suit] + card.rank for card in self.env.public_cards]
        pool_possess, BB_id, current_max_bet, current_left_player_num \
            = self.env.pool_possess, self.alive_player_id[self.BB_pos], \
              self.env.current_max_bet, self.env.current_left_player_num
        return public_card, pool_possess, BB_id, current_max_bet, current_left_player_num

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
            if ni == i:
                # 转了一圈了，没有下一个了，一般到这里的话这个i还就allin了
                return ni
            ni = self._next_idx(ni)
        return ni

    def _prev_idx(self, i):
        return (i - 1 + self.alive_player_num) % self.alive_player_num

    def _prev_bet_available_idx(self, i):
        pi = self._prev_idx(i)
        while self.players[self.alive_player_id[pi]].current_state != Player_State.NORMAL:
            if pi == i:
                # 转了一圈了，没有下一个了，一般到这里的话这个i还就allin了
                return pi
            pi = self._prev_idx(pi)
        return pi

    def print_info(self):
        print()
        suit2word = {'spades': '黑桃', 'hearts': '红心', 'clubs': '梅花', 'diamonds': '方片'}
        print('公共牌：', [suit2word[card.suit] + card.rank for card in self.env.public_cards])
        print('大盲位置：', self.alive_player_id[self.BB_pos])
        for pid in self.alive_player_id:
            player = self.players[pid]
            print('玩家%d | 底牌: ' % pid, [suit2word[card.suit] + card.rank for card in player.card], ' | 状态: ',
                  player.current_state,
                  ' | 本局下注: %d | 总筹码: %d' % (player.current_bet, player.possess))

    def init_env(self, BB_pos, current_left_player_num):
        self.env = Env(BB_pos, current_left_player_num, self.base_chip)

    def update_env(self):
        # TODO: 更新环境，记录玩家动作
        self.print_info()

    def check_match_state(self):
        if self.env.current_left_player_num == 1:
            for pidx in self.alive_player_id:
                if self.players[pidx].current_state != Player_State.FOLD:
                    self.players[pidx].possess += self.env.pool_possess
                    self.end_match()
                    return False
        return True

    def end_match(self):
        # 清理没钱的人，重新分配大盲位置，可能会一个人赢光了，没有下一个大盲了
        for i in range(1, self.alive_player_num + 1):
            pos = (self.BB_pos + i) % self.alive_player_num
            pidx = self.alive_player_id[pos]
            if self.players[pidx].possess > 0:
                next_BB_pidx = pidx
                break
        new_alive_player_id = []
        for pidx in self.alive_player_id:
            self.players[pidx].reset_all_state()  # 重置所有玩家的状态
            if self.players[pidx].possess > 0:
                new_alive_player_id.append(pidx)
        self.alive_player_id = new_alive_player_id
        self.alive_player_num = len(new_alive_player_id)

        self.BB_pos = new_alive_player_id.index(next_BB_pidx)
        self.SB_pos = (self.BB_pos - 1 + self.alive_player_num) % self.alive_player_num

    def refresh_player_public_info(self, g_conn_pool):
        # 把player的公开信息发送给client，每个client通过id判断哪个是自己
        # TODO: 可以优化成只更新指定pid的人的信息
        ret = Protocol()
        # 要发送的信息是一个列表[(pid, possess, cur_bet, current_state)]
        ret.add_str("public_info")
        num = len(g_conn_pool)
        ret.add_int32(num)
        for r in g_conn_pool:
            pid = r.id
            public_info = self.get_public_info_by_pid(pid)
            ret.add_int32(pid)
            ret.add_int32(public_info[0])
            ret.add_int32(public_info[1])
            ret.add_int32(public_info[2].value)
        for r in g_conn_pool:
            r.conn.sendall(ret.get_pck_has_head())

    def refresh_env_info(self, g_conn_pool):
        # 向所有人发送env信息：公共牌、最大下注、大盲位置啥的
        public_card, pool_possess, BB_id, current_max_bet, \
        current_left_player_num = self.get_env_info()
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

    def process_action(self, idx, eidx, g_conn_pool):
        pid = self.alive_player_id[idx]
        cur_player = self.players[pid]
        # 当前玩家的下注与最大下注的差距
        bet_dist = self.env.current_max_bet - cur_player.current_bet
        # if bet_dist > 0:
        #     availble_actions = [Action.FOLD, Action.CALL]
        # action = cur_player.take_action(-1, self.env)

        # 向对应player索要action
        self.player_action_flag[pid] = False  # 先重置，尽量减少延迟带来的bug
        ret = Protocol()
        ret.add_str("ask_for_action")
        g_conn_pool[pid].conn.sendall(ret.get_pck_has_head())
        print('ask %d for action' % pid)
        # 等待返回gm用一个数组flag来记录
        timeout = 0  # 等待玩家40秒
        while not self.player_action_flag[pid] and timeout < 80:
            time.sleep(0.5)
            timeout += 1
        action = Action("FOLD")  # 超时默认弃牌
        if self.player_action_flag[pid]:
            action = self.player_actions[pid]

        if action.is_FOLD():
            # 弃牌
            self.env.current_left_player_num -= 1
            cur_player.current_state = Player_State.FOLD
        elif action.is_CHECK_OR_CALL():
            if bet_dist >= cur_player.possess:
                # 筹码不够跟了，要跟就只能allin了
                self.env.pool_possess += cur_player.bet(cur_player.possess)
                cur_player.current_state = Player_State.ALLIN
            else:
                # check或者跟上
                self.env.pool_possess += cur_player.bet(bet_dist)
        elif action.is_CALL_AND_RAISE():
            if bet_dist + action.money >= cur_player.possess:
                # 筹码不够跟了，要跟就只能allin了，或者要加的超了自己财产了
                self.env.pool_possess += cur_player.bet(cur_player.possess)
                cur_player.current_state = Player_State.ALLIN
            else:
                self.env.pool_possess += cur_player.bet(bet_dist + action.money)
        else:
            print("invalid action")

        # 刷新
        FLUSH_FLAG = False
        if cur_player.current_bet > self.env.current_max_bet:
            self.env.current_max_bet = cur_player.current_bet
            eidx = self._prev_bet_available_idx(idx)
            FLUSH_FLAG = True
        idx = self._next_bet_available_idx(idx)

        self.update_env()
        # 调用refresh_player_public_info和refresh_env_info
        self.refresh_player_public_info(g_conn_pool)
        self.refresh_env_info(g_conn_pool)
        return idx, eidx, FLUSH_FLAG

    def a_round_of_bet(self, g_conn_pool):
        idx = self._next_bet_available_idx(self.BB_pos)  # 大盲下家能加注（除去弃牌和allin的人）开始操作
        eidx = self._prev_bet_available_idx(idx)  # 第一家操作的人的上一个能加注的人最后操作
        if idx != eidx:
            # idx==eidx: 没人能加注了（都allin了或者只剩一个了，加不加都无所谓了）
            # 按顺序轮询这些玩家的操作，一旦有玩家的操作使得本局最大加注筹码发生改变，则刷新eidx为该玩家的上一家
            while True:
                while idx != eidx:
                    idx, eidx, _ = self.process_action(idx, eidx, g_conn_pool)

                if self.env.current_left_player_num == 1:
                    break
                # 最后一个玩家的操作，若刷新，则继续，否则，break结束本轮加注
                idx, eidx, last_bet_more = self.process_action(idx, eidx, g_conn_pool)
                if not last_bet_more:
                    # 本轮加注结束
                    break
        return self.check_match_state()

    # 比牌和分赃，要考虑有人ALL-IN吃不下所有，以及牌一样大平分的情况
    # 想通过一次排序就确认不太行，还是要先根据下注排序，然后划分底池和边池，然后对每个池的玩家牌大小排序，选出牌最好的人把那个池吃了
    def compare_card(self):
        # 遍历，找出弃牌的人，把他们的钱加入到底池，以列表的形式记录出要比牌的人
        buttom_pool = 0
        fold_pidx = []
        candidate_bet_pidx_dict = {}
        for pidx in self.alive_player_id:
            cur_bet = self.players[pidx].current_bet
            if self.players[pidx].current_state == Player_State.FOLD:
                buttom_pool += cur_bet
                fold_pidx.append(pidx)
            else:
                # 玩家选出自己最大的牌型
                self.players[pidx].current_chosen_card_info = choose_own_biggest_card(
                    self.players[pidx].card + self.env.public_cards)

                # 玩家下注筹码与pidx记录起来
                if cur_bet in candidate_bet_pidx_dict.keys():
                    candidate_bet_pidx_dict[cur_bet].append(pidx)
                else:
                    candidate_bet_pidx_dict[cur_bet] = [pidx]

        sorted_bet = sorted(candidate_bet_pidx_dict.keys(), reverse=True)
        accumulate_participants_num = 0
        cur_best_card_keepers = []  # 下注由大到小轮询过去当前牌最大的人
        cur_best_card = None
        # 由下注大到小轮询边池，最后底池
        for i in range(len(sorted_bet)):
            if i != len(sorted_bet) - 1:
                # 边池大小
                margin_pool_dist = sorted_bet[i] - sorted_bet[i + 1]
                accumulate_participants_num += len(candidate_bet_pidx_dict[sorted_bet[i]])
                pool_total_award = accumulate_participants_num * margin_pool_dist  # 当前边池的总筹码奖励
            else:
                # 底池
                accumulate_participants_num += len(candidate_bet_pidx_dict[sorted_bet[i]])
                pool_total_award = accumulate_participants_num * sorted_bet[i] + buttom_pool  # 加上弃牌的底池

            # 将当前牌型最大的人跟新加入的人比一比，比出最大的玩家（们）
            if len(cur_best_card_keepers) == 0:
                to_compare_pidx = candidate_bet_pidx_dict[sorted_bet[i]]
                cur_best_card_pidx = to_compare_pidx[0]
                cur_best_card = self.players[cur_best_card_pidx].current_chosen_card_info.best_card
                cur_best_card_keepers = [cur_best_card_pidx]
            else:
                to_compare_pidx = cur_best_card_keepers + candidate_bet_pidx_dict[sorted_bet[i]]

            compare_begin_index = len(cur_best_card_keepers)
            for j in range(compare_begin_index, len(to_compare_pidx)):
                cur_pidx = to_compare_pidx[j]
                to_compare_card = self.players[cur_pidx].current_chosen_card_info.best_card
                comp_res = compare_hands(cur_best_card, to_compare_card)[0]
                if comp_res == "TIE":
                    cur_best_card_keepers.append(cur_pidx)
                elif comp_res == "RIGHT":
                    # 刷新最大牌
                    cur_best_card = to_compare_card
                    cur_best_card_keepers = [cur_pidx]

            # 将当前池的总奖励分给这些牌最大的人，除不尽的就不要了。。。
            per_player_award = pool_total_award // len(cur_best_card_keepers)
            for pidx in cur_best_card_keepers:
                self.players[pidx].possess += per_player_award

        self.end_match()

    def play_a_game(self):
        # 返回一局的赢家，-1表示人数不足了，游戏结束
        # 开始前默认确定好大小盲位置，且场上玩家大于两位
        if self.alive_player_num < 2:
            return -1
        self.poker.reset_card()

        # 当前牌局的玩家，位置从大盲下家开始
        # current_player_idx = self.alive_player_id[self.BB_pos+1:] + self.alive_player_id[:self.BB_pos+1]

        # TODO: 开局即allin
        self.init_env(self.BB_pos, len(self.alive_player_id))

        # 下盲注
        self.env.pool_possess += self.players[self.alive_player_id[self.BB_pos]].bet(2 * self.base_chip)
        self.env.pool_possess += self.players[self.alive_player_id[self.SB_pos]].bet(self.base_chip)

        # 开始发两张底牌
        for pidx in self.alive_player_id:
            self.players[pidx].card += self.poker.deal(2)
        self.update_env()

        # self.print_info(current_player_idx)
        # 第一轮下注
        if not self.a_round_of_bet():
            return

        # 发三张公共牌
        self.env.public_cards += self.poker.deal(3)
        self.update_env()

        # 第二轮下注
        if not self.a_round_of_bet():
            return

        # 发一张公共牌
        self.env.public_cards += self.poker.deal(1)
        self.update_env()

        # 第三轮下注
        if not self.a_round_of_bet():
            return

        # 发一张公共牌
        self.env.public_cards += self.poker.deal(1)
        self.update_env()

        # 最后一轮下注
        if not self.a_round_of_bet():
            return

        # 开牌比大小，分赃
        self.compare_card()


if __name__ == '__main__':
    gm = GameManager(player_num=4)
    gm.play_a_game()
    gm.print_info()

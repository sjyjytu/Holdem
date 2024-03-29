from enum import Enum
import collections
from random import shuffle, choice


class Action:
    # type: FOLD, CHECK_OR_CALL, CALL_AND_RAISE
    def __init__(self, type="FOLD", money=0):
        self.type = type
        self.money = money

    def is_FOLD(self):
        return self.type == "FOLD"

    def is_CHECK_OR_CALL(self):
        return self.type == "CHECK_OR_CALL"

    def is_CALL_AND_RAISE(self):
        return self.type == "CALL_AND_RAISE"


class Player_State(Enum):
    NORMAL = 1
    ALLIN = 2
    FOLD = 3
    OUT = 4


Chosen_Card_Info = collections.namedtuple('Chosen_Card_Info', ['best_card_type', 'best_card', 'best_card_value'])


class Player:
    def __init__(self, init_possess=10000, id=0, policy=None):
        self.possess = init_possess
        self.current_bet = 0
        self.policy = policy
        self.id = id
        self.card = []
        self.have_money = True
        self.current_chosen_card_info = None
        self.current_state = Player_State.NORMAL

    def bet(self, chip):
        # 下注
        # TODO: 当前筹码不够了的处理
        self.possess -= chip
        self.current_bet += chip
        return chip

    def reset_all_state(self):
        # 一局游戏结束时，重置玩家状态
        self.current_bet = 0
        self.card = []
        self.current_chosen_card_info = None
        self.current_state = Player_State.NORMAL

    def take_action(self, pos, env):
        # 根据策略下注
        # pos: 自己在当前牌局的位置，越大的越后下注，位置越有利; env:场上的形势; no:第几次下注
        a = input('玩家%d 采取动作（1弃牌，2check或call，3加注 加注金额）: ' % self.id)
        a = a.strip(' ').split(' ')
        money = 0
        if len(a) > 1:
            money = int(a[1])
        no2action = {'1': 'FOLD', '2': 'CHECK_OR_CALL', '3': 'CALL_AND_RAISE'}
        return Action(no2action[a[0]], money)


Card = collections.namedtuple('Card', ['rank', 'suit'])


class Poker:
    ranks = [str(n) for n in range(2, 11)]
    ranks.extend('JQKA')
    suits = 'spades hearts clubs diamonds'.split()

    def __init__(self):
        # 初始化 FrenchDeck 类，创建 52 张牌 self._cards
        self._cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        self.deal_pos = 0

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, item):
        return self._cards[item]

    def __setitem__(self, key, value):
        self._cards[key] = value

    def reset_card(self):
        # 重新洗牌
        self.deal_pos = 0
        shuffle(self._cards)

    def deal(self, num=1):
        # 发num张牌
        assert self.deal_pos+num <= self.__len__()
        cards = self._cards[self.deal_pos:self.deal_pos+num]
        self.deal_pos += num
        return cards


class Env:
    # 记录公共牌，每个人下注情况
    def __init__(self, BB_pos, current_left_player_num, base_chip=10):
        self.public_cards = []
        self.pool_possess = 0
        self.BB_pos = BB_pos
        self.current_max_bet = 2 * base_chip
        self.current_left_player_num = current_left_player_num


class LocalEnvInfo:
    def __init__(self):
        self.public_cards = []
        self.pool_possess = 0
        self.BB_id = 0
        self.current_max_bet = 0
        self.current_left_player_num = 0

    def update(self, pc, pp, bbid, cmb, clpn):
        self.public_cards = pc
        self.pool_possess = pp
        self.BB_id = bbid
        self.current_max_bet = cmb
        self.current_left_player_num = clpn


def print_card_small(cards):
    ''' Nicely print a card or list of cards
    Args:
        cards: list of string such as ['♠A', '♥10']
    '''
    if cards is None:
        cards = [None]
    if isinstance(cards, str):
        cards = [cards]

    lines = [[] for _ in range(5)]

    for card in cards:
        if card is None or card == '':
            lines[0].append('┌───────┐')
            lines[1].append('│░░░░░░░│')
            lines[2].append('│░░░░░░░│')
            lines[3].append('│░░░░░░░│')
            lines[4].append('└───────┘')
        else:
            suit = card[0]
            rank = card[1]
            if len(card) == 3:
                space = card[2]
            else:
                space = ' '

            lines[0].append('┌───────┐')
            lines[1].append('│{}{}     │'.format(rank, space))
            lines[2].append('│   {}   │'.format(suit))
            lines[3].append('│     {}{}│'.format(space, rank))
            lines[4].append('└───────┘')

    for line in lines:
        print('   '.join(line))


def chinglish_align(string, length=20):
    difference = length - len(string)  # 计算限定长度为20时需要补齐多少个空格
    if difference == 0:  # 若差值为0则不需要补
        return string
    elif difference < 0:
        print('错误：限定的对齐长度小于字符串长度!')
        return None
    new_string = ''
    space = '　'
    for i in string:
        codes = ord(i)  # 将字符转为ASCII或UNICODE编码
        if codes <= 126:  # 若是半角字符
            new_string = new_string + chr(codes+65248) # 则转为全角
        else:
            new_string = new_string + i  # 若是全角，则不转换
    return new_string + space*(difference)  # 返回补齐空格后的字符串

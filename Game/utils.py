from enum import Enum
import collections
from random import shuffle, choice


class Action(Enum):
    FOLD = 1
    CHECK = 2
    CALL = 3
    RAISE = 4
    ALLIN = 5

    def __init__(self):
        self.money = 0


class Player:
    def __init__(self, init_possess=1000, pos=0, policy=None):
        self.possess = init_possess
        self.current_bet = 0
        self.policy = policy
        self.pos = pos
        self.card = []
        self.alive = True

    def bet(self, chip):
        # 下注
        # TODO: 当前筹码不够了的处理
        self.possess -= chip
        self.current_bet += chip

    def calc_chip(self, win_chip):
        # 一局游戏结束时，清算赢得的钱
        # TODO: 自己ALL-IN了，赢不了全部筹码的处理
        self.possess += win_chip
        self.current_bet = 0

    def take_action(self, pos, env, no):
        # pos: 自己在当前牌局的位置，越大的越后下注，位置越有利; env:场上的形势; no:第几次下注
        if pos == 0:
            return Action.RAISE
        else:
            return Action.CALL


Card = collections.namedtuple('Card', ['rank', 'suit'])


class Poker:
    ranks = [str(n) for n in range(2, 11)]
    ranks.extend('JQKA')
    suits = 'spades hearts diamonds clubs'.split()

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






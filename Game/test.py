# a = [1,2,3,4,5,6]
# b = 0
# for i in a:
#     b += 1
#     if b % 3 == 0:
#         print('remove%d'%i)
#         a.remove(i)
#     print(i)
#
# def KK(a):
#     if a %2==0:
#         return True, 0
#     else:
#         return False, 2
#
# a = KK(3)
# print(a)
# if a[0]:
#     print('dd')
# b = KK(4)
# print(b)
# if b[0]:
#     print('ss')

# from collections import Counter
#
# def Most_Common(lst):
#     data = Counter(lst)
#     return data.most_common(1)[0]
#
# lst = ['A', 'A', 'A', 'A', 2]
# print(Most_Common(lst))
#
# lst = [13,4,13,14,1]
# print(sorted(lst))
# from Game.utils import *
# players = [Player() for i in range(5)]
# p2 = players[2]
# p2.bet(300)
# print(p2.possess)
# print(players[2].possess)
# print(id(p2))
# print(id(players[2]))
#
# p2.current_state = Player_State.ALLIN
# print(players[2].current_state)

# a = '  d a  '
# print(a.strip(' ').split(' '))

# a = [1,2,3,4,5,6]
# print(a[3:])

from Game.utils import *
public_cards = [Card('10', 'hearts'), Card('J', 'spades'), Card('Q', 'clubs'), Card('K', 'clubs'), Card('A', 'spades')]

h1 = [Card('K', 'hearts'), Card('Q', 'diamonds')]
h2 = [Card('J', 'clubs'), Card('2', 'diamonds')]
h3 = [Card('4', 'diamonds'), Card('Q', 'spades')]

# 测试比牌
from evaluate_card import *
hb1 = choose_own_biggest_card(h1+public_cards)
hb2 = choose_own_biggest_card(h2+public_cards)
hb3 = choose_own_biggest_card(h3+public_cards)

print(hb1)
print(hb2)
print(hb3)

# 测试多人allin下筹码分配
from Game.main import GameManager
public_cards = [Card('6', 'hearts'), Card('J', 'spades'), Card('Q', 'clubs'), Card('K', 'clubs'), Card('A', 'spades')]
h1 = [Card('K', 'hearts'), Card('Q', 'diamonds')]
h2 = [Card('J', 'clubs'), Card('10', 'diamonds')]
h3 = [Card('10', 'diamonds'), Card('Q', 'spades')]

gm = GameManager(4)
gm.alive_player_id = alive_player_id = [0,1,2,3]
gm.alive_player_num = 4
gm.init_env(0, 3)
gm.env.public_cards = public_cards

gm.players[0].possess = 100
gm.players[0].current_bet = 500
gm.players[0].current_state = Player_State.FOLD

gm.players[1].card = h1
gm.players[1].possess = 0
gm.players[1].current_bet = 3000
gm.players[1].current_state = Player_State.ALLIN

gm.players[2].card = h2
gm.players[2].possess = 0
gm.players[2].current_bet = 2000
gm.players[2].current_state = Player_State.ALLIN

gm.players[3].card = h3
gm.players[3].possess = 0
gm.players[3].current_bet = 2200
gm.players[3].current_state = Player_State.ALLIN

gm.print_info()
gm.compare_card()
gm.print_info()


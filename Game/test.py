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

a = '  d a  '
print(a.strip(' ').split(' '))
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
# from NetworkVersion.utils import *
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

# 在这里我们模仿一个红绿灯的应用场景，绿灯亮的时候，车可以通过，红灯亮的时候要等待。
import time
import threading

event = threading.Event()  # 首先要获取一个event对象


def lighter():
    count = 0
    event.set()  # 先设置绿灯
    while True:
        if count > 5 and count < 10:  # 改成红灯
            event.clear()  # 把标志位清了
            print("红灯")
        elif count > 10:
            event.set()  # 变绿灯
            count = 0
        else:
            print("绿灯")
        time.sleep(1)
        count += 1


def car(name):
    while True:
        if event.is_set():  # 代表绿灯
            print("[%s] 正在开过" % name)
            time.sleep(1)
        else:
            print("[%s] 正在等待" % name)
            event.wait()  # 车的这个线程就锁在这里不动了，一直到set的时候，才会继续执行car的这个线程


light = threading.Thread(target=lighter, )
light.start()

car1 = threading.Thread(target=car, args=("奔驰",))
car1.start()

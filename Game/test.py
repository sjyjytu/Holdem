a = [1,2,3,4,5,6]
b = 0
for i in a:
    b += 1
    if b % 3 == 0:
        print('remove%d'%i)
        a.remove(i)
    print(i)
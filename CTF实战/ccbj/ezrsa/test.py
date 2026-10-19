def get_list(n):
    # 功能：求出小于n的所有素数
    my_list, cnt, st = [], 0, [False]*n*10
    for i in range(2, n+1):
        if not st[i]:
            my_list.append(i)
            cnt += 1
        for j in range(n):
            if my_list[j] * i > n: 
                break
            st[my_list[j] * i] = True

            if i % my_list[j] == 0: 
                break
    return my_list


from random import choice, shuffle
from math import sqrt

def get_prime(_, n1, n2, bound):
    my_list = get_list(n1)
    print(my_list)
    shuffle(my_list)
    my_list = my_list[:n2]
    print(my_list)
    
get_prime(1,300,50,20)

print(sqrt(300))
print(round(sqrt(300)))
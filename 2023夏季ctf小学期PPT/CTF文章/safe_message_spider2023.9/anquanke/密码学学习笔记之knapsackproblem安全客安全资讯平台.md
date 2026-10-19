# 密码学学习笔记 之 knapsack problem

阅读量 **227640**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-08 15:30:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

ACM中的背包问题是一种组合优化的NP完全问题，而在密码学中，也有对背包问题的应用。

## Subset-sum problems and knapsack cryptosystems

密码学中的利用knapsack
problem的加密。大意就是，你公开一个序列，然后你把你的消息转为二进制，如果你消息的这一位是1，就从你序列中取出对应位置的值，最后密文就是你所有取出的值的和。

但是这样就产生一个问题，加密是加过去了。那该怎么解密呢？

蛮力攻击的时间复杂度是O(2^n),就算中途相遇也只能降低到O(2^(n/2))。太难了。。。

那Alice怎么解决这个问题呢？公钥密码系统如何体现呢？

这就看Alice对序列的选择了。她用的是超递增序列。什么是超递增序列呢？就是后一项≥前一项的两倍，也就意味着，后一项大于前面的所有项之和。

有超递增序列后，给你一个密文，你只需要一项一项对比过来，你就能知道加密者选取的元素是哪几个了。

这不难理解。我们将序列中的每一项放到二进制下就很明显。如果第一项的位长是2，那第二项的位长就至少是3，如果第二项位长是3，那么第三项的位长至少是4。如果你的密文最后是个2位长的，那加密者必定是没有用到第三项，必定是用到了第二项，至于有没有用到第一项，那就看密文减掉第二项之后还有没有剩下来了。【当然，这在每一项只能用一次的大前提下】

###  preparation

Alice准备加密了，首先她先整了一个超递增序列，r = (r1,r2…rn)，然后她生成了两个大数A和B，其中要求B>2rn
也就是B大于这个超递增序列之和啦。然后要需要gcd(A,B)=1，因为之后要求一个A在B下的逆。

###  encryption

Alice要加密了，她先用她的A和她的超递增序列生成一个新的序列M，其中Mi ≡ A·ri mod B

这个新的序列就是Alice的公钥了，她把这个序列甩给Bob，然后Bob按照之前描述的方式，用这个序列和他的明文生成密文S = x·M =
sum{xi·Mi} ，  
然后把这传给Alice

###  decryption

Alice要解密了，她拿到了这个密文S，然后计算

![](https://p5.ssl.qhimg.com/t015ee8aa398f946173.png)

所以这个S’就是密文在超递增序列下的值了，之后再像之前那样判断一下这个S’和序列里面每一项的关系就能解出明文了。【记得从序列大的一端开始判断，如果满足关系别忘了减掉那一项再判断下一项】

伪代码走一波

    
    
    for i in reverse(r):
        if s >= i:
            m = '1' + m
            s -= i
        else:
            m = '0' + m
    

###  table

来个总体流程

![](https://i.loli.net/2020/05/26/7HwAdyNEGqDKLat.png)

###  attention

同RSA一样，这里对参数的选择也要慎重，不然会出现许多出人意料的问题。

具体实例可参考[BJD3rd-knapsack](https://www.anquanke.com/post/id/206493#h3-11)

这里由于对参数A的不当选择，导致序列中较小的项乘以A后并没有被B模掉，也就导致了参数A的泄露。

并且由于这里的超递增序列的生成规则过于简单，只是不断地整除2，所以攻击者能够利用加密后的序列轻易的计算出B来。

###  further more

之前提到Alice最开始整的一个无序的序列，由于这玩意儿没有陷门(trapdoor)，因此这无法成为一个密码系统。但自从有关LLL的paper发表后，基于背包的密码系统出现了一个大weakness，

这里简短的介绍下Eve怎么去解决这个无序序列的背包问题。不管是序列本身无序，还是超递增序列加密后显得无序的序列。

Eve先构造了一个矩阵

![](https://p3.ssl.qhimg.com/t01f1ed21b3a75f594d.png)

其中这个m1,m2,m3…就是那个无序序列，S就是密文

然后Eve从这个矩阵中，将每一条行向量划分出来，分别为V1,V2,…,Vn,Vn+1

我们现在假设向量x = (x1,x2,x3,…,xn) 是明文，(xi = 0 or 1)

那么这个格中就会有这么一条向量

![](https://p1.ssl.qhimg.com/t011934168dbb7da220.png)

这个t，因为2xi – 1 = ±1，所以t的模长是 √n，

根据Minkowskl’s First Theorem,

即对于任意n维满秩格基，都有

![](https://p1.ssl.qhimg.com/t016076bdb94eae1528.png)

显然t是格L中的短向量。

所以，如果Eve知道如何找到lattice中的短向量，那么他就可以完成破解了。

关于找到lattice中短向量的算法我们称之为reduction algorithm，最著名的就是LLL algorithm了，然后它还有变体LLL-BKZ。

###  variant

再刚过去不久的2020RCTF中出现了一道有关knapsack problem 的变体，这里用的不是子集之和，而是子集之积

    
    
    from Cryptodome.Util.number import bytes_to_long, getPrime
    import random
    import hashlib
    
    sr = random.SystemRandom()
    p = getPrime(120)
    num = [sr.randint(1,p-1) for i in range(90)]
    secret = sr.randint(0, 2**90)
    r = 1
    for i in range(90):
        if (secret >> i) & 1:
            r *= num[i]
            r %= p
    
    flag = open("flag.txt","rb").read()
    h = hashlib.sha256(str(secret).encode('utf-8')).digest()
    
    print(p)
    print(num)
    print(r)
    print(bytes_to_long(h)^bytes_to_long(flag))
    

蛮力攻击的时间复杂度是2的90次方，即使是中途相遇攻击的时间复杂度也仍然有2的45次方，于此同时还得考虑2的45次方的空间复杂度。

赛后看了国外大佬hellman的[脚本](https://gist.github.com/hellman/73eaee8c5b905b68badba147bfba6287)才明白了本题的解法。

这一道题的切入点就在于模数p，通过不断地nc，直到获得的模数p具有p-1 smooth的性质（为了方便后面解离散对数），

这个时候再找到一个p的原根，然后对所有的数据利用pohlig算法解一个离散对数，就是开一个log，这样这个子集积的问题就能重新变回子集和的问题了。

    
    
    from sage.all import *
    import ast, sys, subprocess
    import hashlib
    from random import shuffle
    from time import time
    
    #不断nc以获取一个具有p-1 smooth性质的模数p
    while True:
        data = subprocess.check_output("nc 124.156.133.6 22298 </dev/null", shell=True).splitlines()
        p = int(data[0])
        nums = ast.literal_eval(data[1].decode())
        r = int(data[2])
        encflag = int(data[3])
    
    
        fp1 = factor(p-1)
        print("p-1 =", fp1)
    
        if all(d < 2**50 for d, e in fp1):    #判断模数是否具有p-1 smooth的性质
            break
        print("too high factor of p-1")
    
    # 解离散对数问题 -> 将子集积问题转化问子集和
    F = GF(p)
    g = F.primitive_element() #获取原根g
    es = []
    for num in nums:
        e = F(num).log(g)    #以原根为底数开log，因为循环群中所有的数都能以原根的整数幂次来表示
        print(num, "->", e)
        es.append(e)
    
    r = F(r).log(g)
    nums = es
    mod = p - 1
    
    #利用LLL解决0-1背包问题
    N = 90
    
    nums0 = nums[::]
    
    BS = 30
    
    itr = 0
    while True:
        itr += 1
        print(itr, "BS", BS)
        t0 = time()
    
        nums = nums0[::]
        shuffle(nums)
    
        h = QQ(1)/2
        #  n1 1 0 0 0 0
        #  n2 0 1 0 0 0
        #  n3 0 0 1 0 0
        #  n4 0 0 0 1 0 
        #   r h h h h h
        # mod 0 0 0 0 0
        m = matrix(QQ, N+2, N+2)
        m.set_column(0, nums + [r, mod])
        m.set_row(N, [r] + [h] * (N+1))
        m[:N,1:N+1] = identity_matrix(N)
    
        m.set_column(0, 50*m.column(0))
    
        ml = (m*2).change_ring(ZZ).BKZ(block_size=BS)
        print("time %.3fs" % (time() - t0))
    
        for irow, row in enumerate(ml):
            if not (-1 <= min(row[:-1]) < max(row[:-1]) <= 1):
                continue
            if row[-1] < 0:
                row = -row
            print("GOOD", irow)
            secret = 0
            for i in range(N):
                if row[1+i] < 0:
                    secret |= 1 << nums0.index(nums[i])
            print("secret", secret, "=", hex(secret))
    
            h = hashlib.sha256(str(secret).encode('utf-8')).digest()
            h = int.from_bytes(h, "big")
            flag = encflag ^ h
            print(int(flag).to_bytes(100, "big").strip(b"x00"))
            quit()
    
    # RCTF{M4th_0f_MuLLLtiplication_2333}
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **V** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/207798](/post/id/207798)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [密码学](/tag/密码学)

 **+1** __4赞

 __收藏

![](https://p2.ssl.qhimg.com/t013485e4462a9b3b6d.png) V

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


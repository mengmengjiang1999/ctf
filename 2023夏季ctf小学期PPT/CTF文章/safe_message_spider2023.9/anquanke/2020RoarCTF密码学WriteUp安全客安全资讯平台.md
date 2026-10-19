# 2020 RoarCTF 密码学 Write Up

阅读量 **329026**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-10 10:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t015addbfc1a6874e7b.jpg)

这次比赛密码学一共有四题，除了EZRSA真的比较easy，其他题还是有一些做头
，尤其最后一道ECDSA个人感觉出的挺不错的，想了还挺久的，做题的时候思维有点跳不出来，还是太菜了。

先来两道RSA

## EZRSA

    
    
    from Crypto.Util.number import *
    from gmpy2 import *
    from secret import *
    
    assert(flag.startwith('flag{')) and (flag.endwith('}'))
    assert(is_prime(beta) and len(bin(beta)[2:]) == 512) 
    assert(len(bin(x)[2:]) == len(bin(y)[2:]))
    # This is tip!!!
    assert(tip == 2*x*y*beta + x + y)
    
    p = 2*x*beta + 1
    q = 2*y*beta + 1
    
    assert(is_prime(p) and is_prime(q))
    
    n = p*q
    e = 65537
    m = bytes_to_long(flag)
    enc = powmod(m,e,n)   
    
    #n = 
    #beta = 
    #e =
    

题目提供了n，beta，e

这道题意思很明确了，n = p * q = 4xybeta ^ 2 + 2(x+y )beta + 1

很自然的能得到 tip = (n-1)//beta

然后我们给tip模上beta，我们就能得到 (x+y)%beta ，如果我们能够获得x + y，那么显然我们也能获得x *
y，然后解个方程即可获得x和y，然后就能获得p和q，继而解密rsa得到flag

那么对于获得 x + y这个问题，由于beta是512位，我们去看一下n的位数为 2068，那么平均一下p的位数就是1034了，那么x的位数大概就是1034
– 1 – 512 = 521，x + y 估计也就是522位左右，和beta位数差了10位左右，完全是可以暴力的范围

参考脚本

    
    
    n =
    e = 65537
    enc = 
    beta =
    tip = (n-1)//(2*beta)
    for i in range(10000):
        #获取x + y的值
        x_add_y = tip % beta + beta*i
    
        #根据x + y 获取 x * y
        x_mul_y = (tip - x_add_y)//(2*beta)
        try:
            if iroot(x_add_y**2 - 4*x_mul_y,2)[1]:
                #解方程获取x 和 y
                y = (x_add_y - iroot(x_add_y**2 - 4*x_mul_y,2)[0] )//2
                x = x_add_y - y
                p = 2*y*beta + 1
                q = 2*x*beta + 1
                phi = (p-1)*(q-1)
                d = inverse(e,int(phi))
                print long_to_bytes(pow(enc,d,n))
        except:
            pass
    

## reverse

    
    
    from Crypto.Util.number import *
    from gmpy2 import *
    from secret import *
    
    assert(flag.decode().startswith('flag{')) and (flag.decode().endswith('}'))
    def reverse(x):
        y = 0
        while x != 0:
            y = y*2 + x%2
            x = x // 2
        return y
    
    
    while True:
        p = getStrongPrime(512)
        q = reverse(p)
        if is_prime(q):
            break
    
    n = p*q
    e = 65537
    m = bytes_to_long(flag)
    enc = powmod(m,e,n)
    
    #n = 
    #enc =
    

这一道题就是一个正常的RSA，但是生成的p和q再二进制上是相反的，即若p是11（0b1011），那么q就是13（0b1101）

其实有点像一个算法题，我们可以通过测试得知，如果p * q = n ，那么p的最低位 乘以 q的最低为 等于 n
的最低为，基于这个事实，我们可以从最低位一位一位爆破p和q，但是实际操作后会发现，可能性太多，无法剪枝，那么复杂度过高的情况下这种做法是不可取的。

所以我们在以上的基础再加一个判断：

由于我们知道 p的高位是q的低位，那么我们将p反过来然后末尾补0，补齐512位，这个肯定会比真真的q小，同理将q反过来末尾补0，这样子我们可以得到p_min
和 q_min，那么p_min * q_min 肯定是小于 n的，如果p_min * q_min > n，那么就可以舍弃这个可能性。

同理末尾补1就能得到p_max 和 q_max ，如果p_max * q_max < n 那么这种可能行也可以舍弃

参考代码

    
    
    from Crypto.Util.number import *
    from gmpy2 import *
    from itertools import product
    
    n = 158985980192501034004997692253209315116841431063210516613522548452327355222295231366801286879768949611058043390843949610463241574886852164907094966008463721486557469253652940169060186477803255769516068561042756903927308078335838348784208212701919950712557406983012026654876481867000537670622886437968839524889
    ct = 103728452309804750381455306214814700768557462686461157761076359181984554990431665209165298725569861567865645228742739676539208228770740802323555281253638825837621845841771677911598039696705908004858472132222470347720085501572979109563593281375095145984000628623881592799662103680478967594601571867412886606745
    
    max_idx = 1
    
    pq_list = [(1,1)]
    
    for idx in range(1, 512):
        mod = 2 ** (idx + 1)
        new_pq_list = []
    
        for p, q in pq_list:
            for i, j in product(range(2), repeat=2):
                np = i * 2 ** idx + p
                nq = j * 2 ** idx + q
    
                #judge1
                if (np * nq) % mod != n % mod:
                    continue
    
                #judge2
                rp_min = int('{:b}'.format(np)[::-1].ljust(512, '0'), 2)
                rq_min = int('{:b}'.format(nq)[::-1].ljust(512, '0'), 2)
                rp_max = int('{:b}'.format(np)[::-1].ljust(512, '1'), 2)
                rq_max = int('{:b}'.format(nq)[::-1].ljust(512, '1'), 2)
    
                if n < rp_min * rq_min or rp_max * rq_max < n:
                    continue
    
                #可能性集合
                new_pq_list.append((np, nq))
    
        print(len(new_pq_list))
        print(idx)
    
        pq_list = new_pq_list
    

运行代码大概要个十多分钟。然后可能性集合能达到快二十万，我们遍历这个集合，找到其中的两个512位素数即为p和q，进而RSA解密即可。

然后是两个需要交互的题目，给的是Crypto_System，一个给了源码， 一个没给，但两道题核心都是构造一个等式然后解方程。先来看看这个给了源码的。

## Crypto_System

    
    
    # These three are constants
    p = 12039102490128509125925019010000012423515617235219127649182470182570195018265927223
    g = 10729072579307052184848302322451332192456229619044181105063011741516558110216720725
    
    # random generation
    m1 = "test1"
    m2 = "test2"
    
    # Initialization
    r1, s1 = sign(m1)
    # r1 will be provided to player
    
    def int2str(data, mode="big"):
        if mode == "little":
            return sum([ord(data[_]) * 2 ** (8 * _) for _ in range(len(data))])
        elif mode == "big":
            return sum([ord(data[::-1][_]) * 2 ** (8 * _) for _ in range(len(data))])
    
    def get_parameter(m):
        x = int2str(m, 'little')
        y = powmod(g, x, p)
        a = bytes_to_long(hashlib.sha256(long_to_bytes(y).rjust(128, "\0")).digest())
        b = powmod(a, a, p - 1)
        h = powmod(g, b, p)
    
        return y, h, b
    
    def sign(m):
        y, h, b = get_parameter(m)
        r = getStrongPrime(512)
        s = (y * powmod(h, r, p)) % p 
    
        return str(r),str(s)
    
    def verify(m, r, s):
        y, h, b = get_parameter(m)
        if s == ((y * powmod(h, r, p)) % p):
            return True
        else:
            return False
    
    # Give me the (r2,s2)
    if r2 != r1 and s2 == s1 and verify(m2, r2, s2):
        print("Congratulation!Here is your flag: %s" % flag)
    

这道题的他会提供两个msg，然后你需要给他们签名，要求是，签名中两者的s相等，但是r不相等

我们提取一下信息，

签名的验证是 s == ((y * powmod(h, r, p)) % p)

其中 x 就是要被签名的信息， y = powmod(g, x, p)， h = powmod(g, b, p) ， b = powmod(a, a, p
– 1) ，

a = bytes_to_long(hashlib.sha256(long_to_bytes(y).rjust(128, “\0”)).digest())
,显得挺麻烦，但是由于我们是知道参数x, g,
p的，因此y是一个已知的常数，从而a也可以看成一个已知常数即可，继而b、h也会是一个已知常数。（全都已知，完全不用管了）

那么s = powmod(g, x, p) * powmod(powmod(g, b, p), r, p)) == powmod(g, x + br, p)

我们要给不同的x，有着相同的s和不同的r，那么可以构造我们的目标等式： powmod(g, x1 + b1r1, p) == powmod(g, x2 +
b2r2, p)

很自然的我们可以把这个方程转化为 x1 + b1r1 == x2 + b2r2，由于模数p，那么g应该是一个原根叭。那么阶就是p – 1了，所以完整的应该是
x1 + b1r1 ≡ x2 + b2r2 （mod p – 1 ） 固定r1，那么有r2 = (x1 + b1r1 – x2) * inverse(b2
, p-1)，

这里会有一个问题，就是b2 和 p –
1不互素怎么办？撞就完事了，由于决定b2的是msg2，每次连接msg2都是随机的，所以撞就完事，经过测试，互素的概率还是蛮高的。

或者也可以提前将方程两边整除b2 和 p – 1的公因数，但如果没法整除，那就GG了，还是撞叭23333

参考脚本

    
    
    from pwn import *
    from Crypto.Util.number import *
    sh=remote("139.129.98.9","30001")
    from pwnlib.util.iters import mbruteforce
    from hashlib import sha256
    import hashlib
    from math import gcd
    context.log_level = 'debug'
    def proof_of_work(sh):
        sh.recvuntil("XXXX+")
        suffix = sh.recvuntil(')').decode("utf8")[:-1]
        log.success(suffix)
        sh.recvuntil("== ")
        cipher = sh.recvline().strip().decode("utf8")
        proof = mbruteforce(lambda x: sha256((x + suffix).encode()).hexdigest() ==  cipher, string.ascii_letters + string.digits, length=4, method='fixed')
        sh.sendlineafter("Give me XXXX:", proof)
    
    proof_of_work(sh)
    sh.interactive()
    
    # These three are constants
    p = 12039102490128509125925019010000012423515617235219127649182470182570195018265927223
    g = 10729072579307052184848302322451332192456229619044181105063011741516558110216720725
    
    
    def int2str(data, mode="big"):
        if mode == "little":
            return sum([ord(data[_]) * 2 ** (8 * _) for _ in range(len(data))])
        elif mode == "big":
            return sum([ord(data[::-1][_]) * 2 ** (8 * _) for _ in range(len(data))])
    
    def get_parameter(m):
        x = int2str(m, 'little')
        y = pow(g, x, p)
        a = bytes_to_long(hashlib.sha256(long_to_bytes(y).rjust(128, b"\0")).digest())
        b = pow(a, a, p - 1)
        h = pow(g, b, p)
    
        return y, h, b
    
    def sign(m):
        y, h, b = get_parameter(m)
        r = getStrongPrime(512)
        s = (y * powmod(h, r, p)) % p 
    
        return str(r),str(s)
    
    def verify(m, r, s):
        y, h, b = get_parameter(m)
        if s == ((y * powmod(h, r, p)) % p):
            return True
        else:
            return False
    
    sh.recvuntil("Here is the frist message(64 bytes):")
    message1 = bytes.fromhex(sh.recvuntil("\n")[:-1].decode()).decode()
    sh.recvuntil("Here is the second message(64 bytes):")
    message2 = sh.recvuntil("\n")[:-1].decode()
    print("message2",message2)
    message2 = bytes.fromhex(message2).decode()
    
    sh.recvuntil("The frist message's 'r':")
    message1_r = int(sh.recvuntil("\n")[:-1])
    sh.recvuntil("Please choice your options:")
    
    #根据题目获取各个参数
    message1_y, message1_h, message1_b = get_parameter(message1)
    message1_s = (message1_y * pow(message1_h, message1_r, p)) % p
    message2_s = message1_s
    message2_y, message2_h, message2_b = get_parameter(message2)
    
    
    ######################################################
    #解题核心
    #x1+b1r1=x2+b2r2
    
    x1 = int2str(message1, 'little')
    b1 = message1_b
    r1 = message1_r
    x2 = int2str(message2, 'little')
    b2 = message2_b
    tmp = gcd(b2,p-1)
    print(tmp)
    r2 = (((x1+b1*r1-x2)//tmp)*inverse(b2//tmp,p-1))%(p-1)
    
    ######################################################
    
    sh.sendline("3")
    sh.recvuntil("Please give me the (r,s) of the second message:")
    print("("+str(r2)+","+str(message2_s)+")")
    sh.sendline("("+str(r2)+","+str(message2_s)+")")
    sh.interactive()
    

## ECDSA

这道题贼狠，源码都不给，来看一看MENU叭

    
    
    [DEBUG] Received 0xd bytes:
        b'Give me XXXX:'
    [DEBUG] Sent 0x5 bytes:
        b'bwUI\n'
    [DEBUG] Received 0x4f bytes:
        b'Hello,guys!Welcome to my ECC Signature System!I promise no one can exploit it!\n'
    [DEBUG] Received 0x269 bytes:
        b'Howevers if you can exploit it in 10 times,I will give what you want!\n'
        b'Here is the frist message(64 bytes):fipoN9jy/*@~J:] PcZY8{&X!7v+\\duTln_#k(WK^Q2L)<SbM$-V=Ex3Uw|h,%}F\n'
        b'Here is the second message(64 bytes):%wh-(xJ4kR+7<^Zv9,Ol\\Kp/&"FHbc_ D@Y*mSos}V?.#L{!3B8QiP=nqCI[y:X2\n'
        b'Try to calculate the same signature for this two messages~\n'
        b'(((Notice: curve = SECP256k1, hashfunc = sha1)))\n'
        b'\n'
        b'ECC Signature System:\n'
        b'    1. Show your pubkey\n'
        b'    2. Generate new prikey\n'
        b'    3. Update your pubkey\n'
        b'    4. Sign a message\n'
        b'    5. Verify a message\n'
        b'    6. Exploit\n'
        b'    7. Exit\n'
        b'\n'
        b'You have only 10 times to operate!\n'
        b'Please choice your options:'
    

根据题目名这是一个ECDSA的签名系统，完了呢要求是给这他提供的两个msg签名，不仅验证要通过，而且签名还得一样。

先来看看这几个功能，

功能1是显示公钥，（可能要利用）

功能2是重新生成一个私钥，（应该是没用的，没啥意义，生成后就是告诉你更新后的公钥）

功能3是更新你的公钥，你来输入（这个肯定有点用）

功能4是帮你签个名 （也许用得上）

功能5是验证签名 （可以，但没必要）

功能6就是整完了用来获取flag的了。

六个功能一眼看来也就这个功能3可以用了。这里需要一点前置知识（现查就可以了，一样的），就是ECDSA签名的验证规则

这种[资料](https://blog.csdn.net/s_lisheng/article/details/79871341)CSDN一抓一大把。

![](https://i.loli.net/2020/12/07/z9EpbT2FRwQrHkg.png)

最后是判断 v = r，即 X.x = dG.x ,我们可以把验证公式提取出来，也即 es^{-1}G + rs^{-1}Q = dG

注意到由于验证用的是公钥Q，然后题目是提供篡改公钥这个功能的，我们知道ECDSA中Q = kG,
其中k是私钥，那么其实等价于我们是可以篡改私钥的，即我们用自己的私钥去给一个信息签名，完了后把用于验证的公钥给改成我们自己的公钥，验证同样也是可以通过的。那么整个过程系统的私钥都不参与了。

解决了签名验证的问题，剩下来就是解决如何让他们的签名保持一致了。

回到验证公式 es^{-1}G + rs^{-1}Q = dG

其中e是我们的消息，可以看作已知常数，r和s是我们能控制的，G是固定的，Q是公钥，也是我们自己决定，d是签名时用的随机数，整个签名的过程我们都能掌握，自然d也有我们决定，然后d会决定r，因为r
= dG.x， 那么r也就固定下来了，只剩Q和s了。

我们把公式约一约，去掉G后就是 es^{-1} + rs^{-1}k = d => e + rk = ds => s = (e + rk)*d^{-1}

由于两个msg的s要保持一直，那么我们构造的等式就是(e_1 + rk) * d^{-1} = (e_2 + rk) * d^{-1}

很显然啊，因为d不能等于0，这等式不可能成立啊，于是陷入僵局。

但这里我们忘了一个很重要的性质，就是，我们最后验证的是v = r，而r是什么，r = dG.x，我们要知道的是，椭圆曲线是一个关于x轴对称的图形，所以其实
r = -dG.x。华点都发现了，这题就解决了，

等式变为 (e_1 + rk) * d^{-1} = (e_2 + rk) * (-d)^{-1}

化成同余式就是(e_1 + rk) * d^{-1} ≡ (e_2 + rk) * (-d)^{-1} mod{n}

有 e_1 + rk ≡ -e_2 -rk mod{n}

有 k ≡ (-e1-e2) // 2r mod{n}

然后怕【我们去查一下这条曲线的[参数](https://www.secg.org/sec2-v2.pdf)即可

参考脚本

    
    
    from pwn import *
    from Crypto.Util.number import *
    sh=remote("139.129.98.9","30002")
    from pwnlib.util.iters import mbruteforce
    from hashlib import sha256
    import hashlib
    from math import gcd
    context.log_level = 'debug'
    
    a=0
    b=7
    q=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    gx=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    gy=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    order=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    ecc = EllipticCurve(GF(q), [a,b])
    G = ecc(gx,gy)
    
    import hashlib
    
    def sha1(content):
        return hashlib.sha1(content).digest()
    
    
    def proof_of_work(sh):
        sh.recvuntil("XXXX+")
        suffix = sh.recvuntil(')').decode("utf8")[:-1]
        log.success(suffix)
        sh.recvuntil("== ")
        cipher = sh.recvline().strip().decode("utf8")
        proof = mbruteforce(lambda x: sha256((x + suffix).encode()).hexdigest() ==  cipher, string.ascii_letters + string.digits, length=4, method='fixed')
        sh.sendlineafter("Give me XXXX:", proof)
    
    proof_of_work(sh)
    
    sh.recvuntil("Here is the frist message(64 bytes):")
    msg1 = sh.recvuntil("\n")[:-1]
    
    sh.recvuntil("Here is the second message(64 bytes):")
    msg2 = sh.recvuntil("\n")[:-1]
    message = hex(bytes_to_long(msg1))[2:]
    e1=bytes_to_long(sha1(msg1))
    e2=bytes_to_long(sha1(msg2))
    
    ######################################################
    #解题核心
    #pubkey = sh.recvuntil("\n")[:-2].decode()
    #r=[d * G].x
    d=12321
    r=int((d*G)[0])
    new_k = ((-e1-e2)*inverse(2*r,order))%order
    new_Q = new_k * G
    new_S = ((e1 + new_k*r)*inverse(d,order))%order
    newpubkey = hex(new_Q[0]).replace("0x","").rjust(64,"0")+hex(new_Q[1]).replace("0x","").rjust(64,"0")
    newsignature = hex(r).replace("0x","").rjust(64,"0")+hex(new_S).replace("0x","").rjust(64,"0")
    
    ######################################################
    
    sh.recvuntil("Please choice your options:")
    sh.sendline("3")
    sh.recvuntil("Please give me your public_key(hex):")
    sh.sendline(newpubkey)
    
    sh.recvuntil("Please choice your options:")
    sh.sendline("6")
    sh.recvuntil("Please give me the signature(hex) of the frist message:\n")
    sh.sendline(newsignature)
    sh.recvuntil("Please give me the signature(hex) of the second message:\n")
    sh.sendline(newsignature)
    
    sh.interactive()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **V** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/224973](/post/id/224973)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [密码学](/tag/密码学)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t013485e4462a9b3b6d.png) V

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


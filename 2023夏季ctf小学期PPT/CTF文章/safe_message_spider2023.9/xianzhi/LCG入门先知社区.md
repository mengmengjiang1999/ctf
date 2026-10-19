线性同余方法(LCG)是一种产生伪随机数的方法。接下来我会对其进行基础的介绍：![](./img/9021626434974079413.png)

线性同余法最重要的是定义了三个整数，乘数 a、增量 b和模数 m，其中a，b，m是产生器设定的常数。其中 a,b,m 是三个用来生成伪随机数的常量。

举个例子，就是上一个数是 114，设 a=10，b=12，c=514，那么下一个伪随机数就是（114 * 10 + 12）% 514 = 124

下面是常用公式，请牢记并熟练运用：  
![](./img/357256794537338394.png)

用代码简答示例就是：

    
    
    for i in range(10):
        seed = (a*seed+b)%n
    

直接例题如下：

    
    
    # PYTHON 例题一
    from Crypto.Util.number import *
    
    source=b"flag{*********}"
    plaintext=bytes_to_long(source)
    length=plaintext.bit_length()
    a = getPrime(length)
    b = getPrime(length)
    n = getPrime(length)
    seed = 3281857254
    print("seed = ",seed)
    for i in range(10):
        seed = (a*seed+b)%n
    ciphertext = seed^plaintext
    print("a = ",a)
    print("b = ",b)
    print("n = ",n)
    print("c = ",ciphertext)
    # seed =  3281857254
    # a =  540148988578728116547540370955365641360430675811
    # b =  691767495086914115399769389216940791240924902423
    # n =  524988838768493801533758786071154204860765947187
    # c =  210504742144537844110730225465101123460260815127
    

思路:  
想要得到flag就要知道plaintext  
想要得到plaintext只能通过ciphertext = seed ^ plaintex这个表达式推出  
而ciphertext==c我们知道，式子中的seed可以通过他给的初始seed,a,b,n运用算法lcg十次得到  
然后根据异或的特性求解出plaintext，即plaintext = seed ^ ciphertext  
(异或特性，c=a异或b，那么a=b异或c，或者b=a异或c)

那么这题就是非常简单的逆过程计算，仅仅需要的是最后那次迭代出来的seed

    
    
    seed = 33477128523140105764301644224721378964069
    a = 216636540518719887613942270143367229109002078444183475587474655399326769391
    b = 186914533399403414430047931765983818420963789311681346652500920904075344361
    n = 155908129777160236018105193822448288416284495517789603884888599242193844951
    c = 209481865531297761516458182436122824479565806914713408748457524641378381493
    
    for i in range(10):
        seed = (a*seed+b)%n
    # 迭代生成种子值
    
    plaintext=seed^c
    print(long_to_bytes(plaintext))
    

基本情况一：seed = plaintext

那么如果稍稍改动将’seed = 3281857254‘改为‘seed =
plaintext’，也就是将seed与plaintext相互联系起来又会发生什么？

那么求flag相当于求plaintext，求plaintext相当于求初始seed，我们知道lcg算法十次之后的seed=ciphertext=c，而c我们已知，我们还知道a，b，n。所以这道题要我们从lcg十次之后的seed推算出初始seed。

用公式1：Xn=(a-1 (Xn+1 - b))%n，前文已经给出，这里a-1是a相对于模数m的逆元，他也有公式。

    
    
    a =  
    b = 
    n =  
    c =  
    MMI = lambda A, n,s=1,t=0,N=0: (n < 2 and t%N or MMI(n, A%n, t, s-A//n*t, N or n),-1)[n<1] #逆元计算
    ani=MMI(a,n) 
    seed=c
    for i in range(10):
        seed = (ani*(seed-b))%n
    print(long_to_bytes(seed)
    

基本情况二：b = plaintext

求flag相当于求plaintext，plaintext相当于求b，然后在看看我们已知的条件，我们知道a，知道n知道10次lcg中的第n次和第n+1次的结果，所以我们要根据已知的信息求b，用公式3：
**b=(Xn+1 - aXn)%n** 直接求出b

    
    
    a =  
    n =  
    output1 =  
    output2 =  
    b=(output2-a*output1)%n
    plaintext=b
    print(long_to_bytes(plaintext))
    

基本情况三：output.append(seed) 并给出n和output

给了n和10次lcg的output序列，用公式2： **a=((Xn+2-Xn+1)(Xn+1-Xn)-1)%n**
，用已知信息可以求出a，再用a，output序列，n求出b，根据output序列第一个反推出初始seed

    
    
    n =  
    output =  []
    
    MMI = lambda A, n,s=1,t=0,N=0: (n < 2 and t%N or MMI(n, A%n, t, s-A//n*t, N or n),-1)[n<1] #逆元计算
    a=(output[2]-output[1])*MMI((output[1]-output[0]),n)%n
    ani=MMI(a,n)
    b=(output[1]-a*output[0])%n
    seed = (ani*(output[0]-b))%n
    plaintext=seed
    print(long_to_bytes(plaintext))
    

基本情况四：output.append(seed) 仅给出output（即s[]）

用公式4

    
    
    from Crypto.Util.number import *
    def gcd(a,b): 
        if(b==0): 
            return a 
        else: 
            return gcd(b,a%b) 
    s =  []
    t = []
    for i in range(9):
        t.append(s[i]-s[i-1]) 
    all_n = []
    for i in range(7):
        all_n.append(gcd((t[i+1]*t[i-1]-t[i]*t[i]), (t[i+2]*t[i]-t[i+1]*t[i+1]))) 
    
    MMI = lambda A, n,s=1,t=0,N=0: (n < 2 and t%N or MMI(n, A%n, t, s-A//n*t, N or n),-1)[n<1] #逆元计算
    for n in all_n:
        n=abs(n)
        if n==1:
            continue
        a=(s[2]-s[1])*MMI((s[1]-s[0]),n)%n
        ani=MMI(a,n)
        b=(s[1]-a*s[0])%n
        seed = (ani*(s[0]-b))%n
        plaintext=seed
        print(long_to_bytes(plaintext))
    

以上是经常出现的一些LCG算法的基本使用情况，一路下来其实也不难发现无外乎就是公式的应用，就像四道十分基础的数学题一样，用代码来套公式即可，如有解释不到位之处敬请指出。


## 介绍

**加密类300分这道题是有关于RSA生成的质数p和q。题目提供了3个文件，其中mail.msg是RSA加密过的邮件，hitbctf.crt是含有公钥的证书文件，
gen_rsa.py是产生RSA参数的源码。这题网上有一篇老外的writeup，但其中省略了一些步骤，导致我等小白看起来非常费劲。而且老外的代码选择性省略，跑不出最终结果。freebuf上有一篇翻译的文章，跟老外的内容完全一样。本人小白，经过网上各种翻查，终于弄清楚了这题的完整原理。基本思路都是参考老外的文章，在此向原作者致敬！**

##  **参考**

1.<http://www.romainthomas.fr/post/writeup-hitb2015-crypto300/>

2.<http://www.freebuf.com/articles/web/84744.html>

题目的文件在老外的文章中链接，可以自行下载。

##  **原理**

RSA的原理网上的文章很多，请自行搜索。

##  **文件及函数分析**

mail.msg是RSA加密过的邮件，是最终要解密的文件。

hitbctf.crt是含有公钥的证书文件，从中可以获取RSA的参数e、N。

gen_rsa.py是产生RSA参数的源码，从源码中能推导出解题的关键。

gen_rsa.py中有几个函数，功能如下：

 **rabin_miller(num)**

Miller-Rabin素性测试算法判断num是否素数，原理网上很多文章。

 **is_prime(num)**

判断num是否素数。如果是1000以内素数或倍数，则直接返回false。

 **egcd(a,b)**

扩展欧几里得算法求最大公约数。函数返回a和b的最大公约数g和两个数字x、y，其中x和y可以实现g = ax+ by。

 **modinv(a,m)**

从函数名称就能判断是求模反元素的，即乘法逆元，在RSA中就是通过e、N求d。

 **next_prime(n)**

求大于等于n的第一个素数。

 **gen_rsa_parameters()**

首先获取2个随机数，通过next_prime算出2个素数作为e、p。然后求出(p-1）模e的乘法逆元alpha，算出（p *alpha %
e）判处是否素数，如果不是则加e。通过得到的p、q最终求出d。

##  **攻击假想**

根据源程序gen_rsa.py中，假设(p-1)模e的乘法逆元为α，可得2个已知条件：

α *(p − 1) ≡ 1 (mod e)

q = (pα mod e) + k*e

假设N'=N mod e，带入上面的已知条件可得：

N' ≡ p* q (mod e)

≡ p * ((pα mod e) + k *e) (mod e)

≡ p * (pα mod e) (mod e)

≡ p * (pα - j * e) (mod e)

≡ p2α (mod e)  
由于已知条件中有α⋅(p−1) ≡ 1 (mod e)，所以引入p-1分析：

N' ≡ (p - 1 + 1)2α (mod e)  
≡ (p - 1)2α + 2(p - 1)α + α (mod e)

≡ (p - 1) + 2 + α (mod e)

(p - 1) N' ≡ (p - 1)2 + 2(p - 1) + 1 (mod e)

(p - 1)2 - (N' - 2) (p -1) + 1 ≡ 0 (mod e)

令 X = p - 1并假设N' - 2为偶数，所以有N'- 2 = 2b，上面的二次方程可写成：

X2- 2bX + 1 ≡ 0 (mod e)

(X- b)2 - b2 + 1 ≡ 0 (mod e)

(X - b)2 ≡ b2 - 1 (mod e)

上述方程从二次剩余（quadratic residue）能找到解决方案。

![image.png](https://image.3001.net/images/20180717/15318183241466.png)

转换成SageMath的公式就是：  

Np = N % e

b = (Np - 2)/ 2

pp =int(Mod(pow(b, 2) - 1, e).sqrt()) + b + 1

设pp = p % e ，求q：

q= (p * modinv(p - 1, e) % e)

= (pp + ke)* modinv(p - 1, e) % e

= (pp *modinv(p - 1, e)) % e

= (pp *modinv(pp + ke - 1, e)) % e

= (pp *modinv(pp - 1, e)) % e

算出pp后也可以直接通过pp + ke循环测试发现p。老外放弃了这一途径，原因是：I tried to find pp by adding some e
but the distance betweenp and p mod e is huge。个人觉得很奇怪！

##  **实际操作：**

假设N' - 2为偶数（N' = N mod e），很明显本题符合要求。

第一步：从证书文件中获取RSA的参数e和N。方法很多，简单列出2种。

### 方法1：利用openssl可以直接显示

openssl x509 -in hitbctf.crt -text -noout

###
![image.png](https://image.3001.net/images/20180717/15318184499444.png)方法2：通过证书文件生成公钥文件，显示公钥文件的内容  

openssl x509 -outform PEM -in hitbctf.crt -pubkey -noout >public.pem

openssl rsa -pubin -text -modulus -in public.pem

![image.png](https://image.3001.net/images/20180717/15318184663609.png)

需要10进制数的可以利用python的int函数转换：

![image.png](https://image.3001.net/images/20180717/15318184792213.png)

第二步：使用SageMath的数学计算功能，算出正确的pp（p % e）  

e=
21558488234539889837938770635971330903489839146766895224490179041465516193145582266963154883831707522081140734421052039099233464837201660281606980530249

N=162157588231432175750266419709084494256738149198416702818838192688585199555839792754739411546929869488574731499231574687207152393171517768019327338646577588312972543620665360591059281057979460340279244616489314862289312195704820435867259965443285749719682327313893490163672147378911558526315013166594183212229

Np = N % e

b = (Np - 2) / 2

pp = int(Mod(pow(b, 2) - 1, e).sqrt()) + b + 1

pp

![image.png](https://image.3001.net/images/20180717/15318185212110.png)

如果这一步用python中的math.sqrt()计算，结果就不正确了。通过math.sqrt()在计算pp的过程中会丢失精度。举个例子：

![image.png](https://image.3001.net/images/20180717/15318185339817.png)![image.png](https://image.3001.net/images/20180717/15318185403417.png!small)

计算z的平方根的2次方。sage计算还是原来的z，但通过python的math.sqrt计算出来就不是原来的z。

第三步：有2个方法可以计算出p和q

### 方法1：通过pp直接计算p，再得到q

在gen_rsa.py脚本最后加入下列代码运行：

![image.png](https://image.3001.net/images/20180717/15318185658330.png)

### 方法2：通过pp计算出q，在得到p

![image.png](https://image.3001.net/images/20180717/15318185774204.png)

第四步：通过获得的p、q计算出d，生成私钥解密邮件。方法很多，列出2个。

### 方法1：利用rsatools工具

    
    
    python ./rsatools.py -o private.pem \
    
    -e
    
    21558488234539889837938770635971330903489839146766895224490179041465516193145582266963154883831707522081140734421052039099233464837201660281606980530249\
    
    -p 13317713478157317654574552532079837937895228108820477140030796245493222349714497856652987583926206280627498615972491072112647669795345566943409669535038641\
    
    -q12176083266650126897170100375931110708350668494730113414987801764299563774952801449439933220072280766145748279998832962142839152786620322097065894585706069

### 方法2：利用python的 RSA和gmpy2库

    
    
    # -*-coding:utf-8 -*-    
    # 通过p、q和e计算出d，生成私钥文件private.pem
    
    import math 
    
    import sys
    
    import gmpy2
    
    from Crypto.PublicKeyimport RSA 
    
    keypair=RSA.generate(1024) 
    
    keypair.p=13317713478157317654574552532079837937895228108820477140030796245493222349714497856652987583926206280627498615972491072112647669795345566943409669535038641
    
    keypair.q=12176083266650126897170100375931110708350668494730113414987801764299563774952801449439933220072280766145748279998832962142839152786620322097065894585706069
    
    keypair.e=21558488234539889837938770635971330903489839146766895224490179041465516193145582266963154883831707522081140734421052039099233464837201660281606980530249
    
    keypair.n=keypair.p*keypair.q 
    
    Qn=long((keypair.p-1)*(keypair.q-1)) 
    
     phi_n = (keypair.p - 1)* (keypair.q - 1)
    
    keypair.d =gmpy2.invert(keypair.e, phi_n)
    
     private=open('private.pem','w') 
    
    private.write(keypair.exportKey()) 
    
    private.close()

有了私钥文件就简单了，直接用openssl解密获得flag：

    
    
    openssl smime -decrypt-in mail.msg -inkey private.pem
    
    hitb{0b21cc2025534dbd2965390d2bcef45d} 

***本文作者mv371634，转载请注明来自FreeBuf.COM**


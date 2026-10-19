**作者:evilpan  
原文链接：<https://evilpan.com/2020/05/17/ec-crypto/>**

本文主要介绍椭圆曲线的基本原理以及基于椭圆曲线的密码学实现，包括ECC加密、ECDH秘钥交换以及ECDSA签名算法，并介绍其中潜在的一些安全问题。其中分析了两个ECC实现相关的真实案例，分别是索尼PS3的签名问题和美国国家安全局NSA留下的椭圆曲线后门。

# 前言

上周写过一篇[关于RSA实现的介绍文章](https://evilpan.com/2020/05/02/rsa-security/)。相对于RSA对称加密，椭圆曲线加密要复杂得多，以至于多数的介绍文章都难免涉及大量的数学理论和公式。作为一个非密码学专业的业余爱好者，我的目的只是希望对这些概念有个宏观的理解，因此本文会对涉及到的概念在尽量保证正确的前提下进行简化描述。

# 椭圆曲线

作为梦开始的地方，椭圆曲线(Elliptic
Curve)真的只是一个曲线，和其他曲线一样，都是函数在坐标轴中的一个映射。根据mathworld中给出的[椭圆曲线定义](https://mathworld.wolfram.com/EllipticCurve.html)，描述椭圆曲线的函数可以定义如下：

    
    
    y^2 = x^3 + a*x + b 

其中a、b是曲线的特征参数，决定了椭圆曲线的形状。当`43*a^3 + 27*b^2 =
0`时，椭圆曲线退化成奇异曲线，因此不再是合法的椭圆曲线。上述方程的表示方法也称为 _Weierstrass nomal form_
。椭圆曲线在坐标系上的形状参考如下：

![](https://images.seebug.org/content/images/2020/10/ff439391-add9-4185-be1c-774384b6e6d2.png-w331s)

通过观察或者证明都可以得知椭圆曲线是关于x轴对称的。为了理解椭圆曲线，还需要引入一个 **无穷远点** 作为曲线的一部分，也称为理想点，用符号 **0**
表示。椭圆曲线本身比较直观，在不同取值范围中会存在不同的特性，下面会分别进行介绍。

## 实数集

在数学中， **群(Group)** 表示一个特殊的集合，对于集合中的元素我们可以执行二元运算，比如加法(+)。一个集合成为群的前提是需要满足以下4个条件

  1. 封闭性：若a和b属于群G，则a+b也属于群G
  2. 结合性： _(a+b)+c = a+(b+c)_
  3. 存在单位元θ，使得 _a + θ = θ + a = a_
  4. 群中每个元素都存在逆元素，即对于任意元素a存在b，使得 _a + b = θ_

如果集合满足上述条件且满足第5条：

  * 交换律： _a + b = b + a_

那么该集合也称为阿贝尔群(abelian group)。

> _单位元_ ：在二元运算中，单位元与任意元素运算不改变其值，比如实数中加法单位元是0，乘法单位元是1

根据定义，整数集合是一个群(阿贝尔群)，但自然数集合不是一个群，因为不满足第4个条件。

如果一个集合是一个群，那么就可以推导出它也满足其他一些性质，比如单位元唯一性、逆元素唯一性等。

椭圆曲线和群有什么关系？实际上我们可以在椭圆曲线上定义一个群，具体来说：

  * 群的元素是椭圆曲线上的点
  * 单位元是无穷远点0
  * 点P的逆是它关于x轴的对称点
  * 加法的定义为：对于三个同一直线上的非零点P、Q和R，它们的和为 _P+Q+R =0_

用图来表示就是：

![](https://images.seebug.org/content/images/2020/10/ce2b7191-69dc-4b7b-9633-550b80d041ff.png-w331s)

这只是一种几何表示，比如计算P+P，实际上是在P点作一条切线。为了能够进行计算，我们需要将几何加法转换成代数加法，即将上述规则转换为一组方程
。其中涉及到三次方程的解，这里直接给结论，假设P、Q、R的坐标分别是(Px, Py)、(Qx, Qy)、(Rx, Ry)，则：

    
    
    # 直线斜率为m m = (Py - Pq) / (Px - Qx) Rx = m^2 - Px - Qx Ry = Py + m(Rx - Px) 

因此，计算P+Q也就可以在代数上转化为对 _(Rx, -Ry)_ 的计算。

有了加法，自然就可以推出乘法：

    
    
    n * P = P + P + P + ... + P 

其中n是自然数。写成以上形式需要计算n次加法，算法复杂度为O(2^k)，k为n的位宽。实际上可以转换为倍乘相加(double and add)的方式，例如：

    
    
    151 * P = 2^4 * P + 2^2 * P + 2^1 * P + 2^0 * P 

这样可以将算法复杂度减少到O(logn)，或者说O(k)。

有了乘法，自然有除法。给定n和P，我们至少有一种在多项式时间内计算出 _Q=nP_ 的算法。那么反过来，给定Q和P，是否能计算出n呢？这个问题就是我们常说的
**对数问题(logarithm problem)**
。其实这里应该说是除数问题，但大多密码学算法是基于指数计算的，因此求逆称为对数。对数问题求解的时间远大于乘法的计算时间，但连续对数的解存在一些特点，因此并不算是个合格的难题，这里只是引出这个概念，以及我们下面将要看到的真正主角——离散对数问题。

## 有限域

接下来我们将椭圆函数的范围从实数集转到有限集，或者称为有限域(finite field)。
_域(field)*在抽象代数是个专有名词，表示一种支持可进行加减乘除运算的代数结构，并且运算结果不会超出域的集合，其概念是*数域_ 和四则运算的拓展。

有理数集合、实数集合都满足域的概念，如果一个域中的元素个数有限，则成为有限域。有限域一个典型是伽罗瓦域(Galois
Field)，记作GF(p^n)，其中p是素数，n是正整数。p^n也称为有限域的 _阶(order)_ ，即有限域中的元素个数。 _n=1_
时称为素数域GF(p)。

GF(p)元素集合为所有从 _0_ 到 _p-1_
的整数，其加法和乘法可以转换为[模运算](https://en.wikipedia.org/wiki/Modular_arithmetic)，也称为时钟算术，例如对GF(23)：

  * 加法：(18+9) mod 23 = 4
  * 减法：(7-14) mod 23 = 16
  * 乘法：4 * 7 mod 23 = 5
  * 加法逆元：-5 mod 32 = 18
  * (5 + (-5)) mod 23 = (5 + 18) mod 23 = 0
  * 乘法逆元：9^-1 mod 23 = 18
  * 9 * 9^-1 mod 23 = (9 * 18) mod 23 = 1

使用拓展欧几里得算法，我们可以在O(logp)的复杂度内计算出某个数的乘法逆元，这也是除法计算的基础。

在将椭圆曲线的范围限制到有限域中后，椭圆曲线的算式定义也可以做出如下修改：

![](https://images.seebug.org/content/images/2020/10/8cdfa5f5-8abc-4ab2-b54e-6bc4dd7a45a6.png-w331s)

其中 _0_ 依旧是无穷远点，而a、b是有限域集合中的两个整数。对于任意x，最多存在两个点，即两个y的解。

举个例子，对于椭圆曲线 _y^2 ≡ x^3 - 7x + 10 (mod p)_ ，当p的值分别是19、97、127、487时，其在坐标轴上的图像如下：

![](https://images.seebug.org/content/images/2020/10/4d7789ff-6a4b-4d18-9ac6-9fb73b24c4fc.png-w331s)

注意这些点的集合在直角坐标中是关于直线 _y=p/2_
对称的。虽然之前连续的椭圆曲线现在变成了离散的点，但可以证明这些点的集合同样是一个阿贝尔群，因此也满足群的定义和推论。

那么，我们要如何定义和计算这些离散点的 **加法**
呢？与实数集中我们定义几何学上同一直线上的三个点P、Q、R之和为0，有限域中也类似，不过这里的直线并不是实数集中的直线，而是满足 _ax + by + c
≡ 0 (mod p)_ 的点的集合。

举例来说，椭圆曲线 _y^2 ≡ x^3 - x + 3 (mod 127)_ ，且P=(16, 20)，Q=(41,120)。注意连接它们的“直线” _y
≡ 4x + 83 (mod 127)_ 实际上在空间中是重复的：

![](https://images.seebug.org/content/images/2020/10/a23af7b0-6c47-4801-9903-5047f1bfc360.png-w331s)

计算对应几何表示的代数加法和前面类似，不过后面都需要加上(mod p)，这是可以推导出来的。

从加法到乘法同样可以使用倍乘加的算法加速运算，同时对于有限域的椭圆曲线，乘法还有个有趣的特点。例如对于椭圆曲线 _y^2 ≡ x^3 + 2x + 3
(mod 97)_ 和点 P=(3,6)，在计算乘积时发现：

  * 0P = 0
  * 1P = (3,6)
  * 2P = (80,10)
  * 3P = (80,87)
  * 4P = (3, 91)
  * 5P = 0
  * 6P = (3, 6)
  * 7P = (80, 10)
  * …

乘积每5次一个循环，也就是说实际上该点的乘积只有5个可能的值，这个规律可以写成：

    
    
    k * P = (k mod 5) * P 

同时，这5个点本身也是封闭的，即这些点相加也是其中某个点：

    
    
    n * P + m * P = (m + n) * P 

因此， _P的乘积所组成的集合也是一个群_ ，称为 **循环子群** ，P称为该循环子群的生成器(generator)或者 **基点** (base
point)。循环子群是椭圆曲线加密的基础，在后面的章节会进行介绍。

循环子群的元素个数称为该子群的 _阶(order)_ ，比如上述子群的阶为5。通过给定椭圆曲线和基点P我们可以计算出子群的阶。

在椭圆曲线加密中一个常见需求就是找到一个阶比较高的子群。假设椭圆曲线的阶为N，子群的阶为n，想要寻找的基点为P。根据拉格朗日定理 _h = N / n_
总是一个整数，h称为子群的 **余因子** (cofactor)。考虑到椭圆曲线中所有点的和 _NP = 0_ ，我们可以写成：

    
    
    n(hP) = 0 

假设n是一个素数，该等式实际上告诉我们：对于一个随机的点P，以点 _G = hP_
为基点的子群阶的阶为n(当G不为0时，G为0则子群阶为1)。当然该算法也要求n是一个素数，否则G的阶只是n的其中一个除数而已。

介绍完了乘法，最后就让我们来看除法：给定点P和Q，并且 _Q = kP_
，如何求k的值？这个问题就是椭圆曲线的离散对数问题，这个问题是一个公认的难题，目前没有一个多项式时间的求解算法可以计算出来。与大数分解问题类似，这个难题也只是实践上的，并没有严谨的数学证明不可解。

实际的加密系统中，如DSA签名算法、DH秘钥交换算法和ElGamal算法等，使用的是指数形式而不是乘法形式，即已知a和b，求解k以满足 _b = a^k
mod p_ 。椭圆曲线加密相比于RSA加密而言的优点之一是我们只需要更少位数的k就可以获得和RSA相同甚至更高的安全性。

# ECC

ECC(Elliptic Curve
Cryptography)即椭圆曲线加密算法。在上文中我们说了，在有限域中的椭圆曲线乘法(指数)是相对容易计算的，但是除法(对数)则很难计算，这也是椭圆曲线得以实现非对称加密的难题假设和理论基础。

椭圆曲线加密算法主要基于椭圆曲线在有限域中的循环子群，因此定义下面一些参数(domain parameters)：

  * _p_ ：定义了有限域大小的素数
  * _a、b_ ：定义椭圆曲线的特征参数
  * _G_ ：生成循环子群的基点
  * _n_ ：循环子群的阶(order)
  * _h_ ：循环子群的余因子(cofactor)

其中，组成ECC椭圆曲线加密算法的秘钥定义如下：

  * 私钥：一个在 _{1, …, n - 1}_ 范围内的随机数 _d_
  * 公钥：一个椭圆曲线上的点 _H = dG_

就是这么的朴实无华。已知私钥d和G我们可以很容易通过乘法计算出公钥H，但是反过来从公钥计算私钥却要面临离散对数问题。虽然我们可以直接使用这个特性对信息(转换成数字)进行非对称加密，但实践上更多的是使用集成加密方案(IES,
Integrated Encryption
Scheme)，比如[ECIES](https://cryptobook.nakov.com/asymmetric-key-ciphers/ecies-public-key-encryption)混合加密方法和[EEECC](https://cse.unl.edu/~ssamal/crypto/EEECC.pdf) (EC-based ElGamal)方法。

在openssl中使用也是通过ECC私钥生成对称加密的秘钥：

    
    
    openssl ecparam -genkey -param_enc explicit -out priv.pem -name secp256k1 openssl pkeyutl -derive -inkey priv.pem -peerkey RecipientsPublicKey.pem -out SharedSecret.bin 

详见[Command Line Elliptic Curve
Operations](https://wiki.openssl.org/index.php/Command_Line_Elliptic_Curve_Operations)。

## ECDH

DH即 _Diffie–Hellman_ ，是两个提出者的名字， _Whitfield Diffie_ 和 _Martin Hellman_
。ECDH则为DH的其中一个实现，而DH是一个秘钥协商协议。秘钥协商问题可以简化为：如何在通信链路不安全的安全下安全交换秘钥。DH的实现有很多，但本质上也是基于某种不可逆的拆分操作，WiKi中有个比较直观的例子介绍了交换秘钥的过程：

![](https://images.seebug.org/content/images/2020/10/8e2b64a8-6b77-434e-b56a-9918905426fa.png-w331s)

其中所基于的就是颜色混合容易但是分离难的假设，在这个假设前提下，双方可以获得共同的秘钥。注意双方的secret
color是没有暴露在通信链路中的，因此即便被监听或者劫持也无法成功伪造对端进行中间人(MITM)攻击。

回到ECDH的实现上，这里的难题假设自然就是椭圆曲线的离散对数问题。假设通信双方还是Alice和Bob，则ECDH的工作流程为：

  1. Alice和Bob使用同样的椭圆曲线，并分别随机生成它们自己的私钥和公钥，其中Alice的私钥为da，公钥为 **Ha = da * G** ，Bob的私钥和公钥分别为db和Hb；
  2. Alice和Bob在不安全的信道中交换它们的公钥Ha和Hb；
  3. Alice和Bob分别计算自己私钥和收到的对方公钥的乘积，有：

    
    
    Sa = da * Hb = da * (db * G) = db * (da * G) = db * Ha = Sb 

双方计算出了同样的乘积，即为安全的共享秘钥S，这个秘钥就可以用来作为对称加密的秘钥进行后续通信从而保证安全性。中间人通过偷听只能获得双方的公钥，如果它想要在没有私钥的情况下计算出该乘积，就相当于需要解决这么一个问题：给定椭圆曲线上三个点
_P_ 、 _aP_ 和 _bP_ ，如何计算 _abP_ ？这个问题在DH中也称为 _Diffie-Hellman problem_
，即构成安全秘钥交换基石的难题。

## ECDSA

DSA([Digital Signature
Algorithm](https://en.wikipedia.org/wiki/Digital_Signature_Algorithm))即数字签名算法。我们之前介绍RSA的时候说过RSA的签名方法，即对数据进行hash然后将其使用私钥加密，对端公钥解密并成功校验hash可认为数据没有被篡改。使用椭圆曲线实现的数字签名算法则称为ECDSA。

与RSA类似，ECDSA主要针对所校验数据的hash而不是数据本身。不同的是hash结果需要被截断，从而保证hash的位数与 _n_
(子群的阶)的位数相同，截断后的hash同样是一个整数，记为 _z_ 。Alice使用私钥 _da_ 对数据签名的流程如下：

  1. 从 _{1,…,n-1}_ 中随机选取一个整数 _k_
  2. 计算点 _P = kG_
  3. 计算 _r = Px mod n_ (Px为点P的x坐标)
  4. 如果r=0，从新选一个k
  5. 计算 **s = k^-1 (z + r*da) mod n**
  6. 如果s=0，从新选一个k

运算的结果 _(r, s)_ 则为签名。从计算过程中我们可以看到，s是与哈希 _z_ 绑定的，而 _k_ 可以理解为一个临时私钥，用来生成临时公钥 _r_
。

Bob收到签名 _(r, s)_ 后，自己也计算一份数据的哈希 _z_ ， _Ha_ 是Alice的公钥，校验签名的过程如下：

  1. 计算整数 **u1 = s^-1 * z mod n**
  2. 计算整数 **u1 = s^-1 * r mod n**
  3. 计算点 **P = u1 * G + u2 * Ha**
  4. 当 **r = Px mod n** 时，表示签名有效，数据未被篡改。Px为点P的x坐标

说实话我也不是很清楚为什么要搞这么绕，但ECDSA就是这么实现的。

# 安全性

和RSA一样，椭圆曲线加密的安全性根本在于其难题假设的“难度”，一旦这个前提被打破，椭圆曲线的安全性也会在根本上被动摇。打破难题假定的方法有很多，且不去谈量子计算这种未来的可能性，即便聚焦于当下也依然存在。

## 椭圆曲线的选择

我们说椭圆曲线在有限域上的的离散对数问题是个难题，这并不完全正确。前面看到了根据a、b不同，椭圆曲线可能有不同的形状，事实上存在一些类型椭圆曲线，它们的安全性是相当脆弱的。对于这些椭圆曲线，可以使用特殊的算法来高效的求解离散对数问题。

比如，对于所有 _p=hn_
的曲线(有限域的阶等于椭圆曲线的阶)，就受到一种[特殊攻击](http://interact.sagemath.org/edu/2010/414/projects/novotney.pdf)的影响，攻击者可以用一个普通电脑在多项式时间内求解出离散对数问题。

如果我给你一组椭圆曲线参数(domain parameters)，并告诉你说”OMG!
用它”，这时有一种可能性，即我可能已经秘密地找到了一种方法可以快速地对这条曲线求解离散对数。为了解决这个问题，有时候我们额外引入一个参数，即随机数种子S，并用其生成椭圆曲线特征参数a、b或基点G：

    
    
    S = random() H = hash(S) a = f(H) b = g(H) ... 

使用随机种子生成的椭圆曲线可被认为是验证随机的(verified
random)，其中使用hash来生成的参数在密码学中也称为“我的袖子里可没藏东西”数(Nothing-up-my-sleeve number)。

一个生成和校验随机椭圆曲线的标准算法是`ANSI
X9.62`，感兴趣的可以参考[SECG标准](http://www.secg.org/sec1-v2.pdf)中 _Verifiably Random
Curves and Base Point Generators_ 一节。

实践中不会每次生成新的椭圆曲线进行加密，因为我们实际上需要的是一个足够大的素数p以及子群阶n，并确保不含人为的预置。所以一般会根据标准如NIST、SECG中建议的方式去选择预置的曲线和随机数种子S，不同的椭圆曲线有不同的安全性、运算速度和不同的秘钥长度。

例如， **比特币** 使用的椭圆曲线 **secp256k1** 的参数如下：

    
    
    curve = EllipticCurve(    'secp256k1',    # Field characteristic.    p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,    # Curve coefficients.    a=0,    b=7,    # Base point.    g=(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,       0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8),    # Subgroup order.    n=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141,    # Subgroup cofactor.    h=1, ) 

ECC秘钥的长度取决于所使用的椭圆曲线，在大多数系统中，如OpenSSL、OpenSSH和比特币中默认的ECC秘钥长度都是256位。在OpenSSL中预置的曲线可见：

  * https://github.com/openssl/openssl/blob/master/crypto/ec/ec_curve.c

## ECDSA中的k

在生成ECDSA签名时，我们说到要从 _{1, …, n}_ 中随机选择一个整数 _k_
。这个k需要秘密保存，一旦泄露就可能让攻击者找到签名方的私钥。秘密保存不只是不将k泄露给别人，也意味着生成k的随机数生成器不可预测，更进一步地，要求签名方不能使用同样的k来进行所有签名。

只不过使用了相同的k签名，会有什么问题呢？在这个场景中，我们假设攻击者有两份信息的签名 _(r1, s1)_ 和 _(r2,s2)_
，并且计算这两份信息的原始哈希 _z1_ 和 _z2_ ，加上其他已知的椭圆曲线参数(公钥)，攻击方式如下：

  1. 注意到 _r1 = r2_ ，因为 _r = Px mod n_ 且 _P=kG_ ，对两个信息是一样的
  2. _(s1 - s2) mod n = k^-1(z1 - z2) mod n_
  3. 两边同时乘以 _k_ ，则 _k(s1 - s2) mod n = (z1 - z2) mod n_
  4. 两遍同时除 _(s1 - s2)_ ，则 _k = (z1-z2)(s1-s2)^-1 mod n_

最后一个算式中我们可以直接通过两个文件的哈希和签名计算出 _k_ ，得到 _k_ 之后就可以计算出私钥d：

    
    
    s = k^-1(z + r * d) mod n d = r^-1(s*k - z) mod n 

一个现实中的经典案例就是索尼。出于保护目的，PS3只能运行索尼自家ECDSA签名过的游戏，没有索尼签名的游戏或应用无法被PS3的系统加载。但问题是当年索尼的实现是用一个
_同样的k_ 来对所有游戏进行签名的，最终被黑客发现导致了PS3的沦陷。直到现在我们都经常能看到索尼被人用下面这张XKCD的图片进行嘲讽：

![](https://images.seebug.org/content/images/2020/10/e47760f9-3edf-4602-a1e9-60e198945806.png-w331s)

## 离散对数

除了文章中提到的安全陷阱或隐患，实际上也有其他问题会导致椭圆曲线离散对数的难题假设在一定程度上失效(或者变弱)。比如，有一种称为[`baby-step,gaint-step`](https://en.wikipedia.org/wiki/Baby-step_giant-step)的算法可以将求解离散对数的算法和空间复杂度从暴力破解的 _O(p)*降低为*O(√n)_ ，当所选的椭圆曲线子群阶 _n_
相对较小时，这种方式就能将离散对数的计算时间减少到可接受的水平，从而威胁加密的安全性。

同样类似的算法还有[`Pollard's
rho`](https://en.wikipedia.org/wiki/Pollard's_rho_algorithm_for_logarithms)算法，其进一步将求解离散对数的空间复杂度降到
_O(1)_ 。对于一些破解椭圆曲线的比赛，如 _Certicom ecc challenge_
，通常就是使用该算法的变种求解的。目前的[最新记录](https://en.wikipedia.org/wiki/Discrete_logarithm_records)是2016年破解的117.35位通用椭圆曲线离散对数求解，使用FPGA实现并行
_Pollard’s rho_ 算法，用到的算力为64至576个FPGA并行运行6个月时间。

除此之外，其他的攻击方式有：

  * Weil pairing / Tate pairing
  * Semaev-Smart-Satoh-Araki attack
  * Gaudry、Hess、Smart等提出的针对二进制域的度为小约数时的一种求解方法
  * …

# NSA后门

在前一段时间介绍比特币的文章中，说到中本聪的一个特别之处就是他“避开了NSA的椭圆曲线后门”，当时听起来挺神奇的，但对于密码学家而言其实只是个正常的选择。

前面说椭圆曲线标准时提到了NIST，其全称为 _National Institute of Standards and Technology_
，即美国的国家标准技术研究所，负责制定一系列产业统一标准。NIST在2006年颁布了一个标准[NIST SP
800-90A](https://en.wikipedia.org/wiki/NIST_SP_800-90A) (SP表示特别发布)，其标题为
**Recommendation for Random Number Generation Using Deterministic Random Bit
Generators** ，这其实只是一个伪随机数生成器的定义标准，其中涉及了4个伪随机数生成器：

  1. Hash_DRBG：基于hash函数
  2. HMAC_DRBG：基于HMAC
  3. CTR_DRBG：基于块加密
  4. **Dual_EC_DRBG** ：基于椭圆曲线加密

四个随机数生成器都是基于现有的密码学原语(cryptographic
primitives)构建的。但是第4个比较特殊，用现在的俚语来说就是“画风和别人不太一样”，而且运行速度也较其他三个而言要慢几个数量级，之所以存在于NIST标准中的唯一原因是因为这是NSA建议的。

因此，早在该标准发表后不久，就有人提出了质疑。[2006](http://eprint.iacr.org/2006/190)到[2007](http://eprint.iacr.org/2007/048)年之间最早提出的主要观点是认为
_Dual_EC_DRBG_ 这个随机数生成器的输出带有一定的偏好(bias)。

随后，在[2007年8月的CRYPTO大会](http://rump2007.cr.yp.to/15-shumow.pdf)上，研究人员进一步提出了这个随机数生成器中的不合理之处。简单来说，就是
_Dual_EC_DRBG_ 所使用的椭圆曲线是由一系列 **常数**
定义的，这些常数定义在NIST标准的附录中，但完全不知道是从何而来。研究人员提出这些常数和另外一个秘密的常数存在某种联系，如果知道了这个秘密常数，那么就可以通过获取
_Dual_EC_DRBG_ 的32字节输出后预测该随机数生成器所生成的随机数。

然而研究人员并不知道这个秘密常数是什么， _也许_
给出这组椭圆曲线参数的人会知道，也许没人知道。不过这种可能性的存在就足够让人警惕了。值得一提的是NIST在标准的附录中还指出可以通过其他随机数生成器来重新产生常数来替换默认的椭圆曲线参数，但这一步是可选的，实际上大部分Dual_EC_DRBG的实现都不会去额外做这个工作。

在比特币诞生之初，作为密码学专家的中本聪，自然也不会放过这个问题，所以避开这个后门也就理所当然了。

虽然Dual_EC_DRBG饱受质疑，但没有人能拿出实质性的证据，所以很多公司如[RSA
Security](https://en.wikipedia.org/wiki/RSA_Security)仍然使用Dual_EC_DRBG来实现一些加密项目，并表示
_问题不大_ 。直到 _2013年_ ，Edward
Snowden跳了出来。在他披露的文件中显示，NSA曾给过1000万美金给RSA，条件是令其将NSA的随机数生成器设为默认。……所以一切就说得通了。

值得一提的是，除了在标准中留后门，NSA还灵活运用了其他方法，比如网络漏洞利用、网络劫持、和工业界进行py、和其他Agent(如英国的GCHQ)进行py等等……这一系列操作构成了网络行动——`Operation
Bullrun`，感兴趣的可以去进一步了解。

_2015年_ ，NIST发布新版本的标准，默默地去掉了Dual_EC_DRBG。

# 参考文章

  * [Practical Cryptography for Developers](https://cryptobook.nakov.com/)
  * [Elliptic Curve Cryptography: a gentle introduction](https://andrea.corbellini.name/2015/05/17/elliptic-curve-cryptography-a-gentle-introduction/)
  * [一个把玩椭圆曲线的在线网站](https://cdn.rawgit.com/andreacorbellini/ecc/920b29a/interactive/reals-add.html)
  * [ECDSA代码实现示例](https://github.com/andreacorbellini/ecc/blob/master/scripts/ecdsa.py)
  * [Did NSA Put a Secret Backdoor in New Encryption Standard?](https://www.wired.com/2007/11/securitymatters-1115/)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1366/>


**作者:[evilpan](https://evilpan.com)  
原文链接: <https://mp.weixin.qq.com/s/c-GVbyzrdU7RV8qjW0NMIA>**

**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

# 前言

之前写过一篇[对称加密与攻击案例分析](https://evilpan.com/2019/06/02/crypto-attacks/
"对称加密与攻击案例分析")，而对于非对称加密，虽然接触的时间不短了，但一直没有很系统的记录过。因此趁着国庆家里蹲的五天长假，就来好好回顾总结一下。

其实从加密的定语就能看出，对称加密表示通信双方是拥有同样信息的(即信息对称)。信息可以是预共享的秘钥(PSK)，也可以是事先约定的编解码方法(如凯撒密码)。非对称加密则将信息分为两部分，例如秘钥A和秘钥B，通过秘钥A加密的信息可以用秘钥B进行解密，反之通过秘钥B加密的信息也可以通过秘钥A进行解密。通常这对秘钥可以叫做公钥和私钥，公钥对外发布，私钥自己保留，从而在信息不对称的情况下实现加密和认证。

非对称加密的实现方法有很多，大都依赖于难题假设(hardness
assumptions)。基于一个常量时间内被公认不可解的难题，将该问题的答案分为不同因子，组成对应非对称密码学算法的公钥和私钥。例如RSA基于大素数分解问题，(EC)DSA基于离散对数问题等。本文重点关注RSA非对称加密。

# RSA原理

[RSA](https://en.wikipedia.org/wiki/RSA_\(cryptosystem\)
"RSA")应该是最早的公钥加密系统之一了，其名称是三个发明者的名字首字母缩写(Rivest–Shamir–Adleman)。其算法所基于的难题假设是质数分解问题，在此之前先简单介绍一下涉及到的数学基础。

  1. 欧拉函数： _φ(n)_ ，表示小于n的正整数中与n互质的数的数目。如果n能写做两个不同质数 _p_ 和 _q_ 的乘积，那么则有 _φ(n) = (p - 1)(q - 1)_ 。证明：略。

  2. 同余：给定一个正整m，如果两个整数 _a_ 和 _b_ 满足 _(a-b)_ 被 _m_ 整除，那么就称为`a和b对模m同余`，记作 _a≡b(mod m)_ ，其中`≡`是同余符号。同余的两个数有一些有趣的特性，比如反身性、对称性、传递性等等，详见《数论》。

  3. 模逆元：也叫模倒数(modular multiplicative inverse)。整数 _a_ 的模逆元为整数 _x_ ，则满足 _ax≡1(mod m)_ ，其中 _m_ 为模(modulus)。

  4. 欧拉公式：若 _a_ 与 _n_ 互为质数，则满足 **a^φ(n)≡1(mod n)** ，证明：参考拉格朗日定理。

  5. lcm：least common multiple，最小公倍数。

  6. gcd：greatest common devisor，最大公约数。

  7. 互质：co-prime，两个正整数 _a_ 、 _b_ 互质意味着能同时被它们整除的数只有1，即 _gcd(a, b) = 1_

## 秘钥构成

有了上面的数学基础，再来看RSA公私钥的组成和生成过程。秘钥生成主要有以下几步，其实每一步在实践上都有注意事项，这个后面单独说。

  1. 找到两个不同的质数 _p_ 和 _q_

  2. 计算其乘积 _n=pq_

  3. 计算 _φ(n)_ ，由于 _p_ 和 _q_ 是质数，根据欧拉定理得 _φ(n) = lcm(p-1, q-1)_

  4. 选择一个整数 _e_ ，满足 _1 < e < φ(n)_且 _gcd(e, φ(n)) = 1_ ，即 _e_ 和 _φ(n)_ 互质

  5. 计算一个 _e_ 的 **模逆元** _d_ ，对应模为 _φ(n)_ 。计算过程涉及[拓展欧几里得算法](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm "拓展欧几里得算法")和[贝祖恒等式](https://en.wikipedia.org/wiki/B%C3%A9zout%27s_identity "贝祖恒等式")， _d_ 就是其中一个贝祖系数(coefficient)

在上面的数字中挑选出构造非对称加密的元素：

  * 公钥： _(n, e)_
  * 私钥： _(n, d)_

_e_ 和 _d_ 分别是公钥和私钥的核心，这两个数互为模逆元。要想通过公钥 _e_ 推算出私钥 _d_ ，就需要知道 _φ(n)_ ；而计算
_φ(n)=(p-1)(q-1)_ 则需要知道 _p_ 和 _q_ ；公私钥都已知 _n=pq_ ，所以这就是难题假设的关键：当n很大的时候很难计算出对应的
_p_ 和 _q_ 。

## 加密与解密

假设我们有公钥 _(n, e)_ ，需要加密的内容为 _m_ ， _m_ 是个小于 _n_ 的正整数。则密文 _c_ 为：

    
    
    m^e ≡ c (mod n)
    c = m^e mod n

使用模指数运算，即便数字很大也可以很快算出。

对方拥有私钥 _(n, d)_ ，对密文 _c_ 解密可获得明文 _m_ ，方法如下：

    
    
    c^d ≡ (m^e)^d ≡ m (mod n)
    m = c^d mod n

这里值得注意的是，由于明文m是通过模n获取的，所以要求`m<n`，这也是为什么RSA加密有长度限制的原因。

举一个具体的例子，

  1. p = 61, q = 53 
  2. n = 61 x 53 = 3233 
  3. φ(n) = lcm(p-1, q-1) = lcm(60, 52) = 780 
  4. e = 17 
  5. d = 413 

公钥: (n = 3233, e = 17)  
私钥: (n = 3233, d = 413)

加密和解密函数分别为：

    
    
    enc(m) = m^e mod n
    dec(c) = c^d mod n

假设加密的内容为1337，可以用python进行简单的验证：

    
    
    enc(1337) = 1337**17 % 3233 = 1306
    dec(1306) = 1306**413 % 3233 = 1337

感兴趣的可以自己尝试一下。

## 签名和校验

RSA算法除了可以用来进行加密，同样也能用来进行签名。签名的目的是确保发送的信息是由对应私钥的持有者发布的，而且信息没有遇到篡改。公钥签名则使用私钥校验，私钥签名则使用公钥校验，和加密方向类似。

签名所依赖的数学原理是指数的运算规则，对于整数 _h_ ，有：

    
    
    (h^e)^d = h^(e*d) = h^(d*e) = (h^d)^e ≡ h (mod n)

这里的 _h_ 可以是我们所发送信息的哈希值，比如md5或者sha256。因此对于私钥的持有者而言，签名实际上就可以转换为用私钥对hash进行加密的过程。

消息的接收方收到信息以及加密的hash，使用发送者的公钥对签名进行解密，并计算消息的hash，将解密后的值与hash进行比对即可实现校验过程。

# 安全陷阱

回顾上面秘钥构成的一节，有几个地方说得其实有点含糊，比如 **选择**
p、q、e的地方，存在了一定的主观性。只要满足条件，就可以任意选择吗？事实上在有些场景下选择不当也会导致潜在的安全问题。

## 质数选择

我们知道在秘钥生成的第一步就是选择两个 **足够大**
的质数，这两个数都是需要秘密保存的，任何一个数泄露都会导致质数分解的难度假设无效。那么问题来了，多大的数才算够大？这两个数之间的关系会影响难题假设吗？

对于第一个问题，我们可以参考算力增长和近期的挑战情况判断。例如，一个称为YAFU工具可以在20分钟左右分解一个300位的质数，如下：

Bits | Time | Memory used  
---|---|---  
128 | 0.4886 seconds | 0.1 MiB  
192 | 3.9979 seconds | 0.5 MiB  
256 | 103.1746 seconds | 3 MiB  
300 | 1175.7826 seconds | 10.9 MiB  
  
截止至2019年，被分解的最大RSA数有795位，分解使用了900个CPU年的算力。

同时，对应权威机构的建议也是其中一个参考来源，例如NIST或者密码局。根据[NIST](https://csrc.nist.gov/publications/
"NIST")的判断，非对称加密的秘钥强度和对称加密之间有近似的类比关系：

  * 1024位的RSA秘钥强度相当于80位的对称加密秘钥
  * 2048位的RSA秘钥强度相当于112位的对称加密秘钥
  * 3072位的RSA秘钥强度相当于128位的对称加密秘钥

并且[NIST](https://csrc.nist.gov/publications/
"NIST")建议目前的RSA秘钥安全强度是2048位，如果需要工作到2030年之后，就使用3072位的秘钥。

解决了秘钥长度的问题，我们再看 _p_ 和 _q_
以及它们的关系。判断一个数是不是质数(素数)的方法称为[素性测试](https://en.wikipedia.org/wiki/Primality_test
"素性测试")。其中有一些算法可以提高测试速度，比如启发性测试和费马素性测试，后者通常用来在RSA秘钥生成中快速筛选数据。

在[A Method for Obtaining Digital Signatures and Public-Key
Cryptosystems](http://people.csail.mit.edu/rivest/Rsapaper.pdf "A Method for
Obtaining Digital Signatures and Public-Key Cryptosystems")中提出，出于安全性考量， _p_ 和
_q_ 应该 **随机**
选取，而且应该有相似的量级，但是在长度上又有若干位的不同，才能更难被计算机分解。这其实是从实践上考虑的，但也引出了一个问题：什么样的数好分解，什么样的数难分解？只可惜目前并没有明确的结论。也许在数学专家的钻研下，已经有了一种快速分解满足特定条件大数的方法，只不过出于“国家安全”并未公开，这大概也是我们推国密而舍RSA的原因之一吧。

## 私钥指数

私钥指数就是私钥中的 _d_ ，在计算时我们提到这是模逆元算式的 **一个解** 。事实上该算式通常是多解的，那么在这种情况下如何选择呢？正确答案是
**随机** 选择一个解。曾经有过的情况是秘钥生成者为了解密时计算速度更快，选择一个比较小的 _d_ 作为私钥指数。由于模指数运算的时间复杂度是log2(
_d_ )，在模为1024字节的情况下，一个较小的d甚至可以令运算速度提高10倍。

这样看似没怎么影响安全性，但实际上`M. Wiener`提出了一种攻击方法]令这种情况完全破坏了RSA加密的根基。Wiener定理如下：

![](https://images.seebug.org/content/images/2020/05/455ef3cb-d7b1-4c43-9317-7963303943d1.png-w331s)

因此，使用一个过小的私钥指数虽然提升了解密运算速度，但同时也提升了攻击者还原私钥 _d_ 的计算效率。

> 详细的证明过程见: M. Wiener. Cryptanalysis of short RSA secret exponents. IEEE
> Transactions on Information Theory, 36:553-558, 1990。

## 公钥指数

前面秘钥生成的过程中第四步我们说需要选择一个整数 _e_ ，满足 _1 < e < φ(n)_且 _gcd(e, φ(n)) = 1_ ，即 _e_ 和
_φ(n)_ 互质。这个 _e_ 是公钥的重要组成，因此称为公钥指数。

作为一个选择困难症患者，依旧是看到 **选择** 两个字就犯难。既然要求e和φ(n)互质即可，那么我随便选个满足要求的质数不就行了吗，比如 _e=3_
。估计抱有和我同样想法的人不在少数，但这样其实是有问题的，从结论上看会导致攻击者可以在特定情况下较为高效地还原私钥 _d_
，据不完全统计，涉及到的攻击场景有下面这些：

  * Hastad's Broadcast Attack
  * Franklin-Reiter Related Message Attack
  * Coppersmith's Short Pad Attack
  * Partial Key Exposure Attack
  * ...

感兴趣的朋友可以查看文末的参考资料，这里就不展开了。值得一提的是这种情况的危害相对于前面选择过小的私钥指数情形而言相对较轻一些，即便选取了较小的公钥指数，距离成功的攻击也有不少的计算量。现实中私钥指数一般选择`e
= 2^16 + 1 = 65537`就可以很好地防御攻击了，后面在拆解一些现实中的秘钥时也会看到。

## Padding

我们前面所指的加密、解密和签名运算，明文和密文标的都是一个 **整数** ，该整数小于 _n_ 。这种方式叫做plain RSA(Textbook
RSA或裸加密)，在现实中很少直接使用。plain RSA实际上存在许多安全隐患，列举一些如下：

  * 当使用较小的公钥指数 _e_ (比如3)加密较小的明文 _m_ (比如`*m<n^(1/e)*`)时，由于 _m^e_ 严格小于模 _n_ ，因此只要对密文进行 _e_ 方根取整，就可以很容易解密获得明文。

  * 如果同样的明文发送给 _e_ 个以上的接收方，并且接收方的公钥指数 _e_ 相同， _p_ 、 _q_ 不同，那么通过[中国剩余定理(孙子定理)](https://baike.baidu.com/item/%E5%AD%99%E5%AD%90%E5%AE%9A%E7%90%86/2841597 "中国剩余定理\(孙子定理\)")，中间人就可以很容易解密出明文信息。可以参考前面提到的[Coppersmith's Attack](https://en.wikipedia.org/wiki/Coppersmith%27s_Attack "Coppersmith's Attack")。

> 《孙子算经》：有物不知其数，三三数之剩二，五五数之剩三，七七数之剩二。问物几何？

另外最最重要的一点，由于RSA加密本身没有随机数参与，因此是一种确定性加密算法，即同样的明文加密一定会出现同样的密文。从这点来看，裸RSA加密并不是语义安全的。

非语义安全的加密系统，很有可能会受到[Chosen plaintext
attack](https://en.wikipedia.org/wiki/Chosen-plaintext_attack "Chosen
plaintext attack")攻击的影响。举例来说，RSA的一个特性是两个密文的乘积等于对应明文的乘积：

    
    
    m1^e * m2^e ≡ (m1m2)^e (mod n)

如果攻击者想要解密某个特定密文 _c ≡ m^e (mod n)_ ，他可以让私钥持有方去解密一个构造的密文 _c′ ≡ cr^e (mod n)_ ，
_r_ 是攻击者选择的值。由于前面提到的乘积特性，实际上密文 _c'_ 的明文值是 _mr (mod n)_ ，因此如果解密成功，攻击者就可以计算出原本密文
_c_ 的明文 _m_ 。

除了上面介绍的这些，裸加密很存在许多其他隐患。为了缓解这些问题，真实的RSA实现中通常还会在明文加密之前进行一定的填充。填充要求能引入足够的随机性，但是也需要能够方便地对明文进行还原(unpading)。之前对称加密介绍的一种填充`PKCS#5`可以实现后者，但是没有随机性。

`PKCS#1`标准中最初就包含了精心设计的填充方法。虽然是精心设计，但在1998年Bleichenbacher在Crypto会议上对其展示了一种称为[adaptive
chosen ciphertext
attack](https://en.wikipedia.org/wiki/Adaptive_chosen_ciphertext_attack)的攻击方法，两年后在[Eurocrypt](https://en.wikipedia.org/wiki/Eurocrypt)
大会上也有人提出一些潜在的不安全性。这期间`PKCS#1`标准也一直进行修订，比如引入`OAEP`填充方式等。

如果使用过高级语言中封装的RSA加密库，应该也会发现其提供的接口都是可以指定Padding的，比如Python的例子：

    
    
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.Hash import SHA256
    
    def encrypt(key, plainText) 
        pubkey = RSA.importKey(key)
        cipher = PKCS1_OAEP.new(pubkey, hashAlgo=SHA256)
        encrypted = cipher.encrypt(plaintext)
        return base64.b64encode(encrypted)

Java的例子：

    
    
    String decrypt(String privateKeyStr, cipherText) {
      byte[] cipherTextBytes = DatatypeConverter.parseBase64Binary(cipherText);
        byte[] privateKeyBytes = DatatypeConverter.parseBase64Binary(privateKeyStr);
      KeyFactory kf = KeyFactory.getInstance("RSA");
        PKCS8EncodedKeySpec ks = new PKCS8EncodedKeySpec(privateKeyBytes);
        PrivateKey privateKey = kf.generatePrivate(ks);
    
        Cipher c = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding");
        c.init(Cipher.DECRYPT_MODE, privateKey, new OAEPParameterSpec("SHA-256",
            "MGF1", MGF1ParameterSpec.SHA256, PSource.PSpecified.DEFAULT));
        byte[] plainTextBytes = c.doFinal(cipherTextBytes);
        String plainText = new String(plainTextBytes);
      return plainText;
    }

# 基础设施

介绍完了理论，想必很多人也觉得枯燥无味了。诚然，理论与实践结合才是密码学大放异彩的地方，我们日常生活中每天上网用到的`https`，手机系统用到的应用签名、Secure
Boot，各种认证和校验，无不涉及到非对称加密。实践依赖于背后的数学根基，但同时也在易用性和标准化上做了很多工作，在此基础上构建了广泛应用的秘钥基础设施。值得一提的是，这里的基础设施并不是狭义的PKI，而是涉及到的标准和实践，下面会挑一些来进行介绍。

## ASN.1

为了解决高级语言中结构化数据在磁盘、网络中传输后能够进行还原，我们早先有JSON、XML等表示，现在有protobuf、thrift等序列化方法。不过在更早之前就有了跨平台的抽象语法标准ASN.1(Abstract
Syntax Notation One)，ASN.1定义在`X.208`中，提供了标准的IDL接口描述语言，可以用来表示一系列类型和值。

在ASN.1中，类型就是一组值。有些类型包含了有限的值，但是有些类型也可以包含无限的值。ASN.1包含四种类型：

  1. 简单类型，即没有组合的”原子“类型
  2. 结构类型，类型的组合
  3. 标记类型，从其他类型衍生的类型
  4. 其他类型，例如`CHOICE`和`ANY`类型

类型和名称都可以通过赋值符号`::=`进行命名。除了CHIOCE和ANY的每个ASN.1类型都包含一个标记(tag)，tag可以理解成唯一的标识符，当且仅当tag相等时对应类型才相等。tag也有4个种类：

  1. 通用标记(Universal)
  2. 应用标记(Application)
  3. 私有标记(Private)
  4. 上下文标记(Context-Specific)

通用标记是定义在`X.208`中的，具有全局唯一性，其他标记在不同应用中可能会有不同的含义。拥有通用标记的类型大部分是简单类型，如`BIT
STRGING`、`INTEGER`、`IA5String`、`OBJECT
IDENTIFIER`等，也有结构类型如`SEQUENCE`、`SET`等。一个简单的ASN.1文件如下：

    
    
    Person ::= SEQUENCE {
        age INTEGER,
        name OCTETSTRING,
        birth Date, -- 注释：这里的组合类型在下面定义
    }
    Date ::= SEQUENCE {
        year INTEGER,
        month INTEGER,
        day INTEGER
    }

ASN.1仅仅是一个抽象的表示方法，编码方式则定义在`X.209`中。常见的编码实现有：

  * BER：Basic Encoding Rules
  * DER：Distinguished Encoding Rules
  * XER：XML Encoding Rules
  * JER：JSON Encoding Rules
  * ...

编码实现多种多样，和RSA相关的主要是DER编码。DER是BER的一个子集，编码方式为TLV(Type-Length-Value)结构，具体定义在`X.509`标准中。

## X.509

在密码学中，X.509定义了公钥证书的标准(RFC5280)，其最常见的应用场景之一就是HTTPS中的TLS/SSL认证中。公钥证书中包括公钥和身份信息(如域名、组织或个人)，并且是经过签名的。权威认证的签名机构CA([certificate
authority](https://en.wikipedia.org/wiki/Certificate_authority)
)公钥证书预置在我们的浏览器或者操作系统中，因此可以认证签名的有效性。

![](https://images.seebug.org/content/images/2020/05/d3468b9f-8560-457f-b923-45b89693166c.jpg-w331s)

X.509同样使用ASN.1来描述，但经历了多个版本的变化，例如：

  * <https://tools.ietf.org/html/rfc2459#appendix-A>
  * <https://tools.ietf.org/html/rfc3280#appendix-A>
  * <https://tools.ietf.org/html/rfc5280#appendix-A>

>
> 事实上`X.509`是由国际电信联盟(ITU)管理的，权威版本可以在[ITU](https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-X.509-201210-S!!PDF-E&type=items
> "ITU")的网站上看到，同时ITU也提供了[X.509以及对应拓展包的ASN.1压缩包下载](https://www.itu.int/ITU-T/recommendations/rec.aspx?id=4123&showfl=1
> "X.509以及对应拓展包的ASN.1压缩包下载")。

X509中定义了许多字段，列举一些常见的解释一下：

  1. Serial Number：CA所签名的证书都都包含的一个针对该CA的序列号

  2. Subject：主题名称，CA所签名的目标对象标识符，通常使用X.500或者LDAP格式来描述

  3. Issuer：签发者名称，CA本身的标识符。对于自签名的证书而言，Issuer和Subject是相同的，例如根证书

  4. Subject Public Key Info：Subject的公钥信息，包括公钥算法和对应的公钥，例如RSA公钥则包括之前介绍过的模n和公钥指数e的值

  5. Signature：Issuer对Subject公钥证书的签名

  6. Validity period：Issuer对Subject公钥证书签名的有效时间

以B站的的HTTPS证书为例，我们也可以使用openssl查看公钥详细信息：

    
    
    $ openssl s_client -connect bilibili.com:443 -showcerts 2>/dev/null | openssl x509 -noout -text -nameopt multiline,-esc_msb,utf8
    Certificate:
        Data:
            Version: 3 (0x2)
            Serial Number:
                27:6d:f4:81:02:c7:45:53:a7:ee:12:58
        Signature Algorithm: sha256WithRSAEncryption
            Issuer:
                countryName               = BE
                organizationName          = GlobalSign nv-sa
                commonName                = GlobalSign Organization Validation CA - SHA256 - G2
            Validity
                Not Before: Sep 18 09:32:07 2018 GMT
                Not After : Sep 18 09:21:04 2020 GMT
            Subject:
                countryName               = CN
                stateOrProvinceName       = 上海
                localityName              = 上海
                organizationName          = 上海幻电信息科技有限公司
                commonName                = *.bilibili.com
            Subject Public Key Info:
                Public Key Algorithm: rsaEncryption
                    Public-Key: (2048 bit)
                    Modulus:
                        00:da:ce:77:ab:d9:e2:99:25:28:c1:4c:8e:15:ac:
                        22:5a:8a:31:80:0f:20:3b:1d:a9:a6:d2:76:71:25:
                        a0:8b:08:41:31:7a:7f:b9:d3:12:f4:c0:d6:d5:03:
                        bf:7b:e7:56:f2:f0:5b:c4:69:ca:6f:aa:d5:eb:86:
                        a7:06:2f:67:2b:93:d2:70:33:45:40:f7:18:48:68:
                        d4:4f:65:5c:91:7c:aa:64:d4:e2:37:7b:7e:66:83:
                        fe:b3:be:69:20:9b:20:5d:dd:1a:02:0d:53:e8:2a:
                        91:7a:84:c5:12:66:bb:51:6c:c0:40:4a:9d:b5:19:
                        39:35:3a:1d:80:55:7f:b0:85:61:8e:a5:87:24:7c:
                        32:59:35:0d:2c:2e:80:6d:f1:a4:96:1d:12:aa:c9:
                        a6:88:90:15:18:b3:c6:93:8e:49:36:53:20:d7:23:
                        6c:5c:40:4e:23:87:8b:9f:6b:41:d2:52:ac:18:65:
                        d8:6f:d9:a0:43:e6:e9:45:a2:81:e2:7e:f5:8b:0d:
                        91:d2:c0:93:9b:8c:65:18:93:c1:de:1f:f2:82:0c:
                        43:54:17:e9:79:7d:3d:d3:6b:bf:2b:d2:02:8a:93:
                        7c:13:8f:1f:4f:62:81:58:54:81:4f:70:83:57:b0:
                        47:62:1b:81:00:76:3c:46:6d:e7:07:1d:aa:35:5a:
                        c8:f9
                    Exponent: 65537 (0x10001)
            X509v3 extensions:
                X509v3 Key Usage: critical
                    Digital Signature, Key Encipherment
                Authority Information Access:
                    CA Issuers - URI:http://secure.globalsign.com/cacert/gsorganizationvalsha2g2r1.crt
                    OCSP - URI:http://ocsp2.globalsign.com/gsorganizationvalsha2g2
    
                X509v3 Certificate Policies:
                    Policy: 1.3.6.1.4.1.4146.1.20
                      CPS: https://www.globalsign.com/repository/
                    Policy: 2.23.140.1.2.2
    
                X509v3 Basic Constraints:
                    CA:FALSE
                X509v3 Subject Alternative Name:
                    DNS:*.bilibili.com, DNS:bilibili.com
                X509v3 Extended Key Usage:
                    TLS Web Server Authentication, TLS Web Client Authentication
                X509v3 Subject Key Identifier:
                    0D:DB:87:B5:F7:C5:57:18:2B:1F:71:56:19:64:1A:DE:C3:C9:12:06
                X509v3 Authority Key Identifier:
                    keyid:96:DE:61:F1:BD:1C:16:29:53:1C:C0:CC:7D:3B:83:00:40:E6:1A:7C
    
                1.3.6.1.4.1.11129.2.4.2:
                    ...i.g.u..u..Y|..C._..n.V.GV6.J.`....^......e.........F0D. ^.R..~AV|..A.....@..c.......u ... A$MqBP..iY1Jl]c......}..o.p.(.t..v.......X......gp
    .....e.........G0E. s.2...-.*+..!......+Ui..2....j;..!..v..v$-m.R..Z#J. TB....3...7x..Y.v.oSv.1.1.....Q..w.......).....7.....e.........G0E.!....v]W....'.\G.]....B..Hn.c....u. ..Cb.....l0L.-.......O....7.....
        Signature Algorithm: sha256WithRSAEncryption
             35:13:01:e0:20:2c:84:ce:76:c9:91:9f:8e:74:f1:5e:49:0d:
             b9:2d:25:96:ae:e6:87:02:52:ce:0e:d7:64:71:81:8f:30:90:
             85:24:e1:2c:17:9c:78:31:97:c7:e8:c2:b2:3d:fd:b7:b1:41:
             25:94:1b:45:79:d4:33:8c:c0:1b:0c:0d:85:3b:8d:41:eb:0c:
             34:51:54:26:80:e6:a0:d4:ac:75:b3:c9:e9:16:8b:ae:9d:bd:
             2f:9a:2c:a2:29:49:20:aa:53:88:c7:70:64:ea:d6:67:a3:e7:
             c4:48:f1:16:64:a5:7a:6b:93:b0:af:00:ee:1c:5f:8d:d2:07:
             b7:ec:b7:da:1a:d8:e2:07:01:37:e0:78:6a:1c:d7:0d:9b:91:
             f0:7c:36:c6:8e:f2:59:d0:0a:f0:54:a8:db:a3:f5:c3:1a:24:
             03:38:86:b0:37:da:89:c1:70:35:c0:1e:02:a2:65:2a:95:68:
             b1:0e:40:56:0c:82:00:5d:8a:9f:f1:50:d9:ed:4b:43:d9:59:
             c8:70:75:ab:85:37:13:89:09:07:08:81:ca:b2:0a:bd:b9:57:
             52:d0:8d:4e:9c:64:06:4a:87:e3:71:3d:b5:47:91:a1:2d:0f:
             75:46:55:81:ea:a1:31:64:ce:27:c5:59:2e:bf:b5:2c:82:07:
             a2:32:b9:91

可以看到实际中的公钥指数 _e_ 为65537，这里的Modulus即为 _n_
，使用冒号分隔十六进制的方式表示，转换为整数是`0x00dace77d9e2...`，另外如名字所言，X509第三版(v3)包含了可选的拓展选项，对于HTTPS而言最重要的是`Subject
Alternative
Name`，即所认证的域名。其他拓展选项详细说明可以参考[RFC5280](https://tools.ietf.org/html/rfc5280
"RFC5280")的介绍。

# 秘钥分析

最后再来分析几个实际落到我们磁盘上的秘钥结构。

## ssh

对于开发者而言ssh都不会陌生，其除了可以使用密码登录远程服务器，也可以通过私钥登录。使用`ssh-keygen`工具可以直接生成私钥`id_rsa`和公钥`id_rsa.pub`，格式为RSA-2048。先看公钥：

    
    
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDEkBTUATNtj5xzF8S+CXzh+8A3LzTXeHyIZams0g37hAFi1SmYK82QAANxUzypUSZSHTY+WnMjOmNEpqgEmE5MWg3tYp4hK7tSyI2/UYUQu8y9KUPa7dnwYA+gkPWxM4sEu3u3bh6dP6bf/t8u6I1fca4tmiEcIqlq3DRz9YQXwIHr27ld5gHFiyEO6vi1ECtddnz6DKuzpQ6Dj1QNVmCF6N81DXfpmTRmVIZV+vZbfD35f1/iw116jQ5lW5VVF00fz7NqYgdK3KH9TiSexJduXjMczyamrTjotNpWZo98JcltkxJF1vYRPIDgX7rTbOzIV/DiCzgROU3JmacI9lmf evilpan

其中重要的中间的base64，解码后hexdump出来如下：

    
    
    00000000: 0000 0007 7373 682d 7273 6100 0000 0301  ....ssh-rsa.....
    00000010: 0001 0000 0101 00c4 9014 d401 336d 8f9c  ............3m..
    00000020: 7317 c4be 097c e1fb c037 2f34 d778 7c88  s....|...7/4.x|.
    00000030: 65a9 acd2 0dfb 8401 62d5 2998 2bcd 9000  e.......b.).+...
    00000040: 0371 533c a951 2652 1d36 3e5a 7323 3a63  .qS<.Q&R.6>Zs#:c
    00000050: 44a6 a804 984e 4c5a 0ded 629e 212b bb52  D....NLZ..b.!+.R
    00000060: c88d bf51 8510 bbcc bd29 43da edd9 f060  ...Q.....)C....`
    00000070: 0fa0 90f5 b133 8b04 bb7b b76e 1e9d 3fa6  .....3...{.n..?.
    00000080: dffe df2e e88d 5f71 ae2d 9a21 1c22 a96a  ......_q.-.!.".j
    00000090: dc34 73f5 8417 c081 ebdb b95d e601 c58b  .4s........]....
    000000a0: 210e eaf8 b510 2b5d 767c fa0c abb3 a50e  !.....+]v|......
    000000b0: 838f 540d 5660 85e8 df35 0d77 e999 3466  ..T.V`...5.w..4f
    000000c0: 5486 55fa f65b 7c3d f97f 5fe2 c35d 7a8d  T.U..[|=.._..]z.
    000000d0: 0e65 5b95 5517 4d1f cfb3 6a62 074a dca1  .e[.U.M...jb.J..
    000000e0: fd4e 249e c497 6e5e 331c cf26 a6ad 38e8  .N$...n^3..&..8.
    000000f0: b4da 5666 8f7c 25c9 6d93 1245 d6f6 113c  ..Vf.|%.m..E...<
    00000100: 80e0 5fba d36c ecc8 57f0 e20b 3811 394d  .._..l..W...8.9M
    00000110: c999 a708 f659 9f                        .....Y.

这些数据怎么解析呢？查阅`RFC4253`我们可以发现ssh公钥的定义如下：

    
    
    The "ssh-rsa" key format has the following specific encoding:
    
          string    "ssh-rsa"
          mpint     e
          mpint     n

而在`RFC4251`中包含了string和mprint类型的定义：

    
    
    string
    
        [...] They are stored as a uint32 containing its length
        (number of bytes that follow) and zero (= empty string) or more
        bytes that are the value of the string.  Terminating null
        characters are not used. [...]
    
    mpint
    
        Represents multiple precision integers in two's complement format,
        stored as a string, 8 bits per byte, MSB first. [...]

说白了三个字段都是Length-Value格式，转换如下：

    
    
    (4 bytes)   00 00 00 07          = 7
    (7 bytes)   73 73 68 2d 72 73 61 = "ssh-rsa" 字符串
    (4 bytes)   00 00 00 03          = 3
    (3 bytes)   01 00 01             = 65537 (公钥指数e)
    (4 bytes)   00 00 01 01          = 257
    (257 bytes) 00 c4 .. f6 59 9f    = 模n

再看私钥：

    
    
    -----BEGIN OPENSSH PRIVATE KEY-----    b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
    NhAAAAAwEAAQAAAQEAxJAU1AEzbY+ccxfEvgl84fvANy8013h8iGWprNIN+4QBYtUpmCvN
    kAADcVM8qVEmUh02PlpzIzpjRKaoBJhOTFoN7WKeISu7UsiNv1GFELvMvSlD2u3Z8GAPoJ
    ...
    -----END OPENSSH PRIVATE KEY-----
注意这里和网上很多文章说的不太一样了，因为之前ssh-keygen生成的直接是RSA私钥，比如：

    
    
    -----BEGIN RSA PRIVATE KEY-----    MIICXAIBAAKBgQCqGKukO1De7zhZj6+H0qtjTkVxwTCpvKe4eCZ0FPqri0cb2JZfXJ/DgYSF6vUp
    wmJG8wVQZKjeGcjDOL5UlsuusFncCzWBQ7RKNUSesmQRMSGkVb1/3j+skZ6UtW+5u09lHNsj6tQ5
    1s1SPrCBkedbNf0Tp0GbMJDyR4e9T04ZZwIDAQABAoGAFijko56+qGyN8M0RVyaRAXz++xTqHBLh
    ...
    -----END RSA PRIVATE KEY-----
前者是PKCS#1定义的DER编码私钥，在下一节中详细介绍。以前openssh默认是支持`PKCS#1`的，不过现在使用了自己的一套格式，大致布局如下：

    
    
    "openssh-key-v1"0x00    # NULL-terminated "Auth Magic" string
    32-bit length, "none"   # ciphername length and string
    32-bit length, "none"   # kdfname length and string
    32-bit length, nil      # kdf (0 length, no kdf)
    32-bit 0x01             # number of keys, hard-coded to 1 (no length)
    32-bit length, sshpub   # public key in ssh format
        32-bit length, keytype
        32-bit length, pub0
        32-bit length, pub1
    32-bit length for rnd+prv+comment+pad
        64-bit dummy checksum?  # a random 32-bit int, repeated
        32-bit length, keytype  # the private key (including public)
        32-bit length, pub0     # Public Key parts
        32-bit length, pub1
        32-bit length, prv0     # Private Key parts
        ...                     # (number varies by type)
        32-bit length, comment  # comment string
        padding bytes 0x010203  # pad to blocksize (see notes below)

详细关于OpenSSH新的私钥格式详情可以参考：

  1. [The OpenSSH Private Key Format](https://coolaj86.com/articles/the-openssh-private-key-format/)
  2. <https://github.com/openssh/openssh-portable/blob/master/sshkey.c>

## AVB

AVB即`Android Verified
Boot`，是安卓中对系统镜像完整性保护的方案。最近在工作中有对其进行了一点研究，不过这里并不是深入介绍AVB，而只看其中涉及到RSA的秘钥。

在我们自行编译安卓源码(AOSP)时，会发现一系列秘钥：

    
    
    $ ls  build/target/product/security/
    Android.mk  media.x509.pem     shared.pk8       testkey.x509.pem  verity_key
    README      platform.pk8       shared.x509.pem  verity.pk8
    media.pk8   platform.x509.pem  testkey.pk8      verity.x509.pem

每组秘钥分别负责用来对不同的组件进行签名，我们主要看Verified
Boot相关的秘钥`verity`，安卓中使用该秘钥对boot.img进行签名，并自定义了签名的ASN.1格式：

    
    
        AndroidVerifiedBootSignature DEFINITIONS ::=
        BEGIN
            formatVersion ::= INTEGER
            certificate ::= Certificate
            algorithmIdentifier ::= SEQUENCE {
                algorithm OBJECT IDENTIFIER,
                parameters ANY DEFINED BY algorithm OPTIONAL
            }
            authenticatedAttributes ::= SEQUENCE {
                target CHARACTER STRING,
                length INTEGER
            }
            signature ::= OCTET STRING
        END

其中证书`Certificate`类型是在X.509中定义的。

私钥的存储格式有几种常见类型，比如[PKCS#1(RFC3447)](https://tools.ietf.org/html/rfc3447#appendix-A.1
"PKCS#1\(RFC3447\)")和[PKCS#8(RFC5208)](https://tools.ietf.org/html/rfc5208#appendix-A
"PKCS#8\(RFC5208\)")。

例如`PKCS#1`中定义私钥的ASN.1表示如下：

    
    
      Version ::= INTEGER { two-prime(0), multi(1) }
          (CONSTRAINED BY
          {-- version must be multi if otherPrimeInfos present --})
    
      RSAPrivateKey ::= SEQUENCE {
          version           Version,
          modulus           INTEGER,  -- n
          publicExponent    INTEGER,  -- e
          privateExponent   INTEGER,  -- d
          prime1            INTEGER,  -- p
          prime2            INTEGER,  -- q
          exponent1         INTEGER,  -- d mod (p-1)
          exponent2         INTEGER,  -- d mod (q-1)
          coefficient       INTEGER,  -- (inverse of q) mod p
          otherPrimeInfos   OtherPrimeInfos OPTIONAL
      }

一般而言，我们保存的私钥都是der格式，即使用DER对相应的ASN.1定义进行编码。许多高级语言中提供了对应的库函数方便从DER中进行反序列化获取原始数据，比如Python的`from
Crypto.Util.asn1 import DerSequence`。同时也有些在线工具可以方便查看DER的反序列化内容，比如：

  1. <https://lapo.it/asn1js>
  2. <https://asn1.io/asn1playground/>

回到上面的verity私钥，我们将其转换为PKCS#1格式：

    
    
    openssl pkcs8 -nocrypt -in build/target/product/security/verity.pk8 -inform DER

解析对应的字段并将其与上面的ASN.1对比。

    
    
    SEQUENCE (3 elem)
      INTEGER 0
      SEQUENCE (2 elem)
        OBJECT IDENTIFIER 1.2.840.113549.1.1.1 rsaEncryption (PKCS #1)
        NULL
      OCTET STRING (1 elem)
        SEQUENCE (9 elem)
          INTEGER 0
          INTEGER (2048 bit) 294034013011457495254632688690709311939827882765990777183788030470572…
          INTEGER 65537
          INTEGER (2047 bit) 152690229409630177395988743674731983661872870808474054654559379297267…
          INTEGER (1024 bit) 172086361699816285157285992007634379277365906572602995588734914497382…
          INTEGER (1024 bit) 170864216145358483792372871509731496788274625374475577044849125456480…
          INTEGER (1024 bit) 121316723122128141459586606081095008794617691006109580880887598144682…
          INTEGER (1024 bit) 160008079977555979458768333051051332108378146438007378884805916911676…
          INTEGER (1024 bit) 111229147058742660120109027367598084873926761525467238165320120548663…

可以对应RSA秘钥的各个元素：

  * n = 2940340130...
  * e = 65537
  * d = 1526902294...
  * ...

# 后记

本文主要介绍了RSA的基本原理以及常见的安全陷阱，其中大部分的实现隐患出在定义中关于选择的地方，比如对于质数 _p_ 、 _q_ 以及公钥指数 _e_
的选择，在某些情况下选择不当会导致在数学上求解难度骤减；RSA裸加密本身并非语义安全，容易受到CPA攻击。对于现代机器学习而言，通过学习语义从端到端还原明文也不是不可能的事。

除此之外，RSA还存在时序攻击、随机数以及侧信道等潜在威胁没有在文中介绍。即便小心翼翼地按照最佳实践去实现了RSA，也依然有不确定性：大质数分解真的很难吗？这个问题目前并没有确切证伪，只有经验性的结论。有人说`RSA-2048`坚不可摧，对于这点我还是持怀疑态度，不说NSA已经“破解”了RSA，至少对于满足
**某些条件** 的质数，可能存在特别的分解方式，毕竟历史上密码学的后门总是留得猝不及防。

虽然存在不确定性，RSA也已经是当今最为广泛使用的秘钥基础设施根基，所以文章也对常见的实现标准和一些常见秘钥进行了介绍和分析，一方面是对自己学习研究的记录，另一方面也希望能对感兴趣的朋友提供点参考。如果你也对密码学感兴趣，欢迎[加群](https://mp.weixin.qq.com/s/z6mXZtxctud4BCiSG0njxA
"加群")一起交流学习!

# 参考资料

  1. [WikiPedia - RSA cryptosystem](https://en.wikipedia.org/wiki/RSA_\(cryptosystem\) "WikiPedia - RSA cryptosystem")
  2. [A Method for Obtaining Digital Signatures and Public-Key Cryptosystems](http://people.csail.mit.edu/rivest/Rsapaper.pdf "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems")
  3. [Twenty Years of Attacks on the RSA Cryptosystem](http://crypto.stanford.edu/~dabo/abstracts/RSAattack-survey.html "Twenty Years of Attacks on the RSA Cryptosystem")
  4. M. Wiener. Cryptanalysis of short RSA secret exponents. IEEE Transactions on Information Theory, 36:553-558, 1990
  5. [A Layman's Guide to a Subset of ASN.1, BER, and DER](http://crypto.stanford.edu/~dabo/abstracts/RSAattack-survey.html "A Layman's Guide to a Subset of ASN.1, BER, and DER")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1191/>


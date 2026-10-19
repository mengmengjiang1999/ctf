RFID（或者准确说是射频卡）的安全方面，既简单又复杂。简单在于其技术并没有那么复杂，因为算力、硬件限制、历史发展等因素的制约，导致不像蓝牙、WiFi这种有大量应用层的逻辑问题引发的漏洞，因此总结起来问题主要来源于认证和加密；而复杂在于标准、说法、名词众多，因此看不同的文章会有不同的说法，要准确理解并融会贯通还是有一定的难度。

下面我就简单梳理一下近期学习到的关于射频卡的一些基础知识，以及存在的相关攻击方法。

# 基础知识

首先必须将RFID的基础知识说明，或者说将一些名词的定义事先约定， **否则后面的表述会出现歧义，或者难以理解**
。本次参考的一个重点就是Freebuf上两个“神仙”打架的文章，感兴趣的可以去看原文：

[《RFID破解三两事》](https://www.freebuf.com/articles/wireless/8792.html)

[《关于“RFID破解两三事”的一些事》](https://www.freebuf.com/articles/wireless/8858.html)

[《低俗文章之傻傻分不清楚的IC和ID卡》](https://www.freebuf.com/articles/wireless/9451.html)

[《“RFID 破解三两事”讨论总结》](https://www.freebuf.com/articles/wireless/8899.html)

## 名词、定义和概念

### 射频识别（RFID）

首先，先说明RFID的概念。在Wiki-pedia RFID词条下的定义：

>  **R** adio **F** requency **ID**
> entification一种无线通信技术，可以通过无线电信号识别特定目标并读写相关数据，而无需识别系统与特定目标之间建立机械或者光学接触。

所以RFID实际上并不只限于我们日常用的刷卡的“卡”，还有其他比如商品上的射频标签。

### IC卡和ID卡

这两者的关系，也是目前这一领域中争论最多的一个点。

ID卡，即IDentification Card，指的是身份识别卡，一般情况下是不可写入的感应卡，能读出固定的编号。（来源：[百度百科-ID卡](https://baike.baidu.com/item/ID%E5%8D%A1) 词条）

IC卡，是Integrated Circuit Card的简称，即集成电路卡，又称智能卡（详见Wiki-pedia“智能卡”条目）。特点是可读写，容量大，有加密功能，数据记录可靠，使用方便。

### 低频卡和高频卡

这里低频、高频的概念总是容易和IC卡、ID卡有所混淆。很多地方都把ID卡归类为低频卡，IC卡归类为高频卡，实际上这是错误的。

根据百度百科关于ID卡的描述，其工作频率有125KHz和13.56MHz两种不同的频段，因此高频和低频并不是区分ID和IC卡的方式。

RFID卡从空中接口上区分，大致有5种，分别有ISO/IEC制定的标准进行描述，截图来自 Wiki-pedia RFID 词条：

![2019-06-27_105751.png](https://image.3001.net/images/20191225/1577262017_5e031bc102b6c.png!small)

从上表中可以看出，按照ISO给出的标准，卡片工作的频率范围其实有很多， **因此直接从高频和低频对卡片或技术进行区分是不准确的** 。

但是在日常生活中，大家接触到的ID卡一般都是125K的低频卡，而IC卡大多是13.56M的高频卡，因此就形成了固有的印象，认为ID卡都是低频卡，IC卡都是高频卡。

## “白卡”和卡复制

这个实际上是一种攻击手段，在这一节提出是因为一个“神奇的卡片”，被国外人称为”Chinese magic Card”的白卡。

理论上来说，卡片的`序列号`是不可更改的，各种百科和官方文档中也有提到：`卡号在封卡前写入后不可再更改，绝对确保卡号的唯一性和安全性`，但是有人制作了允许对卡片的序列号进行修改的卡片，导致了卡片的序列号非唯一，这也是有“复制卡”出现的原因。

![2019-06-27_120026.png](https://image.3001.net/images/20191225/1577262063_5e031befe9cce.png!small)  

这是某国外的电商网站上出售的复制卡的条目，UID可更换的“Chinese Magic Card”

# 攻击方式

## RFID伪造（卡号复制）

这里说卡号复制，实际上是从传统的ID卡复制而来。但是在实际生活中，对于ID卡和IC卡的使用没有区分的那么明显。以门禁为例，有些门禁就是使用ID卡，去识读卡片的序列号（或者说UID）进行判别；有些门禁会使用IC卡，但是并不在其中的存储扇区写入数据，故读卡器仍旧读取的是序列号。

因此这里统一使用“卡号复制”而不是ID卡复制来避免这一部分的歧义。

由于ID卡在设计之初就是将UID公开、不防护的，因此这部分没有任何的安全机制可言，尤其是出现了可以修改UID的“白卡”。

因为读取到UID即可完成卡片的复制，攻击者可以制作一个功率很大的天线，来延长射频卡的识读距离，可达到30cm甚至更远的距离，且该读取设备可以做的很小而增强便携性，放在手腕、手提包中靠近目标对象从而读取到其卡片信息（详见DefCon
21，RFID hacking live free or RFID hard）。

![2019-06-27_151718.png](https://image.3001.net/images/20191225/1577262079_5e031bff6b7b5.png!small)  

## 数据伪造

对于IC卡来说，卡片中提供了存储的能力。有些卡片中会存储与卡相关的信息，比如卡片余额，或者持有人的信息等。如果可以读出卡片中的数据，并且解析成有意义的字段并修改，然后重新写入卡中，就可以对卡片进行数据的伪造和篡改。

下面所提到的方法，都是关于Mifare Classic这种类型的卡的，其工作频率是13.56 MHz，符合ISO/IEC
14443A标准。常见的Mifare Classic有两种，`MF1 S50`和`MF1 S70`，S50有1K的存储空间，而S70有4K的存储。

### 扇区、块和卡密

Mifare
Classic卡片分为很多个扇区。S50有16个扇区，而S70有40个扇区。S50卡每个扇区分为4个块(Block)，而S70卡的扇区略有区别。两种卡片的存储结构如下图所示，可以看出两种卡的特点和关系：

S50卡的大致结构如下图（来源：[NXP官方文档 - MIFARE Classic EV1
1K](https://www.nxp.com/docs/en/data-sheet/MF1S50YYX_V1.pdf)）![2019-07-01_143104.png](https://image.3001.net/images/20191225/1577262101_5e031c15b865e.png!small)

S70卡的大致结构如下图（来源：[NXP官方文档 - MIFARE Classic EV1
4K](https://www.nxp.com/docs/en/data-sheet/MF1S70YYX_V1.pdf)）

![14883779693311.png](https://image.3001.net/images/20191225/1577262113_5e031c2183e4d.png!small)  

每个扇区的最后一个block是卡密（Key A和Key B）及访问控制字段。相关访问控制比较复杂，具体可以参见官方文档。

 **0扇区的0块是厂商信息** ，包含了卡的UID。一般0扇区0块是不可写的，但是所谓的“白卡”就是0扇区0块可写的卡，是复制卡的基础。

其中，卡密是卡片校验读卡器权限的，其简单的交互流程如下：卡片产生一个随机数发送给读卡器，读卡器需按照算法计算出结果再发送给卡片，由卡片进行验证。验证通过之后，后续的交互都是用卡密进行加密的。借用BlackHat
2014的Slides中的一张图：

![2019-07-01_101637.png](https://image.3001.net/images/20191225/1577262123_5e031c2b412c2.png!small)  

### Nested攻击

因为复制卡只是复制了卡的UID，还需要将卡片扇区的数据都拿出来，因此需要知道每个扇区的卡密，才能读取到内容。引用[Freebuf上的相关文章](https://www.freebuf.com/articles/terminal/128238.html)中的介绍：

> 简单地说，就是默认密码攻击。
>
> 由于M1卡片有16个扇区，在绝大多数情况下16个扇区不一定会同时使用到。于是根据厂商在出厂时预设的密码可能碰撞出其中某一个扇区的密码。
>
>
> 由于无源的M1卡每一次刷卡上电的时候，密钥交换采用的随机数都是“有规律”的，用已经碰撞出的某一扇区的密钥去试探其它扇区，在此时根据随机数的规律即可“套”出密码

根据上述的交互原理可知，想要读取卡片内容，需要知道各个扇区的Key A和Key
B。扇区密钥是48bit，使用FPGA直接暴力破解，可在约10小时的时间内完成。

M1卡片使用的加密方式是Crypto-1，卡片上的硬件实现中，加密用的随机数产生器（RNG）使用了LFSR(Liner Feedback Shift
Register)，其产生的随机数是可预测的。随机数的生成与两个变量相关： **一是读卡器启动的时间，二是请求随机数的时间**
。由于攻击者可以通过操纵这两个时间来预测随机数，导致其通信有被破解的可能性。

下图为CRYPTO-1的硬件结构示意图，来源于Black Hat 2014 演讲中的PPT[1]。

![2019-12-24_094307.png](https://image.3001.net/images/20191225/1577262272_5e031cc0734bd.png!small)  

Courtios等于2009年提出了一种新的破解方法[11]，简单描述为：卡片在识别读卡器发送的认证数据时，会先检查读卡器返回数据校验位是否正确，如果不正确则不返回；当检查通过时，若认证数据错误，则卡片会返回0x5
(NACK)，且该数据是加密的。利用加密数据与0x5进行异或 (XOR) 操作后的数据，可恢复出密钥流中的4bit数据。

在该文献中，作者称该攻击恢复出卡片其中一个扇区的密钥时间在1小时左右。

### Darkside攻击

> 简单地说就是暴力破解，即爆破出某一个扇区的密钥，之后再使用Nested攻击就能Dump出整张卡。
>
> 而与通常意义上的暴力破解不同的是，由于M1卡片的认证机制，其会泄露部分认证信息，从而大大加快爆破的进度。

由于Crypto-1算法中，对扇区密钥的检查依赖于LFSR产生的随机数，因此通过检测和预测随机数可以猜测其他扇区的密钥，并通过认证[12]。其过程如下：

  1. 对某一扇区用默认密钥进行认证，并且读取卡片的Nt；

  2. 对同一扇区用默认密钥进行认证，并且读取卡片的Nt'；

  3. 计算“时间距离”，即LFSR的位移；

  4. 猜测下一个Nt的值，计算ks1, ks2和ks3并且认证下一个扇区。

因此，Nested攻击结合Darkside，可以在很短的时间内破解出M1卡片的密码。

### 算法分析

这其实不能算是RFID的攻击方式，但是很多相关的文章都有提及。实际上，在智能卡的攻击过程中，分析卡中数据的算法、校验等都是必须的过程，只有掌握了数据的构成方式，才能成功的进行数据的篡改。

## Fuzz攻击

这类的攻击主要针对读卡器（Reader）。向读卡器模拟卡片进行数据的交互，给其发送非预期的数据，有可能造成缓冲区溢出等问题，进而可能产生代码执行等后果。

# 总结

从整个大的RFID的方向上来看，其安全性主要在两块：卡复制（包括远程读取）和数据篡改。

由于出现了UID可改写的“白卡”，而且RFID在读取时无需用户授权，因此可能出现未授权的远距离读取并复制的可能。此外，像公交卡、饭卡等，如果使用时仅通过卡中数据进行识别和处理而没有实时与数据库数据校验的话，一旦卡片中的数据被破解，攻击者可以任意伪造数据并写入卡中，造成损失。

因此，在卡片的选择上，如果安全性要求比较高，应该选用CPU卡，而不应继续使用Mifare Classic
1K这种已知漏洞的卡片；其次，在认证卡片时，应增加更多的认证选项，而不是仅识读卡片的UID，比如使用某些扇区的数据进行辅助认证，同时认证卡类型等，避免简单的读取了UID后进行卡片复制。

存储上来说，尽量应该将数据加密后再保存在卡片中，避免明文数据直接存储，尽量增加攻击者对系统算法分析的难度；如有可能，应在刷卡的时候将数据与后台数据库的数据进行比对以提升安全性。

# 参考文献

[1] [Almeida M. Hacking Mifare Classic Cards[J]. blackhat, Sao Paulo,
2014.](https://www.blackhat.com/docs/sp-14/materials/arsenal/sp-14-Almeida-Hacking-MIFARE-Classic-Cards-Slides.pdf)

[2] [Brown F. RFID hacking: Live free or die hard, 2013[J]. Black Hat USA,
2013.](https://media.blackhat.com/us-13/US-13-Brown-RFID-Hacking-Live-Free-or-RFID-Hard-Slides.pdf)

[3] [Mifare Classic 官方说明页面.](https://www.nxp.com/products/identification-security/rfid/mifare-hf/mifare-classic:MC_41863#/)

[4] [低成本安全硬件（二）：RFID on PN532. ya0guang@Freebuf.com,
2017.](https://www.freebuf.com/articles/terminal/128238.html)

[5] [RFID开发之圣诞老人无稽之谈. chown@Freebuf.com,
2012.](https://www.freebuf.com/articles/wireless/6580.html)

[6] [RFID开发之圣诞袜的秘密. chown@Freebuf.com,
2012.](https://www.freebuf.com/articles/wireless/6588.html)

[7] 词条：“RFID”. Wikipedia.

[8] 词条：“Mifare”. Wikipedia.

[9] 词条：“智能卡”. Wikipedia.

[10] [词条：“ID卡”. 百度百科.](https://baike.baidu.com/item/ID%E5%8D%A1)

[11]  Ho G, Leung D, Mishra P, et al. Smart locks: Lessons for securing
commodity internet of things devices[C]//Proceedings of the 11th ACM on Asia
conference on computer and communications security. ACM, 2016: 461-472.

[12] Garcia F D, Van Rossum P, Verdult R, et al. Wirelessly pickpocketing a
Mifare Classic card[C]//2009 30th IEEE Symposium on Security and Privacy.
IEEE, 2009: 3-15.


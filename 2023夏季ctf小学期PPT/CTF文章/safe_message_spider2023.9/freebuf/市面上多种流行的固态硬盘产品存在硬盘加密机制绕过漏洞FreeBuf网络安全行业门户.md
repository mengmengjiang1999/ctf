***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![ssd-header.jpg](https://image.3001.net/images/20181106/1541496509_5be15ebdf3d78.jpg!small)**
**近期，荷兰奈梅亨拉德堡德大学研究人员发现，市面上多种流行的固态硬盘（ SSD
drive）存在加密机制可绕过漏洞，无需密码即可绕过硬盘加密措施，从而获取到硬盘中的数据内容。**

拉德堡德大学研究人员Carlo Meijer 和 Bernard van Gastel，为此还专门发表了一篇论文《[Self-encrypting
deception: weaknesses in the encryption of solid state drives (自我加密欺骗-固态硬盘中的加密缺陷)](https://t.co/UGTsvnFv9Y)，文中详细叙述了他们通过固件修改和接口调试，改变了固态硬盘中的密码验证方式，从而无需密码解密了固态硬盘中的数据信息。

![04.png](https://image.3001.net/images/20181106/1541496220_5be15d9cde9f4.png!small)文中还提及，包括Samsung（三星）和Crucial(英睿达)在内的多种固态硬盘产品，加密机制存在缺陷，未对硬盘数据实现完整加密，可无需密码轻松实现加密机制绕过。

> 全盘加密（FDE，full-disk
> encryption）是硬件级加密，它是自动地将硬盘上的数据转换成一种不能被人理解的形式。只有那些有密钥的人才能“还原”转换。如果没有合适的认证密钥，即使把硬盘移出，安装到另一台机器上，仍然不可获得硬盘上的数据。  
>

## 研究成果

研究人员测试了多款固态硬盘产品，有Crucial MX100, Crucial MX200, Crucial MX300, Samsung 840 EVO,
Samsung 850 EVO, Samsung T3 Portable, 以及 Samsung T5
Portable，这些产品都能通过同样方法绕过加密获取到硬盘中的数据信息。

研究人员表示：我们对多款SSD硬盘固件的全盘加密机制进行了逆向工程分析，理论上来说，硬件设备的安全措施和软件实现类似，或者要强于软件应用，但实际上，我们发现很多种硬件实现产品都存在非常严重的高危安全漏洞，多数测试产品直接不需要任何密钥信息就能对其中的数据信息进行完整的提取恢复。

另外，更糟糕的是，支持硬盘加密的Windows中的 BitLocker 加密软件，在加密固态硬盘之后，也可利用这种漏洞方式实现加密绕过。

## 无需密码获取硬盘数据

为了实现硬盘加密绕过，研究人员根据硬盘的调试端口、ATA安全模式的自加密标准、Opal存储规范应用等特点，采用了一系列的分析测试技术，

目前，这些漏洞已经通过责任披露方式通报给了相关厂商，Crucial(英睿达)已经公布了最新的补丁固件更新，而Samsung（三星）则只发布了针对 T3 和
T5便携版固态硬盘的固件更新，对于非便携版的固态硬盘，三星表示，希望用户尽可能地使用软件加密方式进行代替。

## Crucial MX 100, Crucial MX 200, & Samsung T3 便携版固态硬盘

针对Crucial MX 100, Crucial MX 200, & Samsung T3
便携版固态硬盘，研究人员通过连接其JTAG测试组接口，对其密码验证方式进行了修改，以此实现了对硬盘数据的无需密码访问获取，这样攻击者就能无限制地解锁硬盘。

## Crucial MX300 固态硬盘

Crucial MX300
固态硬盘同样存在一个JTAG调试端口，但它是禁用未开放的。之后，研究人员使用了一种更复杂的手段，来对其固件程序进行了刷新，以此实现了多种操作的可执行，其中就包括了可以解密密钥和使用空密码进行身份验证。

研究人员可通过MASTER PASSWORD CAPABILITY 位来重置密码，而在Crucial
MX300固态硬盘中，研究人员发现，这个字节位竟然是一串空字符串，是的，这个用来加密全硬盘的密钥信息是空的，是一串32个的空字符- 32 0x00 byte
values：

##
![1_U3ZDLuLuPhGCdX7oUSt64A.png](https://image.3001.net/images/20181106/1541496325_5be15e05ef7cb.png!small)Samsung
840 EVO 和 Samsung 850 EVO 固态硬盘

根据ATA安全模式的自加密标准的使用特点，研究人员通过连接JTAG调试端口，配合一种损耗水平问题（wear-level
issue）修改密码验证，对加密密钥进行了恢复，实现了对硬盘加密数据的访问获取。

Samsung 850 EVO 固态硬盘不存在损耗水平问题（wear-level issue），研究人员通过调试端口对其密码验证方式进行了修改。

## 默认的硬盘加密软件 BitLocker 失效

大多数现代的操作系统都提供软件加密，允许用户执行全磁盘加密，其中，Linux、macOS、Android和iOS具备强大的软件加密手段，但Windows上的BitLocker，由于其默认为硬盘加密，因此成为了该固态硬盘加密漏洞的牺牲品。

当使用 BitLocker 对Windows下的硬盘执行加密时，如果操作系统探测到了接入的固态硬盘带有硬件加密机制，则会默认使用BitLocker
执行加密，而这种应用BitLocker加密的硬盘，也存在上述发现的加密绕过漏洞，且在此之前，BitLocker
软件加密方式还没有任何验证过或被披露的密码绕过缺陷。

为了防止BitLocker 对固态硬盘的这种默认加密应用，研究人员建议用户在“计算机配置\管理模板\ Windows组件\
BitLocker驱动器加密\操作系统驱动器”中，禁用一个名为“配置操作系统驱动器基于硬件的加密使用”的组策略。

##
![03.jpg](https://image.3001.net/images/20181106/1541496398_5be15e4e07a16.jpg!small)影响产品

> Crucial(英睿达) MX100, MX200 和 MX300固态硬盘
>
> Samsung T3 和 T5 便携版固态硬盘
>
> Samsung 840 EVO 和 850 EVO 固态硬盘

![05.png](https://image.3001.net/images/20181106/1541496427_5be15e6b1ba77.png!small)
***参考来源：[medium](https://medium.com/asecuritysite-when-bob-met-alice/doh-what-my-encrypted-drive-can-be-unlocked-by-anyone-a495f6653581)/[bleepingcomputer](https://www.bleepingcomputer.com/news/security/flaws-in-popular-ssd-drives-bypass-hardware-disk-encryption/)，clouds编译，转载请注明来自FreeBuf.COM**  


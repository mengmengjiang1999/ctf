6月底，Avast发布Akira解密工具。Akira出现于2023年3月，作者称能入侵教育、金融、房产等各行业组织。

Akira是用 C++ 编写的64 位 Windows 二进制文件，并用Boost库实现异步加密。该二进制文件由 Microsoft Linker
14.35 版本链接。

2023 年 6 月，安全研究人员 rivitna 发布了一个针对 Linux 的样本。

## Akira的加密模式

Akira运行后通过[CryptGenRandom()](https://learn.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptgenrandom)生成对称加密密钥，CryptGenRandom() 是 Windows CryptoAPI 实现的随机数生成器。文件由
Chacha 2008（[D. J. Bernstein](https://cr.yp.to/chacha.html)）加密。

对称密钥由 RSA-4096 加密并附加到加密文件末尾。公钥被硬编码在勒索软件二进制文件中，且每个样本都不同。

### 文件排除列表

在观察Akira加密文件时，我们发现Akira有一个不加密的文件列表（一般勒索软件都有一个要加密的列表）：

  * .exe
  * .dll
  * .lnk
  * .sys
  * .msi
  * akira_readme.txt

此外，还有一些文件夹会被 Akira 忽略：

  * winnt
  * temp
  * thumb
  * $Recycle.Bin
  * $RECYCLE.BIN
  * System Volume Information
  * Boot
  * Windows
  * Trend Micro

其中甚至有旧版的 winnt 文件夹（Windows 2000 安装的默认文件夹）。

### 小文件的加密方案

文件加密方式根据文件大小执行。对于 2,000,000 字节及以下的文件，勒索软件会加密文件的前半部分。结构如下：

Block类型

|

文件大小  
  
---|---  
  
Encrypted Block

|

文件大小 / 2  
  
Plain Text Block

|

文件大小/ 2  
  
File Footer

|

534 bytes  
  
### 大文件的加密方案

对于大于 2,000,000 字节的文件，Akira 会加密四个块。首先，计算整个块的大小（见图 1）。

![](https://image.3001.net/images/20230712/1689141587_64ae4153016b5e47d9041.png!small)

然后计算块的加密部分的大小（参见图 2）。

![](https://image.3001.net/images/20230712/1689141611_64ae416b78b21abb33d16.png!small)

然后设计加密部分（参见图 3）。

Block类型

|

大小  
  
---|---  
  
Encrypted Block #1

|

EncryptedLength加密长度  
  
Plain Text Block

|

BlockLength – EncryptedLength块长度-加密长度  
  
Encrypted Block #2

|

EncryptedLength  
  
Plain Text Block

|

BlockLength – EncryptedLength  
  
Encrypted Block #3

|

EncryptedLength  
  
Plain Text Block

|

BlockLength – EncryptedLength  
  
Encrypted Block #4

|

EncryptedLength  
  
Plain Text Block

|

Rest of the file文件剩余部分  
  
File Footer

|

534 bytes  
  
图 3：加密文件设计

file footer的结构用C语言描述如下：

![1689141637_64ae4185c77cf7ebd640a.png!small?1689141637627](https://image.3001.net/images/20230712/1689141637_64ae4185c77cf7ebd640a.png!small?1689141637627)

图 4：file footer加密结构

加密文件可以通过文件扩展名 .akira 来识别。每个文件夹中都会放置一个名为 akira_readme.txt的文件（见图 5）。

![1689141654_64ae41964ea9f4000bd15.png!small?1689141654081](https://image.3001.net/images/20230712/1689141654_64ae41964ea9f4000bd15.png!small?1689141654081)

图 5：Akira 勒索信

勒索信中提到了两个 TOR 站点。第一个站点（图6）罗列了已经被黑的组织；第二个站点写着如何付赎金（图 7）。

![1689141663_64ae419ff242a9fd8d0a5.png!small?1689141664094](https://image.3001.net/images/20230712/1689141663_64ae419ff242a9fd8d0a5.png!small?1689141664094)

图 6：已受害公司

![1689141672_64ae41a8d16e25ba5a5d8.png!small?1689141672663](https://image.3001.net/images/20230712/1689141672_64ae41a8d16e25ba5a5d8.png!small?1689141672663)

图 7：赎金支付说明

### Linux 版本的 Akira

Linux 版本的工作原理与 Windows
版本相同。加密文件具有相同的扩展名和相同的加密模式，并用Crypto++库来覆盖Windows中CryptoAPI处理的部分。

Avast称目前正在研发Linux
版本的解密工具。同时，Windows版本的解密器也可用于解密Linux版本加密的文件，需要使用WINE层在Linux中运行解密器。

### 与Conti相似之处

Akira 与 Conti v2 有一些相似之处，说明Akira作者可能受到了泄露的 Conti 源代码的启发。共同点包括：

  1. 文件类型排除列表类似
  2. 目录排除列表相似：Akira 会忽略与 Conti 相同的文件夹，包括 winnt 和 Trend Micro，因而Trend Micro 的默认安装文件夹对这两种勒索软件病毒天然免疫。
  3. Akira文件尾部结构等于Conti附加的文件尾部（见图8）

![1689141704_64ae41c83c663fb3cc0d7.png!small?1689141703927](https://image.3001.net/images/20230712/1689141704_64ae41c83c663fb3cc0d7.png!small?1689141703927)

图 8：Conti 勒索软件文件尾部

变量bEncryptType被Conti版本2设置为0x24、0x25、0x26，Akira使用0x32。

  4. Akira采用的 ChaCha 2008 的实现与 Conti的实现相同。
  5. 密钥生成代码（两次调用 CryptGenRandom，然后调用 CryptEncrypt）类似于 Conti 的密钥生成函数。

## 如何使用Avast解密工具

工具下载链接：<https://files.avast.com/files/decryptor/avast_decryptor_akira64.exe>

1\. 下载解密器。 Avast 提供了 64 位解密器，因为勒索软件也是 64 位的，无法在 32 位 Windows 上运行。

运行可执行文件，最好以管理员身份运行。根据引导完成解密过程的配置。

2\. 准备好开始后，点击“Next”。

![1689141731_64ae41e3f1a7ad1e4ddf4.png!small?1689141731938](https://image.3001.net/images/20230712/1689141731_64ae41e3f1a7ad1e4ddf4.png!small?1689141731938)

3\. 选择要搜索和解密的位置列表。默认情况下，它会出现所有本地驱动列表。

![1689141772_64ae420c595363ed9a55e.png!small?1689141772243](https://image.3001.net/images/20230712/1689141772_64ae420c595363ed9a55e.png!small?1689141772243)

4\. 提供原始形式的文件示例以及由 Akira 勒索软件加密的文件示例。键入两个文件名称。也可以将文件从 Windows 资源管理器拖放到向导页面。

尽量选择大文件。由于 Akira 块大小计算方式，即使只差 1 个字节的两个文件，大小限制也可能存在巨大差异。

点击“Next”，解密工具会仔细检查文件对并显示最大的可解密文件是什么。一般来说，大小限制应该与原始文件的大小相同。

![1689141825_64ae42419345c05365f53.png!small?1689141825558](https://image.3001.net/images/20230712/1689141825_64ae42419345c05365f53.png!small?1689141825558)

5\. 下一页是密码破解。点击“Start”，该过程通常只需要几秒钟，但需要大量的系统内存。这就是为什么我们强烈建议使用64位版本的解密工具。

找到密码后，点击“Next”继续解密 PC 上所有加密文件。

![1689141843_64ae42536f8e8d538cd7e.png!small?1689141843284](https://image.3001.net/images/20230712/1689141843_64ae42536f8e8d538cd7e.png!small?1689141843284)

6\. 最后，还可以选择备份加密文件。如果解密过程中出现任何问题，这些备份可能会起到帮助。建议默认选择此选项。单击“Decrypt”，等待解密完成即可。

![1689141878_64ae42762b2e281eb5643.png!small?1689141878150](https://image.3001.net/images/20230712/1689141878_64ae42762b2e281eb5643.png!small?1689141878150)

## IOCs（入侵指标）

### Windows

3c92bfc71004340ebc00146ced294bc94f49f6a5e212016ac05e7d10fcb3312c

5c62626731856fb5e669473b39ac3deb0052b32981863f8cf697ae01c80512e5

678ec8734367c7547794a604cc65e74a0f42320d85a6dce20c214e3b4536bb33

7b295a10d54c870d59fab3a83a8b983282f6250a0be9df581334eb93d53f3488

8631ac37f605daacf47095955837ec5abbd5e98c540ffd58bb9bf873b1685a50

1b6af2fbbc636180dd7bae825486ccc45e42aefbb304d5f83fafca4d637c13cc

9ca333b2e88ab35f608e447b0e3b821a6e04c4b0c76545177890fb16adcab163

d0510e1d89640c9650782e882fe3b9afba00303b126ec38fdc5f1c1484341959

6cadab96185dbe6f3a7b95cf2f97d6ac395785607baa6ed7bf363deeb59cc360

### Linux

1d3b5c650533d13c81e325972a912e3ff8776e36e18bca966dae50735f8ab296

  

原文：<https://decoded.avast.io/threatresearch/decrypted-akira-ransomware/>


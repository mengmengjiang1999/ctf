自从 2021 年 9 月 Qakbot 木马回归以来，积极通过 SquirrelWaffle 垃圾邮件进行传播，安全分析人员都发现了可疑的 Qakbot
新样本。

Qakbot 是最早在 2007 年被发现的银行木马，运营者不断增强恶意软件的功能，例如横向移动、窃取电子邮件和浏览器数据等。最新发现 Qakbot
应用的技术是将加密数据写入注册表中，通常对 Qakbot 的分析中，并没有讲述如何解密注册表数据的细节，本文将展示如何解密这些数据。

![image.png-252.4kB](https://image.3001.net/images/20220128/1643355477_61f39d55dfc644a19b90e.png!small)加密注册表项示例

## 解密流程

![image.png-163kB](https://image.3001.net/images/20220128/1643355478_61f39d569240fe5134cf3.png!small)解密流程

## 密钥生成

Qakbot 会从失陷主机收集系统相关信息，包括：

  * 计算机名称（使用 `GetComputerNameW`）
  * 卷序列号（使用 `GetVolumeInformationW`）
  * 帐户名称（使用 `LookUpAccountSidW`）

分析环境的主机为：

信息| 值  
---|---  
计算机名称| DESKTOP-4NQG47A  
卷序列号| 2797280851  
账户名称| SECRET ACCOUNT  
  
将获取的系统信息连起来形成密码 `DESKTOP-4NQG47A2797280851SECRET ACCOUNT`，再使用修改后的
`CRC32_shift4`算法对密码进行哈希计算。

![image.png-68.9kB](https://image.3001.net/images/20220128/1643355479_61f39d577a6f4a8a02c6a.png!small)修改的
CRC32 shift4 函数

本例中哈希为 `AC E9 B5 8D`，将其称为 `PASSWORDHASH`。

## 配置 ID

Qakbot 创建的每个注册表项值名称都是由 1 字节的 ID 定义的配置字段决定的，该 ID 还用于对 `PASSWORDHASH`进行加盐。

将 ID 与 `PASSWORDHASH`连接起来，使用 SHA1 进行哈希计算，得到派生密钥称为 `DERIVED_KEY`。

> SHA1(<1 bytes ID> \+ <3 byte \x00 padding> \+ < 4 bytesCRC32 Hash KEY_B>) =
> DERIVED_KEY

例如，在 ID 为 `0Eh`、PASSWORDHASH 为 `\xac\xe9\xb5\x8d`的情况下：

> SHA1(“\x0e” + ”\x00\x00\x00” + “\xac\xe9\xb5\x8d”) =
> \x7a\x2b\x30\xb1\xaf\x46\xeb\xc0\xe3\xc7\xf6\x9b\xf1\x97\x2b\x05\xd5\xca\x06\x8f

SHA1 哈希值将被用做派生密钥，通过 RC4 算法解密与 ID 相关的注册表项。

## 解密注册表

将 ID 与 DERIVED_KEY 连在一起再使用 `CRC32_shift4`算法进行哈希即可获得注册表项名称。

> mit_crc32_shift4("\x0e\x00\x00\x00" + "\xac\xe9\xb5\x8d") ->
> "\x6a\xae\x40\xdd"

使用 DERIVED_KEY 解密 RC4 算法加密的特定注册表项（6aae40dd）：

>
> \x7a\x2b\x30\xb1\xaf\x46\xeb\xc0\xe3\xc7\xf6\x9b\xf1\x97\x2b\x05\xd5\xca\x06\x8f

解密数据中发现了包含恶意软件安装时间戳的配置文件：

> 6aae40dd id=14 (0x0e)
>
> 03 01 16 00 00 00 35 3b 31 3b 30 7c 33 3b 32 31 | ......5;1;0|3;2  
> 3b 31 36 33 38 37 35 32 30 35 35 00 8e 53 03 0b | 1;1638752055..S.  
> df e5 f0 2d bf 42 cb 70 bf 1d 62 d1 d8 ec 1a c5 | ....-.B.p..b....  
> a8 f4 cf d8 e1 c4 bd 52 18 d6 68 a6 e2 95 03 f8 | ........R..h....  
> c8 c9 a3 41 7a ff 6b 69 11 2b 1b 9b 60 d4 19 49 | ....Az.ki.+..`..  
> 00 eb f5 7f 08 24 86 c0 10 6d 55 d7 bd ce 2c 23 | I.....$...mU...,  
> e9 d7 91 b1 | #....

## 解密工具

研究人员编写了解密工具来帮助社区对 Qakbot 的加密注册表项进行解密，可以在
[GitHub](https://github.com/drole/qakbot-registry-decrypt)的仓库中找到。

![image.png-173.2kB](https://image.3001.net/images/20220128/1643355480_61f39d5816297491eb988.png!small)解密示例

## IOC

> 90aac91ba4336bdb252dee699d32d78d  
> a53c130fe120348b9bfa188ab93b6ad4

## 参考来源

> [Trustware](https://www.trustwave.com/en-us/resources/blogs/spiderlabs-> blog/decrypting-qakbots-encrypted-registry-keys/)


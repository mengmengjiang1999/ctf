## 背景

如今，勒索软件运营商已经熟练掌握双重勒索技术。不时就会观察到许多攻击者以不同的方式窃取数据，其中一些预先提供依赖于 RClone、FTP
站点等合法服务和工具、一些通过 VPN 窃密，但也有其他攻击者使用定制的工具。

LockBit 攻击团伙开发了一种专门用于数据泄露的定制工具，并将其用作树立其犯罪品牌的标杆。事实上，StealBit 2.0
工具是该攻击团伙开发的工具集的一部分，以克服大规模数据窃取的难点。

了解该工具背后的运作机制和基础设施是特别有价值的。在分析了最新版本的 StealBit 后，跟踪了该工具滥用的攻击基础设施。

## 技术分析

哈希| 3407f26b3d69f1dfce76782fee1256274cf92f744c65aa1ff2d3eaaaf61b0b1d  
---|---  
文件大小| 52.7KB  
ssdeep|
768:FXPkQ2Csnwhxvfhko88yb6cvXbhb7vJawOuArU1o/xnmGP:YLqvZko9ybpvrtvJa/uArU+5nNP  
描述| LockBit 攻击团伙采用的数据渗漏程序  
  
该样本缺少元数据字段，只能获得位数、入口点和编译时间戳。

![](https://image.3001.net/images/20210929/1632897134_6154086e7e22935bc432f.png!small)

该样本没有能生成导入表哈希，并不是工具错误，而是样本的导入表完全是空的，没有导入任何 Windows API。

## 反调试

即使不调用系统 API 也不影响开发者保护代码。StealBit 在入口点后就会进行反分析。

![](https://image.3001.net/images/20210929/1632897138_615408721534a9b8edd92.png!small)

这是一种常见的反调试技术，对进程环境块（PEB）中特定标志位（NtGlobalFlags）进行检查：

    
    
    mov eax, fs:[30h] ; Load the PEB data structure mov eax, eax+68h ; Load the value of the “NtGlobalFlags” flag 

如果标示为 `0x70`则表示该进程被调试，样本会陷入相同的指令循环对抗分析。

## 动态加载

样本需要加载其他库来执行恶意行为，即使不存在 IAT 也会加载三个基本的 DLL 文件：

![](https://image.3001.net/images/20210929/1632897140_6154087452cd22d7aa818.png!small)

为了加载其余系统 API，StealBit 隐藏了本机 DLL 名称以导入栈中。这意味着需要加载的 DLL
文件的名称一次一个字符被写入栈中，然后弹出重新构建所需字符串。![](https://image.3001.net/images/20210929/1632897143_615408770a68f9ee57c5c.png!small)

上图为 `ws2_32.dll`，是用于网络通信的库文件。加载的其他字符串如下所示：

![](https://image.3001.net/images/20210929/1632897145_615408796fd62137dcb0f.png!small)

样本在分析中大量使用了栈字符串混淆技术对抗分析。

## 数据泄露

当 C&C 服务器成功连接时，会启动数据外带任务。通过 HTTP 的 `PUT`方法执行，尽可能快的将数据外带。

![](https://image.3001.net/images/20210929/1632897149_6154087dd8165516f1d16.png!small)

主要的字段如下所示：

> PUT：HTTP PUT 方法
>
> File Hash：要上传的文件
>
> HTTP 头
>
> DAV2 常量头
>
> 配置 ID
>
> 完整文件名
>
> 文件的明文内容

构建的请求如下所示：

![](https://image.3001.net/images/20210929/1632897155_615408833b791c72229e6.png!small)

抛开 LockBit 的宣传，StealBit 工具实际上并没有对文件进行压缩。事实上，除了系统文件、注册表项、脚本和特定扩展名（如
.cmd、.msi、.ocx、.cpl、.hta、.lnk、.exe）的文件外，恶意软件会选择性地上传文件。

## 配置提取

恶意软件的静态配置信息被加密保护：

![](https://image.3001.net/images/20210929/1632897159_6154088741ce265d3a422.png!small)

攻击者使用巧妙的算法来解密 StealBit 的配置，读取长为 8 个字节的密钥来解码从偏移量 `0x40E250`开始的数据。所有的
`124`个字节都被解码时，循环结束。

解密前后如下所示：

![](https://image.3001.net/images/20210929/1632897162_6154088a2cbfdad62d7ab.png!small)

配置包括一个五字符的 ID，用来标识受害者，另一部分是数据渗漏的 IP 地址。

## 其他样本

通过 Yara 规则狩猎其他样本，如下所示：

样本  
---  
2f18e61e3d9189f6ff5cc95252396bebaefe0d76596cc51cf0ade6a5156c6f66  
4db7eeed852946803c16373a085c1bb5f79b60d2122d6fc9a2703714cdd9dac0  
07a3dcb8d9b062fb480692fa33d12da05c21f544492cbaf9207956ac647ba9ae  
3407f26b3d69f1dfce76782fee1256274cf92f744c65aa1ff2d3eaaaf61b0b1d  
bd14872dd9fdead89fc074fdc5832caea4ceac02983ec41f814278130b3f943e  
ced3de74196b2fac18e010d2e575335e2af320110d3fdaff09a33165edb43ca2  
107d9fce05ff8296d0417a5a830d180cd46aa120ced8360df3ebfd15cb550636  
  
样本完全是相似的：

![](https://image.3001.net/images/20210929/1632897165_6154088db4532912c22e7.png!small)

提取的配置如下所示：

哈希| 编译时间戳| ID| IP地址  
---|---|---|---  
07a3dcb8d9b062fb480692fa33d12da05c21f544492cbaf9207956ac647ba9ae| 2021-07-12
04:58:17| 84AFC| 93.190.143.101 139.60.160.200 193.162.143.218 193.38.235.234
45.227.255.190  
107d9fce05ff8296d0417a5a830d180cd46aa120ced8360df3ebfd15cb550636| 2021-07-31
07:09:59| J29EV| 93.190.139.223 168.100.11.72 139.60.160.200 193.38.235.234
174.138.62.35  
2f18e61e3d9189f6ff5cc95252396bebaefe0d76596cc51cf0ade6a5156c6f66| 2021-07-31
07:09:59| D26VN| 174.138.62.35 93.190.143.101 139.60.160.200 193.38.235.234
193.162.143.218  
3407f26b3d69f1dfce76782fee1256274cf92f744c65aa1ff2d3eaaaf61b0b1d| 2021-07-31
07:09:59| LCPA0| 88.80.147.102 168.100.11.72 139.60.160.200 193.38.235.234
174.138.62.35  
4db7eeed852946803c16373a085c1bb5f79b60d2122d6fc9a2703714cdd9dac0| 2021-07-12
04:58:17| 4ATGY| 139.60.160.200 193.38.235.234 193.162.143.218 45.227.255.190
185.215.113.39  
bd14872dd9fdead89fc074fdc5832caea4ceac02983ec41f814278130b3f943e| 2021-07-31
07:09:59| D26VN| 174.138.62.35 93.190.143.101 139.60.160.200 193.38.235.234
193.162.143.218  
ced3de74196b2fac18e010d2e575335e2af320110d3fdaff09a33165edb43ca2| 2021-07-12
04:58:17| 84AFC| 93.190.143.101 139.60.160.200 193.162.143.218 193.38.235.234
45.227.255.190  
  
## 攻击基础设施分析

不同的攻击行动间的关系并不明确，但是这些恶意 IP 地址也发现了相关的攻击行动。

IP| 计数| Whois| 发现  
---|---|---|---  
139.60.160.200| 7| HOSTKEY-USA US|  
  
168.100.11.72| 2| BLNETWORKS-01 US| 2021年8月针对意大利银行的钓鱼  
174.138.62.35| 4| DIGITALOCEAN-174-138-0-0 US|  
  
185.215.113.39| 1| SC-ELITETEAM-20201113 SC| 2021年2月移动恶意软件传播  
193.162.143.218| 5| FirstByte RU|  
  
193.38.235.234| 7| VDSINA-NET RU| 2021年8月，RDP名为 WIN-R84DEUE96RB 和
WIN-5ODCFIGQRP3  
45.227.255.190| 3| Okpay Investment Company PA-OICO-LACNIC|
2021年4月扫描/攻击MongoDB  
88.80.147.102| 1| BelCloud-net BG|  
  
93.190.143.101| 4| WORLDSTREAM NL| 2020年发送垃圾邮件  
93.190.139.223| 1| WORLDSTREAM NL|  
  
  
## 结论

LockBit 已经成为最活跃的攻击团伙之一，StealBit 等数据窃取工具将会为公司带来更多威胁。

## IOC

> 07a3dcb8d9b062fb480692fa33d12da05c21f544492cbaf9207956ac647ba9ae  
> 2f18e61e3d9189f6ff5cc95252396bebaefe0d76596cc51cf0ade6a5156c6f66  
> 3407f26b3d69f1dfce76782fee1256274cf92f744c65aa1ff2d3eaaaf61b0b1d  
> 4db7eeed852946803c16373a085c1bb5f79b60d2122d6fc9a2703714cdd9dac0  
> bd14872dd9fdead89fc074fdc5832caea4ceac02983ec41f814278130b3f943e  
> ced3de74196b2fac18e010d2e575335e2af320110d3fdaff09a33165edb43ca2  
> 107d9fce05ff8296d0417a5a830d180cd46aa120ced8360df3ebfd15cb550636  
> 139.60.160.200  
> 168.100.11.72  
> 174.138.62.35  
> 185.215.113.39  
> 193.162.143.218  
> 193.38.235.234  
> 45.227.255.190  
> 88.80.147.102  
> 93.190.143.101  
> 93.190.139.223

## Yara

> rule stealbit_decode {  
> meta:  
> description = "Yara Rule for StealBit Configuration decryption"  
> author = "Yoroi Malware Zlab"  
> last_updated = "2021_09_01"  
> tlp = "white"  
> category = "informational"  
> strings:  
> decode_Conf = { 8b c1 83 e0 0f 8a 8? ?? ?? ?? ?? 30 8? ?? ?? ?? ?? 41 83 f9
> 7c }
>
> condition:  
> all of them  
> }

## 参考来源

> [Yoroi﻿](https://yoroi.company/research/hunting-the-lockbit-gangs-> exfiltration-infrastructures/)


# GandCrab 5.1样本详细分析

阅读量 **452600**

|评论 **1**

发布时间 : 2019-01-23 20:37:08

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_565_/t013452211815e0d42b.png)

作者：360企业安全华南基地

## 概述

最近国外安全研究人员发现了GandCrab勒索病毒的V5.1最新版变种，360企业安全华南基地团队马上对此事进行了相关跟进，获取到了相应的变种样本，确认此样本为GandCrab勒索家族的最新的变种，新版本增加了大量花指令，大部分关键功能都是动态获取
API，并且所有关键字符串也都被加密了。文件加密算法采用RSA-2048+ salsa20，并且加密共享目录中的文件,
并使用漏洞进程提权还将系统中指定的文档和文件加密为随机字符后缀，然后对用户进行勒索。天擎已能对该勒索者进行查杀

![](https://p0.ssl.qhimg.com/t01f97d8ec7fbd71f1a.jpg)

## 技术细节详细分析

前期准备

首先GandCrab会遍历当前系统进程列表，如果匹配到指定的进程后则结束该进程。防止文件被占用，要结束的进程列表如下总共71个进程名字

msftesql.exe、sqlagent.exe、sqlbrowser.exe、sqlwriter.exe、oracle.exe、ocssd.exe、dbsnmp.exe、synctime.exe、agntsvc.exe、isqlplussvc.exe、xfssvccon.exe、sqlservr.exe、mydesktopservice.exe、ocautoupds.exe、encsvc.exe、firefoxconfig.exe、tbirdconfig.exe、mydesktopqos.exe、ocomm.exe、mysqld.exe、mysqld-nt.exe、mysqld-opt.exe、dbeng50.exe、sqbcoreservice.exe、excel.exe、infopath.exe、msaccess.exe、mspub.exe、onenote.exe、outlook.exe、powerpnt.exe、steam.exe、thebat.exe、thebat64.exe、thunderbird.exe、visio.exe、winword.exe、wordpad.exe、synctime.exe、dbsnmp.exe、oracle.exe、sqlwriter.exe、ocomm.exe、sqlbrowser.exe、sqlagent.exe、thebat.exe、isqlplussvc.exe、msftesql.exe、agntsvc.exe、xfssvccon.exe、sqlservr.exe、mydesktopservice.exe、ocautoupds.exe、encsvc.exe、firefoxconfig.exe、tbirdconfig.exe、mydesktopqos.exe、ocssd.exe、mysqld.exe、mysqld-nt.exe、mysqld-opt.exe、dbeng50.exe、sqbcoreservice.exe、excel.exe、mspub.exe、infopath.exe、msaccess.exe、onenote.exe、outlook.exe、powerpnt.exe、steam.exe

![](https://p3.ssl.qhimg.com/dm/1024_663_/t01766056442c5b1bda.png)

然后动态获取Kernel32模块地址，获取导出函数名称，并计算hash后与硬编码的hash比较获取函数地址如下:

0xC930EA1E = Process32Next

0x6C544060 = SetErrorMode

0x99A4299D = OpenProcess

![](https://p1.ssl.qhimg.com/dm/1024_405_/t016f5989740a08f3e5.png)

通过预先设置好的硬编码做为RC4解密算法的key做进行解密，然后还原出每个字符串的原始内容，根据内容判断，是连接C2时使用的请求参数名。

![](https://p2.ssl.qhimg.com/dm/1024_324_/t01c2f4ea364013c1df.png)

参数名  
---  
pc_user  
pc_name  
pc_group  
av  
pc_lang  
pc_keyb  
os_major  
os_bit  
ransom_id  
hdd  
ip  
Sub_id  
version  
  
![](https://p2.ssl.qhimg.com/t0167b1ea20b0ec8c8a.png)

最后将获取到的系统信息，再次使用RC4进行加密，使用的加密key值为 ：

.oj=294~!z3)9n-1,8^)o((q22)lb$

![](https://p5.ssl.qhimg.com/t0168107e0053099f5a.png)

加密后的：

![](https://p4.ssl.qhimg.com/t01ac1045b05ff5cd33.png)

然后获取Windows版本信息

![](https://p1.ssl.qhimg.com/t010fd2280b3c7a6434.png)

获取当前运行进程权限等级

![](https://p0.ssl.qhimg.com/t0136c007acb26520b6.png)

然后判断当前自身进程权限，如果是低权限，则使用CVE-2018-8440 和 CVE-2018-8120进行提权，如下代码

![](https://p3.ssl.qhimg.com/t0188373fcfa418140b.png)

然后使用WMI 将自身以管理员权限进行重启

![](https://p1.ssl.qhimg.com/t01cbb2e9224202355a.png)

获取操作系统语言版本 如果是以下语言时则退出加密，并删除程序

419（俄罗斯）422(乌克兰) 423(比利时) 428(塔吉克) 42B(亚美尼亚)42c(阿塞拜疆) 437(格鲁吉亚) 43f(吉尔吉斯坦)
440(吉尔吉斯斯坦) 442(土库曼) 443(乌兹别克斯坦) 444(鞑靼斯坦) 818(未知) 819(未知) 82c(阿塞拜疆)
843(乌兹别克)45A 叙利亚语(叙利亚) 2801 阿拉伯语(叙利亚)

![](https://p2.ssl.qhimg.com/t01fe59efb8c60be784.png)

使用磁盘序列号计算hash后，创建名为GLobal\<hash>.fuck 互斥体，防止多次运行

![](https://p2.ssl.qhimg.com/dm/1024_385_/t0198d584a2e647b010.png)

在这个版本中仍就点名安全研究员 @hashbreaker Daniel J. Bernstein

![](https://p5.ssl.qhimg.com/dm/1024_381_/t01fa9cddaf547492f9.png)

## 开始加密

做完上文中说的事情后，开始进入加密文件的流程，通过两层解密后得到RSA-2048公钥：

首先使用硬编码的RC4算法进行解密，然后再进行xor算法得到密文

![](https://p4.ssl.qhimg.com/t01583f97c878dbaa58.png)

然后再使用下图解密出来的KEY再次去解密，最终得到RSA的公钥明文

![](https://p1.ssl.qhimg.com/t01b4cd3d6cbd2450d6.png)

解密后的RSA-2048 公钥：

![](https://p5.ssl.qhimg.com/t01146a20f72c4681ac.png)

不进行加密的文件后缀：

![](https://p1.ssl.qhimg.com/dm/1024_354_/t01fa6e866e7f253334.png)

不加密的后缀列表如下：

.cab .cpl .cur .diagcab .diagpkg .dll .drv .lock .hlp .ldf .icl .icns .ico
.ics .lnk .key .idx .mod .mpa.msc .msp .msstyles .msu .nomedia .ocx .prf .rom
.rtp .scr .shs.spl .sys .theme .themepack .exe .bat .cmd .gandcrab .KRAB .CRAB
.zerophage_i_like_your_pictures

要加密的文件后缀列表如下：

![](https://p0.ssl.qhimg.com/dm/1024_247_/t012c0497ee8b83a49b.png)

随机生成字符串作为加密后的文件扩展名，写入到注册表

HKEY_LOCAL_MACHINE\SOFTWARE\ex_data\data[ext]，该字符串作为被加密文件后缀，如下图所示：

![](https://p1.ssl.qhimg.com/dm/1024_442_/t01521e23112d11fa6e.png)

然后生成一对RSA-2048密钥，并导出PUBLICKEYBLOB和PRIVATEKEYBLOB 用于加密salsa20
算法的key（用于加密文件的key）

![](https://p4.ssl.qhimg.com/dm/1024_669_/t019a9067f958e7d939.png)

创建注册表SOFTWARE\keys_data\data

![](https://p1.ssl.qhimg.com/dm/1024_398_/t014750833cb8957253.png)

写入注册表前生成的RSA-2048公钥

![](https://p1.ssl.qhimg.com/t01f1bae9b0e33cd5d3.png)

  1. 导入硬编码公钥

sub_2040EC函数导入硬编码的RSA2048公钥来加密生成的8位随机数和32位随机数

![](https://p1.ssl.qhimg.com/dm/1024_757_/t017503f7415d4af23d.png)

使用硬编码的公钥加密8位、32位随机字符串，以及生成的RSA-2048私钥，随后将加密的信息写入注册表

![](https://p3.ssl.qhimg.com/dm/1024_422_/t0100e5550799458208.png)

写入加密后的私钥大小+32位随机字符+8位随机字符+加密后的私钥

![](https://p5.ssl.qhimg.com/dm/1024_426_/t0182d1d095d963fb8d.png)

  2. 解密勒索字符串信息

使用Base64加密之前的key以及收集的pc信息，拼接到勒索提示文件中

![](https://p3.ssl.qhimg.com/t01d026946e5e846764.png)

解密勒索提示文本内容，如下图所示

![](https://p3.ssl.qhimg.com/t01662e043c455eb7c7.png)

最终写入的勒索提示文件，如下图所示：

![](https://p4.ssl.qhimg.com/dm/1024_769_/t01ffa18c0c34d58d12.png)

  3. 加密文件

加密可用局域网共享目录下的文件

![](https://p4.ssl.qhimg.com/t01462c5354b713916b.png)

加密磁盘目录下的文件

![](https://p2.ssl.qhimg.com/t01ed9d4138bf1521b7.png)

写入勒索提示文本JBKJFFEII-DECRYPT.txt

![](https://p0.ssl.qhimg.com/t0192bd497347dc84df.png)

写入.lock文件

![](https://p2.ssl.qhimg.com/t016140e81c2f06c3d7.png)

排除特定文件

![](https://p4.ssl.qhimg.com/t01988497fa49333590.png)

加密文件内容

![](https://p3.ssl.qhimg.com/t016ece3d85c811c730.png)

追加加密信息到文件末尾

![](https://p4.ssl.qhimg.com/t01e93e49acc6a4d8be.png)

创建勒索桌面壁纸文件到C:\Users\<USERNAME> \AppData\Local\Temp\bxmeoengtf.bmp

![](https://p0.ssl.qhimg.com/t01577d69b49d99a6cd.png)

通过修改注册表HKCU\Control Panel\Desktop\Wallpaper设置壁纸

![](https://p4.ssl.qhimg.com/t012efb014d7792e501.png)

  4. 删除卷影拷贝

![](https://p3.ssl.qhimg.com/t017e350d0efbd3629c.png)

检测如果WMI可用，则使用WMI命令删除卷影拷贝:

    
    
    C:\Windows\system32\wbem\wmic.exe shadowcopy delete

否则使用CMD命令删除：

    
    
    C:\Windows\system32cmd.exe /c vssadmin delete shadows /all /quiet

## 查杀、防御技术方案

  * 不要打开来历不明的邮件附件
  * 在Windows中禁用U盘的“自动运行”功能
  * 打齐操作系统安全补丁，及时升级Web、数据库等服务程序，防止病毒利用漏洞传播
  * 避免使用弱口令，采用复杂密码，设置登录失败次数限制，防止暴力破解攻击
  * 安装杀毒软件，定期扫描电脑，及时升级更新病毒库保持杀毒软件的良好运行
  * 提高安全意识，保持良好的上网习惯，重要数据做好备份

## 关于360天擎新一代终端安全管理系统

360天擎新一代终端安全管理系统是360企业安全集团为解决政企机构终端安全问题而推出的一体化解决方案，是中国政企客户3300万终端的信赖之选。系统以功能一体化、平台一体化、数据一体化为设计理念，以安全防护为核心，以运维管控为重点，以可视化管理为支撑，以可靠服务为保障，能够帮助政企客户构建终端防病毒、入侵防御、安全管理、软件分发、补丁管理、安全U盘、服务器加固、安全准入、非法外联、运维管控、主机审计、移动设备管理、资产发现、身份认证、数据加密、数据防泄露等十六大基础安全能力，帮助政企客户构建终端威胁检测、终端威胁响应、终端威胁鉴定等高级威胁对抗能力，为政企客户提供安全规划、战略分析和安全决策等终端安全治理能力。

[](https://p3.ssl.qhimg.com/t0162de226c86b2fa2c.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170149](/post/id/170149)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [勒索软件](/tag/勒索软件)
  * [GandCrab](/tag/GandCrab)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


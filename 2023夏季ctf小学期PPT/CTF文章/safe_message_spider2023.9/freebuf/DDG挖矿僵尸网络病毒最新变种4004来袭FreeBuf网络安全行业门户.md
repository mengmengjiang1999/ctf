## 背景

近日，深信服安全团队接到反馈，某虚拟平台大量机器CPU占用非常高，怀疑中了挖矿病毒。经过安全专家排查，发现还存在ssh爆破行为。进一步分析后，判断其为DDG挖矿病毒。

![](https://image.3001.net/images/20190916/1568633913_5d7f7439a6730.png!small)

DDG挖矿病毒(国外称其为Linux.Lady)是一款在Linux系统下运行的恶意挖矿病毒，前期其主要通过ssh爆破，redis未授权访问漏洞等方式进行传播，近年来其更新非常频繁，已经出现多个版本，本次捕获到的是4004版本。

![](https://image.3001.net/images/20190916/1568633918_5d7f743eeca18.png!small)

## 详细分析

本次其相对于以往的版本主要体现在其增加了2个漏洞利用，分别为supervisord的远程命令执行漏洞CVE-2017-11610和nexus仓库管理器的远程代码执行漏洞CVE-2019-7238。

![](https://image.3001.net/images/20190916/1568633925_5d7f7445ab2d7.png!small)

DDG初始入口点为一个下载脚本，主要根据机器的平台架构选择对应版本的ddg二进制文件(i686和x86_64)

![](https://image.3001.net/images/20190916/1568633935_5d7f744faeb49.png!small)

创建定时任务执行持久感染

![](https://image.3001.net/images/20190916/1568633945_5d7f745944761.png!small)

再次尝试分析之后，发现其i.sh文件里面的一些固定位置的内容已经随机变换了，可以从这方面初步了解到黑产的自动化

![](https://image.3001.net/images/20190916/1568633949_5d7f745dd4950.png!small)

下载的是DDG的go语言编译的母体文件，其主要作用有创建守护进程、创建后门、下载挖矿程序挖矿、命令执行这4个功能。

获取用户home目录，在当前目录下生成一个.ddg的隐藏文件夹，在该目录下生成一个bolt数据库文件4004.db，该数据库文件中保存对执行过的命令进行记录，保存集群节点信息。

![](https://image.3001.net/images/20190916/1568633954_5d7f7462f1fcc.png!small)

![](https://image.3001.net/images/20190916/1568633960_5d7f746830f98.png!small)

![](https://image.3001.net/images/20190916/1568633963_5d7f746ba83df.png!small)

![](https://image.3001.net/images/20190916/1568633967_5d7f746f25e25.png!small)

其中，创建后门主要是将恶意程序内置的ssh公钥写入验证秘钥文件中，实现免密登录：

![](https://image.3001.net/images/20190916/1568633972_5d7f7474c3ae1.png!small)

其ssh公钥为：

![](https://image.3001.net/images/20190916/1568633987_5d7f748387d3c.png!small)

命令执行，连接集群中的机器获取配置信息：

![](https://image.3001.net/images/20190916/1568633993_5d7f7489391f9.png!small)

![](https://image.3001.net/images/20190916/1568633997_5d7f748d4460a.png!small)

然后对获取到的配置信息进行解码获取指令，指令解密如下。其中针对之前的systemdminer，有了针对性的对抗，对其域名做重定向、kill对应进程以及文件做了清除。

![](https://image.3001.net/images/20190916/1568634001_5d7f74917a8c7.png!small)

本次除了原本的ssh爆破以及redis未授权访问之外，新添加了2个漏洞利用分别为CVE-2019-7238，CVE-2017-11610。可以看到在下发的配置文件中对ssh(22,
1987,2222)、redis(端口6379, 6389, 7379, 26379)和nexus(8081)进行扫描。

![](https://image.3001.net/images/20190916/1568634005_5d7f749547fb3.png!small)

![](https://image.3001.net/images/20190916/1568634009_5d7f749964189.png!small)

![](https://image.3001.net/images/20190916/1568634012_5d7f749c4b358.png!small)

nexus的远程代码执行漏洞CVE-2019-7238

![](https://image.3001.net/images/20190916/1568634016_5d7f74a08f4d9.png!small)

supervisord的远程代码执行漏洞CVE-2017-11610

![](https://image.3001.net/images/20190916/1568634020_5d7f74a42c643.png!small)

挖矿程序/tmp/SzDXM，可以看到其编译于2019年8月29日

![](https://image.3001.net/images/20190916/1568634023_5d7f74a7a0794.png!small)

![](https://image.3001.net/images/20190916/1568634027_5d7f74ababd76.png!small)

查询硬编码的钱包地址相关信息，目前该地址并没有太多的收益：

![](https://image.3001.net/images/20190916/1568634031_5d7f74af23ff2.png!small)

## 解决方案

### 病毒检测查杀

部署相关产品用户可进行病毒检测，如图所示：

![](https://image.3001.net/images/20190916/1568634035_5d7f74b32218b.png!small)

### 病毒防御

深信服安全团队再次提醒广大用户，注意日常防范措施：

> 1、及时给电脑打补丁，修复漏洞。
>
> 2、对重要的数据文件定期进行非本地备份。
>
>
> 3、深信服防火墙、终端检测响应平台（EDR）均有防爆破功能，防火墙开启此功能并启用11080051、11080027、11080016规则，EDR开启防爆破功能可进行防御。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。

### IOCs

钱包地址：8AzmXnQJ4kjNmcE4w6mwVabzhUTZ4jsaj5rmBgJosvrD7ag7TPTG2U4Kruv5Mevxp2BE8K6n9YJGfeLYZzkCDUdNGHT8sUy

C2：68.183.140.39

### URI：

> <http://103.219.112.66:8000/slave>
>
> <http://68.183.140.39:8000/static/4004/ddgs.i686>
>
> <http://68.183.140.39:8000/static/4004/ddgs.x86_64>
>
> <http://68.183.140.39:8000/static/SzdXM>

### MD5:

> ddgs.x86_64 : BDFA1**3B3E03880D718609AF3B9648F
>
> ddgs.i686 : 76309D50AD8412954CA87355274BD8FF
>
> SzdXM :F24E35D722150B5E2E70F316734D88F

## 参考链接

> <https://www.anquanke.com/post/id/170021>
>
> <https://www.anquanke.com/post/id/170021>
>
> <https://icematcha.win/?p=1189>
>
> <https://www.52pojie.cn/thread-841311-1-1.html>

***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**


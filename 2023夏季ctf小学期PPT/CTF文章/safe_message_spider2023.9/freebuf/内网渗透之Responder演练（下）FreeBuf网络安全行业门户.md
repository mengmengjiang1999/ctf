## 前情提要

承接[上文](https://www.freebuf.com/articles/network/256844.html)，本文主要介绍了以下几点：

> 获取ntlmv1 hash并还原出ntlm hash
>
> NTLM hash中继攻击入门
>
> 对抗responder：工具对抗、关闭协议、蜜罐检测的优势

## 获取NTLMv1 hash并还原nt hash

本次实验环境情况：

kali： 172.21.128.72  
win7-A： 172.21.128.100  
win7-B： 172.21.128.101

### 使用win7降级，获取V1进行测试

上文主要是讲了NTLM V2的窃取与破解，在实际情况中，NTLMv1 hash也是存在于winserver 2003、windows
xp上，而在win7上是默认关闭的，我们可以通过修改注册表的方式，使win7支持NTLM V1认证，由于NTLM
V1认证过程的特殊性，非常容易被破解并还原出NTLM HASH，需要说明的是，NTLM降级的情况一般不常见，除非在局域网内存在低于windows
Vista版本的windows机器，这里是为了方便做实验所以手动降级。

为破解NTLMv1 hash，我们还需要做一些准备，在“欺骗阶段”，所以我们需要将challenge固定下来，得出特定challenge的NTLMv1
hash，方便后续破解，这里我们需要修改responder.conf里边的challenge值为“1122334455667788”，然后再次开启responder（注意加上
--lm参数），此时收到的NTLMv1 hash就可以直接破解并还原出NTLM HASH。

### 实验步骤：

首先在将win7-A降级，管理员权限执行下列命令：

reg add HKLM\SYSTEM\CurrentControlSet\Control\Lsa\ /v lmcompatibilitylevel /t
REG_DWORD /d 2 /f  
reg add HKLM\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0\ /v NtlmMinClientSec
/t REG_DWORD /d 536870912 /f  
reg add HKLM\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0\ /v
RestrictSendingNTLMTraffic /t REG_DWORD /d 0 /f

修改responder配置文件：![](https://image.3001.net/images/20210305/1614932361_6041e98945926bab1f420.png!small)

开启responder，启动参数加上--lm（如果报错可以尝试python2执行对应py脚本）：![](https://image.3001.net/images/20210305/1614932373_6041e99520be2ad76c344.png!small)

win7执行net use \\\win-test1\qq命令：![](https://image.3001.net/images/20210305/1614932386_6041e9a2dcb95637037ce.png!small)

kali获取到NTLMv1
hash（如欺骗成功但是获取不到HASH，可尝试删除Responder.db再次尝试）：![](https://image.3001.net/images/20210305/1614932509_6041ea1d7205b90d7c8c2.png!small)

经查找相关资料发现，破解此格式的NTLMv1
HASH，本质上还是属于暴力破解，所以我们需要借助彩虹表来进行破解，当然自己生成彩虹表显得太过复杂，这里就不尝试重复造轮子了，我们可以通过一个在线网站（https://crack.sh/）来帮助破解，这个网站有很多收费的破解密码项目，但是破解NTLMv1
hash是免费的。

这里填入固定格式的值，然后填上你需要接收的邮箱：![](https://image.3001.net/images/20210305/1614932547_6041ea4317ab87c510341.png!small)

一般几十秒就会收到破解成功的短信，短信内容包含破解之后的NTLM HASH值， **还原出的** **NTLM hash** **可用于PTH**
**攻击**
:![](https://image.3001.net/images/20210305/1614932564_6041ea542308f17770b66.png!small)

### 为什么能破解NTLMv1 hash？

要了解破解原理，先来看加密过程（加密方式一）：

  1. windows将NTLM Hash后面补5个字节0，共21字节。
  2. 将步骤1处理后的NTLM Hash分成3组7字节，每7个比特后面添加1比特0，组成3个8字节的DES密钥。
  3. 使用得到的3个密钥，分别对8字节的challenge进行3DES加密获得三组8字节密文，然后拼接共组成24字节的密文，这样就得到了NTLMv1 hash。

知道了其加密方式之后，由于challenge是固定的，所以可以建立从key到response的彩虹表，并在知道response的情况下获取key，破解跟机器的密码强度没有关系，且成功率几乎为100%。

需要说明的是，NTLMv1 hash有两种，对应两种加密方式，在上文中responder加入--lm参数也是为了固定为加密方式一，这里简单说下加密方式二，加密方式二跟一最大的不同就是并不是完全用的server
challenge（也就是上文的1122334455667788）参与上边的运算，这就导致了生成的彩虹表不能使用，破解难度增加，responder不加--lm参数的时候就是加密方式二，得出hash的叫 **NTLMv1-SSP Hash** **（如下图）** 。

responder加上--lm参数：![](https://image.3001.net/images/20210305/1614932582_6041ea666139126305f9f.png!small)

responder不加--lm参数：![](https://image.3001.net/images/20210305/1614932590_6041ea6e5c0333832589e.png!small)

  

## NTLM HASH中继攻击入门

https://blog.csdn.net/whatday/article/details/107698383

NTLM中继攻击已经被发现十多年了，要实现NTLM中继攻击，也需要先进行LLMNR/NBNS欺骗，这样，攻击机器就可以充当了中间人，本质上还是由于NTLM认证机制所导致的，且对于最新的NTLMv2认证任然有效，但这个过程并不是没有限制，对于工作组的机器来说，两台机器的密码需要一致才能成功，对于域用户来说，被欺骗用户（发起请求的用户）需要域管理员组里边的用户才可以，NTLM中继成功后的权限为被欺骗用户的权限。

###
流程图如下图：![](https://image.3001.net/images/20210305/1614932605_6041ea7dbd36028d1ec26.png!small)

准备阶段，我们需要改变responder.conf的设置，在这个环节，responder起到的作用仅仅是欺骗，所以我们需要将配置文件的SMB
server和HTTP
server选项从On改为Off（smbrelayx会启动相应端口），随后我们使用smbrelayx.py来进行中继攻击测试，在kali中，这个脚本在/usr/share/doc/python3-impacket/examples/文件夹下，可以通过
--help查看具体用法。

在实验阶段，首先开启responder：![](https://image.3001.net/images/20210305/1614932627_6041ea93cbe343cc78c83.png!small)

由于仅仅是入门，这里使用smbrelayx进行实验，其中参数-h 指定目标主机，-c
给出要执行的命令：![](https://image.3001.net/images/20210305/1614932648_6041eaa8a90f9a1d3bd40.png!small)

在win7-B的机器上执行net use \\\win-test\w进行测试，此时win7-B的NTLM
hash将会被kali中继到win7-A这台机器上，中继成功后执行whoami的命令。下列三个场景分别是win7-B上的机器登录不同账户后产生的NTLM
hash被中继的结果。

场景一：win7-B为域内普通用户，可以看到被拒绝了：![](https://image.3001.net/images/20210305/1614932676_6041eac4aca91fc0eaa03.png!small)

场景二：WIN7-B为域控管理员，可以看到中继成功且为高权限：![](https://image.3001.net/images/20210305/1614932689_6041ead15306340ffea1e.png!small)

场景三：将情况一的普通账户加入域管理员组中，然后再次尝试（可以看到中继成功）：![](https://image.3001.net/images/20210305/1614932697_6041ead989a5178f2b103.png!small)

## 如何应对？

既然responder如此危险，那么如何才能够确保内网安全呢？

抛开边界安全来说，可以从两个方面入手，一是将不必要的服务禁用，这是最保险的方式。二是内网中要有检测工具的手段，最好能够覆盖各个网段，这样才是一个比较安全的策略。

### 禁用不必要的服务

#### 禁用NetBIOS服务

在《网络连接》中右击对应网卡选择属性，然后依次点击如下图所示：![](https://image.3001.net/images/20210305/1614932714_6041eaeaf051c25352ce3.png!small)

### 禁用LLMNR

域内机器可以在域控机器上通过"设置组策略管理"关闭多播名称解析，非域内机器也可以通过本机的"设置组策略管理"关闭LLMNR。![](https://image.3001.net/images/20210305/1614932729_6041eaf9273c69db54628.png!small)

### 开源工具

开源的工具不多，功能方面也比较简单，主要还是通过使用NBNS或者LLMNR协议，向多个随机主机名发起一个广播行为，如果多个回应均为同一IP地址就会产生警告。

### 一：Conveigh

运行效果：![](https://image.3001.net/images/20210305/1614932746_6041eb0ad04b4ceb888cc.png!small)

### 二：VindicateTool

运行效果：![](https://image.3001.net/images/20210305/1614932767_6041eb1fc7dda832ed4df.png!small)

### 安全产品

对于安全产品来说，蜜罐是比较适合检测responder的产品。主要原因是要确保网络覆盖程度，而蜜罐本身的机制正好是要求覆盖于各个网段之中，发现告警后可以上报可疑机器的IP地址，以及对该IP地址的探测情况。后续可以人工研判并处理。


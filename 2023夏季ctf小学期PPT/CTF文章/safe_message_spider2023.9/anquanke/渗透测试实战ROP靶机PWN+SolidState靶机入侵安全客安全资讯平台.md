# 渗透测试实战-ROP靶机PWN+SolidState靶机入侵

阅读量 **384053**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-28 10:30:53

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t017e9184f513b589d4.jpg)

## 前言

大家好，爱写靶机入侵文章的我又来了！本次靶机分2种第一种为CTF中的PWN，该靶机设计在Linux 32位系统中，一共分为3个等级，本次先实战使用
**level-0** ，第二个靶机为SolidState，还是跟原来一样我们入侵进去拿到root权限。

## 靶机安装/下载

靶机ROP下载地址：<https://pan.baidu.com/s/1rYDOK-EDZDEfEYk2_IfRMg>

靶机IP：172.16.24.48

![](https://p0.ssl.qhimg.com/t01706a78b61397bd21.png)

SolidState靶机下载地址：<https://pan.baidu.com/s/1UvSFf-8wMAtRFZ5qNkjMJg>

靶机IP：172.16.24.66

![](https://p2.ssl.qhimg.com/t01ffc785c5ff5bb7a8.png)

## 实战

###  ROP靶机PWN

老规矩探测IP：

![](https://p2.ssl.qhimg.com/t014c33084964b612eb.png)

通过nmap探测可以看到该靶机开了3个端口，我们访问http看一下

![](https://p5.ssl.qhimg.com/t014eade6155250095b.png)

这里给出来了，该等级的c语言代码和一些需要我们关注的信息，比如该等级靶机让我们锻炼ret2libc技术，还给出了一个ssh的账号密码为： **level0
: warmup** ，通过上面的源码可以看到这里有很明显的栈溢出漏洞，下一步我们就登陆该等级ssh，查看调试一下吧

![](https://p2.ssl.qhimg.com/t012c20a9922895392e.png)

登陆成功，在目录下面有一个flag文件，我们现在的权限说没办法读取的，下一步我们运行一下该level0，看看是怎么样的

![](https://p0.ssl.qhimg.com/t014e10387bee13c8b3.png)

可以看到程序接收用户的输入，如果经常挖漏洞的小伙伴一看就知道这样的方式很有可能是出现溢出漏洞的（假如没有源码的情况下），下面我们来调试一下这个level0看看，

![](https://p0.ssl.qhimg.com/t0177a6cd36d38a9d9f.png)

通过上图可以看到小弟是先确认一下系统版本，确认其为32位Linux操作系统，后面才使用gdb加载level0文件

![](https://p5.ssl.qhimg.com/t016c737353325f1d0f.png)

通过查看main可以看到比较敏感的函数：gets

下一步使用checksec来检测一下开启了那些防护，

![](https://p5.ssl.qhimg.com/t010a09dba794faa2ac.png)

如上图可以看到只开启了NX，满足可以使用ret2libc技术，下一步我们来确认偏移地址，我们使用pattern来完成，gdb
peda插件已经内置，因为我们有源码所有我就不把偏移指设的那么多，如图：

![](https://p4.ssl.qhimg.com/t01884e0f1c88c15566.png)

生成完后，我们继续运行一下该程序，在gdb里直接输入 “r” 即可，如何输入生成的值执行

![](https://p4.ssl.qhimg.com/t01b3349cb35282ee30.png)

通过上图可以看到程序如我们预想的那样奔溃，EIP变成了 0x41414641

接下来我们通过pattern_offset来判断溢出点为44

![](https://p3.ssl.qhimg.com/t013d3b51358cda111e.png)

![](https://p1.ssl.qhimg.com/t01e1177bddedd56b07.png)

下一步我们来确认一下溢出点是否真确

![](https://p3.ssl.qhimg.com/t01092e9a14931aa0f3.png)

![](https://p2.ssl.qhimg.com/t0113722f373ddb256c.png)

通过上面的调试已经确认该溢出点是正确的，eip也可控，存在栈溢出漏洞，下一步我们使用vmmap查看内存映射，寻找选择可读可写和可执行的内存块

![](https://p1.ssl.qhimg.com/t013673d5a00fea636d.png)

到了这里有经验的小伙伴肯定知道该怎么做了，

![](https://p3.ssl.qhimg.com/t012bfe38b23ad6e3f2.png)

![](https://p3.ssl.qhimg.com/t010562ce2100566aba.png)

我们找到了2个，下一步我们找pop3ret，我们使用 ropgadget 来帮我们完成，pade插件里已经有了，如图：

![](https://p5.ssl.qhimg.com/t010a7252c6aecf7e6d.png)

，我们找到了一个，是否正确呢，我们去<http://ropshell.com> 上验证一下，小弟这里就把这个level0 下载到本机然后上传到该站分析，

![](https://p4.ssl.qhimg.com/t0165139b5f603144f8.png)

![](https://p0.ssl.qhimg.com/t015907499bc6e1e3ab.png)

![](https://p3.ssl.qhimg.com/t0184f42feec90c715a.png)

确认无误后，下一步我们就来编写这个exp吧，

![](https://p0.ssl.qhimg.com/t01249fdca5eb2f3439.png)

上图中 0xbffdf000 为 堆栈地址

![](https://p0.ssl.qhimg.com/t01787f9f527842502e.png)

下面的0x21000 为 堆栈的空间地址

![](https://p0.ssl.qhimg.com/t01522c87053cdefb46.png)

最后的 0x666 为发送的shellcode字节，其实小伙伴们可以写小一点，我就不一样了我喜欢大的。。。。

最后我们运行该exp，拿flag

![](https://p5.ssl.qhimg.com/t0133afe3c01c68b19f.png)

如图所示，已成功拿到shell和flag

【完】

###  SolidState靶机入侵

看完比较枯燥的，下面我们来点有趣的。

老规矩探测IP：

![](https://p1.ssl.qhimg.com/t0150c5dcee52bd24a2.png)

下一步使用nmap探测一下，

![](https://p1.ssl.qhimg.com/t01aa03f1954884bcf6.png)

发现其开放了多个端口，我们先看看80端口，看有没有什么可利用的

![](https://p4.ssl.qhimg.com/t013f95ef8177691fbf.png)

下一步我们使用目录猜解工具跑一下看看

![](https://p0.ssl.qhimg.com/t014ce5e5c23720926d.png)

发现其过滤了我们的探测,我们在上面扫描时，看到4555端口开放了一个很敏感的服务：JAMES Remote Admin 2.3.2

到了这里我们访问一下该端口看看，

![](https://p0.ssl.qhimg.com/t01848b9437c3928702.png)

让我们登陆，哈哈哈，不用怀疑谷歌一波，发现其默认账号密码为：root ：root

试一下，然后就直接进去了。。。。

![](https://p0.ssl.qhimg.com/t01fee4ac2b7791e704.png)

通过上图提示，我们直接输入 help

看到了其给了我们几个命令，下面小弟就直接列出用户，然后选择一个账户修改其密码，如图：

![](https://p0.ssl.qhimg.com/t015c9e712fb20a8012.png)

可以看到 我重置了 mindy 账户的密码改为 666

下面我又搜索了关于 JAMES 的漏洞，发现一个远程命令执行漏洞，如图：

![](https://p4.ssl.qhimg.com/t014cf92cbc378ad115.png)

地址：<https://www.exploit-db.com/exploits/35513>

那这个漏洞需要配合登陆ssh触发，我们看到上面我已经重置了其邮箱密码，下面我们登陆其邮箱看看有没有什么发现，（关于邮箱怎么设置连接，请查看小弟的前面几篇文章）

![](https://p4.ssl.qhimg.com/t01f08b38e8ca10367e.png)

成功拿到ssh密码：P[@55W0rd1](https://github.com/55W0rd1 "@55W0rd1")!2@

下一步我们修改一下我们找到的exp脚本，

直接修改第19行代码，把payload改成我本机的ip，然后在本机接收1234 端口

![](https://p2.ssl.qhimg.com/t012eb737e74c654dff.png)

![](https://p4.ssl.qhimg.com/t0191f119db92c08895.png)

下一步就是登陆该ssh账户，

![](https://p3.ssl.qhimg.com/t01646528cdb08f798e.png)

我们已经成功拿到shell，（注，这里要说一下，如果没有利用这个漏洞，直接用ssh登陆，得到的shell是“rbash”的，小弟试了试没办法绕过）。

下面我们直接提权吧，老规矩在/tmp目录下上传提权脚本看看

![](https://p2.ssl.qhimg.com/t01a2f2bf0f7e32e8cb.png)

我在/tmp目录下操作的时候，发现刚刚下载完的文件突然就不见了，我去。。。

![](https://p3.ssl.qhimg.com/t01342ddf8af5765f16.png)

当然我的手速还是挺快的，刚刚已经运行完了该脚本，分析中发现了一个可写文件且权限较高，如图：

![](https://p0.ssl.qhimg.com/t01bc5b75cfff6e9315.png)

我们访问查看一下这个文件，

![](https://p5.ssl.qhimg.com/t012ea4be7d4a1d1c0b.png)

看了源码应该就知道了为什么/tmp目录下的文件会突然不见。。。

下面不用怀疑直接替换这个文件，即可

![](https://p0.ssl.qhimg.com/t01f499e3b3fbd5b375.png)

![](https://p2.ssl.qhimg.com/t0127f08b1cf8898498.png)

因为刚刚我们可以看到，这个文件是自己默认隔段时间执行的，所以我们只需要在本机上运行监听端口静静等待美丽的shell自己送来门了就行，如图：

![](https://p2.ssl.qhimg.com/t01477c540ee063ffc3.png)

成功拿到root_shell

## 结语

祝您生活工作愉快！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **d3ckx1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168739](/post/id/168739)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [渗透测试](/tag/渗透测试)
  * [靶机](/tag/靶机)

 **+1** __13赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t017a53cae377f0cd5e.jpg) d3ckx1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


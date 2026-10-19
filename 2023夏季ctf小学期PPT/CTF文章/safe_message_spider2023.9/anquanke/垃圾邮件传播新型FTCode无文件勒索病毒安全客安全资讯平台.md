# 垃圾邮件传播新型FTCode无文件勒索病毒

阅读量 **587463**

发布时间 : 2019-10-08 16:30:17

 **x**

##### 译文声明

本文是翻译文章，文章原作者 安全分析与研究，文章来源：安全分析与研究

原文地址：<https://mp.weixin.qq.com/s/Y86Yc_VOTO9tTq6kzRsaPA>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01ccbbc1efea51f7a4.png)

目前勒索病毒仍然是全球最大的威胁，最近一年针对企业的勒索病毒攻击越来越多，不断有新型的勒索病毒出现，各企业一定要保持高度的重视，大部分勒索病毒是无法解密的，近期国外安全研究人员发现了一款基于PowerShell脚本的勒索病毒FTCode，此勒索病毒主要通过垃圾邮件进行传播

近日国外某独立恶意软件安全研究人员曝光了一个新型的FTCode PowerShell勒索病毒，如下所示：  

此勒索病毒主要通过垃圾邮件进行传播，发送的垃圾邮件会附加一个压缩包，压缩包里面包含一个恶意的DOC文档，从app.any.run上下载到相应DOC样本，打开DOC文件，如下所示：  

启动恶意宏代码，相应的文档内容，如下所示：

![](https://p0.ssl.qhimg.com/t016b63945d4eb855fa.png)

恶意宏代码，启动PowerShell进程执行脚本，如下所示：

![](https://p1.ssl.qhimg.com/t01135440ffbfd22d5a.png)

从恶意服务器下载PowerShell脚本执行，服务器URL地址：

hxxp://home.southerntransitions.net/?need=9f5b9ee&vid=dpec2&81038

打开恶意服务器脚本，如下所示：

![](https://p0.ssl.qhimg.com/t01154a94a4c4395d2b.png)

从恶意服务器下载VBS脚本，然后设置计划任务自启动项，如下所示：

![](https://p5.ssl.qhimg.com/t016add6de56bf12a27.png)

相应的计划任务自启动项WindowsApplicationService，如下所示：

![](https://p3.ssl.qhimg.com/t016cddf70816b90a46.png)

恶意服务器URL

hxxp://home.southerntransitions.net/?need=6ff4040&vid=dpec2&，脚本内容，如下所示：

![](https://p0.ssl.qhimg.com/t01905247340c9481c9.png)

解密后的VBS脚本，是一个PowerShell脚本，如下所示：

![](https://p1.ssl.qhimg.com/t01f8abf04e7eda6f20.png)

再次解密PowerShell脚本之后为一个恶意软件下载器，会下载安装其他恶意软件，内容如下所示：

![](https://p3.ssl.qhimg.com/t018e99630db224e693.png)

下载完VBS脚本，设置计划任务之后，FTCode PowerShell恶意脚本会解密内置字符串生成一个RSA加密密钥，如下所示：

![](https://p0.ssl.qhimg.com/t0153c410eb95ec95cf.png)

删除磁盘卷影，操作系统备份等，如下所示：

![](https://p0.ssl.qhimg.com/t01f266699987a647f0.png)

然后开始加密文件，对指定的文件后缀进行加密，加密后的文件后缀名FTCODE，如下所示：

![](https://p2.ssl.qhimg.com/t01e00892fb67839aff.png)

加密后的文件，如下所示：

![](https://p2.ssl.qhimg.com/t01f2c4b182e85f8c32.png)

在每个加密的文件目录生成勒索提示信息HTM文件READ_ME_NOW.htm，内容如下所示：

![](https://p5.ssl.qhimg.com/t0101bd3dddae37c01d.png)

需要支付500美元进行解密，勒索病毒解密网站

[http://qvo5sd7p5yazwbrgioky7rdu4vslxrcaeruhjr7ztn3t2pihp56ewlqd.onion/?guid=[guid](http://qvo5sd7p5yazwbrgioky7rdu4vslxrcaeruhjr7ztn3t2pihp56ewlqd.onion/?guid=%5Bguid)]

## 附录

### IOC

HASH  
A5AF9F4B875BE92A79085BB03C46FE5C

### C&C

185.158.248.151  
185.120.144.147  
home.southerntransitions.net  
connect.southerntransitions.com

### URL

hxxp://home.southerntransitions.net/?need=9f5b9ee&vid=dpec2&81038  
hxxp://home.southerntransitions.net/?need=6ff4040&vid=dpec2&  
hxxp://connect.southerntransitions.com/  
hxxp://home.hopedaybook.com/?need=9f5b9ee&vid=dpec1&9337  
hxxp://home.southerntransitions.net/?need=6ff4040&vid=dpec1&  
hxxp://home.isdes.com/?need=6ff4040&vid=dpec2&

最近一两年针对企业攻击的勒索病毒越来越多,不断有新的变种以及勒索病毒新家族出现,真的是越来越多了，各企业一定要高度重视,黑产团伙一直在寻找新的攻击目标……

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/Y86Yc_VOTO9tTq6kzRsaPA)

本文翻译自安全分析与研究
[原文链接](https://mp.weixin.qq.com/s/Y86Yc_VOTO9tTq6kzRsaPA)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全分析与研究** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/187920](/post/id/187920)

安全客 - 有思想的安全新媒体

本文转载自: [安全分析与研究](https://mp.weixin.qq.com/s/Y86Yc_VOTO9tTq6kzRsaPA)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/Y86Yc_VOTO9tTq6kzRsaPA>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [勒索病毒](/tag/勒索病毒)
  * [恶意代码](/tag/恶意代码)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t016695dd24f0873866.png) 安全分析与研究

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


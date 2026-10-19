# Hvv样本合集分析（一）

阅读量 **257562**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-13 10:30:58

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01f1358cf0abebebc1.jpg)

## 概述

hvv期间，攻击者除了会对企业用户发起钓鱼攻击，还喜爱对蓝队防守人员发起钓鱼攻击，以防钓鱼手册、禁止访问xxx、钓鱼情况通报、蜜罐监控数据等为话题的鱼叉攻击层出不穷。在本文中，笔者将对最近看到的一系列样本进行分析，希望能帮助大家识别此类攻击，减少危害。

## 样本诱饵

根据不完全统计，目前笔者已经看到并统计到的诱饵名称包括但不限于（部分样本诱饵名涉及企业名称，已手动打码）：

个人信息资料&关于xxxxx银行公司薪酬架构内部调整决定初稿xxxx **.exe**  
1.《xxxxx》课程审核材料填报 **.exe**  
2.xxxx需要收集的信息 **.doc**  
3.xxx个人简历_-副本- **.docx**  
4.采购资料 **.zip**  
5.简历 **.exe**  
6.公司出入款明细 **.exe**  
7.2021年春季学期xxx级干部专题进修班学院信息补充表. **docx.exe**  
8.个人信息资料（信用卡中心） **.zip**  
9.资料未通过 **.rar**  
10.攻防演戏补丁检测使用手册 **.CHM**  
11.xxxx简历模板 **.doc**  
12.xxxx简历1 **.exe**  
13.Windows激活工具 **.exe**  
14.xxx安全防护 **.exe**  
15.自查工具 **.exe**  
16.关于护网攻防演练员工行为监管人员名单 **.exe**  
17.Flash_Update **.exe**  
18…….

## 样本分析

###  Flash_Update.exe

原始样本模仿了Flash的更新程序，双击运行程序之后，程序首先会弹框显示”安装成功，请关闭窗口”以迷惑用户。

![](https://p1.ssl.qhimg.com/t01e503bef0ac149f55.png)

接着程序从data段去取一段数据，先通过base64解码，然后通过AES解密之后得到shellcode，程序通过VirtualAlloc分配一段内存空间并将该段shellcode拷贝过去后call
rbx加载执行：

![](https://p3.ssl.qhimg.com/t01b2bcd4858a59d380.png)

解密出的dll是CobaltStrike生成的shellcode，程序会在dll中解密C2并准备建立连接

![](https://p1.ssl.qhimg.com/t0181759203cfa4975f.png)

###  蜜罐服务监测情况.xlsm

原始样本是带有恶意VBA代码的excel文档，文档内容看起来像是正常的蜜罐报告。

![](https://p1.ssl.qhimg.com/t015bff2fee106af3b7.png)

调用的宏代码由CobaltStrike框架生成，是标准的CS马：

![](https://p3.ssl.qhimg.com/t0199d7c55cdd761b7f.png)

数据转换完成，程序将会通过rundll32.exe加载这段代码， 地址是589824，转换为16进制为：0x90000

![](https://p2.ssl.qhimg.com/t0108b0bf2c6567df64.png)

通过火绒剑，可以看到EXCEL.exe调起了Rundll32.exe，该线程中0x90000的地方，就是CobaltStrike的shellcode。

![](https://p1.ssl.qhimg.com/t01b07120d6da7fe744.png)

将这部分数据dump下来，然后调试之后可以看到C2:81[.]69.250.97

![](https://p2.ssl.qhimg.com/t015eabf85e0423dafb.png)

**关联样本：APT攻击常用漏洞列表.xlsm**

859f0a38a3d5a5d1ab0d382eea7a14c7  
根据样本C2，可以顺藤摸瓜找到一些其他的样本，其中一例名为《APT攻击常用漏洞列表.xlsm》，由于命名和此次捕获的样本十分类似，引起了笔者的注意。

![](https://p1.ssl.qhimg.com/t01476f3e16585c1bb7.png)

需要注意的是，此样本显示的创建时间为2019年3月25日，首次上传VT时间为2020年12月21日，此样本不是VBA的宏利用，而是Macro4.0的恶意样本：

![](https://p3.ssl.qhimg.com/t01b77aa578ff91358f.png)

宏代码执行后将会从<http://81.69.250.97/anquan.msi>
下载msi文件到本地通过msiexec安装，下载的msi文件中包含了一个Binary.Payload的恶意文件：

![](https://p2.ssl.qhimg.com/t01d631c3b6e315ba91.png)

该文件是msf生成的meterpreter后门

![](https://p0.ssl.qhimg.com/t01480c905d55628ffb.png)

###  ***企业资产汇总.xlsm

和上一个样本类似，该样本也是以资产为诱饵，样本打开后是一些ip地址，然后诱导用户启用宏代码以执行CobaltStrike的Payload

![](https://p4.ssl.qhimg.com/t01bc18f09837714564.png)

dump出shellcode调试可知C2：180.215.22.252

###  2021年春季学期xxx级干部专题进修班学院信息补充表.docx.exe

原始样本为双拓展名，由于Windows默认不显示后缀名，普通用户接收该文件之后很容易误以为是docx文档并双击打开，样本运行后，会读取资源加载到新分配的内存

![](https://p4.ssl.qhimg.com/t01a4ad02210ff1369f.png)

创建新线程执行资源的shellcode：

![](https://p5.ssl.qhimg.com/t017a6146abfe71b17e.png)

shellcode会多次循环解密后面的代码

![](https://p4.ssl.qhimg.com/t012cee3bd3e168a334.png)

解密后的shellcode依旧保持着较高的混淆，无法有效阅读：

![](https://p0.ssl.qhimg.com/t01ef7d1d3c1d9b6e49.png)

解密请求C2路径和请求头(User-Agent:Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0))

![](https://p3.ssl.qhimg.com/t019ae944f160ab7435.png)

设置session：Cookie:session=776t3g==

![](https://p3.ssl.qhimg.com/t01e6ade9ac504ee872.png)

对C2：hxxps://8.140.160.74:8080/Home发起请求，接收返回值

![](https://p3.ssl.qhimg.com/t011773fbbf0b0fd3d7.png)

![](https://p2.ssl.qhimg.com/t01aaeb1fb4ec8ac029.png)

###  《xxxxx》课程审核材料填报.exexxxxx

原始样本是一个C#编写的加载器，通过盗用正常Word程序的图标来迷惑用户

![](https://p0.ssl.qhimg.com/t01b780a8b226d082c9.png)

样本启动之后，会先通过AES解密硬编码的数据，在base64解码之后解压缩得到shellcode，ASE的key为：

![](https://p1.ssl.qhimg.com/t012edb3ecb974b1900.png)

这里解密的两段数据分别为一段shellcode和一个用于迷惑用户的docx文件，程序首先会通过notepad.exe加载shellcode，然后将自身移动到temp目录下并以GUID重命名，最后打开释放的docx文档。

![](https://p1.ssl.qhimg.com/t011cb6547b2c772b11.png)

解密出来的shellcode由CobaltStrike生成：

![](https://p2.ssl.qhimg.com/t0161ac4783be968a54.png)

第二段数据为docx文档：

![](https://p4.ssl.qhimg.com/t01b1e89798187d3676.png)

注入notepad.exe加载shellcode:

![](https://p2.ssl.qhimg.com/t01dcb66f65b36636d9.png)

请求C2：8.133.232.154（上海阿里云）

![](https://p4.ssl.qhimg.com/t0199ce19ccbcdcc123.png)

## 小结

通过对上面样本的分析可以看到，目前来讲，CobaltStrike和MSF依旧是红队最常用的攻击框架，大部分恶意样本都是基于这两款框架生成的，由于cs和msf支持直接导出shellcode，这使得红队/攻击者可以使用各种骚套路去编码shellcode以达到免杀的效果。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jux1a** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/237419](/post/id/237419)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [样本分析](/tag/样本分析)
  * [红蓝对抗](/tag/红蓝对抗)

 **+1** __6赞

 __收藏

![](https://p4.ssl.qhimg.com/t01c900f6a705a10464.png) jux1a

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


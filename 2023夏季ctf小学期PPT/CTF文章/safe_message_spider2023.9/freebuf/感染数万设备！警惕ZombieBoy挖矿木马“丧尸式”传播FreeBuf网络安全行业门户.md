**近日，深信服安全团队监测到一款名为ZombieBoy的木马悄然感染了国内外各个行业的用户主机。该木马包含了内网扫描、“永恒之蓝”漏洞利用、“双脉冲星”后门、挖矿工具等多个恶意模块，是一款集传播、远控、挖矿功能为一体的混合型木马。该木马的结构类似于“MassMine”，由于释放第一个恶意DLL文件时使用了一个名为ZombieBoy的工具，因此被命名为ZombieBoy挖矿木马。**

![](https://image.3001.net/images/20190711/1562806503_5d2688e7e8706.png!small)

ZombieBoy木马最早出现于2017年底，国外安全网站于2018年跟踪报道了该木马的相关分析，2018年下旬，安全媒体报道被该木马控制的主机多达七万台。日前，经深信服安全云脑数据监测发现，该木马在各个行业中迅速扩散，其中，安全防护较为薄弱的企业成为感染的重灾区，教育行业、政企单位等均受到不同程度的感染：

![](https://image.3001.net/images/20190711/1562806515_5d2688f350efd.png!small)

木马感染区域没有明确的目标，经统计，全国各省以及国外用户均存在感染现象：

![](https://image.3001.net/images/20190711/1562806548_5d2689149717d.png!small)

## 感染现象

受感染的主机上出现明显现象为未知IP策略，该策略会将除了22.148.18.88之外连接445的IP全部阻止。

![](https://image.3001.net/images/20190711/1562806572_5d26892c26255.png!small)

可疑IP地址查询为一个美国IP。

![](https://image.3001.net/images/20190711/1562806577_5d268931356c6.png!small)

搜索最新创建的TXT文件，能发现大量IP.TXT文件，是该木马内网传播模块的日志文件：

![](https://image.3001.net/images/20190711/1562806593_5d26894172ba7.png!small)

出现木马目录下恶意文件的计划任务：

![](https://image.3001.net/images/20190711/1562806618_5d26895ac22fd.png!small)

ZombieBoy木马详细分析

木马母体会在windows目录下创建一个5位随机字母的文件夹，将攻击所用到的东西以及挖矿等程序释放到该文件夹，并且会将自身拷贝到windows目录下名为boy的文件，再次拷贝自身到随机文件夹下且也为随即名，该随机文件夹的路径名称以及母体副本随机名称保存在C:\\\Windows\\\IEM\\\tps.exe中，创建tps.exe是为了进行伪装：

![](https://image.3001.net/images/20190711/1562806624_5d268960c8581.png!small)

攻击文件：

![](https://image.3001.net/images/20190711/1562806638_5d26896e2c4e9.png!small)

创建ipsec_ply和qianye等IP策略：

![](https://image.3001.net/images/20190711/1562806647_5d268977d0313.png!small)

为boy副本创建服务：

![](https://image.3001.net/images/20190711/1562806658_5d26898274db0.png!small)

创建aC.exe挖矿程序，挖矿地址为：

    
    
    44FaSvDWdKAB2R3n1XUZnjavNWwXEvyixVP8FhmccbNC6TGuCs4R937YWuoewbbSmMEsEJuYzqUwucVHhW73DwXo4ttSdNS

![](https://image.3001.net/images/20190711/1562806679_5d268997b369c.png!small)

TCP端口扫描模块在进行IP段的扫描，该扫描器为名为WinEggDrop开发的开源扫描器，其项目地址如下：

![](https://image.3001.net/images/20190711/1562806716_5d2689bc4ab63.png!small)

永恒之蓝漏洞利用工具Cstrl.exe：

![](https://image.3001.net/images/20190711/1562806734_5d2689ce9686f.png!small)

双星脉冲后门植入工具chrome.exe：

![](https://image.3001.net/images/20190711/1562806744_5d2689d8444b8.png!small)

下载可执行文件123.exe到C:\\\Windows\\\System32\\\sys.exe，并运行：

![](https://image.3001.net/images/20190711/1562806756_5d2689e40d54a.png!small)

sys.exe功能为检测是否存在C:\Windows\IEM\tps.exe，下载母体文件并执行：

![](https://image.3001.net/images/20190711/1562806786_5d268a02321bc.png!small)

其中C:\Windows\IEM\tps.exe是配置文件，保存着母体文件创建的随机文件夹路径以及自身副本的随机文件名：

![](https://image.3001.net/images/20190711/1562806791_5d268a074caa9.png!small)

接下来会访问<http://v9.monerov8.com:8800/A.txt>获取URL地址用于下载恶意文件，当前木马的URL已失效：

![](https://image.3001.net/images/20190711/1562806809_5d268a1928526.png!small)

从自身释放出并执行84.exe：

![](https://image.3001.net/images/20190711/1562806815_5d268a1f7c2a8.png!small)

生成一个随机数，判断是否大于0x32， 选择不同的端口进行下载执行母体文件并保存为las.exe：

![](https://image.3001.net/images/20190711/1562806824_5d268a2882bbe.png!small)

同样会下载执行wk.exe为CPUInfo.exe：

![](https://image.3001.net/images/20190711/1562806886_5d268a666b0c3.png!small)

从自身释放脚本文件SB360.bat到windows目录下：

![](https://image.3001.net/images/20190711/1562806898_5d268a72d0455.png!small)

该脚本内容主要是创建IP策略，屏蔽135、139、445 . . .等端口，防止用户机器被其他黑产团队进行攻击，脚本内容如下：

![](https://image.3001.net/images/20190711/1562806920_5d268a88f1518.png!small)

84.exe分析，其导出了一个Update函数：

![](https://image.3001.net/images/20190711/1562806927_5d268a8f2e307.png!small)

该样本中存储了一份DLL文件，通过解密DLL文件动态执行，然后调用84.exe的导出函数获取参数，可以直接在Update参数处设置断点(或者在LoadLibrary处进行断点，可以dump出被加密的DLL)，该DLL通过自己的Data导出函数调用Update函数：

![](https://image.3001.net/images/20190711/1562806935_5d268a97cb0f9.png!small)

检测是否存在该服务dazsks gmeakjwxo,没有就进行创建该服务：

![](https://image.3001.net/images/20190711/1562806942_5d268a9ee8f7e.png!small)

将自身拷贝到C:\windows\system32\seser.exe，并设置为隐藏属性，创建服务：

![](https://image.3001.net/images/20190711/1562806956_5d268aac517de.png!small)

删除自身：

![](https://image.3001.net/images/20190711/1562806965_5d268ab583eb2.png!small)

解密出C2地址，用于连接等：

![](https://image.3001.net/images/20190711/1562806974_5d268abe1ed3b.png!small)

Cpuinfo.exe拉起挖矿等进程，创造攻击链，其内包含了其他的样本文件：

![](https://image.3001.net/images/20190711/1562806978_5d268ac267ff7.png!small)

## 解决方案

1\. 更新MS17-010漏洞补丁；

2\. 关闭业务上不需要的端口，如135、137、138、139、445等；

3\. 深信服为广大个人用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> 64位系统下载链接：[
> _http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z_](http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z)
>
> 32位系统下载链接：[
> _http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z_](http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z)

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**


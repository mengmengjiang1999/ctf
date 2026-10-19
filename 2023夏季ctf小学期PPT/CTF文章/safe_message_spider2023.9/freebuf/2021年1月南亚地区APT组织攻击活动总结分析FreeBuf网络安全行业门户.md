## 概述

南亚地区一直以来便是APT 组织攻击活动的热点区域。从 2013 年 5月 国外安全公司披露 Hangover
行动（即摩诃草组织）以来，先后出现了多个不同命名的 APT
组织在该地域持续性的活跃，并且延伸出错综复杂的关联性，包括摩诃草、蔓灵花、肚脑虫、魔罗桫、响尾蛇等。

造成归属问题的主要因素是上述 APT
活动大多使用非特定的攻击载荷和工具，脚本化和多种语言开发的载荷往往干扰着归属分析判断，包括使用.Net、Delphi、AutoIt、Python
等。但从历史攻击活动来看，其也出现了一些共性：

> 同时具备攻击 PC 和智能手机平台能力；
>
> 巴基斯坦是主要的攻击目标，部分组织也会攻击中国境内；
>
> 政府、军事目标是其攻击的主要目标，并且投放的诱饵文档大多也围绕该类热点新闻，如克什米尔问题；

![1612751413_6020a2355d950e3fa85b9.png!small?1612751413726](https://image.3001.net/images/20210208/1612751413_6020a2355d950e3fa85b9.png!small?1612751413726)

  

2021年开年仅一个月，奇安信威胁情报中心红雨滴团队便多次捕获到该地区APT组织攻击活动。

![1612751431_6020a247a3dea5c436c15.png!small?1612751431991](https://image.3001.net/images/20210208/1612751431_6020a247a3dea5c436c15.png!small?1612751431991)

## 攻击活动分析

### 摩诃草

“摩诃草”APT团伙（APT-C-09），又称HangOver、VICEROY TIGER、The Dropping
Elephant、Patchwork，是一个来自于南亚地区的境外APT组织，该团伙已持续活跃了超过8年时间。“摩诃草”最早由Norman安全公司于2013年曝光，该组织主要针对亚洲地区和国家进行网络间谍活动，主要攻击领域为政府军事机构、科研教育等。

该组织近年来常使用携带有CVE-2017-0261漏洞利用的文档开展攻击活动，2021年1月，奇安信红雨滴团队再次捕获组织利用该漏洞的诱饵文档，相关信息如下：

 **样本名称**

|

xxx_Pakistani_fighter_planes_play_war_games.docx  
  
---|---  
  
 **MD5**

|

6d63dc5cdb504f3365403c1296e696a0  
  
 **利用方式**

|

CVE-2017-0261  
  
  

该样本以巴基斯坦空军演习为诱饵，运行后，展示诱饵内容如下图所示：

![1612751463_6020a2670ea30e32badc3.png!small?1612751463452](https://image.3001.net/images/20210208/1612751463_6020a2670ea30e32badc3.png!small?1612751463452)

该样本是一个docx格式的office文档，内部嵌入了利用CVE-2017-0261漏洞的EPS脚本，当用户打开该文档文件，office内部的EPS解释器就会执行EPS脚本触发漏洞执行恶意shellcode载荷。

![1612751488_6020a2809a4efaa406348.png!small?1612751488946](https://image.3001.net/images/20210208/1612751488_6020a2809a4efaa406348.png!small?1612751488946)

shellcode会先枚举进程并查找进程WINWORD.EXE，如果未能找到则结束运行。

![1612751495_6020a28749c39e57b6f75.png!small?1612751495645](https://image.3001.net/images/20210208/1612751495_6020a28749c39e57b6f75.png!small?1612751495645)

之后样本会在启动目录释放PE文件：MSBuild.exe，该EXE是该组织常用的FakeJLI后门。

![1612751504_6020a2909570c04027e5b.png!small?1612751504892](https://image.3001.net/images/20210208/1612751504_6020a2909570c04027e5b.png!small?1612751504892)

与之前攻击活动中的以前白加黑利用方式不同，此次文件释放过后，样本会注入shellcode到Explorer进程，Explorer进程会运行位于启动目录的后门
MSBuild.exe。

![1612751509_6020a295f2e46ceee58c9.png!small?1612751510279](https://image.3001.net/images/20210208/1612751509_6020a295f2e46ceee58c9.png!small?1612751510279)

该样本还会尝试在C:\Windows\Temp目录创建临时文件并删除，目的是检测当前触发漏洞的FLTLDR.EXE是否处于office沙箱保护模式，如果失败，则会进入提权流程，样本利用了两个CVE漏洞：CVE-2019-0808、CVE-2016-7255。

如果当前进程属于WOW64进程，则会使用前面的PE异或算法解密并内存加载针对CVE-2016-7255的提权dll文件，此过程无文件落地。

![1612751519_6020a29f8ae18548796a1.png!small?1612751520024](https://image.3001.net/images/20210208/1612751519_6020a29f8ae18548796a1.png!small?1612751520024)

![1612751545_6020a2b9366316c2015aa.png!small?1612751545561](https://image.3001.net/images/20210208/1612751545_6020a2b9366316c2015aa.png!small?1612751545561)

CVE-2016-7255提权dll信息如下

 **MD5**

|

bb238c3beff27c0be2e8f8d7dd927c1e  
  
---|---  
  
 **编译时间**

|

2017-02-27 / 17:36:45  
  
![1612751599_6020a2efdcbf7de8a42c4.png!small?1612751600120](https://image.3001.net/images/20210208/1612751599_6020a2efdcbf7de8a42c4.png!small?1612751600120)

![1612751602_6020a2f2d599ba671e06c.png!small?1612751603175](https://image.3001.net/images/20210208/1612751602_6020a2f2d599ba671e06c.png!small?1612751603175)

如果当前进程不属于WOW64进程，样本会调用ntdll的RtlDecompressBuffer函数解压并释放针对CVE-2019-0808的提权dll到文件

%ProgramData%\Microsoft\DeviceSync\pri.dll

![1612751698_6020a3524f767d9696c37.png!small?1612751698646](https://image.3001.net/images/20210208/1612751698_6020a3524f767d9696c37.png!small?1612751698646)

pri.dll经过UPX了加密，脱壳之后发现程序结构和github开源项目https://github.com/exodusintel/CVE-2019-0808
高度相似

 **文件名**

|

pri.dll  
  
---|---  
  
 **MD5**

|

7c4110a082add2fd175a5c1463e88b3e  
  
 **编译时间**

|

2020-11-26 / 18:03:32  
  
![1612751753_6020a389bf2628f8f74b2.png!small?1612751754099](https://image.3001.net/images/20210208/1612751753_6020a389bf2628f8f74b2.png!small?1612751754099)

**![1612751760_6020a39091fab15454d15.png!small?1612751761031](https://image.3001.net/images/20210208/1612751760_6020a39091fab15454d15.png!small?1612751761031)**

释放执行的MSBuild.exe信息如下：

 **MD5**

|

8B498B56FD71467657104C301A558F06  
  
---|---  
  
 **编译时间**

|

2020-12-08 / 14:50:59  
  
  

该样本时摩诃草组织常用的FakeJLI后门，指令功能如下所示：

 **指令号**

|

 **功能**  
  
---|---  
  
0

|

退出  
  
8

|

上传键盘记录文件TPX498.dat到服务器  
  
23

|

上传屏幕截图到服务器  
  
5

|

上传指定文件到服务器  
  
13

|

上传收集的特定后缀文件列表

(doc:docx:pdf:ppt:pptx:jpg:jpeg:png:rtf:txt:7z:rar:zip:docm:msg:wp)  
  
33

|

下载指定exe到本地执行  
  
4

|

重启自身进程  
  
### 魔罗桫

2020年9月中旬，奇安信威胁情报中心红雨滴团队披露了长期针对南亚大陆的攻击组织”魔罗桫”，该组织长期针对中国，巴基斯坦，尼泊尔等国和地区进行了长达数年的网络间谍攻击活动，主要针对领域为政府机构，军工企业，核能行业等。

此次捕获的样本以军事信息为诱饵信息，采用模板注入的方式从远程服务器获取公式编辑漏洞利用文档加载执行。样本基础信息如下：

 **样本名称**

|

CXXX Cruise Missiles Capabilities-Implications for the Indian Army.docx  
  
---|---  
  
 **MD5**

|

9f54962d644966cfad560cb606aeade2  
  
运行后，将从远程获取文件加载执行，并展示相关文档内容，显示的诱饵内容如下图所示：

![1612751842_6020a3e27dbb7d7d7e489.png!small?1612751842798](https://image.3001.net/images/20210208/1612751842_6020a3e27dbb7d7d7e489.png!small?1612751842798)

![1612751851_6020a3eba81121e2832ed.png!small?1612751851971](https://image.3001.net/images/20210208/1612751851_6020a3eba81121e2832ed.png!small?1612751851971)

从远程获取执行的文件是公式编辑器漏洞利用文档，相关信息如下：

 **MD5**

|

16560f7e2a3e2f53a5b07149cbf50cb0  
  
---|---  
  
 **来源**

|

hxxp://msoffice[.]user-assist[.]site/refresh/word  
  
 **利用方式**

|

公式编辑器漏洞  
  
该文件成功加载利用后，将在%temp%目录下释放bing.dll,之后加载该dll并执行其导出函数mark

![1612751873_6020a401e890d148b8282.png!small?1612751874273](https://image.3001.net/images/20210208/1612751873_6020a401e890d148b8282.png!small?1612751874273)

加载执行后，将从远程服务器hxxp://msoffice[.]user-assist[.]site/update/content下载文件并保存到C:/ProgramData/Software/update.exe。

![1612751882_6020a40a8a6609907608f.png!small?1612751882977](https://image.3001.net/images/20210208/1612751882_6020a40a8a6609907608f.png!small?1612751882977)

之后在启动项目录下创建update.lnk用以创建持久化。

![1612751890_6020a412c79bce0884157.png!small?1612751891095](https://image.3001.net/images/20210208/1612751890_6020a412c79bce0884157.png!small?1612751891095)

下载部署的update.exe基础信息如下：

 **样本名**

|

update.exe  
  
---|---  
  
 **MD5**

|

e13134c8411557ce9c9e58d57b855a62  
  
 **编译时间**

|

2021:01:03 23:35:26+00:00  
  
 **C2**

|

Synchronize[.]3utilities[.]com  
  
update.exe加载执行后，将在内存加载执行Warzone RAT

![1612751917_6020a42dd31aa81af2727.png!small?1612751918098](https://image.3001.net/images/20210208/1612751917_6020a42dd31aa81af2727.png!small?1612751918098)

  

Warzone RAT部分指令功能如下表所示：

0x2

|

当前进程列表  
  
---|---  
  
0x4

|

本地驱动器列表  
  
0x6

|

文件目录  
  
0xA

|

删除文件  
  
0xC

|

关闭指定进程  
  
0xE

|

远程执行命令  
  
0x10

|

创建互斥体  
  
0x12

|

请求摄像头使用权限  
  
0x14

|

打开摄像头  
  
0x16

|

关闭摄像头  
  
0x1A

|

清除后门，卸载自身  
  
0x1C

|

创建服务器回传文件  
  
0x20

|

获取浏览器数据  
  
0x22

|

执行文件下载  
  
0x24

|

安装在线键盘记录器  
  
0x26

|

安装离线键盘记录器  
  
0x28

|

RDP  
  
0x2A

|

反向代理  
  
0x2C

|

关闭代理  
  
0x30

|

设置VNC 端口  
  
### 蔓灵花

蔓灵花（BITTER）是疑似具有南亚背景的APT组织，因其早期特马通信的数据包头部以“BITTER”作为标识而得名。该组织主要针对周边国家地区的政府，军工业，电力，核等单位进行攻击，以窃取敏感资料为目的，具有强烈的政治背景。

近日，红雨滴团队发现BITTER组织疑似攻陷了南亚地区某国技术提供商官方网站，并在其网站中部署了恶意软件，该恶意软件基础信息如下：

 **样本名称**

|

ds.msi  
  
---|---  
  
 **MD5**

|

830561d02bfdef6282fa45a1a3cdec20  
  
 **来源**

|

http://rastek.net/gdb/ds.msi  
  
样本运行后将展示某软件安装界面，之后会提示用户安装包存在问题，无法安装，用以迷惑受害者。
**![1612751948_6020a44c29e5f4ae7e177.png!small?1612751952561](https://image.3001.net/images/20210208/1612751948_6020a44c29e5f4ae7e177.png!small?1612751952561)**

之后释放脚本文件执行，脚本文件内容如下：

![1612751961_6020a45911c44f7914565.png!small?1612751961360](https://image.3001.net/images/20210208/1612751961_6020a45911c44f7914565.png!small?1612751961360)

执行初始样本释放dsparse.exe，并添加一个名为\Windows\Wininet\CheckCacheBuffer的任务计划，该任务计划每十五分钟会通过msiexec下载并执行hxxp://rastek[.]net/HjlkYR/chkupdate.msi，不过在分析时该链接已无法访问。

![1612751970_6020a462a25b803b15ebb.png!small?1612751970972](https://image.3001.net/images/20210208/1612751970_6020a462a25b803b15ebb.png!small?1612751970972)

dsparse.exe信息如下表所示：

 **样本名称**

|

dsparse.exe  
  
---|---  
  
 **MD5**

|

562122123e57a63766737aab096d8d3c  
  
释放执行的 dsparse.exe是一个.NET 平台的Downloader,执行后首先将创建一个定时器用于与服务器通信。

![1612751986_6020a47292ec2b75a7fdc.png!small?1612751987045](https://image.3001.net/images/20210208/1612751986_6020a47292ec2b75a7fdc.png!small?1612751987045)

之后获取当前计算机用户名，系统版本，系统位数，MAC地址等信息。

![1612751992_6020a478782788fdf21dd.png!small?1612751992761](https://image.3001.net/images/20210208/1612751992_6020a478782788fdf21dd.png!small?1612751992761)

最后通过powershell向注册表添加自启项。

![1612751997_6020a47d5ba8381adecfb.png!small?1612751997692](https://image.3001.net/images/20210208/1612751997_6020a47d5ba8381adecfb.png!small?1612751997692)

当通信定时器函数触发后，将首先检测是否已成功获取MAC地址信息，若未获取成功，仍为空则再次尝试获取信息，之后通过解密函数（实为解码）解出通信服务器地址。

解码函数如下：

![1612752014_6020a48e8ff99476ddef2.png!small?1612752014885](https://image.3001.net/images/20210208/1612752014_6020a48e8ff99476ddef2.png!small?1612752014885)

从C2服务器返回数据中解析数据，下载文件执行，遗憾的是，在分析过程中，未获取到任何后续Payload文件。

### 肚脑虫

Donot“肚脑虫”（APT-C-35）是疑似具有南亚背景的APT组织，其主要以周边国家的政府机构为目标进行网络攻击活动，通常以窃取敏感信息为目的。该组织具备针对Windows与Android双平台的攻击能力。

2021年1月，红雨滴团队在日常的威胁狩猎中捕获多个该组织样本，涉及Windows以及Android平台。其中一例样本以数字丝绸之路为诱饵开展攻击，信息如下：

 **样本名称**

|

FiscalReview_July_September_2020_ace.docx  
  
---|---  
  
 **MD5**

|

c92901f2ef13374f4afd950d840e02c1  
  
该样本是公式编辑器漏洞利用文档，执行后，将展示诱饵内容迷惑受害者如下所示：

**![1612752039_6020a4a7361cab3185e9e.png!small?1612752039558](https://image.3001.net/images/20210208/1612752039_6020a4a7361cab3185e9e.png!small?1612752039558)**

漏洞利用成功后，将从远程服务器
hxxp://cdndownload[.]buzz/ace/Dq4cOqmOhfuvadroK8TGm71XOVzfnQtw获取数据执行，但遗憾的时，在分析时已无法获取。但该托管服务器还存在多个样本。

![1612752059_6020a4bb9e6c47bcf11b8.png!small?1612752059953](https://image.3001.net/images/20210208/1612752059_6020a4bb9e6c47bcf11b8.png!small?1612752059953)

其中GdnAi2lBs1MgqrjU9KRG79JR01QbcvP0.dot时公式编辑器漏洞利用文档，执行后将获取执行Donot样本执行，基础信息如下：

 **MD5**

|

eed158a07bb7964798372f5e1ab13f0c  
  
---|---  
  
 **文件名**

|

GdnAi2lBs1MgqrjU9KRG79JR01QbcvP0.dot  
  
 **漏洞利用**

|

CVE-2018-0798  
  
通过取反异或解密下方shellcode字节。

![1612752090_6020a4da881c43c5af7f8.png!small?1612752090841](https://image.3001.net/images/20210208/1612752090_6020a4da881c43c5af7f8.png!small?1612752090841)

通过URLDownloadToCacheFile下载hxxp://cdndownload.buzz/ace/GdnAi2lBs1MgqrjU9KRG79JR01QbcvP0

![1612752094_6020a4de56d8aa5f853b2.png!small?1612752094899](https://image.3001.net/images/20210208/1612752094_6020a4de56d8aa5f853b2.png!small?1612752094899)

将下载的payload取反异或后，如果首字节为0x90则代表解密正确，跳转进入payload。

![1612752111_6020a4ef4121db1dac3ce.png!small?1612752111582](https://image.3001.net/images/20210208/1612752111_6020a4ef4121db1dac3ce.png!small?1612752111582)

 **MD5**

|

93993048bdf2d3ad5824de9aca8aa1f6  
  
---|---  
  
 **样本名称**

|

FiscalReview_July_September_2020_ace.docx  
  
异或解密后续1821个字节。

![1612752149_6020a515c6a0415f34c7f.png!small?1612752150148](https://image.3001.net/images/20210208/1612752149_6020a515c6a0415f34c7f.png!small?1612752150148)

检测卡巴斯基，avast，nod32，MacFree，360杀毒软件的驱动文件。

![1612752154_6020a51a9480c2b1e85af.png!small?1612752154891](https://image.3001.net/images/20210208/1612752154_6020a51a9480c2b1e85af.png!small?1612752154891)

![1612752158_6020a51e3830ec2b72663.png!small?1612752158488](https://image.3001.net/images/20210208/1612752158_6020a51e3830ec2b72663.png!small?1612752158488)

解密后续0xD29个字节，并且再解密0x100个字节。

![1612752162_6020a52223c97b74622d0.png!small?1612752162416](https://image.3001.net/images/20210208/1612752162_6020a52223c97b74622d0.png!small?1612752162416)

![1612752165_6020a5252f906092d79bd.png!small?1612752165542](https://image.3001.net/images/20210208/1612752165_6020a5252f906092d79bd.png!small?1612752165542)

通过URLDownloadToFileA从http://cdndownload.buzz/ace/GdnAi2lBs1MgqrjU9KRG79JR01QbcvP0.dat下载文件到%Appdata%\\\wingui.dll

![1612752170_6020a52a09ff7e840e011.png!small?1612752170346](https://image.3001.net/images/20210208/1612752170_6020a52a09ff7e840e011.png!small?1612752170346)

通过URLDownloadToFileA从http://cdndownload.buzz/ace/GdnAi2lBs1MgqrjU9KRG79JR01QbcvP0.doc下载文件到%Temp%\\\doucument.doc

![1612752173_6020a52d273ad79697f8a.png!small?1612752173479](https://image.3001.net/images/20210208/1612752173_6020a52d273ad79697f8a.png!small?1612752173479)

创建名为wakeup任务计划程序，每天11：00到24：00每隔十分钟运行一次恶意dll。

![1612752182_6020a53639ec48f780bb1.png!small?1612752182522](https://image.3001.net/images/20210208/1612752182_6020a53639ec48f780bb1.png!small?1612752182522)

![1612752187_6020a53b078ff616d6a38.png!small?1612752187353](https://image.3001.net/images/20210208/1612752187_6020a53b078ff616d6a38.png!small?1612752187353)

关闭word程序，删除office各版本的Word\Resiliency键值，启动新word文件

![1612752191_6020a53f4d96f248379ef.png!small?1612752191679](https://image.3001.net/images/20210208/1612752191_6020a53f4d96f248379ef.png!small?1612752191679)

 **MD5**

|

d57e69b5e48280662bdbfbfd9fd32a33  
  
---|---  
  
 **文件名**

|

GdnAi2lBs1MgqrjU9KRG79JR01QbcvP0.dat  
  
该样本与Donot以往攻击活动中的样本类似，运行后会首先判断是否处于虚拟机环境，若检测到虚拟机则退出程序。

![1612752209_6020a551dd739d693db46.png!small?1612752210253](https://image.3001.net/images/20210208/1612752209_6020a551dd739d693db46.png!small?1612752210253)

之后获取计算机用户名，机器名等信息，格式化后与C2通信，获取其他Payload执行。
**![1612752217_6020a5596233379b80431.png!small?1612752217652](https://image.3001.net/images/20210208/1612752217_6020a5596233379b80431.png!small?1612752217652)**

![1612752226_6020a562411a2af804b56.png!small?1612752226518](https://image.3001.net/images/20210208/1612752226_6020a562411a2af804b56.png!small?1612752226518)

![1612752231_6020a56759697f10f9c5d.png!small?1612752231674](https://image.3001.net/images/20210208/1612752231_6020a56759697f10f9c5d.png!small?1612752231674)

## 总结

南亚地区APT组织活动频繁，其并不会因为被安全公司多次曝光而开始有所收敛，反而会持续更新其攻击武器库，其在2021年短短的一个月内被捕获披露的攻击活动已如此之多，尚且还有未被发现攻击。

此次捕获的样本主要针对南亚地区开展攻击活动，暂未发现影响国内用户，但防范之心不可无，奇安信威胁情报中心再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。

## IOCs

> bb1cc4ed1d3ea35305a48dfa0259208c
>
> c92901f2ef13374f4afd950d840e02c1
>
> 79b09a28e122177ba7c0e8bb77011295
>
> ac2019f08b226dc2ab5c58467a143d98
>
> 25a2df5647a72e89cd807dd313ebe5fa
>
> 242e05f06544349256470110fdb433b5
>
> 0a0dbb70a59333f3425346eaff2b2fdb
>
> a84149f859addd42e8b84ba6e1cfca8a
>
> 6d63dc5cdb504f3365403c1296e696a0
>
> 9f54962d644966cfad560cb606aeade2
>
> 16560f7e2a3e2f53a5b07149cbf50cb0s
>
> e13134c8411557ce9c9e58d57b855a62
>
> 830561d02bfdef6282fa45a1a3cdec20
>
> 562122123e57a63766737aab096d8d3c
>
> 16560f7e2a3e2f53a5b07149cbf50cb0
>
> hxxp://msoffice[.]user-assist[.]site/refresh/word
>
> hxxp://msoffice[.]user-assist[.]site/update/content
>
> hxxp://rastek[.]net/HjlkYR/chkupdate.msi
>
> Synchronize[.]3utilities[.]com
>
> hxxp://rastek[.]net/gdb/ds.msi
>
> hxxps://paf.gov-mail.net/13621/1/18844/2/0/0/1390324815/files-b74d99d6/hta

## 参考链接

<https://ti.qianxin.com/blog/articles/analysis-of-donot-apt-group-attacks-on-surrounding-areas/>

<https://mp.weixin.qq.com/s/TbiXJ359ZXOyQYWsfVDwGA>


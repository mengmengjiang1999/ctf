## 概述

蔓灵花（BITTER）是疑似具有南亚背景的APT组织，该组织长期针对中国，巴基斯坦等国家进行攻击活动，主要针对政府、军工业、电力、核能等单位进行定向攻击，窃取敏感资料。

近日，奇安信威胁情报中心在日常监控过程中发现蔓灵花APT组织开始通过邮箱投递包含有恶意脚本Chm文件的RAR压缩包，对国内外相关单位发起定向攻击，经过遥测此类的攻击行动已经持续两年，我们将其成为operation
magichm。

经过溯源，本次攻击活动中蔓灵花采用了与以往截然不同的攻击链，使用.net远控作为节点执行命令或者下发插件，并下发了一个之前从未被披露过的新模块。攻击全流程如下：

![1619488506_60876efad38041ab424e8.png!small](https://image.3001.net/images/20210427/1619488506_60876efad38041ab424e8.png!small)

## 样本分析

第一阶段样本均通过邮件进行投递，附件中包含

![1619488547_60876f2331561d64feeb0.png!small?1619488547451](https://image.3001.net/images/20210427/1619488547_60876f2331561d64feeb0.png!small?1619488547451)

启动Chm后会执行内置的恶意脚本

![1619488554_60876f2ab32463382f71f.png!small?1619488555070](https://image.3001.net/images/20210427/1619488554_60876f2ab32463382f71f.png!small?1619488555070)

创建计划任务从远程服务器下载msi并执行，通过天擎日志我们发现一个有趣的现象，受害者在16:21分时打开恶意文件创建计划任务，16:52成功从服务器下载并执行Msi文件，在c:\intel\logs\目录下释放名为dlhost.exe的payload。

 **文件名**

|

 **MD5**

|

 **类型**  
  
---|---|---  
  
 **dlhost.exe**

|

25a16b0fca9acd71450e02a341064c8d

|

PE  
  
该样本为蔓灵花组织常用的ArtraDownloader

![1619488575_60876f3fd8ae28604b14d.png!small?1619488576346](https://image.3001.net/images/20210427/1619488575_60876f3fd8ae28604b14d.png!small?1619488576346)

C2：82.221.136.27///RguhsT/accept.php?a=XX&b=XX&c=XX&d=XX&e=

但文件一落地就被天擎查杀，并没有执行后续操作，接着蔓灵花组织花了半小时的时间来替换服务器上的payload，直到17:21分时受害者才成功下载了一种免杀的Downloader，我们将其命名为MuuyDownLoader，信息如下：

 **文件名**

|

 **MD5**

|

 **类型**  
  
---|---|---  
  
 **otx_live.exe**

|

6452e2c243db03ecbcacd0419ff8bebf

|

PE  
  
创建“Check”信号量用于互斥，

![1619488596_60876f5499a40f80262d7.png!small?1619488596976](https://image.3001.net/images/20210427/1619488596_60876f5499a40f80262d7.png!small?1619488596976)

检查是否存在360totalSecurity、Tencent、kaspersky等信息，将自身拷贝到

%userprofile%\appdata\roaming\microsoft\windows\sendto命名为winupd.exe

![1619488622_60876f6ee6f563e2d76bf.png!small?1619488623226](https://image.3001.net/images/20210427/1619488622_60876f6ee6f563e2d76bf.png!small?1619488623226)

收集本机信息

![1619488636_60876f7ce9a0e9c8a0796.png!small?1619488637423](https://image.3001.net/images/20210427/1619488636_60876f7ce9a0e9c8a0796.png!small?1619488637423)

进入下载流程解密C2。访问的URL如下

 **URL**

|

 **含义**  
  
---|---  
  
OtPefhePbvw/onlinedata1inf.php?data={收集的本机数据}

|

发送本机相关信息  
  
OtPefhePbvw/datarcvoninfile.php?idata=

|

发起下载payload请求，返回payload名称  
  
OtPefhePbvw/nnodata3inf.php?inf1=

|

检查payload是否在运行  
  
OtPefhePbvw/xFiiL33i5sx/%payloadName%

|

若payload没有在运行，则下载  
  
下载成功后会存放在%userprofile%\appdata\roaming\microsoft\windows\sendto目录下，样本信息如下：

 **文件名**

|

 **MD5**

|

 **类型**  
  
---|---|---  
  
 **msmpenq.exe**

|

7cf4ea9df2f2e406fac23d71194c78fd

|

.net  
  
样本为Bitter组织常用的.net远控程序

![1619488658_60876f92ed86f3961949e.png!small?1619488659256](https://image.3001.net/images/20210427/1619488658_60876f92ed86f3961949e.png!small?1619488659256)

C2被转换为十六进制存放在配置文件中，C2:45.11.19.170:34318

![1619488667_60876f9bb2fbf0935d72a.png!small?1619488667965](https://image.3001.net/images/20210427/1619488667_60876f9bb2fbf0935d72a.png!small?1619488667965)

在以往对Bitter组织的研究中我们仅仅将.net远控作为ArtraDownloader的一个插件来看待，主要功能为窃取受害者数据，

![1619488687_60876fafce1806ce79569.png!small?1619488688223](https://image.3001.net/images/20210427/1619488687_60876fafce1806ce79569.png!small?1619488688223)

但在本次攻击活动中，我们首次发现该团伙将其作为分发插件的节点。分发的插件均做了免杀处理，信息如下：

 **文件名**

|

 **MD5**

|

 **类型**

|

 **功能**  
  
---|---|---|---  
  
 **Sysmgr.exe**

|

ade9a4ee3acbb0e6b42fb57f118dbd6b

|

VC

|

文件收集模块  
  
 **scvhost.exe**

|

578918166854037cdcf1bb3a06a7a4f3

|

VC

|

键盘记录模块  
  
 **winsync.exe**

|

eb6f0cfb0dff0f[b]504dc1f060f02adaa

|

CAB-SFX

|

备份模块  
  
值得一提的是分发插件前会使用节点远控执行cmd命令，例如会执行tasklist | find “
Sysmgr”命令来判断插件是否正在运行。下发插件后会使用schtasks命令来实现插件的持久化。

Sysmgr.exe是Bitter组织常用文件收集模块的免杀版本，在Bitter以往的攻击活动中该类型的插件名称一般都为Lsapip、Lsap、Lsapcr、Lsapc等，均由ArtraDownloader下发。

![1619488760_60876ff827e1200ea38ec.png!small?1619488760455](https://image.3001.net/images/20210427/1619488760_60876ff827e1200ea38ec.png!small?1619488760455)

之后通过POST将数据发送到远程服务器上

![1619488771_60877003489b627e03840.png!small?1619488771530](https://image.3001.net/images/20210427/1619488771_60877003489b627e03840.png!small?1619488771530)

C2：svc2mcxwave.net/UihbywscTZ/45Ugty845nv7rt.php

scvhost.exe是Bitter组织常用的键盘记录模块，在在Bitter以往的攻击活动中该类型的插件名称一般都为Igfxsrvk **、**
keylogger等名称，同样由ArtraDownloader下发

![1619488811_6087702b9a5899e4e546e.png!small?1619488812304](https://image.3001.net/images/20210427/1619488811_6087702b9a5899e4e546e.png!small?1619488812304)

winsync.exe是一款之前从未被披露的模块，我们将其称之为备用模块BackupDownloader，由CAB-SFX打包而成，执行过程中释放并执行appsync.vbs脚本。

![1619488838_60877046dd46c79f8c807.png!small?1619488839217](https://image.3001.net/images/20210427/1619488838_60877046dd46c79f8c807.png!small?1619488839217)

通过cmstp执行恶意inf脚本，inf脚本调用powershell从远程服务器下载payload（wdisvcnotifyhost.com/n9brCs21/apprun），最后将其注册为计划任务实现持久化。

我们观察到当核心.net节点正常运行时，远程服务器上的Payload一直处于404状态，当核心节点被杀软或者人工清除，攻击者才会在远程服务器上传免杀后的核心节点，核心节点复活后，攻击者首先执行了键盘记录模块，并使用cmd命令评估损失情况。

## 关联分析

基于奇安信遥测数据，我们发现Bitter APT组织最晚于2019年中时开始投递恶意Chm邮件，历史捕获到的样本如下：

 **文件名**

|

 **URL**  
  
---|---  
  
 **20210225.doc.chm**

|

http://youxiangxiezhu.com/youxi/crt.php?h=  
  
 **Suspicious NTC Mail Server Access Logs.chm**

|

http://sartetextile.com/img/wnsetup.msi  
  
 **海事政策分析和对南亚的港口安全影响** **.chm**

|

http://windiagnosticsvc.net/jscript/jsp.php?h=  
  
 **SHIPMENT TO PNS INVOICE NO 03021.chm**

|

http://myprivatehostsvc.com/br/js.php?h=  
  
 **SOP for Logging out Mail and PCs.chm**

|

http://myprivatehostsvc.com/xuisy/css.php?h=  
  
 **Invitation To Roundtable.chm**

|

http://msisspsvc.net/img/msiwindef.msi  
  
 **日程安排** **.chm**

|

http://w32timeslicesvc.net/jscript/jsp.php?h=  
  
 **remote.chm**

|

http://sartetextile.com/img/wnsetup.msi  
  
 **MyPictures.jpg.chm**

|

https://bheragreens.com/img/winsupdater.msi  
  
 **附件** **-** **会议** **.chm**

|

http://webmailcgwip.com/xingsu/asp.php?h=  
  
 **…**

|

…  
  
本次活动使用的MuuyDownLoader最早可以追溯到2019年

 **文件名**

|

 **MD5**

|

 **ITW**  
  
---|---|---  
  
 **wupdte**

|

4bcfb31d0e3df826d3615a41149ebf9c

|

http://galluppakistan.com/images/wupdte  
  
 **wupd.msi**

|

f38b9ac9d6a1070ac9dbae6f30c1f8aa

|

  
  
  
老版本的样本包含PDB：

 **PDB**  
  
---  
  
 **C:\Users\user\Desktop\360ActiveDefence 1.4 Sep2019\360ActiveDefence 1.4
V2\Release\360ActiveDefence.pdb**  
  
新老版本代码结构相似度极高

![1619488892_6087707c233b045dd88a6.png!small?1619488892688](https://image.3001.net/images/20210427/1619488892_6087707c233b045dd88a6.png!small?1619488892688)

## 总结

BITTER
APT组织是一个长期活跃的境外网络攻击组织，且长期针对国内开展攻击活动，奇安信红雨滴团队提醒广大用户，切勿打开社交媒体分享的来历不明的链接，不点击执行未知来源的邮件附件，不运行夸张的标题的未知文件。做到及时备份重要文件，更新安装补丁。

若需运行、安装来历不明的应用，可先通过奇安信威胁情报文件深度分析平台（https://sandbox.ti.qianxin.com/sandbox/page）进行简单判别。目前已支持包括Windows、安卓平台在内的多种格式文件深度分析。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC、奇安信态势感知等，都已经支持对此类攻击的精确检测。

![1619488939_608770aba8ef755bb48cd.png!small?1619488939955](https://image.3001.net/images/20210427/1619488939_608770aba8ef755bb48cd.png!small?1619488939955)

## IOC

所涉及的目录：

> \intel\logs
>
> %userprofile%\appdata\roaming\programdata
>
> %userprofile%\appdata\roaming\
>
> %userprofile%\appdata\roaming\microsoft\windows\sendto
>
> \windows\debug\wia

恶意文件名称：

> scvhost.exe
>
> otx_live.exe
>
> winupd.exe
>
> winmgr.exe
>
> msmpenq.exe
>
> sysmgr.exe
>
> winsync.exe
>
> winsc.exe
>
> winapirun.exe

MD5:

> 6452e2c243db03ecbcacd0419ff8bebf
>
> 2cb0b743e4ff348c1ec16d1d0dd06092
>
> 578918166854037cdcf1bb3a06a7a4f3
>
> 6452e2c243db03ecbcacd0419ff8bebf
>
> 7cf4ea9df2f2e406fac23d71194c78fd
>
> ade9a4ee3acbb0e6b42fb57f118dbd6b
>
> eb6f0cfb0dff0f[b]504dc1f060f02adaa

C2:

> 82.221.136.27:80
>
> 45.11.19.170:34318
>
> 193.142.58.186:80

URL:

> http://youxiangxiezhu.com/youxi/crt.php?h=
>
> http://sartetextile.com/img/wnsetup.msi
>
> http://windiagnosticsvc.net/jscript/jsp.php?h=
>
> http://myprivatehostsvc.com/br/js.php?h=
>
> http://myprivatehostsvc.com/xuisy/css.php?h=
>
> http://msisspsvc.net/img/msiwindef.msi
>
> http://w32timeslicesvc.net/jscript/jsp.php?h=
>
> http://sartetextile.com/img/wnsetup.msi
>
> https://bheragreens.com/img/winsupdater.msi
>
> http://webmailcgwip.com/xingsu/asp.php?h=
>
> http://otx.gxwxtvonline.com/OtPefhePbvw/datarcvoninfile.php
>
> http://svc2mcxwave.net/UihbywscTZ/45Ugty845nv7rt.php
>
> http://wdisvcnotifyhost.com/n9brCs21/apprun


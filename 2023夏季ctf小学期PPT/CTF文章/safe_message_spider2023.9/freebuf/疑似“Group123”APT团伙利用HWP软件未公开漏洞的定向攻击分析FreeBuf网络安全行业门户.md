## 背景  

2018年9月20日，360威胁情报中心在日常样本分析与跟踪过程中发现了一例针对韩国文字处理软件Hancom
Office设计的漏洞攻击样本。通过详细分析发现，该样本疑似与APT组织“Group 123”相关，且该HWP样本利用了一个从未公开披露的Hancom
Office漏洞来执行恶意代码。360威胁情报中心通过对该漏洞进行详细分析后发现，这是Hancom
Office在使用开源Ghostscript（下称GS）引擎时未正确使用GS提供的沙盒保护功能而导致的任意文件写漏洞。

360威胁情报中心通过对已知的HWP相关漏洞检索后发现，该漏洞疑似从未被公开（没有任何信息来源对该漏洞进行过描述或者分析，也没有漏洞相关的CVE等信息）。幸运的是，由于版权相关问题，最新版的HancomOffice已经将GS开源组件移除，使问题在最新的软件中得到缓解，但老版本的用户依然受影响，而且此类用户的数量还很大。

而截止我们发布本篇报告时，VirusTotal上针对该攻击样本的查杀效果如下，也仅仅只有5家杀软能检查出其具有恶意行为：

  

![image.png](https://image.3001.net/images/20181108/1541655969_5be3cda1e3f77.png!small)

## Hancom Office

HWP的全称为Hangul Word
Processor，意为Hangul文字处理软件，其是Hancom公司旗下的产品，该公司为韩国的政府所支持的软件公司。Hancom
Office办公套件在韩国是非常流行的办公文档处理软件，有超过75%以上的市场占有率。

Hancom公司目前主要的是两个产品系列，一个是Hancom Office，另一个是ThinkFree Office。Hancom
Office套件里主要包含HanCell（类似微软的Excel），HanShow
（类似微软的PowerPoint），HanWord（也就是HWP，类似微软的Office Word）等。

而在它的官网提供两种语言（英文和韩文），当你以英文的界面语言去访问该网站时，它的下载中心里所提供的只有ThinkFree
Office的系列产品，当以韩文界面语言去访问时，它的下载中心里所提供的是Hancom
Office系列产品，可以看出Hancom公司针对国内还是主推Hancom Office的产品，针对其他非韩文国家则推送ThinkFree
Office的系列产品：

  

![image.png](https://image.3001.net/images/20181108/1541655979_5be3cdab1a0eb.png!small)

## HWP未公开漏洞分析

360威胁情报中心针对该未公开HWP漏洞的整个分析过程如下。

### 利用效果

使用安装了HancomOffice Hwp 2014（9.0.0.1086）的环境打开捕获到的恶意HWP文档，以下是Hancom Office版本信息：

  

![image.png](https://image.3001.net/images/20181108/1541655985_5be3cdb1d26a6.png!small)

HWP样本打开后不会弹出任何提示框，也不会有任何卡顿，便会静默在当前用户的启动目录释放恶意脚本UpgradeVer45.bat，并且在%AppData%目录下释放Dhh01.oju01和Dhh02.oju01文件，如下图：

  

![image.png](https://image.3001.net/images/20181108/1541655991_5be3cdb7e310e.png!small)

通过进程行为分析可以发现，这其实是Hancom Office自带的gbb.exe程序执行了恶意文件的释放操作：

  

![image.png](https://image.3001.net/images/20181108/1541655998_5be3cdbe4e323.png!small)

而gbb.exe其实是HancomOffice用于处理HWP文件中内嵌的EPS脚本的一个外壳程序，其核心是调用了开源GhostScript（下称GS）组件gsdll32.dll来处理EPS脚本：

  

![image.png](https://image.3001.net/images/20181108/1541656005_5be3cdc5ccf24.png!small)

gbb.exe解析EPS文件所执行的命令行如下：

所以该恶意HWP样本极有可能是通过内嵌的EPS脚本触发漏洞来实现释放恶意文件的。为了验证该想法，360威胁情报中心的研究人员提取了HWP文件中的EPS文件后，使用HWP自带的EPS脚本解析程序gbb.exe来模拟Hancom
Office解析该脚本（向gbb.exe传入了Hancom
Office解析EPS脚本文件时相同的参数列表），也可达到相同的效果（Windows启动项被写入恶意脚本）：

  

![image.png](https://image.3001.net/images/20181108/1541656015_5be3cdcfb3e75.png!small)

### 漏洞分析过程

既然确定了该恶意HWP样本是利用了解析EPS脚本的相关漏洞来释放恶意文件的，那么我们通过深入分析HWP文件携带的EPS脚本即可找到漏洞成因。

#### EPS/PS、PostScript以及GhostScript项目

在分析该漏洞前，我们需要了解一些关于EPS/PS和PostScript以及GhostScript项目的相关知识。

**1.** **EPS** **（** **Encapsulated Post Script** **）** ****

EPS是Encapsulated Post
Script的缩写，是一个专用的打印机描述语言，可以描述矢量信息和位图信息，支持跨平台。是目前桌面印刷系统普遍使用的通用交换格式当中的一种综合格式。EPS/PS文件格式又被称为带有预视图象的PS文件格式，它是由一个PostScript语言的文本文件和一个（可选）低分辨率的由PICT或TIFF格式描述的代表像组成。其中，PostScript是一种用来描述列印图像和文字的编程语言，该编程语言提供了丰富的API，包括文件读写等功能：

  

![image.png](https://image.3001.net/images/20181108/1541656023_5be3cdd791e4a.png!small)

 **2.** **GhostScript** **项目** ****

GhostScript项目是一套Post Script语言的解释器软件。可对Post Script语言进行绘图，支持Post Script与PDF互相转换。
换言之，该项目可以解析渲染EPS图像文件。而Hangul正是利用此开源项目支持EPS文件渲染。

#### 提取HWP中的EPS脚本

要分析HWP中的EPS脚本，需要将EPS脚本提取出来。而HWP文件本质上是OLE复合文件，EPS则作为复合文件流存储在HWP文件中，可以用现有工具oletools、StructuredStorage
eXplorer、Structured Storage Viewer等工具查看和提取，以下是StructuredStorage
eXplorer工具查看的效果图：

  

![image.png](https://image.3001.net/images/20181108/1541656030_5be3cddeb67fc.png!small)

而HWP文件中的大部分流都是经过zlibraw deflate压缩存储的，EPS流也不例外。可以通过Python解压缩恶意HWP文件中的EPS流，代码如下：

![image.png](https://image.3001.net/images/20181108/1541656208_5be3ce9092bdf.png!small)  

以下是解压缩后的恶意EPS文件内容：

![image.png](https://image.3001.net/images/20181108/1541656222_5be3ce9ec9c79.png!small)  

#### 恶意EPS脚本分析

解压后的恶意PostScript脚本功能分析如下：

第1行为注释代码，表示使用Adobe-3.0、EPSF-3.0标准。  
---  
第3-8行定义了一个字符串拼接函数catme，类似C语言中的strcat函数。  
第10行获取%AppData%环境变量并存储于变量envstr中。  
第11行利用catme函数拼接出文件路径并存储于变量path1中。  
第12、13行含义同11行。  
第14行采用写入的方式打开%AppData%\Microsoft\Windows\Start
Menu\Programs\StartUp\UpgradeVer45.bat文件并将文件句柄存储于变量file1中。  
第15行将字符串“copy /b … WinUpdate148399843.pif”写入path1中。  
第16行关闭file1。  
第17行以写入方式打开%AppData%\Dhh01.oju01文件。  
第18行写入PE文件头MZ标识到%AppData%\Dhh01.oju01文件。  
第19-36行将后面的16进制字符串写入文件%AppData%\Dhh02.oju01。  
  
#### 未正确使用GhostScript提供的沙盒保护导致任意文件写漏洞

可以看到，整个EPS脚本中并没有任何已知漏洞相关的信息，脚本功能是直接将恶意文件写入到了Windows启动项，这显然脱离了一个图像解析脚本的正常功能范围。

我们在翻阅了GhostScript开源组件的说明后发现，GhostScript其实提供了一个名为“-dSAFER”的参数来将EPS脚本的解析过程放到安全沙箱中执行，以防止诸如任意文件写这类高危操作发生。

而Hancom
Office在解析处理HWP文件中包含的EPS文件时，会调用自身安装目录下的gbb.exe。gbb.exe内部最终会调用同目录的GhostScript开源组件gsdll32.dll来解析和显示EPS图像：

![image.png](https://image.3001.net/images/20181108/1541656235_5be3ceabc56a4.png!small)  

可以很明显的看到，Hancom Office在调用GhostScript开源组件的过程中没有使用-dSAFER参数，使得EPS解析过程并没有在沙箱中执行，也就是说PostScript脚本的所有操作均在真实环境中。这自然就导致了Hancom
Office允许EPS脚本执行任意文件写。

至此，我们可以很清楚的认定，该漏洞成因为Hancom
Office未正确使用GhostScript（开源EPS解析组件）提供的沙盒保护而导致了任意文件写漏洞。

  

360威胁情报中心安全研究员通过手动调用gswin32.exe（GhostScript提供的一个解析EPS脚本的外壳程序）来解析恶意EPS文件，并加上了-dSAFER参数，此时gswin32.exe提示“invalidfileaccess”，即未能将文件写入到磁盘（写入启动项失败，这也反面证明了漏洞的成因）。如下图：

![image.png](https://image.3001.net/images/20181108/1541656243_5be3ceb3e6f22.png!small)  

### 受影响软件版本

理论上2017年5月之前开发的支持EPS脚本解析的Hancom Office软件都受该漏洞影响。

### 漏洞时间线

![image.png](https://image.3001.net/images/20181108/1541656257_5be3cec133d92.png!small)  

截止目前，Hangul Office产品线已经有了很多版本分支，而至少在Hangul
2010就引入了GhostScript开源组件用于解析EPS文件。根据维基百科资料显示：在2017年5月由于Hangul
Office产品线使用了GhostScript组件而没有开源，这一行为违反了GhostScript的开源协议GUN GPL，被要求开源其产品的源代码。

![image.png](https://image.3001.net/images/20181108/1541656264_5be3cec864f32.png!small)  

鉴于此版权问题，Hangul在Hangul NEO(2016)的后续版本中去除了GhostScript开源组件。并且在我们测试的Hangul
2014的最新更新中，已经剔除了老版本中的GhostScript开源组件，这变相的消除了该漏洞隐患。

## 恶意样本Payload分析

### 漏洞利用文档

漏洞利用文档是名为“7주 신뢰와 배려의 커뮤니케이션.hwp(7周信任和关怀的交流)”

文档内容如下：

![image.png](https://image.3001.net/images/20181108/1541656290_5be3cee2b5f12.png!small)  

成功利用后会在当前用户的启动目录释放UpgradeVer45.bat脚本，并且在%appdata%目录下释放Dhh01.oju01和Dhh02.oju01文件，当用户重新登录时，UpgradeVer45.bat会将%appdata%目录下释放的两个文件合并为WinUpdate148399843.pif文件。

  

![image.png](https://image.3001.net/images/20181108/1541656296_5be3cee8bd830.png!small)

### WinUpdate148399843.pif

WinUpdate148399843.pif文件则是一个PE文件，该文件使用Themida加壳：

  

![image.png](https://image.3001.net/images/20181108/1541656305_5be3cef136154.png!small)

使用OD脚本脱壳后进行分析，样本执行后首先检测进程路径是否包含”WinUpdate”（样本本身包含的名字），若不是则退出：

  

![image.png](https://image.3001.net/images/20181108/1541656311_5be3cef72220d.png!small)

进而检测启动项目录下是否有以”UpgradeVer”开头的文件

  

![image.png](https://image.3001.net/images/20181108/1541656315_5be3cefb69381.png!small)

样本还会进行反调试检测：

  

![image.png](https://image.3001.net/images/20181108/1541656326_5be3cf064a954.png!small)

随后，样本会执行%system32%下的sort.exe程序：

  

![image.png](https://image.3001.net/images/20181108/1541656331_5be3cf0b185f3.png!small)

之后利用WriteProcessMemory，RtlCreateUserThread向sort.exe注入一段ShellCode执行：

  

![image.png](https://image.3001.net/images/20181108/1541656337_5be3cf113c0d8.png!small)

### ShellCode

注入的ShellCode首先会通过IsDebuggerPresent检测是否处于调试状态：

  

![image.png](https://image.3001.net/images/20181108/1541656342_5be3cf16c80a6.png!small)

并通过与“E2F9FC8F”异或解密出另一个PE文件：

  

![image.png](https://image.3001.net/images/20181108/1541656347_5be3cf1be1c53.png!small)

最后内存执行解密后的PE文件：

  

![image.png](https://image.3001.net/images/20181108/1541656355_5be3cf232b057.png!small)

### ROKRAT

最终解密后的PE文件是ROKRAT家族的远控木马，该木马会获取计算机名称、用户名、并通过smbios判断计算机类型：

  

![image.png](https://image.3001.net/images/20181108/1541656364_5be3cf2c20857.png!small)

  

![image.png](https://image.3001.net/images/20181108/1541656369_5be3cf318d005.png!small)

随后会进行沙箱执行环境检测：

  

![image.png](https://image.3001.net/images/20181108/1541656376_5be3cf38c546e.png!small)

如果检测到存在”C:\ProgramFiles\VMware\VMware
Tools\vmtoolsd.exe”路径则会往MBR中写入”FAAAA…Sad…”字符串：

  

![image.png](https://image.3001.net/images/20181108/1541656381_5be3cf3dbb8e7.png!small)

写入之后通过shutdown命令重启电脑：

  

![image.png](https://image.3001.net/images/20181108/1541656387_5be3cf43d2854.png!small)

重启后开机显示画面：

  

![image.png](https://image.3001.net/images/20181108/1541656396_5be3cf4c953e2.png!small)

如果样本未检测到沙箱运行环境，则会执行后续的主要功能，包括获取屏幕截图：

  

![image.png](https://image.3001.net/images/20181108/1541656400_5be3cf5086e90.png!small)

并通过网盘上传数据，网盘的APIKey会内置在样本数据里。下图为提取到的字符串的信息，样本会通过API调用4个国外主流的网盘包括：pcloud、box、dropbox、yandex

  

![image.png](https://image.3001.net/images/20181108/1541656406_5be3cf56cac1b.png!small)

API KEY通过解密获取，解密函数如下：

  

![image.png](https://image.3001.net/images/20181108/1541656412_5be3cf5c00612.png!small)

  

![image.png](https://image.3001.net/images/20181108/1541656417_5be3cf610b373.png!small)

尝试向网盘上传数据：

  

![image.png](https://image.3001.net/images/20181108/1541656421_5be3cf6570c44.png!small)

## 溯源与关联

360威胁情报中心通过内部威胁情报平台以及公开情报进行关联，发现此次攻击事件疑似为APT组织“Group 123”所为，关联依据如下：

Group 123团伙曾在多次活动使用ROKRAT：

  

![image.png](https://image.3001.net/images/20181108/1541656426_5be3cf6ad707d.png!small)

且在2017年3月的攻击活动使用的样本也会判断当处于虚拟机环境下时，会向MBR写入字符串“Are you
Happy”，而在本次活动中，同样的向MBR写入了字符串“FAAAA…Sad…”：

  

![image.png](https://image.3001.net/images/20181108/1541656432_5be3cf701243a.png!small)

  

![image.png](https://image.3001.net/images/20181108/1541656436_5be3cf746371a.png!small)

并且本次捕获的样本代码片段和之前的基本一致，我们在这里选取Group 123曾使用的ROKRAT（MD5:
bedc4b9f39dcc0907f8645db1acce59e）进行对比，如下图可见，代码结构基本相同：

  

![image.png](https://image.3001.net/images/20181108/1541656440_5be3cf784a122.png!small)

## 总结

360威胁情报中心本次分析的HWP漏洞的根本原因是Hangul Office在使用GS引擎解析PostScript脚本时没有合理使用沙箱功能，即忽略了-dSAFER的沙箱选项。在这种情况下，攻击者只需要通过PostScript脚本将恶意软件写入到启动项或者其它系统劫持路径中，当用户重新启动操作系统或者触发劫持时就达到执行恶意代码的目的。虽然相关的漏洞在最新版本的Hancom
Office软件中不再存在，但依然有大量的老版本用户暴露在这个免杀效果非常好的漏洞之下，成为攻击执行针对性的入侵的有效工具，360威胁情报中心在此通过本文向公众提醒这类攻击的威胁以采取必要的防护措施。

## IOC

**说明** |  **MD5**  
---|---  
HWP文档  |  3f92afe96b4cfd41f512166c691197b5  
UpgradeVer45.bat  |  726ef3c8df210b1536dbd54a5a1c74df  
Dhh01.oju01  |  ac6ad5d9b99757c3a878f2d275ace198  
Dhh02.oju02  |  d3f076133f5f72b9d1a55f649048b42d  
WinUpdate148399843.pif  |  6ec89edfffdb221a1edbc9852a9a567a  
ROKRAT远控  |  7a751874ea5f9c95e8f0550a0b93902d  
  
## 参考

[1].https://blog.talosintelligence.com/2018/01/korea-in-crosshairs.html

[2].https://ti.360.net/blog/articles/analysis-of-cve-2018-4878/

[3].[https://zenhax.com/viewtopic.php?f=4&t=1051](https://zenhax.com/viewtopic.php?f=4&t=1051)

[4].https://en.wikipedia.org/wiki/HancomOffice_(word_processor)

[5].https://en.wikipedia.org/wiki/Hancom

[6].https://hancom.com


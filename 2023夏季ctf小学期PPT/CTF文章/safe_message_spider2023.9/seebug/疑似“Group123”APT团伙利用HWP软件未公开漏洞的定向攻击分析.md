**作者：360威胁情报中心  
公众号： [360威胁情报中心](https://mp.weixin.qq.com/s/X8Iz26L1k5ibdqv3lKFHKg
"360威胁情报中心")**

### 背景

2018年9月20日，360威胁情报中心在日常样本分析与跟踪过程中发现了一例针对韩国文字处理软件Hancom
Office设计的漏洞攻击样本。通过详细分析发现，该样本疑似与APT组织“Group 123”相关，且该HWP样本利用了一个从未公开披露的Hancom
Office漏洞来执行恶意代码。360威胁情报中心通过对该漏洞进行详细分析后发现，这是Hancom
Office在使用开源Ghostscript（下称GS）引擎时未正确使用GS提供的沙盒保护功能而导致的任意文件写漏洞。

360威胁情报中心通过对已知的HWP相关漏洞检索后发现，该漏洞疑似从未被公开（没有任何信息来源对该漏洞进行过描述或者分析，也没有漏洞相关的CVE等信息）。幸运的是，由于版权相关问题，最新版的HancomOffice已经将GS开源组件移除，使问题在最新的软件中得到缓解，但老版本的用户依然受影响，而且此类用户的数量还很大。

而截止我们发布本篇报告时，VirusTotal上针对该攻击样本的查杀效果如下，也仅仅只有5家杀软能检查出其具有恶意行为：

![
](https://images.seebug.org/content/images/2018/11/9f42f326-58ca-4d78-8d70-b47e854e66e0.jpg-w331s)

### Hancom Office

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

![
](https://images.seebug.org/content/images/2018/11/1bf373f5-0e2a-4c47-a84c-a8de883225ab.png-w331s)

### HWP未公开漏洞分析

360威胁情报中心针对该未公开HWP漏洞的整个分析过程如下。

#### 利用效果

使用安装了HancomOffice Hwp 2014（9.0.0.1086）的环境打开捕获到的恶意HWP文档，以下是Hancom Office版本信息：

![
](https://images.seebug.org/content/images/2018/11/73650103-76d0-4335-9b97-ad1c6b2a1ed3.png-w331s)

HWP样本打开后不会弹出任何提示框，也不会有任何卡顿，便会静默在当前用户的启动目录释放恶意脚本UpgradeVer45.bat，并且在%AppData%目录下释放Dhh01.oju01和Dhh02.oju01文件，如下图：

![
](https://images.seebug.org/content/images/2018/11/87b044cb-d9f3-43a6-9b55-6f5b92ce5735.png-w331s)

通过进程行为分析可以发现，这其实是Hancom Office自带的gbb.exe程序执行了恶意文件的释放操作：

![
](https://images.seebug.org/content/images/2018/11/18e2e36e-a42a-448b-8ea6-ec928fd642b1.png-w331s)

而gbb.exe其实是HancomOffice用于处理HWP文件中内嵌的EPS脚本的一个外壳程序，其核心是调用了开源GhostScript（下称GS）组件gsdll32.dll来处理EPS脚本：

![
](https://images.seebug.org/content/images/2018/11/ac61a3fc-1261-4c98-8a24-2728f3132ffd.png-w331s)

gbb.exe解析EPS文件所执行的命令行如下：

    
    
    "C:\Program  Files\Hnc\HOffice9\Bin\ImgFilters\gs\gs8.71\bin\gbb.exe"  "C:\Users\admin\AppData\Local\Temp\Hnc\BinData\EMB000009b853ef.eps"  "C:\Users\admin\AppData\Local\Temp\gsbF509.tmp"

所以该恶意HWP样本极有可能是通过内嵌的EPS脚本触发漏洞来实现释放恶意文件的。为了验证该想法，360威胁情报中心的研究人员提取了HWP文件中的EPS文件后，使用HWP自带的EPS脚本解析程序gbb.exe来模拟Hancom
Office解析该脚本（向gbb.exe传入了Hancom
Office解析EPS脚本文件时相同的参数列表），也可达到相同的效果（Windows启动项被写入恶意脚本）：

![
](https://images.seebug.org/content/images/2018/11/ea99420e-54c6-4e9d-8150-6d93c41abbe7.png-w331s)

#### 漏洞分析过程

既然确定了该恶意HWP样本是利用了解析EPS脚本的相关漏洞来释放恶意文件的，那么我们通过深入分析HWP文件携带的EPS脚本即可找到漏洞成因。

##### EPS/PS、PostScript以及GhostScript项目

在分析该漏洞前，我们需要了解一些关于EPS/PS和PostScript以及GhostScript项目的相关知识。

###### 1\. EPS（Encapsulated Post Script）

EPS是Encapsulated Post
Script的缩写，是一个专用的打印机描述语言，可以描述矢量信息和位图信息，支持跨平台。是目前桌面印刷系统普遍使用的通用交换格式当中的一种综合格式。EPS/PS文件格式又被称为带有预视图象的PS文件格式，它是由一个PostScript语言的文本文件和一个（可选）低分辨率的由PICT或TIFF格式描述的代表像组成。其中，PostScript是一种用来描述列印图像和文字的编程语言，该编程语言提供了丰富的API，包括文件读写等功能：

![
](https://images.seebug.org/content/images/2018/11/6ea62d77-2477-4fd9-8b7f-613295d45051.png-w331s)

###### 2\. GhostScript项目

GhostScript项目是一套Post Script语言的解释器软件。可对Post Script语言进行绘图，支持Post
Script与PDF互相转换。换言之，该项目可以解析渲染EPS图像文件。而Hangul正是利用此开源项目支持EPS文件渲染。

##### 提取HWP中的EPS脚本

要分析HWP中的EPS脚本，需要将EPS脚本提取出来。而HWP文件本质上是OLE复合文件，EPS则作为复合文件流存储在HWP文件中，可以用现有工具oletools、StructuredStorage
eXplorer、Structured Storage Viewer等工具查看和提取，以下是StructuredStorage
eXplorer工具查看的效果图：

![
](https://images.seebug.org/content/images/2018/11/e7c250e0-07ca-4dea-b592-a8687ba20ba7.png-w331s)

而HWP文件中的大部分流都是经过zlibraw deflate压缩存储的，EPS流也不例外。可以通过Python解压缩恶意HWP文件中的EPS流，代码如下：

![
](https://images.seebug.org/content/images/2018/11/2f6ddaa3-4fe4-4280-b61a-767bfa433aae.png-w331s)

以下是解压缩后的恶意EPS文件内容：

![
](https://images.seebug.org/content/images/2018/11/e5c6871e-2ade-4239-ae56-49dd1e3451e4.png-w331s)

##### 恶意EPS脚本分析

解压后的恶意PostScript脚本功能分析如下：

    
    
    第1行为注释代码，表示使用Adobe-3.0、EPSF-3.0标准。
    
    第3-8行定义了一个字符串拼接函数catme，类似C语言中的strcat函数。
    
    第10行获取%AppData%环境变量并存储于变量envstr中。
    
    第11行利用catme函数拼接出文件路径并存储于变量path1中。
    
    第12、13行含义同11行。
    
    第14行采用写入的方式打开%AppData%\Microsoft\Windows\Start  Menu\Programs\StartUp\UpgradeVer45.bat文件并将文件句柄存储于变量file1中。
    
    第15行将字符串“copy /b … WinUpdate148399843.pif”写入path1中。
    
    第16行关闭file1。
    
    第17行以写入方式打开%AppData%\Dhh01.oju01文件。
    
    第18行写入PE文件头MZ标识到%AppData%\Dhh01.oju01文件。
    
    第19-36行将后面的16进制字符串写入文件%AppData%\Dhh02.oju01。

##### 未正确使用GhostScript提供的沙盒保护导致任意文件写漏洞

可以看到，整个EPS脚本中并没有任何已知漏洞相关的信息，脚本功能是直接将恶意文件写入到了Windows启动项，这显然脱离了一个图像解析脚本的正常功能范围。

我们在翻阅了GhostScript开源组件的说明后发现，GhostScript其实提供了一个名为“-dSAFER”的参数来将EPS脚本的解析过程放到安全沙箱中执行，以防止诸如任意文件写这类高危操作发生。

而Hancom
Office在解析处理HWP文件中包含的EPS文件时，会调用自身安装目录下的gbb.exe。gbb.exe内部最终会调用同目录的GhostScript开源组件gsdll32.dll来解析和显示EPS图像：

![ ](https://images.seebug.org/content/images/2018/11/6c79fc5a-1f13-449c-aafd-fa9d47651795.png-w331s)

可以很明显的看到，Hancom Office在调用GhostScript开源组件的过程中没有使用-dSAFER参数，使得EPS解析过程并没有在沙箱中执行，也就是说PostScript脚本的所有操作均在真实环境中。这自然就导致了Hancom
Office允许EPS脚本执行任意文件写。

至此，我们可以很清楚的认定，该漏洞成因为Hancom
Office未正确使用GhostScript（开源EPS解析组件）提供的沙盒保护而导致了任意文件写漏洞。

360威胁情报中心安全研究员通过手动调用gswin32.exe（GhostScript提供的一个解析EPS脚本的外壳程序）来解析恶意EPS文件，并加上了-dSAFER参数，此时gswin32.exe提示“invalidfileaccess”，即未能将文件写入到磁盘（写入启动项失败，这也反面证明了漏洞的成因）。如下图：

![ ](https://images.seebug.org/content/images/2018/11/ebe0d61b-1092-47ba-ba6b-98a006db9e2b.png-w331s)

#### 受影响软件版本

理论上2017年5月之前开发的支持EPS脚本解析的Hancom Office软件都受该漏洞影响。

#### 漏洞时间线

![
](https://images.seebug.org/content/images/2018/11/af78efda-8a69-4c0b-af91-9e89578930a4.png-w331s)

截止目前，Hangul Office产品线已经有了很多版本分支，而至少在Hangul
2010就引入了GhostScript开源组件用于解析EPS文件。根据维基百科资料显示：在2017年5月由于Hangul
Office产品线使用了GhostScript组件而没有开源，这一行为违反了GhostScript的开源协议GUN GPL，被要求开源其产品的源代码。

![
](https://images.seebug.org/content/images/2018/11/0bc8d21d-6e0b-439c-904b-945b3ca01b58.png-w331s)

鉴于此版权问题，Hangul在Hangul NEO(2016)的后续版本中去除了GhostScript开源组件。并且在我们测试的Hangul
2014的最新更新中，已经剔除了老版本中的GhostScript开源组件，这变相的消除了该漏洞隐患。

### 恶意样本Payload分析

#### 漏洞利用文档

漏洞利用文档是名为“7주 신뢰와 배려의 커뮤니케이션.hwp(7周信任和关怀的交流)”

文档内容如下：

![
](https://images.seebug.org/content/images/2018/11/10ba9cf4-d5d3-42a8-8827-a8fc6b6696fa.png-w331s)

成功利用后会在当前用户的启动目录释放UpgradeVer45.bat脚本，并且在%appdata%目录下释放Dhh01.oju01和Dhh02.oju01文件，当用户重新登录时，UpgradeVer45.bat会将%appdata%目录下释放的两个文件合并为WinUpdate148399843.pif文件。

![
](https://images.seebug.org/content/images/2018/11/50450fb2-dceb-49af-8eb6-cf73c6617fd6.png-w331s)

#### WinUpdate148399843.pif

WinUpdate148399843.pif文件则是一个PE文件，该文件使用Themida加壳：

![
](https://images.seebug.org/content/images/2018/11/000aec67-4cea-49fd-a8c0-334d5e9bd5d9.png-w331s)

使用OD脚本脱壳后进行分析，样本执行后首先检测进程路径是否包含”WinUpdate”（样本本身包含的名字），若不是则退出：

![
](https://images.seebug.org/content/images/2018/11/e886c16e-f74f-497e-b1ef-3c38fe8d09ef.png-w331s)

进而检测启动项目录下是否有以”UpgradeVer”开头的文件

![
](https://images.seebug.org/content/images/2018/11/19667242-de1b-485e-b6ea-31250bfed0b2.png-w331s)

样本还会进行反调试检测：

![
](https://images.seebug.org/content/images/2018/11/75a6c7d8-3ee2-450e-93db-773116a5eb57.png-w331s)

随后，样本会执行%system32%下的sort.exe程序：

![
](https://images.seebug.org/content/images/2018/11/e87eb00f-cf36-493f-8124-93707b48e5c3.png-w331s)

之后利用WriteProcessMemory，RtlCreateUserThread向sort.exe注入一段ShellCode执行：

![
](https://images.seebug.org/content/images/2018/11/237c4076-29b1-4881-aa92-f3636a585d9f.png-w331s)

#### ShellCode

注入的ShellCode首先会通过IsDebuggerPresent检测是否处于调试状态：

![
](https://images.seebug.org/content/images/2018/11/097926c5-0753-4a9f-8c49-6d728d263b61.png-w331s)

并通过与“E2F9FC8F”异或解密出另一个PE文件：

![
](https://images.seebug.org/content/images/2018/11/94c99cbd-5a38-4c59-8382-15d1f1d352c3.png-w331s)

最后内存执行解密后的PE文件：

![ ](https://images.seebug.org/content/images/2018/11/edb48eeb-4a9d-4b0e-91cf-ce5f25f6a09f.png-w331s)

#### ROKRAT

最终解密后的PE文件是ROKRAT家族的远控木马，该木马会获取计算机名称、用户名、并通过smbios判断计算机类型：

![
](https://images.seebug.org/content/images/2018/11/c6861cda-875c-45b0-876d-21fcda48b82d.png-w331s)
![
](https://images.seebug.org/content/images/2018/11/d03d8768-f6d5-4971-a98d-535086b93258.png-w331s)

随后会进行沙箱执行环境检测：

![
](https://images.seebug.org/content/images/2018/11/be7fb003-0100-409d-9d5c-e0a2ab0b2244.png-w331s)

如果检测到存在”C:\ProgramFiles\VMware\VMware
Tools\vmtoolsd.exe”路径则会往MBR中写入”FAAAA…Sad…”字符串：

![
](https://images.seebug.org/content/images/2018/11/2aee3b46-e931-4c76-b767-ddb687823c2d.png-w331s)

写入之后通过shutdown命令重启电脑：

![
](https://images.seebug.org/content/images/2018/11/f8eb2fe7-4097-4750-a406-d08243298bdd.png-w331s)

重启后开机显示画面：

![
](https://images.seebug.org/content/images/2018/11/cb724661-3cd2-4054-ba4f-07db26693b88.png-w331s)

如果样本未检测到沙箱运行环境，则会执行后续的主要功能，包括获取屏幕截图：

![
](https://images.seebug.org/content/images/2018/11/660987b7-6d13-4ec7-bcd1-5e9e0e4800b5.png-w331s)

并通过网盘上传数据，网盘的APIKey会内置在样本数据里。下图为提取到的字符串的信息，样本会通过API调用4个国外主流的网盘包括：pcloud、box、dropbox、yandex

![
](https://images.seebug.org/content/images/2018/11/319ab490-82e5-463b-a658-86ac92313ae2.png-w331s)

API KEY通过解密获取，解密函数如下：

![
](https://images.seebug.org/content/images/2018/11/775a5e9b-1115-4ad8-855c-7dc8f39c9128.png-w331s)
![
](https://images.seebug.org/content/images/2018/11/4169a288-8208-4e45-b5e0-18ca61c26d9e.png-w331s)

尝试向网盘上传数据：

![
](https://images.seebug.org/content/images/2018/11/196c1774-e2e3-4f7c-9324-69c251be6048.png-w331s)

### 溯源与关联

360威胁情报中心通过内部威胁情报平台以及公开情报进行关联，发现此次攻击事件疑似为APT组织“Group 123”所为，关联依据如下：

Group 123团伙曾在多次活动使用ROKRAT：

![
](https://images.seebug.org/content/images/2018/11/c3afd7fb-2b38-46c0-a7dd-1ff1e04b165d.png-w331s)

且在2017年3月的攻击活动使用的样本也会判断当处于虚拟机环境下时，会向MBR写入字符串“Are you
Happy”，而在本次活动中，同样的向MBR写入了字符串“FAAAA…Sad…”：

![
](https://images.seebug.org/content/images/2018/11/4c466482-820a-4cd8-982f-b9b1ed5ab4b5.png-w331s)
![
](https://images.seebug.org/content/images/2018/11/f0243237-075b-4eae-a736-1d6f5f212b05.png-w331s)

并且本次捕获的样本代码片段和之前的基本一致，我们在这里选取Group 123曾使用的ROKRAT（MD5:
bedc4b9f39dcc0907f8645db1acce59e）进行对比，如下图可见，代码结构基本相同：

![
](https://images.seebug.org/content/images/2018/11/d7a141ac-657c-4b58-8061-40aa87b1976a.png-w331s)

### 总结

360威胁情报中心本次分析的HWP漏洞的根本原因是Hangul Office在使用GS引擎解析PostScript脚本时没有合理使用沙箱功能，即忽略了-dSAFER的沙箱选项。在这种情况下，攻击者只需要通过PostScript脚本将恶意软件写入到启动项或者其它系统劫持路径中，当用户重新启动操作系统或者触发劫持时就达到执行恶意代码的目的。虽然相关的漏洞在最新版本的Hancom
Office软件中不再存在，但依然有大量的老版本用户暴露在这个免杀效果非常好的漏洞之下，成为攻击执行针对性的入侵的有效工具，360威胁情报中心在此通过本文向公众提醒这类攻击的威胁以采取必要的防护措施。

### IOC

![
](https://images.seebug.org/content/images/2018/11/84af3478-229e-4d86-9d5e-b85c1b4f33dd.png-w331s)

### 参考

[1].<https://blog.talosintelligence.com/2018/01/korea-in-crosshairs.html>

[2].<https://ti.360.net/blog/articles/analysis-of-cve-2018-4878/>

[3].[https://zenhax.com/viewtopic.php?f=4&t=1051](https://zenhax.com/viewtopic.php?f=4&t=1051)

[4].<https://en.wikipedia.org/wiki/HancomOffice_(word_processor)>

[5].<https://en.wikipedia.org/wiki/Hancom>

[6].<https://hancom.com>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/738/>


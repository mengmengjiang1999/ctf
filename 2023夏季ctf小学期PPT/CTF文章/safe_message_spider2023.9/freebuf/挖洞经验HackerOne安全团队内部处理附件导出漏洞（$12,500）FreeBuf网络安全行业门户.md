***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![bc2122a6d14c534052d32038d8a007b7.jpg](https://image.3001.net/images/20181112/1542013441_5be94201b4f4f.jpg!small)**
**大家好，今天我要和大家分享的是一个和HackerOne平台相关的漏洞，该漏洞在于可以利用HackerOne平台的“Export
as.zip”功能（导出为.zip格式），把HackerOne安全团队后台的漏洞处理图片附件导出。最终的漏洞赏金为 $12,500美金。**

## 漏洞说明

首先要说明的是，这个漏洞是我在2016年底就发现的漏洞了，HackerOne也已作了公开，在此想写出来，一是为了分享，二是想告诉大家要发现漏洞其实也并不是那么难。

这是一个功能性Bug漏洞，属于信息泄露漏洞，但是，基于该漏洞的严重性和对业务的影响程度，HackerOne决定给予我最高的漏洞赏金，这也是HackerOne自开通自身漏洞测试项目起，给出的单个提交漏洞最高奖励。

> 漏洞严重性：高 (7.5)
>
> 漏洞定性: 信息泄露 (CWE-200)

## 漏洞端倪

HackerOne是一个知名的第三方漏洞众测平台，在HackerOne中，厂商的漏洞测试项目公开披露某个漏洞时，有两种披露模式可选，一种是完全披露（Full
disclosure），另一种是有限披露（ Limited
disclosure）。其中，完全披露也就是我们平常在H1看到的正常披露方式，这种披露状态下包括了漏洞信息、测试附件截图和整个的漏洞处理进程；而有限披露中，则会对漏洞摘要信息进行隐藏，就连安全团队与白帽之间的评论、沟通和操作处理进程等内容也有所限制。

2016年11月14日，HackerOne平台推出了一项名为[“EXPORT”的报告导致新功能](https://docs.hackerone.com/programs/export-reports.html#___gatsby)，可以在公开披露漏洞报告中的TIMELINE- EXPORT按钮处找到，如下：

![export.png](https://image.3001.net/images/20181112/1542012925_5be93ffd63ad7.png!small)白帽子们在查看一些HackerOne公开披露的漏洞报告时，可以利用该功能导出报告，导出方式有View
raw text（查看原始文本）和Export as .zip（导出为.zip格式）两种。

View raw text（查看原始文本）：从中可查看到整个漏洞报告的文本文字，方便复制粘贴。如下：

![01.png](https://image.3001.net/images/20181112/1542012816_5be93f90c4ef2.png!small)Export
as .zip（导出为.zip格式）：可以把整个漏洞报告的文本打包为.zip压缩格式下载。如下：

##
![02.png](https://image.3001.net/images/20181112/1542012836_5be93fa40f023.png!small)漏洞发现

在HackerOne推出了这项报告导出功能之后的第三天，我才注意到，说实话我的节奏是有点晚了，但不管那么多，我还是着手来进行一些测试吧。11月17日那天，我先做的测试就是，导出一些编辑过的限制型披露报告，看看能否在其中能看到一些编辑隐藏（redacted）的文本内容，但最后发现，这根本不可以。

11月29日，当我在HackerOne的hacktivity上查看披露漏洞时，我忽然看到名为@faisalahmed的白帽提交了一个与HackerOne报告导出功能相关的漏洞，在提交漏洞中，@faisalahmed描述了他可以通过View
raw text（查看原始文本）方式看到一些编辑隐藏的限制型内容（redacted
text），What，真的吗？！我怎么一直没发现呢！在看了@faisalahmed的漏洞报告后（<https://hackerone.com/reports/182358>），我才发现人家是在报告导出功能后的第二天就提交了这个漏洞了，我完全落后了！

好吧，算我没那个运气吧，那就来认真阅读一下人家的漏洞报告吧。于是，我就点击了“EXPORT”按钮把整个漏洞报告导出为.zip格式进行了下载。

当我解压了.zip格式的压缩包后，看到其中包含了一个text文档和一张图片，text文档说明了整个漏洞的处理进程和结果，但，等等....，这里的这张图片是什么东东？我迫不及待地打开一看，这是一张漏洞验证（PoC）的截图，但是在HackerOne公开披露的报告中没有这张图片啊！而且，我在报告中还看到@faisalahmed希望HackerOne在报告公开后，移除一张图片附件的评论请求，如下：

![remove.png](https://image.3001.net/images/20181112/1542013072_5be94090283f3.png!small)如果我没猜错的话，这张图片就是@faisalahmed希望HackerOne移除的那张图片附件，由此，我立马写了一个以下的简单漏洞重现步骤，向HackerOne提交了这个漏洞。

漏洞重现步骤：

> 1、访问@faisalahmed提交的漏洞报告 <https://hackerone.com/reports/182358>
>
> 2、点击“EXPORT”按钮，用 Export as .zip 功能把漏洞报告导出为.zip压缩格式
>
> 3、解压.zip格式报告压缩包(HackerOne_Report-security#182358.zip)
>
> 4、可以查看到公开披露报告中已经移除的图片附件

上报漏洞仅12分钟之后，HackerOne安全团队就确认并分类了该漏洞：

![traiged.png](https://image.3001.net/images/20181112/1542013231_5be9412f2c89a.png!small)20分钟之后，HackerOne安全团队就执行了修复，并向生产环境系统中部署了解决方案：

![release
fix.png](https://image.3001.net/images/20181112/1542013248_5be94140d21f0.png!small)两天之后，HackerOne官方向我奖励了自其漏洞测试项目开展以来的最高奖励
$12,500 美金：

##
![highest.png](https://image.3001.net/images/20181112/1542013263_5be9414fcb353.png!small)漏洞修复

现在，当我们以.zip格式下载任何一个HackerOne公开披露的漏洞报告后，也已经无法在其中查看到任何作了删除和编辑隐藏的截图附件，只包含了一个txt的漏洞文本。

## 漏洞上报进程

> 2016.11.29 03:04:52 向HackerOne安全团队上报漏洞
>
> 2016.11.29 03:16:36 HackerOne安全团队确认并分类漏洞
>
> 2016.11.29 04:36:34 修复漏洞
>
> 2016.11.29 04:59:23 确认修复
>
> 2016.11.30 09:15:51 HackerOne向我发放最高赏金$12,500和漏洞奖品

更多技术信息请参考原漏洞报告 - <https://hackerone.com/reports/186230>

***参考来源：[medium](https://medium.com/japzdivino/security-teams-internal-attachments-can-be-exported-via-export-as-zip-feature-on-hackerone-35ca6ec2bf8b)，clouds编译，转载请注明来自FreeBuf.COM**  


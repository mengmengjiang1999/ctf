## **一.事件背景**

动荡局势之下，网络暗战从未缺席。在9月初， **安恒信息威胁情报中心猎影实验室** 捕获到了一个来自 **白俄罗斯的rtf样本**
，其被命名为：“СВЕДЕНИЯ О ПОДСУДИМОМ.rtf”（大致意思为“被告人的相关信息”）。

伪装文件内容为刑事案件登记卡，内容中可以看出与最高法院司法部门的相关信息，文档里面的语言属于俄语，这份模板可以在俄罗斯的一个教育的网站上下载到。

![10ba68c15901c30ba3f9a7717a12ec7f-sz_1226592.png](https://image.3001.net/images/20200925/1601013551.png!small)

显然攻击者利用了“白俄罗斯总统大选结束后，爆发大规模活动，大量人员被捕事件”发起的网络攻击。

攻击者使用了之前从未公开漏洞利用代码的JS引擎解析漏洞CVE-2020-0968进行的攻击，该漏洞曾被微软认定为未被利用。未知1day的利用，说明这次的攻击者具备非常高的技术实力或经济实力（花钱购买漏洞），其利用的木马使用一个命名为
“Domino”函数的特殊性，所以我们将此次活动命名为多米诺行动（Operation Domino）。

##  **二.攻击概述**

该文档利用未公开利用代码的CVE-2020-0968漏洞，实现加载远程恶意木马，其攻击手法专业，下载的木马具备合法数字签名，其除了传统的木马功能，还会修复存在漏洞利用的文档，一看就是专业团队。

![78f6298e4708fa062d94192d1740e7cc-sz_272656.png](https://image.3001.net/images/20200925/1601013555.png!small)

##  **三.武器详细分析**

样本以内嵌URL Moniker 的rtf文档为载体，远程加载了位于http://94.156.174[.]7/up/a1a.htm 的网页文件，

![f41cef6f9fcd1f0e7619661ee8b47a72-sz_13658.png](https://image.3001.net/images/20200925/1601013556.png!small)

远程加载的网页文件内嵌一个之首次被观察到在野利用的jscript漏洞，

![b4f7cae0b859d89126582071e926ba65-sz_65409.png](https://image.3001.net/images/20200925/1601013557.png!small)

猎影实验室对该漏洞进行了分析，发现这是一个IE浏览器jscript.dll模块中的UAF漏洞。jscript在处理两个对象(type=0x81)的相加操作时，CScriptRuntime::Run会连续两次调用VAR::GetValue获取对应的值，开发者没有将期间保存到栈上的variant变量加入GC追踪列表。如果对象实现了自定义toString方法，VAR::GetValue内部会进一步调用NameTbl::InvokeInternal函数，这个函数可以调用自定义的toString，在第二个VAR::GetValue导致的回调中，可以手动释放相关variant变量，回调函数返回时，CScriptRuntime::Run会再次使用被释放的variant变量，造成UAF。

![c465b6b30a44b22dd448a1dc73e3b1a2-sz_82265.png](https://image.3001.net/images/20200925/1601013557.png!small)

通过补丁分析，可以确认该漏洞出现在双星漏洞(CVE-2020-0674)之后，且在2020年4月的补丁中被修复。

值得注意的是，2020年4月微软确实修复了一个等级为“Critical”的IE漏洞，并在初始发布时将其标注为“Exploited:
Yes”，但随后微软将其修改为“Exploited: No”，这件事当时还引起了安全研究人员的讨论：

![f129318bc963fad11bcc38967964799f-sz_128031.png](https://image.3001.net/images/20200925/1601013558.png!small)

结合修复时间和上述信息，我们合理推断本次攻击使用的漏洞为CVE-2020-0968
Jscript远程代码执行漏洞。此次攻击中的漏洞利用采用和之前出现过的Jscript
UAF漏洞相同的利用方式，先借助漏洞泄露一个RegExp对象的地址，紧接着利用RegExp对象伪造一个超长BSTR，借助此BSTR数组实现越界读，在此基础上伪造一个假的RegExpObj对象，最终借助正则引擎实现任意地址读写，实现ShellCode执行。

ShellCode执行成功后，会从远程地址http://94.156.174[.]7/up/a1a.dll下载附加模块，并解密执行，解密方法为简单的异或，key为“weHnh”。解密得到dll文件中含有一个名为“Domino”的导出函数，经判断为主要功能函数。

![cfbf18bda6cc9b9c0a0c4223ab0bf7fc-sz_90529.png](https://image.3001.net/images/20200925/1601013559.png!small)

Dll样本会找到自身rtf/doc文档，并找到“{\object\\\objemb ……}”所在内容并进行删除，而这部分内容正是内嵌的URL
Moniker数据。

![](https://image.3001.net/images/20200925/1601023229_5f6dacfd53b1b25463042.png!small)

删除URL Moniker后，dll会再次打开文档。此时原始文档已被修改为干净的文档。

![314f3c574931e478cec82690cd6e294d-sz_175444.png](https://image.3001.net/images/20200925/1601013560.png!small)

随后，Dll会执行一个内嵌的EXE程序，

![6e9b5c1f58a6f96e340416821a532c03-sz_34861.png](https://image.3001.net/images/20200925/1601013560.png!small)

该EXE后门使用了打印机图标进行伪装，伪装为Microsoft Windows Fax and Scan程序，其包含有效的数字证书，签名人信息为“Sizg
Solutions GmbH”。该EXE程序被VMP加壳，输入表被加密：

![598b0d9506c935ad6a0c954469c27fc6-sz_83577.png](https://image.3001.net/images/20200925/1601013561.png!small)

该后门启动后会创建了一个窗口标题为“8Wsa1xVPfvJcrgRY”，类名为“frAQBc”的窗口。

![b5b2fb2df9a5ec433689a2a0876b9173-sz_117180.png](https://image.3001.net/images/20200925/1601013561.png!small)

接着进入消息循环机制，大部分恶意功能都是在窗口处理函数WindowProc里面实现，当窗口收到窗口创建消息WM_CREATE时，后门发送自定义消息触发其他关键恶意流程：

![2cd33638bd1629eab07c1f92fad10103-sz_216133.png](https://image.3001.net/images/20200925/1601013562.png!small)

大部分的消息码对应的函数功能统计如下表：

![5ead422965b94e0b740a8a2b599e8c1b-sz_16878.png](https://image.3001.net/images/20200925/1601013563.png!small)

动态获取API地址后，通过wmi命令获取各类操作系统、硬件、用户信息等信息

![b04e10c818ff345d3695880e34573056-sz_120983.png](https://image.3001.net/images/20200925/1601013563.png!small)

大量不同密钥通过异或算法解密出HTTP通讯需要HTTP头信息，用于构造Post请求的数据包

![8f041ee59bcd373752329de64449f0d6-sz_751308.png](https://image.3001.net/images/20200925/1601013564.png!small)

通讯数据被AES加密，后门内置3组密钥，在不同功能模块使用不同密钥处理数据

![c1f34bb48c024717f2a6f45659072c4f-sz_578448.png](https://image.3001.net/images/20200925/1601013567.png!small)

由于后门被VMP保护以及内部混淆较严重，对分析造成了很大干扰，目前的分析发现的主要功能包括：

●加密上传收集的用户信息

![6b9c554c33faedb13d03d5e3783fa8eb-sz_831518.png](https://image.3001.net/images/20200925/1601013569.png!small)

●截图获取用户桌面以及更新自身

![7b5e1d66e6cda81be7dbf34708ec8b8c-sz_690494.png](https://image.3001.net/images/20200925/1601013572.png!small)

##  **四.关联猜想**

本次攻击中用到了一个之前未出现在公众视野的JScript漏洞，从漏洞利用手法来看，之前只有DarkHotel拥有此类原创的JScript新漏洞利用。不过，在对后续载荷进行分析的过程中，我们并未发现有DarkHotel的明显特征。考虑到此次漏洞使用时是一个1Day，不排除其他组织从相关渠道获取了这个漏洞利用并进行攻击。

##  **五.总结**

网络暗战在政治军事博弈中起到了关键性作用，在政治军事情报体系运营过程中，从收集信息到网络空间基础设施打击都能够起到意想不到的作用。

正如此次活动中使用的dll的功能函数“Domino”（多米诺），推动第一步后，多米诺所带来的连锁反应导致一系列的引导式的变化。这里再畅想一点，上个世纪50年代，由美国总统艾森豪威尔首先提出的多米诺理论，是对当时针对东南亚形式的非常重要的一条理论，东南亚地区一个国家的政治倾向只要出现第一例，那么这个地区的其他国家就会像多米诺骨牌一样，一个接一个的倾向于一个方向。其用在当前局势下，也十分应景。

此次为 **首次发现在野利用的疑似CVE-2020-0968漏洞** ，说明攻击组织有一定的实力。针对“Domino”函数的特殊性，我们将此次活动命名为
**多米诺行动（Operation Domino）** 。

##  **六.IOC**

60981545a5007e5c28c8275d5f51d8f0

7fce761a343ceb15126e7d8f6314c4ed

67b5d793cf4b0a1ddecf756c42af47c8

ba1fa3cc9c79b550c2e09e8a6830e318

f927659fc6f97b3f6be2648aed4064e1

94.156.174[.]7

185.243.112[.]57

PS：

微软已经不对windows 7系统提供服务支持了，所以默认不会推送补丁，如果是windows7用户需要手动去微软网站下载补丁进行安装。


# 风雨欲来：恶意软件 Brushaloader 深入分析

阅读量 **282420**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-02-27 15:30:33

 **x**

##### 译文声明

本文是翻译文章，文章原作者 talosintelligence，文章来源：blog.talosintelligence.com

原文地址：<https://blog.talosintelligence.com/2019/02/combing-through-brushaloader.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t018edd94fc81f3de9c.png)

## 摘要

在过去的几个月中，Cisco 的 Talos 团队监测到了多种利用 Brushaloader 向系统下载恶意代码的行为。Brushaloader
目前最主要的特征是利用了多种语言脚本，例如：使用 PowerShell 来隐藏在受害者机器上的行为，使用 VBScript 和 PowerShell
来创建一个远程访问的木马(RAT, Remote Access Trojan)，能够长期在受感染的机器上执行命令。

根据我们的监测，Brushaloader 正在不断地进化，随着攻击者不断修改自身特征并添加其他功能，Brushaloader
正在以很快的速度开发和完善。自从 2018 年中开始，我们已经监测到 Brushaloader 进化了多个版本。我们观察到的大多数与
Brushaloader 相关的恶意软件传播活动都利用特定地理区域的电子邮件来分发各种恶意软件负载，最主要地例子是 Danabot。在此之前，已经有人研究过
Danabot 了([A](https://www.welivesecurity.com/2018/09/21/danabot-targeting-europe-adds-new-features/),[B](https://www.welivesecurity.com/2018/09/21/danabot-targeting-europe-adds-new-features/))，所以这篇文章将会着重分析 Brushaloader 本身。最近， Talos 观测到与
Brushaloader 相关的恶意活动有明显的上升趋势，而且， Brushaloader 不断进化的隐藏技术也会是我们的观测值远远低于实际值。

[ThreatGrid](https://www.cisco.com/c/en/us/products/security/threat-grid/index.html) 中提供的高级命令行审计和报告功能可以有效地分析 Brushaloader 等威胁。诸如 Brushaloader
之类的威胁也说明了在大多数企业环境终端上启用和配置 PowerShell 日志记录功能的重要性。

## Brushaloader 的发展历史

###  初次交锋: 首次观测到 Brushaloader 的记录

我们第一次监测到 Brushaloader 的活动是在 2018 年 8
月。最初之所以会吸引我们关注，是因为它只使用针对波兰用户的波兰语邮件。通常来说，恶意软件都会以多种语言针对多类用户，像 Brushaloader
这样，只针对单个欧洲国家的恶意软件并不多见。下面是我们第一次发现 Brushaloader 时的一封电子邮件示例，在图片中，展示了我们最初用来识别
Brushaloader 的特征：RAR 附件文件中包含一个 Visual Basic Script 文件，该脚本导致受害者感染
Brushaloader，并下载和执行 Danabot。

![](https://3.bp.blogspot.com/-khLHtq2RNFc/XG1wHq6YXAI/AAAAAAAAA50/3bH8TJOGtNU1jC5mt9tUVK1wpOlZ8prUgCLcBGAs/s640/image17.png)

关于 Brushaloader 还有一个特点是，在它的传播邮件中会有一个单词 Faktura, 是波兰语中 “发票”
的意思。虽然在接下来的几个月中，这个单词会变化，但是几乎每封邮件都会与“发票”，“账单”相关。对于传播邮件的附件，它通常是一个以 “Faktura” 命名的
RAR 文件。这个 RAR 文件都会包含一段 VBScript 脚本，用来下载有效载荷。这段 VBScript
脚本本身具有一定的对抗沙箱以及网络模拟的技术，但是并没有做太多的混淆，而是直接地与一个硬编码地 IP 地址建立了 C2 (Command and
Control) 通信。其中，这个硬编码地地址如下：

    
    
        http://162.251.166.72/about.php?faxid=446708802&opt=.
    

一段时间后，Brushaloader 似乎陷入了一个循环： 在持续活跃一到两周后，Brushaloader
会慢慢地进入休眠，休眠几周之后会再重新开始活跃。不过有一点值得注意的是，在 Brushaloader 的不断更新与进化后，它越来越注重隐蔽自己建立 C2
通信的过程。

###  另辟蹊径：规避网络模拟，多重条件的 C2 通信

当第二次监测到 Brushaloader 活动时，Brushaloader
又增加了一部分新的功能。在程序运行的初始阶段，程序会先与一个不存在的网址进行通信，来判断是否处于一个网络仿真环境中。如果这个 GET 请求返回的是一个
HTTP /200，即访问成功，则 Brushaloader 会持续不断地访问下去。下面就是这个新功能地截图：

![](https://3.bp.blogspot.com/-wwABN-ViwpE/XG1wRpg26YI/AAAAAAAAA58/2ND51mu8wzQ9UzzO1kdONwwPURtngiefgCLcBGAs/s640/image13.jpg)

第一段代码片段用来对一个本来不存在的地址(www.dencedence.denceasdq)发送的 GET 请求。第二段代码判断返回的结果是否为
HTTP/200。第三段代码中，如果是返回的是
HTTP/200，则会陷入一个无限的递归中。这是一个简单方法，用来判断自己是否处于网络模拟环境中。这些简单的技术可以在躲避某些种类的监测和分析时发挥意想不到的用途。

几天后发起的一次活动又做了一些改变。早期版本的脚本只通过硬编码的IP地址通信，这次的脚本会从一个域名和硬编码IP中进行随机选择，然后开始通信，下面就是这个版本的部分代码：

![](https://4.bp.blogspot.com/-PxwnzuH0QyU/XG1wXCDobyI/AAAAAAAAA6A/L3pDk1YWpYESzZ3NKMx6iRGuWnLLea6xgCLcBGAs/s640/image27.jpg)

这段代码中实现了 C2 请求的初始化。这个请求中包含了一些新的变量和功能。从这个图中可以看出， (1) Brushaloader
随机的选择一个地址进行通信，候选的地址已经在 DaLoweRsxMinsa 函数中列出。 (2) 然虽硬编码的 IP
地址(192.3.204.226)与域名(emailerservo.science)托管在不同的服务器上，但是却可以响应相同的路径。

在接下来的几个月里，这个特征将一直保持不变，但是随着时间的推移，它们又会出现一些微妙的变化。

###  虚虚实实：使用普通的 URL 来混淆

上面的两波活动主要出现在整个九月以及十月的前几天，之后，Brushaloader 又出现了变种。 Brushaloader 在混淆 C2
通信的方法上出现了一些细微的变化。在十月初的变种中，Brushaloader 又增加了一个合法的域名用来选择：

![](https://2.bp.blogspot.com/-6QA66jk7O5c/XG1wxk772tI/AAAAAAAAA6U/EKvH5-X8Ye8B2rzpwVqjwMA6dTj0RiceQCLcBGAs/s1600/image31.png)

在这里，Brushaloader 又增加了一个 google.com 域名作为其建立 C2 通信的候选域名。在接下来的几个月中，Brushaloader
又逐渐增加了 www.ti.com 和 www.bbc.com
两个域名。这是躲避沙箱监测的另一种简单方法，在这种方法中，VBScript只会周期性地向这些域名发送请求。

###  删繁就简：精简的版本出现

在 2018 年十月之后，Brushaloader 出现了特别明显的变化。 包括删除了所有地虚假域名，并且，在 WScript
中加入了注册表操作，能够从注册表中读写数据。 它可能只是用来做某些权限检查，但是所有权限级别的所有用户都能够查询键值
HKEY_CURRENT_USER，这又十分的矛盾。我们无法得知其真正地目的。下面是实现此检查时的屏幕截图。

![](https://2.bp.blogspot.com/-_A2yb27-zvU/XG1x-qnBiRI/AAAAAAAAA6g/EeDyBHK-alwlvma9jQ2j4Z635ctHTdnHACLcBGAs/s640/image19.png)

这个检查的功能持续时间相对较短，也就是在十月份的最后几天出现过，在这之后，Brushaloader 就完全从 WScript 迁移到了 Internet
Explorer中。 除此之外，VBScript经过了大量的简化，从一个4KB的文本变成了小于1KB的文本。下面是整个VBScript的屏幕截图。
大多数检查和隐蔽技术都被移除了，只保留了一些睡眠的命令来躲避沙箱检测。

![](https://1.bp.blogspot.com/-CBYTFiEUzoA/XG1yDtpRHxI/AAAAAAAAA6k/6vwbru3ZoEgyf5Ge4TEvKwM0zVHSFV9YgCLcBGAs/s1600/image16.jpg)

需要注意的是，标亮的代码创建了一个无头 IE 浏览器实例， Brushaloader 与 C2 服务器就是通过这个无头浏览器进行通信的。
此外，Brushaloader 完全放弃了使用域名，退而只是使用硬编码 IP 来托管所有的内容。

###  狼烟再起：新语种的出现

也是在这个时候，Cisco 的 Talos 团队监测到恶意传播邮件出现了波兰语之外的语种。与此同时，与 Brushaloader
相关的多个语种的活动也活跃起来，下面是德语语种的一个例子：

![](https://3.bp.blogspot.com/-SaZ8xL3KUfc/XG1yJcnbrPI/AAAAAAAAA6o/_Yq0uX4NYxEYwNm8lrPrWlywMZ_OMdYwACLcBGAs/s640/image6.png)

这波活动的邮件主题主要都是“所得税申报表”，在邮件的正文中提到了未付账单的附件，并威胁收件人，如果付款未汇出，将采取法律行动。比较有意思的是，”Faktura”在德语中翻译为账单，在波兰语中翻译为发票。

又过几个星期，大约在11月中旬，Brushaloader 又开始重新加入了一些虚假域名的检测，如下所示：

![](https://2.bp.blogspot.com/-F1hP8jHZkdM/XG1yNezOZsI/AAAAAAAAA6s/cZ40PO6L5-82ziII220uRpIIlh8hGruawCLcBGAs/s640/image25.png)

在这个特定的版本中， Brushaloader 将发送一个HTTP请求来获取 <http://someserver/folder/file.pdf>,
同样的，如果返回 HTTP/200 则会陷入死循环。几天后，Brushaloader 再次变化，在 C2 通信时不再使用硬编码IP，转而使用域名。

###  不破不立：11月底的重构

在 11 月底的活动中，VBScript 脚本被全面的重构了一遍，并在实现上做了一些改进。第一个更改是 VBScript 首先创建一个文件系统对象，它允许
Brushaloader 读写磁盘文件。

![](https://1.bp.blogspot.com/-RqEIdZ-BfOg/XG1ycFJ9F4I/AAAAAAAAA68/Di4yE3js5M4dIAZgaG-Aezt6xUXrxmUEwCLcBGAs/s640/image3.png)

接下来，脚本会下面的函数中调用这个文件系统对象。

![](https://3.bp.blogspot.com/-aaXGzjXrtAI/XG1ykJlP3iI/AAAAAAAAA7A/MXVN3n9wjx4FG11H3CSgvXTj6XzKcaGegCLcBGAs/s400/image20.png)

下图是 WriteFile 以及 readFile 函数，用来读写系统中的文件。需要注意的是，在函数的调用之间，会有几秒的 Sleep。

![](https://2.bp.blogspot.com/-QWm8GoekP-c/XG1ypPcceYI/AAAAAAAAA7E/FqbwPlpnoTAxTTgUTm2aPwdx8GLfMCYKACLcBGAs/s1600/image4.png)

WriteFile函数会专门在临时文件夹中创建一个文件，然后将ASCII文本”test”以及vbCrLf的引用写入文件中，这是VBScripting早期的残余，如果成功创建，则会返回“rn”。readFile函数会读取包含”test”的行，并将其存储在变量strLine中。在又
Sleep 了一下后，会调用函数 HttpsSend 函数，下面是HttpsSend函数。

![](https://1.bp.blogspot.com/-Pfv1fzSHrnQ/XG1ytTAP6lI/AAAAAAAAA7I/UH7JpMoDKJgtxPtNz8HgdklyBzxyWzvDACLcBGAs/s1600/image12.png)

这里有一些关键的变化要注意。首先是 Brushaloader 已经开始使用域名而不是硬编码的 IP 了，而且通信的流量也已经变成了 HTTPS。  
此外,请求的方法已经从一个GET到POST。

请求发出后，收到的响应被存到一个数组中，之后，在 Sleep 了 10 秒钟后，调用了 Emulator 函数:

Emulator 函数检查以确保在脚本之前创建的文件中具有”test”字符串。  
如果文件有”test”,那么脚本将执行由C2服务器发送的命令,并将命令存储到数组 ArrAddMyArray 中。

上面的所有行为都是在一个while循环中完成的，它不断地相应C2服务器的各种指令，类似一个简单地框架。

![](https://1.bp.blogspot.com/-HlF1J4Y1b0w/XG1y-i3qa_I/AAAAAAAAA7Y/pF1fXo0Pr94lCsAtHMJ5ne83hABB8UbmgCLcBGAs/s400/image21.jpg)

这次的活动规模并不大，到11月底就停止了。在整个12月和1月的大部分时间里， Brushaloader 不太活跃。然而，在1月底和2月初，情况又发生了变化。

###  风起云涌：最近期的活动

今年 1 月底， Brushaloader 的活动又一次活跃了起来，与之前相同， Brushaloader 仍然使用电子邮件传播具有恶意 VBScript
脚本的 RAR 文件。  
这次的活动主要从基于波兰语的电子邮件开始，下图就是这个邮件的例子：

![](https://4.bp.blogspot.com/-0iEsD71_VpA/XG1zDU1hYmI/AAAAAAAAA7c/quJ9TJ7l3oEhDncg_OsJ0M1BvAsHMeRbgCLcBGAs/s1600/image30.png)

这与我们在之前看到的 Brushaloader 邮件十分类似，以波兰语的 “Faktura” 为主题，并附带一个包含恶意 VBScript 脚本的 RAR
文件。  
然而，最值得注意的是，这次的活动是我们首次监测到意大利语的邮件：

![](https://3.bp.blogspot.com/-J_v44Je3xGI/XG1zHhYAKDI/AAAAAAAAA7g/5rMmu8bi524ef6K5j3MWX8DLXvricOcEACLcBGAs/s640/image33.png)

在这个意大利语的邮件中，与之前的 Brushaloader 传播邮件非常相似。他们的主题是 “Fattura”，
也是意大利语中发票的意思，同样，附件还是一个带有 VBScript 脚本的 RAR 文件。

在搜集系统信息、执行指令、以及提供附加载荷时，脚本使用的语言用到了 PowerShell。 此外，这次活动的规模是前所未见的，很有可能代表
Brushaloader 已经发展成熟，准备在世界范围内扩散，而不再仅仅局限于欧洲地区。 新功能的完整细节将在本博客的后面部分进行介绍，包括对利用
HTTPS 进行 C2 通信的深入研究。

这次的活动一直持续到 2 月份的第一周，自那以后又处于不活跃的状态。 在过去的半年里，Brushaloader 已经从一种新的基于 vbscript
的加载程序，发展成为一种日益完善的分布式威胁。 下面的时间表说明了 Brushaloader 的开发迭代非常的快。 按照往常的经验，Brushaloader
将是一个非常严重的威胁。

![](https://2.bp.blogspot.com/-PwMRFjWPirE/XG1zLswbfeI/AAAAAAAAA7k/yeP6f9qhed8YDwjD9rCzA9aXfSgTvpPjgCLcBGAs/s640/image26.png)

## Brushaloader 中用到的抗分析技术

在许多公司的内部网络中，任何从外界引入的文件都先提交到类似 sandboxes
地自动化分析平台中进行分析。分析平台会自动的执行该文件并观察系统活动，以确定该文件是恶意的还是良性的。如果是良性的，才允许将该文件传输到内部网路中。
Brushaloader
发起者们一开始就意识到了这种情况，并且不断地提出一些新的方法来绕过它。通常情况下，这些机制都是为了隐藏恶意文件的行为，以绕过自动化分析平台的检测。

此外，Brushaloader 还使用了多个 Sleep 定时器，它能使恶意程序休眠一段时间。

在一般情况下，恶用户意软件都会利用邮件的附件来引诱用户输入一些信息。然而，由于许多自动检测和分析平台并不能模拟用户提交信息，因此无法使恶意软件的感染程序启动。Brushaloader
同样利用这种技术，以增加其感染的成功率。

###  用户交互

在过去几个月的 Brushaloader
活动中，我们观察到的一个变化是，恶意软件的下载程序在受感染系统上执行恶意行为之前，需要与用户进行交互。攻击者通常会利用用户交互来绕过自动化分析平台。

对于 Brushaloader, 它的邮件中包含了 RAR 文件，RAR 文件中又包含了 VBScript 脚本。这个 VBScript
脚本会向攻击者控制的服务器发送一个 HTTP 请来下载 PE 文件。 当然，在下载 PE 文件之前，VBScript
会弹出一个对话框，上面显示了Fibonacci序列的各种字符，并且有一个 OK 按钮:

![](https://4.bp.blogspot.com/-HsoJtQfCJ0U/XG1zRT9ao6I/AAAAAAAAA7s/wKNCDzdazMkovCthysSanH74HMgKsyCGwCLcBGAs/s640/image28.jpg)

当 VBS 脚本执行后，就会跟着弹出下面的对话框：

![](https://1.bp.blogspot.com/-LScMXApxrtU/XG1zVbEX33I/AAAAAAAAA7w/wWwWcHqwchQb9Qj4PlWTWKungwIvPAlaACLcBGAs/s640/image14.png)

用户一旦点击 OK
按钮，就会触发脚本下载恶意程序。这种需要用户交互的机制能够绕过许多自动化分析平台，因为大部分的分析平台都没有考虑过用户交互的情况。因此这种方法会导致检测率很低。

![](https://3.bp.blogspot.com/-Igo9LyuOxjM/XG1zZacYEGI/AAAAAAAAA74/bdQEmGIHHzsQVjWtCsGNkGKFAKnRyhkvwCLcBGAs/s640/image1.jpg)

###  虚假域名

许多次活动中， Brushaloader
的脚本利用原本不存在的域名来检测其是否正在一个仿真网络环境中。在许多恶意软件分析的环境中，网络仿真是允许恶意软件与外界进行交互的。如果样本所请求的资源不存在，则仍然会返回请求成功。当
C2 服务器下线时，或者在缺少网络链接的环境中，这个方法尤其有用。有许多工具都会提供这个功能，其中有两个工具特别常用:
[inetsim](https://www.inetsim.org/) 和 [FakeNet-NG](https://github.com/fireeye/flare-fakenet-ng)。

对于 Brushaloader 来说，
他们会请求一些根本不存在的顶级域名(比如www.weryoseruisasds.oedsdenlinsedrwersa)，或者是直接使用主机名，而不是域名(比如
someserver)。  
很显然，这两种情况都不可能连通，这只是简单的检测一下这是不是在一个仿真网络环境中。

## 装载器功能

一旦初始感染过程开始，前面描述的多阶段 VBS 脚本就开始执行了。受感染的系统向 C2 服务器发出 HTTPPOST 请求。然后会对HTTP
POST请求的响应进行处理。

第一阶段的 VBS 脚本负责执行下面一段编码的 PowerShell 脚本:

![](https://3.bp.blogspot.com/-bQbDbXpIYDI/XG10N7jPIgI/AAAAAAAAA8Q/HVR2moyjKw4neUxMrvUzGZLkTqFh3igBACLcBGAs/s640/image11.jpg)

这段编码后的 PowerShell 脚本会被执行三次，最终被解码成:

![](https://3.bp.blogspot.com/-UAjNhYPGAA0/XG10SrGEzTI/AAAAAAAAA8U/i8iY-BmOalc-0EufITqWrn67fe3vgICTwCLcBGAs/s640/image5.jpg)

这会向 C2 服务器发送一个 HTTP 请求，并且会执行另一组命令：

![](https://3.bp.blogspot.com/-5dl5mCWdvzA/XG10WwmEmMI/AAAAAAAAA8Y/pSPYcp3WueMXkNany7jMm2Rx269d6iD0wCLcBGAs/s640/image2.jpg)

这段脚本解码后为:

![](https://2.bp.blogspot.com/-ID7NaPwYwyc/XG10bloXXvI/AAAAAAAAA8c/Fz2OVbv1xx859jE9kpFbqxbgpIZiP0egACLcBGAs/s640/image10.jpg)

这段代码主要负责与受感染的系统建立一个远程会话，然后使用该会话在受感染的系统上执行命令，并获取命令执行的结果。 就这样，这个脚本循环执行，等待并运行 C2
服务器的指令。 此外，这个会话还可以用于执行各种 Powershell 命令， Brushaloader 一般会使用 PowerShell
命令收集系统信息。

![](https://4.bp.blogspot.com/-sUE2npnZwR4/XG10pyt-pRI/AAAAAAAAA8s/yqi3sVx1Ud8ezMKfgZniM16Lc4hWzs-WwCLcBGAs/s640/image8.jpg)

例如，上面的 PowerShell 将会被传给 IEX 并执行，执行的结果将会传回给 C2 服务器。

![](https://4.bp.blogspot.com/-04K7PZ_U6NE/XG10uXUCa8I/AAAAAAAAA80/JVBgj6UuqsYdPQHI3vax-opVL6haE7S3wCLcBGAs/s640/image24.jpg)

由上图可知，攻击者会尝试枚举以下的系统信息。

    
    
    ProcessorId
    Windows operating system version
    Currently logged in Username
    Installed Antivirus Products
    System Make/Manufacturer
    Powershell version
    IP address information
    Available memory
    Current Working Directory
    System Installation Date/Time
    Display Adapter Information
    

然后，所有这些信息都可以用于判断是否需要使用额外的恶意载荷感染系统，或者应该向系统下载哪些模块。

此外，在受感染系统上运行的Powershell进程还会创建 Windows 快捷方式(LNK)来实现持久化，该快捷方式被添加到系统上的启动目录:

![](https://1.bp.blogspot.com/-dh0AJwlV7rA/XG10zvuqzoI/AAAAAAAAA84/K34bwgNjlgcC4AH7dWlUY4gArZPt3N6BwCLcBGAs/s640/image23.png)

快捷方式文件中包含 Powershell 脚本，用来读写注册表项的内容，以便在每次重新启动系统时自动执行一些指令。

![](https://3.bp.blogspot.com/-J2-dro4Wjog/XG105Y_25uI/AAAAAAAAA88/qxCweR7RYdcVU6T4myImYZiCOJOw1AGwwCLcBGAs/s640/image29.jpg)

被写入注册表的脚本命令如下：

![](https://4.bp.blogspot.com/-w4auhrajZQs/XG10-CvWQOI/AAAAAAAAA9I/hjLhIx3KqRsFKYIDBrazX9TXEO_mRjObgCLcBGAs/s640/image15.jpg)

这个脚本解码后为，用来通过HTTPS协议向 C2 服务器进行通信。

![](https://3.bp.blogspot.com/-93yQCSY7Z8g/XG11B-OPqtI/AAAAAAAAA9M/RQ_Po1Amd-Ul7DhPpv_bwegCJo-VcMyrQCLcBGAs/s640/image32.jpg)

## 活跃时间分布

Cisco Talos 团队从 2018 年中就监测到了与 Brushaloader 有关的而已活动。与 Emotet
等其他商业恶意软件分发活动相比，这些活动的数量相对较低。在我们分析的大多数情况下，主要的传播都发生在每个月底。然而，我们最近发现它活动的数量和持续时间显著增加。

下图显示了当前的活跃的数量与 2018 年大部分时间观察到的活跃数量的对比。

![](https://2.bp.blogspot.com/-ygaKRaKz3n8/XG11GX0-sII/AAAAAAAAA9U/YWWu9pev5WUhruS5DP8yuSM-nO_mWY-zQCLcBGAs/s640/image18.png)

除了传播活动的数量发生了变化之外，我们还观察到攻击的目标收件人群发生了变化。起初，这些活动将目标定位在波兰人中，后来，我们观察到新的活动扩展到德国、意大利和其他国家的用户。

## 总结

就像 Brushaloader 一样，恶意软件传播的机制一直在变化。这篇博客概述了它是如何不断变化和发展的。事实上， Brushaloader
所使用的技术并不是特别的新颖，但是其开发人员的开发迭代速度使我们不得不重视。此外，值得注意的是，经过去年12月和今年1月长时间的沉寂后，Brushaloader
已经发展的非常完善，随时都可能会爆发。开始 Brushaloader
只是专门针对波兰，后来逐渐扩散到其他的几个国家。然而，这种限定区域的传播策略并不太常见。

Brushaloader 是一个典型的例子，这个简单的基于 VBS
的恶意软件以很少的代码实现了多种巧妙的规避和混淆技术，同时，攻击者不断在改进，并开发新的方式来向用户传播恶意软件。我们将继续监控这一威胁，并将继续保持警惕，保护我们的客户免受损失。

## IoC

###  传播邮件的附件

  * RAR 文件

234个出现过的 RAR [文件哈希](https://alln-extcloud-storage.cisco.com/ciscoblogs/5c6d7a32eda38.txt)

  * VBS 文件

150个出现过的 VBS [文件哈希](https://alln-extcloud-storage.cisco.com/ciscoblogs/5c6d7a4e78bd6.txt)

###  域名

    
    
    cheapairlinediscount[.]site
    emailerservo[.]science
    faxpctodaymessage[.]press
    faxpctodaymessage[.]space
    faxpctodaymessage[.]website
    faxzmessageservice[.]club
    fazadminmessae[.]info
    housecleaning[.]press
    hrent[.]site
    irepare[.]site
    macmall[.]fun
    managerdriver[.]website
    mantorsagcoloms[.]club
    mediaaplayer[.]win
    mobileshoper[.]science
    plomnetus[.]club
    ppservice[.]stream
    progresservesmail[.]science
    proservesmail[.]science
    proservesmailing[.]science
    searchidriverip[.]space
    servemai[.]science
    servemaining[.]science
    serveselitmail[.]science
    serveselitmailer[.]science
    servesmailelit[.]science
    servesmailerpro[.]science
    servesmailerprogres[.]science
    servespromail[.]science
    servicemaile[.]science
    serviveemail[.]science
    servoemail[.]science
    servomail[.]science
    

###  IP Address

    
    
    107[.]173[.]193[.]242
    107[.]173[.]193[.]243
    107[.]173[.]193[.]244
    107[.]173[.]193[.]246
    107[.]173[.]193[.]247
    107[.]173[.]193[.]248
    107[.]173[.]193[.]249
    107[.]173[.]193[.]250
    107[.]173[.]193[.]251
    107[.]173[.]193[.]252
    107[.]173[.]193[.]253
    162[.]251[.]166[.]72
    172[.]245[.]159[.]130
    185[.]212[.]44[.]114
    192[.]3[.]204[.]226
    192[.]3[.]204[.]228
    192[.]3[.]204[.]229
    192[.]3[.]204[.]231
    192[.]3[.]204[.]232
    192[.]3[.]204[.]233
    192[.]3[.]204[.]234
    192[.]3[.]204[.]235
    192[.]3[.]204[.]236
    192[.]3[.]204[.]237
    192[.]3[.]207[.]115
    192[.]3[.]207[.]116
    192[.]3[.]207[.]117
    192[.]3[.]207[.]118
    192[.]3[.]207[.]119
    192[.]3[.]207[.]120
    192[.]3[.]207[.]123
    192[.]3[.]207[.]124
    192[.]3[.]207[.]125
    192[.]3[.]207[.]126
    192[.]3[.]31[.]211
    192[.]3[.]31[.]214
    192[.]3[.]45[.]90
    192[.]3[.]45[.]91
    192[.]3[.]45[.]92
    192[.]3[.]45[.]93
    192[.]3[.]45[.]94
    64[.]110[.]25[.]146
    64[.]110[.]25[.]147
    64[.]110[.]25[.]148
    64[.]110[.]25[.]150
    64[.]110[.]25[.]151
    64[.]110[.]25[.]152
    64[.]110[.]25[.]153
    64[.]110[.]25[.]154
    

###  虚假域名

    
    
    www[.]analiticsmailgooglefaxidload[.]onlinsedsa
    www[.]wewanaliticsmailgooglefaxidload[.]oeenlinsedsa
    www[.]lovisaaa[.]oedsdenlinsedrwersa
    www[.]weryoseruisasds[.]oedsdenlinsedrwersa
    www[.]dencedence[.]denceasdq
    www[.]goooglwas[.]freesaf
    dgdfgdfgdfg
    faxdaytodayd
    mailsssssssssssdddaas[.]com
    mailsmessage[.]comssaaa
    mailsmaasessage[.]comssssaaa
    sssaaalllsaallsaaaasssaaa[.]comssssaaa
    lvelalslllasaasss[.]lllassaassaa
    1122212121212[.]1221212
    00000000000000[.]11111111
    11111[.]222222222222
    someserver
    someserversdfdfdf[.]111
    www[.]wikipedia[.]000212[.]nl
    wikipedia[.]112000212[.]com

本文翻译自blog.talosintelligence.com
[原文链接](https://blog.talosintelligence.com/2019/02/combing-through-brushaloader.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **MoonKey** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/171517](/post/id/171517)

安全客 - 有思想的安全新媒体

本文转载自:
[blog.talosintelligence.com](https://blog.talosintelligence.com/2019/02/combing-through-brushaloader.html)

如若转载,请注明出处： <https://blog.talosintelligence.com/2019/02/combing-through-brushaloader.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)

 **+1** __2赞

 __收藏

![](https://p1.ssl.qhimg.com/t017d0ebb688dc22d8e.png) MoonKey

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


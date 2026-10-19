# 【APT报告】海莲花团伙利用MSBuild机制免杀样本分析

阅读量 **195938**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-11-23 15:44:48

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**背景**

****

进入2017年以来，360威胁情报中心监测到的海莲花APT团伙活动一直处于高度活跃状态，近期团伙又被发现在大半年内入侵了大量网站执行水坑式攻击。
**海莲花团伙入侵目标相关的网站植入恶意JavaScript获取系统基本信息，筛选出感兴趣的目标，诱导其执行所提供的恶意程序从而植入远控后门。**

基于所收集到的IOC数据，360威胁情报中心与360安全监测与响应中心为用户发现了大量被入侵的迹象，协助用户做了确认、清除及溯源工作，在此过程中分析了团伙所使用的各类恶意代码样本。为了顺利实现实现植入控制，海莲花团伙所使用的恶意代码普遍加入了绕过普通病毒查杀体系的机制，利用带白签名程序加载恶意DLL是最常见的方式。除此之外，部分较新的恶意代码利用了系统白程序MSBuild.exe来执行恶意代码以绕过查杀，以下为对此类样本的一些技术分析，与安全社区分享。

  

**MSBuild介绍**

****

MSBuild是微软提供的一个用于构建应用程序的平台，它以XML架构的项目文件来控制平台如何处理与生成软件。Visual Studio会使用MSBuild，
**但MSBuild并不依赖Visual Studio，可以在没有安装VS的系统中独立工作。**

按照微软的定义，XML架构的项目文件中可能包含属性、项、任务、目标几个元素，其中的任务元素中可以包含一些常见的操作，比如复制文件或创建目录，甚至编译执行写入其中的C#源代码。如下是一个XML项目文件的例子：

其中的Message标签指定了一个Message任务，它用于在生成期间记录消息。

用MSBuild加载处理这个helloworld.xml项目文件，我们看到Message任务被执行，输出了”hello world”。

除了如上的系统预定义的内置任务，MSBuild还允许通过Task元素实现用户自定义的任务，功能可以用写入其中的C#代码实现，
**我们看到的海莲花样本正是利用了自定义Task来加载执行指定的恶意代码。**

  

**样本分析**

****

我们所分析的样本主要的执行流程为：使用MSBuild解密执行一个Powershell脚本，该Powershell脚本直接在内存中加载一个EXE文件，执行以后建立C&C通道，实现对目标的控制。

利用MSBuild的加载执行

样本的初始执行从MSBuild.exe开始，攻击者把恶意代码的Payload放到XML项目文件中，调用MSBuild来Build和执行，下图为调用MSBuild程序的命令行属性：

其中SystemEventsBrokers.xml文件内容如下：

文件中指定的Task对象的Execute方法被重载了，功能代码用C#实现，变量aaa是一块经过Base64编码的数据，C#的处理逻辑其实只是简单地对aaa做Base64解码并在编码转换以后交给Powershell执行。下图为aaa变量对应的数据做编码转换以后的Powershell脚本：

可以看到这块代码还是经过混淆的，通过层层解码执行，最终得到的代码如下：

该脚本的功能主要是把var_code的数据经过Base64解密后在内存中执行，var_code解密后其实为一段shellcode。首先它会通过call/pop指令序列获取到后面所附加数据的地址，数据起始在0xf63+0x0a处，头部的前两个字节为0x4567，地址存在ebp-0x68中，如下图：

通过PEB获取kernel32基址，然后获得 **GetProcAddress** 的地址：

之后通过 **GetProcAddress** 获取一些API的地址。

获取的API包括：

Ø **VirtualAlloc**

Ø **VirtualFree**

Ø **LoadLibraryA**

Ø **Sleep**

获取系统调用地址完成后，Shellcode先判断所附加数据的前2个字节是否为0x4567来确认是否为自己构造的文件，如果是则继续执行：

接下来会调用VirtualAlloc申请一片可执行的内存，并把后面附带的PE文件分别复制到该内存中：

PE在内存中初始化完毕，这里就开始执行PE入口代码：

下图为内存中加载的PE的OEP处：

将此PE文件提取出来，我们发现文件的PE头和NT头的标志被故意修改了，PE头被改为0x4567，NT头被改为0x12345678，如图：

把此2处修改后，恢复正常PE的结构，可以查看PE的基本信息如下，版本信息伪装来自苹果公司：

  

**远控程序分析**

****

该文件是一个EXE程序，功能为支持DNSTunnel通信的远控Server。程序中的字符串都做了简单的加密处理，下图为入口处初始化用到的API的地址：

解密算法有2种，一种是单字节+0x80获取ASCII的明文字符串，另一种为双字节+0x80获取UNICODE的明文字符串：

**1、 解密DLL模块名的函数如下：**

解密函数是每2个字节加上0x80，遇到0结束，得到模块的字符串：

**2、 解密API函数的的函数：**

每一个字节+0x80，遇到0结束，得到明文的字符串：

然后通过枚举模块导出表的形式获取函数的地址并存到参数里：

解密出域名，解密的算法一样：

解密出的域名如下：

Ø facebook-cdn.net

Ø z.gl-appspot.org

Ø z.tonholding.com

Ø z.nsquery.net

使用UDP协议连接8.8.8.8（Google DNS服务器）的53端口或208.67.222.222 （OpenDNS）的53端口；

调用sendto把符合DNS请求格式的数据包发送出去：

数据包信息如下，使用Base64编码：

该样本也支持TCP协议：

然后进入远控消息分发模块：

如下为消息分发执行函数，第4-8字节为命令的Token：

后门Token对应的恶意功能映射列表如下：

**总结**  

****

本文中所分析的样本所包含的后门Payload为2017年上半年海莲花团伙的样本，但加载方式上换用了通过MSBuild加载，这种加载恶意代码的方式本质上与利用带正常签名的PE程序加载位于数据文件中的恶意代码的方法相同。原因在于：

**一、MSBuild是微软的进程，不会被杀软查杀，实现防病毒工具的Bypass；**

**二、很多Win7电脑自带MSBuild，有足够大的运行环境基础，恶意代码被设置在XML文件中，以数据文件的形式存在不易被发现明显的异常。**

  

**IOC**

****

**C &C** **域名**  
  
---  
  
facebook-cdn.net  
  
z.gl-appspot.org  
  
z.tonholding.com  
  
z.nsquery.net  
  
**注册表键值**  
  
KEY_CURRENT_USER SoftwareINSUFFICIENTINSUFFICIENT.INI  
  
**互斥体**  
  
8633f77ce68d3a4ce13b3654701d2daf_[用户名]  
  
**Payload** **文件名**  
  
SystemEventsBrokers.xml  
  
NTDSs.xml  
  
  

**参考链接**

****

MSBuild

<https://docs.microsoft.com/zh-cn/visualstudio/msbuild/msbuild>

MSBuild入门 – Blackheart – 博客园:

<https://www.cnblogs.com/l_nh/archive/2012/08/30/2662648.html>

Cybereason Labs Discovery: Operation Cobalt Kitty: A large-scale APT in Asia
carried out by the OceanLotus Group:

<https://www.cybereason.com/blog/blog-cybereason-labs-discovery-operation-cobalt-kitty-a-large-scale-apt-in-asia-carried-out-by-the-oceanlotus-group>

  

**欢迎加入我们**

****

目前360威胁情报中心还在提供 **安全事件分析员**
的职位，欢迎有恶意代码逆向分析基础的同学上船。在360威胁情报中心你才有机会看到真正的货色面临真正的挑战，工作地点北京、武汉、成都，投
**wangliejun@360.net** 。

  

**传送门：**[
**【北京招聘】360企业安全诚聘安全人才（四餐免费，免费健身房按摩室）**](http://bobao.360.cn/introduce/detail/281.html)

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87299](/post/id/87299)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


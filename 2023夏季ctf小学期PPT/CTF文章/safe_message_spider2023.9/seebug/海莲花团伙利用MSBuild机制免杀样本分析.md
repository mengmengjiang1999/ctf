作者：[360威胁情报中心](https://mp.weixin.qq.com/s/3v_dGXGZ_RkVyMxl6s3MIg "360威胁情报中心")

#### 背景

进入2017年以来，360威胁情报中心监测到的海莲花APT团伙活动一直处于高度活跃状态，近期团伙又被发现在大半年内入侵了大量网站执行水坑式攻击。海莲花团伙入侵目标相关的网站植入恶意JavaScript获取系统基本信息，筛选出感兴趣的目标，诱导其执行所提供的恶意程序从而植入远控后门。

基于所收集到的IOC数据，360威胁情报中心与360安全监测与响应中心为用户发现了大量被入侵的迹象，协助用户做了确认、清除及溯源工作，在此过程中分析了团伙所使用的各类恶意代码样本。为了顺利实现实现植入控制，海莲花团伙所使用的恶意代码普遍加入了绕过普通病毒查杀体系的机制，利用带白签名程序加载恶意DLL是最常见的方式。除此之外，部分较新的恶意代码利用了系统白程序MSBuild.exe来执行恶意代码以绕过查杀，以下为对此类样本的一些技术分析，与安全社区分享。

#### MSBuild介绍

MSBuild是微软提供的一个用于构建应用程序的平台，它以XML架构的项目文件来控制平台如何处理与生成软件。Visual
Studio会使用MSBuild，但MSBuild并不依赖Visual Studio，可以在没有安装VS的系统中独立工作。

按照微软的定义，XML架构的项目文件中可能包含属性、项、任务、目标几个元素，其中的任务元素中可以包含一些常见的操作，比如复制文件或创建目录，甚至编译执行写入其中的C#源代码。如下是一个XML项目文件的例子：

![](https://images.seebug.org/content/images/2017/11/533d17f1-396c-47cb-a2f4-bd48f0e2e794.jpg-w331s)

其中的Message标签指定了一个Message任务，它用于在生成期间记录消息。

用MSBuild加载处理这个helloworld.xml项目文件，我们看到Message任务被执行，输出了“hello world”。

![](https://images.seebug.org/content/images/2017/11/048f1f95-5061-4ad9-907d-37b5e6e3c417.jpg-w331s)

除了如上的系统预定义的内置任务，MSBuild还允许通过Task元素实现用户自定义的任务，功能可以用写入其中的C#代码实现，我们看到的海莲花样本正是利用了自定义Task来加载执行指定的恶意代码。

#### 样本分析

我们所分析的样本主要的执行流程为：使用MSBuild解密执行一个Powershell脚本，该Powershell脚本直接在内存中加载一个EXE文件，执行以后建立C&C通道，实现对目标的控制。

##### 利用MSBuild的加载执行

样本的初始执行从MSBuild.exe开始，攻击者把恶意代码的Payload放到XML项目文件中，调用MSBuild来Build和执行，下图为调用MSBuild程序的命令行属性：

![](https://images.seebug.org/content/images/2017/11/a29dfa4d-94ca-405c-ae53-906cda411e39.jpg-w331s)

其中SystemEventsBrokers.xml文件内容如下：

![](https://images.seebug.org/content/images/2017/11/54109796-27a3-4fd1-ba5e-5cb03f68bde7.jpg-w331s)
![](https://images.seebug.org/content/images/2017/11/5264e316-2b20-4dcc-a32d-4d1e75151b7e.jpg-w331s)

文件中指定的Task对象的Execute方法被重载了，功能代码用C#实现，变量aaa是一块经过Base64编码的数据，C#的处理逻辑其实只是简单地对aaa做Base64解码并在编码转换以后交给Powershell执行。下图为aaa变量对应的数据做编码转换以后的Powershell脚本：

![](https://images.seebug.org/content/images/2017/11/89e2e738-d7e0-4f54-b990-e77ca9141c88.jpg-w331s)

可以看到这块代码还是经过混淆的，通过层层解码执行，最终得到的代码如下：

![](https://images.seebug.org/content/images/2017/11/80451b02-1a59-42eb-be9b-715b1b6f657f.jpg-w331s)

该脚本的功能主要是把var_code的数据经过Base64解密后在内存中执行，var_code解密后其实为一段shellcode。首先它会通过call/pop指令序列获取到后面所附加数据的地址，数据起始在0xf63+0x0a处，头部的前两个字节为0x4567，地址存在ebp-0x68中，如下图：

![](https://images.seebug.org/content/images/2017/11/f7b3668d-5844-48dd-8eff-1b4ca5869e62.jpg-w331s)

通过PEB获取kernel32基址，然后获得GetProcAddress的地址：

![](https://images.seebug.org/content/images/2017/11/38d4535c-bd67-4410-ac57-03e84e02c7a3.jpg-w331s)
![](https://images.seebug.org/content/images/2017/11/d92d6597-7c53-422d-8b3e-8e93da7ecbbb.jpg-w331s)
![](https://images.seebug.org/content/images/2017/11/370c99d0-2c27-4546-90f0-03d89ca4d890.jpg-w331s)
![](https://images.seebug.org/content/images/2017/11/3bd10bb4-a027-4c1e-91f3-fb3369402245.jpg-w331s)
![](https://images.seebug.org/content/images/2017/11/e6a223e6-1022-4f32-8da3-d1de56f1d36a.jpg-w331s)

之后通过GetProcAddress获取一些API的地址。

获取的API包括：

  * VirtualAlloc
  * VirtualFree
  * LoadLibraryA
  * Sleep

![](https://images.seebug.org/content/images/2017/11/79b846f8-41a0-49e9-b8a3-0308bd68fcc3.jpg-w331s)

获取系统调用地址完成后，Shellcode先判断所附加数据的前2个字节是否为0x4567来确认是否为自己构造的文件，如果是则继续执行：

![](https://images.seebug.org/content/images/2017/11/711b9412-d48a-4b6e-8352-23aaa4c30fcc.jpg-w331s)

接下来会调用VirtualAlloc申请一片可执行的内存，并把后面附带的PE文件分别复制到该内存中：

![](https://images.seebug.org/content/images/2017/11/5ecc21ca-ec0e-458c-8e47-d75811896168.jpg-w331s)

PE在内存中初始化完毕，这里就开始执行PE入口代码：

![](https://images.seebug.org/content/images/2017/11/cce2ef0e-9046-490b-a17f-71da73caee8b.jpg-w331s)

下图为内存中加载的PE的OEP处：

![](https://images.seebug.org/content/images/2017/11/a00b5913-d415-4694-ab58-6acdf4cfa191.jpg-w331s)

将此PE文件提取出来，我们发现文件的PE头和NT头的标志被故意修改了，PE头被改为0x4567，NT头被改为0x12345678，如图：

![](https://images.seebug.org/content/images/2017/11/e82a07d2-dbed-4826-b40b-6a4e45d13dd9.jpg-w331s)

把此2处修改后，恢复正常PE的结构，可以查看PE的基本信息如下，版本信息伪装来自苹果公司：

![](https://images.seebug.org/content/images/2017/11/6f707f8e-768c-42fb-b73f-13fb32ccafe3.jpg-w331s)

#### 远控程序分析

该文件是一个EXE程序，功能为支持DNSTunnel通信的远控Server。程序中的字符串都做了简单的加密处理，下图为入口处初始化用到的API的地址：

![](https://images.seebug.org/content/images/2017/11/f4da77c9-19f6-41b3-9a42-b941392e260f.jpg-w331s)

解密算法有2种，一种是单字节+0x80获取ASCII的明文字符串，另一种为双字节+0x80获取UNICODE的明文字符串：

  1. 解密DLL模块名的函数如下：

![](https://images.seebug.org/content/images/2017/11/d3fb0a27-29d5-4332-8138-684abfac9ab7.jpg-w331s)

  1. 解密API函数的的函数：

每一个字节+0x80，遇到0结束，得到明文的字符串：

![](https://images.seebug.org/content/images/2017/11/5671bbf9-5bcc-4eb2-b2f7-ca1284c215e3.jpg-w331s)
![](https://images.seebug.org/content/images/2017/11/b1081bd6-f5f0-4b20-8828-595d39902eaa.jpg-w331s)

然后通过枚举模块导出表的形式获取函数的地址并存到参数里：

![](https://images.seebug.org/content/images/2017/11/3c87f789-3594-4590-8710-52f4a70cbe18.jpg-w331s)

解密出域名，解密的算法一样：

![](https://images.seebug.org/content/images/2017/11/71392404-3bae-4bb3-9112-db84cf1269e2.jpg-w331s)

解密出的域名如下：
![](https://images.seebug.org/content/images/2017/11/6117fa77-45f2-4135-8f61-ad98b3d08e9b.jpg-w331s)

  * facebook-cdn.net
  * z.gl-appspot.org
  * z.tonholding.com
  * z.nsquery.net

使用UDP协议连接8.8.8.8（Google DNS服务器）的53端口或208.67.222.222 （OpenDNS）的53端口；

![](https://images.seebug.org/content/images/2017/11/cbf64dc8-d592-4339-ada2-229e80f1db28.jpg-w331s)

调用sendto把符合DNS请求格式的数据包发送出去：

![](https://images.seebug.org/content/images/2017/11/f3d3a820-3ce5-4427-a022-df9a21c4904f.jpg-w331s)

数据包信息如下，使用Base64编码：

![](https://images.seebug.org/content/images/2017/11/b91bdca7-24e2-4b92-bd18-dbe414deb846.jpg-w331s)

该样本也支持TCP协议：

![](https://images.seebug.org/content/images/2017/11/a258f6f0-f53e-42e8-87d0-ab15ddc1e7ef.jpg-w331s)
![](https://images.seebug.org/content/images/2017/11/f53893bb-20b1-4f5c-b98c-373b099908b2.jpg-w331s)
![](https://images.seebug.org/content/images/2017/11/7233cc66-971e-4fd3-8bcd-4ce3b79aa49e.jpg-w331s)

然后进入远控消息分发模块：

![](https://images.seebug.org/content/images/2017/11/0be79146-65cd-449a-a024-10d13482e1a4.jpg-w331s)

如下为消息分发执行函数，第4-8字节为命令的Token：

![](https://images.seebug.org/content/images/2017/11/b90e9a05-dc6a-4feb-b3ac-764fa18c290c.jpg-w331s)

后门Token对应的恶意功能映射列表如下：

![](https://images.seebug.org/content/images/2017/11/1201ff91-0f27-44ca-a799-5990f8fe7e3e.jpg-w331s)

#### 总结

本文中所分析的样本所包含的后门Payload为2017年上半年海莲花团伙的样本，但加载方式上换用了通过MSBuild加载，这种加载恶意代码的方式本质上与利用带正常签名的PE程序加载位于数据文件中的恶意代码的方法相同。原因在于：一、MSBuild是微软的进程，不会被杀软查杀，实现防病毒工具的Bypass；二、很多Win7电脑自带MSBuild，有足够大的运行环境基础，恶意代码被设置在XML文件中，以数据文件的形式存在不易被发现明显的异常。

#### IOC

![](https://images.seebug.org/content/images/2017/11/aa698913-ae30-4686-9e29-d562157e5672.png-w331s)

#### 参考链接

MSBuild  
<https://docs.microsoft.com/zh-cn/visualstudio/msbuild/msbuild>

MSBuild入门 - Blackheart - 博客园:  
<https://www.cnblogs.com/l_nh/archive/2012/08/30/2662648.html>

Cybereason Labs Discovery: Operation Cobalt Kitty: A large-scale APT in Asia
carried out by the OceanLotus Group:  
<https://www.cybereason.com/blog/blog-cybereason-labs-discovery-operation-cobalt-kitty-a-large-scale-apt-in-asia-carried-out-by-the-oceanlotus-group>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/462/>


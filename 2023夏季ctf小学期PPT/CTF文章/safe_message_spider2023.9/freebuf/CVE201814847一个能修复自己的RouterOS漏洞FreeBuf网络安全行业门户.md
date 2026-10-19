2018年10月7日，来自全球知名高科技网络安全公司Tenable的安全研究人员Jacob
Baines针对CVE-2018-14847[2]发布了一段新的概念验证（PoC）代码[1]，实现了在受漏洞影响的MikroTik路由器上的远程代码执行。我们第一时间对PoC进行了研究，目前我们对漏洞利用的部分改进已经合入了Tenable的Github仓库[7]。本文将对CVE-2018-14847目录穿越漏洞成因进行分析，同时阐述我们的一些发现，如何通过受此漏洞影响的Winbox指令进行任意文件上传，从而实现一些更有趣的利用方式。我们能够利用CVE-2018-14847在RouterOS
6.42中触发后门shell，或在其他漏洞的配合下，通过在LD_LIBRARY_PATH中注入动态链接库的方法，对存在漏洞的可执行文件进行热补丁修复。我们还将在文章中介绍一种“修改”只读文件系统修复漏洞的方法。

# 漏洞分析

## 环境简介

MikroTik
RouterOS是一个基于Linux开发的网络设备操作系统，兼容x86、ARM、MIPS等多种CPU架构，因此RouterOS也可以安装在PC上将其作为软路由，提供防火墙、VPN、无线网络等多种功能与服务。

RouterOS提供了多种途径对其进行管理与配置，包括SSH、Telnet、Web界面（Webfig）与客户端软件（Winbox）等。本文讨论的漏洞，位于RouterOS与客户端软件Winbox通信过程中所使用的Winbox私有协议中。

RouterOS官网提供了针对多种CPU架构的ISO安装镜像，我们下载6.41.3版本的ISO镜像并安装一个虚拟机。

![1.png](https://image.3001.net/images/20191028/1572245931_5db691abf3a9b.png!small)  

在虚拟机中配置好IP等基本设置后，我们对各个配置项进行探索，可以总结出一些基本认知。

1\.
RouterOS可以通过Web（80端口）、SSH（22端口）、Winbox（8291端口）、Telnet（23端口）进行远程访问，使用相同的用户名与密码进行身份验证。

2\. 命令行方式访问（SSH、Telnet）会登录到一个厂商定制的shell界面，只能运行厂商实现的管理功能，无法运行Linux命令。

![2.png](https://image.3001.net/images/20191028/1572245947_5db691bb9755c.png!small)  

3\. 通过Webfig途径登录后，与服务器的交互全部通过一个名为master-min-xxxxx.js的脚本进行加密传输。这个加密协议我们下文将称之为JSProxy。

![3.png](https://image.3001.net/images/20191028/1572245970_5db691d23f1dc.png!small)![4.png](https://image.3001.net/images/20191028/1572245970_5db691d25e425.png!small)  

4\.
Webfig与Winbox途径提供的配置选项几乎完全相同，根据Tenable与Talos等前人的研究，二者在传输层的编码方式上有些许差异，但在应用层的指令编号、指令参数等保持一致。

![5.png](https://image.3001.net/images/20191028/1572245983_5db691dfbb4f8.png!small)  

## 协议分析

在上节我们提到，使用GUI管理RouterOS的两个方式Webfig网页端与Winbox客户端，分别采用JSProxy与Winbox协议与RouterOS进行通信，下面我们将分别分析两种协议的通信格式。

在JSProxy通信过程中，浏览器与服务器通信采用变种的MS-CHAP-2方式生成会话密钥，并用于全程的数据加解密，在此我们不作深入讲解，通过JSProxy我们能够略窥RouterOS控制所需要的指令格式与指令映射关系。

![6.png](https://image.3001.net/images/20191028/1572246021_5db69205aad9d.png!small)  

对JSProxy的payload进行解密后，我们得到一条条JSON编码的数据。基本格式如下：

![7.png](https://image.3001.net/images/20191028/1572246042_5db6921aa6c79.png!small)  

JSON数据中的每个键值对包含了三种信息：字段类型、字段名、字段值。JSON键的第一个字母（上图蓝色部分）代表字段类型，包括字符串、整型、布尔值、数组等。JSON键的剩下6个十六进制位（上图红色部分）代表字段名，通常是一个编号，表示数据值的含义，我们下文称之为key
ID。JSON值（上图黄色部分）就是这个字段的数据值。

到这里我们可以了解到，RouterOS管理页面的通信方式是通过键值对的请求与回复实现的，键值对的编码方式在JSProxy与Winbox中不尽相同，但数据含义是相同的。我们对
master-min-xxxxx.js进行分析，一个好消息是，我们可以在其中找到所有keyID。

![8.png](https://image.3001.net/images/20191028/1572246192_5db692b027b4f.png!small)  

而Winbox协议的二进制编码格式，我们可以从Winbox客户端中分析得到。我们寻找到了一个关键函数，功能是将Winbox消息转换成字符串进行日志输出，四舍五入等于开源了。

![9.png](https://image.3001.net/images/20191028/1572246205_5db692bd95b48.png!small)  

Winbox协议二进制格式的大致格式分为6字节的消息头，与依次紧密排列的键值对，大于255字节的消息会插入两字节的长度数据作为消息分片。

![10-.png](https://image.3001.net/images/20191028/1572246219_5db692cb3393d.png!small)  

其中键值都是以小端序传输，同样采取类似“数据类型-键-值”的格式。

![11.png](https://image.3001.net/images/20191028/1572246232_5db692d84dc9a.png!small)  

借助Cisco Talos实验室开源的Winbox协议Wireshark解析插件[9]。我们能非常直观的看到数据中各个字段与原始数据的对应关系。

![12.png](https://image.3001.net/images/20191028/1572246246_5db692e666f24.png!small)  

当然这个插件还有一些不足之处，无法解析所有类型的数据包，但对于我们，能够对数据包进行过滤和简单查看一下对应关系就足够了。

## 关键漏洞：目录穿越、任意文件读写（CVE-2018-14847）

CVE-2018-14847漏洞发生在漏洞上传的位置。我们如何知道文件上传指令发给谁，文件由谁接收，保存到哪里呢？我们需要先定位哪个程序在RouterOS上负责接收用户上传的文件。

从Winbox消息中，我们注意到不同指令会发送给不同的目的组件，从JSProxy中我们能够得知这个目的地位于SYS_TO字段对应的字段中。这个字段是两个int32组成的数组，第一个数字对应了系统中的一个程序，第二个数字对应了这个程序的第几个功能。Tenable对系统中保存了这个对应关系的数据文件/nova/etc/loader/system.x3进行了分析，并制作了一个名为parse_x3的小工具，我们可以在Tenable的Github仓库中的parse_x3目录找到。

![13.png](https://image.3001.net/images/20191028/1572246262_5db692f65be3b.png!small)  

根据这个对应关系，结合抓包我们能够得知，文件上传请求的SYS_TO值为{0x02,0x02}，对应的二进制文件位于/nova/bin/mproxy。

![14.png](https://image.3001.net/images/20191028/1572246321_5db6933120edf.png!small)  

我们从RouterOS的ISO文件中提取出对应的二进制文件。文件位于mikrotik-6.41.3.iso\system-6.41.3.npk\nova\bin\mproxy，直接用7-zip打开iso和里面的npk，拖出来即可（很多地方其实用不着binwalk）。

在对mproxy进行分析的过程中，Tenable通过功能（handler）实现对应的基类nv::Handler找到了每个程序里面的所有功能的所有编号，并编写了一个Binary
Ninja脚本寻找程序中的所有handler，从而快速定位功能对应的函数，这个小工具位于Github仓库中的find_handlers目录中，有兴趣的同学可以尝试一下。

![15.png](https://image.3001.net/images/20191028/1572246338_5db69342d557e.png!small)  

我们尝试找一个简单点的方法，从另外一个角度定位对应的函数。我们在Winbox客户端中正常上传一个文件，并寻找上传的文件所在的路径。当然，假如现在是黑盒测试的话，我们可以用其他的方法获得文件系统的访问权，例如利用其他漏洞进行提权、直接修改文件系统植入shell等等。我注意到文件系统根目录下有很多的符号链接，其中有一些链接到可写目录中，所以我在这里用find
-follow跟随符号链接确保我们能够定位到文件的所有可能的路径。

![16.png](https://image.3001.net/images/20191028/1572246367_5db6935f72a48.png!small)  

通过这种方法获得的路径，与mproxy程序中出现的字符串进行交叉比对，我们可以得到结论：mproxy程序中，某个负责文件上传的函数能够上传文件至/var/pckg目录中。

![17.png](https://image.3001.net/images/20191028/1572246385_5db69371aade6.png!small)  

再通过这个字符串的交叉引用，我们就能够定位到我们所需的关键函数，我们命名为ked_handler。

![18.png](https://image.3001.net/images/20191028/1572246401_5db693816ef4a.png!small)  

对这个函数进行分析，我们可以得出ked_handler函数大致有7个功能，以传入的第5个参数进行选择，有以下7个取值（以IDA伪代码中出现顺序排序）：

l 功能1：在/var/pckg目录下创建文件，返回一个用于写入数据的session

l 功能3：打开/var/pckg目录下的一个文件，返回一个用于读取数据的session

l 功能7：打开/home/web/webcfg目录下的一个文件，返回一个用于读取数据的session

l 功能2：向一个打开文件的session写入数据

l 功能4：从一个打开文件的session读取数据

l 功能5：中止一个session并删除先前写入的文件

l 功能6：在/var/pckg目录下新建一个目录

通过对抓包数据进行分析，我们发现官方客户端在读取并下载文件时调用的是3号功能，而Tenable的poc调用的是7号功能。

![19.png](https://image.3001.net/images/20191028/1572246449_5db693b13cd39.png!small)  

与这两个功能相关的部分逻辑如下。

![20.png](https://image.3001.net/images/20191028/1572246466_5db693c2cc31e.png!small)  

其中，tokenize函数对传入的字符串按 /
字符进行切分，返回一个字符串数组。ked_check_path函数采用类似状态机的方式有限制的允许“..”字符串，不允许穿越到父目录中。但函数中没有对“.”（即，当前目录）进行验证，所以我们可以构造类似“/./../”的payload，让函数误以为我们进入1级子目录后返回了当前目录，但实际我们进入了父目录，成功实现目录穿越。ked_check_path这个函数可以说是搬起石头砸了自己的脚。

通过伪代码我们能看到这三个功能都没有对输入参数进行正确过滤，应该存在相同的目录穿越漏洞。这两个命令理论上都能利用来进行任意写入，实际情况呢？

关键点在权限上，对ked_handler进行调用回溯，我们能够定位到mproxy的main函数中，向eventloop注册handler的代码片段。在添加handler前，程序调用了set_policy对7个命令进行了某种设置，据Tenable的深入研究，这几条函数调用与handler中相关功能的调用权限相关。第三个参数为0的时候，代表调用此功能无需登录。由以上代码可知，功能命令4、5、7的调用无须登录。

![21.png](https://image.3001.net/images/20191028/1572246519_5db693f73c9d1.png!small)  

到这里，我们已经实现了对系统根目录的任意文件读写。

## 关键漏洞：开发者后门（Tenable exp: bytheway）

下一个问题，有了权限，我们能做什么呢？当然是Getshell了！我们前面提到，即使我们有管理员账号密码，ssh登录进去依然是一个功能受限的shell，不能执行Linux指令。Tenable在报告中提出了一种利用厂商开发者后门进行提权的方法。这个后门与上文提到的目录穿越漏洞，在RouterOS
6.42.1与6.40.8版本一并得到修复。

这个漏洞存在于ssh和telnet登录时运行的/nova/bin/login中。命令行登陆时，程序先正常向用户请求输入用户名和密码，然后根据两个判断条件：用户名是否等于devel、hasOptionPackage返回是否为非0值，如果都符合则进入下一个代码块。

![22.png](https://image.3001.net/images/20191028/1572246585_5db69439b690d.png!small)  

其中，hasOptionPackage函数位于/lib/libumsg.so中，它的取值依据为/pckg/option文件是否存在。

![23.png](https://image.3001.net/images/20191028/1572246602_5db6944acd7a4.png!small)  

确认用户名与OptionPackage后，程序将用户名重置为admin，并设置一个标志位，指示后门的激活状态。

![24.png](https://image.3001.net/images/20191028/1572246618_5db6945aa8fce.png!small)  

处理一部分其他逻辑之后，程序再次检查这个标志位，如果后门激活，则将shell运行的实际命令设置为bash。根据PATH环境变量的设置，最后命中并执行文件系统中名为/bin/bash（实际是一个busybox）的交互式命令行。

![25.png](https://image.3001.net/images/20191028/1572246634_5db6946a049c3.png!small)![26.png](https://image.3001.net/images/20191028/1572246634_5db6946a2180f.png!small)  

这个后门的触发逻辑在RouterOS的不同版本中略有不同。根据Tenable的研究，在RouterOS
6.40.9以下版本中，依据的文件是/flash/nova/etc/devel-login，在6.41.1以下版本中，判断的是/pckg/option，在6.42以上版本中，对/pckg/option文件类型做了额外的验证，但依然能够通过修改文件系统的方式进行触发。

## 利用方式总结

根据上面的两个漏洞的细节，我们已经可以总结出整个漏洞利用的过程：

1\. 构造payload，调用功能7，打开/flash/rw/store/user.dat文件，获得session id。

2\. 调用功能4，用这个session id读取文件内容。

3\. 用其他工具解密管理员账户的明文密码。

4\. 调用{0x0d，0x04}号handler进行Winbox管理员登录（模拟Winbox客户端登录，协议细节不再赘述），获得管理员权限session
id。

5\. 调用功能1，用管理员session在/pckg/option创建空文件。

6\. 用管理员明文密码登录ssh/telnet，获得root shell。

整个的利用过程已经被Tenable总结出了一个漏洞利用程序bytheway，在他们的Github中可以找到。

# 漏洞复现

我们在这里使用的是基于Tenable的bytheway进行修改后的exploit。

![27.png](https://image.3001.net/images/20191028/1572246657_5db694814921d.png!small)  

交互过程如下：

![28.png](https://image.3001.net/images/20191028/1572246672_5db694902ecb7.png!small)  

根据RouterOS版本不同，触发后门需要的文件也不同，因此exploit里面将两个文件都创建了，尽量兼容更多的版本。

# One More Thing

漏洞复现了就结束了？NO。我们在公网上部署了多台测试环境对RouterOS漏洞的利用行为进行捕获，从攻和守两个角度都有一些新的发现。我们接下来将介绍一个帮我们“修复”漏洞的好心攻击者与我们对其修复方法的复现，还有我们发现的另一种漏洞利用方法，同时介绍如何利用这种方法反过来修复这个漏洞。

## “删除”只读rootfs系统文件

挖矿、蠕虫、僵尸网络等攻击行为不再多说，都是常规操作。在其中一个设备上，我们发现了一个好心的攻击者帮助我们“修复”了后门shell。具体表现是，“修复”后的设备能够通过ssh登录管理界面，也能通过exp触发后门，但却无法登录devel用户，输入正确的密码后却被断开连接。估计是某个病毒的作者想要防止其他攻击者利用这个漏洞，所以好心帮我们“修复”了。可以说是滑天下之大稽。

![29.png](https://image.3001.net/images/20191028/1572246689_5db694a195b2e.png!small)  

通过对设备文件系统的分析和虚拟机上的复现，我们猜测这个设备上的/bin/bash文件被“删掉”了。但问题是，PATH变量是硬编码的不可能修改，而/bin目录所在的根文件系统是只读挂载的squashfs，所以删除系统文件是怎么实现的呢？

前面我提到了特殊意义的“删掉”，是因为我们重新分析线上环境的文件系统时，发现/bin/bash并没有被删，所以下面的这种漏洞“修复”方式仅是我们能够复现的一种猜想。

首先我们想知道，在系统目录中有哪些是可写入的。

![30.png](https://image.3001.net/images/20191028/1572246704_5db694b02f127.png!small)  

我们选择/ram，并用随便一种方式上传一个完整版busybox进去（因为RouterOS自带的mount进行bindmount时会报错）。随后，在可写目录中新建bin文件夹并将/bin目录中的内容复制进去，并用mount将新目录挂载到/bin目录之上，实现“覆盖”的效果。由下图可见，我们断开连接后再次登录，就会在登录成功后马上断开，提示消息为Connection
Closed而不是漏洞修复后提示的Permission denied。

![31.png](https://image.3001.net/images/20191028/1572246719_5db694bf2e5ba.png!small)  

用这种方式实现的修改，并没有真实写入文件系统，在重启之后，后门依然可以访问。病毒作者可以说是用心良苦哇。

这个思路同样可以用于一些敏感的生产环境系统，很多嵌入式设备都采用squashfs或者其他用于Flash芯片的只读文件系统，如果对可用性有较高的要求，不能接受重启、系统升级带来的服务中断的话，可以用类似的目录挂载方式对系统进行热修复。

## CVE-2018-14847的其他用途

在对CVE-2018-14847漏洞进行分析的时候，我产生了一个疑问。既然功能1、3、7共享这个目录穿越漏洞，那理论上我们可以在未授权的情况下向系统任意目录写入任意文件。也许我们不需要开发者后门，也可以实现远程代码执行。

我尝试利用Tenable的协议库winbox_message.hpp编写一些poc，利用ked_handler中功能1提供的session写入文件，在可写的路径上传busybox。但服务器对上传的功能2指令没有任何响应。通过对Winbox客户端上传功能的分析，我发现Tenable的协议库中对长度大于256字节的message处理有一些小bug。

下图以一个文件上传数据包内容为例，以全0数据方便我们观察原始数据格式。方框部分就是Tenable协议库遗漏的部分，我们在winbox_session.cpp中，在每个消息分片之前加入分片长度值与截断标记，修复后的数据包就和Winbox客户端发送的协议格式完全相同了。

![32.png](https://image.3001.net/images/20191028/1572246738_5db694d27d01a.png!small)  

进行修复以后，调用mproxy的功能2能够正常上传文件到指定位置，在修复之前，因为其他header的存在，最多只能上传209字节的文件，更大的文件请求就会因为消息分片格式的问题被mproxy丢弃。这个patch我们也提交到了Github上。现在，我们打开了另一扇大门。

### 不依赖开发者后门的漏洞利用方法

最开始我的设想，直接利用上传功能覆盖一个系统可执行文件，并触发对应的功能。但后来发现有两个难点。一是从未授权用户的角度来看，能够调用的程序就那么几个，/nova/bin/login与mproxy、telnet和ssh服务器等，这些程序所在的挂载点都是只读的，root用户也无法覆盖。二是通过功能2创建的文件默认权限都是644，即可读可写不可执行，即使传上去了也会因为权限问题无法启动。

不过对RouterOS有了更多的了解后，我有了一个设想。查看shell登录以后的环境变量：

![33.png](https://image.3001.net/images/20191028/1572246755_5db694e3c9988.png!small)  

我们发现，LD_LIBRARY_PATH中包含了多个目录，/lib在根文件系统下，是只读的。/pckg是一个指向/ram/pckg的符号链接，/pckg/security/lib与/pckg/user-manager/lib只在安装了对应的可选包才会出现，也都是只读的。/rw是一个指向/flash/rw的符号链接，这个目录是可写的。虽然/rw/lib目录在默认配置下不存在，但我们可以通过上文的目录穿越漏洞调用ked_handler的功能6进行创建，从而使这个漏洞的利用成为可能。

LD_LIBRARY_PATH是一个危险的东西。利用这个环境变量，我们可以实现在任何程序运行前对程序的行为进行修改，甚至在程序运行时实现进程注入。子进程可以继承父进程的环境变量，而系统中绝大多数应用都是loader进程的子进程（下图PID
276）。

![34.png](https://image.3001.net/images/20191028/1572246771_5db694f3e2e8f.png!small)  

因此，将payload封装为so库，放置在LD_LIBRARY_PATH中的可写路径/rw/lib下，即可实现对接下来任意启动的进程进行注入并实现命令执行——比如我们在命令行登录时，就会启动一个/nova/bin/login。

### 在RouterOS 6.42+植入后门shell

用这个思路，我们还可以在无法触发后门的6.42版本中，使用老版本libumsg.so重新引入这个后门，对RouterOS“越狱”会有帮助。前面我们提到，

这个后门的触发逻辑在RouterOS的不同版本中略有不同。根据Tenable的研究，在RouterOS
6.40.9以下版本中，依据的文件是/flash/nova/etc/devel-login，在6.41.1以下版本中，判断的是/pckg/option，在6.42以上版本中，对/pckg/option文件类型做了额外的验证，但依然能够通过修改文件系统的方式进行触发。

RouterOS
6.42+中，远程触发开发者后门几乎是不可能的，攻击者更不可能跑到别人家里去拆掉Flash芯片往里塞后门。意味着即使攻击者拿下了用户名密码，但他也仅仅能访问GUI中有限的控制选项，不能植入payload利用设备获得更多的经济利益。

我们前面分析过，与后门相关的控制逻辑，有一部分位于/lib/libumsg.so中，准确来讲是nv::hasOptionPackage函数。既然我们已经能够进行任意文件上传，同时我们能够控制LD_LIBRARY_PATH，那么我们简单的将RouterOS
6.41.x中的libumsg.so复制出来，再在6.42.x的系统中利用目录穿越漏洞调用ked_handler的功能6创建/rw/lib目录并将libumsg.so上传上去，因为LD_LIBRARY_PATH的函数加载优先级高于PE文件中定义的加载路径[8]，我们用这种方式即可实现后门触发，在6.42.x系统中启用ssh
shell。

因为不想再写代码了，为了从另一个角度验证这个思路的可行性，我们在RouterOS 6.41.x上设计了下面的实验。

### 在RouterOS 6.41.x上利用漏洞“修复”漏洞

我们现在有一个后门，我们还控制了LD_LIBRARY_PATH下可写的目录/rw/lib，同时能够创建这个目录并向其中写入文件。假如我现在的设备就是一个骨干路由，需要对漏洞进行紧急修复，我们现在来尝试一下，在不更新、不重启系统的情况下通过LD_LIBRARY_PATH预加载动态链接库关掉这个后门。

首先，我们确认后门可以正常工作，并创建/rw/lib目录。当然，我们也可以用漏洞来创建这个目录，我只是懒得写exp了（笑

![35.png](https://image.3001.net/images/20191028/1572246796_5db6950c2dad1.png!small)  

接下来，我们从RouterOS
6.42的ISO中提取出libumsg.so，并利用CVE-2018-14847（或者用你能想到的其他方法）上传到指定目录中。我在这里同时上传了一个busybox。

![36.png](https://image.3001.net/images/20191028/1572246809_5db69519b5593.png!small)  

上传成功后，kill掉所有名为login和sshd的进程。

![37.png](https://image.3001.net/images/20191028/1572246830_5db6952e9d6ad.png!small)  

这样一来，当前所有通过控制台、Telnet与ssh登录的终端都会被关闭，再次连接就会启动新进程，同时加载我们通过LD_LIBRARY_PATH植入的新版本libumsg.so，后门shell失效。

![38.png](https://image.3001.net/images/20191028/1572246847_5db6953f6b8e8.png!small)  

还记得我们在前面对开发者后门的分析吗？如果libumsg.so中的后门函数hasOptionPackage返回true后，登录session的用户名会被重置为admin，从而控制台中显示的登录成功、失败的日志中的用户名都会因此被修改。但后门修复之后，这一段程序逻辑不复存在，因此对后门的登录尝试也会在系统日志中显示出来。

![39.png](https://image.3001.net/images/20191028/1572246864_5db695503bad8.png!small)  

再结合我们前面提到的，用mount挂载魔改只读文件系统的方式，我们还可以用新版本覆盖根文件系统的/nova/bin/mproxy，将目录穿越漏洞一并修复掉。

我们再开个脑洞，整个漏洞修复过程分为三步：创建目录、上传修补程序、重启服务，这个过程完全可以自动化，一个脚本对全网存在漏洞的设备进行扫描修复。真正做出来肯定也会非常有趣吧。

# 后记

攻与防的较量，就是正常程序猿与脑洞程序猿的较量。不知攻，焉知防？知己知彼，方能百战不殆。

# 参考资料

[1] Bug Hunting in RouterOS 视频：<https://youtu.be/ItclhUF6MnA>
讲稿：<https://github.com/tenable/routeros/raw/master/slides/bug_hunting_in_routeros_derbycon_2018.pdf>

[2] MikroTik blog - CVE-2018-14847winbox vulnerability
<https://blog.mikrotik.com/security/winbox-vulnerability.html>

[3] MikroTik RouterOS AuthenticatedDirectory Traversal <https://zh-cn.tenable.com/security/research/tra-2019-16>

[4] GitHub - tenable/routeros:RouterOS Security Research Tooling and Proof of
Concepts <https://github.com/tenable/routeros>

[5] 深入分析MikroTik RouterOSCVE-2018-14847 & Get bash shell
<https://www.anquanke.com/post/id/162457>

[6] 基于 CVE-2018-14847 的 Mikrotik RouterOS 安全事件分析
<http://ith4cker.com/content/uploadfile/201811/aed91542039274.pdf>

[7] Fix message length issue withpacket bigger than 256 bytes
<https://github.com/tenable/routeros/pull/7>

[8] What is the order that Linux'sdynamic linker searches paths in? - Unix &
Linux Stack Exchange <https://unix.stackexchange.com/a/367682>

[9] GitHub -Cisco-Talos/Winbox_Protocol_Dissector <https://github.com/Cisco-Talos/Winbox_Protocol_Dissector>

  

****

****

****

****

****

****

********


## 一、前言

 **APT已经成为了安全领域热门的话题。**

Eleven Paths旗下Innovación y laboratorio 4月发表《Docless Vietnam APT》报告：

![](https://image.3001.net/images/20190617/1560743614_5d070ebe4666d.png!small)

上述信息表述，我们侦测到一些恶意邮件发送到属于越南政府的邮箱，这封越南语邮件的日期是2019年3月13号。这封邮件可能是来源于越南政府内部，不排除是有人把这封邮件投送到安全部门，因为这封邮件存在可疑因素。

TKCT quy I nam 2019.doc.lnk.malw样本信息如下：

![](https://image.3001.net/images/20190617/1560743632_5d070ed09a37c.png!small)

图片一：TKCT quy I nam 2019.doc.lnk.malw

## 二、静态分析

1\. TKCT quy I nam
2019.doc.lnk.malw样本被下载到本地后，巧妙伪装成Word快捷方式，欺骗受害运行或者习惯性双击查看，如下所示：

![](https://image.3001.net/images/20190617/1560743653_5d070ee5c0039.png!small)

图片二：伪装doc快捷方式

首先word文档一般不会是.lnk链接，链接的大小应该在1kb左右，而该APT样本快捷方式竟然126kb，很明显隐藏着别的东西，很多病毒把文件名伪装成.dat、.docx等，其实后缀是.exe，开启文件名扩展就可以看到。

2\. 提取样本属性中目标包含的恶意代码，发现是经混淆加密的一段cmd指令，且执行powershell，如下所示：

![](https://image.3001.net/images/20190617/1560743706_5d070f1ab23dd.png!small)

图片三：混淆指令

APT攻击手段非常青睐vbs、powershell、js等类型脚本语言，容易混淆与加密，而且方便做免杀处理。

所以历来的病毒及恶意软件都有这种共性，如蔓零花、Xbash、勒索都喜欢执行powershell作为第一个“见面礼”（payload）送给计算机当作惊喜。

3\. 解析混淆指令，发现重定向TKCT quy I nam
2019.doc.lnk快捷方式到s.sp1文件，其实桌面快捷方式是一个powershell的脚本文件，梳理混淆变量如下所示：

![](https://image.3001.net/images/20190617/1560743793_5d070f71bb30a.png!small)

最终将TKCT quy I nam 2019.doc.lnk重定向到temp文件夹下，命名为s.ps1执行该powershell，如下所示：

![](https://image.3001.net/images/20190617/1560743803_5d070f7b0ecba.png!small)

图片四：去混淆

4\. 手动去除iex混淆也是可以的，打开文件去掉“iex”这几个字符，powerhell运行指令格式：文件名（原） >>
s.sp1（新文件名）即可，重定向文件如下所示：

![](https://image.3001.net/images/20190617/1560743819_5d070f8b9ff74.png!small)

![](https://image.3001.net/images/20190617/1560743821_5d070f8dc48b4.png!small)

图片五：powershell恶意代码

5\.
如图五所示，发现了两段Base64编码的数据，powershell意图将编码后的恶意数据执行，添加定时任务，每9分钟执行创建，利用了InstallUtil服务实现了自启动与持久性化，有意思的利用Wscript.Shell执行，越出其不意越有意想不到的效果，如下所示：

![](https://image.3001.net/images/20190617/1560743833_5d070f9963cf6.png!small)

![](https://image.3001.net/images/20190617/1560743833_5d070f9971b65.png!small)

图片六：s.sp1

6\. Base64编码数据解析后，其实是两个可执行文件，分别是恶意.net与.doc，执行手段如下图所示：

![](https://image.3001.net/images/20190617/1560743898_5d070fda253ba.png!small)

![](https://image.3001.net/images/20190617/1560743864_5d070fb84ad75.png!small)

图片七：通用的套路

7\.
分析tmp_pFWwjd.dat.exe，经过dnSpy工具反汇编后，代码清晰可见，虽然有一些小混淆（可以使用de4dot.exe去混淆即可），不影响代码程度。

定位关键函数Exec(),发现Base64String编码的数据，根据执行流程，由.NET去委托去调用函数Call，而且是可读可写，那么就要申请内存VirtualAlloc(),将Base64shellcode拷贝到申请内存中，获取CreateThread()指针委托执行回调指针，执行恶意的shellcode，如下所示：

![](https://image.3001.net/images/20190617/1560743924_5d070ff49314b.png!small)

图片八：.net反汇编

如何理解shellcode或payload？本质上可以是说一堆十六进制组成的数据，对于可执行文件来说则是能够被汇编引擎所解释执行的数据。

因为下面将会涉及二进制数据提取与汇编分析，所以这里做了一副简单的图先介绍关于shellcode或者payload基本概念(针对恶意代码)，如下图所示：

![](https://image.3001.net/images/20190617/1560743942_5d07100659edb.png!small)

图片九：payload

如图九所示，对于病毒来说，特别是可自启动，持久化攻击,没有后门很难实现（漏洞持续化利用，每次拉取少量流量做数据窃取之类的除外）。

举例来说，ASLR地址随机化每次系统重启后基址都会改变，或者注入到新的进程空间，代码本身的函数基址都是错误的，如何精准的获取函数地址？从而达到完美运行，需要格外的一些操作，当然这些都不是问题，技术相对成熟。

下面一段知识所讲述的内容，假设读者对Windows
PE格式及汇编、内核相关内容有一定的基础。不会普及基础知识，将从PE格式及汇编层面去分析这些shellcode如何去做，如何实现动态获取模块基址如kernel32.dll，如何利用散列值或者Hash遍历导出表，过免杀敏感字符串及敏感函数API等。

## 三、PE与病毒杂谈

以上述的恶意代码举例，因为.net执行shellcode调试过程中遇到诸多问题，所以用c/c++还原了tmp_pFWwjd.dat.exe样本。

再一次OD进行动态调试，当然可以Dump下来分析，根据个人爱好，直接在执行shellcode下断，如下所示：

![](https://image.3001.net/images/20190617/1560743968_5d071020a5508.png!small)

图片十：Pointer

1\. 入口点进入，接着就是数据的异或解密，将需要真正执行的恶意代码还原，如下所示：

![](https://image.3001.net/images/20190617/1560743993_5d07103933567.png!small)

图片十一：异或解密

2\. 散列值加密字符串，这样的好处既可以减少shellcode体积，而且可以隐蔽敏感字符，不容易被杀毒软件截获，如下所示：

![](https://image.3001.net/images/20190617/1560744006_5d0710462270d.png!small)

图片十二：散列值获取函数地址

3\. 我们进入函数1E0A42，发现一堆看上去很平常的赋值操作，如下所示：

![](https://image.3001.net/images/20190617/1560744018_5d071052d83af.png!small)

图片十三：fs:[0x30]

Fs是寄存器，内核态是fs = 0x30，用户态 fs = 0x3B，fs在内核态指向_KPCR，用户态指向_TEB。

TEB(Thread Environment
Block)，线程环境块，也就是说每一个线程都会有TEB，用于保存系统与线程之间的数据，便于操作控制。那么Fs:[0x30]就是PEB进程环境块。

4\.
PEB就是当前进程环境，shellcode就可以轻易获取PEB信息，通过偏移0xc获取到了_PEB_LDR_DATA,这个结构体包含有关进程的已加载模块的信息.

通过偏移0x1c获取到一个双向循环链表，每个链表指向LDR_DATA_TABLE_ENTRY结构体，这个结构体包含的数据我们来看一下，以上数据偏移与操作系统有关，如下所示：

![](https://image.3001.net/images/20190617/1560744030_5d07105e14de0.png!small)

图片十四：获取模块基质

![](https://image.3001.net/images/20190617/1560744042_5d07106af024a.png!small)

图片十五：获取当前环境模块基址步骤

5\. 通过上述的过程，就会成功获取如ntdll.dll，如下所示：

![](https://image.3001.net/images/20190617/1560744062_5d07107eb3426.png!small)

图片十六：获取模块Address

6\.
继续分析函数1E0B2A,两个参数，根据函数调用约定，参数1是kernel32基地址，参数2是函数名散列值，该函数则是一个自己实现的GetProcAddress()函数，如下所示：

![](https://image.3001.net/images/20190617/1560744082_5d07109269916.png!small)

图片十七：GetProcAddress

7\. 该函数会判断是不是PE标准格式，然后获取NT头，获取导出表。导出表保存了三张表的地址，先来看导出表结构体，如下所示：

![](https://image.3001.net/images/20190617/1560744095_5d07109fd6c78.png!small)

恶意代码需要定位到这三张表的地址，遍历函数名称表AddressOfName,获取函数名进行散列值计算，如果与参数2散列值相同，意味着是同一个函数。

返回当前遍历的下标，通过下标去函数序号表AddressOfNameOrdinals找到对应的序号，获取序号表保存的数值，在函数地址表中获取AddressOfFunctions，如下图所示简单表述了三者关系：

![](https://image.3001.net/images/20190617/1560744106_5d0710aa30868.png!small)

图片十八：三者关联

如上图所示，序号表与名称表一一对应，下标与下标中存储的值是相关联的，这三张表设计巧妙，利用了关系型数据库的概念。

需要注意的是，序号不是有序的，而且会有空白。地址表中有些没有函数名，也就是地址表有地址却无法关联到名称表中，这时候用序号调用，序号内容加上Base序号基址才是真正的调用号。

8\. 当有了这些认知，再来看样本中的恶意代码，会发现与上述的描述是一摸一样的，如下所示：

![](https://image.3001.net/images/20190617/1560752331_5d0730cbad585.png!small)

![](https://image.3001.net/images/20190617/1560752331_5d0730cbaf88d.png!small)

图片十九：GetProcAddress()

9\. 最后验证结果是否成功，如下所示：

![](https://image.3001.net/images/20190617/1560752332_5d0730cc18dfb.png!small)

图片二十：验证

![](https://image.3001.net/images/20190617/1560752339_5d0730d375421.png!small)

11\. 创建了新得线程，线程回调会创建目录及文件，但是本地验证创建文件失败，如下所示：

![](https://image.3001.net/images/20190617/1560752347_5d0730dbb3312.png!small)

图片二十一：创建目录

创建文件及目录名路径c:\User\\......\AppData\Roaming\

![](https://image.3001.net/images/20190617/1560752358_5d0730e605d97.png!small)

11\. 服务器响应及下载恶意代码，这将开启一段新得旅程，如下所示：

![](https://image.3001.net/images/20190617/1560752367_5d0730ef42e5f.png!small)

图片二十二：DownLoader

![](https://image.3001.net/images/20190617/1560752380_5d0730fc393b4.png!small)

## 四、vkT2模块分析

1\. 跟进函数后我们发现了大量的散列值，动态获取函数地址，与上述函数调用一致，梳理函数名如下：

![](https://image.3001.net/images/20190617/1560752391_5d073107483cd.png!small)

1E0AAA函数解密如下：

![](https://image.3001.net/images/20190617/1560752400_5d073110ac073.png!small)

2\. 做了预热操作，其实根据函数名称，应该猜测到接下来会发生什么，如下图所示：

![](https://image.3001.net/images/20190617/1560752492_5d07316ce547c.png!small)

图片二十三：InternetOpenA

![](https://image.3001.net/images/20190617/1560752511_5d07317fe8429.png!small)

图片二十四：InternetConnectA

![](https://image.3001.net/images/20190617/1560752526_5d07318e25fdb.png!small)

图片二十五：HttpOpenRequestA

3\.
动态调试过程中会卡断在请求，静态分析代码，lstrcmpiA比较下载数据的指纹信息text字段是否为plain，然后利用InternetReadFile读取下载数据执行，否则的话将陷入睡眠、请求死循环状态。

![](https://image.3001.net/images/20190617/1560752536_5d073198f2f19.png!small)

图片二十六：请求状态

我们根据已知的ip与请求格式，直接访问该网页，如下所示：

![](https://image.3001.net/images/20190617/1560752558_5d0731ae140de.png!small)

图片二十七：vkT2

发现Web解析的全是乱码？下载到本地，根据原代码执行流程，这是一段二进制数据，老规矩写个程序来调试这段恶意代码。

4\. vkT2分析，先是解密了数据，然后动态获取函数地址,样本惯用的老套路了。

循环拼接各区段(节表)数据，这里按照VirtuallAddress，各区段在加载到内存后的地址循环拼接，内存的对齐粒度0x1000，抹掉了DOS头特征码,形成了一个PE格式文件，如下所示：

![](https://image.3001.net/images/20190617/1560752586_5d0731cad4327.png!small)

![](https://image.3001.net/images/20190617/1560752572_5d0731bc5fd1d.png!small)

图片二十八：内存扩展

5\.
既然是PE格式扩展到了内存里面，接下来就是修复了IAT表与重定位了，这里涉及的面比较多，还属于PE格式内容，可查阅《Windows权威指南》，如下图所示：

![](https://image.3001.net/images/20190617/1560752616_5d0731e811da0.png!small)

图片二十九：修复IAT

6\. 接下来分析关键要点，获取了系统变量，判断是否运行在64bit系统上，如下所示：

![](https://image.3001.net/images/20190617/1560752632_5d0731f8626a1.png!small)

![](https://image.3001.net/images/20190617/1560752634_5d0731fa57ff0.png!small)

![](https://image.3001.net/images/20190617/1560752634_5d0731fa6b8d1.png!small)

图片三十：判别运行环境

8\. 系统数据、主机ip、主机名等信息收集，如下所示：

![](https://image.3001.net/images/20190617/1560752649_5d0732097047c.png!small)

![](https://image.3001.net/images/20190617/1560752651_5d07320ba5d15.png!small)

![](https://image.3001.net/images/20190617/1560752651_5d07320bb0efa.png!small)

图片三十一：数据收集

9\. 新一轮的C&C通信开始，如下图示所示：

![](https://image.3001.net/images/20190617/1560752661_5d07321596fcd.png!small)

图片三十二：建立通信

9\.
继续分析，使用函数HttpOpenRequest和HttpSendRequest打开文件。HttpOpenRequest创建个请求句柄并且把参数存储在句柄中，HttpSendRequest把请求参数送到HTTP服务器，如下所示：

![](https://image.3001.net/images/20190617/1560752669_5d07321dba2d3.png!small)

![](https://image.3001.net/images/20190617/1560752669_5d07321dc2a47.png!small)

图片三十三：HttpOpenRequest

![](https://image.3001.net/images/20190617/1560752683_5d07322ba2718.png!small)

![](https://image.3001.net/images/20190617/1560752683_5d07322bd4751.png!small)

图片三十四：HttpSendRequestA

11\. 遗憾的是HttpSendRequeSt已经没有什么响应了，静态分析剩余的代码(模拟执行)，读取服务器返回的恶意代码，有用到线程安全上下文。

情报分析没找到更有价值的数据，不过这种请求方式很独特，而且构造的数据包也很特别，下面会讲到这样做的特殊性。

关联样本过程，梳理执行流程图如下所示：

![](https://image.3001.net/images/20190617/1560752693_5d073235a9dd2.png!small)

图片三十五：TKCT quy I nam 2019.doc执行流程

如图三十五，客户端通信的服务器应该都是代理服务器，其实真是的环境远远要比上述过程复杂更多，这也是溯源的难点。

如图三十三，堆栈内存中提取关键的数据信息，这与往常的我们所见到的请求数据不太一样，梳理如下所示：

![](https://image.3001.net/images/20190617/1560752701_5d07323d0c02c.png!small)

APT通讯的手段越来越谨慎，如果不进行详细的样本分析，沙箱模拟运行、内存取证、抓包工具来对网络层面进行分析，结果与想要的数据可能有一定的出入，样本进行通信的时候，其实用到了域前端网络攻击技术。

什么是域前端网络攻击技术？简单点来说可以将msf、cs（Cobalt
Strike）等团队控制服务器的流量，目的用来绕过一定程度的防火墙与检测器，一些较大的厂商都会提供服务，所以用msf或cs等工具都可以实现。

我们用Cobalt Strike这款工具举例，集成了端口转发、扫描多模式端口Listener、Windows exe程序生成、Windows
dll动态链接库生成、java程序生成、office宏代码生成，包括站点克隆获取浏览器的相关信息等。

其中比较有用的一个功能就是Beacon
payload的行为，修改框架默认属性值，更改检入的频率及修改Beacon网络流量，而这些功能的配置都在文件Malleable C2。

Malleable-C2-Profiles功能就可以做到构造一个正常的Web伪装流量，最终达到通信隐匿的效果，我们摘取amazon.profile举例，如下所示：

    
    
    set useragent "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko";
    
    http-get {
    
    Seturi"/s/ref=nb_sb_noss_1/167-3294888-0262949/field-keywords=books";
    
    client {
    
    header "Accept" "*/*";
    
    header "Host" " [www.amazon.com](http://www.amazon.com) ";
    
    metadata {
    
    base64;
    
    prepend "session-token=";
    
    prepend "skin=noskin;";
    
    append "csm-hit=s-24KU11BB82RZSYGJ3BDK|1419899012996";
    
    header "Cookie";
    
    }
    
    http-post {
    
    set uri "/N4215/adj/amzn.us.sr.aps";
    
    client {
    
    header "Accept" "*/*";
    
    header "Content-Type" "text/xml";
    
    header "X-Requested-With" "XMLHttpRequest";
    
    header "Host" " [www.amazon.com](http://www.amazon.com) ";
    
    parameter "sz" "160x600";
    
    parameter "oe" "oe=ISO-8859-1;";
    
    id {parameter "sn";}
    
    parameter "s" "3717";
    
    parameter "dc_ref" "http%3A%2F%2F [www.amazon.com](http://www.amazon.com) ";
    
    }

上述代码与样本vkT2.shellcode通信的特征完全匹配，通过加载相应的profile文件，来改变目标主机与server端的流量特征，以此来隐藏流量，最终达到通信隐匿的目的。

详细的内容网上已有很多相关的好文，这里不做介绍，可以在参考连接中找到这些学术知识进行研究。

## 五、总结

APT攻击技术趋势与威胁情报的发展热度一直在上涨，不同种类的APT攻击趋势越加明显。

防御者在明，攻击者在暗，APT攻击具有一定的规模性，大量的资金及后台作为支撑，敌暗我明情况下，防御的结果往往令人不满意。

企业安全响应情报生成和评估，需要不断的驱动事件，周而复始收集、处理、分析、决策，将情报与驱动应急响应融合，完善网络安全态势感知，第一时间掌握攻击的”来龙去脉”，防患于未然。

样本链接：<https://bbs.kafan.cn/thread-2148052-1-1.html>

 ***本文作者：光通天下，转载请注明来自FreeBuf.COM**


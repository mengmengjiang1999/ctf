## 一、Cobalt Strike检测与发现背景

Cobalt Strike（Cobalt Strike is software for Adversary Simulations and Red Team
Operations. Cobalt Strike）
简称CS，是一款优秀的后渗透工具，可以在获取主机权限后进行长久权限维持，快速进行内网提权，凭据导出等。已知的多个APT组织都曾经使用过Cobalt
Strike攻击框架，如FIN6、Cobalt Group组织和“海莲花”等。同时该工具在近2年国内兴起的红蓝对抗演习中被使用的较多。

## 二、检测与发现方法：

从防守方流量检测的角度考虑，检测CS有几种思路

1.基于工具服务器默认特征的角度

将符合cs服务器特征（默认证书，默认端口）的ip加入到情报库，seebug上看到一篇文章讲如何用Cobalt
Strike绕过流量审计设备【1】，里面讲到三种去除cs特征的方式，修改默认端口，修改默认证书，修改默认dns。在攻击者修改掉默认配置后，检测方法失效。

2.基于Ip测绘的角度

fireeye的研究文章里提到该方式【2】， 针对3.13以前版本在zoomeye里通过如下语法搜索 "HTTP/1.1 404 Not Found
Date:" +"GMT Content-Type: text/plain Content-Length: 0" -"Connection:”
，基于其服务器的相应包的特点可以判断该服务器为cs。

![1603870950_5f9920e6467d122e4247c.png!small?1603870692335](https://image.3001.net/images/20201028/1603870950_5f9920e6467d122e4247c.png!small?1603870692335)

这种测绘方法是基于基于NanoHTTPD的特点来做，因此在一定程度上存在误报。

3 尝试基于流量本身的特点：

CS 提供Malleable C2。Malleable C2 允许我们仅通过一个简单的配置文件来改变 Beacon 与 C2 通信时的流量特征与行为.
Malleable
C2提供对http内容头内容进行定义，URL头及参数也可以定制，并提供4种加密的方法，因此在分析后认为仅通过流量特征无法检测CS流量。实际抓包：

![1603870990_5f99210e7371394aabde9.png!small?1603870732496](https://image.3001.net/images/20201028/1603870990_5f99210e7371394aabde9.png!small?1603870732496)

4.通过代码特点去检测：

CS可以生成宏，hta，shellcode，exe，下面仅对shellcode和exe进行分析

4.1Raw shellcode

Cobalt Strike可以通过Payload Generator 生成raw payload，raw payload

可以作为原始shellcode可以以PowerShell，PythonJava，c等语言生成。

![1603871033_5f99213931f3501a2f8e5.png!small?1603870775468](https://image.3001.net/images/20201028/1603871033_5f99213931f3501a2f8e5.png!small?1603870775468)

主要针对raw的形式进行特征分析。Payload由于是shellcode不能直接运行，需要用其他加载器将其加载起来，先分配一段内存，将shellcode放进去再调到这段新的内存开始执行。先看下raw形式的payload：

![1603871046_5f9921460d1d948b9edb5.png!small?1603870788122](https://image.3001.net/images/20201028/1603871046_5f9921460d1d948b9edb5.png!small?1603870788122)

Shellcode的第一条命令是cld（fc），cld使DF 复位，即是让DF=0

Sub_8f
的前面2个参数为“winnet.dll”，726774ch为kernel32!LoadLibrary的hash，0a779563h为winnet.dll!InternetOpenA的hash：

![1603871077_5f99216512a26862794c0.png!small?1603870819153](https://image.3001.net/images/20201028/1603871077_5f99216512a26862794c0.png!small?1603870819153)

sub_8f其中ebp的值为call的函数返回地址0x006，而其就是经典的shellcode处理IAT的操作，通过读取PEB中的InMemoryOrderModuleList获取dll地址并获取相应的导出表地址并通过dll名+函数名的hash值来调用导出函数。

![1603871087_5f99216fc82ba0b12302c.png!small?1603870829855](https://image.3001.net/images/20201028/1603871087_5f99216fc82ba0b12302c.png!small?1603870829855)

可以把shellcode开头的代码段作为特征，cld 接一个对近地址的call，FC E8 89 00 00 00 60 89 E5 31 D2 64 8B
52 30 8B 52 0C 8B做为流量检测特征1。

打开c#格式的：

![1603871106_5f9921823a4731c87d1f3.png!small?1603870848240](https://image.3001.net/images/20201028/1603871106_5f9921823a4731c87d1f3.png!small?1603870848240)

跟刚才的raw代码特征一样。

打开c格式的：

![1603871120_5f99219096a668dd14b40.png!small?1603870862665](https://image.3001.net/images/20201028/1603871120_5f99219096a668dd14b40.png!small?1603870862665)

java代码：

![1603871130_5f99219a332d9aef5555b.png!small?1603870872238](https://image.3001.net/images/20201028/1603871130_5f99219a332d9aef5555b.png!small?1603870872238)

都符合。

继续往下动态调试这段shellcode，会通过winnet.dll的通过如下的导出函数调用序列wininet.dll->InternetOpenA->InternetConnectA->HttpOpenRequestA->HttpSendRequestA->VirtualAlloc->InternetReadFile从服务器上下载第二阶段shellcode，通过抓包可以看到下载的第二阶段代码也有特征（FC
E8 03 00 00 ，

![1603871143_5f9921a7f38cb98bc5c4f.png!small?1603870886357](https://image.3001.net/images/20201028/1603871143_5f9921a7f38cb98bc5c4f.png!small?1603870886357)

这一段起始处的代码可以作为流量检测的特征2：FC E8 03 00 00 00 7A A4…

继续往下调试，会通过virtualalloc创建一段内存，将刚才从服务下载的代码读到新创建的内存：

![1603871157_5f9921b5c32b2d4b578ee.png!small?1603870900173](https://image.3001.net/images/20201028/1603871157_5f9921b5c32b2d4b578ee.png!small?1603870900173)

再进行这一段的新的shellcode执行，依然是cld开始：

![1603871171_5f9921c376a1c9d4f66c2.png!small?1603870913590](https://image.3001.net/images/20201028/1603871171_5f9921c376a1c9d4f66c2.png!small?1603870913590)

这一段shellcode依然是常用套路，virtualalloc一段内存，解密一段自身的代码放到新申请的内存段，然后通过peb找到各种库函数的导出函数，然后再跳转到这一段内存中去执行，解密完成后通过字符串可以确定这一段代码是Cobalt
Strike反射型注入后门模块beacon.dll：

![1603871185_5f9921d1d8377c8ab8d4e.png!small?1603870928163](https://image.3001.net/images/20201028/1603871185_5f9921d1d8377c8ab8d4e.png!small?1603870928163)

综上payload的流程 shellcode1（特征1）--下载-->shellcode2（特征2）—解密—-》beacon.dll

4.2 EXE(Stage/stageless)

cs的pe文件载荷分为stage和stageless两种。stage是把载荷分为几段，因此它的体积更小，主要用于加载后续阶段的复杂载荷。stageless则是把恶意代码全部包含在自身文件里一次性投递到目标机器上。stage的载荷更小，因此看起来似乎更容易绕过各种检测。

![1603871223_5f9921f77398cdae74dec.png!small?1603870965460](https://image.3001.net/images/20201028/1603871223_5f9921f77398cdae74dec.png!small?1603870965460)

以stage为例子开始分析,首先会创建并连接一个pipe

![1603871234_5f9922023e39fb292edc5.png!small?1603870976331](https://image.3001.net/images/20201028/1603871234_5f9922023e39fb292edc5.png!small?1603870976331)

接下来从pipe中读取加密的shellcode，再分配内存，将shellcode代码写入并解密

![1603871348_5f9922747b334ad205b57.png!small?1603871090549](https://image.3001.net/images/20201028/1603871348_5f9922747b334ad205b57.png!small?1603871090549)

解密算法为第一个红色方框中的代码，可以看到第二个框处为解密后的shellcode，这段shellcode也符合3.1中提出的shellcode特征1：

![1603871359_5f99227fae4efb6472d1d.png!small?1603871101961](https://image.3001.net/images/20201028/1603871359_5f99227fae4efb6472d1d.png!small?1603871101961)

之后进入shellcode执行，这段shellcode实际上就是payload
generator中产生的shellcode，stageless只是cs替攻击者实现了shellcode加载.

stage的入口点跟普通pe没有区别，因此不能像shellcode一样把入口点作为检测特征，可以选取创建pipe时候的名称字符串特征+代码特征作为检测点：

![1603871381_5f9922959e8265e1594da.png!small?1603871123733](https://image.3001.net/images/20201028/1603871381_5f9922959e8265e1594da.png!small?1603871123733)

![1603871386_5f99229ad4f51d6b724c6.png!small?1603871128979](https://image.3001.net/images/20201028/1603871386_5f99229ad4f51d6b724c6.png!small?1603871128979)

也可以选择这段查找pe文件头的代码做为检测点：

![1603871397_5f9922a537eb3cdd0ecb6.png!small?1603871139265](https://image.3001.net/images/20201028/1603871397_5f9922a537eb3cdd0ecb6.png!small?1603871139265)

stageless经过分析，前半部分的功能和stagless一样，代码功能也是一样的，只是最后的beacon.dll不用从服务器下载，因此我们之前选取的特征也可以相同使用。

其他的攻击载荷也可以通过分析得出类似的流量检测特征.

## 三、总结：

通过分析我们可以找到3大类数十个特征用于对CS流量和服务器进行检测发现，但是攻击方也可以有新的绕过方式，比如针对payload检测的情况，可以对shellcode进行加密或者对pe文件加壳等方式绕过特征检测，但是网络攻防的本质即是在对抗中螺旋前进，当攻击方有了新的方法绕过检测的时候，防守方也可以再通过研究新的攻击方法找到新的检测方式。

参考附录：

> [【1】https://paper.seebug.org/1349/](https://paper.seebug.org/1349/)
>
> [【2】https://www.fireeye.com/blog/threat-research/2020/07/scandalous-> external-detection-using-network-scan-data-and-> automation.html](https://www.fireeye.com/blog/threat-> research/2020/07/scandalous-external-detection-using-network-scan-data-and-> automation.html)，


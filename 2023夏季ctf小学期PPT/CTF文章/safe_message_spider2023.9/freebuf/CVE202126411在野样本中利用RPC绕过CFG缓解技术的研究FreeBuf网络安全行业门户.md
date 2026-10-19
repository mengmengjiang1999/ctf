浏览器渲染进程漏洞利用的一般思路是：在利用漏洞获得用户态任意地址读写权限后，通过篡改DOM、js等对象的虚表函数指针劫持程序执行流，通过ROP链调用VirtualProtect等Win32
API，修改保存shellcode
buffer的内存属性为PAGE_EXECUTE_READWRITE，最终由ROP链跳转到shellcode执行。Windows
8.1后，Microsoft引入了CFG（Control Flow
Guard）缓解技术[1]，对间接调用的函数指针进行验证，从而缓解了通过篡改虚表函数指针劫持程序执行流这种利用技术。

然而对抗不会因此终止，随后出现了一些绕过CFG缓解技术的新方法，比如chakra/jscript9中通过篡改栈上函数返回地址劫持程序执行流[2]，v8中利用具有可执行内存属性的WebAssembly对象执行shellcode[3]等。
2020年12月，Microsoft在Windows 10 20H1中基于Intel Tiger Lake
CPU加入了CET缓解技术[4]，防护了通过篡改栈上函数返回地址劫持程序执行流的利用方法。因此，如何在有CET防护的环境中绕过CFG再次成为漏洞利用的难题。

在分析CVE-2021-26411在野利用样本时[5]，我们发现了一种利用Windows RPC（Remote Procedure
Call）[5]绕过CFG的新方法，这种方法无需依赖ROP链，通过构造RPC_MESSAGE并调用rpcrt4!NdrServerCall2即可实现任意代码执行。

##  ** **1\. CVE**** ** **-2021-26411**** ** **回顾****

《IE浏览器在野0day：CVE-2021-26411分析》[5]
一文中介绍了该漏洞的根因：removeAttributeNode()触发属性对象nodeValue的valueOf回调，回调期间手动调用clearAttributes()，导致nodeValue保存的BSTR被提前释放。回调返回后，没有检查nodeValue是否存在继续使用该对象，最终导致UAF。

3月份Windows补丁中该漏洞的修复方法为，在CAttrArray::Destroy函数中删除对象操作前增加索引检查：

![](https://image.3001.net/images/20210421/1618986046_607fc43e8ea00d0a5efe6.png!small)

对于这样一个大小可控的UAF漏洞，利用思路为：利用两个不同类型的指针（BSTR和Dictionary.items）指向该空洞内存，通过类型混淆实现指针泄露和指针解引用：

![](https://image.3001.net/images/20210421/1618986071_607fc45772b2eda46223e.png!small)

##  ** **2\. RPC原理**** ** **及利用方法****

Windows RPC用来解决分布式客户端/服务端函数调用问题。基于RPC，客户端可以像调用本地函数一样调用服务端函数，RPC基本架构如下图：

![](https://image.3001.net/images/20210421/1618986098_607fc472932f2d420e3ea.png!small)

客户端/服务端程序将调用参数/返回值等传给下层Stub函数，Stub函数负责封装数据成NDR（Network Data
Representation）格式，最后通过rpcrt4.dll提供的runtime库进行通信。

下面给出一示例idl：

![](https://image.3001.net/images/20210421/1618986121_607fc489720881b060200.png!small)

当客户端调用add函数后，服务端由rpcrt4.dll接受处理请求并调用rpcrt4!NdrServerCall2：

![](https://image.3001.net/images/20210421/1618986139_607fc49b74d6ff09a562a.png!small)

rpcrt4!NdrServerCall2只有一个参数PRPC_MESSAGE，其中包含了客户端调用的函数索引、传参等重要数据，服务端RPC_MESSAGE结构及主要子数据结构如下图（32位）：

![](https://image.3001.net/images/20210421/1618986159_607fc4afe1782e022bc0e.png!small)

如上图所示，RPC_MESSAGE结构中，函数调用关键的两个变量为Buffer和RpcInterfaceInformation。其中Buffer存放了函数的传参，RpcInterfaceInformation指向RPC_SERVER_INTERFACE结构。RPC_SERVER_INTERFACE结构保存了服务端程序接口信息，其中+0x2c
DispatchTable保存了runtime库和Stub函数的接口函数指针，+0x3c
InterpreterInfo指向MIDL_SERVER_INFO结构。MIDL_SERVER_INFO结构保存了服务端IDL接口信息，其中DispatchTable保存了服务端提供的远程调用例程的函数指针数组。

下面以一个实例介绍RPC_MESSAGE的结构：

根据上面给出的idl，当客户端调用add(0x111, 0x222)，服务端程序断在rpcrt4!NdrServerCall2：

![](https://image.3001.net/images/20210421/1618986181_607fc4c517d148d95f93a.png!small)

可以看到，动态调试的内存dump与RPC_MESSAGE结构分析一致，其中add函数就存放在MIDL_SERVER_INFO.
DispatchTable中。

接下来分析rpcrt4!NdrServerCall2是如何根据RPC_MESSAGE调用add函数的：

rpcrt4!NdrServerCall2内部调用rpcrt4!NdrStubCall2，rpcrt4!NdrStubCall2内部根据MIDL_SERVER_INFO.
DispatchTable的基地址和RPC_MESSAGE.
ProcNum计算调用的函数指针地址，将函数指针、函数参数和参数长度传给rpcrt4!Invoke：

![](https://image.3001.net/images/20210421/1618986204_607fc4dca59f7d336ff78.png!small)

rpcrt4!Invoke内部最终调用服务端例程函数：

![](https://image.3001.net/images/20210421/1618986222_607fc4ee3a3e7dec3d7bb.png!small)

通过上面的分析可以知道，在获得任意地址读写权限后，可以构造一个RPC_MESSAGE数据结构，传入想要调用的函数指针和函数参数，最后手动调用rpcrt4!NdrServerCall2，即可实现任意函数执行。

接下来需要解决两个问题：

1）如何通过js脚本调用rpcrt4! NdrServerCall2

2）观察rpcrt4!Invoke最后的服务端例程函数调用：

![](https://image.3001.net/images/20210421/1618986245_607fc505a95106a4c8ab9.png!small)

可以看到这里是一处间接调用，且有CFG检查。因此需要考虑替换MIDL_SERVER_INFO.
DispatchTable函数指针后如何绕过这里的CFG防护。

首先解决问题1: 如何通过js脚本调用rpcrt4! NdrServerCall2

这里可以复用替换DOM对象虚表函数指针劫持程序执行流的方法，因为rpcrt4!NdrServerCall2是记录在CFGBitmap里的合法指针，所以替换后依然可以通过CFG检查。样本里通过篡改MSHTML!CAttribute::normalize，最终由“xyz.normalize()”调用rpcrt4!NdrServerCall2。

接着解决问题2: 如何绕过rpcrt4!NdrServerCall2中的CFG防护

样本里的思路是:

> 1)
> 利用伪造的RPC_MESSAGE和rpcrt4!NdrServerCall2调用VirtualProtect修改RPCRT4!__guard_check_icall_fptr内存属性为PAGE_EXECUTE_READWRITE
>
>
> 2)替换rpcrt4!__guard_check_icall_fptr里保存的指针ntdll!LdrpValidateUserCallTarget为ntdll!KiFastSystemCallRet，从而关闭rpcrt4的CFG检查
>
> 3) 恢复RPCRT4!__guard_check_icall_fptr内存属性

解决了问题1，2后，后续即可利用伪造的RPC_MESSAGE实现任意函数的调用。样本中将shellcode写入msi.dll +
0x5000的位置，最终通过rpcrt4!NdrServerCall2调用shellcode:

![](https://image.3001.net/images/20210421/1618986274_607fc522b977c1f22a9a9.png!small)

最终完整的利用演示：

![](https://image.3001.net/images/20210421/1618986292_607fc534dbbf01914f9f7.png!small)

##  ** **一些思考****

CVE-2021-26411在野样本中出现了利用RPC绕过CFG缓解技术的这一创新方法。这种利用方法无需构造ROP链，直接通过伪造RPC_MESSAGE即可实现任意代码执行，利用简单且稳定，有理由相信该方法会成为绕过CFG缓解措施的一种新的有效利用技术。

##  ** **参考文献****

[1] https://docs.microsoft.com/en-us/windows/win32/secbp/control-flow-guard

[2] https://zhuanlan.kanxue.com/article-14133.htm

[3] https://www.anquanke.com/post/id/201951

[4] https://windows-internals.com/cet-on-windows/

[5]
https://mp.weixin.qq.com/s?__biz=MzI4NjE2NjgxMQ==∣=2650250070&idx=1&sn=5906feea0cfe498bffbb961e73f5c285

[6] https://docs.microsoft.com/en-us/windows/win32/rpc/rpc-start-page

##  ** **团队简介****

深信服南研安全研究团队专注于APT攻击，在野漏洞利用追踪、研究、检测，攻防对抗等方向的研究工作。团队成员曾在Windows，MacOS/iOS，Linux/Android等主流操作系统中发现了上百个安全漏洞，在BlackHat
USA、BlackHat Europe、BlackHat Asia、HITB、Microsoft BlueHat、CodeBlue、HITCON、Virus
Bulletin、Pacsec、看雪SDC、FreeBuf CIS等国内外知名安全会议上发表过演讲和论文。


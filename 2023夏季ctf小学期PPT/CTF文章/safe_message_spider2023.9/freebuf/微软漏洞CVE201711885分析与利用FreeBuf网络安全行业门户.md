***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **根据微软官网对CVE-2017-11885的描述，该漏洞几乎可以通杀微软的全版本操作系统，有关该漏洞的POC在exploit-db上于2018年5月份被披露，该POC仅仅针对windows server 2003进行了测试。**

由于在相关描述中并没有获取到触发该漏洞的原因，因此在获取POC后，尝试对该漏洞进行复现并分析。

POC的关键代码如下：

![图片.png](https://image.3001.net/images/20180928/1538117513_5badcf89096e5.png!small)作者已经对该POC做了较为详细的注释，从stub的布局以及注释来看，第41行的stub数据可能会被传入到CALL
off_64389048[ECX*4]的ecx中，ecx如果是被控制的值，那么基本上可以直接在目标系统执行任意代码了。接下来搭建一个windows
server2003系统，并尝试通过该POC触发漏洞。

该漏洞仅当操作系统开启了RRAS服务才会存在，在windows server2003中，通过管理工具->路由和远程访问进行配置，结果如下：

![图片.png](https://image.3001.net/images/20180928/1538117524_5badcf941d8cc.png!small)开启了RRAS服务后，在另一台主机执行POC，并抓包。发现使用了SMB协议进行数据传输，pcap包数据如下图：

![图片.png](https://image.3001.net/images/20180928/1538117535_5badcf9f6f36a.png!small)随便打开一个包，发现是SMB协议并且通过445端口发送的数据，SMB协议后紧跟着DCERPC协议，对该协议的解释如下：

![图片.png](https://image.3001.net/images/20180928/1538117544_5badcfa8bd4ab.png!small)还是相对古老的协议，而微软的操作系统中的MSRPC协议是对DCERPC的一种实现，也算是第一代RPC协议。在这里简单介绍下RPC协议以及关键内容。

RPC 是指计算机 A 上的进程，调用另外一台计算机 B 上的进程，其中 A 上的调用进程被挂起，而 B 上的被调用进程开始执行，当值返回给 A 时，A
进程继续执行。A、B进程的交互过程如下图：

![图片.png](https://image.3001.net/images/20180928/1538117598_5badcfde66857.png!small)RPC应用程序的开发基于C/S模式，在windows环境下开发RPC所要实现的内容有：

> 1.IDL文件
>
> 2.ACF文件（可选）
>
> 3.客户端程序
>
> 4.服务端程序

IDL文件是接口描述文件，编写该文件所需的关键信息包含程序注册的uuid、函数调用接口以及参数的数据结构定义等。ACF文件可用来创建一些相对复杂的数据结构，这里不多关注。利用MIDL程序对IDL文件进行编译生成对应的客户端和服务端所需的头文件。客户端程序和服务端程序包含着关键调用函数的主体程序。其整个模式类似于我们通常的WINAPI调用，如我们调用ReadFile函数时，通常需要传递一部分参数，并得到一个返回值，在RPC编程中客户端程序负责参数的传递，服务端程序负责接收参数并执行相应的功能，随后将数据返回，整个过程对于开发人员是透明的，只不过是跨计算机的调用。RPC开发具体可参考微软的官方文档。

> 链接如下：<https://docs.microsoft.com/en-us/windows/desktop/rpc/rpc-start-page>

这里我们主要关注的内容包含RPC的协议传输方式、端点名称、以及具体的程序接口调用。该POC利用到了impacket这个库进行SMB以及rce协议的传输，POC中通过transport.DCERPCTransportFactory('ncacn_np:%s[\\\pipe\\\browser]'
% target)进行远程命名管道的链接，其中使用到的rpc协议为ncacn_np,通用的rpc协议如下：

![图片.png](https://image.3001.net/images/20180928/1538117614_5badcfee95f78.png!small)而且，SMB作为rpc的底层通信协议，一般都会同135、445这两个端口进行通信，一般的RPC
漏洞挖掘工具如spike等会通过特定端口查询rpc服务的名称数据库来获取一些关键信息，如下：

![图片.png](https://image.3001.net/images/20180928/1538117635_5badd003d3e9b.png!small)但是本次漏洞中的服务端程序无法通过客户端查询来获取信息，原因可能是因为服务端在绑定端点时采用了动态绑定的方式，并且没有将自身的相关信息绑定到名称服务中，将自身的信息导出到名称服务一般需要调用如下函数：

![图片.png](https://image.3001.net/images/20180928/1538117645_5badd00d86603.png!small)这样只有特定的程序才能够访问对应的服务端程序，一般的msrpc
fuzz工具在获取不到指定信息，也不会对远程服务进行fuzz，所以此类fuzz工具也难以挖掘到该类型的漏洞。

除了协议外，比较重要的一点就是远程的端点了，该POC中用到了/pipe/browser这个远程的命名管道，其实这个和RRAS协议中所规定的有点出入，在微软的官方文档[MS-RRASM]中指出，如果需要同RRAS服务进行交互，应该使用/pipe/ROUTER这个命名管道。

![图片.png](https://image.3001.net/images/20180928/1538117657_5badd019b3e1a.png!small)当然漏洞的发现者之所以用这个命名管道当然有他的用意，这涉及到了另一方面的操作系统缺陷即MSRPC
NULL
sessions，在很早以前有人做过研究，可能在渗透中会用的多一些。还有一个相对重要的就是uuid，这代表着唯一的远程服务端程序的标识，本次POC中对应的uuid为8f09f000-b7ed-11ce-bbd2-00001a181cad，同样在官方文档中也有说明，该uuid对应着RRAS服务的应用程序。

![图片.png](https://image.3001.net/images/20180928/1538117691_5badd03b596b1.png!small)  

接下来就开始对漏洞的调试分析，通过在win7、winserver2003、winserver2008上进行测试，发现仅能在win
server2003上触发漏洞，win7尚没有找到配置远程路由的功能，尽管开启了RRAS服务，但是无法触发漏洞。

由于微软不再维护win server2003的符号表，因此在调试起来很难确定函数的关键的信息，同时，由于使用的win
server2003可能打了补丁，导致在发送攻击报文后，并没有反弹shell，同时操作系统也没有产生异常，当时怀疑该漏洞是否需要其它条件才能触发，随后查看了win
server的事件日志记录，发现了一个appcrash记录，点击进去查看详细信息如下：

![图片.png](https://image.3001.net/images/20180928/1538117700_5badd0444e6a3.png!small)从图中看出svchost.exe发生了崩溃，而svchost具有是管理、开启服务的功能，因此猜测可能是RRAS服务在接收到攻击报文后发生了异常，异常的模块是iptrmgr.dll，利用ida打开该dll，同时跳转到偏移为0x17436的地方查看代码如下：

![图片.png](https://image.3001.net/images/20180928/1538117712_5badd05028f66.png!small)此处的代码和POC中提供的相对应，接下来利用调试工具对RRAS服务进行调试。由于在win
server2003进行调试，很多工具都无法使用，连最基本的windbg都无法使用，只能用最原始的OD来调试，还有一个问题就是如何找到RRAS对应的svchost程序，因为系统会开启多个svchost程序，在不考虑使用其他监控程序的情况下，可以使用tasklist
/M
iprtrmgr.dll来显示当前加载了iprtrmgr.dll这个模块的svchost，基本可以确定该svchost同RRAS服务相对应，结果显示如下：

![图片.png](https://image.3001.net/images/20180928/1538117723_5badd05b39cf8.png!small)接下来直接附加该程序，并在出现崩溃处的函数下断点，观察程序的状态如下：

![图片.png](https://image.3001.net/images/20180928/1538117732_5badd0644bd94.png!small)可以看出ecx的值来源于eax，而eax来自于第三个参数，在内存dump中可以看到这些是POC中构造的NDR(网络数据表示)数据，在MSRPC中，通过NDR引擎对参数格式进行编码、解码，比如客户端希望传递一个结构体指针类型的参数，该参数在IDL文件中被定义，在MIDL对IDL进行编译的时候，会将该参数通过NDR引擎编码转换成为可以通过网络传输的数据格式，在服务端由NDR引擎进行解码，并将解码后的参数传递给服务端程序，整个过程对程序员是透明的。在POC中，作者通过构造特定的NDR数据作为服务端的参数进行漏洞利用，观察0x64127058处的数据，发现该处保存着函数列表，如下：

![图片.png](https://image.3001.net/images/20180928/1538117742_5badd06e83d14.png!small)一共有0x23个函数，可以猜测服务端根据客户端的调用号ecx值来确定下一步的函数调用，但是当传入的ecx可以被控制时，那么通过ROP技术可以控制整个程序的流程。

漏洞发现者通过在内存中找到包含着jmp
eax这样的gadgets来实现漏洞利用，但是由于应用程序的版本问题导致特定地址的代码并非预期，指向了一个不可读的地址，因此这里会产生一个访问异常，使应用程序崩溃。

![图片.png](https://image.3001.net/images/20180928/1538117755_5badd07b51207.png!small)程序的调用栈当前无法正常显示，但是查看栈指针不难发现如下的函数调用：

![图片.png](https://image.3001.net/images/20180928/1538117765_5badd08573721.png!small)这里比较关键的是mprdim.dll，该dll存放着服务端的代码存根stub，利用ida的mIDA工具可以将RPC的IDL数据结构分析出来，通过对比发现win7和winserver上的代码基本类似，win7上也存在着本次的漏洞，由于win7上的dll可以获取到符号，因此下面的所有代码都是对应的win7版本的，将win7下的mprdim.dll利用mIDA工具进行分析的结果如下：

![图片.png](https://image.3001.net/images/20180928/1538117774_5badd08ecbe75.png!small)可以看到触发漏洞的函数为RMIBEntryGetFirst，该函数对应的调用号为0x1e(30)，通过wireshark查看RRAS协议的包格式也可以得到验证：

![图片.png](https://image.3001.net/images/20180928/1538117787_5badd09b32daa.png!small)接下来查看该函数的一些关键RPC数据结构，如下：

![图片.png](https://image.3001.net/images/20180928/1538117796_5badd0a4b392e.png!small)该函数以及对应数据结构在微软的官方文档有定义，如下：

![图片.png](https://image.3001.net/images/20180928/1538117824_5badd0c071b27.png!small)从第二个参数开始，分别对应着我们构造的三个参数，第三个关键的参数为DIM_MIB_ENTRY_CONTAINER结构，当dwPid=10000时，该结构体指向
MIB_OPAQUE_QUERY，该结构体声明如下：

![图片.png](https://image.3001.net/images/20180928/1538117834_5badd0ca84a55.png!small)在触发漏洞的函数中，ecx代表着dwVarID，而dwVarID对应着函数的编号，微软的解释如下：

![图片.png](https://image.3001.net/images/20180928/1538117845_5badd0d5c2580.png!small)在ida中体现如下：

![图片.png](https://image.3001.net/images/20180928/1538117895_5badd107c122c.png!small)通过ida查看该函数的整个实现发现，仅仅在开始对传入数据中的dwPid进行检测，而并没有对参数范围进行严格校验，导致其最终指向了rop
gadgets的地址。

在漏洞触发的地方查看关键的上下文信息，发现eax指向了用户传入的参数的缓冲区，而该内存的属性是RWE（可读可写可执行），简直为漏洞利用提供了完美的环境，不需要通过ROP来绕过DEP等防护技术，该漏洞更像是一个后门。

![图片.png](https://image.3001.net/images/20180928/1538117906_5badd1124f0c0.png!small)当然存在漏洞的也不只这一处函数，查看对函数表的引用可以发现共有三处，其执行逻辑基本类似，只要更改下函数调用号，同样可以触发。

![图片.png](https://image.3001.net/images/20180928/1538117933_5badd12dba7ae.png!small)前面提到过漏洞使用了/pipe/browser这个命名管道进行通信，该命名管道在winxp
、win server2003默认开启，并且是空会话格式的，意味着匿名的用户也可以进行访问，无需用户名、密码，但是在win
server2008上，微软关闭了大部分的命名管道，因此即便开启了RRAS服务，前期的通信尚无法建立，该漏洞自然无法成功利用，返回结果如下：

![图片.png](https://image.3001.net/images/20180928/1538117943_5badd13707cec.png!small)利用pipelist程序查看当前开启的命名管道，结果如下：

![图片.png](https://image.3001.net/images/20180928/1538117953_5badd14148856.png!small)但是全部无法通过远程访问，结果如下：

![图片.png](https://image.3001.net/images/20180928/1538117962_5badd14a9b456.png!small)所以，如果需要成功利用该漏洞，必须开启一个空会话的命名管道，启用方式如下：

![图片.png](https://image.3001.net/images/20180928/1538117971_5badd153bd0a9.png!small)这样就可以通过POC对win
server 2008进行攻击了，而且最重要的是调试起来相对更方便点，可以使用windbg并且加载符号进行调试。

微软目前已经对该程序打了补丁，打补丁的方式是在对参数的范围作了校验，如下：

![图片.png](https://image.3001.net/images/20180928/1538117981_5badd15dd258b.png!small)![图片.png](https://image.3001.net/images/20180928/1538117986_5badd16223509.png!small)

到此漏洞基本分析完毕。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**


* **严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

**9月7日，Metasploit发布了BlueKeep远程桌面命令执行漏洞[利用模块](https://github.com/rapid7/metasploit-framework/pull/12283)和[分析博客](https://blog.rapid7.com/2019/09/06/initial-metasploit-exploit-module-for-bluekeep-cve-2019-0708/)。工具适用于64位Win7系统及打开启用桌面音频播放功能的64位2008系统，本文将结合rdp相关实现对利用模块进行简要分析。**

## 漏洞原理

BlueKeep是一个释放后使用（Use After
Free）漏洞。存在漏洞的远程桌面服务器，在接收到特殊数据包时会释放一个内部信道MS_T120的控制结构体，但并未将指向该结构体的指针删除，而且在远程桌面连接结束之后还会调用MS_T120结构体内的一个函数指针，若攻击者可通过远程发送数据重新占据被释放的MS_T120，并为结构体内的函数指针赋恰当的值，即可实现远程命令执行。
关于漏洞利用的详细分析可参看雪安全峰会讲座的[相关内容](https://bbs.pediy.com/attach-download-173963.htm)，安全研究员Hutchins的
[分析](https://www.malwaretech.com/2019/09/bluekeep-a-journey-from-dos-to-rce-cve-2019-0708.html)和github用户0xeb-bp的[write-up](https://github.com/0xeb-bp/bluekeep/blob/master/0xeb_bp_BlueKeep_Technical_Analysis.pdf)

## Metasploit BlueKeep模块利用流程

基于[cve_2019_0708_bluekeep_rce.rb](https://github.com/rapid7/metasploit-framework/blob/edb7e20221e2088497d1f61132db3a56f81b8ce9/modules/exploits/windows/rdp/cve_2019_0708_bluekeep_rce.rb)文件进行分析。利用模块启动后，会先扫描目标是否存在BlueKeep漏洞([扫描原理](https://zerosum0x0.blogspot.com/2019/05/avoiding-dos-how-bluekeep-scanners-work.html))，存在漏洞则开始漏洞利用流程，先建立rdp连接并注册MS_T120(触发漏洞)和RDPSND(内核池喷射)两个虚拟信道。
wiresharkRDPDR信道会在rdp连接建立后与客户端进行握手，相关协议可见[微软文档](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpefs/bbb6321e-7d66-42da-9884-bdd15151159c)。在接收到来自RDPDR信道的CLIENTID_CONFIRM消息后，程序便认为rdp连接已建立完成，开始进行下一漏洞利用步骤。

![](https://image.3001.net/images/20190919/15688588973412.png!small)

先介绍MS_T120结构体和利用RDPSND在内核非分页池中分配数据。
MS_T120结构体由rdp组件termdd.sys分配，用于控制rdp连接中的虚拟信道MS_T120。
微软的一篇[rdp驱动开发文档](https://support.microsoft.com/nb-no/help/2867446/how-to-enable-a-third-party-driver-to-intercept-and-disable-the-sas-ke)中公开了这类结构体的定义，虽然其中大部分字段名是保留的，但再结合termdd.sys可分析出其中数据代表的意义。

![ntGya4.png](https://image.3001.net/images/20190919/15688586668087.png!small)

termdd!IcaAllocateChannel中创建了信道控制结构体并分配内存空间，可看出分配的内存位于内核非分页池，大小为0x160字节。则要在内核非分页池中分配大量相同大小的可控数据，方可在MS_T120被释放后重新占据并控制关键字段的值。这就需求利用rdp协议进行内核池喷射（Pool
Spray）（当然非rdp的池喷同样可以达到相同目的，BlueKeep利用模块主要贡献者zerosum0x0分享了一份利用SMBLoris和IP分片进行池喷的
[BlueKeep
Exp](https://github.com/zerosum0x0/CVE-2019-0708/blob/master/poc/cve_2019_0708_bluekeep.py)，但要求目标启用额外服务无疑增加了漏洞利用条件。）。这一点可以利用向特殊虚拟信道中发送数据实现(虚拟信道数据包格式文档
[见此](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/6c074267-1b32-4ceb-9496-2eb941a23e6b))。同样在termdd.sys中的IcaChannelInputInternal用于处理发往虚拟信道的数据，在接收到数据后，IcaChannelInputInternal会根据虚拟信道的状态执行不同的操作。关键代码如下：

![](https://image.3001.net/images/20190919/15688589096155.png!small)

注意第154行的判断，IrpList是虚拟信道结构体中用于存放正在排队的Irp读取请求的链表。若该链表不空，则IcaChannelInputInternal会取出一个Irp并将接收的数据复制过去，此时不会在内核非分页池中分配数据。若链表为空，则IcaChannelInputInternal会将接收到的数据缓存在内核非分页池中，此时便可进行池喷射，代码如下：

![](https://image.3001.net/images/20190919/15688589165227.png!small)

可以看到此时接收的数据被完全储存在内核非分页池中，但需要注意的是分配大小会比数据多0x38字节的不可控制区域，此部分用于储存缓存数据的长度、位置、前后缓存块等元数据。Metasploit
BlueKeep利用模块选取的RDPSND虚拟信道便满足IrpList链表为空的要求，内核调试可验证这一点。

![](https://image.3001.net/images/20190919/15688589231521.png!small)

但RDPSND信道是用于完成远程桌面音频播放相关功能的，若此功能被禁用则RDPSND会在rdp连接建立前被关闭。Win7系统是默认启用远程桌面音频播放功能的，2008系统是默认禁用的，必须通过通过远程桌面会话主机配置相关选项才可启用(也可通过[注册表](https://getadmx.com/?Category=Windows_10_2016&Policy=Microsoft.Policies.TerminalServer::TS_CLIENT_AUDIO)操作)

![](https://image.3001.net/images/20190919/15688589321351.png!small)

向RDPSND信道发送Size大小字节数据会被保存在Size+0x38大小的内核非分页池中，可以用此来占据被释放的MS_T120结构体和写入shellcode。经计算可知需要发送0x128的数据，这样便会在内核非分页池中分配0x160大小的数据，与MS_T120结构体大小相同。Metasploit
BlueKeep利用模块先发送大量大小为0x128的数据，这样便会在内核非分页池中占据大量0x160字节内存空间，再发送会触发MS_T120释放的数据包，紧接着再次发送大小为0x128的数据。由于此前已经在内核中占据了大量0x160大小的空间，刚刚被释放的MS_T120结构体原来所占据的0x160字节内存空间就极有可能被这批新发送数据中的一个所占据。

![](https://image.3001.net/images/20190919/15688589407239.png!small)

成功占据被释放的MS_T120结构体后，利用模块继续利用RDPSND向内核中大量写入shellcode。

![](https://image.3001.net/images/20190919/1568858955488.png!small)

最后BlueKeep利用模块将rdp连接断开，触发shellcode执行。

![](https://image.3001.net/images/20190919/15688589629760.png!small)

这一步并不是绝对稳定的，利用模块在控制MS_T120结构体后，将结构体内函数指针(偏移0x100处)设置为一个内核非分页池地址范围中的值（参考[Windows
x64系统内核虚拟地址空间布局](https://www.codemachine.com/article_x64kvas.html)），并期望向内核中写入的shellcode能占据这个值，如果成功占据则可顺利触发远程命令执行，若不能占据则会造成目标蓝屏崩溃。Metasploit
BlueKeep利用模块针对不同场景预设了不同地址，可在利用漏洞前通过target选项选择。

![](https://image.3001.net/images/20190919/15688589691012.png!small)

如果漏洞利用成功，则在termdd!IcaChannelInputInternal+17d处触发shellcode执行。

![](https://image.3001.net/images/20190919/15688589751507.png!small)

由于漏洞触发点在termdd.sys中，shellcode执行时IRQL为DISPATCH_LEVEL，需要进行特殊的处理。BlueKeep利用模块的[shellcode](https://github.com/rapid7/metasploit-framework/blob/d393c5203a9359b5ee4a82fe6688acc7b7e9a6b9/modules/exploits/windows/rdp/zerosum-bkshellcode64.asm)实现逻辑与
[永恒之蓝](https://github.com/worawit/MS17-010/blob/master/shellcode/eternalblue_kshellcode_x64.asm)基本一致，均是先hook
syscall再利用APC注入完成R0到R3的转移。有一点不同之处在于BlueKeep是在shellcode运行过程中用egg
hunter的方式搜寻并复制用户态payload（出于虚拟信道单次发送数据大小有限的考虑），而永恒之蓝用户态payload偏移位置是固定的。BlueKeep

![](https://image.3001.net/images/20190919/15688589828954.png!small)

EternalBlue

![](https://image.3001.net/images/20190919/15688589921387.png!small)

而且BlueKeep的shellcode为避免返回到IcaChannelInputInternal函数的麻烦，选择直接在hook
syscall之后返回到IcaChannelInputInternal的上层函数。

![](https://image.3001.net/images/20190919/15688589999135.png!small)

这部分代码与IcaChannelInputInternal结束返回部分功能是一致的。

![](https://image.3001.net/images/20190919/15688590085477.png!small)

但这也造成了一点小问题，IcaChannelInputInternal在之前获取了信道结构体中的同步锁，这里直接退出了IcaChannelInputInternal而锁并没有释放。

![](https://image.3001.net/images/20190911/1568170141_5d78609da9b6e.png!small)

 ***本文作者：cradel，转载请注明来自FreeBuf.COM**


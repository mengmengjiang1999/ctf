# 一、漏洞简介

希望通过复现这个经典的漏洞成因及利用细节，可以让你重新认识到要想利用它其实并不只是栈溢出覆盖返回地址那么简单。

ms08_067漏洞是经典SMB协议漏洞之一，该漏洞影响深远，时至今日仍有用武之地。该漏洞CVE编号为CVE-2008-4250，影响范围：Microsoft
Windows 2000 SP4，XP SP2和SP3，Server 2003 SP1和SP2，Vista Gold和SP1，Server 2008和7
Pre-Beta。

该漏洞起因在于系统在处理远程函数调用时，函数NetpwPathCanonicalize在处理格式化路径时未对路径范围进行有效校验，致使在查找并拷贝路径字符串时产生栈溢出，通过精心设计的路径可以覆盖wcscpy函数的返回地址，最终可以执行任意shellcode。

该漏洞已有很多详细分析文章了，个人认为比较详尽的分析是《0day2--》中第26章中的ms08067漏洞分析。该文章正式基于前辈分析成果基础上进一步详细刨析每个细节，结合大家最常用的MSF复现该漏洞攻击及调试工具，对该v洞的漏洞细节及shellcode触发执行进行复现分析，以及探讨尝试改写前辈的EXP实现更广泛更易用的漏洞利用工具。

# 二、漏洞成因

在netapi32.dll中，NetpwPathCanonicalize调用CanonicalizePathName,后者又调用RemoveLegacyFolder.最终因为RemoveLegacyFolder.在处理路径字符串时由于对父目录字符串”\\..\”处理时出现缓冲区漏洞：

![](https://image.3001.net/images/20210316/1615901378_6050b2c221299be948ef3.png!small)

![](https://image.3001.net/images/20210316/1615901422_6050b2ee8f9ba414589a7.png!small)

NetpwPathCanonicalize是netapi32.dll的一个导出函数，用于格式化网络路径字符串，其原型为：

Int NetpwPathCanonicalize(

Uint16 path[ ], // [in] path name

Uint8 can_path[ ], // [out] canonicalized path

Uint32 maxbuf, // [in] max size of can_path

Uint16 prefix[ ], // [in] path prefix

Uint32* pathtype, // [int out] path type

Uint32 pathflags // [in] path flags, 0 or 1

);

该函数功能为字符串处理函数，大体功能是：若prefix串非空，将prefix串与path串用‘\’相连，并复制到输出串can_path中，输出串的容量为maxbuf字节读大小：

Prefix + ‘\’ + path => can_path [max_buf]

在路径合并过程中，函数会做各种检查，如prefix或path长度是否越界、是否符合路径规范，或can_path的容量是否够大等等。返回值：若函数成功则返回0，否则返回相应的错误号。

# 三、漏洞分析

由于出现漏洞的函数NetpwPathCanonicalize是导出函数，因此我们可以编写一个本地程序直接调用该函数，如此方便漏洞复现分析。

如下图我们在0day2书中的POC中加入了getchar()函数用于暂停程序，以便我们使用调试器附加该进程进行分析：

![](https://image.3001.net/images/20210316/1615901526_6050b356eb2e7fb2450d8.png!small)

我们使用ollydbg附加该进程（当然你也可以使用windbg,我最开始是使用windbg双机联调进行分析的，可总是出现卡死（该换电脑了），索性就换ollydbg本地调试分析了），程序已经停在了getchar()函数执行位置，我们ollydbg暂停，在程序的输入窗口上随便输入几个字符后回车，Alt+F9运行到用户代码区，可以看到我们的漏洞触发代码存储的起始位置在0040815C处：

![](https://image.3001.net/images/20210317/1615942459_6051533b1181d1f6f073a.png!small)

经过一个wcscpy和两个wcscat后，exp被拷贝到了栈区0013FB84处：

![](https://image.3001.net/images/20210317/1615942841_605154b985ad80dd49b0b.png!small)

接下来调用一个wprintf()函数输出一下攻击载荷，我们看到shellcode部分并没有打印出来，这是因为wprintf是以双字节格式输出可显示字符的，而shellcode部分在此情形下为不可显示字符，故然没有打印出来：

![](https://image.3001.net/images/20210317/1615942860_605154cca432b81f0a2d9.png!small)

之后就是调用存在漏洞的函数NetpwPathCanonicalize，我们单步步入跟进去：

![](https://image.3001.net/images/20210317/1615942876_605154dc7e3f7429f33c4.png!small)

我们可以结合IDA中NetpwPathCanonicalize的伪代码快速在ollydbg中定位到漏洞函数分析入口（注：除了导出函数NetpwPathCanonicalize可以被识别外，CanonicalizePathName及RemoveLegacyFolder都是非导出函数，是我们根据分析函数功能自定义的函数名称，并在IDA或者动态调试器中将相应位置标签添加为该函数名）：

![](https://image.3001.net/images/20210317/1615942891_605154ebb093f2b60d743.png!small)

CanonicalizePathName函数内部，我们可以看到会有对传入的参数string（即路径）长度进行判断，当长度大于0x208（十进制520）时函数退出，所以我们在构造exploit时，shellcode的长度要尽量的小，路径参数整体不要超过520个字节。

![](https://image.3001.net/images/20210317/1615942905_605154f97c264fe9232c6.png!small)

接着往下走：![](https://image.3001.net/images/20210317/1615942916_60515504a368bbddddec1.png!small)

在调用问题函数RemoveLegacyFolder之前，程序还进行了斜杠转化、DOS路径识别等操作：

![](https://image.3001.net/images/20210317/1615942926_6051550eee168fbb66084.png!small)

我们定位到问题函数RemoveLegacyFolder的地址为5FDDA3CE，本漏洞就是这个函数在处理上下层级目录时，未对字符串边界进行校验造成的栈溢出。我们分析函数调用时栈空间，函数调用前，exploit代码的起始位置为0013F718，距离栈顶0013F700有0x18个字节距离：

![](https://image.3001.net/images/20210317/1615942944_60515520e19ba317009fc.png!small)

当函数调用发生时，栈顶0013F6FC变成了函数RemoveLegacyFolder执行完毕后的返回地址：

![](https://image.3001.net/images/20210317/1615942954_6051552a9475b9693eeab.png!small)

接下来我们跟进去RemoveLegacyFolder函数，具体分析下其漏洞成因。不过首先我们使用IDA更直观地查看下该函数的伪代码，伪代码很多逻辑操作需要静心分析。具体“移径”原理是：遇到\\..\\**时向前查找反斜杠'\'，然后将\\..\\**中\\**部分拷贝过来：

![](https://image.3001.net/images/20210317/1615942965_605155352a96489146ffb.png!small)

我们再在ollydbg里动态调试来分析具体“移径过程”：

![](https://image.3001.net/images/20210317/1615942975_6051553f1f6b1c232e235.png!small)

第一次“移径”操作：

![](https://image.3001.net/images/20210317/1615942985_60515549e89b388e8b6fa.png!small)

第二次“移径”前的操作，向前查找反斜杠的过程：

![](https://image.3001.net/images/20210317/1615942994_60515552384c158aaf670.png!small)

当向前查找到反斜杠时，可以看到此时eax==0013F5FA,已经距离真实路径存放位置0013F718已经很远了：

![](https://image.3001.net/images/20210317/1615943001_60515559f1459483780e5.png!small)

第二次调用wcscpy进行“移径”操作时，调用wcscpy函数的返回地址（0013F6DC处的值）将被覆盖，而该地址距离字符串复制的目的地址0013F5FA，距离为226个字节：

![](https://image.3001.net/images/20210317/1615943012_605155648a7e93e578a75.png!small)

这就是为何我们构造的EXP中要用224个字节填充的原因：

![](https://image.3001.net/images/20210317/1615943023_6051556fa95248a1e937b.png!small)

我们按F7进入wcscpy函数查看字符串拷贝及返回地址覆盖过程，我们看到wcscpy函数的返回地址（0013F6DC处的值）已被覆盖为7C82385D，程序将跳转至该地址执行该地址处的指令：

![](https://image.3001.net/images/20210317/1615943031_60515577a2ebc29301319.png!small)

该处的指令为call esp,即执行栈空间中栈顶的shellcode：

![](https://image.3001.net/images/20210317/1615943050_6051558a8bfad13530320.png!small)![](https://image.3001.net/images/20210317/1615943150_605155ee6b3bc86db42c5.png!small)

Shellcode功能是可变的，这里不再赘述，本次实验使用的POC是在0day2中的例子基础上修改的。最终成功弹框：

![](https://image.3001.net/images/20210317/1615943168_60515600467fd08d424b9.png!small)

# 四、POC与EXP分析

以上的本地调试分析漏洞成因虽然很方便，但其毕竟和该漏洞的真实利用环境，即远程代码执行有一定区别，这里我们结合MSF中ms08_067漏洞利用进行调试分析。

首先，我们在被调试主机上使用命令“wmic process where caption="svchost.exe" get
caption,handle,commandline”查找到提供SMB服务的svchost进程（netsvcs）：

![](https://image.3001.net/images/20210317/1615943180_6051560c56bdd3d992322.png!small)

当然，你也可以通过process explorer这样的进程监视工具来找到netsvcs服务进程及其PID：

![](https://image.3001.net/images/20210317/1615943191_605156171a770f775b6ff.png!small)

而后我们使用Immunity
Debugger附加该进程，而后在M窗口中查看内存中模块镜像，找到netapi32.dll,然后在反汇编窗口查看，而后CTRL+N查看该模块关联函数，找到NetpwPathCanonicalize右键在反汇编窗口查看，而后F2在该处下断。Immunity
Debugger使用F9之继续运行（中间会遇到进程中断，shift+F9跳过使持续运行），同时我又在CanonicalizePathName和RemoveLegacyFolder处分别下了断点。

![](https://image.3001.net/images/20210317/1615943222_60515636ded69d4c7ed83.png!small)

而后我们在kali中启动MSF并做相关配置后，exploit指令发起攻击：

![](https://image.3001.net/images/20210317/1615943234_605156427030423beed8c.png!small)

调试器成功停在NetpwPathCanonicalize处，我们继续F9运行，程序在CanonicalizePathName处断下：

![](https://image.3001.net/images/20210317/1615943255_605156571c079caaee92b.png!small)

可以看到当程序循环查找到下一个反斜杠时，该位置01B5F692距离exploit的起始位置01B5F494相距1FE即510个字节。

![](https://image.3001.net/images/20210317/1615943265_60515661ba1e1523c5fe5.png!small)

第一次移径操作：

![](https://image.3001.net/images/20210317/1615943275_6051566b81fa0ec05c9e4.png!small)

第二次“移径”操作前，我们看到程序向前查找反斜杠，找到反斜杠时该地址是01b5f444，该位置早已经越过了路径的起始位置01B5F494，若第二次移径操作得以执行，其下栈区调用wcscpy函数进行移径操作的返回地址将被覆盖：

![](https://image.3001.net/images/20210317/1615943289_605156795605e068c0c23.png!small)

F7进入wcscpy函数内部观察该函数返回地址被覆盖过程，其返回地址位于01B5F458：

![](https://image.3001.net/images/20210317/1615943301_6051568533f570c9b349f.png!small)

第二次“移径”操作后，exploit成功覆盖了wcscpy函数的返回地址，wcscpy函数返回时exploit将得以执行：

![](https://image.3001.net/images/20210317/1615943310_6051568e0fd26d7f69a19.png!small)

暂停一下，这里有一个问题，即01b5f444处的反斜杠从哪儿来的呢，经分析发现是在CheckDosPathType()函数中使得该位置产生了个反斜杠的，我们进去该函数分析下它具体机理。经过跟踪调试，最终锁定到了01b5f444处被修改为反斜杠的地方。该位置位于CheckDosPathType()->ntdll.RtlIsDosDeviceName_U()->ntdll.RtlIsDosDeviceName_Ustr->ntdll.RtlInitUnicodeString()中,可以看到该操作是内置的硬编码,是不是该赋值操作不受外来变量输入影响，换句话说，即在本次调试用系统上该位置一定会被赋值为反斜杠（即0x5c）？

![](https://image.3001.net/images/20210317/1615943325_6051569ded03983849807.png!small)

答案是否定的，通过动静结合分析，我们发现这个赋值操作需要条件的。首先我们回溯CheckDosPathType()的函数调用，虽然没有直接的参数传递，但我们注意call之前的语句，将Destination（“\\..\\..\”后的字符串起始地址）的地址传给了eax：

![](https://image.3001.net/images/20210317/1615943337_605156a9b80632789e341.png!small)

我们跟进CheckDosPathType()中，看到它被传到了ntdll.RtlIsDosDeviceName_U()：

![](https://image.3001.net/images/20210317/1615943346_605156b26bf1a30d127fd.png!small)

进入ntdll.RtlIsDosDeviceName_U()，我们看到参数被传给了RtlInitUnicodeStringEx()进行了一些操作，这些操作是使得vstrings成了一个类似结构体的数据结构，其中vstrings+4处存放着Destination（“\\..\\..\”后的字符串起始地址）：

![](https://image.3001.net/images/20210317/1615943355_605156bb9e012c323af7f.png!small)

![](https://image.3001.net/images/20210317/1615943367_605156c7dfcb3cc9dd689.png!small)

我们进入ntdll.RtlIsDosDeviceName_Ustr(),看到该参数继续向下传递，但要调用该函数，需要满足if中的条件判断，经分析这部分的功能是判断路径中最后一个反斜杠\后的第一个字符是否是‘L’、’C’,、’P’、’A’、’N中的任意一个，若是才可调用ntdll.RtlInitUnicodeString():

![](https://image.3001.net/images/20210317/1615943379_605156d3eb2fbe6182901.png!small)

进入ntdll.RtlInitUnicodeString()中，可以看到目标位置最终被赋值为92是因为函数判断Destination（“\\..\\..\”后的字符串起始地址）的字符串长度为92.至此我们分析清楚了要想li用该漏洞还需要，一、最后一个反斜杠\后的第一个字符是否是‘L’、’C’,、’P’、’A’、’N中的任意一个。2、我们构造的Destination的长度需要是92个字节：

![](https://image.3001.net/images/20210317/1615943392_605156e0223f7f6b95b9d.png!small)

![](https://image.3001.net/images/20210317/1615943416_605156f8a9abe928af939.png!small)

回归主线，我们看到wcscpy的函数返回地址被覆盖成了58FC17C2，即程序将跳转至此开始执行接下来的程序，我们分析下这里的函数作用，不难看出该函数的功能就是调用ZwSetInformationProcess用来关闭DEP，使得栈区的shellcode得以执行：

![](https://image.3001.net/images/20210317/1615943426_6051570223b9b6d569cd6.png!small)

哦？现在程序走到关闭DEP的程序内了，但该程序中用到了ss:[EBP+8]来配合进行参数传递（你说它不就直接传递个参数2嘛，干嘛这么麻烦呢，答曰人家正常的函数调用过程是需要用到的，而你直接从别处跳过来的，不按套路出牌，当然需要做些特殊处理啦），所以我们再回过头来看下EBP此时是个啥（如下图），不难看出程序在跳转至关闭DEP的函数时EBP指向的是栈空间中被覆盖的wcscpy的返回地址的上一个栈空间，那么就需要此处被覆盖后的SS:[EBP+8]可读可写，所以我们找到一个在所有Windows系统上都可读可写的位置0x00020408来覆盖这个位置（当然该位置也是可变幻的）：

![](https://image.3001.net/images/20210317/1615950986_6051748a31bf8636c7f69.png!small)

这里有几个关键地址，其一反斜杠位置01b5f444，其二wcscpy返回地址01B5F458，二者相距0x14即20个字节，所以在攻击载荷的两个上级目录\\..\\..\xxx后的攻击载荷部分，包含反斜杠在内向后偏移20个字节处才是有效shellcode入口，第一个指令是去关闭DEP的程序入口.并且由于“小端存储”在构造EXP时要记得关键地址字节倒置，即58FC17C2->C217FC58。其三，我们看到关闭DEP的函数返回之前有pop
ebp动作，所以shellcode中关闭DEP的函数入口之后需要4个字节的填充字符之后才是跳转指令地址，由于该函数使用的是retn
4进行函数返回，所以如果跳转指令使用call esp\jmp
esp的话，esp=esp+4+4,故此真正功能的shellcode起始位置应该位于跳转指令向后偏移8个字节的位置，即01B5F468处。而我们本次研究的MSF生成exploit中的跳转指令使用的是call
esi：

![](https://image.3001.net/images/20210317/1615943434_6051570acd2422917c3ce.png!small)

经调试分析，esi的值相对于shellcode的起始位置的偏移值是相对固定的。这是因为在shellcode执行之前，esi最后一次的使用是用来记录上层目录“\\..\xxx”中的第一个点“.”的位置(即01b5f496，当然在溢出发生后该位置会被覆盖，而不再是点“.”),而该位置则相对于01b5f444处的反斜杠位置是相对不变的，因此msf中可以使用call
esi来跳转至真正功能的shellcode。所以计算可得call
esi跳转的目的地址为“\\..\\..\xxx”中最后一个反斜杠在内向后偏移01b5f496-01b5f444+1=0x52+1,即第83个字节处，即"\xeb\x62"。

![](https://image.3001.net/images/20210317/1615943444_60515714b54ea336062b5.png!small)

而"\xeb\x62"对应的反汇编代码为jmp
0x62,即程序在此使用jmp跳转指令跳到shellcode处进而执行之。那么问题来了，为什么跳转的步长是0x62呢，从何计算而得。如下图我们根据以上分析过程梳理的栈空间溢出时的示意图，可计算得到jmp后跳转的步长==shellcode起始位置(01b5f4fa)-jmp位置(01b5f496)-2(jmp指令长度)
==0x62.

![](https://image.3001.net/images/20210317/1615943454_6051571e892413b43d9bb.png!small)

至此，该漏洞已经分析完毕。

# 五、EXP改写

分析清楚了漏洞，接下来我们就可以自己手工构造EXP了。具体说来有以下步骤：

  * 编写后门功能的shellcode，要求尽量短小，因为该漏洞利用payload有长度限制。
  * 坏字节处理，编写脚本对shellcode的中的坏字节进行加密处理。所谓坏字节，即该漏洞利用中的敏感字节，有'\x00','\x0a','\x0d','\x5c','\x5f','\x2f','\x2e','\x40'。（当然你也可以偷懒使用msfvenom搞定）
  * 通过IDA、OD等分析工具找到目标系统关闭DEP和call esi的跳转地址，其中call esi的地址较多，选一个用即可（但要在一定会被加载的文件中查找，你懂的；最好使用在不同版本系统都相同的地址，这就需要你手动搭建相应的系统并手动查找了，多动手，没毛病）。
  * 构造SMB发包，把shellcode和关键跳转按相关偏移进行组合，完成。

Exploit运行完毕，成功，看一下效果：

![](https://image.3001.net/images/20210317/1615943464_605157283cb6d99e3df12.png!small)

# 六、写在最后

Exploit变幻：

  * 通过上文分析可以看出有很多变量是可以更改的，比如shellcode长度、call esi值、EBP覆盖值等等，以此可以绕过部分流量检测。

坑点：

  * shellcode长度不能太长，超过上限则攻击不成功，具体原因看上文分析过程。
  * 构造SMB报文需要对SMB协议比较清晰，SMB报文头部的标识报文大小的字节需要根据你具体构造的shellcode长度进行相应的变化。

文中瑕疵或错误，欢迎各位大佬不吝指教，感谢。


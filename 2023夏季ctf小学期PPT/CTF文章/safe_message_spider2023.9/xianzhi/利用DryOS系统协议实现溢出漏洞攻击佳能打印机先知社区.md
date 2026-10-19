> 翻译原文链接：<https://www.synacktiv.com/en/publications/the-printer-goes-brrrrr-> again#>
>
>
> 翻译主题：本篇文章从NetBIOS协议在打印机中的应用，找到了四个函数，其中两个函数可用于系统攻击，实现漏洞利用，造成堆溢出攻击，其中DryOs系统是佳能打印机的实时操作系统，从实际情况来看，该操作不仅应用在打印机上，也应用在佳能相机中。

# 利用DryOS系统协议实现溢出漏洞攻击佳能打印机

>
> 在2022年的Pwn2Own比赛中，网络打印机再次成为焦点。与前一年在奥斯汀举行的比赛一样，今年的参赛品牌包括惠普（HP）、雷马克（Lexmark）和佳能（Canon），且型号相同。与上一次比赛不同的是，我们只专注于攻击雷马克和佳能打印机，但仍然成功地入侵了两者。遗憾的是，我们之前用于攻击佳能打印机的漏洞被另一个团队在比赛中使用。无论如何，我们将展示如何在佳能打印机上实现代码执行的方法。

如果您对如何启动这项研究感兴趣，请参考我们的另一篇文章，以及发布的工具，可以解释为什么在上一版中看到了这个目标的那么多参赛作品：共有14个。

在本届Pwn2Own比赛中，我们将目标对准了另一种在打印机上默认可用且在许多网络中著名的协议：NetBIOS。

## 0.NetBIOS协议

NetBIOS为 **网络基本输入输出系统** （英语：Network Basic Input/Output
System）的缩写，它提供了[OSI模型](https://zh.wikipedia.org/wiki/OSI模型)中的[会话层](https://zh.wikipedia.org/wiki/会话层)服务。准确来说，是一个API协议，这个API能够提供许多不同的服务，包括名称服务，数据报文分发服务和会话服务，
所以NetBIOS协议也可以运行在多种网络协议之上。如今，基于TCP/IP的NetBIOS第2级（NBT），我将重点关注允许名称注册和解析的名称服务。NetBIOS通信通常发生在必须先进行名称解析之前。

## 1.在DryOS系统中实现协议

从下面的调试信息来看，NetBIOS协议的实现通常基于Dry-OS的`netcifsnqendapp`提供的服务。

    
    
    nblogf0("netcifsnqendapp/IMP/nq/nddaemon.c", "ndStart", 404, 0x64u);
    nblogf_info("netcifsnqendapp/IMP/nq/nddaemon.c", "ndStart", 406, 0xC8u, "====> Name Daemon is starting up");
    if ( Nsinitialize() )
    {
        /* ... */
    }
    

在经过主要的研究之后，可以发现似乎协议的实现是闭源的。然而，我发现，系统中滥用与日志相关的函数会导致泄露函数名称以及实现这些函数的文件名称。这篇文章将介绍在DryOS系统中NetBIOS协议的实现。

## 2.分配上下文

在nddaemon.c文件中实现了一个初始化函数initialize，这个函数调用了三个函数来实现上下文的分配，分别是：`ndDaragramInit`，`ndNameInit`和`ndAdapterlistinit`。

`ndDatagramInit`分配了2个字符数组，每一个字符数组25字节大小，同时又把该数组作为函数`cmNetBiosParseName`的参数，这个函数被用于NetBIOS名称的解码。

`ndNameInit`调用`ndInternalNameInit`函数，系统为后面这个函数分配了一个包含20个`netbios_internal_name_entry`类型条目的表，每个条目占用100字节，用来存储内部的NetBIOS名称（比如打印机的名称）。默认情况下，会填充2个条目名称，一个是打印机的NetBIOS名称：CANONA5A2C6，另一个是打印机所属的工作组：Workgroup。

最后，`ndAdapterListInit`分配一个适配器表，用于存储最多2个适配器的上下文信息。

一旦所有上下文分配工程完成，那么会调用四次函数`CreateService`，用来创建自己的通用标识符，目的是绑定sockets和对应的端口。

Identifier | Binding address | Description  
---|---|---  
0 | 0.0.0.0:137 (UDP) | 实现NetBIOS协议名称服务  
1 | 0.0.0.0:138 (UDP) | 实现NetBIOS数据报文服务  
3 | 127.0.0.1:1022 (UDP) | 实现NetBIOS本地解析服务 (处理来自`nsGetHostByName`的请求)  
4 | 127.0.0.1:1023 (UDP) | 实现 NetBIOS本地转发服务(处理来自`nsSendToName`的请求)  
  
## 3.NetBIOS名称注册

在网络中使用`ndInternalNameResgister`服务时会进入第一个入口条目`netbios_interbal_name_entry`，根据RFC标准[RFC
1001 -15.1.1](https://datatracker.ietf.org/doc/html/rfc1001#section-15.1.1).，系统会在UDP的137端口发送NetBIOS名称注册请求，NetBIOS内部名称注册调用堆栈关系如下：

    
    
    initialize
        processConfigChange
            ndInternalNameRegisterAllNames
                ndInternalNameRegister
                    sendRegistrationRequest
                        sySendToSocket
    

## 4.数据包接收

NetBIOS协议使用`sySelectSocket`来监视函数`CreateService`创建的4个文件描述符。一旦系统的文件描述允许被读取，那么就会以1500字节的固定长度调用`syRecvFromSocket`函数，根据接收数据包的文件描述符，分别有4种不同的函数：

UDP/PORT | function  
---|---  
0.0.0.0:137 (UDP) | ndNameProcessExternalMessage  
0.0.0.0:138 (UDP) | ndDatagramProcessExternalMessage  
127.0.0.1:1022 (UDP) | ndNameProcessInternalMessage  
127.0.0.1:1023 (UDP) | ndDatagramProcessInternalMessage  
  
从攻击端来看，这里有两个函数非常有趣，分别是`ndNameProcessExternalMessage`和`ndDatagramProcessExternalMessage`函数，因为他们实现了一个不太可能被过滤的网络协议。通过查看函数的实现，可以很快的从`cmNetBiosParseName`函数中发现，从这里我可以看看NetBIOS名称服务的编码是如何在下层实现的。

## 5.NetBIOS协议名称编码

根据RFC 1001 标准，提供了两种等级的编码，第一等级的是将16字节的NetBIOs名称映射到32字节的位置，使用的编码方式时属于可逆的，half-ascii的基本编码，操作过程如下：

![](./img/964315346507694066.png)

使用上面的编码方式的话， _SYNACKTIV_ 就会被映射到 _FDFJEOEBEDELFEEJFGCACACACACACACA_ 。

第二等级的编码映射方式是将所在域的系统名称映射和编码为域名系统交互所需的“压缩”的表示形式。RFC
833标准提供了域名称的描述格式。根据RFC，域名称可以由标签序列表示，每个标签被表示为一个八位字节长度字段，后面跟着对应数量的八位字节。实际上，长度字段是一个6位的字段。如果长度字段的高位2位被设置为1，剩下的14位是一个指针，是一个指向完成信息中属于该名称的另一个域名的实际标签字符串的偏移指针，指针的值为0，那么表示根标签的值为空。

根据上面的两种等级的编码方式，那么假设NetBIOS的名称为SYNACKTIV.synacktiv.synacktiv.com会被编码的NetBIOS数据包如下：

![](./img/8297572464139030428.png)

## 6.寻找漏洞细节

目前可以知道发现在函数`cmNetBiosParseName`中存在漏洞，相关代码如下：

    
    
    uint8_t *cmNetBiosParseName(
        netbios_datagram_hdr *pkt_hdr,
        uint8_t *pkt_after_hdr,
        char *first_level_name,
        char *second_level_name,
        unsigned int len_remaining_255)
    {
        /* ... */
    
        ptr_buff = resolveLabel(pkt_hdr, &pkt_after_hdr_);
        v12 = ptr_buff + 1;
        if ( *ptr_buff == '\x20') {
            // parse first level encoding
            for ( i = 0; i < 16; ++i ) {
                v15 = 16 * *v12 - 16;
                v16 = v12[1];
                v12 += 2;
                first_level_name[i] = (v16 - 'A') | v15;
            }
            v17 = *pkt_after_hdr_;
    
            if (*pkt_after_hdr_ )
                v5 = '.';
            else
                *second_level_name = 0;
    
            // parse second level encoding
            if (v17) {
                do {
                    new_src_ptr = resolveLabel(pkt_hdr, &pkt_after_hdr_);
                    label_len = (unsigned __int8)*new_src_ptr;
                    src = new_src_ptr + 1;
                    n = label_len;
                    if (len_remaining_255 > label_len) {
                        memcpy(second_level_name, src, n); // [1]
                        new_dest = &second_level_name[n];
                        len_remaining_255 -= n;
                        *new_dest = v5;
                        second_level_name = new_dest + 1;  // [2]
                    }
                }
                while (*pkt_after_hdr_);
                *(second_level_name - 1) = 0;
            }
        }
    }
    

在第一个fisrt
label标签处是第一等级的编码，如果后续的标签不以NUL字节开头，那么该函数将继续进行第二级的解码。每个标签都在`resolveLabel`函数中被解码，这个函数会返回一个指向label长度开始时的位置。如果在目的地缓冲区仍然由足够的空间的话，那么解码标签被复制到一个255字节的缓冲区。如果标签字段的的长度为0，那么不会进行任何复制，而是在目标缓冲区处`second_level_name`增加1，情况如下如所示：

![](./img/1710376677726789007.png)

经过解码第一个级别的标签之后，解析器会遇到标签偏移，即高位的长度字段被设置为1，指向NUL字节。此时，不会复制缓冲区，并且目标缓冲区增加1，如果重复这个过程多次，会让目标缓冲区增加255字节。因此，如果后续标签label被复制到超出缓冲区的地方，就会造成基于堆的缓冲区移除。可以发现，在NetBIOS上下文初始化期间，有一个分配顺序，这个分配顺序对我来说相当重要，目标缓冲区的地址是`second_level_name`，来自结构体`netbios_internal_name_entry`，这可以帮助我们溢出漏洞，从而进行漏洞利用。

由于调度问题，在极少数的情况下会发生上下文切换，导致这两个分配在内存中的位置不是连续的。

所以调用以下堆栈可以触发漏洞。

    
    
    ndStart
        syRecvFromSocket
        ndNameProcessExternalMessage
            cmNetBiosParseName
    

## 7.实战漏洞利用

在下面的部分中，描述了堆溢出漏洞允许全部（或部分地）覆盖20个`netbios_internal_name_entry`类型结构的数组。每个结构体的大小为0x64字节，仅覆盖其中一个结构体即可获得一个2字节的`Write-What-Where`（WWW）原语。获取这个原语的方式是通过发送一个带有损坏状态的正向名称查询响应（[RFC 1002 - Section
4.2.13](https://datatracker.ietf.org/doc/html/rfc1002#autoid-28)），用来触发一个反向名称查询响应（([RFC
1002 - Section
4.2.14](https://datatracker.ietf.org/doc/html/rfc1002#autoid-29)），它将在受控地址处写入2字节的受控数据。写入的2字节将是在正向名称查询响应中指定的事务ID，以便构建反向名称查询响应的报头（([RFC
1002 - Section
4.2.2.1](https://datatracker.ietf.org/doc/html/rfc1002#section-4.2.1.1)）。

出发此Write写入原语的调用堆栈是：

    
    
    ndStart
        syRecvFromSocket
        ndNameProcessExternalMessage
            ndInternalNamePositiveQuery
                returnNegativeRegistrationResponse
    

因为在结构体`netbios_internal_name_entry`中包含了原语，所以其中这几个字段非常的重要。

![](./img/7040341330244088736.png)

  1. NetBIOS名称是一个16字节的数组，在查询中指定，并位于偏移量0x04的结构体中。该名称用于在20个条目的数组中找到匹配的`netbios_internal_name_entry`结构。
  2. 位于偏移量0x24的`netbios_adapter`结构体指针。该结构体包含位于偏移量0x38的另一个指针，用于写入负向名称查询响应的有效载荷。通常情况下，该指针用于构建NetBIOS响应有效载荷，并将前2个字节设置为事务ID（如RFC 1002第4.2.2.1节定义的NAME_TRN_ID）。在漏洞利用的上下文中，该指针定义了将写入2个受控字节的地址（“WHERE”）。使用BJNP协议将伪造的`netbios_adapter`结构体写入内存，从而允许在固定地址写入受控数据。
  3. 位于偏移量0x20的`uint16_t`字段，允许在先前写入的指针指向的地址写入2个字节（“WHAT”）。
  4. 位于偏移量0x2c的`uint16_t`字段，允许通过状态检查（必须设置为8）来达到函数`returnNegativeRegistrationResponse`。
  5. 位于偏移量0x3c的`uint16_t`字段，其值是请求中指定的预期事务请求ID。

使用这个原语两次允许覆盖一个函数指针（4字节）。目标是`pjcc_dec_ope_echo`函数指针，该函数与PJCC协议相关联，目的是将执行流程重定向到shellcode。

因此，利用漏洞的步骤如下：

  1. 使用堆溢出漏洞准备WWW（Write-What-Where），允许写入函数指针`pjcc_dec_ope_echo`的低2字节。

  2. 通过发送正向名称查询响应来触发WWW。

  3. 再次利用堆溢出漏洞，现在准备WWW，其中WHERE地址指向函数指针`pjcc_dec_ope_echo`的高2字节。

  4. 通过发送另一个正向名称查询响应来触发WWW。

  5. 发送BJNP SessionStart消息，将shellcode存储到固定地址。

  6. 发送PJCC ECHO消息。覆盖的函数指针导致执行shellcode。

该场景在以下图中进行了总结：

![](./img/7640417388796853327.png)

我们在Austin 2021的后渗透中使用了与之前文章相同的方法，因此您可以参考我们之前的文章获取详细信息。

接下来... 这是我们攻击成功的经典忍者画面，我们在Pwn2Own尝试中成功利用漏洞后显示在打印机屏幕上的画面：

![](./img/305938002275926152.png)

## 8.漏洞补丁代码

在Pwn2Own的比赛中（2022年12月9日），我们针对固件版本11.04进行攻击，该固件是当时最新可用的版本。在2023年4月14日，佳能发布了一份公告，提及与Pwn2Own中涉及相关的漏洞安全修复，并列出了10个CVE，其中包括6个影响我们设备的缓冲区溢出漏洞，如下：

  * CVE-2023-0851
  * CVE-2023-0852
  * CVE-2023-0853
  * CVE-2023-0854
  * CVE-2023-0855
  * CVE-2023-0856

因此，我们决定下载新的固件版本（12.03）来检查我们的漏洞是否已被修补，并确认我们确实与另一个团队发生了冲突。请注意，在撰写本文时，这个新的固件并不直接通过OTA更新提供。因此，我们从佳能网站下载了
[Firmware Update Tool
V12.03](https://hk.canon/en/support/0400623316?model=3102C013#)，并使用USB进行了升级。

我们直接查看了存在漏洞的函数，并检查了与存在漏洞的函数`cmNetBiosParseName`相关的修改。

![](./img/8195824922181563827.png)

可以发现，在新的补丁中，指定了标签长度（`label_len`）为0将会使得字段得剩余长度（`len_remaining_255`）减少1。因此，不可能在不减少字段剩余长度的情况下增加目标指针，修复漏洞。


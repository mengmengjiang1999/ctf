## 关于modifyCertTemplate

modifyCertTemplate是一款针对活动目录证书服务（ADCS）的安全研究工具，该工具旨在帮助广大研究人员修改ADCS证书模版，以便创造出存在安全问题的证书模版并以此来实现权限提升。实现提权后，研究人员还可以将模版重制为之前的状态。

该工具适用于针对WriteProperty权限攻击的研究场景，但也适用于其他的权限安全研究场景。

在该工具的帮助下，广大研究人员可以轻松查询模版的ACL，并使用属性GUID交叉引用相应的ACE信息，以确定可修改的属性。

## 工具下载

该工具基于Python开发，因此广大研究人员首先需要在本地设备上安装并配置好Python 3环境。

接下来，我们可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/fortalice/modifyCertTemplate.git

## 工具使用

    
    
    usage: modifyCertTemplate.py [-h] -template template name [-property property name] [-value new value] [-get-acl] [-dn distinguished name] [-raw] [-add flag name] [-debug]
    
                                 [-hashes LMHASH:NTHASH] [-no-pass] [-k] [-aesKey hex key] [-dc-ip ip address] [-ldaps]
    
                                 target
    
     
    
    Modify the attributes of an Active Directory certificate template
    
     
    
    positional arguments:
    
      target                [[domain/]username[:password]
    
     
    
    optional arguments:
    
      -h, --help             显示帮助信息和退出
    
      -template template name
    
                           目标证书模版名称
    
      -property property name
    
                            目标模版属性名称
    
      -value new value       设置目标模版属性值
    
      -get-acl               输出证书的ACE
    
      -dn distinguished name
    
                            显式设置证书模板的名称
    
      -raw                  输出元证书模版属性
    
      -add flag name        向一个属性添加标记，并维持现有选项标记
    
      -debug               开启调试输出模式
    
     
    
    authentication:
    
      -hashes LMHASH:NTHASH
    
                            NTLM哈希,格式为LMHASH:NTHASH
    
      -no-pass              不使用密码
    
      -k                   使用Kerberos认证
    
      -aesKey hex key       Kerberos认证所需的AES密钥(128或256位)
    
     
    
    connection:
    
      -dc-ip ip address     域控制器的IP地址
    
      -ldaps                使用LDAPS

## 工具使用

### 查询模版或属性值

查询一个证书模版（所有属性）：

    
    
    python3 modifyCertTemplate.py -template KerberosAuthentication ez.lab/administrator:pass

查询目标证书模版的单个属性：

    
    
    python3 modifyCertTemplate.py -template KerberosAuthentication -property msPKI-Certificate-Name-Flag ez.lab/administrator:pass

查询所有模版属性的值：

    
    
    python3 modifyCertTemplate.py -template KerberosAuthentication -raw ez.lab/administrator:pass

### 查询ACL信息

查询证书模版的ACL：

    
    
    python3 modifyCertTemplate.py -template KerberosAuthentication -get-acl ez.lab/administrator:pass

通过提供对象的名称来查询任何对象的ACL：

    
    
    python3 modifyCertTemplate.py -dn "CN=ws1,CN=computers,DC=ez,DC=lab" -get-acl ez.lab/administrator:pass

### 修改模版

向模版的“msPKI-Certificate-Name-Flag”属性添加“ENROLLEE_SUPPLIES_SUBJECT”标记：

    
    
    python3 modifyCertTemplate.py -template KerberosAuthentication -add enrollee_supplies_subject -property msPKI-Certificate-Name-Flag ez.lab/administrator:pass

更新模版属性的值（non-list属性）：

    
    
    python3 modifyCertTemplate.py -template KerberosAuthentication -property msPKI-Certificate-Name-Flag -value -150994944 ez.lab/administrator:pass

向“pKIExtendedKeyUsage”属性添加一个EKU：

    
    
    python3 modifyCertTemplate.py -template KerberosAuthentication -add "client authentication" -property pKIExtendedKeyUsage ez.lab/administrator:pass

更新一个列表格式的属性（例如：显式地设置pKIExtendedKeyUsage的值）：

    
    
    python3 modifyCertTemplate.py -template KerberosAuthentication -value "'1.3.6.1.5.5.7.3.4', '1.3.6.1.5.5.7.3.2'" -property pKIExtendedKeyUsage ez.lab/administrator:pass

## 项目地址

 **modifyCertTemplate：** 【[
_GitHub传送门_](https://github.com/fortalice/modifyCertTemplate)】

## 参考资料

> [ _https://www.fortalicesolutions.com/posts/adcs-playing-with-> esc4_](https://www.fortalicesolutions.com/posts/adcs-playing-with-esc4)
>
> [
> _https://github.com/ShutdownRepo/pywhisker_](https://github.com/ShutdownRepo/pywhisker)
>
> [ _https://github.com/zer1t0/certi_](https://github.com/zer1t0/certi)
>
> [
> _https://github.com/FuzzySecurity/StandIn﻿_](https://github.com/FuzzySecurity/StandIn)


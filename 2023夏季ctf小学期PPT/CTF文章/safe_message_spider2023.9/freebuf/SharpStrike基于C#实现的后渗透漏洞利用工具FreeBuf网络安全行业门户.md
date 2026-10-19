![](https://image.3001.net/images/20210914/1631626411_6140a4ab8d4f1ba349283.jpg!small)

## 关于SharpStrike

 **SharpStrike是一款基于C#开发的后渗透工具，该工具可以使用CIM或WMI来查询远程系统。**
除此之外，该工具还可以使用研究人员提供的凭证信息或使用当前的用户会话。

注意：SharpStrike中的某些命令将使用PowerShell结合WMI以实现其功能。

SharpStrike可以帮助广大研究人员收集关于目标远程系统的数据、执行命令以及提取数据等等。该工具允许使用WMI或CIM来跟远程系统进行连接，而CIM的使用则需要我们获取到目标系统的管理员权限。

## 解决方案架构

SharpStrike由三个主组件构成：

服务层：提供核心功能并由UI层使用（cs、ExecuteWMI.cs、ExecuteCIM.cs）；

模型：包含整个项目所有共享的数据类型；

用户接口：GUI/命令行终端；

## 工具安装

我们可以选择直接使用该项目【[
_Releases页面_](https://github.com/iomoath/SharpStrike/releases)】所提供的预构建版本，不过这个版本是在调式模式下构建的。

### 手动构建

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/iomoath/SharpStrike.git

接下来，在Visual Studio中加载项目中的SharpStrike.sln文件。

选择顶部菜单中的“构建”项，然后构建解决方案。

此时将会生成两个版本的SharpStrike，即带有GUI界面的WinForms和命令行终端应用程序，每一个版本都实现的是相同的功能。

## 工具使用

### 命令行终端版本

    
    
    SharpStrike.exe --help
    
    SharpStrike.exe --show-commands
    
    SharpStrike.exe --show-examples
    
    SharpStrike.exe -c ls_domain_admins
    
    SharpStrike.exe -c ls_domain_users_list
    
    SharpStrike.exe -c cat -f "c:\users\user\desktop\file.txt" -s [remote IP address]
    
    SharpStrike.exe -c cat -f "c:\users\user\desktop\file.txt" -s [remote IP address] -u [username] -d [domain] -p [password] -c
    
    SharpStrike.exe -c command_exec -e "quser" -s [remote IP address] -u [username] -d [domain] -p [password]

### GUI版本

    
    
    show-commands
    
    show-examples
    
    ls_domain_admins
    
    ls_domain_users_list
    
    cat -f "c:\users\user\desktop\file.txt" -s [remote IP address]
    
    cat -f "c:\users\user\desktop\file.txt" -s [remote IP address] -u [username] -d [domain] -p [password]
    
    command_exec -e "quser" [remote IP address] -u [username] -d [domain] -p [password]

## 功能介绍

### 文件操作

    
    
    cat                          -  Reads the contents of a file
    
    copy                         -  Copies a file from one location to another
    
    download**                   -  Download a file from the targeted machine
    
    ls                           -  File/Directory listing of a specific directory
    
    search                       -  Search for a file on a user
    
    upload**                     -  Upload a file to the targeted machine

### 横向活动

    
    
    command_exec**               -  Run a command line command and receive the output. Run with nops flag to disable PowerShell
    
    disable_wdigest              -  Sets the registry value for UseLogonCredential to zero
    
    enable_wdigest               -  Adds registry value UseLogonCredential
    
    disable_winrm**              -  Disables WinRM on the targeted system
    
    enable_winrm**               -  Enables WinRM on the targeted system
    
    reg_mod                      -  Modify the registry on the targeted machine
    
    reg_create                   -  Create the registry value on the targeted machine
    
    reg_delete                   -  Delete the registry on the targeted machine
    
    remote_posh**                -  Run a PowerShell script on a remote machine and receive the output
    
    sched_job                    -  Not implimented due to the Win32_ScheduledJobs accessing an outdated API
    
    service_mod                  -  Create, delete, or modify system services
    
    ls_domain_users***           - List domain users                                 
    
    ls_domain_users_list***      - List domain users sAMAccountName                  
    
    ls_domain_users_email***     - List domain users email address                   
    
    ls_domain_groups***          - List domain user groups                           
    
    ls_domain_admins***          - List domain admin users                           
    
    ls_user_groups***            - List domain user with their associated groups
    
    ls_computers***              - List computers on current domain

### 进程操作

    
    
    process_kill                 -  Kill a process via name or process id on the targeted machine
    
    process_start                -  Start a process on the targeted machine
    
    ps                           -  Process listing

### 系统操作

    
    
    active_users                 -  List domain users with active processes on the targeted system
    
    basic_info                   -  Used to enumerate basic metadata about the targeted system
    
    drive_list                   -  List local and network drives
    
    share_list                   -  List network shares
    
    ifconfig                     -  Receive IP info from NICs with active network connections
    
    installed_programs           -  Receive a list of the installed programs on the targeted machine
    
    logoff                       -  Log users off the targeted machine
    
    reboot (or restart)          -  Reboot the targeted machine
    
    power_off (or shutdown)      -  Power off the targeted machine
    
    vacant_system                -  Determine if a user is away from the system
    
    edr_query                    -  Query the local or remote system for EDR vendors

### 日志操作

    
    
    logon_events                 -  Identify users that have logged onto a system
    
     
    
    * All PowerShell can be disabled by using the --nops flag, although some commands will not execute (upload/download, enable/disable WinRM)
    
    ** Denotes PowerShell usage (either using a PowerShell Runspace or through Win32_Process::Create method)
    
    *** Denotes LDAP usage - "root\directory\ldap" namespace

## 工具使用演示

### GUI版本使用

![](https://image.3001.net/images/20210914/1631626582_6140a556f2e35ac9e3d9a.png!small)

### 命令行终端版本使用

【[
_GIF_](https://github.com/iomoath/SharpStrike/raw/master/Extras/SharpStrike-Usage.gif?raw=true)】

## 项目地址

 **SharpStrike：** 【[ _GitHub传送门_](https://github.com/iomoath/SharpStrike)】

## 参考资料

> [ _https://fortynorthsecurity.com/blog/cimplant-> part-1-detections/_](https://fortynorthsecurity.com/blog/cimplant-> part-1-detections/)
>
> [ _https://www.fireeye.com/blog/threat-> research/2017/03/wmimplant_a_wmi_ba.html_](https://www.fireeye.com/blog/threat-> research/2017/03/wmimplant_a_wmi_ba.html)
>
> [ _https://c99.sh/sharpstrike-post-exploitation-tool-cim-wmi-> inside/﻿_](https://c99.sh/sharpstrike-post-exploitation-tool-cim-wmi-> inside/)


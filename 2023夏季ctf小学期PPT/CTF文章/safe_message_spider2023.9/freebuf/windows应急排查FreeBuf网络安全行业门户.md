# windows应急响应

## 查看启动项

windows运行命令打开启动项查看

    
    
    msconfig
    

利用注册表查看启动项

    
    
    计算机\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
    

## 查看windows日志

    
    
    #打开日志管理器
    eventvwr
    

![image-20211031205620518](https://image.3001.net/images/20211102/1635817654_618098b62c43bdf51ccb6.png!small)

然后利用事件ID去排查相关的操作行为

事件ID| 说明  
---|---  
1102| 清理审计日志  
4624| 账号成功登录  
4625| 账号登录失败  
4672| 授予特殊权限  
4720| 创建用户  
4726| 删除用户  
4728| 将成员添加到启用安全的全局组中  
4729| 将成员从安全的全局组中移除  
4732| 将成员添加到启用安全的本地组中  
4733| 将成员从启用安全的本地组中移除  
4756| 将成员添加到启用安全的通用组中  
4757| 将成员从启用安全的通用组中移除  
4719| 系统审计策略修改  
4768| Kerberos身份验证（TGT请求）  
4769| Kerberos服务票证请求  
4776| NTLM身份验证  
  
 **登录类型：**

登陆类型| 说明| 测试| 是否会记录登陆IP地址  
---|---|---|---  
Logon type 2 Interactive| 本地交互登录。最常见的登录方式。| 用户关机本地登陆，登陆会触发此登陆类型日志|
记录127.0.0.1本地IP地址  
Logon type 3 Network| 网络登录 - 最常见的是访问网络共享文件夹或打印机。IIS的认证也是Type 3|
hydra对445端口(smb)爆破会触发此登陆类型系统日志 IPC$爆破会触发此类登陆类型系统日志| hydra会记录IP地址与登陆用户
IPC$不会记录登录用户  
Logon type 4 Batch 计划任务|  
|  
|  
  
Logon Type 10 RemoteInteractive| RemoteInteractive 远程登录 -- 比如Terminal
service或者RDP方式。但是Windows 2000是没有Type10的，用Type 2。WindowsXP/2003起有Type 10|
RDP爆破登陆会触发此登陆类型系统日志 mstsc远程登陆会触发此登陆类型系统日志| 会记录IP地址与登陆用户  
Logon Type 7 Unlock| 解除屏幕锁定|  
|  
  
  
## 文件排查

运行输入

    
    
    #临时文件
    %temp%
    
    #最近打开的文件
    %UserProfile%\Recent
    

## 进程分析

    
    
    #网络状态排查
    netstat -ano
    #进程排查
    tasklist /svc
    
    #PID定位
    tasklist | find "pid"
    wmic process get name,executablepath,processid | find 进程pid
    wmic process where name="powershell.exe"
    

## windows服务项排查

    
    
    #运行命令打开windows服务
    services.msc
    

主要查看服务属性。

![image-20211102093753004](https://image.3001.net/images/20211102/1635817657_618098b946040f332f85f.png!small)

## windows计划任务

    
    
    #windows  xp/7/..
    at
    
    #windows10
    schtasks
    

打开计算机管理，排查计划任务

![image-20211102091409403](https://image.3001.net/images/20211102/1635817660_618098bcb1f9b932a84ed.png!small)

## 程序替换（shift后门）

在系统登录界面，连按5次shift触发粘贴键功能，所以将其替换为cmd.exe，替换之后登录界面连按5次shift将直接唤醒cmd命令框

常见的是替换Shift程序为cmd程序，连续按五下Shift键触发  
文件路径：`C:\WINDOWS\system32\sethc.exe`

实现：将`C:\WINDOWS\system32\`底下的sethc.exe换成cmd.exe即可

## 账号排查

    
    
    #运行命令
    lusrmgr.msc
    

利用注册表查询

    
    
    #注册表地址
    HKEY_LOCAL_MACHINE\SAM\SAM\Domains\account\Users\Names
    #命令行查询
    reg query HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users\Names
    

有些时候在SAM下面没有内容，这是因为没有权限进行查看，这时需要定位到

    
    
    HKEY_LOCAL_MACHINE\SAM\SAM
    

右键权限 完全控制

![image-20211031223235729](https://image.3001.net/images/20211102/1635817661_618098bd9fc71c1f6f9b9.png!small)

然后重新进行查询


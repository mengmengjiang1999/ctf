# 应急事件检测 入门篇-windows信息检测

阅读量 **164453**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-08 10:30:36

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01642dd9f274998ebd.jpg)

**目标** ：通过数据分析确定攻击事件、查找攻击线索、梳理攻击流程、在可能的情况下，溯源到对方。

数据分析技术—系统信息分析

## 01 windows用户信息收集

**系统用户** ：

###  1.lusrmgr.msc //查找本地用户和组

![](https://p4.ssl.qhimg.com/t017452e01aa8ee40c9.png)

###  2.net user// 查找用户

![](https://p3.ssl.qhimg.com/t01d31e430458c6c2b6.png)

###  3.net localgroup administrators 查找本地管理员组用户

![](https://p3.ssl.qhimg.com/t01db1daf25e6e283e0.png)

###  4.Get-LocalUser 使用powershel 查找用户。

![](https://p2.ssl.qhimg.com/t015fb850d0dda589fc.png)

## 02windows系统进程信息收集

###  1.使用taskmgr.exe工具进行收集。

![](https://p1.ssl.qhimg.com/t019fd317e13d98c466.png)

###  2.发现进程被使用，不能被删除.

![](https://p2.ssl.qhimg.com/t01f75736edc431b887.png)

### 3.tasklist //显示所有进程

![](https://p0.ssl.qhimg.com/t01f4db174fd4ca3297.png)

###  4.可以使用tasklist | find “notepad”查找notepad的pid值。

![](https://p4.ssl.qhimg.com/t01193fb51e8c058a9f.png)

可以使用tasklist /？ 查找帮助信息

![](https://p0.ssl.qhimg.com/t01dcf0bf1116d78722.png)

###  5.get-process 获取进程信息。

![](https://p1.ssl.qhimg.com/t013b4cbf16c771c406.png)

###  6.wmic process list full //获取完整信息

![](https://p5.ssl.qhimg.com/t018e49eb6b03e761b0.png)

###  7.wmic process get name,parentprocessid,processid

获取名称、进程、id。

![](https://p2.ssl.qhimg.com/t0181b87a26d79bb3a6.png)

###  8.wmic process where ‘ProcessID=PID’ get CommandLine
//使用wmic查找指定含PID值的程序。

![](https://p0.ssl.qhimg.com/t012c000a630716516f.png)

## 03 服务信息获取

使用win+r，输入services.msc。

![](https://p1.ssl.qhimg.com/t01cc4e4150110a8a90.png)

###  1.使用net start//查看启动的服务

![](https://p2.ssl.qhimg.com/t01d15f6bc16e669b54.png)

###  2.tasklist /svc //显示每个进程中的服务

![](https://p3.ssl.qhimg.com/t0178e023a2e5741090.png)

###  3.使用psservice工具查看进程。

![](https://p1.ssl.qhimg.com/t01d9a887192a10142b.png)

upnphost服务

![](https://p2.ssl.qhimg.com/t0199f0bdb94b9086ee.png)

![](https://p2.ssl.qhimg.com/t012919e2a9448d34db.png)

## 04-计划任务信息获取

**计划任务**

进入控制面板-管理工具-任务计划程序

输入win+r，输入taskschd.msc进行启动。

![](https://p4.ssl.qhimg.com/t01c7ff6e6e6f4a5320.png)

对计划任务进行管理。

![](https://p0.ssl.qhimg.com/t01eec276e48e325dfd.png)

设置计划任务。

![](https://p0.ssl.qhimg.com/t015192092c8c867eaa.png)

使它进行启动。

![](https://p4.ssl.qhimg.com/t01ce5ca7c7798b7dce.png)

###  1.schtasks// 查看计划任务

![](https://p2.ssl.qhimg.com/t01b2c6e3da9db22cff.png)

###  2.schtasks /? 查看帮助信息。

![](https://p5.ssl.qhimg.com/t018bfd15bf38edf9d0.png)

## 05-自启动项信息收集

###  1.使用taskmgr 启动标签页

![](https://p2.ssl.qhimg.com/t0165ece36434ebeef7.png)

###  2.wmic startup get caption,command //使用wmic查看启动项

![](https://p4.ssl.qhimg.com/t01f68f65d90bb5a88e.png)

也可以使用Get-CimInstance Win32_StartupCommand | Select-Object Name, command,
Location, User | Format-List 查看启动项。

![](https://p2.ssl.qhimg.com/t01a2266e64d0a2232e.png)

![](https://p3.ssl.qhimg.com/t010a9ed0e1870fc32a.png)

## 06-注册表

###  1.输入regedit，启动注册表。

![](https://p2.ssl.qhimg.com/t0103dc5534084e6611.png)

![](https://p0.ssl.qhimg.com/t015a704a3e01e65e7b.png)

###  2.reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run 查看相关程序的进程

![](https://p3.ssl.qhimg.com/t0139b68af24b1ebafe.png)

###  3.reg query
HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run

![](https://p5.ssl.qhimg.com/t0118e1dbcfc6b63f2a.png)

## 07-端口状态

###  1.netstat -ano //查看端口状态

![](https://p5.ssl.qhimg.com/t017b845a97ad8ad922.png)

###  2.Get-NetTCPConnection -LocalAddress 192.168.93.1 | Sort-Object LocalPort
查找特定IP的状态

![](https://p3.ssl.qhimg.com/t01627d8b51a2af0182.png)

![](https://p2.ssl.qhimg.com/t0147391ac4bb4ffdf2.png)

## 08-共享文件

###  1.net view \127.0.0.1 //查看主机共享文件

![](https://p3.ssl.qhimg.com/t0191afb01d08f29540.png)

###  2.Get-SMBShare （powershell查看共享文件命令）

![](https://p3.ssl.qhimg.com/t0132b914c8392eb6b3.png)

![](https://p4.ssl.qhimg.com/t01c5f181acae35696f.png)

## 09-session信息收集

###  1.net use //查看网络连接

![](https://p4.ssl.qhimg.com/t01b2d9d994f6fb85be.png)

###  2.在不同权限进行测试

在普通权限会出现拒绝访问。

![](https://p0.ssl.qhimg.com/t012bc1989211a5b6f3.png)

在管理员权限可以正常使用。

![](https://p1.ssl.qhimg.com/t0103e4a7e45c5971f4.png)

###  3.使用PsLoggedon64.exe查找session信息。

![](https://p0.ssl.qhimg.com/t01513a062d7d44889f.png)

###  4.使用logonsessions64也可以查找session信息。

![](https://p5.ssl.qhimg.com/t01cbf98cf2d37f01dc.png)

## 总结：

本文主要从完整的windows应急事件进行构思，主要包含用户信息收集、进程信息、服务信息、计划任务信息、自启动项信息、注册表、端口状态、共享文件、session信息进行分析。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Arthur** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/261348](/post/id/261348)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [应急响应](/tag/应急响应)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) Arthur

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


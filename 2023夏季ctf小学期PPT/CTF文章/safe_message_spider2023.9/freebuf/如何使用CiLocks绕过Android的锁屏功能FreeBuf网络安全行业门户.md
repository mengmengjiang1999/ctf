![](https://image.3001.net/images/20210526/1622023155_60ae1bf352d34666db595.jpg!small)

## 关于CiLocks

CiLocks是一款功能强大的Android渗透测试工具，在该工具的帮助下，研究人员可以轻松绕过Android设备的锁屏保护。

## 功能介绍

> 爆破四位PIN码；
>
> 爆破六位PIN码；
>
> 使用字典爆破锁屏密码；
>
> 绕过锁屏保护（Antiguard），暂不支持所有操作系统版本；
>
> 设备Root（SuperSU），暂不支持所有操作系统版本；
>
> 窃取文件；
>
> 重置数据；

## 工具要求

> Adb（Android SDK）；
>
> USB线缆；
>
> Android模拟器（Nethunter/Termux），需Root；
>
> 电脑；

## 兼容性

该工具支持在Windows、Linux和macOS操作系统平台上正常使用。并且已在Kali Linux上进行过完整测试。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/tegal1337/CiLocks

## 工具使用

将项目克隆至本地之后，广大研究人员首先需要切换到项目目录下，并给CiLocks提供可执行权限，然后直接运行即可：

    
    
    cd CiLocks
    
    chmod +x cilocks
    
    bash cilocks

## 关于Android模拟器

首先，我们需要安装好Busybox，然后再对设备进行Root操作。

如果爆破攻击不成功的话，请注释掉下列代码：

    
    
    `# adb shell input keyevent 26`

## 工具运行截图

![](https://image.3001.net/images/20210526/1622023185_60ae1c112e7dd60889566.png!small)

## 操作演示

 **绕过锁屏保护：**[ _https://youtu.be/PPMhzt4lGmU﻿_](https://youtu.be/PPMhzt4lGmU)

 **爆破PIN码：**[ _https://youtu.be/D2xjJUQ9Lsw_](https://youtu.be/D2xjJUQ9Lsw)

## 项目地址

 **CiLocks：** 【[ _GitHub传送门_](https://github.com/tegal1337/CiLocks)】

## 参考资料

> [ _https://stackoverflow.com/questions/29072501/how-to-unlock-android-phone-> through-adb_](https://stackoverflow.com/questions/29072501/how-to-unlock-> android-phone-through-adb)
>
> [
> _http://www.hak5.org/episodes/hak5-1205_](http://www.hak5.org/episodes/hak5-1205)
>
> [ _https://github.com/kosborn/p2p-adb_](https://github.com/kosborn/p2p-adb)
>
> [ _https://forum.xda-developers.com/t/universal-guide-root-any-android-> device-manually.2684210/_](https://forum.xda-developers.com/t/universal-> guide-root-any-android-device-manually.2684210/)
>
> [ _https://stackoverflow.com/questions/14685721/how-can-i-do-factory-reset-> using-adb-in-android_](https://stackoverflow.com/questions/14685721/how-can-> i-do-factory-reset-using-adb-in-android)


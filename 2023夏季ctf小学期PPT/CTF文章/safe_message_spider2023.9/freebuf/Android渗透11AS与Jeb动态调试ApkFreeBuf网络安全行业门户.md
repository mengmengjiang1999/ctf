## 0x00 前言

本文分享 **Android studio** 和 **Jeb** 的 **动态调试 Apk** ，后一篇再介绍 IDA pro 动态调试 so 代码

上篇分享了4种方式来获取 CTF案例4 的 flag 值，其中动态调试方式，没有具体展开，接下来，以上篇 CTF案例4 的 apk
作为调试的对象，开始分享使用 AS 和 Jeb 动态调试 Apk，并且获得 flag 值

本文涉及技术

  * Android studio工具

  * Jeb 工具

  * 动态调试技术

  * 安卓程序修改和重新打包

> 注意：本案例所需要的 apk 文件，已经上传到知识星球，需要的朋友可以到文末关注后下载

## 0x01 准备

首先下载好案例所需的 apk 文件

使用 Android Killer 工具修改配置文件，加上 **android:debuggable="true"** 这个配置，这样 apk
就可以被调试了。![1660660913_62fbacb19447224ebc215.png!small?1660660914310](https://image.3001.net/images/20220816/1660660913_62fbacb19447224ebc215.png!small?1660660914310)

保存后，重新打包，然后安装到手机。

## 0x02 Android Studio 动态调试 Apk

> 准备：使用 Android Studio 调试，需要安装一个 smalidea 插件，本文使用的是 0.06 版本，android studio 是
> 2021 版本，手机是 pixel 2xl

![1660660923_62fbacbb3692e7b51053f.png!small?1660660923610](https://image.3001.net/images/20220816/1660660923_62fbacbb3692e7b51053f.png!small?1660660923610)

1、使用 adb 工具，以调试模式打开相应的 Activity

    
    
    adb shell am start -D  -n  com.example.hellojni/com.example.application.IsThisTheRealOne

2、查看启动的进程 id

    
    
    adb shell ps | grep hellojni

![1660660996_62fbad04490fd2d479b24.png!small?1660660996507](https://image.3001.net/images/20220816/1660660996_62fbad04490fd2d479b24.png!small?1660660996507)

3、本地调试端口转发到远程相应的进程

    
    
    adb forward tcp:8700 jdwp:24756     // 8700为本地调试端口，24756 是手机中的进程 id

![1660661013_62fbad1515e249ddb200e.png!small?1660661013395](https://image.3001.net/images/20220816/1660661013_62fbad1515e249ddb200e.png!small?1660661013395)

4、打开 Android studio

![1660661024_62fbad2002986273d738f.png!small?1660661024161](https://image.3001.net/images/20220816/1660661024_62fbad2002986273d738f.png!small?1660661024161)

选择要调试的 apk 文件，打开

5、远程调试配置，端口改为上面的配置的 8700

![1660661034_62fbad2ad566bab592ae2.png!small?1660661035055](https://image.3001.net/images/20220816/1660661034_62fbad2ad566bab592ae2.png!small?1660661035055)

6、关键处打上断点，选择要调试的进程

![1660661046_62fbad369af1c3990171f.png!small?1660661047134](https://image.3001.net/images/20220816/1660661046_62fbad369af1c3990171f.png!small?1660661047134)

7、开始调试，添加需要 watch 的变量

![1660661072_62fbad502bd1f606773cd.png!small?1660661072577](https://image.3001.net/images/20220816/1660661072_62fbad502bd1f606773cd.png!small?1660661072577)

8、 获取 flag 成功

  

## 0x03 Jeb 动态调试 Apk

 **1、使用 Jeb 打开需要调试的 Apk 文件**

可以将 smali 转为 Java 伪代码（快捷键：Tab键），然后在关键的 smali 代码处打上断点

![1660661083_62fbad5bdfef0e615e322.png!small?1660661084250](https://image.3001.net/images/20220816/1660661083_62fbad5bdfef0e615e322.png!small?1660661084250)

 **2、使用 adb 打开相应的 Activity**

    
    
    adb shell am start -D  -n  com.example.hellojni/com.example.application.IsThisTheRealOne

注意：这里 -D 是以调试模式，打开 Activity，如果不使用 -D 就是普通模式调试，在这个案例当中也可以

 **3、选择菜单中的 Debugger - > start，开始调试**

打上断点，快捷键：Ctrl + B

![1660661107_62fbad730dafc737adb3a.png!small?1660661107293](https://image.3001.net/images/20220816/1660661107_62fbad730dafc737adb3a.png!small?1660661107293)

选择对应的进程，点击 Attach ，开始调试

 **4、调试，查看变量**

注意：如果查看的变量是字符串类型的话，需要修改 Type 为 string

![1660661116_62fbad7c18165cebfb081.png!small?1660661116659](https://image.3001.net/images/20220816/1660661116_62fbad7c18165cebfb081.png!small?1660661116659)

5、获取 flag 值成功

  

## 0x04 结语

本文分享了 AS 和 Jeb 动态调试 Apk，在实战中动态调试 Apk 还是非常重要的，这一篇主要调试的 smali 的代码，如果是 native
的代码，就需要使用 IDA 进行动态调试，将会在下一篇进行分享。


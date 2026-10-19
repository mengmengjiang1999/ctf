## 0x01、写在最前面

APP和小程序的渗透、合规等测试中，可能需要抓包分析，并常常由于 **ssl spinning证书锁定机制**
导致一些包是抓不到的；为此分享一下使用Burpsuite对模拟器内APP进行抓包，并绕过一般的SSL pinning机制；

为实现整个抓包流程， 我们要组建一个如下图所示的环境：

![1626182457_60ed9339b949798e7f422.png!small?1626182459158](https://image.3001.net/images/20210713/1626182457_60ed9339b949798e7f422.png!small?1626182459158)

 **安卓模拟器：** 本次环境使用 **夜神模拟器** ，最新夜神模拟器的安卓版本为7.xx，可能不适用于某些场景，root物理手机的分享会
**看情况** 再写一篇文章。

 **ADB：** Android Debug Bridge, 其作用是连接PC和模拟器，本次直接使用 **夜神自带的ADB** 即可。

 **Frida-skeleton：** 基于frida(安卓hook工具)，主要实现了自动化绕过ssl spinning 机制。

 **burpsuite：** 抓取模拟器内APP流量。

 **注意：**

> 其中frida-skeleton基于python、burp基于java，这俩环境请小可爱们自行准备啦~
>
> Frida-skeleton在运行中会自动安装frida(server), 写在这里只为小可爱理解整个环境的架构和原理。

## 0x02、配置步骤

![1626182695_60ed942721068a298a010.png!small?1626182695663](https://image.3001.net/images/20210713/1626182695_60ed942721068a298a010.png!small?1626182695663)

### 1、夜神模拟器安装与配置

 **（1）下载安装打开：**[https://www.yeshen.com/。](https://www.yeshen.com/%E3%80%82)

![](https://image.3001.net/images/20210713/1626184243_60ed9a33b6d6720b78905.png!small)

 **（2）打开开发者模式**

 **打开设置：** 每次使用模拟器的设置都会很自然的打开右上角的设置按钮，
然后什么都找不到。。。。一定要打开下图这里的设置，比较聪明的小可爱请自动忽略这个提示；

![1626184255_60ed9a3f387c1880ea084.png!small?1626184257649](https://image.3001.net/images/20210713/1626184255_60ed9a3f387c1880ea084.png!small?1626184257649)

![1626184259_60ed9a43b906090e03203.png!small?1626184260262](https://image.3001.net/images/20210713/1626184259_60ed9a43b906090e03203.png!small?1626184260262)

打开设置后一直下拉到最后“关于平板电脑”，点击进去

![1626184274_60ed9a528a0adf8ef89b5.png!small?1626184274967](https://image.3001.net/images/20210713/1626184274_60ed9a528a0adf8ef89b5.png!small?1626184274967)

打开“关于平板电脑”后一直下拉到最后， 找到版本号：

![1626184278_60ed9a563e17935f8eb86.png!small?1626184278709](https://image.3001.net/images/20210713/1626184278_60ed9a563e17935f8eb86.png!small?1626184278709)

连续点击版本号这里大约5次，点击起来是会有提示的啦，这个没办法截图演示啦，点击够了后会有提示，听起来有点复杂，但是真的不难，小可爱勇敢尝试下。

到这里就已经开打“开发者模式了”，退出到上一层，会发现“关于平板电脑”上侧出现“开发者选项”，点进去。

找到USB调试，打开即可。

![1626184299_60ed9a6b84fe59651b7d0.png!small?1626184300002](https://image.3001.net/images/20210713/1626184299_60ed9a6b84fe59651b7d0.png!small?1626184300002)

### 2、配置ADB

由于夜神模拟器自带ADB， 免安装直接配置即可。

（1）找到夜神ADB文件nox_adb.exe:一般就在夜神安装目录，或用everything直接搜索;

（2）配置环境变量，这样命令行才能识别到adb命令哦：

> 复制nox_adb.exe到当前路径，重命名为adb.exe；
>
> 添加环境变量，win10左下角的搜索处，搜索env, 打开编辑系统环境变量，然后按如下示例配置你的环境变量；

![1626184310_60ed9a76c61df4a6ca0a4.png!small?1626184311222](https://image.3001.net/images/20210713/1626184310_60ed9a76c61df4a6ca0a4.png!small?1626184311222)

![1626184313_60ed9a7937777de7b074e.png!small?1626184313649](https://image.3001.net/images/20210713/1626184313_60ed9a7937777de7b074e.png!small?1626184313649)

![1626184317_60ed9a7d1036d7ba47d98.png!small?1626184317480](https://image.3001.net/images/20210713/1626184317_60ed9a7d1036d7ba47d98.png!small?1626184317480)

此处加入adb.exe所在路径，点击确认即可。

![1626184321_60ed9a81187ae20621355.png!small?1626184321592](https://image.3001.net/images/20210713/1626184321_60ed9a81187ae20621355.png!small?1626184321592)

 **（3）验证配置**

验证环境变量配置：新开一个cmd,新开一个cmd,新开一个cmd呀，输入adb潇洒回车，成功则如下图所示。

![1626184332_60ed9a8c65b5998dadcc9.png!small?1626184332835](https://image.3001.net/images/20210713/1626184332_60ed9a8c65b5998dadcc9.png!small?1626184332835)

验证adb与夜神连通性，在cmd里依次输入以下命令来来确认:

> `adb connect 127.0.0.1:62001﻿`
>
> : 使用adb连接上夜神，夜神的端口一般是62001，也可能是52001,小可爱要自己试一试呐，连接成功了就如下图这样子，要确认一下哦；
>
> `adb devices`
>
> ：列出当前设备，看看咱们的夜神有没有连接上；
>
> `adb shell`
>
> ：进入设备shell；
>
> `id`
>
> ：在shell内执行后查看结果，确保当前是root权限哦。

![1626184337_60ed9a911a3d7049421f1.png!small?1626184337634](https://image.3001.net/images/20210713/1626184337_60ed9a911a3d7049421f1.png!small?1626184337634)

### 3、frida-skeleton安装与配置

原文链接：https://github.com/Margular/frida-skeleton

    
    
    git clone https://github.com/Margular/frida-skeleton.git
    cd frida-skeleton
    pip install -r requirements.txt

### 4、burp安装与配置

######  **（0） 确保burp安装**

这个要是不会的话找找其他教程哦。

######  **（1）配置透明代理**

确保模拟器里的所有流量都能被burp处理。具体步骤如下图所示。

注意事项：

> burp每次关闭重启后这个配置就没有啦， 每次都需要配置哦~

>
> 端口自己指定哦，注意不要和其他常用端口冲突，截图当时使用了习惯端口2333，但是51129也是可以的！51129可以的！51129可以！只是重新截图太麻烦了就算啦~

>
> ![1626184367_60ed9aaf52da0527e6048.png!small?1626184367992](https://image.3001.net/images/20210713/1626184367_60ed9aaf52da0527e6048.png!small?1626184367992)

![1626184372_60ed9ab4119d544c8af11.png!small?1626184372604](https://image.3001.net/images/20210713/1626184372_60ed9ab4119d544c8af11.png!small?1626184372604)

## 0x03、确定目标，开始抓包！

 **1\. 下载一个app的apk包** ，一把拖入夜神，安装后打开；

 **2\. 获取APP包名** ：ADB shell中运行 `dumpsys activity activities | grep
mResumedActivity`；找到打码处的包名；

![1626184386_60ed9ac20032cdd32aff1.png!small?1626184386466](https://image.3001.net/images/20210713/1626184386_60ed9ac20032cdd32aff1.png!small?1626184386466)

 **3.** **运行frida-skeleton** , 连接ADB和burp，运行方法：

    
    
    cd frida-skeleton
    python .\frida-skeleton.py -vip 2333 包名  
      
    说明：
    -v：输出详细信息
    -i：install, 自动安装frida
    -p：指定burp的端口

注意：首次运行会安装frida，所以时间会较长哦~

 **4.** 然后在 **App里多点击** 看看，就会看到burp已经在抓包啦，frida-skeleton也有相关日志出来啦！

![1626183347_60ed96b32d5f6db762db2.png!small?1626183351208](https://image.3001.net/images/20210713/1626183347_60ed96b32d5f6db762db2.png!small?1626183351208)

![1626184488_60ed9b280b5fb53e24532.png!small?1626184488634](https://image.3001.net/images/20210713/1626184488_60ed9b280b5fb53e24532.png!small?1626184488634)

## 0x04、写在最后

 **SSL Pinning 绕过说明** ：还有些非常注重安全的APP可能会使用经修改的SSL
Pinning机制，此时可能就需要具体问题具体分析来做绕过啦！

如有错漏感谢大佬指正，不喜求轻喷 。

感谢 p1v07 同学（づ￣3￣）づ╭❤～


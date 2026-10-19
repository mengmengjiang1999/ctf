我们知道目前智能手机在人们中普及率越来越高，安卓的安全问题也越来越突出。面临越来越多的安全挑战，遇到越来越多流氓软件的骚扰，我们该如何出手，如何分析自己的安卓系统是否安全？除了把握好应用权限关，不用不明途径来源的APK外，这儿虫虫给你介绍一些安卓安全分析工具，主动出击分析你的手机应用，自己动手发现流氓应用，流氓行为。

# MITM代理&流量分析：PacketCapture

MITM（中间人）代理用于检查分析特定移动设备或特定应用程序的上下行网络流量。一般情况下需要通过网关设备，或通过PC共享热点，在PC上通过Wireshark抓包，设置操作比较费劲。关于Wireshark抓包分析有大量文档可供参考，在此不再多说。

  
![1.jpg](https://image.3001.net/images/20180711/15312731192661.jpg!small)  

在此，虫虫给你介绍一款安卓APK，PacketCapture是一个免费且易于使用的MITM代理，可在Android设备上运行，可以选择性地检查SSL流量，也可以选择性地对特定APP抓包分析。它缺乏其他同类应用胡里花哨的多余功能，使用非常简洁易于上手。它工作无需root，一般权限即可，工作原理是在设备上创建VPN链接来获取流量。

  
![2.jpg](https://image.3001.net/images/20180711/1531273133594.jpg!small)  

打开PacketCapture，需要预设一些参数，基本上每步按确认按钮就行，在第三步的页面需要设置SSL证书，如果要抓取HTTS协议，需要先安装证书。

![3.jpg](https://image.3001.net/images/20180711/15312731448259.jpg!small)  

# 广播监视器：Android Broadcasts Monitor

![4.jpg](https://image.3001.net/images/20180711/15312731937279.jpg!small)  
  

安卓开发中常见的陷阱之一是在应用程序的不同组件之间交换数据时使用全局广播。由于全局广播可被其他应用可见，可能泄漏敏感数据，所以找到全局广播可以帮我们分析应用安全。对全局广播的监控虫虫推荐使用Android
Broadcasts Monitor，这是一款开源应用，其源码托管在github上（ViliusKraujutis/
AndroidBroadcastsMonitor），该应用程序可以显示手机上启用的所有全局广播。

# 文件管理：Amaze 文件管理器

  
![5.jpg](https://image.3001.net/images/20180711/15312732074242.jpg!small)  

安卓下首先应该安装的工具应该是文件管理器。可以用它检查特定应用程序是否在SD卡上留下任何其他应用程序可以访问的敏感数据。比如，检查"/Android
/"目录。关于安卓文件管理软件大家应该有很多选择。这儿虫虫推荐的是一款开源免费的应用Amaze文件管理器，其源码托管在github上，地址为（TeamAmaze/AmazeFileManager）。

Amaze文件管理器也支持将已安装的应用程序备份到SD卡（钛备份），这样你就可以使用JADX等工具获取应用程序的APK以进行进一步分析。

# 设备上的录像机：Telecine

![6.jpg](https://image.3001.net/images/20180711/15312732166348.jpg!small)  
  

在设备上录制操作视频用于演示或显式应用复现bug非常有用。我们在此推荐的使用的一个有用工具是Jake
Wharton的Telecine，Telecine是免费开源软件，其源码托管在github上（/JakeWharton/Telecine）。

Telecine界面非常简单，只有几个设置按钮。但是这完全掩饰不了其强大的功能和效果。

![7.jpg](https://image.3001.net/images/20180711/1531273224623.jpg!small)  

打开应用程序后，点击"LAUNCH
OVERLAY"按钮，就启动屏幕录像，开始工作。工作时在屏幕的右上角弹出小图标，点击图片可以弹出应用界面。要停止录制，请再次点击右上角小图标。

Telecine录制都是高清视频，分辨率很高，你可以使用" **ffmpeg** "或其他视频编辑工具来缩小分辨率，比如：

ffmpeg -i Chongchong_example.mp4 -crf 40 -an final.mp4

# 安卓反编译神器—JADX

JADX是一个免费开源的Java反编译器，可以使用Android APK并将其反编译回Java源代码，JADX的源码托管在github上（/ ）。

![8.jpg](https://image.3001.net/images/20180711/15312732409070.jpg!small)  
  

可以用它对特定的apk包进行反编译，然后对其代码做分析，找到可疑的问题。

  
![9.jpg](https://image.3001.net/images/20180711/15312732568034.jpg!small)  

JADX也支持命令行调用，比如，我们用它进行自反编译：

cd build/jadx/

bin/jadx -d out lib/jadx-core-*.jar

bin/jadx-gui lib/jadx-core-*.jar

请记住，Android使用的JVM与普通JVM不同。所以一些机制和类库，比如加密、SSL连接等安全相关的应用和常规JVM中的行为不同，需要区别处理。


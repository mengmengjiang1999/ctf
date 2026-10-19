**前言**

因为工作关系最近需要分析一款windows上的虚拟定位外挂给出一个检测方案，有趣之处在于这款外挂它既不需要苹果设备越狱又不需要安装APP就可以欺骗iOS
APP的GPS定位功能，本篇文章仅为记录调戏它的过程。

 **初探**

![0.jpeg](https://image.3001.net/images/20181028/1540735321_5bd5c159385c2.jpeg!small)  

初始在拿到了这样一个软件前，通过一些交流了解软件使用流程大体有了些许猜测。因为曾经从事过某iOS助手的建设工作，当时因为产品需要去逆向了iTunes操作苹果设备的各个功能如何实现，我对于利用usb来操纵苹果设备相对熟悉。果不其然的在目录中发现了几个熟悉的名字“iMobileDevice-net.dll”、“libimobiledevice.dll”，也证实了我对其技术原理的猜想。

这几个库来源于老外开源的一套逆向iTunes后整合的基础库libimobiledevice，因为重点并不是如何实现一个iOS助手在这个问题上也就不展开讨论了，不过多一句嘴这套库商用还存在一些问题（最起码当年时是这样的）想商用的注意排坑。

 **直奔主题**

在我的印象中是不记得iTunes中有过类似的服务，因为轻车熟路所以也可以绕过分析的路途直奔主题了。

![1.jpeg](https://image.3001.net/images/20181028/1540735384_5bd5c198348e4.jpeg!small)  

"com.apple.dt.simulatelocation"这是个服务名并去查了一下这个服务的作用。苹果在Xcode 6、iOS
8.0开始提供了一个为设备模拟GPS位置的调试功能，其原理是通过usb获取设备句柄后开启设备内的服务("com.apple.dt.simulatelocation")再通过固定坐标或GPX文件进行位置模拟。

![2.jpeg](https://image.3001.net/images/20181028/1540735445_5bd5c1d5410fd.jpeg!small)  

 **掩耳盗铃**

在根目录下有一个drivers目录，里面有着一些内置的支持iOS版本文件夹，在其中有两个文件，文件名分别“inject.dmg”、“inject.dmg.signature”。

![3.jpeg](https://image.3001.net/images/20181028/1540735493_5bd5c20554c72.jpeg!small)![4.jpeg](https://image.3001.net/images/20181028/1540735497_5bd5c209755f3.jpeg!small)  

如果感觉很眼熟那么就没错，你可以通过“/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/DeviceSupport/”这个目录来找到更多相同的文件。

![5.jpeg](https://image.3001.net/images/20181028/1540735536_5bd5c2308cad6.jpeg!small)![6.jpeg](https://image.3001.net/images/20181028/1540735540_5bd5c234902f6.jpeg!small)  

  

 **行为特征**

很可惜的是我通过查阅开发文档以阅读底层开源代码，没有发现有公开的API可以进行服务的检测，而一些会造成变化的文件目录属于沙箱权限以外的范围。

![7.jpeg](https://image.3001.net/images/20181028/1540735580_5bd5c25ca0e14.jpeg!small)  

  

通过分析及行为测试可以发现，可以通过3点异常去检测行为异常：  

  1. 正常获取gps时LocationManager回调函数会被触发多次，模拟后仅触发一次。

  2. 正常获取不论是4g还是wifi来计算都需要响应时间，模拟后回调是立即返回。

  3. simulate location模拟的数据仅模拟longitude和latitude，不涉及altitude、course、speed。

 **检测方法**

  1. 回调调用次数

  2. 函数响应时间

  3. altitude、course、speed

  4. 其他传感器元素辅助校验，例如：Accelerometer、Gyroscope、Pedometer

 **附录**

  1. libimobiledevice 

<https://github.com/libimobiledevice/libimobiledevice>

BTW：如果看文章的同学知道什么其他的奇技淫巧欢迎关注公众号加群交流指教。

![qrcode_for_gh_f0cd4c7839e2_258.jpg](https://image.3001.net/images/20181101/1541073884_5bdaebdcc0bf7.jpg!small)扫码关注公告号  


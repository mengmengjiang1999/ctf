## 0×1 前言

近期，金山毒霸安全实验室通过“捕风”威胁感知系统的数据监控，发现一款名为“西瓜看图”的恶意软件。该软件主要通过“荒野行动电脑版”、“抖音电脑版”等虚假下载器进行传播。该虚假器运行后，实际安装的是“蜻蜓助手”安卓模拟器，并由“蜻蜓助手”推广安装“西瓜看图”木马远控软件。该软件通过云控手段，进行主页劫持、图标推广、软件推广、广告弹窗等恶意行为。由于该木马会在用户磁盘中创建“Mint”的目录，保存云控插件，所以我们特此命名为“Mint”木马。

## 0×2 传播和推广

Mint木马的传播路径：

![1.png](https://image.3001.net/images/20181210/1544406177_5c0dc4a151698.png!small)  
  

虚假下载器运行界面：

![2.png](https://image.3001.net/images/20181210/1544406185_5c0dc4a929a48.png!small)  
  

该虚假下载器无签名，无版本信息，点击“立即安装”会下载运行“蜻蜓助手”，而不是用户预想的“荒野行动网易版”。

“蜻蜓助手”安装完毕后，会默认勾选“西瓜看图”（Mint木马家族的母体），用户如稍有不慎点击“立即启动”就会被植入木马软件。

![3.png](https://image.3001.net/images/20181210/1544406194_5c0dc4b23f2ea.png!small)  

## 0×3 模块和流程

### 功能模块

Mint 云控木马主要为6个功能：信息收集，广告弹窗，软件推广，图标推广，主页劫持，更新变异。

其中，广告弹窗，软件推广，图标推广和主页劫持的具体内容，均由云端进行配置，通过下发文件的形式，在本地解析执行；

更新变异，则保证云控载体不断更新和变形，以躲避杀软查杀和更新功能。

功能模块图：

![4.png](https://image.3001.net/images/20181210/1544406235_5c0dc4db3d33e.png!small)  
  

信息收集，主页劫持，广告等相关URL信息：

![4.5.png](https://image.3001.net/images/20181210/1544406248_5c0dc4e82a832.png!small)  
  

### 执行流程

Mint木马利用傀儡进程注入、BHO机制（参考<https://en.wikipedia.org/wiki/Browser_Helper_Object>）、UPX加壳、数据加密、服务劫持等技术，使整个执行过程具有很高的隐蔽性。

执行流程：

![5.png](https://image.3001.net/images/20181210/1544406260_5c0dc4f41bbb8.png!small)  
  

## 0×4 影响和分布

通过“捕风”威胁感知系统的监控到，Mint木马家族8月中旬开始爆发；9月中旬活跃达到峰值，感染用户量达5W/天；10月之后活跃降低，近期又逐渐活跃起来。

![6.png](https://image.3001.net/images/20181210/1544406270_5c0dc4fe98c09.png!small)  
  

受感染的用户中，占比最多的是1123变种（71.23%），其次是1122变种（17.11%）

（因为变种众多，为了方便起见，我们暂且用文件名后面的版本号表示变种名称。如url包含的文件名XiGuaViewer_1123.exe，表示1123变种）

变种分布图：

![7.png](https://image.3001.net/images/20181210/1544406282_5c0dc50abfd49.png!small)  
  

## 0×5 细节分析

### 环境检测

Mint母体通过注册表、文件和进程关系，检测是否沙箱/虚拟机/调试/杀软环境，是否浏览器或下载器启动；不是的话才执行恶意代码，否则只调起安装界面。

![8.png](https://image.3001.net/images/20181210/1544406296_5c0dc5187c539.png!small)  
  

沙箱/虚拟机环境检测：

![9.png](https://image.3001.net/images/20181210/1544406308_5c0dc524ba385.png!small)  
  

调试工具和安全监控软件的检测名单：

![10.png](https://image.3001.net/images/20181210/1544406320_5c0dc530e3567.png!small)  
  

### 配置下拉

云控载体解密模块配置文件Ver.ini：

![11.png](https://image.3001.net/images/20181210/1544406334_5c0dc53e8a7fd.png!small)  
  

获取到解密后的内容：

![12.png](https://image.3001.net/images/20181210/1544406349_5c0dc54d93793.png!small)  
  

整理出模块配置文件Ver.ini各字段的含义如下：

![13.png](https://image.3001.net/images/20181210/1544406376_5c0dc5680f934.png!small)  

接着云控载体进行字段解析并更新插件模块和推广配置文件，将核心模块core.dat解密并注入到傀儡进程中执行：

![14.png](https://image.3001.net/images/20181210/1544406392_5c0dc578559e5.png!small)  
  

核心模块core.dat会解密推广配置文件settings.xml，并执行相应的推广劫持操作：

![15.png](https://image.3001.net/images/20181210/1544406408_5c0dc58827bd8.png!small)  
  

### 更新变异

云控载体从模块配置文件Ver.ini中获取最新载体的下载地址（[http://down.om](http://down.om/)*******.com/Lsvr.dat），保存为PsLangue.dat，然后解密还原成PE文件，复制到系统目录下，随机命名，并通过劫持wuauserv系统服务的方式，实现自更新和启动。

![16.png](https://image.3001.net/images/20181210/1544406422_5c0dc596e0d0b.png!small)  
  

### 主页劫持

（1）首先，Mint母体（“西瓜看图”）下载[http://plg.](http://plg./)*******.com/plg.dat，并执行；plg.dat
从资源中释放两个dll（分别是32位和64位），用regsvr32.exe注册dll文件。

![17.png](https://image.3001.net/images/20181210/1544406437_5c0dc5a53a437.png!small)  
  

![18.png](https://image.3001.net/images/20181210/1544406453_5c0dc5b58c4f7.png!small)

  

通过BHO机制劫持IE浏览器主页为http://uee.me/q8gn（跳转后最终为2345网址导航）  

![19.png](https://image.3001.net/images/20181210/1544406465_5c0dc5c1964cf.png!small)  
（2）其次，在core.dat核心功能模块中，通过修改注册表的方式篡改用户主页：

![20.png](https://image.3001.net/images/20181210/1544406478_5c0dc5ce5bee0.png!small)  

settings.xml中篡改页的配置信息：  

![21.png](https://image.3001.net/images/20181210/1544406492_5c0dc5dc4941d.png!small)  
  

### 图标推广

![22.png](https://image.3001.net/images/20181210/1544406503_5c0dc5e745e24.png!small)  
settings.xml中图标推广的配置信息：  

  

![23.png](https://image.3001.net/images/20181210/1544406515_5c0dc5f3bdd0d.png!small)

### 广告弹窗

settings.xml中广告弹窗的配置信息：

![24.png](https://image.3001.net/images/20181210/1544406529_5c0dc60101acb.png!small)  

### 软件推广

settings.xml中软件推广的部分配置信息：

![25.png](https://image.3001.net/images/20181210/1544406838_5c0dc7364f0ad.png!small)  

![26.png](https://image.3001.net/images/20181210/1544406869_5c0dc7559bfe7.png!small)  

我们发现，在配置文件中，主页篡改、图标推广、广告弹窗和软件推广，除规避“北上深广”一线城市外，还规避了昆山和马鞍山。

### 其他

由于Mint木马家族变种繁多，部分云控模块已停用，且由于篇幅和时间所限，这就不多啰嗦啦。

## 0×6 安全建议

> 不安装来源不明的可疑软件；
>
> 默认勾选框千万千万千万要小心；
>
> 安装杀毒防护软件并开启主防功能；
>
> 定时查杀和更新系统。

### 附录IOC

087E97C0A106A4184E61E743664F8764

9FFA36F6B4F2690490851E25390A07B8

0BA931AE318DC6F02D1D660D6A2202AE

7AC1413CC61E997C4FF65E7262D3D173

F9BA5281CF00E096B608C1825C1D60CC

73192ADE5AA1569BE1FD5A9C4758003A

98A9C4A108E10E758861600EB1F6F511

D4667E997D50A4DFECBF2C9E4884E435

9486BBBF6A9DE9CF2BE8C75347AE32F9

35BE3B8495074A4CBAE724572FA90ED4

31C3581C6094E043F4D2492D09997717

1DCBB119B1BA07F7718E9E31D014C817

B493D07BF7857E4851356016DAD13BCA

439EE7F2493D7B453442AC31AA3C5DCD

16181EA5452F547430E1426AE9027D04

[http://down.tw******.cn/XiGuaViewer_1121.exe](http://down.twgdms.cn/XiGuaViewer_1121.exe)

[http://down.vx******.com/XGViewer_1093.exe](https://www.virustotal.com/#/url/d9ee8faeec149e6334abf464be580085ef3da5eec31df0b8c6a039ee3a82379e/detection)

[http://down.wi******.com/XiGuaViewer_1133.exe](http://down.wiremesh-ap.com/XiGuaViewer_1121.exe)

[http://mo.******.net/mo/setup.cr173.386472.exe](http://mo.l5645.net/mo/setup.cr173.386472.exe)

[http://coll.******.com:9804/supp.aspx](http://coll.gz-mail.com:9804/supp.aspx)

[http://ver.******.com/Ver.ini](http://ver.qitianst.com/Ver.ini)

[http://cfg.******.com/config.ini](http://cfg.guanvisual.com/config.ini)

[http://down.om******.com/Lcore.dat](http://down.omeida-edu.com/Lcore.dat)

[http://down.om******.com/Hcore.dat](http://down.omeida-edu.com/Lcore.dat)

[http://down.om******.com/Lsvr.dat](http://down.omeida-edu.com/Lsvr.dat)

[http://down.om******.com/Hsvr.dat](http://down.omeida-edu.com/Lsvr.dat)

[http://down.um******.com/Discontor32.xml](http://down.umsalon.com/Discontor32.xml)

[http://down.um******.com/Discontor64.xml](http://down.umsalon.com/Discontor64.xml)

[http://plg.******.com/PopNews.dat](http://plg.xw-wd.com/PopNews.dat)

### 参考链接

> BHO：<https://en.wikipedia.org/wiki/Browser_Helper_Object>

  


# 概述

  

近期，金山毒霸安全实验室通过“捕风”威胁感知系统的监控数据，追踪发现一款名为“心跳助手”的安卓手游模拟器软件暗藏流量暗刷类病毒。比较特别的是，病毒宿主进程被同时嵌入两套流量暗刷插件，经过病毒特征同源性分析，我们确认这两套木马插件分别是”JsCtrl”和”老裁缝”两大暗刷病毒家族的最新变种，正如传说中的”双生花”，一株二艳，并蒂双花，在同一个枝蔓上相生相杀，所以我们将本次爆发传播的流量暗刷木马命名为”双生花”家族。

  

”双生花”暗刷病毒家族包含的两套插件是完全不同的实现机制，其早期变种的传播也没有太多的交叉点。从我们的监控数据看，其中的”JsCtrl”变种通过JS脚本下载刷量模块到本地内存加载执行，主要针对目标为58同城、百度糯米、百度的广告推广和SEO排名优化；另外一款“老裁缝”变种通过多层的内存模块加载释放后，利用内嵌的浏览器内核和松鼠脚本引擎squirrel来操作加载模拟点击，主要针对目标为爱奇艺、优酷、PPTV等主流视频站点，通过暗刷视频播放量从各大视频平台赚取广告内容分成。

  

两大暗刷木马家族同时藏身”心跳助手”这款正常软件实现”借尸还魂”，虽然”双生花”暗刷木马的合作传播内幕目前尚不完全清楚，但从某种角度来看，这应该算得上一次变相的软件供应链攻击，从”
Putty后门事件”、”XcodeGhost开发工具污染”到”Xshell后门”，
软件供应链攻击案例层出不穷，官方软件是否真的可信，正规软件身份的黑白界限也越来越模糊，以本次”双生花”暗刷病毒家族的传播为例，根据我们的监控数据回溯，本次传播攻击从18年4月初开始出现，早期变种只包含”JsCtrl”变种，到1.1.18版本开始加入”老裁缝”最新变种。凭借正规软件外壳，隐蔽性极强，通过内存加载和脚本机制实现全程无落地文件攻击，在国内多家安全软件的眼皮下，本次”双生花”家族的传播攻击时间跨度已接近半年。

  

另外，”流量暗刷”这种攻击行为一直都是黑产流量变现的重要渠道手段之一，虚假流量也在互联网的各个行业渠道都能看到身影，对于产品商业、业务安全的毒害影响之重已无需多言。对于产品厂商而言，这样的模拟流量暗刷攻击基本上完整模拟了用户的操作过程，从服务端进行有效鉴定识别非常困难，安全策略会被频繁绕过，从我们的监控数据看，近期针对各大广告平台、资讯平台、视频平台的流量攻击愈发泛滥，我们也非常欢迎爱奇艺、优酷、PPTV、58同城、百度糯米等受影响厂商与我们联系(关注我们的官方微信号”
yucunsafe”回复即可)，共同解决此类业务安全问题。

# 正文

# 1、主模块分析

  

病毒模块加载和执行流如下图所示：

![1.png](https://image.3001.net/images/20180824/1535108865_5b7fe701a4e2a.png!small)  

服务进程Xintiao_Service.exe（签名：Beijing Shouyou Duanxiang TechnologyCo.,
Ltd.；版本号：1.1.18.4486）以参数“daemon=1”启动将下载解密执行JS脚本，通过脚本去下载和执行刷量插件1；以参数“daemon=2”或“module1”启动将下载解密加载刷量插件2（老裁缝变种）；

![2.png](https://image.3001.net/images/20180824/1535108887_5b7fe71712243.png!small)

# 2、刷量插件1

  

## 1、Xintiao_Service.exe

以参数daemon=1启动将访问链接hxxp://mnq2.xintiao365.com/tj?timestamp=&id=下载加密的JS脚本并解密执行，在脚本中完成后续模块的下载执行；

![3.png](https://image.3001.net/images/20180824/1535108930_5b7fe742cfaf1.png!small)

脚本引擎通过MSScriptControl.ScriptControl添加对象模型checkstate，使得脚本可以执行自定义的对象方法。

![4.png](https://image.3001.net/images/20180824/1535108948_5b7fe7540a788.png!small)

checkstate的方法定义如下图所示，其中HashCls是调用CalcHash.dll的导出函数CalcHash解密并内存加载PE模块；

![5.png](https://image.3001.net/images/20180824/1535108966_5b7fe766cec7f.png!small)

## 2、JS脚本

整理后的脚本如下：主要功能是检测调试分析进程，检测不到则上报并下载执行刷量插件；

检测checkstate的全局变量xc和xy选择加载test_vmok.dll或者phantomjs.exe；其中phantomjs.exe的下载链接是hxxps://c.wecheng99.com/cfg.db，test_vmok.dll的下载链接是hxxps://c.wecheng99.com/ver_cfg.db；

![6.png](https://image.3001.net/images/20180824/1535108985_5b7fe779364f3.png!small)

下载完成后文件保存到%TEMP%\WinRAR\ac71bf8b-XXX.db（XXX是文件大小）；并调用checkstate.HashCls进入CalcHash.dll的导出函数HashCls进行解密加载。

![7.png](https://image.3001.net/images/20180824/1535109014_5b7fe79601a41.png!small)

脚本执行过程中会写如下注册表标记：

[HKCU\Software\Microsoft\kccloud]

start：当前时间

ac71bf8b-XXX.db：”123”

[HKCU\Software\Microsoft\Wisp]

cfg：加密后的URL “hxxp://k.biubiang.com:8124/apifour/getlink”

[HKLM\Software\WinRAR]

state：加密后的URL” hxxps://c.wecheng99.com/phantomjs.js”

## 3、test_vmok.dll

test_vmok.dll在dllmain中访问链接hxxp://k.biubiang.com:8124/apifour/getlink获取刷量配置，内容和格式如下：

![8.png](https://image.3001.net/images/20180824/1535109039_5b7fe7aff1f90.png!small)

  

其中script是刷量脚本链接，url_list是被刷量的网页链接；通过添加参数host_id=%d可以获取对应的配置。然后下载script脚本文件，访问url_list中的链接并在页面中插入执行script脚本进行刷量。

## 4、phantomjs.js

phantomjs.exe加载后会读取注册表[HKLM\Software\WinRAR]下的值state，解密得到链接hxxps://c.wecheng99.com/phantomjs.js；然后下载并执行主控脚本；

![9.png](https://image.3001.net/images/20180824/1535109064_5b7fe7c805198.png!small)

  

loop函数首先访问hxxp://47.105.34.235:8125/apithird/getlink获取刷量配置json数据，然后解析json并下载刷量脚本；

![10.png](https://image.3001.net/images/20180824/1535109211_5b7fe85b71441.png!small)  

getscript()下载刷量脚本并设置定时器checkkeyword，checkkeyword()解析关键词并访问刷量目标页面；

![11.png](https://image.3001.net/images/20180824/1535109235_5b7fe873aa247.png!small)

viewpage先判断TEMP目录下是否存在uag36.dat，不存在则访问链接hxxp://182.92.228.27/cache.php?f=uag下载然后设置定时器viewpage；

![12.png](https://image.3001.net/images/20180824/1535109267_5b7fe8933cedd.png!small)

如果存在uag36.dat，则解密该文件得到脚本并执行，内容如下：

![13.png](https://image.3001.net/images/20180824/1535109298_5b7fe8b29f7ea.png!small)

  

然后调用initpage()加载页面，在onLoadFinished()方法中执行刷量脚本;

![14.png](https://image.3001.net/images/20180824/1535109322_5b7fe8cabf69b.png!small)

## 5、刷量分析

test_vmok的配置链接为hxxp://k.biubiang.com:8124/apifour/getlink，主要刷58同城广告及部分视频广告；phantomjs的配置链接为hxxp://47.105.34.235:8125/apithird/getlink，主要刷58同城、百度糯米、百度的搜索排名优化。

1、通过遍历host_id获得test_vmok所有刷量配置：

![0.png](https://image.3001.net/images/20180827/1535360230_5b83bce69e2b7.png!small)

  

一共37个配置，24个不同的刷量脚本链接，url_list大部分是58同城的广告、部分视频播放页；url_list中的链接通过HTTP302或window.location.href自动重定向到target_url；也有部分单独的广告页，刷量脚本执行时获取跳转链接，跳到目标链接后进行真正的刷量；

![1.png](https://image.3001.net/images/20180827/1535360246_5b83bcf6ee2d1.png!small)

  

2、通过遍历host_id获得phantomjs所有刷量配置：

![2.png](https://image.3001.net/images/20180827/1535360265_5b83bd0956820.png!small)

  

一共67个配置，17个不同的刷量脚本链接，43个不同的url_list；url_list大部分是58同城房产的移动端页面、部分是百度糯米移动端页面；

3、以test_vmok的广告刷量脚本为例：

每个刷量脚本大同小异，前面大部分代码是相同的，如获取环境信息、禁用部分API、解析网页iframe获取链接、点击链接等；

![18.png](https://image.3001.net/images/20180824/1535109431_5b7fe937ced6a.png!small)

  

主函数主要是设置定时器__baseload，执行核心的刷量功能；

![19.png](https://image.3001.net/images/20180824/1535109450_5b7fe94a4298d.png!small)

  

__baseload()解析页面元素，分多个步骤设置定时器模拟点击广告完成刷量；每个步骤的具体行为根据目标网页上要刷的广告制定；

![20.png](https://image.3001.net/images/20180824/1535109470_5b7fe95e96516.png!small)

  

# 3、刷量插件2

## 1、Xintiao_Service.exe

以参数module1启动将下载hxxp://t.meixinpic.com/cnzz/paras.dat，RC4解密出InProc.dll模块后直接内存加载并调用导出函数Load进入后续流程；

![21.png](https://image.3001.net/images/20180824/1535109500_5b7fe97cb06fc.png!small)

## 2、InProc.dll

1、 Load函数先进行反调试检测，通过检测则继续解密和加载内置dll，否则结束：

![22.png](https://image.3001.net/images/20180824/1535109521_5b7fe991b5184.png!small)

  

A. **调试器检测** ：

存在开关文件C:\Wabjtam_yyyy_mm_dd.ya!则不进行检测，yyyy_mm_dd为日期格式；否则枚举进程检测是否存在如下调试分析进程；

![23.png](https://image.3001.net/images/20180824/1535109546_5b7fe9aa1888f.png!small)

  

B. **虚拟机检测** ：

1\. 通过MAC地址特征判断Vmware虚拟机；

![24.png](https://image.3001.net/images/20180824/1535109572_5b7fe9c4ba126.png!small)

  

2\. 通过检测进程vmtoolsd.exe或wmacthlp.exe，判断Vmware虚拟机；

![25.png](https://image.3001.net/images/20180824/1535109598_5b7fe9deb9e31.png!small)

  

C. **IP地址地理位置检测** ：

根据IP地址获取地理位置，判断是否在北京、上海、深圳、珠海四个城市；

![26.png](https://image.3001.net/images/20180824/1535109618_5b7fe9f2041fe.png!small)

  

2、
通过反调试检测后，异或0xAB解密内置InProcStub.dll；创建并挂起傀儡进程svchost.exe，注入InProcStub.dll，调用其88号导出函数ForkTask；

![27.png](https://image.3001.net/images/20180824/1535109644_5b7fea0ca2925.png!small)

  

3、 最后创建线程上报数据：

![28.png](https://image.3001.net/images/20180824/1535109668_5b7fea24beb9b.png!small)

  

首先访问dh.alyun.cn获取加密的配置链接，解密后如下：

![29.png](https://image.3001.net/images/20180824/1535109690_5b7fea3a11dda.png!small)

并将加密的配置链接保存到注册表[HKCU\Software\Microsoft\WindowsScript\Settings\Domains]-[data]下，后续使用该注册表值作为配置链接；

![30.png](https://image.3001.net/images/20180824/1535109716_5b7fea5441528.png!small)

  

再查找包含inproc的配置链接，不存在则使用默认链接pz.nidie.net/mm3/up/inproc.php；最后收集本机信息生成如下url上报：

pz.nidie.net/mm3/up/inproc.php?sid=554&d=d940d7b321915b1dc46a69d7b14bafbae611b456678223167a8e0a06ccf6133931c73fa7ca698025aa9e7f6ca60c07f8344b79f90704e7b71ab5d458eee6080709db80a53fcd8dd8f3364f465c8c27；

其中参数d是数据“packid=554∣=888&sid=88&x64=0&sysver=5.1.2600&mac=00-0C-29-C5-B5-0E&daystat=1”的RC4加密字符串（发送请求加密key=
“$GiveMe$”，接收数据解密key=” GiveMe$!”，下同）；

## 3、InProcStub.dll

1、
InProcStub的导出函数ForkTask先解密内置模块innerfunc.dll，通过shellcode加载并调用其888号导出函数QueryFunctions得到接口；

![31.png](https://image.3001.net/images/20180824/1535109741_5b7fea6d61446.png!small)

  

2、 然后调用接口的第29个函数，流程进入innerfunc.dll；

![32.png](https://image.3001.net/images/20180824/1535109765_5b7fea8562fdc.png!small)

  

## 4、innerfunc.dll

1、
创建线程，访问链接pz.nidie.net/mm2/up/?sid=554&d=d11780e578d3104d83637f；其中参数d是“x64=0&ver=0”RC4加密后的字符串；返回加密的配置信息，RC4解密后如下（key=”
GiveMe$!”）：

![33.png](https://image.3001.net/images/20180824/1535109794_5b7feaa25c276.png!small)

  

2、 解析返回的配置信息，根据系统版本下载对应的远程模块；

3、 RC4解密并加载远程模块remote_stub.dll，并调用其导出函数：

![34.png](https://image.3001.net/images/20180824/1535109815_5b7feab79ea55.png!small)

  

4、
将下载的加密模块写入注册表[HKLM\Software\Tencent\bugReport\QQ\<packid>]-[cache32]保存，下次先读取注册表数据解密加载，失败再重新下载；

![35.png](https://image.3001.net/images/20180824/1535109836_5b7feacc297c8.png!small)

## 5、remote_stub.dll

1、
导出函数RemoteModInit首先判断当前进程名是否为explorer.exe、svchost.exe、test_remote_stub.exe；是则创建线程进行后续行为，否则直接返回；

![36.png](https://image.3001.net/images/20180824/1535109857_5b7feae13e3aa.png!small)

  

2、
在线程中访问下面链接获取配置：pz.nidie.net/mm3/up/modup.php?sid=554&d=d940d7b321915b1dc46a69d7b14bafb2f85afb4133d6384a23d1014499bf1e2e64c67ae5922b9b63fddc273be20102f0680428f20704ecea38fbdb51f3880d6966dc94b839dec4fbbf680b620edd79821db7d8eb417671c27ff8aa0f6739a9ab09d0af；其中参数d是数据“packid=554∣=0&sid=0&daystat=0&x64=0&sysver=5.1.2600&mac=00-0C-29-C5-B5-0E&loc=XX省XX市”的RC4加密字符串；

返回配置数据RC4解密后如下：

![37.png](https://image.3001.net/images/20180824/1535109877_5b7feaf55efab.png!small)

  

3、
根据配置下载刷量模块stub和刷量脚本config；并且保存到注册表[HKEY_CURRENT_USER\Software\Tencent\QQ\Mods]下；下次将从注册表中读取，读取失败再重新下载；

![38.png](https://image.3001.net/images/20180824/1535109898_5b7feb0a7e8d8.png!small)

  

4、
stub和config解密后是zip压缩文件，其中stub解压后是刷量模块：autoie32.dll、autoie64.dll；config解压后是.nut格式的脚本文件；

![39.png](https://image.3001.net/images/20180824/1535109919_5b7feb1fce36e.png!small)

  

5、 然后加载autoie32.dll，并调用导出函数QueryNotifyInterfaceEx获得接口，最后调用接口执行刷量脚本；

![40.png](https://image.3001.net/images/20180824/1535109944_5b7feb38d8158.png!small)

  

## 6、刷量分析

刷量模块内置完整的浏览器内核并集成松鼠脚本引擎squirrel 3.1版，（一种类似lua的加强版脚本语言，官网[www.squirrel-lang.org](http://www.squirrel-lang.org)）；通过脚本控制实现网页广告和视频点击刷量；

![41.png](https://image.3001.net/images/20180824/1535109980_5b7feb5c7596b.png!small)

  

各脚本功能说明如下：

**脚本文件名** |  **主要功能**  
---|---  
2124dh.nut  |  2124导航刷量  
2345.nut  |  2345导航刷量  
cnzz.nut  |  cnzz统计  
infostream.nut  |  知识屋刷量  
iqiyisite.nut  |  爱奇艺视频和广告刷量  
pptv.nut  |  pptv剧集视频刷量  
pptv_site.nut  |  pptv网站自媒体视频刷量  
soulady.nut  |  搜女郎刷量  
youku.nut  |  优酷视频和广告刷量  
inproc.nut  |  无具体功能  
outproc.nut  |  任务控制脚本  
multiproc.nut  |  多任务控制脚本  
  
脚本实现了网页事件回调函数，通过设置定时器来解析网页元素，获取视频或广告的链接并进行模拟点击访问，实现刷量。

以优酷为例，脚本youku.nut实现了对应的视频刷量机制。针对刷量过程中访问的各页面都定义了单独的类来处理网页事件。

![42.png](https://image.3001.net/images/20180824/1535110004_5b7feb7491d41.png!small)

1、 首先main函数先清除cookies和缓存数据，再新建entrywindow类，调用navigate方法访问URL；

![43.png](https://image.3001.net/images/20180824/1535110045_5b7feb9d7425f.png!small)

2、 entrywindow
继承引擎内置浏览器类ieutil.browser，通过重载事件回调捕获网页事件并设置定时器模拟点击行为；当调用navigate加载网页完毕时触发onDocumentComplete或onNavigateComplete事件，设置定时器init；

![44.png](https://image.3001.net/images/20180824/1535110069_5b7febb5cf6e7.png!small)

3、 init定时器方法如下：通过解析网页元素得到视频的URL，并设置线程定时器visitVideo访问视频播放页进行刷量；

![45.png](https://image.3001.net/images/20180824/1535110094_5b7febce3ae0d.png!small)

  

4、
visitVideo定时器方法如下：新建类youkuwin，调用navigate方法访问视频URL;并重复设置visitVideo定时器访问同一个视频直到maxVisit次；

![46.png](https://image.3001.net/images/20180824/1535110119_5b7febe759fe2.png!small)

  

5、
youkuwin同样继承引擎内置浏览器类ieutil.browser；当网页加载完毕时触发onDocumentComplete或onNavigateComplete事件，设置定时器init模拟点击播放页广告；当触发onNewWindow事件时，调用adwin类navigate方法访问弹窗广告；

![47.png](https://image.3001.net/images/20180824/1535110154_5b7fec0ac1804.png!small)  

6、
定时器init又创建2个定时器scroll和toclose；scroll定时器滚动网页点击播放视频、暂停视频、点击广告完成刷量；toclose则关闭网页结束该视频链接的刷量。

![48.png](https://image.3001.net/images/20180824/1535110182_5b7fec2605723.png!small)

  

模拟点击的广告如下：

![49.png](https://image.3001.net/images/20180824/1535110238_5b7fec5e0f66b.png!small)

  

7、针对弹窗广告的adwin类和minshowwindow类的实现和上面类似，不再赘述；

其他网站的刷量机制同理，具体实现细节略有不同，也不再赘述。

![50.png](https://image.3001.net/images/20180824/1535110255_5b7fec6fc4d3c.png!small)

  

## 7、刷量链接整理

  

 **优酷**

叨剧柴可夫（视频播放数：415万，粉丝数：11.4万，视频数：97）

hxxps://i.youku.com/i/UMTY3MzMxMzUwMA==/videos

**PPTV**

咖妃说娱乐（播放量：3316.8万，粉丝量：1.33万，视频数：72）

hxxp://pgc.pptv.com/upgc/?username=k3CVbpRplmhoY5%2BSZ21jaWlplm9n#video

老烟斗鬼故事hxxp://pgc.pptv.com/upgc/?username=k3CUap1gnG9mZJySZ21ibmpooms%3D#video

叨剧柴可夫

hxxp://pgc.pptv.com/upgc/?username=mm6WbJpik2loYA%3D%3D#video

校长说

hxxp://pgc.pptv.com/upgc/?username=k2iWbZVlmGtoYQ%3D%3D#video

无间密室

hxxp://v.pptv.com/show/pibDNS7MZiaccqqBA.html?rcc_id=2018052032

开封府

hxxp://v.pptv.com/show/t9TPTJ785iaSHBW0.html?&rcc_id=2018072098

**爱奇艺**

《闺蜜说》第一季

hxxp://[www.iqiyi.com/u/1187952588/v](http://www.iqiyi.com/u/1187952588/v)

咖妃说娱乐

hxxp://[www.iqiyi.com/u/2459940611/v](http://www.iqiyi.com/u/2459940611/v)

校长说

hxxp://[www.iqiyi.com/u/1458122074/v](http://www.iqiyi.com/u/1458122074/v)

蜗牛看西游88

hxxp://[www.iqiyi.com/u/1333649153/v](http://www.iqiyi.com/u/1333649153/v)

女魔头驾到频道

hxxp://[www.iqiyi.com/u/1433074399/v](http://www.iqiyi.com/u/1433074399/v)

减脂训练营

hxxp://[www.iqiyi.com/u/1446769852/v](http://www.iqiyi.com/u/1446769852/v)

快看电影

hxxp://[www.iqiyi.com/u/2023137129/v](http://www.iqiyi.com/u/2023137129/v)

家有宝宝视频

hxxp://[www.iqiyi.com/u/2492080645/v](http://www.iqiyi.com/u/2492080645/v)

欢乐上班狗

hxxp://[www.iqiyi.com/u/1231160129/v](http://www.iqiyi.com/u/1231160129/v)

星云视点

hxxp://[www.iqiyi.com/u/1241481140/v](http://www.iqiyi.com/u/1241481140/v)

新快看好书

hxxp://[www.iqiyi.com/u/1304751490/v](http://www.iqiyi.com/u/1304751490/v)

Friday剑玉俱乐部

hxxp://[www.iqiyi.com/u/1351112050/v](http://www.iqiyi.com/u/1351112050/v)

**其他**

搜女郎

hxxp://[www.soulady.net/](http://www.soulady.net/)

QQ头像

hxxps://[www.qqtouxiang.com](http://www.qqtouxiang.com)

知识屋

hxxp://[www.zhishiwu.com](http://www.zhishiwu.com)

2345导航

hxxp://[www.2345.com/?39006](http://www.2345.com/?39006)

2124导航

hxxp://[www.2124.cn](http://www.2124.cn)

**cnzz统计：**

hxxp://t.meixinpic.com/cnzz/6.html

统计链接：hxxp://[www.cnzz.com/stat/website.php?web_id=1260947146](http://www.cnzz.com/stat/website.php?web_id=1260947146)

hxxp://t.meixinpic.com/cnzz/3.html

统计链接：hxxp://[www.cnzz.com/stat/website.php?web_id=1261868857](http://www.cnzz.com/stat/website.php?web_id=1261868857)

# 附录IOC:

136A821EDE570CAC1AAA7E0CEC411EB1

0F7F48867EF568A42DDF5AC646B0E157

8076BC98C013F93B1DCA34901DE8D19E

hxxp://mnq2.xintiao365.com/tj?times**p=&id=

hxxps://c.wecheng99.com/ver_cfg.db

hxxps://c.wecheng99.com/cfg.db

hxxps://c.wecheng99.com/phantomjs.js

hxxp://182.92.228.27/cache.php?f=uag

hxxp://k.biubiang.com:8124/apifour/getlink

hxxp://47.105.34.235:8125/apithird/getlink

hxxp://pz.nidie.net/mm/nv/a/

hxxp://pz.nidie.net/mm/up/

hxxp://pz.nidie.net/mm2/up/

hxxp://pz.nidie.net/mm/fd/

hxxp://pz.nidie.net/mm3/up/modup.php

hxxp://pz.nidie.net/mm2/up/modup.php

hxxp://pz.nidie.net/mm/se.php

hxxp://pz.nidie.net/mm/qd/instat.php

hxxp://pz.nidie.net/mm/brushflow/nv/

hxxp://dh.xhongxiu.net/mm/nv/a/

hxxp://stat.ssbutqi.com/s.php

hxxp://inapi.xxwqiq.net/index.php

hxxp://t.meixinpic.com/cnzz/paras.dat

hxxp://dl.nidie.net/mods/autoie/conf/18081001.png

hxxp://aylld.com/dl/mods/autoie/stub/18071801.png

hxxp://aylld.com/dl/rt/18070501/Rt32.gif

hxxp://aylld.com/dl/rt/18070501/Rt64.gif

  


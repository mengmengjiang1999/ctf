## **一、概述**

 **近期，腾讯反诈骗实验室自研的TRP-AI反病毒引擎捕获到一批大肆传播的Android后门木马病毒样本，此木马在用户设备上存在私自获取设备信息、后台频繁安装应用、后台发送短信等可疑行为。目前，腾讯手机管家客户端已全面查杀FakeSystem病毒家族，已深度集成腾讯TRP-AI引擎的魅族手机用户可以完美防御该家族病毒的入侵。**

经过安全专家的分析，这批病毒样本属于“Fake
System”木马家族的新变种，此木马家族的样本基本上都是以“Power”、“UI组件”、“SystemBase”、“进程管理”和“系统工具”等明显仿冒系统应用的软件名进行命名，最早的样本出现在2016年8月。“Fake
System”木马病毒潜伏周期很长，使用了多种先进的“逃逸”技术来对抗杀软，并集成了三大主要的黑产变现手段以牟取灰色收益。

### 三大技术对抗技术：

1) **静态检测技术逃逸：** 类名、方法名混淆成特殊符号，字符串隐藏未加密数组，每个类自动化生成不同的加密算法。

2) **动态沙箱检测逃逸：** 18种设备状态监控，包括模拟器文件，xposed框架，ADB、Debugger和Usb连接状态等，全面识别非用户运行环境。

3) **第三代云逃逸：**
将恶意功能剥离成payload文件并存储在云服务器,通过云端下发payload文件,在用户设备执行恶意功能代码.传统厂商很难捕获恶意代码进行检测。

### 三大黑产变现手段：

1)恶意推广应用：从云端获取应用推广任务，对不同用户推广ROM内和ROM外应用。

2)恶意扣费短信：从云端获取扣费短信任务，操控中毒设备发送扣费短信。

3)广告作弊刷量：多广告平台，多种类型广告支持刷量，模拟广告的拉取，点击，下载，安装等数据上报。

##  **二、** **木马影响面**

根据腾讯反诈骗实验室大数据引擎数据显示，近一个月时间里，“Fake
System”木马新变种的感染用户增长迅猛，在过去一个月的时间里，几个新变种的感染用户都迅速增长到20万左右，与此同时总体“Fake
System”木马的感染用户也大幅增长，影响近百万用户。

![1.png](https://image.3001.net/images/20180905/1536130632_5b8f7e48b5cac.png!small)

木马感染用户系统版本分布

![2.png](https://image.3001.net/images/20180905/1536130641_5b8f7e51bcfcc.png!small)

腾讯安全反诈骗实验室自研的TRP-AI反病毒引擎基于应用的行为进行深度学习，能有效探测应用的可疑操作，很好的应对上述木马采用的逃逸技术，目前已全面支持查杀该木马家族。

![3.png](https://image.3001.net/images/20180905/1536130715_5b8f7e9b4794b.png!small)

##  **三、** **木马应用详细分析**

“Fake System”木马的主要传播途径有：通过色情和游戏应用进行传播；通过木马老样本的进行传播；地下刷机渠道等方式。

我们以新捕获的样本“UI”组件，对“FakeSystem”木马的作恶行为进行详细分析。

###  **3.1** **样本基本信息**

应用名：UI组件

包名：dozx.wkkv.szzd.njag

证书：8c2b3fbd6fe808f0b67801ecf64f1c02

![4.png](https://image.3001.net/images/20180905/1536130740_5b8f7eb46ba40.png!small)

恶意行为流程图：

![5.png](https://image.3001.net/images/20180905/1536130752_5b8f7ec048629.png!small)

主要访问URL：

设备注册  |  <http://106.>**.**.81/ad/api/sdklog.php
<http://123.>**.**.38/main/api/sdklog.php
<http://106.>**.**.110/main/api/update.php  
---|---  
JAR包更新  |  <http://106.>**.**.83/ad/api/update.php
<http://123.>**.**.196/main/api/update.php
<http://106.>**.**.110/main/api/update.php  
任务获取  |  <http://106.>**.**.105/main/api/data.php  
运行事件上报  |  <http://106.>**.**.26/main/eventlog/adlog.php  
GDT刷量插件更新  |  <http://123.>**.**.196/gt/content/upd.php  
  
### **3.2** **样本编码特征**

恶意应用从早期的样本开始就采用了很强的代码混淆技术。

1、将核心代码的类名、方法名混淆成各种特殊符号。

![7.png](https://image.3001.net/images/20180905/1536130766_5b8f7ecebb8a4.png!small)

2、针对每个类，自动化生成不同的字符串替换加密算法，对所有的字符串信息进行加密处理，加大了病毒样本分析的难度。

![8.png](https://image.3001.net/images/20180905/1536130822_5b8f7f0685230.png!small)

###  **3.3** **恶意木马功能分析**

 **3.3.1** **木马应用主框架**

木马应用启动后，主要完成以下几个动作：

1、监控设备环境；

2、连接CC服务器，注册设备；

3、设置触发器任务，并设置重复定时任务，间隔一定时间拉起触发器任务。

![9.png](https://image.3001.net/images/20180905/1536130840_5b8f7f183231b.png!small)

 **1）** **监控设备环境**

应用Monitor.start()方法中对18种设备状态进行监控，包括对一些虚拟机文件，xposed框架，ADB、Debugger和Usb连接状态等信息进行监控，主要用于识别木马应用的运行环境，避免在蜜罐和试验环境中触发恶意行为。

![10.png](https://image.3001.net/images/20180905/1536130853_5b8f7f25378f4.png!small)

 **2** **）设备注册**

应用的MainAction.register()方法中会连接CC服务器，请求注册设备，将设备的基本信息如imei、imsi、brand、mac、系统版本、内核版本等信息，以及监控到的设备环境信息post到服务器，服务器则返回对应的注册结果。

![11.png](https://image.3001.net/images/20180905/1536130868_5b8f7f345e2b6.png!small)

![12.png](https://image.3001.net/images/20180905/1536130878_5b8f7f3e54593.png!small)

post请求参数：

![13.png](https://image.3001.net/images/20180905/1536130896_5b8f7f50ebc87.png!small)

注册请求返回结果，可以看到返回的结果主要有注册设备的ID、注册时间，kickoff、api版本、uidpush时间等，这些参数会用到后续的与服务器链接的其他请求中。

![14.png](https://image.3001.net/images/20180905/1536130909_5b8f7f5d6eb6d.png!small)

从返回数据中可以看到，测试设备获取的uid为32357573，每台设备注册后会被分配一个唯一的uid，排除一些无效的设备注册请求情况，可以推断出此后门木马曾感染的设备也达到了很大的量级。

 **3** **）触发器任务**

应用会设置触发器，通过设置定时任务来拉起。触发器任务会去动态加载执行Jar包，若应用运行达到一定时间，则会链接服务器，请求更新jar包。

![15.png](https://image.3001.net/images/20180905/1536130922_5b8f7f6aea224.png!small)

更新请求post的参数与注册请求类似，多了uid、reg、uidpush等参数。若服务器校验成功，则下发更新后的Jar包。

![16.png](https://image.3001.net/images/20180905/1536130938_5b8f7f7a48bdb.png!small)

![17.png](https://image.3001.net/images/20180905/1536130944_5b8f7f80dcd44.png!small)

解析更新请求返回内容，校验并存储Jar包到应用files目录。

![18.png](https://image.3001.net/images/20180905/1536130967_5b8f7f973def2.png!small)

JarLoader动态加载执行Jar包，Jar包的入口类为com.a.l.g.a，入口函数为b。

![19.png](https://image.3001.net/images/20180905/1536130979_5b8f7fa3f0be0.png!small)

![21.png](https://image.3001.net/images/20180905/1536130986_5b8f7faa20f55.png!small)

 **3.3.2 Jar** **包Analys.jar**

analys.jar的主要功能有：

1、Root用户设备；

2、链接CC服务器，获取任务列表，包括应用推广任务和短信扣费任务；

3、上报运行信息；

4、动态加载其他恶意子包。

 **a** **）Root** **用户设备**

jar包运行后会检测自己是否已经被安装在设备rom内，若没有安装在设备rom内，则会去尝试root用户设备。

![22.png](https://image.3001.net/images/20180905/1536131003_5b8f7fbbbb369.png!small)

根据设备信息，选择不同的exp进行root：

![23.png](https://image.3001.net/images/20180905/1536131015_5b8f7fc7d37da.png!small)

主要使用到的相关exp列表：

![24.png](https://image.3001.net/images/20180905/1536131027_5b8f7fd3ce893.png!small)

 **b** **）获取任务**

应用连接服务器，请求任务：

![25.png](https://image.3001.net/images/20180905/1536131038_5b8f7fdedc44a.png!small)

任务请求url：

![26.png](https://image.3001.net/images/20180905/1536131049_5b8f7fe941e02.png!small)

解析返回数据，获取任务信息，任务信息主要包括设置下线时间、是否自毁、替换系统debuggerd、Rom内APK下载安装任务和普通APK下载安装任务。  

![27.png](https://image.3001.net/images/20180905/1536131063_5b8f7ff769c48.png!small)

InstallTask任务包括APK的下载链接、包名、launch入口、是否安装到Rom内等信息。

![28.png](https://image.3001.net/images/20180905/1536131079_5b8f8007ce0cf.png!small)

普通APK的下载成功后使用pminstall命令安装，而ROM内APK下载成功后，使用cat命令将应用拷贝到设备的系统目录。  

普通应用安装：

![29.png](https://image.3001.net/images/20180905/1536131094_5b8f8016d6e36.png!small)

ROM内应用安装：

![30.png](https://image.3001.net/images/20180905/1536131110_5b8f80264cc12.png!small)

应用拉起：

![31.png](https://image.3001.net/images/20180905/1536131125_5b8f8035743f4.png!small)

根据腾讯大数据关联分析，“Fake System”木马恶意推广的应用数量庞大，其中ROM应用主要是木马的其他病毒样本，通常“Fake
System”木马会在感染用户设备上安装多个不同的病毒样本，确保对感染设备的控制；而木马在普通类APK的推广上范围十分广泛，涉及多种类型的应用。木马私自下载安装的应用主要有：

![32.png](https://image.3001.net/images/20180905/1536131139_5b8f80434d410.png!small)

同时，应用也会获取扣费短信任务，并根据设备的情况选择不同的短信发送方式来发送扣费短信。

![33.png](https://image.3001.net/images/20180905/1536131150_5b8f804ed6de8.png!small)

 **短信发送方式**

1、普通发送：

![34.png](https://image.3001.net/images/20180905/1536131161_5b8f80594fd4e.png!small)

2、反射发送：

![35.png](https://image.3001.net/images/20180905/1536131173_5b8f806519ef4.png!small)

3、注入发送：

![36.png](https://image.3001.net/images/20180905/1536131183_5b8f806faadd4.png!small)

通过注入so的方式对系统的短信管理器com.android.mms进行注入，绕过安全限定进行发送短信。

![37.png](https://image.3001.net/images/20180905/1536131196_5b8f807c2adf0.png!small)

 **c** **）上报运行信息**

运行一段时间后，应用会将相关的运行信息上报给服务器。

RootEvent信息列表，主要事件有Root相关、短信扣费相关、应用推广相关事件的执行情况。

![38.png](https://image.3001.net/images/20180905/1536131209_5b8f808939e59.png!small)

获取事件list并使用post请求上报：

![39.png](https://image.3001.net/images/20180905/1536131219_5b8f8093041ba.png!small)

上报Url：

![40.png](https://image.3001.net/images/20180905/1536131230_5b8f809e5311d.png!small)

 **d** **）动态加载广告刷量插件**

应用会动态加载和更新广告刷量插件，针对多家广告平台进行广告刷量作弊行为。

![41.png](https://image.3001.net/images/20180905/1536131242_5b8f80aa98e58.png!small)

动态加载调用广告刷量插件，插件的入口类为e.g.g.e.Bridge，入口函数为dispatch。

![42.png](https://image.3001.net/images/20180905/1536131253_5b8f80b5c695d.png!small)

![43.png](https://image.3001.net/images/20180905/1536131260_5b8f80bc319f6.png!small)

 **3.3.3** **广告刷量插件**

广告刷量插件修改多家广告平台的SDK，伪造广告请求，进行恶意的广告刷量行为。

a）破解协议，伪造广告请求

针对广告平台A，修改广告SDK，伪造请求进行插屏广告和banner广告刷量。

插屏广告：

![44.png](https://image.3001.net/images/20180905/1536131278_5b8f80ce14fe5.png!small)

![45.png](https://image.3001.net/images/20180905/1536131284_5b8f80d411ee9.png!small)

Banner广告：

![46.png](https://image.3001.net/images/20180905/1536131294_5b8f80de99e1b.png!small)

![47.png](https://image.3001.net/images/20180905/1536131300_5b8f80e4ee49c.png!small)

b）后台广告自动点击

针对广告平台B刷量：

![48.png](https://image.3001.net/images/20180905/1536131314_5b8f80f2315d9.png!small)

![49.png](https://image.3001.net/images/20180905/1536131322_5b8f80fac7ce9.png!small)

针对广告平台C刷量：

![50.png](https://image.3001.net/images/20180905/1536131339_5b8f810b33de7.png!small)

##  **四、** **总结和防护建议**

“Fake
System”木马应用仿冒系统应用的软件名，且没有图标、恶意行为对普通用户来说感知较弱，具有很强的隐蔽性。此木马功能强大，用户设备一旦感染，即会成为黑产分子控制的“肉鸡”，沦为黑产分子进行应用推广、短信扣费、广告刷量的工具。

针对普通用户如何避免受此木马的侵害，我们对给出了如下防护建议：

1、不要安装非可信渠道的应用、不要随意点击不明URL链接和扫描安全性未知的二维码信息；

2、及时对设备进行安全更新；

3、安装腾讯手机管家等安全软件，实时进行保护；

4、若发现手机感染木马病毒，请及时使用安全软件进行清理，避免重复交叉感染。

另一方面，如今黑产分子利用手中控制的“肉鸡”进行恶意广告刷量等活动日益猖獗，对各大广告平台和广告主带来了很大的负面影响和经济损失。腾讯反诈骗实验室一直致力于打击黑产，对抗诈骗/欺诈，并在黑产对抗、恶意代码识别、黑产团伙打击方面有很深厚的技术、数据积累。针对恶意应用的广告刷量行为，腾讯反诈骗实验室结合自身终端感知能力、覆盖能力以及对黑产设备、从业者信息积累等优势，向广告平台、广告主提供【移动互联网流量反欺诈解决方案】。广告平台、广告主可通过腾讯广告反欺诈服务对当前营销、推广整体状况进行有效评估，可准确、有效评估各渠道流量质量，
对欺诈流量进行精准打击，防止不必要的推广成本付出。

 ***本文作者腾讯手机管家，转载请注明来自FreeBuf.COM**


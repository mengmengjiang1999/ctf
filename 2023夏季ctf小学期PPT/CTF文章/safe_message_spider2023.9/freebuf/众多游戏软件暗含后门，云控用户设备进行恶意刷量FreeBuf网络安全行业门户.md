##  **一、概要**

**近日，腾讯安全分析师在应用商店过审的样本中发现，影视类、天气预报、游戏类等软件中存在后门，黑产开发者通过后门云控下发恶意子包到用户设备，进行视频、广告刷量等恶意行为。一旦被感染用户就是黑产的一只“肉鸡”，沦为黑产的工具。**

**技术对抗手段：**

> 1.方法名混淆成特殊符号，字符串隐藏，加密数组
>
> 2.恶意子包云端加载可控，恶意代码并采用动态拼接技术

##  **二、影响面分析**

通过样本和下发的恶意子包进行关联分析，然后数据统计，影响用户量已有两百万有余，涉及上千款应用，以下是部分恶意样本信息。

软件名  |  包名  |  周用户  
---|---|---  
奥特曼传奇英雄  |  com.joym.***.nearme.gamecenter  |  100+万  
奥特曼之格斗超人  |  com.joym.com****.nearme.gamecenter  |  40+万  
熊出没之熊大快跑2018  |  com.joym.xiongda****.gamecenter  |  20+万  
奥特曼正义降临  |  com.huale.justi****nearme.gamecenter  |  20+万  
酷跑奥特曼2  |  com.huale.ul****.nearme.gamecenter  |  15+万  
熊出没机甲熊大2  |  com.joym.arm****.nearme.gamecenter  |  12+万  
斑马影视  |  com.sq****der  |  10+万  
机甲奥特曼  |  com.joym.arm****nearme.gamecenter  |  10+万  
熊大熊二向前冲  |  com.joym.bear****nearme.gamecenter  |  9+万  
熊出没森林勇士  |  com.joym.arm****.nearme.gamecenter  |  6+万  
菠萝影视  |  com.re****novels  |  6+万  
铠甲勇士战神联盟  |  com.joym.a****nearme.gamecenter  |  3+万  
星火电视  |  io.bin****b.demo  |  2+万  
铠甲勇士格斗无双  |  com.chan****nearme.gamecenter  |  2+万  
夜色福利场  |  com.mnsy****gbd  |  2+万  
喜羊羊之王者特攻队  |  com.huale. ****nearme.gamecenter  |  2+万  
天气预报  |  com.y****ther  |  1+万  
变形超人  |  com.qrg****r.vivo  |  8000+  
美女束缚  |  com.m****rgbvj  |  7000+  
铠甲骑士  |  com.tjg****s.vivo  |  7000+  
大象影视  |  cn.sil****xiang  |  6000+  
武侠魂  |  com.tjg****vivo  |  6000+  
番茄影视  |  com. ****.reader  |  5000+  
  
##  **三、恶意行为详细分析**

以奥特曼传奇英雄为例，对恶意应用的行为进行详细分析。

1、样本基本信息：

软件基本信息  |  
---|---  
软件名  |  奥特曼传奇英雄  
包名  |  com.joy******.nearme.gamecenter  
证书  |  1F42CE6E****956D8FA  
软件图标  |
![](https://image.3001.net/images/20191107/1573134204_5dc41f7c516b9.png!small)  
  
2、作恶流程简介：

![](https://image.3001.net/images/20191107/1573134217_5dc41f89ab5a5.png!small)

3、详细行为分析

a)、样本apk中的集成的恶意代码包：

![](https://image.3001.net/images/20191107/1573134238_5dc41f9e7c738.png!small)

恶意应用在运行后，首先会连接服务器，下载并加载子包tmpbl.jar。

获取子包下载地址

![](https://image.3001.net/images/20191107/1573134255_5dc41faf0c324.png!small)

开始下载tmpbl子包

![](https://image.3001.net/images/20191107/1573134382_5dc4202ee31b5.png!small)

加载并调用子包

![](https://image.3001.net/images/20191107/1573134409_5dc42049c8fc8.png!small)

b)、子包tmpbl.jar的功能就是从云端再次下载其他的子包，主要包括：webengine.jar、dec_cf.jar、dec_c.jar等

子包tmpbl.jar通过类com.vmd.out.b.b下载webengine.jar，其功能是模拟用户刷网页视频播放量、精品推荐游戏等。

![](https://image.3001.net/images/20191107/1573134468_5dc420845faae.png!small)

子包webengine.jar获取视频、广告刷量任务

![](https://image.3001.net/images/20191107/1573134487_5dc42097127c5.png!small)

获取刷量任务后，通过模拟用户操作进行自动刷量

获取坐标：

![](https://image.3001.net/images/20191107/1573134502_5dc420a6844ea.png!small)

模拟点击广告

![](https://image.3001.net/images/20191107/1573134511_5dc420afaeaf6.png!small)

刷视频播放和点击游戏广告

![](https://image.3001.net/images/20191107/1573134520_5dc420b86fa41.png!small)

监控到刷视频播放量的地址：

[http://www.](http://www./)******.com/w_19rybu9fxh.html

![](https://image.3001.net/images/20191107/1573134701_5dc4216da28eb.png!small)

tmpbl.jar通过类doco.arge.c.a.a下载两个新子包dec_cf.jar、dec_c.jar

![](https://image.3001.net/images/20191107/1573134816_5dc421e09f345.png!small)

dec_cf.jar的功能是提供js代码

![](https://image.3001.net/images/20191107/1573134829_5dc421ede79fd.png!small)

广告地址里的js代码有，获取广告信息、获取坐标信息、指定元素的模拟点击等方法

![](https://image.3001.net/images/20191107/1573134870_5dc422167240d.png!small)

子包dec_c.jar的功能是利用webview和js代码完成视频刷量和完成模拟点击广告。

![](https://image.3001.net/images/20191107/1573134965_5dc42275f40c4.png!small)

设置Webview与js代码的交互属性

![](https://image.3001.net/images/20191107/1573135344_5dc423f081653.png!small)

执行js代码

![](https://image.3001.net/images/20191107/1573134992_5dc422907b3a6.png!small)

模拟用户点击的方法：

![](https://image.3001.net/images/20191107/1573134999_5dc422976e184.png!small)

##  **四、相关URL整理**

**URL** |  **备注**  
---|---  
[http://zgx.pow](http://zgx.pow/)****cdn.com/dnfile/cmm/******.jar  |
下载子包tmpbl.jar地址，  
功能是下载其他子包  
[http://218.98.](http://218.0.0.98/)***8888/zip/*******.jar  |
下载子包webengine.jar地址，  
功能是获取任务、刷量  
[http://a.ib](http://a.ib/)****w.com/update_ch/fruit/*******.jar  |
下载子包dec_cf.jar地址，  
功能是提供js代码  
[http://a.ib](http://a.ib/)***w.com/update_ch/fruit/****.jar  |
下载子包dec_c.jar地址，  
功能是利用webview和js代码刷量  
[http://cdn.i.](http://cdn.i./)*******.com/e/i.js  |  子包dec_c提供的js代码地址  
[http://sj.](http://sj./)********.com:9000/api/getAd******.do  
[http://nb.](http://nb./)********.com:9000/api/getAd******Device.do[http://test](http://test/)********.matchvs.com/api/get*******Device.do
|  获取刷量任务地址  
  
##  **五、溯源分析**

根据我们发现的相关URL的地址，查询到两项备案信息，其中tmpbl子包的下载地址：[http://zgx.pow](http://zgx.pow/)***dn.com/，在网上查询到此域名备案信息属于深圳市速***科技有限公司

![](https://image.3001.net/images/20191107/1573135063_5dc422d7cb763.png!small)

子包dec_cf中的地址[http://cdn.i](http://cdn.i/)***.com/，我们在网上查询到此域名备案信息属于北京宇***科技有限公司

![](https://image.3001.net/images/20191107/1573135101_5dc422fdce06d.png!small)

##  **六、应对措施和防护建议**

从作恶手法来看，黑产开发者会把恶意代码放在云端来动态加载，恶意行为以前会选择私自发送扣费短信，现在可能会优先考虑用户不容易发现的行为，如利用webview刷视频播放量、模拟用户点击广告等，针对开发者和用户我们给出如下建议：

> 1、应用开发者在接入具备动态加载子包功能的第三方SDK时需谨慎，防止恶意SDK动态加载恶意行为影响自身的口碑；
>
> 2、不安装不可信渠道应用
>
> 3、及时对设备进行安全更新
>
> 4、安装腾讯手机管家等安全软件进行防护
>
> 5、若发现病毒木马，请马上使用安全软件清理，避免感染其他病毒木马

另外黑产分子利用手中控制的“肉鸡”进行恶意广告刷量等活动日益猖獗，对各大广告平台和广告主带来了很大的负面影响和经济损失。腾讯反诈骗实验室一直致力于打击黑产，对抗诈骗/欺诈，并在黑产对抗、恶意代码识别、黑产团伙打击方面有很深厚的技术、数据积累。针对恶意应用的广告刷量行为，腾讯反诈骗实验室结合自身终端感知能力、覆盖能力以及对黑产设备、从业者信息积累等优势，向广告平台、广告主提供【移动互联网流量反欺诈解决方案】。广告平台、广告主可通过腾讯广告反欺诈服务对当前营销、推广整体状况进行有效评估，可准确、有效评估各渠道流量质量，对欺诈流量进行精准打击，防止不必要的推广成本付出。

 ***本文作者： 腾讯手机管家，转载请注明来自FreeBuf.COM**  


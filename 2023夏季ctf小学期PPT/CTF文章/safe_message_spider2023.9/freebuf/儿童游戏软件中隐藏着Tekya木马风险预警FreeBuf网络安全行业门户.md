**广告软件通常通过弹出式窗口、横幅广告、内文链接等广告方式来呈献广告内容，主要是为了提高相关网站、产品知名度。这能为软件开发商带来一定的广告收入。而广告木马软件则通常通过单击链接和其他交互式元素来模拟网页上的用户操作，实现无声地模拟与广告网站的交互如点击广告提高网站访问率或自动订阅付费服务，从而增加广告带来的收入。**

继2020年2月，[ _Clicker木马新家族-Haken木马_](https://www.freebuf.com/articles/terminal/230524.html)通过在Google
Play分发8种不同的恶意应用来感染用户设备。最近暗影安全实验室在Google
Play上发现了一个新木马家族—Tekya木马。该木马是一款模拟用户点击来自Google
AdMob，Facebook等机构的广告进行移动广告欺诈的木马软件。它通过混淆原生代码来躲避Google的检测机制使其能成功的通过Google
Play平台分发。并利用Android中的“MotionEvent”机制模仿用户的点击行为。

## 一、样本信息

> MD5：2D3B6BDBBDF0AD12E935B97D565B891A
>
> 包名：com.pantanal.stickman.warrior
>
> 应用名：Stickman Fighter
>
> 图标：

![](https://image.3001.net/images/20200408/1586336044_5e8d912c0742a.png!small)

## 二、技术分析

该程序在安装时会在receiver注册多条广播，比如开机自运行，读取网络状态，手机屏幕关闭后台仍然运行，这样使该广播很容易被触发。

![](https://image.3001.net/images/20200408/1586336095_5e8d915f50076.png!small)

图2-1 注册Receiver广播

接收到开机以及运行广播后，利用反射机制来调用apk文件中的libego.so文件。

![](https://image.3001.net/images/20200408/1586336308_5e8d923454324.png!small)

![](https://image.3001.net/images/20200408/1586336117_5e8d9175afc34.png!small)

图2-2 加载libego库文件反射调用本地方法

之后在ego库中创建validators对象列表，可以看到该对象列表中存在了许多混淆的对象。

![](https://image.3001.net/images/20200408/1586336361_5e8d926908c4c.png!small)

图2-3 创建validators对象列表

在这些validators对象中，每个调用的方法会从本地的libego.so中运行对应的函数，函数会调用C函数，运行到Y函数，最后调用xxcrl函数 。

![](https://image.3001.net/images/20200408/1586336403_5e8d9293a76d0.png!small)

![](https://image.3001.net/images/20200408/1586336171_5e8d91abd0ea8.png!small)

图2-4 xxcrl函数调用

我们可以在本地的libego.so中找到对应的函数，该函数大多经过了混淆。

![](https://image.3001.net/images/20200408/1586336449_5e8d92c113a1b.png!small)

图2-5 libego.so对应的函数

我们在文件中的java_uk_nema_Ego_xxcrl函数中可以看到该函数负责多个动作，其中fflwejp方法负责分析配置文件，
getWindow和getDecorView负责获取所需要的handle。

![](https://image.3001.net/images/20200408/1586336467_5e8d92d358250.png!small)

![](https://image.3001.net/images/20200408/1586336480_5e8d92e0d9ccd.png!small)

图2-6 xxcrl函数中的方法作用

接下来在子函数sub_AAF0处理对应的touch事件来进行模拟点击。

![](https://image.3001.net/images/20200408/1586336531_5e8d93133e948.png!small)

![](https://image.3001.net/images/20200408/1586336503_5e8d92f7424a3.png!small)

图2-7 进行模拟点击事件

## 三、服务器后台

接下来我们对Tekya木马家族进行真机模拟抓包测试，通过实际运行我们可以看到此类软件在后台运行多种广告并进行对应的服务器访问。

![](https://image.3001.net/images/20200408/1586336568_5e8d9338ba2f8.png!small)

![](https://image.3001.net/images/20200408/1586336569_5e8d933908bab.png!small)

![](https://image.3001.net/images/20200408/1586336569_5e8d9339094cd.png!small)

![](https://image.3001.net/images/20200408/1586336578_5e8d9342a219d.png!small)

图2-8 多次访问广告

## 四、情报扩展

我们在Google Play上共获取到29个该木马家族应用，下载量超过100万次，其中大部分软件是针对儿童的游戏软件，模拟点击的广告也多为游戏类广告。

部分样本信息：

 **应用名称**|  **文件MD5**|  **包名**  
---|---|---  
Yeah Translator| 0061578f313713f6fbaea7e6491d3450| com.yeyey.translate  
Race in Space| 04f153aef026c05fc0b111e2aa43992f| caracal.raceinspace.astronaut  
PDF Reader| 09c766e5c112bc51e0e1e1299146c781| mcmc.ebook.reader  
AR - Measure Plan| 103e399e10e5dc3e49c5277dfb7b9b5f| com.arsketch.quickplan  
Delicious Recipes| 22428383acdd560aeadeb9cc80b55e7c| mcmc.delicious.recipes  
Best Translate| 2899a311737312112f9156c3d3395e2a| best.translate.tool  
iTranslator| 2acfdc4098031bfd35ed2f2736ed6129| pro.infi.translator  
24h Translate| a897bb59a0721b907cfa89f521ee0830| allday.a24h.translate  
Smart Assistant| 739381cca8586fbfaff598af8e868b6c| com.smart.tools.pro  
Anime Fashion| ba1db1f26166262b4a6a00615489a0a1| com.ichinyan.fashion  
  
## 五、安全建议

> 如果用户已经感染此类木马病毒，建议用户及时卸载此类应用。
>
> 及时更新系统并下载安全软件，养成良好习惯。
>
> 关注暗影实验室的微信公众号，我们会及时发布木马病毒的最新动态。

 ***本文作者：暗影安全实验室，转载请注明来自FreeBuf.COM2**


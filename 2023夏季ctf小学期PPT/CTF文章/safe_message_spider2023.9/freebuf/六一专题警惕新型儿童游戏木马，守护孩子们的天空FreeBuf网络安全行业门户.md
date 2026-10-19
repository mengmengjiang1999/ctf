## 一、概要

 **近期，腾讯安全反诈骗实验室自研的TRP-AI反病毒引擎捕获到儿童游戏-宝宝**、儿童游戏-宝宝**、儿童游戏-公主**
等“儿童游戏”系列应用在用户设备上有流量异常行为，且存在频繁动态加载dex文件、执行命令、私自提权等可疑操作。安全研究人员通过深入跟踪和分析，发现这类应用表面上是儿童益智类的小游戏，在国内大部分应用市场都有上架，运行后应用界面也没有广告，看起来很“良心”，但实际上，这些应用可以通过云端控制下发恶意插件，在背地里做着用户无法感知的恶意行为：加载恶意广告插件，通过将广告展示界面设置为不可见，进行广告盗刷行为，疯狂消耗用户流量；动态加载恶意ROOT子包，获取手机ROOT权限，替换系统文件，将恶意的ELF文件植入用户手机。**

安全人员将这一系列木马应用称为“BlackBaby”木马家族，且“BlackBaby”木马植入的恶意ELF文件模块可以脱离母体独立运行，长期潜伏用户手机，且开机自启动，在后台静默推送恶意色情、扣费软件，对用户造成严重滋扰。

腾讯安全专家分析发现“BlackBaby”系列木马为了绕过查杀、提升了与杀软对抗的能力，使用了很多病毒逃逸技术，主要包括：

使用代码分离技术将代码拆分为多个dex子包，分阶段自云端下载并动态加载，用以绕过了杀软的安装包检测，且便于其他应用集成；

使用了强混淆技术，自定义的字符串变形加密等手段，对抗静态代码检测；

云端控制下发逻辑，躲避杀软的蜜罐检测；

“BlackBaby”系列木马涉及一百多款儿童游戏应用，累计影响用户数达百万，其中影响用户较大的应用有：

**软件名** **** |  **包名** **** |  **周用户量** ****  
---|---|---  
儿童游戏-涂*** |  com.men.******rawl |  20万+  
儿童游戏-宝宝***钉 |  com.lhyy.chil****urnly |  12万+  
儿童游戏-打*** |  com.yuyoo******le3.sub1 |  7万+  
宝宝***-儿童游戏 |  com.lhyy.chi*****ro |  7万+  
宝宝学习-涂色*** |  com.ba*****lor |  6万+  
儿童游戏-宝宝*** |  com.lhyy.children*** |  4万+  
儿童游戏-宝宝*** |  com.lhyy.childrenc*** |  3.5万+  
宝宝游戏-儿童超市 |  com.lhyy.children*** |  3.5万+  
儿童游戏-宝宝***钉 |  com.lhyy.children****ly |  3.5万+  
儿童游戏-宝宝***屋 |  com.lhyy.ltm.baby**** |  3万+  
儿童游戏-宝宝***钉 |  com.lhyy.children****** |  3万+  
儿童游戏-宝宝*** |  com.doding.children****** |  3万+  
宝宝游戏-儿童*** |  com.lhyy.children****** |  2.5万+  
儿童游戏-宝宝***巴士 |  com.baby.baby*** |  2.5万+  
恐龙宝宝***益智 |  com.lhyy.wl.protwobaby****** |  2.5万+  
宝宝***派对 |  com.lhyy.ltm.baby****** |  2.5万+  
宝宝游戏-儿童*** |  com.lhyy.children****** |  2.5万+  
儿童游戏-方块*** |  com.lhyy.******ks |  2.5万+  
儿童游戏-宝宝*** |  com.lhyy.children****** |  2.5万+  
儿童游戏-***花园 |  com.yuyoogame.ameng******u1Sub1.sub1 |  2.5万+  
****拼图儿童拼图 |  com.lhyy.***** |  2万+  
儿童游戏-宝宝*** |  com.baby.**** |  2万+  
宝宝***酷游戏 |  com.lhyy.wl***** |  2万+  
儿童游戏-***音乐 |  com.doding.children**** |  1.5万+  
儿童游戏-宝宝**** |  com.lhyy.children**** |  1.5万+  
****游戏-2到7岁 |  com.doding.fmsdjig****** |  1.5万+  
宝宝神奇** |  com.lhyy.wl.new**** |  1.5万+  
儿童学习公主**** |  com.lhyy.wl.princesspuzzl**** |  1.5万+  
****游戏-2到7岁 |  com.doding.fmsdjigsaw**** |  1.5万+  
美图****宝宝拼图 |  com.lhyy.wl.****puzzle |  1.5万+  
****乐园-宝宝游戏 |  com.yuyoogame.ameng******.bingyuan1 |  1.5万+  
儿童游戏-宝宝**** |  com.lhyy.children**** |  1.5万+  
宝宝游戏-儿童*** |  com.lhyy.children**** |  1.5万+  
儿童游戏-宝宝**** |  com.doding.children****** |  1万+  
宝宝认知****游戏 |  com.yuyoogame.******gu1 |  1万+  
宝宝****益智游戏 |  com.lhyy.wl.probaby**** |  1万+  
儿童游戏-****乐园 |  com.yuyoogame.****** |  1万+  
宝宝*** |  com.lhyy.children**** |  1万+  
宝宝游戏***达人 |  com.lhyy.wl.****** |  1万+  
宝宝游戏-儿童****钉 |  com.lhyy.children****** |  1万+  
儿童游戏-**世界 |  com.yuyoogame.****** |  1万+  
****乐园3 |  com.yuyoogame.ameng.**** |  1万+  
儿童游戏****拼图 |  com.lhyy.wl.****puzzle |  1万+  
儿童游戏-宝宝**** |  com.lhyy.children**** |  1万+  
...... |  |  
  
腾讯安全反诈骗实验室自研的TRP-AI反病毒引擎基于应用的行为进行深度学习，能有效探测应用的可疑操作，很好的应对上述病毒应用采用的逃逸技术，目前已经率先支持查杀该木马家族。  

![图片1.png](https://image.3001.net/images/20180528/15274892373572.png!small)![图片2.png](https://image.3001.net/images/20180528/15274892486768.png!small)

## 二、病毒详细分析

我们以 儿童拼图**拼图 样本为例，对“BlackBaby”木马的作恶行为进行详细分析。

### 2.1 病毒执行流程

![1-dama.png](https://image.3001.net/images/20180528/15274893774159.png!small)  

### 2.2 详细流程分析

应用启动时调起fmsd插件的InitSDK方法，会首先连接云端服务器获取配置信息；

![1.png](https://image.3001.net/images/20180528/15274894486173.png!small)![2.png](https://image.3001.net/images/20180528/15274894954676.png!small)

![3-dama.png](https://image.3001.net/images/20180528/1527489510995.png!small)

云端返回的配置信息，其中子包主要有两个，分别为fmsd_sdk.jar 和 fmsd_sdk_standard.jar，并设置了子包在各渠道上是否下发；

![13-dama.png](https://image.3001.net/images/20180528/15274896153770.png!small)

根据云端返回的结果和自身的渠道信息，决定是否下载恶意子包fmsd_sdk.jar 和 fmsd_sdk_standard.jar

![11-dama.png](https://image.3001.net/images/20180528/15274897113972.png!small)![12-dma.png](https://image.3001.net/images/20180528/15274897125096.png!small)

A、fmsd_sdk.jar子包设置隐藏广告界面，针对不同的广告平台，进行刷广告行为，消耗用户流量

![2.png](https://image.3001.net/images/20180528/15274901748227.png!small)

1）、反射调用*** mobad的API接口进行刷广告

![3.png](https://image.3001.net/images/20180528/15274948825231.png!small)

2）、反射调用g***的API接口进行刷广告

![4.png](https://image.3001.net/images/20180528/15274927544795.png!small)

3）、使用自定义的webView加载广告url来刷德业广告

伪造请求，获取广告链接

![4-dama.png](https://image.3001.net/images/20180528/15274903063464.png!small)

广告提供商返回的广告信息

![5.png](https://image.3001.net/images/20180528/15274903576770.png!small)

解析返回的广告信息，使用自定义的webView加载广告

![6.png](https://image.3001.net/images/20180528/1527490416899.png!small)![7.png](https://image.3001.net/images/20180528/1527490422652.png!small)

4）、动态抓包获取的广告流量

![7-dama.png](https://image.3001.net/images/20180528/15274904823789.png!small)![8-dama.png](https://image.3001.net/images/20180528/15274905054645.png!small)

B、 fmsd_sdk_standard.jar子包静默Root用户手机、植入恶意elf模块

1） Dex子包 fmsd_sdk_standard.jar 会从服务器 <http://bnzx.>*****61819
下载加密文件，并解密释放在应用的.um_ass目录，释放的文件libumeng.so是一个so文件，子包通过System.load()
加载so文件，并调用它的load_native()方法；

![8.png](https://image.3001.net/images/20180528/15274906338150.png!small)

So文件libumeng.so会下载dex子包opa_link.jar
，通过JNI调用DexClassLoader将其动态加载，并将获得的ClassLoader返回给Java层；Java层再通过得到的ClassLoader加载目标类并调用其方法；

![9.png](https://image.3001.net/images/20180528/15274906735741.png!small)

2） opa_link.jar
恶意子包被调用后会链接服务器，上传设备相关信息，获取服务器返回的Root子包的相关数据![10.png](https://image.3001.net/images/20180528/15274908557963.png!small)![11-dama.png](https://image.3001.net/images/20180528/152749085517.png!small)

加密传输的网络请求

![14-dama.png](https://image.3001.net/images/20180528/1527490937471.png!small)

解密后的网络请求，我们可以清楚的看到，恶意子包将设备的恶意子包的版本信息、用户应用安装列表、运行包名、运行信息、以及（imei、imsi、osver、mac等）设备信息上传到服务器端；

![12-dama.png](https://image.3001.net/images/20180528/15274912461356.png!small)

解密后的服务器返回数据，包含一些配置信息和root模块的下载url、入口类名、函数名等信息。

![5.png](https://image.3001.net/images/20180528/15274914141191.png!small)

解析服务器返回的数据，获取Root模块的url、入口类名、函数名等信息

![13.png](https://image.3001.net/images/20180528/15274914657978.png!small)

下载root子包，以md5+.jar重命名文件解密释放到应用的.lib/2001目录

![14.png](https://image.3001.net/images/20180528/15274915394926.png!small)

根据下发的配置信息，加载并调起Root子包

![16.png](https://image.3001.net/images/20180528/15274916784469.png!small)

3） Root子包被加载调用后，会联网下载Root方案，对用户设备进行root

![18.png](https://image.3001.net/images/20180528/15274928675207.png!small)  

子包Root成功后，会链接云端服务器，下载、植入病毒相关的脚本和恶意elf文件到设备的系统目录，并进行长期潜伏。其中主要的恶意文件包括但不限于以下文件：

**类型** |  **功能** |  **主要文件**  
---|---|---  
恶意脚本  |  开机启动病毒模块  |  /system/etc/mocdinfo.sh /system/etc/install-recovery.sh
/system/etc/install-cm-recovery.sh /system/bin/.install-recovery.no.sh  
相关配置文件  |  存储相关配置信息和设备标识  |  /system/etc/.asks /system/etc/.chlres
/system/etc/.zosie /system/etc/.uuidres /system/etc/.rac /system/etc/.rsd ...  
恶意elf文件  |  长期潜伏系统，以root权限运行； 与服务器进行通信，上传设备隐私信息； 下载安装应用，进行流氓推广行为  |
/system/xbin/cksxlbay /system/xbin/csbrislp /system/xbin/uixyeb
/system/xbin/.run-us /system/xbin/oqlgo /system/xbin/qgvyjmr
/system/xbin/zisjj /system/xbin/axhxb /system/xbin/wwmxb /system/xbin/culpxywg
/system/xbin/paeoaki /system/xbin/csbrislp /system/xbin/togxzx ....  
  
被植入恶意elf文件模块在后台运行，连接服务器，下载并静默安装恶意推广应用。恶意推广应用启动后，并以插屏、循环轮播的方式频繁弹出广告，严重影响用户手机正常使用。

![19.png](https://image.3001.net/images/20180528/15274930302394.png!small)

## 三、病毒C2C相关信息和逃逸手段

C2C信息

**URL** |  **备注**  
---|---  
<http://apps>****SDK.json |  云端控制信息  
<http://apps.>******SDK_DEX.jar |  fmsd_sdk.jar下载  
<http://apps>******DEX.jar  |  fmsd_sdk_standard.jar下载  
<http://bnzx.>******61819 |  加密so下载  
<http://zynb>******Service  
<http://yznbt.>******Service |  服务器返回Root子包信息  
<http://ef328t.>******.xjar |  加密Root子包下载  
...... |  
  
病毒隐匿技术和对抗手段：

> 1、将恶意功能的实现拆分到多个dex子包中，通过云端配置是否下发，可以绕过应用安装包检测和增加蜜罐分析的难度；
>
> 2、恶意行为隐藏在后台执行，躲过用户感知；
>
> 3、恶意子包加密传输，且使用自定义的字符串变形、加密，增大病毒分析的难度；

## 四、溯源信息

通过对相关信息溯源发现,该幕后黑手是位于天津的厂商

![6-dama.png](https://image.3001.net/images/20180528/15274930846112.png!small)

## 五、安全建议和防范手段

随着Android生态的发展与完善，Android平台的恶意软件与杀软的对抗也日趋白热化，对抗手段不断升级，恶意软件制作者采取各种病毒逃逸技术，混淆、加密、动态加载、云端下发等，以期绕过杀毒软件的检测。针对日益升级的对抗，腾讯安全已推出自研AI反病毒引擎——腾讯TRP引擎，TRP引擎通过对系统层的敏感行为进行监控，掐住病毒软件的命脉，配合能力成熟的AI技术对应用行为的深度学习，能有效识别恶意应用的风险行为，并实时阻断恶意行为，为用户提供更高智能的实时终端安全防护。

![20.png](https://image.3001.net/images/20180528/15274931295357.png!small)

为尽可能的避免恶意软件的危害，我们也给用户提出了以下几条防护建议：

> 1、不要安装非可信渠道的应用；
>
> 2、手机上网时，不要随意点击不明URL链接和扫描安全性未知的二维码信息；
>
> 3、及时进行安全更新；
>
> 4、安装手机安全软件，实时进行保护。

六、附录

样本sha1

> 0efc20d54*****d1d97784
>
> 0aa152ad********afa5e73d9
>
> 30ef38d************1c0699cba3a3c

恶意子包sha1

> c7e015972****476a68bb4
>
> a60f8****ddfd292aa4
>
> 54aed2****09f1e23c
>
> 839fd****203fff04

恶意elf文件sha1

> cccef575****b543a106
>
> 25e8e36****af84ac1
>
> bca00c****f3a9761
>
> 83ea6****7eb8c0fb
>
> 9a891a1****d9f43ddfe

 ***本文作者：腾讯手机管家，转载请注明来自FreeBuf.COM**


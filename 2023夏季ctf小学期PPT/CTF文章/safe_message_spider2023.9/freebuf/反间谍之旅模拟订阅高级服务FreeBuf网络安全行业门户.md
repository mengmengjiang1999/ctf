**导读：何为“间谍”？《说文解字》解释道：“谍，军中反间也。”使用反间计当然需要三寸不烂之舌，这是“谍”的本义。“间”怎么会跟“谍”联系起来了呢？“间”本来写作“闲”，清代文字训诂学家段玉裁为《说文解字》所作的注释说：“开门月入，门有缝而月光可入。”因此“间”的本义就是门缝，泛指缝隙，有缝隙就可以使用反间计了，故称“间谍”。**

这期我们分析的间谍软件较上期分析间谍软件RBMusic有较大不同，恶意程序并不是根据控制端发送的不同指令执行不同窃取用户隐私数据的操作，而是从服务端获取代码进行动态加载，实现无声地模拟与广告网站的自动交互包括模拟点击和输入高级服务订阅的授权代码，窃取受害者的短信、账号、设备信息并上传至服务器。

##  一、样本信息

攻击者将恶意代码集成到应用的广告插件中，所以这四个样本的恶意行为基本相同，都具有获取服务端代码进行动态加载的远控行为和窃取用户短信、账号、设备信息的窃取隐私行为。但是他们的服务器地址有所不同。

应用名  |  包名  |  MD5  |  版本  
---|---|---|---  
Collate Face Scanner  |  com.hello.sweetangle.horoscope  |
6a0d00632d4aa7dac7668b4ee5db708e  |  1.1.2  
Ignite Clean  |  com.Ignite.amino.clean  |  2dfc268c4b791a5af0e4e19837a64144
|  7.3  
Antivirus Security  |  com.anti.mysecurity  |
e6ed729151b98cb2aad0e4ef1beabf47  |  1.1.2  
Beach Camera  |  com.tr.rushphoto  |  a1b5372f3abb8d3bbaa5858f44726523  |  4.2  
  
表 1-1 样本信息

##  二、程序运行框架

###  2.1 流程图

恶意软件只攻击目标国家。大多数受感染的应用程序都包含一个移动国家代码列表(MCC)，但它会把美国或加拿大排除在外。受害者必须使用其中一个国家的SIM卡才会继续执行动态加载DEX文件操作。程序开始从服务器获取动态加载
DEX文件的代码，加载的类名、函数名以及参数。申请开启通知权限，启动监听短信通知服务，如果程序接收到短信通知会发送一个广播。接着加载DEX文件，在DEX文件中注册接收短信信息的广播，上传用户账户以及设备信息，并解析从服务端返回的数据包括需要加载的订阅高级服务的网页url、授权代码、匹配短信信息的正则表达式、以及模拟点击的javascript代码等。然后加载网页和javascript代码模拟点击。等待带有确认代码的SMS消息，并使用正则表达式提取它。最后将获取的设备和短信等信息上传至服务器。

![](https://image.3001.net/images/20191018/1571379339_5da9588b0cc7a.png!small)

图 2-1 流程图

###  2.2 远控框架

从服务器获取动态加载DEX文件的代码，加载的类名、函数名以及参数。参数包含DEX文件中所用到的服务器地址。第二阶段从传入的参数服务器地址中获取需要加载的订阅高级服务的网页url、授权代码、匹配短信信息的正则表达式、以及模拟点击的
javascript代码等信息。

![](https://image.3001.net/images/20191018/1571379359_5da9589f1181c.png!small)

图2-2远控框架

##  三、病毒技术原理分析

###  3.1 监听短信

注册PermissionActivity用于管理通知权限。注册NoteService用于监听短信通知。

![](https://image.3001.net/images/20191018/1571379379_5da958b3971f3.png!small)

图2-3注册组件

检测应用是否开启通知权限。

![](https://image.3001.net/images/20191018/1571379548_5da9595c3d78d.png!small)

图2-4检测通知权限

如果应用没有开启相应权限。则弹框请求权限。

![](https://image.3001.net/images/20191018/1571379584_5da95980619ec.png!small)

图2-5请求通知权限

如果应用已开启通知权限，监听短信通知，获取短信内容并发送发action_text广播。

![](https://image.3001.net/images/20191018/1571379622_5da959a665ab9.png!small)

图2-6监听短信通知

权限请求界面结束时获取各种设备信息并上传至服务器。

![](https://image.3001.net/images/20191018/1571379654_5da959c68c62c.png!small)![](https://image.3001.net/images/20191018/1571379673_5da959d94f851.png!small)图2-7获取设备信息

将获取的设备信息上传至服务器：<http://171.>***.25.250.18000/backend/api/collect。

![](https://image.3001.net/images/20191018/1571379156_5da957d4b8be0.png!small)

![](https://image.3001.net/images/20191018/1571379783_5da95a47b358d.png!small)图2-8上传设备信息

###  3.2 加载DEX

病毒在应用的Application初始化时加入了自己的代码，并将自己代码集成在mopub广告插件中。

![](https://image.3001.net/images/20191018/1571379801_5da95a59136d7.png!small)图2-9程序开始调用

获取SIM卡的移动国家码和移动网络码，排除美国和加拿大两个国家。启动线程。

![](https://image.3001.net/images/20191018/1571379817_5da95a694c8bc.png!small)图2-10获取SIM卡信息

连接服务器：<http://3.>***.143.***/api/shAKNLHIsX?k=Y29tLmhlbGxvLnN3ZWV0YW5nbGUuaG9yb3Njb3BlIzQ2MDAx0LJ。服务器
url的K值是根据包名、SIM卡信息、随机数而产生的。

![](https://image.3001.net/images/20191018/1571379866_5da95a9a56b9d.png!small)图2-11连接服务器

获取服务器返回值，返回的数据已经过DES加密。

![](https://image.3001.net/images/20191018/1571379918_5da95ace0e28d.png!small)![](https://image.3001.net/images/20191018/1571379934_5da95ade53d35.png!small)图2-12获取服务器返回数据

将获取的返回值保存到配置文件中并进行DES解密。密钥为whijgyxx硬编码在代码中。

![](https://image.3001.net/images/20191018/1571380055_5da95b5703b32.png!small)图2-13解密服务器返回数据

解析并以换行符分割数据得到以下数据。

>
> 1.<https://tb>‐eu‐jet.***‐eu‐central‐1.***.com/s8‐5‐release:用于获取将要动态加载的dex文件代码。
>
> 2.<http://18.>***.46.15/ ：作为参数传入DEX文件的函数调用。
>
> 3.tdelXB ：作为参数传入DEX文件的函数调用。
>
> 4.com.plane.internal.Entrance ：作为加载DEX文件的类名。
>
> 5.initialize ：作为加载DEX文件的函数调用。

![](https://image.3001.net/images/20191018/1571380071_5da95b67a3255.png!small)图2-14解析数据

连接服务器：<https://tb>‐eu‐jet.***‐eu‐central‐1.*** .com/s8‐5‐release，
获取DEX文件代码。将获取的代码写入最开始创建的文件中。

![](https://image.3001.net/images/20191018/1571380085_5da95b7584c3a.png!small)图2-15从服务器下载DEX文件

循环读取文件，每次读取128字节写入另一文件中，形成真正将要加载的DEX文件。

![](https://image.3001.net/images/20191018/1571380102_5da95b868d9f2.png!small)![](https://image.3001.net/images/20191018/1571380117_5da95b95a416f.png!small)图2-16创建需加载的DEX文件

加载DEX文件。并调用com.plane.internal.Entrance类中的函数initialize。传入参数<http://18.>***.46.15/和
tdelXB。

![](https://image.3001.net/images/20190929/1569724155_5d9016fba9629.png!small)图2-17加载DEX文件

###  3.3订阅服务

将传入的参数配置为服务器url和TAG_SMS。

![](https://image.3001.net/images/20191018/1571380280_5da95c38cfbc9.png!small)图2-18配置参数

注册广播，用于接收短信通知所发送的广播从而获取短信内容。

![](https://image.3001.net/images/20191018/1571380294_5da95c46449f7.png!small)图2-19注册广播

获取设备信息上传至服务器：<http://cp>****.com/backend/api/v1/dsp/cpi/postback/

![](https://image.3001.net/images/20191018/1571380319_5da95c5f32ff6.png!small)图2-20获取设备信息并上传

获取用户设备信息以及用户账号信息并上传至服务器：<http://18.>***.46.15/api/ldjb/。不同应用上传的服务器地址不一定一样，<http://18.>***.46.15/api/ldjb/这个地址获取不到返回数据，所以我们从服务器地址为
<http://52.>***.93.217/api/ldjb/这个地址中获取了返回数据。

![](https://image.3001.net/images/20191018/1571380343_5da95c77e0402.png!small)图2-21获取用户账号信息并上传

获取用户账号信息，并将获取的账号信息进行字符替换。

![](https://image.3001.net/images/20191018/1571380362_5da95c8aa8195.png!small)图2-22获取用户账号信息

接收服务器返回数据，数据被加密。

![](https://image.3001.net/images/20191018/1571380390_5da95ca619c25.png!small)![](https://image.3001.net/images/20191018/1571380454_5da95ce6eaeb9.png!small)图2-23接收服务器返回数据

解密返回数据，密钥是将本机IMSI、唯一序列号、包名经过一定处理得到的。

![](https://image.3001.net/images/20191018/1571380472_5da95cf8979d7.png!small)图2-24解密服务器返回数据

解析从服务器获取的数据，并将数据保存为JSON格式。

![](https://image.3001.net/images/20191018/1571380485_5da95d058ccb4.png!small)![](https://image.3001.net/images/20191018/1571380501_5da95d159c302.png!small)图2-25解析服务器返回数据

初始化WebView，实现javascript与Java的交互。

![](https://image.3001.net/images/20191018/1571380520_5da95d286288e.png!small)图2-26初始化WebView

加载网页。加载的网页地址是上面已解析的服务器返回值，根据不同的地区设置不同的Ajax异步请求字段。

![](https://image.3001.net/images/20191018/1571380536_5da95d384686c.png!small)图2-27加载网页

当网页加载完成发送MSG_HOLD消息。

![](https://image.3001.net/images/20191018/1571380633_5da95d99d9d73.png!small)图2-28发送MSG_HOLD消息

监听消息，根据不同的消息标志执行不同操作。

![](https://image.3001.net/images/20191018/1571380651_5da95dab76190.png!small)![](https://image.3001.net/images/20191018/1571380666_5da95dba8e365.png!small)图2-29监听消息

接收MSG_HOLD（网页加载完成）消息。通过加载javascript代码，实现javascript与Java互动，调用 onPageDump函数。

![](https://image.3001.net/images/20191018/1571380701_5da95ddd479b8.png!small)图2-30加载javascript代码

通过加载上方服务器返回的cmd标签值来加载javascript代码模拟点击，订阅服务。

![](https://image.3001.net/images/20191018/1571380714_5da95deaeb24f.png!small)![](https://image.3001.net/images/20191018/1571380727_5da95df7adfc5.png!small)图2-31模拟点击服务

服务订阅完成，等待带有确认代码的SMS消息，并使用正则表达式提取短信内容。

![](https://image.3001.net/images/20191018/1571380789_5da95e355072e.png!small)图2-32提取短信内容

所以工作完成后，将获取的短信、设备、错误码、网络状况等信息上传至服务器。

![](https://image.3001.net/images/20191018/1571380823_5da95e571517e.png!small)![](https://image.3001.net/images/20191018/1571380836_5da95e6410aa0.png!small)![](https://image.3001.net/images/20191018/1571380850_5da95e72d7165.png!small)图2-33获取短信、设备信息

将获取的信息上传至<http://18.>*** .46.15/api/report。

![](https://image.3001.net/images/20191018/1571380867_5da95e8330325.png!small)图2-34上传短信、设备信息

###  4.服务器域名统计

包名：com.hello.sweetangle.horoscope

> <http://3.>***.143.26/api/sh%s?k=%s
>
> <https://tb-eu-jet.>***-eu-central-1.****.com/s8-5-release
>
> [http://18.***.46.15/](https://www.freebuf.com/)

包名：com.Ignite.amino.clean

> <http://3.>***.143.26/api/ckwsI3?icc=
>
> <http://tb-eu-jet.>***-eu-central-1.****.com/s8-5-dsp-release
>
> <http://52.77.93.217/>

包名：com.tr.rushphoto

> <http://3.>***.143.26/api/sh%s?k=%s
>
> <https://tb-eu-jet.>***-eu-central-1.****.com/s8-7-release
>
> [http://18.***.46.15/](https://www.freebuf.com/)

包名：com.anti.mysecurity

> <http://3.>***.143.26/api/ckwkc2?icc=
>
> <http://tb-eu-jet.>***-eu-central-1.****.com/s8-5-dsp-release
>
> <http://18.>***.46.1

##  **四、** 安全建议

> 1）让你的设备保持最新，最好将它们设置为自动补丁和更新，这样即使你不是最熟悉安全的用户，你也能得到保护。
>
> 2）坚持去正规应用商店下载软件，避免从论坛等下载软件，可以有效的减少该类病毒的侵害。
>
> 3)关注”暗影实验室”公众号，获取最新实时移动安全状态，避免给您造成损失和危害。
>
> 4)安装好杀毒软件，能有效的识别已知的病毒。  
>

 ***本文作者： 暗影安全实验室，转载请注明来自FreeBuf.COM**  
  


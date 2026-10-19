# Xcode木马样本分析及被挂马的红包插件

阅读量 **106759**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-09-18 21:32:35

 **x**

##### 译文声明

本文是翻译文章，文章来源：360NiranTeam涅槃

译文仅供参考，具体内容表达以及含义原文为准。

**Xcode事件持续升温！APP受感染数量再度升级！！！**

**一,受影响app**

360NiranTeam团队连夜扫描了14万5千多个app，共发现344款app感染XcodeGhost木马，其中不乏有百度音乐，微信，高德，
滴滴，花椒，58同城，网易云音乐，12306，同花顺，南方航空，工行融e联，重庆银行用户量很广的app，涉及互联网、金融、铁路航空、游戏等领域

微信 | 6.2.5  
---|---  
炒股公开课 | 3.10.02-3.10.01  
股票雷达 | 5.6.1-5.6  
CarrotFantasy | 1.7.0.1-1.7.0  
我叫MT | 4.6.2  
逆轉三國 | 5.80.5-5.80  
卷皮 | 3.3.1  
南京银行 | 3.6-3.0.4  
网易云音乐 | 2.8.1  
图钉 | 15205-7.7.2  
Theme | 2.4  
南方航空 | 2.6.5.0730-2.6.5  
下厨房 | 4.3.1-46  
诊疗助手 | 7.2.3  
WallpaperFlip | 1.8  
VGO视信 | 1.6.0  
高德地图 | 7.3.8.1040-7.3.8  
天使房贷 | 5.3.0.2-5.3.0  
FaceAgeCamera | 3.6.7  
三国名将 | 4.5.0.1-4.5.1  
Theme | 2.4.2-2.4  
滴滴打车 | 3.9.7.1-3.9.7  
Phone+ | 170-3.3.6  
天涯社区 | 5.1.0  
AA记账 | 1.8.7-1.8  
MailAttach | 2.3.2-2.3  
沃玩家 | 1.7.0.1-1.7.0  
微贷网理财 | 2.3.201507291150-2.3.0  
Golf | 2.4.3.2-2.4.3  
PianoTiles6 | 4.1.10  
滴滴出行 | 4.0.0  
牛股宝手机炒股票 | 2.1  
轻松e贷 | 2.2  
news | 2626-2.6.2  
云南手机台 | 3.3.2-3321  
铁路12306 | 2.12-2.1  
夫妻床头话 | 2.0.1  
UME电影票 | 2.9.4  
妈妈圈 | 5.3.0  
DigitGod | 2.0.4-2.0  
造梦西游OL | 4.6.0  
神雕侠侣 | 1.1  
PrincessSalon | 1.0-1.2  
美菱生活 | 4.3.0  
车星人 | 4.0.1-4.0  
MakeMeASuperStar | 1.0-1.2  
TDVideoCol | 3.4.3-3.4  
我有车 | 2.1.1.102-2.1.1  
付融宝 | 20150703-1.0.6  
精品后宫小说 | 2.9.0-2.9  
烘焙秘方 | 3.0  
Scanner+ | 5.0.2-5.0  
mts-iphone | 2.2.0  
FeedBaby | 1.0.3  
合理用药 | 3.2.4-3.2.3  
漫画魔屏 | 7602-7.1.3  
疯点 | 2.7.3-2.7.1  
奇幻仙侠小说 | 2.9-2.9  
淘金路 | 6.1.2.3-6.1  
FollowMe | 168-6.1  
青岛公交查询 | 2.6.0-921  
嘟嘟 | 1.2.119  
部落冲突攻略 | 7.0.0  
magicfishiOS | 1.0.5.4-1.0.5  
穿越小说 | 3.751-3.75  
原油喊单 | 1.2  
福州市民网 | 28-2.114  
公交e路通 | 1.0.2-1.0.5  
卓创农业 | 2.2.0.1-2.2  
IWithYou | 2.3.0.6-2.3.0  
合不拢嘴 | 4.0-4.0.0  
WallPapersHD | 1.0.10  
大众妙客 | 12-1.5.0  
LensCollage | 2.53-2.5  
蛋糕叔叔 | 1.4.3  
Theme | 1.2-1.2  
SplitLens | 5.5.1-5.5  
程序员读 | 1.60.01-1.60  
Baseball | 2.4.2.0-2.4.2  
iWallPapers | 1.2.16  
疯狂24点 | 2.0.1-2.0  
读么 | 2.7.2-2.7  
Taguage | 4.0  
懒人周末 | 1.3.0.0-1.3.0  
画吧 | 1.2.7-1.2.1  
暗黑黎明 | 1.6.0-1.6.0  
DontMakeThemDie | 2.1-2.1.0  
工作宝 | 3.0.1  
支付通签约宝 | 2.1.7  
地图木拼 | 2.0.3  
网络医院 | 2.2.3  
掌证宝天玑版 | 3.0.2-3.0.2  
快乐备孕 | 2.0.0  
我叫MT2 | 1.9.5  
玩机助手 | 1003-1.2.0  
拍鞋网 | 2015070301-2.3.2  
我叫MT2攻略 | 7.0.0  
电掌柜 | 1.6  
中医百科 | 2.1.0  
中医常见疾病 | 2.1.0  
读名著学英语 | 2.0.0  
海棠社区 | 1.2.2005-1.2.201  
移动办税平台 | 14.2.2  
药给力 | 1.10.1  
永泰惠 | 150715-1.1.6  
39健康管家 | 29-0.2.5  
航海王启航 | 2.5.1-2.5  
录音宝 | 22-1.0.1083  
恒富在线 | 1.0.9-1.5  
财理你 | 1.2.4  
中国太保 | 208-2.0.8  
营养早餐食谱 | 2.0.0  
荤菜食谱 | 2.0.0  
ddc | 1.0.5-1.0.6  
必趣视频 | 4.1.5  
素菜食谱 | 2.0.0  
言情小说专集 | 1.1.1-7  
口袋记账 | 1055-1.6.0  
微博相机 | 2139-1.5.0  
暴走表情包 | 2015.08.011-2015.08.01  
西餐食谱 | 2.0.0  
爱竞彩 | 2.4-1.2.2  
Note | 1.0.5.0-1.0.5  
NinjaDash | 1.3-1.3.0  
口袋机战 | 1.0.12-1.0.12  
自由之战 | 1.0.9.2-1.0.9  
猫豆 | 1.4.3  
战地征服 | 1.1216-1.121  
绿色浏览器 | 1.6-1.7.0  
FilmStarSalon | 1.0-1.0  
PP基金 | 1.0.0-1.1.2  
4+1！ | 1505111716-1.0  
猫市台湾快食 | 2.0.2  
FashionStylist-Actor | 1.0  
玉米做法大全 | 1.0.0  
途游麻将 | 1-3.502  
同花顺至尊版 | 9.53.01-9.53.01  
快手菜谱 | 1.0.0  
小吃点心大全 | 1.0.1-1.0.0  
SeaDiamondiOS | 1.0.4-1.0.4  
WeddingSalon | MermaidBride-1.0  
家常小炒 | 2.1.0  
战舰少女攻略 | 700-7.0.0  
Costumedresssup! | 1.1-1.0  
CandySodaiOS | 1.0.3  
税吧 | 1.4-2.0  
桌上坦克 | 1.0.95  
奥特曼横扫怪兽 | 1.3-1.2  
粽子大全 | 1.0.1-1.0.0  
去潜 | 1.1.7  
ForestAdventure | 1.0  
SugarCarnivaliOS | 1.0.7  
PregnantEmergencyDoctor | 1.0.2.1-1.0.2  
FashionDollHairStylist | 1.0  
ExcavatorStunt | 2.0.1.0-2.0.1  
MSPT_Merchant | 1.2.10.0-1.2.10  
钱宝有票 | 2.0.2-2.0.0  
智慧树 | 3.9  
国海极速开户 | 16-3.1.4  
KnowVegetables | 618-1.6.18  
南瓜饼做法 | 1.0.1-1.0.0  
一日多餐 | 20150502001-1.0.0  
糯米饭 | 20150507001-1.0.0  
西游记评书 | 1.0.1-1.0.0  
自由之战iPad | 1.0.7.3-1.0.7  
包子做法大全 | 1.0.0  
途游中国象棋 | 2-3.372  
FromPrincesstoSuperhero | 1.1-1.0  
心健康 | 1.0.4  
凉菜食谱 | 2.0.0  
斗牛牛 | 158-1.3.7  
客户管家 | 1.3.9.3-1.3.9  
Timer运动 | 2.002  
PromHairSalon | 1.0  
FashionStar | 1.0-1.1  
有财股票开户 | 16-3.2.2  
代理人微店 | 1-2.1.1  
米乐汇斗地主 | 2-1.0.0  
桂林中医院 | 1.0.1-1.0.1  
中国大学慕课 | 201009-1.0.3  
拇指医学院 | 1.0.8-1.1.0  
EnglishBite | 34-1.2.3  
FlyingAwesomeGolf | 1505231548-1.0  
FoodStallStory | 1.1-1.0  
GangGouHelper | 1.0.4  
聪头 | 21-1.5.3  
安徒生童话 | 1.2-1.0  
烘焙烤箱食谱 | 2.0.0  
SiblingModels | 1.0-1.1  
HomeEdition | 1.0  
HairSalon | 1.0  
优品速达 | 1.0  
Petcontestsalon | 1.0  
PrincessPet | 1.0  
CamCard | 6.5.1.9544-6.5.1  
BirthdayBash | 1.2-1.0  
好吃吗 | 2.0.7-2.0  
伊索寓言故事 | 1.0-1.0  
ComingCall | 1.52-1.52  
Superstar2 | 1.0-1.0  
ScramblingSnakes | 1.1.1  
财富 | 2.0  
梦幻战神 | 10.2.2-10.2.2  
都都宝 | 1.2.2.1-1.2.2  
JewelsQuest | 3.8-3.8  
YaYa药师 | 1.1.1-1.1.1  
JewelsQuest2 | 3.39-3.39  
YaYa | 6.4.3-6.4  
WO+创富 | 2.0.6-2.0.4  
2345浏览器 | 4.0.1-4.0.1  
Albums | 292-2.9.2  
豆腐做法大全 | 1.0.0-1.0.0  
PonySalon | 1.0-1.0  
MusicFestivalSalon | 1.0-1.1  
银耳汤做法 | 1.0.0-1.0.0  
财达同花顺 | 2.4.2-2.4.2  
花椒 | 2627-1.3  
舌尖上的美味 | 2.0.1-2.0.0  
鲫鱼做法大全 | 1.0.0-1.0.0  
挖掘机大师3D | 1.0.5.0-1.0.5  
BoatTripSalon | 1.0-1.0  
特色西餐 | 1.0-1.0  
Juniorchefmaster | 1.0-1.1  
炒饭做法大全 | 1.0.0-1.0.0  
心脏病防治 | 1.0.1-1.0.0  
Empireoftheocean | 2.7.1-2.7  
MagicKing | 2.0-2.0  
炒股入门 | 1.0-1.0.3  
星派送 | 1.0-1.0  
智慧树 | 3.9-3.9  
CollectBoys | 1.0-1.0.0  
懒人私房菜 | 2.0.1-2.0.0  
PrincessMakeover | 1.0-1.1  
美味奶茶DIY | 1.0.0-1.0.0  
营养早餐 | 1.0-1.0  
申万宏源 | 1-1.1.6  
一品粥 | 1.0-1.0  
素菜大全 | 1.0-1.0  
公交来了 | 20150715-1.3  
KneeDoctor | 1.0.1.1-1.0.1  
黄瓜做法大全 | 1.0.0  
微调查 | 1432-3.4.5  
中药方剂辞典 | 2.0.0  
ChinessChess | 618-2.6.18  
土豆做法大全 | 1.0.0  
鱼的做法 | 1.0  
冰品饮品DIY | 1.0  
面包做法大全 | 1.0-1.0  
仁和珠宝 | 1.02-1.0  
一日三餐 | 1.0.1-1.0.0  
风云三国2 | 1.0.1  
汽车之友 | 2.0.12-1.40  
AutoWorld | 261-3.1.3  
财新周刊 | 3041-3.0.4  
PDFReaderFree | 2.7.6-2.7.1  
悦耳 | 2.3.2-2.3.2  
AngelFuel | 4.3.0.2-4.3.0  
EFParents | 106-2.0.0  
中搜搜悦 | 5.0.0-5.0.0  
YOHO!有货 | 3.4.0.1508240001-3.4.0  
GNum | 2.3.100000459  
WallPapersHD* | 9.3.5-9.3.5  
TurboInvoice | 2.3.1-2.3  
MyChevy | 1422767631-3.1  
PetCatchiOS | 1.3.7.3-1.3.7  
问他作业 | 33-4.2.0  
航海大时代 | 2.5.1-2.5  
语玩 | 240-0.6.4  
PaoPaoTang | 12000-1200  
牵牛 | 1.5.3-1.5.2  
卡曼 | 2.7-2.7  
琅琊榜 | 2.9.2-2.9  
造梦西游OL | 4.6.0-4.6.0  
集享卡 | 1.5.3-1.5.3  
58同城 | 6.1.8.1-6.1.8  
nvshen | 975-2.5.6  
暗黑战神 | 1.13.2-1.13.2  
耍大牌 | 4.5.1-4.5.1  
漫画帮 | 19-4.3.2  
猫团动漫 | 5.5.2-5.5  
海玩 | 2.1-3.0  
Golf | 2.4.2.0-2.4.2  
摩擦 | 45-2.4.9  
百度财富 | 9825-2.2.2  
言情小说吧 | 3.3.3-3.3  
BlackWhiteTiles4 | 9.4.5  
康康在线 | 5.6.0  
加拿大订餐 | 4.0.1  
YingYue | 1.6-1.5  
eHome | 1.26.4  
幸福相馆 | 2.1.3-2.1.3  
支付通QPOS | 3-2.1.2  
平安易贷 | 2.9.0-2.9.0  
你我贷 | 4.2.0.9626-4.2.0  
穷游 | 6.4.1-6.4  
CuteCUT | 1715-1.7  
同花顺 | 9.26.03-9.26.01  
Perfect365 | 4.6.16  
电话归属地助手 | 1-3.6.3  
OPlayerLite | 21051-2105  
H3C易查通 | 2.3-2.2  
百度音乐 | 5.2.7.3-5.2.7  
动卡空间 | 3.4.4.1-3.4.4  
CamCard | 6.3.2.9095-6.3.2  
UA电影票 | 24-2.9.2  
MTP管理微学 | 1.0.0-2.0.1  
YddHotelPro | 14-2.5.2  
美丽家 | 204-2.2.1  
3D动物陆地版 | 3.0.2-3.0  
工银融e联 | 1.1.3.3-1.1.3  
安心理财 | 2.3.8.3-2.3.8  
妈妈值得买 | 6.0.11-6.0  
Research | 1.8-1.8  
MonsterGirlsMakeover | 1.0-1.4  
零钱包 | 4.0.1.0-4.0.1  
南京银行HD | 1.2-3.0.3  
Hugo | 1507031050-2.8.0  
北京工行Style | 1.1.1-1.1  
卓创短讯 | 2.0  
途游德州扑克 | 2-3.375  
钱宝网 | 3.1.3-3.1.3  
WinZip | 4.2-4.2  
口语100 | 314-3.1.2  
富通贷 | 1.2.3-1.1.1  
留学僧 | 199-1.8  
fishsagaiOS | 2.1.2.3-2.1.2  
鱼说 | 202-3.8.0  
西部信天游 | 2.21.011-2.21.011  
LoveStar | 1.0-1.1  
Ps互动教程 | 3.2.1-3.2  
fishinghappyiOS | 1.1.5.2-1.1.5  
Tennis | 43-2.1.0  
途游欢乐牛牛 | 2-3.37  
银泰掌如e.1.3 |  
联趣斗地主 | 1.8.3-1.8.0  
快秀 | 1.4.1.1-1.4.1  
博客下载-For新浪 | 59-1.58  
重庆银行 | 1.0-2.9  
金税通查验 | 309-3.0.9  
恒泰金玉管家 | 1.4  
Tennis | 43-2.1.0  
健康交行 | 3.25  
  
**二、攻击方式及来源**

通过向IDE中植入恶意代码,进而通过IDE向其编译、生成的应用中插入恶意代码。

恶意程序的主要来源:百度网盘、迅雷等第三方平台。

**三、问题描述**

从第三方源下载的 Xcode(苹果平台IDE) 被植入恶意代码,使用受感染的 Xcode 编译、生成的应用中会被植入后门。

间接影响 Xcode 支持的所有平台,包括:iOS,iPhone 模拟器,Mac OS X,目前受影响最大的是 iOS 平台。

被植入恶意代码的 iOS 应用会向 C&C 服务器上传信息,

具体信息包括:时间、应用名字、应用标识ID、设备名字与类型、系统区域及语言、设备唯一标识UUID、网络类型。

**四、xcode样本分析**

xcode样本下载<http://yunpan.cn/cHfMAZY8DA356> (提取码:39e0)

正常的xcode目录结构中SDKs目录下没有Library目录

被种植恶意木马的Xcode中包含了恶意的CoreService库文件,目录结构如下:

Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/Library/Frame

works/CoreServices.framework/CoreService

恶意xcode影响范围

从样本上分析,影响 Xcode v6.1 ~ v6.4。

但是理论上可以影响 Xcode 的所有版本。

影响平台ios,ios模拟器,macox X86 或者x86_64位多版本

**五、苹果官方appstore微信6.2.5样本分析**

微信 6.25 样本 <http://yunpan.cn/cHfMy5WXVbcQM> (提取码:b7b3)

抓包查看如下:

抓包查看如下:

逆向分析connection函数发送的网站地址

****

**六、越狱平台微信抢红包插件分析**

插件样本 <http://yunpan.cn/cHfMTQ9tRmbjY> (提取码:e6d7)

在上次分析过红包插件盗取22万icloud信息的插件后发现在此插件上还隐藏着另一个后门,盗号插件也中了xcode木马,红包插件名称为iwexin.dylib

MD5 :137fdaa6f32658e1a7315f74957e22a0

使用别篡改的XCode会加载coresevice库文件,在编译出的APP或dylib包含了如下头文件的头文件,所有的恶意函数隐藏其中

通过分析使用恶意XCode编译的iwexin.dylib启动时执行如下类中的函数进行收集信息并发送,如下为发送消息至服务器的.h文件和类

通过反编译查看恶意代码收集信息分别为:

国家,语言,设备信息,系统版本,时间戳,app的bundleID

以下为收集设备信息的.h文件和类

以下是ida中查看的获取设备等信息的关键代码

在ida中查看到主要恶意代码关键部分如下,随着程序启动开始执行,获取设备信息发送信息至init.icloud-analysis.com

**七、检测方法**

如果 Xcode 中存在如下文件与目录,即可认为受感染:

1Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/Library/Frameworks/CoreServices.framework/CoreService,针对
iOS

2Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/Library/PrivateFrameworks/IDEBundleInjection.framework,针对
iOS

3Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/Library/Frameworks/CoreServices.framework/CoreService,针对
iPhone 模拟器

4Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/Library/PrivateFrameworks/IDEBundleInjection.framework,针对
iPhone 模拟器

5Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/Library/Frameworks/CoreServices.framework/CoreService,针对
Mac OS X

6Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/Library/PrivateFrameworks/IDEBundleInjection.framework,针对
Mac OS X 7

**八、解决方案**

1、高优先级检测所有编译服务器、自动发布服务器中的 Xcode 是否被感染。

2、开发者需要检查系统中所有版本的 Xcode 是否被感染。

3、如果受感染,首先删除受感染的 Xcode,然后从 Mac AppStore 或者从开发者中心下载 Xcode。

4、如果线上的应用是用受感染的 Xcode 发布的过,请使用官方的 Xcode 清理、重新编译应用,然后上传 AppStore,尽量向苹果说明情况,从而走
AppStore 的紧急上线流程

本文翻译自360NiranTeam涅槃 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360信安-涅槃团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82437](/post/id/82437)

安全客 - 有思想的安全新媒体

本文转载自: [360NiranTeam涅槃]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t018799f60cb7058aec.png) 360信安-涅槃团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


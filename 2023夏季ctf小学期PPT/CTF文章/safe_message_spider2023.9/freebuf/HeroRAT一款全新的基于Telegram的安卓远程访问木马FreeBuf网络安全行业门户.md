**ESET的恶意软件研究专家近期发现了一种新型的AndroidRAT，并将其命名为HeroRat，这款恶意软件利用了Telegram协议来实现远程命令控制以及数据提取。**  

![HeroRAT：一款全新的基于Telegram的安卓远程访问木马](https://image.3001.net/images/20180621/15295962044721.png!small)

实际上，HeroRat并不是第一款利用Telegram协议的恶意软件，之前还曾出现过例如[TeleRAT](https://securityaffairs.co/wordpress/70551/cyber-crime/telerat-android-trojan.html)和[IRRAT](https://news.drweb.com/show/?i=11331&lng=en)这样类似的恶意软件。

HeroRat从2017年8月份就开始在全世界传播了，而在2018年3月份它的源代码在Telegram Hacking
Channels中被发布了出来，任何人都可以免费获取到，这也就意味着网络犯罪分子可以根据自己的需要开发出相应的变种。

不过，HeroRat跟其他借鉴相同代码的变种非常不同，HeroRat是第一款基于Telegram并使用了Xamarin框架的恶意软件，它利用[Telesharp](https://github.com/DaFri-Nochiterov/Telesharp/blob/master/README.md)库来创建Telegram
bot，并采用C#完成了所有的开发，而其他的恶意软件都是采用Java编写的。

根据ESET发布的分析报告：“虽然原版代码已经开源，但这款RAT仍在特定的Telegram
channel上进行出售，而且有三种价格模型可选择。需要注意的是，我们现在还无法确定这款RAT是根据泄露源码开发出来的，还是它本身就是泄漏的源码。”

根据研究人员的介绍，HeroRat目前主要通过伪装成第三方应用商店中的社交媒体App和即时消息App来进行传播。目前受影响最严重的地区为伊朗，该地区的恶意软件主要通过声称提供免费的比特币、免费的联网资源和社交媒体粉丝来吸引目标用户的安装。

![HeroRAT：一款全新的基于Telegram的安卓远程访问木马](https://image.3001.net/images/20180621/15295962118749.png!small)

ESET在对HeroRat进行分析时发现了一个非常奇怪的行为，即在目标设备上安装并运行之后，它会显示一个小的弹窗并提示用户该应用无法在设备上运行，因此很多用户会选择直接卸载它。卸载之后，应用图标会消失，很多用户会认为已经卸载成功了，但其实攻击者早就已经拿到了目标设备的远程控制权限。

攻击者可以利用[Telegram
bot](https://core.telegram.org/bots)来控制受感染设备，并执行例如数据提取和音频/视频录制等大量命令。

分析报告中写到：“该恶意软件具备多种间谍工具以及数据提取功能，其中包括拦截和发送短信消息、拨打电话、提取通讯录、音频/视频记录、屏幕截图、获取设备地理位置以及控制设备设置等等。”

![HeroRAT：一款全新的基于Telegram的安卓远程访问木马](https://image.3001.net/images/20180621/15295962183898.png!small)

HeroRat的源代码基本售价为650美元，并根据用户所需要的功能，该恶意软件还分别提供了青铜版、白银版和黄金版三个升级版本，每个版本分别需要加价25、50和100美元。

 ***
参考来源：[securityaffairs](https://securityaffairs.co/wordpress/73669/malware/herorat-telegram-based-android-rat.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


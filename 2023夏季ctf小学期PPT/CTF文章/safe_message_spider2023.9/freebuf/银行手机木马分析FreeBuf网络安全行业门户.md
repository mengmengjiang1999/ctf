**Android银行木马Geost是最初监视HtBot恶意代理网络检测到的。该僵尸网络以俄罗斯银行为目标，受害者人数已超过80万。该木马使用了混淆，加密，反射和注入非功能代码等方法使逆向分析更加困难。**

##  初步分析

Geost隐藏在随机生成的服务器主机名非官方网页中，利用恶意应用进行传播。 受害人在寻找Google
Play找不到所需应用或无法访问应用商店时通常会在一些不起眼的Web服务器上找到该应用的链接，下载应用程序然后启动。
应用程序将请求权限，如果受害者允许，则可以启用恶意软件。

Geost样本嵌入在俄语名为“установка”的恶意应用中， 该应用程序显示了一个Google Play图标。

![](https://image.3001.net/images/20200322/1584858837_5e7706d58ec23.png!small)

启动应用程序时，它要求设备管理员特权，用户可能在不知不觉中允许重要权限包括访问SMS消息。攻击者可以访问银行应用程序，收集受害者的姓名，余额和其他银行帐户详细信息。只需单击几下，攻击者便可以从受害者的银行帐户中转移资金。

![](https://image.3001.net/images/20200322/1584859058_5e7707b2082db.png!small)![](https://image.3001.net/images/20200322/1584859058_5e7707b20c80b.png!small)

确认必要的权限后，应用程序自我隐藏，并隐藏应用程序图标使受害者认为该应用已被删除。恶意软件一直在后台运行，攻击者获得设备访问权限，可以监视已发送和已接收的消息，包括来自银行的SMS确认消息。为了在重新后启动，它会注册BOOT_COMPLETED和QUICKBOOT_POWERON广播。

![](https://image.3001.net/images/20200322/1584859238_5e770866ed3ad.png!small)

##  第一阶段

与许多恶意软件一样，Geost运行分为多个阶段。 第一阶段是下载解密并运行第二阶段，第二阶段将变得更加复杂。

Geost示
APK在的classes.dex文件中包含已编译的Java代码，还包含AndroidManifest.xml和资源文件，还有一个大小为125k的“
.cache”文件。

![](https://image.3001.net/images/20200322/1584859436_5e77092c7b097.png!small)第一阶段中所有字符串都通过R**加密，该算法被拆分为多个函数以避免表明它使用了R**。
下一步就是找到用于R**解密的密钥。

![](https://image.3001.net/images/20200322/1584859621_5e7709e522d97.png!small)![](https://image.3001.net/images/20200322/1584859621_5e7709e51af9c.png!small)R**密钥：  
![](https://image.3001.net/images/20200322/1584859621_5e7709e51e49b.png!small)R**内部状态随每个解密的符号而变化，通常必须与加密相同的顺序解密。但本样并非如此，R**加密代码始终复制数组S
[]，编写者简化了R**不保留解密之间的内部状态。

![](https://image.3001.net/images/20200322/1584859907_5e770b03abed2.png!small)搜索通用代码库，发现Android.support.v4库和ReflectASM
Java Reflection库。

![](https://image.3001.net/images/20200322/1584860444_5e770d1c78c2c.png!small)第一阶段使用相同的R**算法和密钥解密第二阶段的文件，反射方法调用：

![](https://image.3001.net/images/20200322/1584860560_5e770d90e176d.png!small)“
.cache”文件被重命名为.localsinfotimestamp1494987116，在解密后另存为ydxwlab.jar，从中加载并启动.dex文件。

![](https://image.3001.net/images/20200322/1584860616_5e770dc879d48.png!small)代码作者插入错误标志HttpURLConnection及其URL，该URL已连接到命令和控制（C＆C）服务器，但是此http连接永远不会执行。错误标志：

![](https://image.3001.net/images/20200322/1584860701_5e770e1d9bbd0.png!small)第一阶段在第二阶段开始部分加载一个类，其名为“
MaliciousClass”。

![](https://image.3001.net/images/20200322/1584860806_5e770e8686e89.png!small)

##  第二阶段

c第二阶段中再次使用了混淆和加密，符号名称部分替换为长度为1-2个字符的字符串，不是6-12个字符串，修改了字符串加密算法。
此外，针对每个类别分别修改了解密算法的参数。

![](https://image.3001.net/images/20200322/1584860904_5e770ee896fcb.png!small)![](https://image.3001.net/images/20200322/1584860909_5e770eed6104c.png!small)每种类的解密算法都有不同的参数顺序和不同的常量。

![](https://image.3001.net/images/20200322/1584860978_5e770f32553fa.png!small)字符串解密后，可以检测到所使用的库：

> AES加密
>
> Base64编码
>
> 仿真环境检测
>
> 文件下载服务
>
> IExtendedNetworkService
>
> USSD API库
>
> Zip4jUtil

##  初始化阶段

第一阶段调用的MaliciousClass充当实例化类的envelope，研究人员命名为“ Context”。

![](https://image.3001.net/images/20200322/1584861193_5e77100999ca6.png!small)Context类首先启动EmulatorDetector服务。
然后将启动AdminService和LPService，然后启动主应用程序Intent。

![](https://image.3001.net/images/20200322/1584861238_5e771036b7828.png!small)

###  仿真环境检测

检测器会检查其是否在仿真环境中运行，样本可检测Nox，Andy，Geny，Bluestacks和Qemu Android仿真环境。

![](https://image.3001.net/images/20200322/1584861331_5e771093a85f1.png!small)

###  AdminService

该服务负责向应用程序授予管理员权限，可以访问敏感数据并启动特权操作。

![](https://image.3001.net/images/20200322/1584861391_5e7710cf12d23.png!small)

###  LP服务

该服务负责保持应用程序运行并连接到C＆C服务器。

![](https://image.3001.net/images/20200322/1584861431_5e7710f774610.png!small)

LPService创建LPServiceRunnable线程，该线程每五秒钟唤醒一次，负责监视和重新启动以下服务：

> MainService
>
> AdminService
>
> SmsKitkatService

###  MainService

MainService首先挂接到AlarmManager，然后注册两个广播接收器MainServiceReceiver1和MainServiceReceiver2。
在初始化阶段结束时，它将启动MainServiceRunnable Thread。 样本执行onDestroy方法时，将再次重新启动MainService。

![](https://image.3001.net/images/20200322/1584861636_5e7711c4d14f9.png!small)MainService中processApiResponse()处理从C＆C服务器接收的JSON字符串命令。

![](https://image.3001.net/images/20200322/1584861714_5e771212287c2.png!small)

###  ClearService

该服务调用ClearServiceRunnable线程负责锁定、解锁命令，攻击者无需用户干预即可执行远程任务。
如果尝试终止ClearService，它将重新启动。

###  SmsKitkatService

该服务负责用攻击者编写的应用程序替换标准的SMS应用程序。

![](https://image.3001.net/images/20200322/1584861972_5e7713141b4b4.png!small)

##  指令

命令列表：

![](https://image.3001.net/images/20200322/1584862103_5e7713970f34e.png!small)![](https://image.3001.net/images/20200322/1584862103_5e7713971269e.png!small)

##  解决方案

趋势科技在《[2020年安全预测](https://www.trendmicro.com/vinfo/us/security/research-and-analysis/predictions/2020?_ga=2.230278684.1689648061.1584794338-2003221911.1564911869)》中预测了针对在线银行和支付系统的移动恶意软件家族（例如Geost）持续增长。移动用户需要在危险支付环境时遵循安全原则来保护自己，保护自己的移动设备，避免在官方应用商店之外下载应用。

攻击者开发了通过合法应用商店传播恶意应用方法。随着应用商店自我检查删除恶意软件，用户需要在下载之前仔细检查应用程序评论和其他信息来避免下载到恶意软件。

用户应仔细检查已安装应用程序请求的权限，注意设备的变化，例如性能降低或电池寿命降低，这可能表示设备被恶意软件感染。在这种情况下，用户应立即删除新安装的应用程序。用户还应该进行定期检查，删除未使用的应用程序。

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/dissecting-geost-exposing-the-anatomy-of-the-android-trojan-targeting-russian-banks/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  


**2019年7月Dr. Web报道了[Google
Play中的后门木马](https://news.drweb.com/show/?i=13349&c=0&p=0)，研究人员将其称为“PhantomLance”，它最早活动记录可追溯到2015年12月。目前发现了数十个在野样本，出现在Google
Play等各种应用程序市场中。 最新样本于2019年11月6日在官方Android市场发布，不久后被官方删除。  
**

![image.png](https://image.3001.net/images/20200504/1588587166_5eafea9ec1707.png!small)

在调查过程中发现其与OceanLotus APT有很多相似之处。

## 恶意软件版本

为了便于研究，根据技术复杂性将发现的样本分为基本版本1到高度复杂版本3，版本号与出现的时间不完全相关。

所有样本的功能都是相似的，主要目的是收集敏感信息，包括地理位置，呼叫记录，联系人、SMS、已安装的应用程序列表以及设备信息。攻击者能够根据特定设备环境下载并执行各种恶意有效负载。

### Version 1  

此版本是最新的Google
Play样本（MD5：2e06bbc26611305b28b40349a600f95c）。与其他版本不同，它不会删除其他可执行文件。攻击者尝试使用多种技术绕过Google官方过滤，于2019年上传到Google
Play商店。清单文件中未提及可疑权限，攻击者将其隐藏在dex可执行文件中，在执行过程中动态请求。恶意软件大多数操作都需要root权限。如果设备有root特权，恶意软件可以通过“setUidMode”获得所需权限，无需用户参与。

![image.png](https://image.3001.net/images/20200511/1589188979_5eb9197341a38.png!small)

### Version 2  

此版本在2019年或更早的时候被检测到，其中一个样本于2019年11月出现在Google Play商店中。
根据检测统计数据和版本戳，可判断该版本是版本3的替代品。

恶意有效载荷APK打包在assets加密（AES）文件中，解密密钥和初始化向量（IV）位于加密有效载荷的前32 + 16字节中。  

![image.png](https://image.3001.net/images/20200511/1589189304_5eb91ab8cbe89.png!small)![image.png](https://image.3001.net/images/20200511/1589189317_5eb91ac5d035f.png!small)在APK
magic前，文件头包含对有效载荷方法反射调用的字符串。  

![image.png](https://image.3001.net/images/20200511/1589189404_5eb91b1c504eb.png!small)

所有版本2有效负载都使用相同的程序包名称“com.android.play.games”，类似于官方Google
Play游戏程序包“com.google.android.play.games”。此外，在解密的有效载荷中发现了开发人员版本标记。

![image.png](https://image.3001.net/images/20200511/1589189464_5eb91b58c390d.png!small)

如版本1所述，恶意功能所需的权限是通过未记录的Android API授予的，还发现用于签名版本2有效负载的两个不同证书。

###
![image.png](https://image.3001.net/images/20200511/1589189540_5eb91ba476453.png!small)Version
2.1  

2020年初发现PhantomLance最新样本引入了解密有效载荷的新技术：恶意有效载荷和植入程序捆绑在一起，并使用AES加密。
密钥不会自身携带，而是通过Google的Firebase远程配置系统发送到设备，其他技术功能与版本2非常相似。

向PhantomLance的Firebase
API发出有效请求，响应JSON结构包含AES解密密钥，其中“code_disable”值是有效负载的解密密钥。  

    
    
    {
        "entries": {
            "code_disable": "27ypYitp1UFc9Tvh"
        },
        "appName": "com.ozerlab.callrecorder",
        "state": "UPDATE"
    }  
    

攻击者试图实现第三阶段有效载荷植入。
第二阶段有效负载（MD5：83cd59e3ed1ba15f7a8cadfe9183e156）包含一个名为“data”的APK文件（MD5：7048d56d923e049ca7f3d97fb5ba9812），其assets已损坏。  

![image.png](https://image.3001.net/images/20200511/1589189889_5eb91d010b754.png!small)第二阶段如下所述读取此APK文件，对其解密并重写其前27个字节。  

![image.png](https://image.3001.net/images/20200511/1589189923_5eb91d235799d.png!small)  

执行后会产生一个APK文件（MD5：c399d93146f3d12feb32da23b75304ba），该文件配置有C2服务器（cloud.anofrio[.]com,
video.viodger[.]com, api.anaehler[.]com） 。
第三阶段APK在assets中有名为“data.raw”的本地库，该库用于在受感染的设备上实现持久控制。  

###
![image.png](https://image.3001.net/images/20200511/1589190076_5eb91dbcdb0b1.png!small)Version
3  

版本2已被该版本替换，2019年未观察到版本3的任何新部署，技术细节方面它比版本2更为先进。

与第二版相比，第一阶段的植入程序混淆更为彻底。它使用与版本2类似的方式来解密有效负载，加密内容被分为多个10256字节以下的文件以及一个加密配置文件，其中包含有效载荷解密详细信息。

![image.png](https://image.3001.net/images/20200511/1589190408_5eb91f08aba2a.png!small)解密流程：

![image.png](https://image.3001.net/images/20200511/1589190447_5eb91f2f915ac.png!small)

每个版本3负载都具有相同的程序包名称“com.android.process.gpsp”，使用用于签署某些版本2的相同证书签名。在版本3中找到的唯一版本标记是“10.2.98”。

## 传播方式

攻击者主要通过应用市场进行传播。除了已向Google报告的com.zimice.browserturbo和com.physlane.opengl之外，还观察到其他一些传播痕迹，表明过去有许多恶意应用程序已部署到Google
Play，但现已被删除。

![image.png](https://image.3001.net/images/20200511/1589190690_5eb92022dd38d.png!small)![image.png](https://image.3001.net/images/20200511/1589190703_5eb9202f4cc7f.png!small)确定了多个第三方市场，这些市场与Google
Play不同，它们仍然托管恶意应用程序：

> <https://apkcombo>[.]com  
> <https://apk>[.]support/  
> <https://apkpure>[.]com  
> <https://apkpourandroid>[.]com  
>  
>

![image.png](https://image.3001.net/images/20200511/1589190766_5eb9206e6ee7c.png!small)几乎每种恶意软件部署案例中，攻击者都试图利用伪造用户许可协议（EULA）创建Github开发帐户。  

![image.png](https://image.3001.net/images/20200511/1589190877_5eb920dded846.png!small)![image.png](https://image.3001.net/images/20200511/1589190890_5eb920eaca65f.png!small)在调查中发现攻击者上传的初始版本不包含任何恶意有效负载，
但是后续版本中包含恶意有效负载或其他恶意代码。  

![image.png](https://image.3001.net/images/20200511/1589190991_5eb9214f2c753.png!small)

## 基础设施

在分析С2服务器基础结构时快速确定了多个与先前相似的域，但未链接到任何已知的恶意样本。

![image.png](https://image.3001.net/images/20200511/1589191039_5eb9217f304b6.png!small)![image.png](https://image.3001.net/images/20200511/1589191056_5eb92190e6e02.png!small)发现可以IP：188.166.203[.]57：

##
![image.png](https://image.3001.net/images/20200511/1589191139_5eb921e3c4443.png!small)受害者分布

2016年开始观察到印度，越南，孟加拉国，印度尼西亚等地的Android设备受到攻击。

![image.png](https://image.3001.net/images/20200511/1589191219_5eb9223309c51.png!small)

还在尼泊尔，缅甸和马来西亚进行了多次侦查，南亚是该组织的最大目标地区。除了常见的诱饵应用程序（例如Flash插件，清洁程序和更新程序）以外，还有专门针对越南的应用程序。

##
![image.png](https://image.3001.net/images/20200512/1589241749_5eb9e79562918.png!small)关联分析

研究人员分析了PhantomLance与OceanLotus APT活动的关联。

### OceanLotus Android  

2019年5月，[Antiy Labs](https://www.antiy.net/p/analysis-of-the-attack-of-mobile-devices-by-oceanlotus/)发布了Android恶意软件活动报告，声称该活动与OceanLotus
APT有关，样本最早追踪可追溯到2014年12月。受此活动影响的大多数用户位于越南，只有少数人位于中国。主要感染媒介是第三方网站上托管的恶意应用程序链接，这些链接通过SMS或电子邮件进行分发。

![image.png](https://image.3001.net/images/20200512/1589242076_5eb9e8dcbac05.png!small)

最新恶意软件下载发生在2017年12月，2018年观察到少量活动，但从托管恶意软件的数量和检测数量来看，主要活动时间是在2014年末至2017年。

对报道中OceanLotus
Android（MD5：0e7c2adda3bc65242a365ef72b91f3a8）和未混淆的（可能是开发人员版本）PhantomLance有效负载v3（MD5：243e2c6433833815f2ecc6640）进行了代码结构比较：  

###
![image.png](https://image.3001.net/images/20200512/1589242312_5eb9e9c89af99.png!small)![image.png](https://image.3001.net/images/20200512/1589242338_5eb9e9e268273.png!small)OceanLotus
macOS后门  

对2018年初macOS有效负载（MD5：306d3ed0a7c899b5ef9d0e3c91f05193）进行分析，并将其与Android恶意软件的代码模式进行关联比较。发现七个主要类别中有三个具有相同的名称和相似的功能：“Converter”,
“Packet” and “Parser”.  

###
![image.png](https://image.3001.net/images/20200512/1589242693_5eb9eb45c0661.png!small)相似性分析

大多数OceanLotus恶意软件使用三台不同C2服务器。  

![image.png](https://image.3001.net/images/20200512/1589242826_5eb9ebcad153b.png!small)攻击者对越南十分感兴趣，PhantomLance和OceanLotus的基础设施存在重叠，Android与MacOS后门之间代码存在相似性。

![image.png](https://image.3001.net/images/20200512/1589243008_5eb9ec8010270.png!small)  

## IOCs

### PhantomLance

> HEUR:Backdoor.AndroidOS.PhantomLance.*  
>
>
> HEUR:Trojan-Dropper.AndroidOS.Dnolder.*

### Android campaign linked to OceanLotus (2014-2017)

> HEUR:Trojan.AndroidOS.Agent.eu  
>
>
> HEUR:Trojan.AndroidOS.Agent.vg
>
> HEUR:Trojan-Downloader.AndroidOS.Agent.gv

### macOS campaign linked to OceanLotus

> HEUR:Backdoor.OSX.OceanLotus.*  
>

### MD5

 ** _PhantomLance malware_**

> 2e06bbc26611305b28b40349a600f95c  
>
>
> b1990e19efaf88206f7bffe9df0d9419
>
> 7048d56d923e049ca7f3d97fb5ba9812
>
> e648a2cc826707aec33208408b882e31
>
> 3285ae59877c6241200f784b62531694
>
> 8d5c64fdaae76bb74831c0543a7865c3
>
> 6bf9b834d841b13348851f2dc033773e
>
> 0d5c03da348dce513bf575545493f3e3
>
> 0e7c2adda3bc65242a365ef72b91f3a8
>
> a795f662d10040728e916e1fd7570c1d
>
> d23472f47833049034011cad68958b46
>
> 8b35b3956078fc28e5709c5439e4dcb0
>
> af44bb0dd464680395230ade0d6414cd
>
> 65d399e6a77acf7e63ba771877f96f8e
>
> 79f06cb9281177a51278b2a33090c867
>
> b107c35b4ca3e549bdf102de918749ba
>
> 83cd59e3ed1ba15f7a8cadfe9183e156
>
> c399d93146f3d12feb32da23b75304ba
>
> 83c423c36ecda310375e8a1f4348a35e
>
> 94a3ca93f1500b5bd7fd020569e46589
>
> 54777021c34b0aed226145fde8424991
>
> 872a3dd2cd5e01633b57fa5b9ac4648d
>
> 243e2c6433815f2ecc204ada4821e7d6
>
>  _ **PhantomLance payload-free versions**_
>
> a330456d7ca25c88060dc158049f3298  
>
>
> a097b8d49386c8aab0bb38bbfdf315b2
>
> 7285f44fa75c3c7a27bbb4870fc0cdca
>
> b4706f171cf98742413d642b6ae728dc
>
> 8008bedaaebc1284b1b834c5fd9a7a71
>
> 0e7b59b601a1c7ecd6f2f54b5cd8416a

 ** _Android campaign 2014-2017_**

> 0e7c2adda3bc65242a365ef72b91f3a8  
>
>
> 50bfd62721b4f3813c2d20b59642f022
>
> 5079cb166df41233a1017d5e0150c17a
>
> 810ef71bb52ea5c3cfe58b8e003520dc
>
> c630ab7b51f0c0fa38a4a0f45c793e24
>
> ce5bae8714ddfca9eb3bb24ee60f042d
>
> d61c18e577cfc046a6252775da12294f
>
> fe15c0eacdbf5a46bc9b2af9c551f86a
>
> 07e01c2fa020724887fc39e5c97eccee
>
> 2e49775599942815ab84d9de13e338b3
>
> 315f8e3da94920248676b095786e26ad
>
> 641f0cc057e2ab43f5444c5547e80976

### Domains and IP addresses

 ** _PhantomLance_**

> mine.remaariegarcia[.]com  
>
>
> egg.stralisemariegar[.]com
>
> api.anaehler[.]com
>
> cloud.anofrio[.]com
>
> video.viodger[.]com
>
> term.ursulapaulet[.]com
>
> inc.graceneufville[.]com
>
> log.osloger[.]biz
>
> file.log4jv[.]info
>
> news.sqllitlever[.]info
>
> us.jaxonsorensen[.]club
>
> staff.kristianfiedler[.]club
>
> bit.catalinabonami[.]com
>
> hr.halettebiermann[.]com
>
> cyn.ettebiermahalet[.]com

 ** _Android campaign 2014-2017_**

> mtk.baimind[.]com  
>
>
> ming.chujong[.]com
>
> mokkha.goongnam[.]com
>
> ckoen.dmkatti[.]com
>
> sadma.knrowz[.]com
>
> itpk.mostmkru[.]com
>
> aki.viperse[.]com
>
> game2015[.]net
>
> taiphanmemfacebookmoi[.]info
>
> nhaccuatui.android.zyngacdn[.]com
>
> quam.viperse[.]com
>
> jang.goongnam[.]com

 ***参考来源：[securelist](https://securelist.com/apt-phantomlance/96772/)，由Kriston编译，转载请注明来自FreeBuf.COM**


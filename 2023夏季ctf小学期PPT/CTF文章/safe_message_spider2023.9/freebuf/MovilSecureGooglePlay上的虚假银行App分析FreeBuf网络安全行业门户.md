## 前言

 **现在，各大银行都在通过[银行App](https://www.juniperresearch.com/press/press-releases/digital-banking-users-to-reach-2-billion)来给用户提供更多的功能，多亏了移动互联网，我们才能够在全球的任何一个角落随时随地去使用银行服务。但是，随着金融技术的不断发展，用户会不断在特定的银行App中寻找某些特殊服务，这也给网络犯罪分子提供了可乘之机。**

![页首配图](https://image.3001.net/images/20181123/1542981259_5bf8068b84afe.png!small)

近期，我们在Google Play上发现了一个名叫Movil
Secure的恶意App，这款App应用了[SMiShing技术](https://redirect.viglink.com/?format=go&jsonp=vglnk_154298093149317&key=0d3176c012db018d69225ad1c36210fa&libId=jotzm3d80102jdmu000DA18ze7d1kb8f26&subId=f9f1a771608a24e84c49a8532e282dc1&cuid=f9f1a771608a24e84c49a8532e282dc1&loc=https%3A%2F%2Fblog.trendmicro.com%2Ftrendlabs-security-intelligence%2Ffake-banking-app-found-on-google-play-used-in-smishing-scheme%2F&v=1&out=https%3A%2F%2Fwww.trendmicro.com%2Fvinfo%2Fus%2Fsecurity%2Fdefinition%2Fsmishing%3F_ga%3D2.127725965.1010876111.1542975212-1815790551.1537522001&title=Fake%20Banking%20App%20Found%20on%20Google%20Play%20Used%20in%20SMiShing%20Scheme%20-%20TrendLabs%20Security%20Intelligence%20Blog&txt=SMiShing)（短信诈骗+网络钓鱼），主要针对的是西班牙语用户。

实际上，Movil Secure是一款伪装成移动令牌服务的虚假银行App，显而易见，它的开发者试图用专业的品牌和复杂的用户界面来诱骗用户认为Movil
Secure是合法的。除此之外，我们还发现了另外三个类似的伪造应用，这三个应用都属于同一名开发者的。目前，Google已经将这些恶意App下架了。

MovilSecure于2018年10月19日上线，并在上线6天内达到了100+的下载量。之所以能够达到这样的下载量，很可能是因为这款App声称和西班牙的一家跨国银行集团（BBVA）有联系。实际上，这家银行一直以技术支持服务而闻名，而且这家公司真正的移动端银行业务App也被认为是[目前业内最好的应用程序之一](https://www.bbva.com/en/bbva-compass-mobile-app-deemed-a-leader-by-javelin-strategy-research-in-two-categories-in-2018-mobile-banking-scorecard/)。

这款伪造App正是利用了BBVA在行业内的优势，并通过伪装成银行移动令牌服务来感染用户手机，但研究人员通过分析后发现，Movil
Secure其实并不具备相应的功能。

![Movil
Secure](https://image.3001.net/images/20181123/1542981265_5bf80691ded4b.png!small)  

这款恶意软件软件主要针对的是西班牙语用户，它声称自己能够识别BBVA的用户，并为用户提供授权交易服务。但是，研究人员在分析了Movil
Secure的功能和行为之后，表示它其实可以被归类为间谍软件。而且当前版本的Movil Secure架构非常简单，这可能意味着它只是研究人员在Google
Play上发布的一个实验性应用程序。

## 感染&攻击机制

当Movil
Secure首次启动时，它会收集设备的识别信息，例如设备ID、操作系统版本和国家代码等等。接下来，它会将这些信息发送至远程恶意C2服务器，这一切都会在后台悄悄完成，用户是不会在手机屏幕上察觉到任何异样的。

![感染&攻击机制](https://image.3001.net/images/20181123/1542981277_5bf8069d44ce3.png!small)

当我们访问这个远程恶意C2服务器时，我们看到了一个简单的登录页面，这表明攻击者专门开发了一个完整的管理系统来收集、组织和分析捕捉到的用户数据。更重要的是，攻击者很有可能会利用这些数据来发动一场大规模的网络攻击。

![大规模的网络攻击](https://image.3001.net/images/20181123/1542981282_5bf806a2ef75c.png!small)

当然了，它要收集的数据可不仅仅只有设备标识信息而已，它还会获取目标设备的SMS短信以及手机号。研究人员在对其恶意代码进行了分析之后，发现了这款恶意软件（间谍软件）的主要目的。如下图所示，当受感染设备收到了一条新的短信时，它会将短信的发送者（手机号）以及相应的内容发送至远程C2服务器。这种类型的信息是非常有价值的，因为在目前的银行交易系统中，绝大部分都是利用短信验证码的形式来授权银行交易的。

![授权银行交易](https://image.3001.net/images/20181123/1542981289_5bf806a95c48e.png!small)

目前，这款恶意软件的开发者已经开始尝试将收集到的数据使用到SMiShing恶意活动中了。

![使用到SMiShing恶意活动中了](https://image.3001.net/images/20181123/1542981297_5bf806b102b6a.png!small)  

仔细分析了恶意App的开发者详情之后，你会发现他的名下还有三款类似的恶意App。Evo和Bankia都是在西班牙非常受欢迎的银行，而Compte de
Credit跟任何一家大型金融机构都没有一点关系。这三款恶意App都是在10月19日发布的，发布时间跟MovilSecure是一样的。研究人员通过分析后发现，这些恶意App的运行机制跟Movil
Secure其实是一样的，它们都会收集受感染设备上的设备标识信息以及SMS短信数据，然后将它们发送至远程C2服务器。

![发送至远程C2服务器](https://image.3001.net/images/20181123/1542981304_5bf806b8eca3f.png!small)

## 入侵威胁指标

### SHA256

    
    
    b168e64a02c3aed52b0c6f77a380420dd2495c3440c85a3b7ed99b8ac871d46a
    
    d8018d869254abd6e0b2fb33631fcc56c9f2e355c5d6f40701f71c1a73331cb3
    
    299e1eb8a1f13e1eb77a1c38e5cf7bbdc588db89d4eaad91e7fc95d156d986e5
    
    24e7a8ed726efa463edec2e19ad4796cf4b97755b8fdf06dea4950c175c01f77

### 恶意软件检测名称

    
    
    AndroidOS_FlokiSpy.HRX

### 命令控制服务器

    
    
    hxxps://backup.spykey-floki.org/add.php

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/fake-banking-app-found-on-google-play-used-in-smishing-scheme/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


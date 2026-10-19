曾经有一本书《怎样打飞机》：

![image.png](https://image.3001.net/images/20191211/15760455182903.png!small)

开创了步枪击落飞机的教育先河，14发子弹击落美军战斗机，堪称牛逼。

而如今，各国都开始使用另一种飞机进行敌情侦察，此时，除了使用此前提到过的↓ 激光干扰或无线信号干扰法之外的针对蓝牙连接的无人机外，

现在问世了一种专门针对Wifi连接的无人机的攻击框架。  

废话说到这，下面是正文时间。

## 正文

安全研究人员正在为无人机黑客量身定制一个类似Metasploit的框架。

![image.png](https://image.3001.net/images/20191211/15760456119745.png!small)

该工具的开发者Alexandre D'Hondt和Yannick Pasquazzo在12月5日在伦敦举行的黑帽欧洲会议Blackhat
arsenal阿森纳会议上公开了该框架DroneSploit的进展。

![image.png](https://image.3001.net/images/20191211/15760465558315.png!small)

从PPT来看，他们面向的都是使用Wifi进行连接的无人机，比如手机热点。  

![image.png](https://image.3001.net/images/20191211/15760459263874.png!small)

![image.png](https://image.3001.net/images/20191211/15760466031426.png!small)

其中包括一组模块（基于Aircrack-NG），这些模块使用户可以侵入配置错误的无人机。

如下图所示：  

![image.png](https://image.3001.net/images/20191211/1576046646677.png!small)

![image.png](https://image.3001.net/images/20191211/15760466819816.png!small)

DroneSploit当前支持C-me和Flitt无人机（Hobbico）的模块。其他品牌和型号（包括Parrot和DJI）的新模块正在开发中，并将在不久后添加，大疆厂商要注意啦。

![image.png](https://image.3001.net/images/20191211/15760467394082.png!small)

而他们的最终目标是在尽可能多的无人机模型上收集尽可能多的攻击模块。

![image.png](https://image.3001.net/images/20191211/15760467634106.png!small)

要知道，在Python中创建用于设计类似Metasploit的框架的工具包的底层无疑是该项目中最费力的工作，但最终导致了Sploitkit的发展。

因此他们是基于Sploitkit进行的开发，也就是python版的Metasploit

![image.png](https://image.3001.net/images/20191211/15760468697641.png!small)

> <https://github.com/dhondta/sploitkit>

研究人员说，有了这个软件包，可以很容易地基于社区的分析和研究人员获得的用于测试的无人机为DroneSploit构建新的命令和模块。

![2.png](https://image.3001.net/images/20191211/15760469989215.png!small)

两位开发人员希望鼓励对编程和无人机黑客感兴趣的其他专家为该项目的进一步发展做出贡献，他们认为， **IoT安全研究界非常需要这些** 。

目前市场上最受欢迎的两个无人机品牌DJI和Parrot，虽然有很多开源黑客项目，但它仍然缺乏收集和自动化流程的平台，这也是他们开发这个平台的原因。

两位研究人员还愿意在项目的持续开发中与无人机制造商合作。  

“不幸的是，我们在该项目开始时就可以进行 渗透测试的无人机是Flitt和C-me，它们都是由去年破产的Hobicco制造的，” Pasquazzo说。

“互联网上关于这些模型的信息很少，因此我们从零开始，对该产品进行了重新设计，以发现我们的漏洞，因此无法联系Hobicco提出任何安全补丁。”

他补充说他们买了DJI生产的Tello，该社区拥有更大的社区和一些可利用的漏洞。

大疆，打钱！漏洞即将发到你们邮箱了！  

![3.jpg](https://image.3001.net/images/20191211/15760471859424.jpg!small)

开发不易，虽然不认识这两小哥，但黑鸟还是帮他们打了个星星支持了一下，有研究人机或者IOT安全的老哥可以用起来了。

工程下载链接：  

> <https://github.com/dhondta/dronesploit>

PPT下载链接，教程方法都写在里面了

> <https://github.com/dhondta/dronesploit/blob/master/docs/blackhat-> eu19-arsenal.pdf>

**本文作者：[黑鸟](https://mp.weixin.qq.com/s?__biz=MzAxOTM1MDQ1NA==&mid=2451178552&idx=1&sn=080ac5e9a0b9f1cbf82a699ecd5f3b38&chksm=8c26f2e1bb517bf7676c9a27d0f468d0322fa4f7d91b55999173f36269fea3243cb34b3cd1f6&scene=0&xtrack=1&key=c99d2c1a9cca8413153db3b8383c4e1c875fa6178539a7110672cb3762edd009897405017a981553ffda9bd05205ae99c13b0ab49d63b6d01df85f7cbb82ae843d98bad196337480a9b892bf768dd082&ascene=1&uin=MjUxNDA2NDk1&devicetype=Windows+10&version=62070158&lang=zh_CN&exportkey=ASnq5SRwPACATlib3o1hk8I%3D&pass_ticket=1Lf6Vpnw8eDyu2SraBw8gZbOqTNCYB2CQOhAWX4jNZ8%3D)，转载请注明来自FreeBuf**


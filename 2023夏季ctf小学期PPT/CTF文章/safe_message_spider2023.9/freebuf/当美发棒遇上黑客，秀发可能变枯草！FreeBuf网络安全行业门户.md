**据渗透测试服务商Pen Test Partners 称，其安全人员已成功攻破美发仪器制造商Glamoriser公司的直发棒。**  

来自英国的Glamoriser公司称其研发了“世界上第一款蓝牙直发棒”，用户可以通过蓝牙将直发棒连接到APP，快速设置温度和模式，并在蓝牙范围内开关直发棒。

![1563249969_5d2d4d3124309.jpg!small](https://image.3001.net/images/20190716/1563249969_5d2d4d3124309.jpg!small)

图源：Glamoriser官网

然而，英国消防部门的一项在线调查显示，直发棒在全英国造成多达65万起房屋火灾。甚至，三分之一的直发棒使用者有不同程度的烧伤，可见直发棒的不当使用已成为严重的安全隐患。

这引起了安全公司Pen Test Partners 的注意：蓝牙连接的直发棒是否更具危险性，是否能被黑客入侵并控制？

# 答案是：可以！

实际上这款蓝牙直发棒的APP非常简单：设置温度和持续时间

![https://www.pentestpartners.com/content/uploads/2019/03/glamo13.png?x38147](https://image.3001.net/images/20190716/1563249982_5d2d4d3ed0dbc.png!small)

图源：Pen Test Partners

研究证明，攻击者可在蓝牙范围内发送恶意命令，远程控制直发棒，更改其温度和持续时间。
如果有人在120°C下使用直发棒并设置持续时间5分钟，攻击者则可以将其更改为235°C（超过纸张燃点！）、持续时间20分钟。

![https://www.pentestpartners.com/content/uploads/2017/03/bed-fire.png?x38147](https://image.3001.net/images/20190716/1563249989_5d2d4d457b54f.png!small)

图源：Pen Test Partners

Pen Test
Partners研究人员表示：“如果使用不当，直发棒很容易引起皮肤灼伤和火灾。我们已经证明可以篡改温度，因此即使用户安全使用，黑客也可能降低它们的安全性。”

“对于制造商来说，加入蓝牙配对/绑定功能来防止这种情况发生是很容易的。只要按下按钮将直发棒置于配对模式就可以解决这个问题。否则，则将自己置于火灾的隐患当中。”

由于直发棒是蓝牙连接，为了利用这一漏洞，恶意的攻击者只能在一定范围内行动，Tripwire安全研究高级主管Lamar Bailey
表示，“黑客的攻击概率很低，除非你的兄弟姐妹或邻居恶作剧或报复你。如果你有这个直发棒，在拉直头发前，请善待任何距离你约10米范围内的人。”

为了降低这些蓝牙设备受到威胁的风险，ForgeRock全球业务和企业发展高级副总裁BenGoodman
表示，Glamoriser必须对安全建立和维护物联网设备的整个生命周期负责。

>
> “物联网项目往往优先考虑连接性和数据消耗，最后才考虑安全性和隐私因素。物联网会持续存在，连接的设备、服务和用户的身份及其相关凭证必须在多个连接的生态系统中获得信任和可用，以防止中间人以及其他类型的攻击。”

参考资料：

[《HackedHair Straightener Could Set a Fire》](https://www.infosecurity-magazine.com/news/hacked-hair-straightener-could-set/)

[《Burningdown the house with IoT》](https://www.pentestpartners.com/security-blog/burning-down-the-house-with-iot/)

  

本文由 **安数网络** 编译。部分图片来自网络，如涉及侵权，请及时与我们联系，我们会在第一时间删除或处理侵权内容。

及时掌握网络安全态势 尽在[ **傻蛋联网设备搜索系统**](https://www.anshuw.com/)

【网络安全监管部门】免费试用→→[ **点击申请**](https://www.anshuw.com/freeuse)

更多安全资讯请关注：

微信公众号 **安数网络** ；新浪微博 **@傻蛋搜索**

  

#  

  


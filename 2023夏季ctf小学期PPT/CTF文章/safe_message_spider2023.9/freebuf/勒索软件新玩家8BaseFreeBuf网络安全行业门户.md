尽管 8Base 勒索软件团伙在 2023 年的活动已经大幅增加，但仍不广为人知。该团伙也是双重勒索的使用者，多种手段并用逼迫受害者支付赎金。8Base
最近跨行业攻击了很多目标，但攻击者的身份与潜在动机仍然不明。

![image.png-298.4kB](https://image.3001.net/images/20230710/1688998072_64ac10b8e44d75dcad05d.png!small)数据泄露网站

## 8Base 勒索软件

8Base 是一个勒索软件团伙，自从 2022 年 3 月以来一直保持活跃，且在 2023 年 6
月攻击大幅增强。攻击者在泄漏数据的网站上，提供了各种常见问题的解决方案与多种联系方式。另一个有趣的地方是 8Base
团伙的沟通方式与另一个已知的勒索软件组织 RansomHouse 十分类似。

![image.png-229.7kB](https://image.3001.net/images/20230710/1688998074_64ac10ba35c358bf5b41d.png!small)攻击活动趋势

数据泄露的网站中提供了两个联系方式：

  * Telegram：https[:]//t.me/eightbase
  * Twitter：@8BaseHome

![image.png-882.6kB](https://image.3001.net/images/20230710/1688998075_64ac10bb53936f39cb323.png!small)攻击者的
Twitter 账号

8Base 勒索软件团伙的目标行业有商业服务、金融、制造与信息技术。

![image.png-222.3kB](https://image.3001.net/images/20230710/1688998076_64ac10bc9111073173acd.png!small)攻击行业分布

尽管 8Base 勒索软件团伙并不一定是一个新出现的攻击团伙，但其最近激增的活动并未引起人们的广泛关注。在过去的一个月内，8Base
也可以排得上最活跃的前两位。除了勒索信息与扩展名为 .8Base 的加密文件外，其实大家对 8Base 勒索软件知之甚少。

![image.png-204kB](https://image.3001.net/images/20230710/1688998077_64ac10bdcf2aa73d87142.png!small)受害者排行

## 到底是谁的勒索？

在发现 8Base 之初，研究人员就注意到其与 RansomHouse 之间存在明显的相似之处。目前，RansomHouse
是否是真正的勒索软件团伙尚有争议。该团伙会购买已经泄露的数据，然后向受害者勒索钱财。

![image.png-900.8kB](https://image.3001.net/images/20230710/1688998079_64ac10bf11b1298b1df7e.png!small)勒索信息

第一个相似之处是利用 Doc2Vec 模型处理勒索信息发现的。8Base 的勒索信息与 RansomHouse 的勒索信息相似度达到 99%，如下所示：

![image.png-607.3kB](https://image.3001.net/images/20230710/1688998081_64ac10c14e236ad330165.png!small)网页相似对比

更加深入地研究后，发现了更多的相似之处：

![image.png-629kB](https://image.3001.net/images/20230710/1688998082_64ac10c27bad3bf2e4960.png!small)服务条款页对比

![image.png-650.9kB](https://image.3001.net/images/20230710/1688998084_64ac10c44d30eac93e603.png!small)服务条款页对比

数据泄露网站的欢迎页面就是从 RandomHouse 的页面复制过来的，服务条款页与常见问题解答页也是如此。

![image.png-2055.4kB](https://image.3001.net/images/20230710/1688998086_64ac10c60e1ced09c0063.png!small)FAQ
页面对比

对比这两个攻击团伙时，存在两个主要的区别。第一个区别是 RansomHouse 会宣传合作伙伴关系并公开招募合作方。

![image.png-619.8kB](https://image.3001.net/images/20230710/1688998087_64ac10c7ae20006f0f4f8.png!small)公开宣传页面

另一个区别是数据泄露页面存在差异，如下所示：

![image.png-1055.6kB](https://image.3001.net/images/20230710/1688998088_64ac10c89c57587bb7170.png!small)二者差异对比

由于二者高度相似，研究人员怀疑 8Base 是否为 RansomHouse 的分支或者模仿者，但是RansomHouse
使用黑市上出售的各种勒索软件进行攻击，并不自行开发，对于 8Base 也未能找到任何勒索软件变种。

![image.png-691.5kB](https://image.3001.net/images/20230710/1688998089_64ac10c9caa768de553b4.png!small)勒索信息对比

![image.png-815.3kB](https://image.3001.net/images/20230710/1688998090_64ac10caea0617820c26e.png!small)勒索信息对比

研究人员发现了两个截然不同的勒索信息：一张与 RansomHouse 相符，另一张与 Phobos 相符。这是否能够说明 8Base 与
RansomHouse 类似，也是用不同的勒索软件进行攻击。那么，8Base 是否为 RansomHouse 的一个分支呢？

### 8Base 与 Phobos

研究人员发现了使用 .8Base 扩展名的 Phobos 勒索软件样本，尚不清楚这是勒索软件的早期版本还是 8Base
使用不同的勒索软件进行攻击。8Base 在攻击中使用 2.9.1 版本的 Phobos 与 SmokeLoader 对勒索软件进行混淆。由于 Phobos
本身就提供 RaaS 服务，攻击者可以根据自身需要对勒索软件进行定制。

![image.png-190.2kB](https://image.3001.net/images/20230710/1688998092_64ac10cc29d27f30baaf7.png!small)文件扩展名对比

尽管 8Base 在加密文件上使用了 .8Base 以示区别，但其他内容仍然沿用 Phobos，包括 ID、电子邮件地址等。

8Base 的样本文件是通过域名 admlogs25[.]xyz 下载而来，该域名似乎与远控工具 SystemBC 存在关联。

## 总结

8Base 正在进行疯狂攻击，目前只能推测其使用几种不同的勒索软件进行攻击。该团伙针对小型企业的攻击十分频繁，一直处于活跃期。

8Base 是否为 Phobos 或者 RandomHouse 的分支还有待观察，但一目了然的是 8Base 与 RansomHouse 几乎相同。

## IOC

> 518544e56e8ccee401ffa1b0a01a10ce23e49ec21ec441c6c7c3951b01c1b19c  
> 5BA74A5693F4810A8EB9B9EEB1D69D943CF5BBC46F319A32802C23C7654194B0  
> 20110FF550A2290C5992A5BB6BB44056  
> 3D2B088A397E9C7E9AD130E178F885FEEBD9688B  
> e142f4e8eb3fb4323fb377138f53db66e3e6ec9e82930f4b23dd91a5f7bd45d0  
> 5d0f447f4ccc89d7d79c0565372195240cdfa25f  
> 9769c181ecef69544bbb2f974b8c0e10  
> C6BD5B8E14551EB899BBE4DECB6942581D28B2A42B159146BBC28316E6E14A64  
> 518544E56E8CCEE401FFA1B0A01A10CE23E49EC21EC441C6C7C3951B01C1B19C  
> AFDDEC37CDC1D196A1136E2252E925C0DCFE587963069D78775E0F174AE9CFE3  
> wlaexfpxrs[.]org  
> admhexlogs25[.]xyz  
> admlogs25[.]xyz  
> admlog2[.]xyz  
> dnm777[.]xyz  
> serverlogs37[.]xyz  
> dexblog[.]xyz  
> blogstat355[.]xyz  
> blogstatserv25[.]xyz

## 参考来源

> [VMware](https://blogs.vmware.com/security/2023/06/8base-ransomware-a-heavy-> hitting-player.html)


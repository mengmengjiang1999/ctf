银行木马 FluBot 正在针对全欧洲发起一场新型诈骗攻击，从欧洲的这头到那头，将窃取数据的恶意软件植入受害者的手机中。

复活节前后，罗马尼亚率先出现了 FluBot
的踪迹。本次攻击使用的诈骗方式与此前相同，都是利用虚假短信，特别是语音消息。安卓用户仍然是攻击的主要目标，但本次攻击中安卓用户与苹果用户受到的诈骗短信数量几乎持平。

## FluBot 的持续攻击

攻击都是利用虚假短信投递恶意链接：

![image.png-105.1kB](https://image.3001.net/images/20220526/1653563898_628f61fa029fe685e2395.png!small)虚假短信

![image.png-73.9kB](https://image.3001.net/images/20220526/1653563898_628f61fa755c83a3fb97e.png!small)虚假短信

![image.png-77kB](https://image.3001.net/images/20220526/1653563898_628f61fad56b73f9ad8e0.png!small)虚假短信

用户如果点击访问恶意链接，将会要求用户允许安装一个未知来源的应用程序。攻击者会声称用户需要安装一个应用程序才能收听语音消息：

![image.png-140.4kB](https://image.3001.net/images/20220526/1653563899_628f61fb47defff64d71f.png!small)安装恶意程序

![image.png-89.8kB](https://image.3001.net/images/20220526/1653563899_628f61fbc0bf7dfbab873.png!small)安装恶意程序

攻击者引诱用户亲手安装了 FluBot 银行木马后，会再督促受害者按照说明给予虚假应用程序对应权限：

![image.png-34.7kB](https://image.3001.net/images/20220526/1653563900_628f61fc4585c0f4c798d.png!small)获取权限

在获取权限后，FluBot 会收集受害者的通信录并通过短信给这些受害者的联系人发送恶意消息，以此进行传播。与此同时，还会将窃取的数据回传到 C&C 服务器。

FluBot 是一个典型的银行木马，主要窃取信用卡与其他凭证信息。攻击者通过恶意软件窃取资金，并且利用受害者的各种账户进行作恶。

FluBot 模仿应用程序的图标列表：

![image.png-46.6kB](https://image.3001.net/images/20220526/1653563900_628f61fc91a02aead2aec.png!small)图标列表

尽管 FluBot 不支持 iOS 平台，但当 iPhone 用户访问恶意链接时会被重定向到钓鱼网站，例如下面这个示例，攻击者引诱用户参与市场调查，从而获取
iPhone 13 大奖。

![image.png-111.1kB](https://image.3001.net/images/20220526/1653563900_628f61fce43e9b69e9490.png!small)诈骗网站

![image.png-306.2kB](https://image.3001.net/images/20220526/1653563901_628f61fd624608fa349c7.png!small)诈骗网站

## 横扫欧洲

从复活节在罗马尼亚开始，Bitdefender 发现了席卷整个欧洲的 FluBot 攻击浪潮，在四月份到达顶峰。

![image.png-184.2kB](https://image.3001.net/images/20220526/1653563902_628f61fe06a6639262b27.png!small)欧洲传播趋势

除罗马尼亚外，芬兰在 FluBot 也疯狂传播。本次攻击中看到了高度本地化的运营，这表明 FluBot
正在投入大量的精力用于扩大攻击范围，无论是平台还是语言。

![image.png-77.1kB](https://image.3001.net/images/20220526/1653563902_628f61fe782cd806a52c2.png!small)芬兰传播趋势

受影响最大的是德国、罗马尼亚、英国、波兰、西班牙、瑞典、奥地利、芬兰和丹麦。而德国与罗马尼亚合计份额达到 69%，是攻击者攻击的重点。

![image.png-199.4kB](https://image.3001.net/images/20220526/1653563902_628f61fee09a91e5d8cb9.png!small)国家分布

尽管很多国家都是在同一时间遭到攻击，但其实攻击峰值仍然是交错开的，攻击者对本地化实际上有持续的规划与考虑。如，罗马尼亚的攻击开始减少时，波兰的攻击开始增加。

![image.png-114.6kB](https://image.3001.net/images/20220526/1653563903_628f61ff813081979f422.png!small)攻击趋势

芬兰与瑞典也是如此：

![image.png-104.1kB](https://image.3001.net/images/20220526/1653563904_628f620017622cff85e55.png!small)攻击趋势

比利时与西班牙也是如此：

![image.png-122.5kB](https://image.3001.net/images/20220526/1653563904_628f620093dac4d258b9d.png!small)攻击趋势

FluBot 似乎专注于在各个国家进行规模较小的、较为独立的、本地化攻击行动。

## 永无止境

尽管已经逮捕了多名涉嫌运营 FluBot 的犯罪分子，但 FluBot 并未偃旗息鼓，而是愈发猖獗。未来，预计 FluBot 还会掀起更大的攻击浪潮。

## 参考来源

> [Bitdefender](https://www.bitdefender.com/blog/labs/new-flubot-campaign-> sweeps-through-europe-targeting-android-and-ios-users-alike/)


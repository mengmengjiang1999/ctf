![](https://image.3001.net/images/20201002/1601570900_5f76085489ed85c74a4e0.jpg!small)

近期，一款名为Mount Locker的新型勒索软件一直处于极度活跃状态。跟其他勒索软件一样，Mount
Locker会在对目标用户的文件进行加密之前，先窃取用户文件，然后再去跟目标用户索要数百万美元的赎金。

从2020年7月底开始，Mount Locker就已经开始针对各个大型企业网络进行渗透攻击，并部署勒索软件。

根据我们从目标用户那里获取到的勒索信息来看，Mount Locker在某些情况下，会直接向受害者索要数百万美金的数据赎金。

下图显示的就是其中一个案例，在这里Mount Locker竟然直接向目标用户索要两百万美金的数据赎金：

![](https://image.3001.net/images/20201002/1601570908_5f76085c1e21351d112ef.jpg!small)

在对目标用户的文件进行加密之前，Mount
Locker还会窃取未加密的文件信息，并威胁目标用户称，如果不按时按量支付数据赎金的话，这些数据就将会被公之于众。

比如说，Mount
Locker会告诉目标用户，他们成功窃取了400GB数据，如果目标用户不支付赎金的话，他们就会联系目标用户在行业内的其他竞争者、新闻媒体、电视台和报纸等，然后将这些数据直接提供给他们。

最终，如果目标用户没有支付赎金，那么他们的数据将会被公开到一个勒索软件数据泄露网站上：

![](https://image.3001.net/images/20201002/1601570915_5f7608634fed9517d4856.jpg!small)

这个数据泄露网站目前列出了四个目标用户，但只公布了其中一家的泄露文件。

实际上，若不是[
_MalwareHunterTeam_](https://twitter.com/malwrhunterteam?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor)近期发现了一个Mount
Locker的样本，否则我们也没有机会去更加深入地了解Mount Locker勒索软件活动的详细信息。

研究人员[ _Michael
Gillespie_](https://twitter.com/demonslay335)在对该勒索软件进行了分析之后，并告知BleepingComputer，Mount
Locker使用了ChaCha20来对目标用户的文件进行加密，并且使用了一个嵌入的RSA-2048公共密钥来对加密密钥进行加密。

从我们的分析结果来看，当Mount Locker在进行文件加密时，勒索软件将会添加一个.ReadManual.ID文件后缀。比如说，1.doc在被Mount
Locker加密之后，将会被重命名为1.doc.ReadManual.C77BFF8C，被加密的文件夹内容具体如下图所示：

![](https://image.3001.net/images/20201002/1601570923_5f76086b49d831c6d9eaf.jpg!small)

勒索软件接下来将会在目标设备的注册表中注册该文件扩展，这样一来，当目标用户点击一个被加密的文件之后，将会自动加载勒索信息：

HKCU\Software\Classes\\.C77BFF8C\shell\Open\command\ @="explorer.exe
RecoveryManual.html"

勒索信息文件名为RecoveryManual.html，其中包含了关于访问Tor站点来跟勒索软件攻击者取得联系的方式：

![](https://image.3001.net/images/20201002/1601570931_5f7608736e165639dbd47.jpg!small)

这个Tor网站其实就是一个聊天服务，在这里，目标用户可以跟攻击者针对数据赎金进行讨价还价，或询问其他一些信息。

不幸的是，这款勒索软件是安全的，因此我们目前还无法免费恢复目标用户被加密的文件。


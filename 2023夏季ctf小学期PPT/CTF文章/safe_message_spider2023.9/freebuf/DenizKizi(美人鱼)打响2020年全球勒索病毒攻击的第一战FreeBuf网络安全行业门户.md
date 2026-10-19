**2019年已经过去了，在过去的一年时间里，各种勒索病毒运营团伙针对全球各国的企事业单位，大中小型企业不断发起网络攻击，全球几乎每天都有被勒索病毒攻击的新闻被曝光，勒索病毒攻击成为了2019年网络安全的最大威胁之一。**

深信服安全团队在过去的一年里跟踪分析了多款新型的勒索病毒，比如2019年出现的几款流行的勒索病毒:Sodinokibi勒索病毒、Phobos勒索病毒、Maze勒索病毒、Buran勒索病毒、MegaCortex勒索病毒等，近期深信服安全团队跟踪观察到一款新型的勒索病毒Deniz
Kızı(美人鱼)，这款新型的勒索病毒打响了2020年全球勒索病毒攻击的第一。

Deniz Kizi勒索病毒最早于2019年12月17日，被国外安全研究人员公布在相关论坛上，如下所示：

![](https://image.3001.net/images/20200216/1581823261_5e48b51d4e682.png!small)

2019年12月20日，该勒索病毒再次被发现，并公布在论坛上，如下所示：

![](https://image.3001.net/images/20200216/1581823284_5e48b5346a34d.png!small)

研究人员指出该勒索病毒运营团队其它几个家族变种还有KesLan、MaMo434376、MZRevenge等勒索病毒,同时专业的勒索病毒信息收集网站id-ransomware也迅速收录了此勒索病毒的相关信息，如下所示：

![](https://image.3001.net/images/20200216/1581823294_5e48b53e14e5a.png!small)

该勒索病毒目前主要是针对使用英语和土耳其语的用户进行攻击，但不排除些勒索病毒未来会在全球范围内进行传播。

详细分析

Deniz_Kizi(美人鱼)勒索病毒在不到一个月的时间里，出现了多次变种版本，2019年12月17日，最初始的版本是一个使用NET语言编写的下载器，如下所示：

![](https://image.3001.net/images/20200216/1581823307_5e48b54b317b2.png!small)

该下载器会修改各种Windows的安全策略注册表项，然后从远程服务器下载Deniz_Kizi勒索病毒母体，并执行，如下所示：

![](https://image.3001.net/images/20200216/1581823316_5e48b5546e1a0.png!small)

下载勒索病毒的服务器URL地址：

hxxps://anonymousfiles[.]io/f/svchost_3qrDPzx.exe

下载回来的勒索病毒样本，采用Delphi语言进行编写，VMP加壳处理，如下所示：

![](https://image.3001.net/images/20200216/1581823324_5e48b55c1c78b.png!small)

此勒索病毒加密的文件后缀列表，如下所示：

![](https://image.3001.net/images/20200216/1581823331_5e48b563bb628.png!small)

在内存中解密出来的勒索病毒提示信息，如下所示：

![](https://image.3001.net/images/20200216/1581823339_5e48b56bec9f1.png!small)

此勒索病毒加密后的文件后缀名为Deniz_Kizi，如下所示：

![](https://image.3001.net/images/20200216/1581823348_5e48b574ef40f.png!small)

生成的勒索提示信息文件Please Read Me!!!.hta，内容如下所示：

![](https://image.3001.net/images/20200216/1581823358_5e48b57e89093.png!small)

![](https://image.3001.net/images/20200216/1581823365_5e48b5851cb68.png!small)

黑客的邮箱地址：

[ _yardimail1@aol.com_](mailto:yardimail1@aol.com)

[ _yardimail2@aol.com_](mailto:yardimail2@aol.com)

2019年12月20日，发现其变种版本，名称为Konyali_Zula_Hack_V4_2019_protected.exe，采用VC++编写的外壳程序对核心代码进行加密处理，如下所示：

![](https://image.3001.net/images/20200216/1581823373_5e48b58d1a1ea.png!small)

通过动态调试，解密出里面的核心数据，如下所示：

![](https://image.3001.net/images/20200216/1581823381_5e48b59577696.png!small)

再次解密得到核心代码，如下所示：

![](https://image.3001.net/images/20200216/1581823390_5e48b59ee539e.png!small)

执行到解密出来的核心代码，如下所示：

![](https://image.3001.net/images/20200216/1581823400_5e48b5a84ce58.png!small)

核心代码会在临时目录下生成svchost.exe程序，然后启动svchost.exe程序，释放的svchost.exe程序也是使用VMP加壳处理的，与2019年12月17日捕获的样本下载的Deniz
Kizi勒索病毒一样，脱壳之后，可以看到勒索病毒的核心代码中勒索提示信息，如下所示：

![](https://image.3001.net/images/20200216/1581823410_5e48b5b2b5ec3.png!small)

这个变种与此前2019年12月17日发现的变种一样，只是使用了更隐蔽的免杀和加载方式

2020年1月8日，发现了这款勒索病毒最新的变种，采用Delphi语言进行编写，MPRESS(2.19)加壳处理，脱壳之后如下所示：

![](https://image.3001.net/images/20200216/1581823420_5e48b5bc085b7.png!small)

此最新的勒索病毒外壳程序，与2019年12月17日第一版那个NET编写的下载器程序一样，

同样会修改Windows安全策略注册表项，如下所示：

![](https://image.3001.net/images/20200216/1581823428_5e48b5c43d96a.png!small)

在临时目录下生成svchost.exe程序，并读取程序资源数据，将资源的数据写入到临时目录下的svchost.exe，随后启动该文件，如下所示：

![](https://image.3001.net/images/20200216/1581823437_5e48b5cde277d.png!small)

临时目录下生成的svchost.exe，仍然采用Delphi语言进行编写，MPRESS(2.19)加壳处理，

脱壳之后，就是Deniz_Kize勒索病毒核心代码，结束相关进程，删除磁盘卷影幅本等，如下所示：

![](https://image.3001.net/images/20200216/1581823447_5e48b5d798b81.png!small)

生成勒索提示信息文件，如下所示：

![](https://image.3001.net/images/20200216/1581823456_5e48b5e02b187.png!small)

最新版的变种，加密后的文件后缀仍然为Deniz_Kizi，如下所示：

![](https://image.3001.net/images/20200216/1581823463_5e48b5e74cbf2.png!small)

最新版的勒索提示信息文件名为土耳其语Lütfen Beni Oku!!!.log(请读我)，内容如下所示：

![](https://image.3001.net/images/20200216/1581823471_5e48b5ef0f5e4.png!small)

![](https://image.3001.net/images/20200216/1581823478_5e48b5f63d75b.png!small)

同时最新版的Deniz_Kizi勒索病毒会修改桌面背景图片，如下所示：

![](https://image.3001.net/images/20200216/1581823485_5e48b5fd74d54.png!small)

黑客的邮箱地址与2019年12月17日第一版使用同样的邮箱地址：

> [_yardimail1@aol.com_](mailto:yardimail1@aol.com)

从上面的分析可出得出这款最新的版本就是此前Deniz_Kizi勒索病毒的最新变种样本，在一个月左右的时间里，黑客从2019年12月17日最开始使用下载器程序下载VMP加壳的勒索病毒样本，然后在2019年12月20日使用一个VC++外壳程序封装另一个加壳的程序，再释放使用VMP加壳的勒索病毒，2019年1月8日黑客使用MPRESS加壳外壳程序，然后再释放使用MPRESS加壳的勒索病毒，短短一个月的时间里，黑客组织不断在变换加壳手法，使用各种免杀技术释放加载核心代码，可见此勒索病毒背后的运营团队对这些勒索病毒正在持续的运营和更新，未来这款勒索病毒会不会在全球范围内变的流行起来，需要持续关注。

2019年勒索病毒的巨大利润一定会带来2020年更多的黑客组织加入到使用勒索病毒攻击的犯罪活动当中，2020年一定会有更多新型的勒索病毒出现，同时黑客的攻击手法和技术也会越来越强，攻击的目标也会越来越有针对性，勒索病毒仍将是网络安全的最大威胁之一，必竟一年几百亿美元的市场，全球各大黑客组织肯定不会放弃这块“肥肉”。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**


**CrySiS勒索病毒，又称Dharma，首次出现是在2016年，2017年5月此勒索病毒万能密钥被公布之后，之前的样本可以解密，导致此勒索病毒曾消失了一段时间，不过随后又马上出现了它的一款最新的变种样本，加密后缀为java，通过RDP暴力破解的方式进入受害者服务器进行加密勒索，此勒索病毒加密算法采用AES+RSA方式进行加密，导致加密后的文件无法解密，在最近一年的时间里，这款勒索病毒异常活跃，变种已经达到一百多个，近日国外安全研究人员发现这款勒索病毒的最新的变种，与以往变种不一样，这款最新的变种使用NET语言进行编写，加密后的文件后缀为kharma，之所以采用NET语言进行编写，可能也是为了逃避杀毒软件的检测**

安全研究人员公布的最新的CrySiS勒索病毒，如下所示：

![](https://image.3001.net/images/20191125/1574693673_5ddbeb29e43ec.png!small)

从app.any.run上下载到相应的样本，通过分析发现这个样本仅仅是外壳程序，外壳程序使用了大量的sleep函数，如下所示：

![](https://image.3001.net/images/20191125/1574693689_5ddbeb392c9e5.png!small)

获取加密数据的密钥，如下所示：

![](https://image.3001.net/images/20191125/1574693702_5ddbeb46abe3d.png!small)

解密出来的密钥，如下所示：

![](https://image.3001.net/images/20191125/1574693716_5ddbeb541111e.png!small)

通过密钥对程序资源中的数据进行解密，如下所示：

![](https://image.3001.net/images/20191125/1574693727_5ddbeb5ff1b9e.png!small)

解密出CrySiS最新变种的核心代码，如下所示：

![](https://image.3001.net/images/20191125/1574693745_5ddbeb71d05c8.png!small)

将解密出来的程序DUMP下来，进行查壳分析，发现核心代码使用Confuser进行加壳处理，如下所示：

![](https://image.3001.net/images/20191125/1574693762_5ddbeb82422fe.png!small)

导致代码混淆无法分析查看，如下所示：

![](https://image.3001.net/images/20191125/1574693773_5ddbeb8ddd217.png!small)

对核心代码进行脱壳，去混淆处理之后，如下所示：

![](https://image.3001.net/images/20191125/1574693786_5ddbeb9a9966d.png!small)

此勒索病毒会进行区域判断，如果为如下区域：

> 0419(LANG_RUSSIAN 俄语)
>
> 0422(LANG_UKRAINIAN 乌克兰)
>
> 0423(LANG_BELARUSIAN 白俄罗斯)

则不进行加密，直接退出，如果不为以上区域，则遍历磁盘文件进行加密，如下所示：

![](https://image.3001.net/images/20191125/1574693800_5ddbeba8a98e3.png!small)

加密后的文件后缀为kharma，与这款勒索病毒的名称(Dharma)只差一个字母，如下所示：

![](https://image.3001.net/images/20191125/1574693813_5ddbebb5a4255.png!small)

生成的勒索提示信息文件RETURN FILES.txt，内容如下所示：

![](https://image.3001.net/images/20191125/1574693827_5ddbebc3024d5.png!small)

弹出勒索提示信息框，如下所示：

![](https://image.3001.net/images/20191125/1574693839_5ddbebcfa0e71.png!small)

这款新型的CrySiS(Dharma)勒索病毒与以往CrySiS勒索病毒不同，采用了NET语言进行编写，以逃避部分杀毒软件的检测，黑客的邮件地址为：

> teammarcy10@cock.li
>
> justbtcwillhelpu@firemail.cc

发邮箱名称也很有趣：just btc will help u!

针对企业的勒索病毒攻击越来越多了，具有很强的针对性，攻击手法也是多种多样，旧的勒索病毒不断变种，新型的勒索病毒又不断出现，全球每天都有勒索病毒的变种被发现，同时每天都有不同的企业被勒索病毒攻击，真的是数不甚数，随着BTC等虚拟货币的流行，未来勒索病毒的攻击还会持续增多，而且后面可能会慢慢转向针对不同的平台进行攻击，勒索病毒已经成为了全球网络安全最大的威胁。

 ***本文作者：熊猫正正，转载请注明来自FreeBuf.COM**


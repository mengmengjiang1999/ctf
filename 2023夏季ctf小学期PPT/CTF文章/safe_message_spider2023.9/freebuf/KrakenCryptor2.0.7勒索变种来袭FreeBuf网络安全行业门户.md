## 前言

**近日，深信服安全团队在分析安全云脑全网威胁数据时，发现了一个在国内出现的新勒索家族KrakenCryptor，发现版本为KrakenCryptor2.0.7。该版本为目前发现的最新版本，且从10月22号以来，陆陆续续有客户通过安全云脑对该样本进行检测。该勒索软件最新版本使用RSA+AES加密算法，加密后缀也随机生成。**

## 详细分析

1、样本是用.net框架编写的，并且样本经过混淆，如图所示：

![样本经过混淆](https://image.3001.net/images/20181102/1541134357_5bdbd81530632.png!small)

2、将样本去混淆，便开始对它的研究。跟一般勒索软件类似，该版本也会给受害者设定一个缴纳赎金的时限，超过一个周以后就会涨价。

如图所示，这是给受害者的收费计时，不过并未在图形界面上展示，且这个一周涨价算的是自然周，而不是根据受害者被加密以后开始算。

![缴费（勒索）倒计时](https://image.3001.net/images/20181102/1541134375_5bdbd827788e2.png!small)

缴费（勒索）倒计时

3、样本会首先解密出一些关于加密的信息，比如，家族、版本、技术支持邮箱等。

![家族版本号](https://image.3001.net/images/20181102/1541134389_5bdbd8353e2f2.png!small)

家族版本号

![加密的密钥长度信息](https://image.3001.net/images/20181102/1541134397_5bdbd83dda9d3.png!small)

加密的密钥长度信息

KrakenCryptor支持加密的文件后缀，一共有422种。下图为部分文件后缀。

![支持加密的文件后缀](https://image.3001.net/images/20181102/1541134408_5bdbd8486457c.png!small)

支持加密的文件后缀

4、样本会通过<https://ipinfo.io>网站来确认受害者IP的位置：

![收集受害者IP的物理位置](https://image.3001.net/images/20181102/1541134418_5bdbd8526bea6.png!small)

收集受害者IP的物理位置

5、收集受害者系统版本、mac地址、本地磁盘信息，并生成RSA和AES密钥：

![生成加密密钥](https://image.3001.net/images/20181102/1541134429_5bdbd85d551ad.png!small)

生成加密密钥

6、获取受害者的默认输入法，对特定默认输入法进行免疫（不加密）。

![获取默认输入法](https://image.3001.net/images/20181102/1541134440_5bdbd8686707c.png!small)

获取默认输入法

![免疫输入法](https://image.3001.net/images/20181102/1541134449_5bdbd871c9b64.png!small)

免疫输入法

获取系统语言，对特定语言进行免疫。目前免疫的国家有：

> 亚美尼亚（AM），阿塞拜疆（AZ），白俄罗斯（BY），爱沙尼亚（EE），格鲁吉亚（GE），伊朗（IR），吉尔吉斯坦（KG），立陶宛（
> LT），摩尔多瓦（MD），俄罗斯（RU），塔吉克斯坦（TJ），乌克兰（UA） ， 乌兹别克斯坦（UZ） ，
> 土库曼斯坦(TM)，叙利亚(SY)，拉脱维亚(LV)，哈萨克斯坦（KZ）。

![免疫国家](https://image.3001.net/images/20181102/1541134459_5bdbd87b9da9d.png!small)

免疫国家

7、注册表项，新增一个WordLoad的键，用来作为加密记录。如果Wordload的值为1，就退出。

![注册表项](https://image.3001.net/images/20181102/1541134468_5bdbd8846ac9c.png!small)

注册表项

8、如果不是在免疫国家列表当中，那么接下来就要走入加密流程了。样本会向<https://2no.co/2SVJa5>这个URL发送自己的IP物理地址。由于这个URL是个短连接，还原以后是<https://www.bleepingcomputer.com/>，bleepingcomputer是一个提供安全技术和信息的网站。

![走入加密流程](https://image.3001.net/images/20181102/1541134495_5bdbd89f8cbb6.png!small)

9、生成256位AES密钥，并使用CBC模式加密文件。

![使用CBC模式加密文件](https://image.3001.net/images/20181102/1541134506_5bdbd8aa2e7fa.png!small)

10、加密后的文件会直接将原文件覆盖，然后再重命名。

![加密原文件后覆盖写入](https://image.3001.net/images/20181102/1541134515_5bdbd8b328548.png!small)

加密原文件后覆盖写入

![重命名加密后的文件](https://image.3001.net/images/20181102/1541134524_5bdbd8bcf360b.png!small)

重命名加密后的文件

11、加密完以后样本还会自删除：

![自删除](https://image.3001.net/images/20181102/1541134533_5bdbd8c53a010.png!small)

12、最后更换桌面背景给受害者进行提示：

![给受害者进行提示](https://image.3001.net/images/20181102/1541134543_5bdbd8cf38fa3.png!small)

## 解决方案

> 针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。
>
>
> 深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀：<http://edr.sangfor.com.cn/tool/SfabAntiBot.zip>。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**


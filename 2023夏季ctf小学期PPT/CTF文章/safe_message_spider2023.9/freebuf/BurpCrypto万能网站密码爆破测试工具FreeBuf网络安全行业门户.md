**在Web渗透测试中有一个关键的测试项：密码爆破。**

目前越来越多的网站系统在登录接口中加入各式各样的加密算法，依赖于BurpSuite中的那些编码方式、Hash算法已经远远不够，这里给大家介绍一款支持AES/RSA/DES(即将支持)加密算法，甚至可以直接将加密算法的js运行与BurpSuite中的插件：BurpCrypto。

## 安装

BurpCrypto可从其官方[Github](https://github.com/whwlsfb/BurpCrypto/releases)页面进行下载已编译好的版本，或下载源代码本地编译，然后在BurpSuite的扩展列表中添加插件即可。

## 使用方法

BurpCrypto安装完成后会在BurpSuite中添加一个名为BurpCrypto的选项卡，打开选项卡可进入不同加密方式的具体设置界面。

## AES加密

![](https://image.3001.net/images/20200529/1590739770_5ed0c33ab551f.png!small)

常见的加密插件往往只提供一个Processor，此插件设计了多Processor功能，可以添加多个Processor，同时运行多个不同加密方式、不同密钥的测试器。

![](https://image.3001.net/images/20200529/1590739853_5ed0c38d25551.png!small)

![](https://image.3001.net/images/20200529/1590739866_5ed0c39aa009a.png!small)

在测试器中选择刚刚创建的Processor

![](https://image.3001.net/images/20200529/1590739914_5ed0c3cac1663.png!small)

下面直接点击Start Attack即可。

## 找的密文对应的明文

BurpSuite中有一个饱受诟病的问题，在测试器的测试结果中，无法显示原始Payload，也就是字典内容。

该插件具有内置数据库功能，只要是通过该插件生成的密文内容，都可以使用插件中提供的“Get PlainText”功能找回原始Payload。

![](https://image.3001.net/images/20200529/1590740500_5ed0c61496125.png!small)

![](https://image.3001.net/images/20200529/1590740515_5ed0c623bd3a4.png!small)

## ExecJs功能

该插件对于不支持的加密算法也提供了一种变通方法，使用者可根据不同网站使用的加密方法提取其加密的核心函数，并将核心函数稍作加工即可加入本插件中使用。

此处演示使用的是某网站使用的特殊版本的MD5算法。

![](https://image.3001.net/images/20200529/1590740896_5ed0c7a06ad92.png!small)

![](https://image.3001.net/images/20200529/1590740922_5ed0c7ba2bf24.png!small)

然后像AES模块一样添加Processor即可，使用方式也类似与AES模块。

![](https://image.3001.net/images/20200529/1590740981_5ed0c7f581a07.png!small)

![](https://image.3001.net/images/20200530/1590815511_5ed1eb1743a5e.png!small)

> 该插件的的官方Github为：<https://github.com/whwlsfb/BurpCrypto>

该插件为本人开发，欢迎各位老铁使用测试，使用过程中遇到问题，可以给该项目提issue或者PR。

如果试用了本项目，觉得项目还不错的，麻烦多多宣传啦。

 ***本文作者：whw1sfb，转载请注明来自FreeBuf.COM**


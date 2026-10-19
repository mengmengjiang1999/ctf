**作者：昏鸦 & 奇诺比奥  
日期：2021年3月4日**

## 前言

据金色财经消息，2021年3月4日下午，Meerkat Finance项目的金库合约被盗走近3000万美元资产.

![](https://images.seebug.org/content/images/2021/03/04/1614868272000-jscj-info.png-w331s)

同时也有消息称项目方官网无法打开，项目方也无法联系上。
![](https://images.seebug.org/content/images/2021/03/3f40593e-b8d5-4008-a8b8-71be3c57f062.png-w331s)

知道空间安全团队第一时间跟进分析，分享如下。

## 攻击流程简析

攻击者地址已被标记为Fakes_Phishing17，从交易中可以看到攻击者从Proxy
Vault2（0x7e0c621ea9f7afd5b86a50b0942eaee68b04a61c）合约中盗走13,968,039.801181389726119981
BUSD，然后平均分发给14个后续地址转移。

![](https://images.seebug.org/content/images/2021/03/04/1614868273000-stolen-distribute.png-w331s)

在被盗交易tx:0x1332fadcc5378b1cc90159e603b99e0b73ad992b1e6389e012af3872c8cae27d
中，可以看出攻击者的动作是调用了函数70fcb0a7，参数e9e7cea3dedca5984780bafc599bd69add087d56。

![](https://images.seebug.org/content/images/2021/03/04/1614868274000-tx-0x1332.png-w331s)

而参数e9e7cea3dedca5984780bafc599bd69add087d56正是BUSD代币地址，函数70fcb0a7是目前未知的匿名函数。

查看代理合约Proxy Vault2的事件记录

![](https://images.seebug.org/content/images/2021/03/04/1614868274000-eventlog.png-w331s)

最后一个事件记录，恰巧是发生在攻击前的升级操作，将合约指向了0xB2603fc47331E3500eAf053bd7A971B57e613D36地址，该地址是一个未开源的合约，在平台反编译的伪代码中能发现攻击交易使用的函数70fcb0a7。

![](https://images.seebug.org/content/images/2021/03/04/1614868275000-func70fcb0a7.png-w331s)

而这一升级操作正是项目方的部署者发起的

![](https://images.seebug.org/content/images/2021/03/04/1614868275000-tx-upgrade.png-w331s)

因此推断大概率是项目方跑路。

## 总结

通过对整个事件的分析来看，Meerkat Finance 此次事故并不在安全漏洞的范畴内，主要的原因在于官方通过代理合约的升级操作指向攻击合约，
然后通过调用攻击合约的恶意函数最终转走近 1400 BUSD。 因此，大概率是项目方跑路，项目方官网进不去、也联系不上也印证了这一点。

## 建议

在流动性挖矿的引领下，去中心化金融逐渐成为金融革新的焦点，在这一领域的玩法也越发多样。DeFi投资更需谨慎，不能枉顾风险一哄而上，而需要对DeFi项目及项目方背景做好充分的了解。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1494/>


# 是后门，还是大意？Furucombo遭黑客攻击事件分析

阅读量 **186812**

发布时间 : 2021-03-02 17:30:19

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t012e7d8fe620b30d86.jpg)

## 事件背景

Furucombo推出于2020年3月份，支持Uniswap交易，Compound供应功能，还提供闪电贷的用户界面，使得普通用户也可以使用闪电贷策略。

零时科技监控到消息，北京时间2021年2月28日早7时，Furucombo官方发推称Furucombo代理遭到攻击者攻击，1500万美元受到影响，并说明取消相关组件授权，受到攻击的合约地址0x17e8Ca1b4798B97602895f63206afCd1Fc90Ca5，随后零时科技安全团队立刻对该安全事件进行复盘分析。

![](https://p1.ssl.qhimg.com/t0190c1c0c46f7eda22.png)

## 事件分析

通过初步分析，可以得到攻击者的钱包地址为0xb624E2b10b84a41687caeC94BDd484E48d76B212，目前该地址已被etherscan标记为Furucombo
Hacker。

![](https://p5.ssl.qhimg.com/t01300f0ff4ca610294.png)

该攻击者合约地址除了创建合约交易，其余只有一笔交易0x6a14869266a1dcf3f51b102f44b7af7d0a56f1766e5b1908ac80a6a23dbaf449查看该笔交易的状态会发现，存储地址0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc目前写入的内容为攻击者合约地址0x86765dde9304bEa32f65330d266155c4fA0C4F04。

![](https://p3.ssl.qhimg.com/t0146f79b6fa1feb4d4.png)

为什么会出现这种情况，继续根据Furucombo: Proxy
v1.0.0合约0x17e8ca1b4798b97602895f63206afcd1fc90ca5f，分析其对应的代理Aave
V2合约0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9。Aave V2 Proxy
合约中，0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc值对应IMPLEMENTATION_SLOT变量，最终使用该变量的函数为_implementation()，具体代码如下图所示。

![](https://p1.ssl.qhimg.com/t0190179e6501bd2fcd.png)

继续分析Aave V2 Proxy 合约，

![](https://p0.ssl.qhimg.com/t01c877433e80913a28.png)

在initialize()函数中，均对IMPLEMENTATION_SLOT变量和implementation()函数进行了判断，函数第一行代码判断implementation()函数值是否为0，第二行代码中，也是判断IMPLEMENTATION_SLOT值是否相等，如果前两行代码判断成功，就会将initialize()函数传进来的地址_logic设置为Implementation，当Implementation设置成功后，其他调用者也就无法成功调用initialize()函数（initialize()函数条件的前两行再也无法满足），所以通过initialize()函数设置的Implementation为永久。

通过以上分析，攻击者合约的第二笔交易状态就可以解释了。由于urucombo官方未对Aave V2 Proxy
合约中的0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc
这个位置进行初始化赋值，所以导致攻击者使用自己的地址进行了初始化，最终攻击者盗取了Furucombo合约有授权的代币价值约1500万美元。

建议用户尽快自行检查钱包授权，相关工具：https://cn.etherscan.com/tokenapprovalchecker
未参与的项目及时删除授权。

![](https://p4.ssl.qhimg.com/t0114562ad13a28c82c.png)

## 安全建议

DeFi今年确实备受关注，黑客攻击也不断发生，包括Harvest Finance，Value DeFi，Akropolis，Cheese
Bank和Origin Dollar等均受到不同程度的黑客攻击。针对频频发生的黑客攻击事件，我们给出以下的安全建议：

在项目上线之前，找专业的第三方安全企业进行全面的安全审计，而且可以找多家进行交叉审计；  
可以发布漏洞赏金计划，发送社区白帽子帮助找问题，先于黑客找到漏洞；  
加强对项目的安全监测和预警，尽量做到在黑客发动攻击之前发布预警从而保护项目安全。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/232971](/post/id/232971)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [区块链](/tag/区块链)
  * [defi](/tag/defi)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01482eaf8414a7973c.png) 零时科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


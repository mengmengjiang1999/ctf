# Earing Farm攻击事件分析

阅读量 **133440**

发布时间 : 2022-11-01 12:00:34

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t016772cb7f1f1f4757.jpg)

## 事件背景

零时科技区块链安全情报平台监控到消息，北京时间2022年10月15日，DeFi 投资工具 Earning.Farm 遭受闪电贷攻击，黑客获利超 34
万美元，攻击者地址为0xdf31f4c8dc9548eb4c416af26dc396a25fde4d5f，零时科技安全团队及时对此安全事件进行分析。

## 攻击步骤

1.调用闪电贷借出560 ETH

![](https://p0.ssl.qhimg.com/t015d1aa1b72e7f52f7.png)

2.调用receiveFlashloan函数，根据userData传入参数调用_withdraw函数计算获利资金为833 stETH

![](https://p3.ssl.qhimg.com/t01172a944e39bc27f5.png)

3.归还闪电贷资金560ETH，此时合约中仍有资金约273stETH

![](https://p2.ssl.qhimg.com/t01ce230b95ed1c2e87.png)

4.调用withdraw函数取出合约中资金

![](https://p2.ssl.qhimg.com/t012c925cdc2de17189.png)

5.攻击者共获利268.7ETH

![](https://p4.ssl.qhimg.com/t012ca9589cd6d35cca.png)

## 漏洞核心

合约正常逻辑为通过调用withdraw函数，判断用户持有的ef_token数量后计算用户获得的收益，之后通过闪电贷还款后剩余的资金就是用户获得的收益。

![](https://p5.ssl.qhimg.com/t018a888393391f9bb8.png)

但是在Vault合约中对于调用闪电贷的地址没有进行判断，因此攻击者可以自行调用闪电贷合约，将闪电贷的接受者设置为EFLevelValue的地址，并且传入的参数由用户控制，攻击者可以自行设置userData的数据。

![](https://p5.ssl.qhimg.com/t01a8127858cbd5dce7.png)

在receiveFlashLoan函数中可以看到当传入参数哈希值与“0x2”哈希值相等时执行_withdraw函数

![](https://p2.ssl.qhimg.com/t01a5cda7041c094160.png)

攻击者传入参数userData为307832，通过进制转换可知为字符串0x2

![](https://p0.ssl.qhimg.com/t01446a16830aa8b37e.png)

在_withdraw()函数中根据传入的 amount将stETH从AAVE中取出后兑换为WETH，之后归还闪电贷资金，剩余资金存在合约中。

![](https://p1.ssl.qhimg.com/t010504133b01f60d63.png)

在withdraw（）函数中转账数量计算时没有对于用户应收的资金进行判断，而是将合约中剩余资金全部转出。

![](https://p1.ssl.qhimg.com/t01df10811ebffec824.png)

因此攻击者通过正常调用withdraw函数，可以使用少量的ef_token将合约中的资金全部转出。

![](https://p5.ssl.qhimg.com/t01131b1a45f7fc7059.png)

## 资金来源及去向

攻击者初始资金来源于跨链合约

![](https://p2.ssl.qhimg.com/t01ceb697a01f8c0305.png)

后续攻击者将部分资金转移至Tornado.cash混币平台，部分资金转移至
地址0xDa08116d1e36CaDe5dE91bc6892FB0fAF00eBf15后通过multichain款连合约转出

![](https://p5.ssl.qhimg.com/t0147c9de2bd34bb6c9.png)

![](https://p5.ssl.qhimg.com/t01713f2a4912243696.png)

## 总结及建议

此次攻击主要是由于在闪电贷合约中没有对闪电贷合约发起者进行判断使得攻击者可以直接调用闪电贷将闪电贷接收者设置为被攻击合约进行计算奖励的操作，并且在提取奖励时没有对用户应获得的奖励进行判断，直接将合约剩余资金全部转出，因此攻击者可以使用少量的ef_token将攻击获得资金全部转移。

**安全建议**

建议在闪电贷时对发起闪电贷地址进行判断，避免攻击者恶意调用合约

建议项目方上线前进行多次审计，避免出现审计步骤缺失

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/281979](/post/id/281979)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [攻击事件](/tag/攻击事件)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01482eaf8414a7973c.png) 零时科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


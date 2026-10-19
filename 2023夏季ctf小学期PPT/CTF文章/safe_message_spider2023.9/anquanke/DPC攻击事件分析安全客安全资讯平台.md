# DPC攻击事件分析

阅读量 **73071**

发布时间 : 2022-09-19 10:30:01

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t014ee861c92a44b38a.jpg)

## 事件背景

零时科技区块链安全情报平台监控到消息，北京时间2022年9月10日，DPC代币合约遭到黑客攻击，损失超73,614 BUSD,
零时科技安全团队及时对此安全事件进行分析。

## 攻击信息

攻击者钱包地址：

0xf211Fa86CBc60d693D687075B03dFF3c225b25C9

攻击合约地址：

0x2109bbecB0a563e204985524Dd3DB2F6254AB419

被攻击合约地址：

0xb75ca3c3e99747d0e2f6e75a9fbd17f5ac03cebe

## 攻击步骤

1.向被攻击合约转移代币，每次转移100 BUSD，共转移 4,200 BUSD

![](https://p5.ssl.qhimg.com/t01d534edd3d5872ed9.png)

2.使用 50 BUSD 兑换 3.63 DPC

![](https://p5.ssl.qhimg.com/t01fd878e3423129b25.png)

3.将兑换得到的 DPC与 47.4 BUSD 用于添加流动性，将获得的流动性代币质押

![](https://p0.ssl.qhimg.com/t011377f2b2475a30a6.png)

4.调用claimStakeLp函数多次取出0.000000000000000001
LP代币，在claimStakeLp中会将当前奖励与之前奖励相加，使得获得的奖励增加。

![](https://p2.ssl.qhimg.com/t01f11b82f28e1fe877.png)

![](https://p3.ssl.qhimg.com/t012959fb60c817e45c.png)

5.调用claimDpcAirdrop函数获得奖励20,602 DPC，将获得奖励兑换为 75,664 BUSD

![](https://p4.ssl.qhimg.com/t019e908e243f7d744d.png)

## 漏洞核心

DPC中通过质押LP代币获得奖励，攻击者通过调用合约中claimStakeLp 函数使得获得的奖励增加。

![](https://p2.ssl.qhimg.com/t0174acae6524152710.png)

函数claimStakeLp()
中计算获得的奖励是将之前的奖励与getClaimQuota()计算出的奖励累加，而在函数getClaimQuota()中也进行了一次ClaimQuota的累加计算（下图），攻击者通过多次调用claimStakeLp函数使得获得的奖励增加。

![](https://p4.ssl.qhimg.com/t0170227de87fe2f8e4.png)

第一次调用claimStakeLp函数获得奖励

![](https://p5.ssl.qhimg.com/t01f7f854e9f14b78d7.png)

多次调用claimStakeLp函数后获得奖励

![](https://p5.ssl.qhimg.com/t01d90aee19560ea6f7.png)

## 资金来源

通过混币平台Tornado.Cash转入 10 BNB

![](https://p1.ssl.qhimg.com/t01faa09aea23aa554e.png)

## 资金流向

攻击者通过重复攻击共获利约73,614 BUSD，目前资金仍在攻击者钱包中。

![](https://p5.ssl.qhimg.com/t018c5e41476d0da92f.png)

## 总结及建议

此次攻击主要原因是对于奖励机制设置出现漏洞，使得奖励数额成倍数增加，且奖励数额计算时与调用claimStakeLp()函数时传入的数字无关，因此攻击者可以用一个较小的金额进行多次调用，实现获得大额的奖励。

## 安全建议

建议计算中涉及到函数调用时需要详细检查变量数值变动情况，避免数值被重复计算。

建议项目方上线前进行多次审计，避免出现审计步骤缺失。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/280257](/post/id/280257)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [区块链](/tag/区块链)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01482eaf8414a7973c.png) 零时科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


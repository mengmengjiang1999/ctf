# BXH攻击事件分析

阅读量 **87321**

发布时间 : 2022-10-08 11:00:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01cf4adf4bbbacffce.png)

## 0x1 事件背景

零时科技区块链安全情报平台监控到消息，北京时间2022年9月29日，BXH合约遭到黑客攻击，损失超40,085 BUSD,
零时科技安全团队及时对此安全事件进行分析。

## 0x2 攻击信息

  * 攻击者地址：

0x81c63d821b7cdf70c61009a81fef8db5949ac0c9

  * 攻击者合约地址：

0x4e77df7b9cdcecec4115e59546f3eacba095a89f

  * 被攻击合约地址：

0x27539b1dee647b38e1b987c41c5336b1a8dce663

## 0x3 攻击步骤

调用deposit（）函数向合约转移 5,582 VUSDT

![](https://p3.ssl.qhimg.com/t01dd200c90b166f4ef.png)

攻击者通过闪电贷借出 3,178,800 BUSD

![](https://p4.ssl.qhimg.com/t015123c3f022f1b925.png)

将 3,148,800 BUSD 兑换为 148,851 BXHToken

![](https://p0.ssl.qhimg.com/t01c71a7f631bf2935a.png)

向被攻击合约转移 200BUSD

![](https://p0.ssl.qhimg.com/t014c069268a924aca7.png)

调用depositIToken函数中getITokenBonusAmount()函数，计算得到 40,085 BUSD奖励

![](https://p2.ssl.qhimg.com/t01714c5499a0605b0f.png)

将兑换得到的BXHToken 兑换为 BUSD 并归还闪电贷

![](https://p3.ssl.qhimg.com/t01b843a1a554fd85e9.png)

## 0x4 漏洞核心

攻击者通过闪电贷借出大量BUSD，兑换为BXHToken，使得池子中BUSD
瞬间增大，在计算获得的奖励时由于会与BUSD数量做乘法，使得获得奖励也会成倍增加。

![](https://p2.ssl.qhimg.com/t013ef89649d37b893f.png)

## 0x5 资金流向

兑换为BNB 转移至混币平台

![](https://p3.ssl.qhimg.com/t01b854d1e1e7ff1f99.png)

![](https://p0.ssl.qhimg.com/t01c09b8c01d902c7f7.png)

## 0x6 总结及建议

此次攻击主要原因是在计算奖励时会与池子中BUSD的数量相乘，当池子中USDT数量增加时，获得的奖励相应增加。攻击者通过闪电贷向池子中转移大量BUSD，使得计算出的奖励增加从而获利。

###  安全建议

建议计算中涉及数值引用及乘除法计算时详细检查，避免出现计算数值受引用数值较大影响的情况发生。

建议项目方上线前进行多次审计，避免出现审计步骤缺失。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/281172](/post/id/281172)

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


# Victor the Fortune攻击事件分析

阅读量 **169268**

发布时间 : 2022-11-07 10:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01d74fbcac76970b1f.jpg)

## 事件背景

零时科技区块链安全情报平台监控到消息，北京时间2022年10月27日，BSC链上Victor the Fortune
合约受到黑客闪电贷攻击，攻击者已获利约5.8万美元，耗尽了流动资金池，攻击者地址为0x57c112cf4f1e4e381158735b12aaf8384b60e1ce，零时科技安全团队及时对此安全事件进行分析。

## 攻击步骤

1.攻击者通过闪电贷借出约100,000 USDT

![](https://p4.ssl.qhimg.com/t01911967cfc29ca911.png)

2.将借出的USDT兑换为77,853 VTF

![](https://p1.ssl.qhimg.com/t01b75d015ca7b0b71d.png)

3.调用updateUserBalance()函数计算获得奖励

![](https://p4.ssl.qhimg.com/t01a967c9b3b62823cf.png)

4.调用transfer函数将资金全部转移至 地址 0x1dd557415a0ddea7d3e56f49c78d54ebbf31f569

![](https://p4.ssl.qhimg.com/t01b6a55767394c742b.png)

5.调用updateUserBalance()函数获得奖励

![](https://p4.ssl.qhimg.com/t0102e173c10fe7fe5a.png)

6.重复执行第四步和第五步，最后共获得 499,803,157 VTF

![](https://p3.ssl.qhimg.com/t011187ebebca501949.png)

![](https://p1.ssl.qhimg.com/t012b0025eac93d5ec1.png)

7.将获得的VTF兑换获得 158,450 USDT

![](https://p4.ssl.qhimg.com/t016eace251d2d75723.png)

归还闪电贷后共获利 58,450 USDT

![](https://p2.ssl.qhimg.com/t015228db6546163eb9.png)

## 漏洞核心

攻击者通过调用transfer函数进行转账，在转账函数中调用了updateUserBalance()函数，由于此时userBalanceTime[user]为0会将当前时间赋值给userBalanceTime[user]。

![](https://p2.ssl.qhimg.com/t01d4264398decbb3c0.png)

之后调用updateUserBalance()，当userBalanceTime大于0时会调用 getUserCanMint函数计算奖励值

![](https://p1.ssl.qhimg.com/t019a9489f6548c9a70.png)

在getUserCanMint函数中计算返回值是用户的余额除以常数乘当前时间与用户开始时间的时间差，由于没有设置最小时间差，因此在很短时间调用函数也可以获得奖励。

![](https://p2.ssl.qhimg.com/t01d1b21b371d06b5d3.png)

由于调用一次updateUserBalance()函数后会更新时间，攻击者通过调用transfer函数将资金转移至一个新的地址，再次调用updateUserBalance()函数可以继续获利，并且当攻击者地址资金增加时获得的奖励也随着增加，攻击者通过重复以上步骤获得奖励逐渐增加直到将池子掏空。

## 总结及建议

此次攻击是由于合约中的计算奖励函数的算法只与用户地址余额和时间差有关，攻击者通过先调用转账获得用户初始时间，之后调用获得奖励的函数，通过这两个函数调用过程中的时间差计算获得奖励。通过多次转账计算获得奖励使得资金累加，最后将池子中代币几乎掏空。

****安全建议****

建议对于计算获得奖励时设置最小时间差，避免攻击者通过短时间多次调用函数获利。

建议项目方上线前进行多次审计，避免出现审计步骤缺失

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/282574](/post/id/282574)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [区块链](/tag/区块链)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t01482eaf8414a7973c.png) 零时科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


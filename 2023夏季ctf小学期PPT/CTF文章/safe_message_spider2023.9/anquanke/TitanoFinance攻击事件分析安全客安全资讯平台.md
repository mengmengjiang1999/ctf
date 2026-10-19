# Titano Finance攻击事件分析

阅读量 **109520**

发布时间 : 2022-02-17 17:30:35

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01773a5fec35a66b32.png)

## 0x1 事件背景

Titano是加密领域中较好的自动质押和自动复利协议，它的定位是通过Titano自动质押协议或TAP引领DeFi的革命，TAP是一种新的金融协议，使质押更容易，并为$TITANO代币持有者提供加密货币中最高的稳定回报。

零时科技区块链安全情报平台监控到消息，北京时间2022年2月14日，Titano
Finance遭到攻击，损失3200万TITANO代币，零时科技安全团队及时对此安全事件进行分析。

## 0x2 攻击信息

零时科技安全团队通过追踪分析，主要攻击信息如下：

  * 攻击者钱包地址

_<https://bscscan.com/address/0xad9217e427ed9df8a89e582601a8614fd4f74563>_

  * 攻击者创建的相关合约地址

**MultipleWinnersProxyFactory**
_<https://bscscan.com/address/0x940151f5bbbcda5b1b482592d816e96f80d6073a>_

**MultipleWinnersBuilder**
_<https://bscscan.com/address/0x1866207c355d4c6e0b03b4dc0bf9c658f4d13f8a>_

**MultipleWinners**
_<https://bscscan.com/address/0x49d078d25b08f2731cbf5af8e8cdf1ea3e0a2046>_

  * 出现异常操作的官方合约

**StakePrizePool**
_<https://bscscan.com/address/0x4d7f0a96967dce1e36dd2fbb131625bbd9106442>_

## 0x3 攻击分析

下面拆解攻击者交易，先看一下攻击者获利的交易操作，一共分为三部分：

第一部分主要是获得Ticket Titano代币；

第二部分将Ticket Titano代币转换成BNB；

第三部分将获取的BNB转移至多个钱包地址。

![](https://p5.ssl.qhimg.com/t01fb80debbaa3427ad.png)

![](https://p0.ssl.qhimg.com/t01972668c1c6a00752.png)

下来详细分析三部分的攻击流程。

1.首先第一部分中，攻击者创建了两个合约，分别为MultipleWinnersProxyFactory和MultipleWinnersBuilder，随后通过MultipleWinnersBuilder合约的createMultipleWinnersFromExistingPrizeStrategy方法创建了MultipleWinners合约，

这里有一个重要操作：官方StakePrizePool合约中执行了只有管理员可操作的setPrizeStrategy方法，并且该方法将攻击者之前创建的MultipleWinners合约地址设置为新的_prizeStrategy地址。

![](https://p5.ssl.qhimg.com/t01a146a4b5673915b1.png)

![](https://p0.ssl.qhimg.com/t01cf2ab214f2349b59.png)

随后攻击者通过MultipleWinners合约中可铸造Ticket Titano代币的_awardTickets方法，

![](https://p2.ssl.qhimg.com/t0121a066a2d36fdd80.png)

铸造了3200万Ticket
Titano代币（由于此处MultipleWinners合约由攻击者生成，所以攻击者很容易达到管理员地址onlyOwner的条件）。

铸币完成后，官方StakePrizePool合约又将原始的_prizeStrategy地址设置回去。

2.第二部分将Ticket Titano代币转换成BNB，攻击者首先通过StakePrizePool合约将Ticket
Titano代币代币转换成TITANO代币，随后通过PancakeSwap将得到的TITANO代币兑换成BNB，一共获得约4828枚BNB。

3.攻击者将获得的4828枚BNB以200枚为一组转移至25个钱包地址，目前转移后的资金暂未流动。

目前Titano Finance已宣布参与Titano PLAY用户都将全额退还其代币。

## 0x5 总结

通过此次攻击事件来看，攻击者最重要的步骤是Titano
Finance官方StakePrizePool合约只有管理员可调用的方法进行了恶意操作，基本可以确定为管理员地址泄露或者内部拥有该管理员私钥人员所为，不管出于哪种情况，项目出现类似的波动都是用户不想遇到的，所以对于项目管理者密钥安全性，零时科技安全团队给出以下建议。

## 0x6 安全建议

  * 建议管理员地址使用多签钱包管理私钥
  * 建议管理员地址采用锁合约限制管理员敏感操作

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/268024](/post/id/268024)

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


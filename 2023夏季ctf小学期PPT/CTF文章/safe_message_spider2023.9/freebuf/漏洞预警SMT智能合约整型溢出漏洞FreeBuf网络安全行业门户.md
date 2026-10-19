***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![SmartMesh-banner.jpg](https://image.3001.net/images/20180425/15246455974844.jpg!small)  

## 漏洞概述

 **SmartMesh
Token是基于Ethereum的合约代币，简称SMT。Ethereum是一个开源的、公共的分布式计算平台，SmartMesh代币合约SmartMeshTokenContract基于ERC20Token标准。漏洞发生在转账操作中，攻击者可以在无实际支出的情况下获得大额转账。**

## 漏洞影响  

不久前，BEC美蜜遭遇黑客的毁灭性攻击，天量BEC从两个地址转出，引发了市场抛售潮。当日，BEC的价值几乎归零。

4月25日早间，火币Pro公告，SMT项目方反馈今日凌晨发现其交易存在异常问题，经初步排查，SMT的以太坊智能合约存在漏洞。受此影响，火币Pro现决定暂停所有币种的充提币业务。  

截至目前，OKEx已经[暂停](https://support.okex.com/hc/en-us/articles/360003019292)使用ERC-20 token的取款交易。  

## 漏洞成因

![TIM截图20180425163432.png](https://image.3001.net/images/20180425/15246454825373.png!small)  

漏洞来源自合约机制中的整数溢出漏洞。在出现问题的交易记录中，交易金额和交易手续费用异常庞大。

![0
Bc9Nk6mq4sMSfYrX.png.jpg](https://image.3001.net/images/20180425/15246455098642.jpg!small)  

而在执行转账操作的proxyTransfer()函数中，_fee与_value参数（分别代表转账费用和转账金额）可以由攻击者控制，如果二者相加数额为0，第206行的校验机制就不再生效。根据proxyTransfer()函数中定义的数据类型，_fee与_value参数都为uint256类型，如果设置过大数值导致二者相加后整型溢出，转帐方实际损失的费用就为0，并且能够收取巨额资金。

根据PeckShield 团队的报告，目前已有多笔交易利用漏洞产生巨额资金：

![1
gMm1cJb5hWvQEd1Ly8gGNg.png](https://image.3001.net/images/20180425/15246457023481.png!small)

 ***参考来源：[挖链网](https://www.walian.cn/news/1446.html) &
[新浪](http://finance.sina.com.cn/blockchain/coin/2018-04-25/doc-ifzqvvsc0353302.shtml)， 部分图片、分析来自永信至诚Ar（先进研究）实验室，本文作者：Sphinx，转载请注明来自FreeBuf**  


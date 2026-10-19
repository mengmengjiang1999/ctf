![1686573123_6487104393e76b309258d.png!small?1686573124200](https://image.3001.net/images/20230612/1686573123_6487104393e76b309258d.png!small?1686573124200)

## **0** **1**

根据 Numen 链上监控显示，Jun-12-2023 01:06:35 AM（+UTC）， Ethereum 链上 Sturdy（@Sturdy
Finance）项目遭到闪电贷攻击，损失442枚 ETH，价值约80万美元。

被盗资金已全部转移至 Tornado.Cash。

###  **事件分析**

 **攻击者地址：** etherscan.io/address/0x1e8419e724d51e87f78e222d935fbbdeb631a08b  
 **攻击者合约地址：** etherscan.io/address/0x0b09c86260c12294e3b967f0d523b4b2bcdfbeab

###  **根本原因**

“攻击者”利用重入漏洞，重复创建合约以调用 joinPool 函数，然后调用 exitPool
函数。![1686573166_6487106e2809b62b727b0.png!small?1686573167698](https://image.3001.net/images/20230612/1686573166_6487106e2809b62b727b0.png!small?1686573167698)由于
exitPool 函数中存在重入 #vulnerability，黑客获得了操纵从 getAssetPrice(cB-stETH-STABLE)
获得的价格并从中获利的能力。

![1686573181_6487107d8245d49359b2f.png!small?1686573182094](https://image.3001.net/images/20230612/1686573181_6487107d8245d49359b2f.png!small?1686573182094)

##  **0** **2**

近期闪电贷攻击事件较为频发。  
根据 Numen 链上监控显示，Jun-11-2023 10:37:49
AM（+UTC），SellToken（@TrustTheTrident）可能受到了攻击，攻击者利用闪电贷和多个地址借入了大量资金。  
 **攻击者地址：** bscscan.com/address/0x0060129430df7ea188be3d8818404a2d40896089  
 **攻击者合约地址：** bscscan.com/address/0x2cc392c0207d080aec0befe5272659d3bb8a7052

###  **根本原因**

攻击者通过矿工合约中的“sendMiner”方法操纵价格，使计算的资金膨胀，最终获得可观的金额。  
![1686573205_64871095c169f45f93191.png!small?1686573206458](https://image.3001.net/images/20230612/1686573205_64871095c169f45f93191.png!small?1686573206458)

 **END**


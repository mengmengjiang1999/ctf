## ​​ **一、事件概览**

北京时间7月14日，BSC生态DeFi收益耕种聚合器ApeRocket
Finance遭遇“闪电贷攻击”。据相关消息指出，此次攻击事件中，攻击者针对的是ApeRocket其下Apeswap的SPACE-BNB池，其项目代币SPACE已下跌逾75%。

有安全团队近期已披露多起BSC生态“闪电贷”攻击事件，在ApeRocket
Finance被黑事件中，攻击者依然利用了“闪电贷”的攻击原理，“换汤不换药”，通过操纵项目合约的“质押收益”和“奖励机制”从而进行获利。值得注意的是，ApeRocket
Finance是本月首起较为典型的安全攻击事件，在此提醒各项目方做好日常安全审计和安全防护工作。

![007apYDpgy1gsgps69jp9j30ql0eygss.jpg](https://image.3001.net/images/20210714/1626265451_60eed76be5027cd4cb288.jpg!small)

##  **二、事件分析**

###  **攻击过程分析**

1\. 攻击者首先利用了“闪电贷”，借取了1259459+355600个cake。

![007apYDpgy1gsgps6h5lbj30px01sglq.jpg](https://image.3001.net/images/20210714/1626265452_60eed76c6e9b9dcff6109.jpg!small)

2\. 随后，将其中的509143个cake抵押至AutoCake（相当于是Aperocket的策略合约）。

![007apYDpgy1gsgps7mg22j30p0015a9z.jpg](https://image.3001.net/images/20210714/1626265452_60eed76cab085dcd65078.jpg!small)

3\. 攻击者将剩余的1105916个cake直接打入AutoCake合约。

![007apYDpgy1gsgps7y3c8j30pb010dfr.jpg](https://image.3001.net/images/20210714/1626265452_60eed76ce97d5cdc06f22.jpg!small)

4\. 然后攻击者再调用AutoCake中的harvest触发复投，将步骤3中打入Autocake的cake进行投资。

![007apYDpgy1gsgps86iy3j30p300zq2u.jpg](https://image.3001.net/images/20210714/1626265453_60eed76d362002968f213.jpg!small)

5\. 完成上述攻击步骤后，攻击者调用AutoCake中的getReward结算步骤2中的抵押盈利，随即触发奖励机制铸币大量的SPACE
Token进行获利。

![007apYDpgy1gsgps8ch1mj30ot00u0sn.jpg](https://image.3001.net/images/20210714/1626265453_60eed76d724c604b8de80.jpg!small)

6\. 归还“闪电贷”，完成整个攻击后离场。

![007apYDpgy1gsgps8l8jwj30p60763zy.jpg](https://image.3001.net/images/20210714/1626265453_60eed76daff01fe72310d.jpg!small)

###  **攻击原理分析**

在此次攻击事件中，攻击者首先在AutoCake中抵押了大量Cake，这使得其持股占比非常之高，从而能够分得AutoCake中几乎全部的质押收益。

在步骤3中，攻击者直接向AutoCake合约中打入大量cake，这部分cake因并没有通过抵押的方式打入AutoCake合约；根据合约自身逻辑，将会被当作“奖励”（抵押cake，奖励也是cake）。

一来一回，直接打入AutoCake中的cake大部分最终也会结算给攻击者。但另一方面，在进行getReward操作时，函数会根据质押而获得奖励的数量来铸币SPACE
Token发放给用户，做为另外的奖励。在正常情况下，质押奖励较少，因此铸币的SPACE
Token也会很少；但由于攻击者上述的操作，便导致铸出了大量的SPACE Token。

![007apYDpgy1gsgps8t6uvj30jn08agmb.jpg](https://image.3001.net/images/20210714/1626265454_60eed76e3def36866e955.jpg!small)

##  **三、事件复盘**

不难看出，这是一次典型的利用“闪电贷”而完成获利的攻击事件，其关键点在于AutoCake合约自身逻辑的“奖励机制”，最终导致攻击者铸出了大量的SPACE
Token完成获利。同时，这也是本月首起典型的“闪电贷”攻击事件，值得引起注意。

安全团队建议，随着“闪电贷”在DeFi生态越来越受青睐，潜藏在暗处的攻击者也随时准备着利用“闪电贷”而发动攻击。因此，DeFi生态各项目方仍然需要格外重视来自“闪电贷攻击”的威胁，与第三方安全公司积极联动，构建起一套完善而专业的安全防护机制。


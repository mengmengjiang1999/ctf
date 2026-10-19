作者：腾讯湛泸实验室  
来源：<https://weibo.com/ttarticle/p/show?id=2309404232782242012923#_0>

此次漏洞发生的虚拟货币为SmartMesh（简称SMT），目前该货币以以太坊智能合约的形式发布，Token为[0x55f93985431fc9304077687a35a1ba103dc1e081](https://etherscan.io/address/0x55f93985431fc9304077687a35a1ba103dc1e081
"0x55f93985431fc9304077687a35a1ba103dc1e081")，最初触发漏洞的交易记录位于下图所示的交易记录上：

![](https://images.seebug.org/content/images/2018/05/9e3ed1fe-2c2c-4b5d-953a-bf39e82d3512.jpg-w331s)
异常交易记录

根据图中Input
Data中的信息，定位到SMT中发生错误的智能合约函数transferProxy，该函数主要用于没有以太币的SMT币拥有者，将签署过的交易信息交由第三方节点进行发布，而消息的发送节点会收到SMT币作为酬劳。

![](https://images.seebug.org/content/images/2018/05/9a7c14f3-b80e-46fa-8fc0-b104289b2750.jpg-w331s)
漏洞函数截图

该函数的第一行对于此次交易转出者的余额进行校验。交易记录中的0-6变量依次对应于该函数的７个参数，此处的_feeSmt + _value实际为：

    
    
    0x7000000000000000000000000000000000000000000000000000000000000001 +
    
    0x8FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

运算结果会被映射为uint256型数据，因此会发生无符号整型数据的上溢，使计算结果为0，从而绕过了此处检查。这最终将导致msg.sender（发送交易消息的节点）和`_to`（钱币接受者）代表的钱包在记账时分别记入feeSmt（0x7000......）和`_value`（0x8FFF......）个SMT货币。这一过程被同样被记录在了以太坊的交易记录中，如下图最后两条记录所示，而后续发生的交易则是攻击者向其他钱包进行钱币转移的操作。

![](https://images.seebug.org/content/images/2018/05/593550fb-abcd-4131-b13f-db4dbcd875cc.jpg-w331s) 攻击者账户交易信息

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/591/>


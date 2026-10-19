2022 年 04 月 15 日，由于恶意攻击，Rikkei Finance 的五个资金池 (USDT, BTC, DAI, USDT, BUSD)
中近乎全部代币被盗。

![慢雾](https://image.3001.net/images/20220421/1650539515_62613bfb361a70e3fa35b.jpg!small)

慢雾安全团队将复现分析结果分享如下：

##  **相关信息**

Rikkei Finance 是 BSC 上的一个 DeFi 借贷平台。

以下是本次攻击涉及的相关地址：

攻击者地址：

<https://bscscan.com/address/0x803e0930357ba577dc414b552402f71656c093ab>

攻击合约：

<https://bscscan.com/address/0xe6df12a9f33605f2271d2a2ddc92e509e54e6b5f>

攻击交易：

<https://bscscan.com/tx/0x93a9b022df260f1953420cd3e18789e7d1e095459e36fe2eb534918ed1687492>

##  **攻击核心点**

此次 Rikkei Finance 遭受攻击的根本原因是 setOracleDate 函数调用的权限控制缺失导致预言机价格被恶意操纵。

##  **具体细节分析**

1\. 攻击者用 0.0001 BNB 兑换一些 rBNB 作为抵押物，rBNB 合约地址为

<https://bscscan.com/address/0x157822aC5fa0Efe98daa4b0A55450f4a182C10cA>

![慢雾](https://image.3001.net/images/20220421/1650539516_62613bfc2d82bacabdced.jpg!small)

2\. 对 rBNB 设置恶意预言机，合约地址为

<https://bscscan.com/address/0xd55f01b4b51b7f48912cd8ca3cdd8070a1a9dba5>

![慢雾](https://image.3001.net/images/20220421/1650539516_62613bfcc7b8ae3478f20.jpg!small)

![慢雾](https://image.3001.net/images/20220421/1650539517_62613bfd68408d785b83e.jpg!small)

部署的恶意预言机地址为

<https://bscscan.com/address/0xA36F6F78B2170a29359C74cEFcB8751E452116f9>，其反编译得到：

![慢雾](https://image.3001.net/images/20220421/1650539517_62613bfdf3a7235a6e16b.jpg!small)

可以看到，预言机返回价格被写成一个巨大的常数。

3\. 分别对 rUSDC, rBTC, rDAI, rUSDT, rBUSD 合约进行借贷。由于上一步部署了恶意预言机，rBNB
被认为有高价值，因此能贷出池子中所有币。然后在 pancake 中进行 swap 换成 BNB，攻击者总获利约 2571 枚 BNB。

![慢雾](https://image.3001.net/images/20220421/1650539518_62613bfe8c7631c8a633c.jpg!small)

![慢雾](https://image.3001.net/images/20220421/1650539519_62613bff1ae2937bed4ba.jpg!small)

4\. 攻击者将 BNB 打入 Tornado.Cash：

![慢雾](https://image.3001.net/images/20220421/1650539519_62613bffc6b56bb700fb9.jpg!small)

##  **总结**

本次攻击事件是由于 Rikkei Finance 项目中的 SimplePriceOracle 合约文件中的 setOracleData
函数缺少鉴权，可以被任意调用。攻击者通过 setOracleData 函数将恶意 Oracle 合约加入到 SimplePriceOracle
中，在借贷时攻击者持有的少量抵押物，由于抵押物的价格是从恶意 Oracle
合约中获取，导致攻击者的抵押物被误认为具有很高价值，从而允许攻击者用少量的抵押物将 Rikkei Finance 池子中的 USDC, BTC, DAI,
USDT, BUSD 全部借出。慢雾安全团队建议建议开发合约代码时注意函数的访问权限控制，例如使用 OpenZeppelin 提供的 Ownable.sol
合约。


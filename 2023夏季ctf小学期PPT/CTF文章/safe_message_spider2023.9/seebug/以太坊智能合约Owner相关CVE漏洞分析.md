作者：Hcamael@知道创宇404区块链安全研究团队

### 背景

最近学习了下以太坊的智能合约，而且也看到挺多厂家pr智能合约相关的漏洞，其中[《ERC20智能合约整数溢出系列漏洞披露》](https://paper.seebug.org/626/
"《ERC20智能合约整数溢出系列漏洞披露》")文章中披露了6个CVE编号的漏洞，而这些漏洞都属于整型溢出漏洞范畴，其中5个漏洞均需要合约Owner才能触发利用。本文正是针对这些漏洞从合约代码及触发逻辑上做了详细分析，并提出了一些关于owner相关漏洞的思考。

### 漏洞分析

#### 1\. CVE-2018-11809

该漏洞被称为“超额购币”，相关合约（EthLendToken）源码:
<https://etherscan.io/address/0x80fB784B7eD66730e8b1DBd9820aFD29931aab03#code>

在合约代码中，`buyTokensPresale`和`buyTokensICO`两个函数都是存在整型上溢出的情况：

    
    
    function buyTokensPresale() public payable onlyInState(State.PresaleRunning)
        {
            // min - 1 ETH
            require(msg.value >= (1 ether / 1 wei));
            uint newTokens = msg.value * PRESALE_PRICE;
    
            require(presaleSoldTokens + newTokens <= PRESALE_TOKEN_SUPPLY_LIMIT);
    
            balances[msg.sender] += newTokens;
            supply+= newTokens;
            presaleSoldTokens+= newTokens;
            totalSoldTokens+= newTokens;
    
            LogBuy(msg.sender, newTokens);
        }
    
        function buyTokensICO() public payable onlyInState(State.ICORunning)
        {
            // min - 0.01 ETH
            require(msg.value >= ((1 ether / 1 wei) / 100));
            uint newTokens = msg.value * getPrice();
    
            require(totalSoldTokens + newTokens <= TOTAL_SOLD_TOKEN_SUPPLY_LIMIT);
    
            balances[msg.sender] += newTokens;
            supply+= newTokens;
            icoSoldTokens+= newTokens;
            totalSoldTokens+= newTokens;
    
            LogBuy(msg.sender, newTokens);
        }

溢出点：

    
    
    require(presaleSoldTokens + newTokens <= PRESALE_TOKEN_SUPPLY_LIMIT);
    require(totalSoldTokens + newTokens <= TOTAL_SOLD_TOKEN_SUPPLY_LIMIT);

拿`buyTokensPresale`函数举例，在理论上`presaleSoldTokens +
newTokens`存在整型上溢出漏洞，会导致绕过`require`判断，造成超额购币。

接下来，我们再仔细分析一下，如果造成整型上溢出，先来看看`presaleSoldTokens`变量的最大值

    
    
    uint public presaleSoldTokens = 0;
    require(presaleSoldTokens + newTokens <= PRESALE_TOKEN_SUPPLY_LIMIT);
    presaleSoldTokens+= newTokens;

该合约代码中，`presaleSoldTokens`变量相关的代码只有这三行，因为存在着require判断，所以不论`presaleSoldTokens +
newTokens`是否溢出，`presaleSoldTokens <= PRESALE_TOKEN_SUPPLY_LIMIT`恒成立，因为有着断言代码：

    
    
    assert(PRESALE_TOKEN_SUPPLY_LIMIT==60000000 * (1 ether / 1 wei));

所以，`presaleSoldTokens <= 60000000 * (1 ether / 1 wei)`，其中`1 ether / 1 wei =
1000000000000000000`，所以`max(presaleSoldTokens) == 6*(10^25)`

再来看看变量`newTokens`，该变量的值取决于用户输出，是用户可控变量，相关代码如下：

    
    
    uint newTokens = msg.value * PRESALE_PRICE;
    uint public constant PRESALE_PRICE = 30000;

如果我们向`buyTokensPresale`函数转账1 ether,
`newTokens`的值为`1000000000000000000*30000=3*(10^22)`

下面来计算一下，需要向该函数转账多少以太币，才能造成溢出

在以太坊智能合约中，`uint`默认代表的是`uint256`，取值范围是`0~2^256-1`，所以，需要`newTokens`的值大于`(2^256-1)-presaleSoldTokens`。

最后计算出，我们需要向`buyTokensPresale`函数转账:

    
    
    >>> (2**256-1)-(6*(10**25))/(3*(10**22))
    115792089237316195423570985008687907853269984665640564039457584007913129637935L

才可以造成整型上溢出，超额购币，整个以太坊公链，发展至今，以太币总余额有达到这个数吗？

虽然理论上该合约的确存在漏洞，但是实际却无法利用该漏洞

#### 2\. CVE-2018-11810

该类漏洞被称为：“超额定向分配”

相关事例（ LGO
）源码：<https://etherscan.io/address/0x123ab195dd38b1b40510d467a6a359b201af056f#code>

根据该漏洞的描述：

> 管理员绕过合约中规定的单地址发币上限，给指定地址分配超额的token

跟上一个漏洞相比，因为该漏洞存在于`onlyOwner`的函数中，只能Owner(管理员)才能调用该漏洞，所以我认为该类漏洞可以算做是“后门“类漏洞。

所以该类漏洞的利用有两个思路：

  1. Owner留下来的“后门”，供自己使用，专门用来坑合约的其他使用者(所谓的”蜜罐合约“，就是这种情况)
  2. 该合约有其他漏洞，能让自己成为Owener，或者可以说，结合提权漏洞进行利用

首先，我们先假设自己就是Owner，来研究该漏洞的利用流程，以下是存在漏洞的函数：

    
    
    function allocate(address _address, uint256 _amount, uint8 _type) public onlyOwner returns (bool success) {
            // one allocations by address
            require(allocations[_address] == 0);
    
            if (_type == 0) { // advisor
                // check allocated amount
                require(advisorsAllocatedAmount + _amount <= ADVISORS_AMOUNT);
                // increase allocated amount
                advisorsAllocatedAmount += _amount;
                // mark address as advisor
                advisors[_address] = true;
            } else if (_type == 1) { // founder
                // check allocated amount
                require(foundersAllocatedAmount + _amount <= FOUNDERS_AMOUNT);
                // increase allocated amount
                foundersAllocatedAmount += _amount;
                // mark address as founder
                founders[_address] = true;
            } else {
                // check allocated amount
                require(holdersAllocatedAmount + _amount <= HOLDERS_AMOUNT + RESERVE_AMOUNT);
                // increase allocated amount
                holdersAllocatedAmount += _amount;
            }
            // set allocation
            allocations[_address] = _amount;
            initialAllocations[_address] = _amount;
    
            // increase balance
            balances[_address] += _amount;
    
            // update variables for bonus distribution
            for (uint8 i = 0; i < 4; i++) {
                // increase unspent amount
                unspentAmounts[BONUS_DATES[i]] += _amount;
                // initialize bonus eligibility
                eligibleForBonus[BONUS_DATES[i]][_address] = true;
                bonusNotDistributed[BONUS_DATES[i]][_address] = true;
            }
    
            // add to initial holders list
            initialHolders.push(_address);
    
            Allocate(_address, _amount);
    
            return true;
        }

该合约相当于一个代币分配的协议，Owner可以随意给人分配代币，但是不能超过如下的限制：

代币的总额: `uint256 constant INITIAL_AMOUNT = 100 * onePercent;` 给顾问5%: `uint256
constant ADVISORS_AMOUNT = 5 * onePercent;` 创始人要15%: `uint256 constant
FOUNDERS_AMOUNT = 15 * onePercent;` 销售出了60%: `uint256 constant HOLDERS_AMOUNT
= 60 * onePercent;` 保留了20%: `uint256 constant RESERVE_AMOUNT = 20 *
onePercent;`

对应到下面三个判断：

    
    
    require(advisorsAllocatedAmount + _amount <= ADVISORS_AMOUNT);
    require(foundersAllocatedAmount + _amount <= FOUNDERS_AMOUNT);
    require(holdersAllocatedAmount + _amount <= HOLDERS_AMOUNT + RESERVE_AMOUNT);

跟上一个CVE一样，该漏洞本质上也是整型上溢出，但是上一个漏洞，用户可控的变量来至于向合约转账的以太币的数值，所以在实际情况中，基本不可能利用。但是在该漏洞中，用户可控的变量`_amount`，是由用户任意输入，使得该漏洞得以实现

下面，利用漏洞给顾问分配超过5%的代币：

  1. 给顾问A分配`2*onePercent`数量的代币：`allocte("0xbd08e0cddec097db7901ea819a3d1fd9de8951a2", 362830104000000, 0)`

![](https://images.seebug.org/content/images/2018/06/9ed1b0c1-ffa1-4bb5-98e7-c02c66bd366a.png-w331s)

  1. 给顾问B分配一个巨大数量的代币，导致溢出：`allocte("0x63ac545c991243fa18aec41d4f6f598e555015dc", 115792089237316195423570985008687907853269984665640564039457583645083025639937, 0)`

  2. 查看顾问B的代币数：`balanceOf("0x63ac545c991243fa18aec41d4f6f598e555015dc") => 115792089237316195423570985008687907853269984665640564039457583645083025639937`

![](https://images.seebug.org/content/images/2018/06/51dd8d8d-3e71-4a0e-930b-9e7bcaaed69b.png-w331s)

经过后续的审计，发现该合约代码中的`own`变量只能由Owner修改，所以该漏洞只能被Owner利用

#### 3\. CVE-2018-11809

该漏洞被称为：”超额铸币“，但实际和之前的漏洞没啥区别

含有该漏洞的合约Playkey
(PKT）源码：<https://etherscan.io/address/0x2604fa406be957e542beb89e6754fcde6815e83f#code>

存在漏洞的函数:

    
    
      function mint(address _holder, uint256 _value) external icoOnly {
        require(_holder != address(0));
        require(_value != 0);
        require(totalSupply + _value <= tokenLimit);
    
        balances[_holder] += _value;
        totalSupply += _value;
        Transfer(0x0, _holder, _value);
      }

比上一个漏洞的代码还更简单，只有ico(相当于之前的owner)能执行该函数，阅读全篇代码，ico是在合约部署的时候由创建人设置的，后续无法更改，所以该漏洞只能被ico(owner)利用

该合约本身的意图是，ico能随意给人分配代币，但是发行代币的总额度不能超过`tokenLimit`，但是通过整型上溢出漏洞，能让ico发行无限个代币，利用流程如下：

  1. 部署合约，设置ico为自己账户地址，设置发行代币的上限为100000: `PTK("0x8a0b358029b81a52487acfc776fecca3ce2fbf4b", 100000)`

![](https://images.seebug.org/content/images/2018/06/ed4a80ce-de7a-47a2-bcfd-92ccb4fa83a2.png-w331s)

  1. 给账户A分配一定额度的代币: `mint("0xbd08e0cddec097db7901ea819a3d1fd9de8951a2", 50000)`

![](https://images.seebug.org/content/images/2018/06/e9f8775b-378c-462a-aaea-1efa67ec9b0e.png-w331s)

  1. 利用整型上溢出给账户B分配大量的代币: `mint("0x63ac545c991243fa18aec41d4f6f598e555015dc", 115792089237316195423570985008687907853269984665640564039457584007913129589938)`
  2. 查看账户B的余额: `balanceOf("0x63ac545c991243fa18aec41d4f6f598e555015dc") => 115792089237316195423570985008687907853269984665640564039457584007913129589938`

![](https://images.seebug.org/content/images/2018/06/cdc0e9e6-5c14-4153-841c-4a3a7e19c82f.png-w331s)

#### 4\. CVE-2018-11812

该漏洞被称为：“随意铸币”

相关漏洞合约 Polymath
(POLY)源码：<https://etherscan.io/address/0x9992ec3cf6a55b00978cddf2b27bc6882d88d1ec#code>

具有漏洞的函数:

    
    
    function mintToken(address target, uint256 mintedAmount) onlyOwner {
        balanceOf[target] += mintedAmount;
        Transfer(0, owner, mintedAmount);
        Transfer(owner, target, mintedAmount);
    }

这个漏洞很简单，也很好理解，Owner可以随意增加任意账户的代币余额，可以想象成，银行不仅能随心所欲的印钞票，还能随心所以的扣你的钱

因为Owner是在合约部署的时候被设置成合约部署者的账户地址，之后也只有Owner能修改Own账户地址，所以该漏洞只能被Owner利用

这个我觉得与其说是漏洞，不如说是Owner留下的“后门”

#### 5\. CVE-2018-11687

该漏洞被称为：“下溢增持”

相关漏洞合约Bitcoin Red
(BTCR)源码：<https://etherscan.io/address/0x6aac8cb9861e42bf8259f5abdc6ae3ae89909e11#code>

相关的漏洞函数:

    
    
    function distributeBTR(address[] addresses) onlyOwner {
        for (uint i = 0; i < addresses.length; i++) {
            balances[owner] -= 2000 * 10**8;
            balances[addresses[i]] += 2000 * 10**8;
            Transfer(owner, addresses[i], 2000 * 10**8);
        }
    }

该合约限制了发行代币的上限: `uint256 _totalSupply = 21000000 * 10**8;`

并且在合约部署的时候把能发行的合约都分配给了Owner: `balances[owner] = 21000000 * 10**8;`

然后Owner可以把自己账户的代币，任意分配给其他账户，分配的代码就是上面的函数，给别人分配一定额度的代币时，自己减去相应额度的代币，保证该合约总代币数不变

但是因为没有判断Owner的账户是否有足够的余额，所以导致了减法的整型下溢出，同样也存在整型上溢出，但是因为uint256的上限是`2^256-1`，但是利用过于繁琐，需要运行非常多次的`balances[addresses[i]]
+= 2000 * 10**8;`

而减法的利用就很简单了，或者我们可以根本不考虑这个减法，Owner可以给任意账户分配`2000 *
10**8`倍数的代币，该漏洞的功能和上一个漏洞的基本一致，可以任意发行代币或者减少其他账户的代币数

因为Owner是在合约部署的时候被设置为部署合约人的账户地址，后续没有修改own的功能，所以该漏洞也只有Owner可以利用

#### 6\. CVE-2018-11811

该漏洞被称为：“高卖低收”

相关漏洞合约 Internet Node Token
(INT)源码：<https://etherscan.io/address/0x0b76544f6c413a555f309bf76260d1e02377c02a>

在该CVE的描述中，存在漏洞的函数是:

    
    
    function sell(uint256 amount) {
      require(this.balance >= amount * sellPrice);      // checks if the contract has enough ether to buy
      _transfer(msg.sender, this, amount);              // makes the transfers
      msg.sender.transfer(amount * sellPrice);          // sends ether to the seller. It's important to do this last to avoid recursion attacks
    }

并且描述的漏洞原理是:

> sellPrice被修改为精心构造的大数后，可导致amount *
> sellPrice的结果大于整数变量(uint256)最大值，发生整数溢出，从而变为一个极小值甚至归零`

相关函数如下：

    
    
    function buy() payable {
      uint amount = msg.value / buyPrice;               // calculates the amount
      _transfer(this, msg.sender, amount);              // makes the transfers
    }
    
    function setPrices(uint256 newSellPrice, uint256 newBuyPrice) onlyOwner {
      sellPrice = newSellPrice;
      buyPrice = newBuyPrice;
    }

该漏洞的利用流程如下：

  1. 管理员设置`buyPrice = 1 ether`, `sellPrice = 2^255`
  2. 用户A买了两个以太币价格的代币: buy({value:toWei(2)})
  3. 用户A卖掉两个代币: send(2)
  4. 用户A将会收到`2*sellPrice = 2^256`价格的Wei
  5. 但是因为`transfer`的参数是uint256, 所以发生了溢出，用户A实际得到0Wei

表面上看这个漏洞还是有危害的，但是我们仔细想想，这个漏洞其实是比较多余的，我们可以使用更简单的步骤达到相同的目的:

  1. 管理员设置`buyPrice = 1 ether`, `sellPrice = 0`
  2. 用户A买了两个以太币价格的代币: buy({value:toWei(2)})
  3. 用户A卖掉两个代币: send(2)
  4. 用户A将会收到`2*sellPrice = 0`价格的Wei

我认为该合约最大的问题在于Owner可以随意设置代币的买入和卖出价格。

顺带提一下这个问题也是前面peckshield公布的“tradeTrap”漏洞(<https://peckshield.com/2018/06/11/tradeTrap/>)提到的“Security
Issue 2: Manipulatable Prices and Unfair Arbitrage” 是同一个问题。

### 总结

经过上面的分析，在这6个CVE中，虽然都是整型溢出，但第一个CVE属于理论存在，但实际不可实现的整型上溢出漏洞，剩下5个CVE都属于对管理者有利，会损害用户利用的漏洞，或者可以称为“后门”，也正是这个原因也导致了一些关于需要Owner触发漏洞意义讨论

如果我们把智能合约类比为传统合同，智能合约代码就是传统合同的内容，但是和传统的合同相比，智能合约拥有三个利益团体，一个是编写合约代码的人(智能合约中的Owner，或者我们可以称为甲方)，使用该合约的其他人(我们可以称为乙方)，跟该智能合约无关的其他人(比如利用合约漏洞获利的黑客)。从这个角度来看Owner条件下触发的漏洞在理论上是可以损害到乙方的利益，如对于存在“恶意”的owner或者黑客配合其他漏洞获取到owner权限的场景上来说，还是有一定意义的。

另外从整个上市交易流程来看，我们还需要关注到“交易所”这个环节，交易所的风控体系在某种程度上可以限制这种“恶意”的owner或黑客利用。

由此可见合约审计对于“甲方”、“乙方”、交易所都有重要的意义。

知道创宇智能合约安全审计：<http://www.scanv.com/lca/index.html>

欢迎扫码咨询：
![](https://images.seebug.org/content/images/2018/06/95677dc3-cb3e-474e-832e-8b79ec73bfa9.png-w331s)

### 参考链接

  1. <https://paper.seebug.org/626/>
  2. <https://mp.weixin.qq.com/s/6PKWXJXAKVCu5bJYlKy2Aw>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/627/>


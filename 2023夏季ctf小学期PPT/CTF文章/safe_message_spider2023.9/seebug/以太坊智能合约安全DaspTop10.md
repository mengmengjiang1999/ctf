译者：爱上平顶⼭  
来源：[慢雾区](https://t.zsxq.com/rv7EAIi "慢雾区")  
原文链接：<https://www.dasp.co/>

这是分布式应⽤安全项⽬（或DASP）2018 年排名前10的漏洞第⼀次迭代

该项⽬是[NCC集团](https://www.nccgroup.trust/uk/
"NCC集团")的⼀项举措。这是⼀个开放的合作项⽬，致⼒于发现安全社区内的智能合约漏洞。要参与，请[加⼊github⻚⾯](https://github.com/CryptoServices/dasp
"加⼊github⻚⾯")。

#### 1.重⼊漏洞

也被称为 或与空⽩竞争，递归调⽤漏洞，未知调⽤

> 这种漏洞在很多时候被很多不同的⼈忽略：审阅者倾向于⼀次⼀个地审查函数，并且假定保护⼦例程的调⽤将安全并按预期运⾏。 Phil Daian

重⼊攻击，可能是最着名的以太坊漏洞，第⼀次被发现时，每个⼈都感到惊讶。它在数百万美元的抢劫案中⾸次亮相，导致了以太坊的分叉。当初始执⾏完成之前，外部合同调⽤被允许对调⽤合同进⾏新的调⽤时，就会发⽣重新进⼊。对于函数来说，这意味着合同状态可能会在执⾏过程中因为调⽤不可信合同或使⽤具有外部地址的低级函数⽽发⽣变化。

损失：估计为350万ETH（当时约为5000万美元）

发现时间表：

2016年6⽉5⽇ [Christian
Reitwiessner发现了⼀个坚定的反模式](https://blog.ethereum.org/2016/06/10/smart-contract-security/ "Christian Reitwiessner发现了⼀个坚定的反模式")  
2016年6⽉9⽇ [更多以太坊攻击：Race-To-Empty是真正的交易（vessenes.com）](http://vessenes.com/more-ethereum-attacks-race-to-empty-is-the-real-deal/ "更多以太坊攻击：Race-To-Empty是真正的交易（vessenes.com）")  
2016年6⽉12⽇
[在以太坊智能合约'递归调⽤'错误发现（blog.slock.it）之后，没有DAO资⾦⾯临⻛险。](https://blog.slock.it/no-dao-funds-at-risk-following-the-ethereum-smart-contract-recursive-call-bug-discovery-29f482d348b "在以太坊智能合约'递归调⽤'错误发现（blog.slock.it）之后，没有DAO资⾦⾯临⻛险。")  
2016年6⽉17⽇
[我认为TheDAO现在正在流失（reddit.com）](https://www.reddit.com/r/ethereum/comments/4oi2ta/i_think_thedao_is_getting_drained_right_now/
"我认为TheDAO现在正在流失（reddit.com）")  
2016年8⽉24⽇ [DAO的历史和经验教训（blog.sock.it）](https://blog.slock.it/the-history-of-the-dao-and-lessons-learned-d06740f8cfa5 "DAO的历史和经验教训（blog.sock.it）")

真实世界影响：

  * [DAO](https://en.wikipedia.org/wiki/The_DAO_\(organization\) "DAO")

示例：

  1. ⼀个聪明的合同跟踪⼀些外部地址的平衡，并允许⽤户通过其公共资⾦检索`withdraw()`功能。
  2. ⼀个恶意的智能合同使⽤`withdraw()`函数检索其全部余额。
  3. 在更新恶意合同的余额之前，受害者合同执⾏`call.value(amount)()` 低级别函数将以太⽹发送给恶意合同。
  4. 该恶意合同有⼀个⽀付`fallback()`接受资⾦的功能，然后回调到受害者合同的`withdraw()`功能。
  5. 第⼆次执⾏会触发资⾦转移：请记住，恶意合同的余额尚未从⾸次提款中更新。结果， 恶意合同第⼆次成功退出了全部余额。

代码示例：

以下函数包含易受重⼊攻击影响的函数。当低级别`call()`函数向`msg.sender`地址发送ether时，它变得易受攻击;
如果地址是智能合约，则付款将触发其备⽤功能以及剩余的交易⽓体：

    
    
    function withdraw(uint _amount) {
    require(balances[msg.sender] >= _amount);
     msg.sender.call.value(_amount)();
     balances[msg.sender] -= _amount;
    }

其他资源：

  * [DAO智能合约](https://etherscan.io/address/0xbb9bc244d798123fde783fcc1c72d3bb8c189413#code "DAO智能合约")
  * [分析DAO的利⽤](http://hackingdistributed.com/2016/06/18/analysis-of-the-dao-exploit/ "分析DAO的利⽤")
  * [简单的DAO代码示例](http://blockchain.unica.it/projects/ethereum-survey/attacks.html#simpledao "简单的DAO代码示例")
  * [重⼊代码示例](https://github.com/trailofbits/not-so-smart-contracts/tree/master/reentrancy "重⼊代码示例")
  * [有⼈试图利⽤我们的智能合约中的⼀个缺陷，盗取它的⼀切](https://blog.citymayor.co/posts/how-someone-tried-to-exploit-a-flaw-in-our-smart-contract-and-steal-all-of-its-ether/ "有⼈试图利⽤我们的智能合约中的⼀个缺陷，盗取它的⼀切")

#### 2.访问控制

> 通过调⽤initWallet函数，可以将Parity Wallet库合约变为常规多sig钱包并成为它的所有者。 Parity

访问控制问题在所有程序中都很常⻅，⽽不仅仅是智能合同。事实上，这是[OWASP排名前10位](https://www.owasp.org/images/7/72/OWASP_Top_10-2017_%28en%29.pdf.pdf
"OWASP排名前10位")的[第5位](https://www.owasp.org/images/7/72/OWASP_Top_10-2017_%28en%29.pdf.pdf
"第5位")。⼈们通常通过其公共或外部功能访问合同的功能。尽管不安全的可视性设置会给攻击者直接访问合同的私有价值或逻辑的⽅式，但访问控制旁路有时更加微妙。这些漏洞可能发⽣在合约使⽤已弃⽤tx.origin的验证调⽤者时，⻓时间处理⼤型授权逻辑require并delegatecall在[代理库](https://blog.zeppelin.solutions/proxy-libraries-in-solidity-79fbe4b970fd
"代理库")或[代理合约中](https://blog.indorse.io/ethereum-upgradeable-smart-contract-strategies-456350d0557c "代理合约中")鲁莽使⽤。

损失：估计为150,000 ETH（当时约3000万美元）

真实世界影响：

  * [奇偶校验错误1](http://paritytech.io/the-multi-sig-hack-a-postmortem/ "奇偶校验错误1")
  * [奇偶校验错误2](http://paritytech.io/a-postmortem-on-the-parity-multi-sig-library-self-destruct/ "奇偶校验错误2")
  * [Rubixi](https://blog.ethereum.org/2016/06/19/thinking-smart-contract-security/ "Rubixi")

示例：

  1. ⼀个聪明的合同指定它初始化它作为合同的业主的地址。这是授予特殊特权的常⻅模式，例如提取合同资⾦的能⼒。
  2. 不幸的是，初始化函数可以被任何⼈调⽤，即使它已经被调⽤。允许任何⼈成为合同的拥有者并获得资⾦。

代码示例：

在下⾯的例⼦中，契约的初始化函数将函数的调⽤者设置为它的所有者。然⽽，逻辑与合约的构造函数分离，并且不记录它已经被调⽤的事实。

    
    
    function initContract() public {
     owner = msg.sender;
    }

在Parity multi-sig钱包中，这个初始化函数与钱包本身分离并在“库”合同中定义。⽤户需要通过调⽤库的函数来初始化⾃⼰的钱包delegateCall。不幸的是，在我们的例⼦中，函数没有检查钱包是否已经被初始化。更糟糕的是，由于图书馆是⼀个聪明的合同，任何⼈都可以⾃⾏初始化图书馆并要求销毁。

其他资源：

  * [修复Parity多信号钱包bug 1](https://github.com/paritytech/parity/pull/6103/files "修复Parity多信号钱包bug 1")
  * [奇偶校验安全警报2](http://paritytech.io/security-alert-2/ "奇偶校验安全警报2")
  * [在奇偶钱包multi-sig hack上](https://blog.zeppelin.solutions/on-the-parity-wallet-multisig-hack-405a8c12e8f7 "在奇偶钱包multi-sig hack上")
  * [不受保护的功能](https://github.com/trailofbits/not-so-smart-contracts/tree/master/unprotected_function "不受保护的功能")
  * [Rubixi的智能合约](https://etherscan.io/address/0xe82719202e5965Cf5D9B6673B7503a3b92DE20be#code "Rubixi的智能合约")

#### 3.算术问题

也被称为 整数溢出和整数下溢

> 溢出情况会导致不正确的结果，特别是如果可能性未被预期，可能会影响程序的可靠性和安全性。 Jules Dourlens

整数溢出和下溢不是⼀类新的漏洞，但它们在智能合约中尤其危险，其中⽆符号整数很普遍，⼤多数开发⼈员习惯于简单int类型（通常是有符号整数）。如果发⽣溢出，许多良性代码路径成为盗窃或拒绝服务的载体。

真实世界影响：

  * [DAO](http://blockchain.unica.it/projects/ethereum-survey/attacks.html "DAO")
  * [BatchOverflow（多个令牌）](https://peckshield.com/2018/04/22/batchOverflow/ "BatchOverflow（多个令牌）")
  * [ProxyOverflow（多个令牌）](https://peckshield.com/2018/04/25/proxyOverflow/ "ProxyOverflow（多个令牌）")

示例：

  1. ⼀个聪明的合同的`withdraw()`功能，您可以为您的余额仍是⼿术后积极检索，只要捐赠合同醚。
  2. ⼀个攻击者试图收回⽐他或她的当前余额多。
  3. 该`withdraw()`功能检查的结果总是正数，允许攻击者退出超过允许。由此产⽣的余额下降，并成为⽐它应该更⼤的数量级。

代码示例：

最直接的例⼦是⼀个不检查整数下溢的函数，允许您撤销⽆限量的标记：

    
    
    function withdraw(uint _amount) {
    require(balances[msg.sender] - _amount > 0);
     msg.sender.transfer(_amount);
     balances[msg.sender] -= _amount;
    }

第⼆个例⼦（在[⽆益的Solidity编码竞赛](https://github.com/Arachnid/uscc/tree/master/submissions-2017/doughoyte
"⽆益的Solidity编码竞赛")期间被发现）是由于数组的⻓度由⽆符号整数表示的事实促成的错误的错误：

    
    
    function popArrayOfThings() {
    require(arrayOfThings.length >= 0);
     arrayOfThings.length--;
    }

第三个例⼦是第⼀个例⼦的变体，其中两个⽆符号整数的算术结果是⼀个⽆符号整数：

    
    
    function votes(uint postId, uint upvote, uint downvotes) {
    if (upvote - downvote < 0) {
     deletePost(postId)
     }
    }

第四个示例提供了即将弃⽤的var关键字。由于var将⾃身改变为包含指定值所需的最⼩类型，因此它将成为uint8保持值0.如果循环的迭代次数超过255次，它将永远达不到该数字，并且在执⾏运⾏时停⽌出⽓：

    
    
    for (var i = 0; i < somethingLarge; i ++) { 
    // ...
    }

其他资源：

  * [SafeMath防⽌溢出](https://ethereumdev.io/safemath-protect-overflows/ "SafeMath防⽌溢出")
  * [整数溢出代码示例](https://github.com/trailofbits/not-so-smart-contracts/tree/master/integer_overflow "整数溢出代码示例")

#### 4.未检查返回值的低级别调⽤

也称为 或与静默失败发送，未经检查发送

> 尽可能避免使⽤低级别的“调⽤”。如果返回值处理不当，它可能会导致意外的⾏为。Remix

其中的密实度的更深层次的特点是低级别的功能`call()`，`callcode()`，`delegatecall()`和`send()`。他们在计算错误⽅⾯的⾏为与其他Solidity函数完全不同，因为他们不会传播（或冒泡），并且不会导致当前执⾏的全部回复。相反，他们会返回⼀个布尔值设置为false，并且代码将继续运⾏。这可能会让开发⼈员感到意外，如果未检查到这种低级别调⽤的返回值，则可能导致失败打开和其他不想要的结果。请记住，发送可能会失败！

真实世界影响：

  * [以太之王](https://www.kingoftheether.com/postmortem.html "以太之王")
  * [Etherpot](https://www.dasp.co/ "Etherpot")

代码示例：

下⾯的代码是⼀个当忘记检查返回值时会出错的例⼦send()。如果调⽤⽤于将ether发送给不接受它们的智能合约（例如，因为它没有应付回退功能），则EVM将⽤其替换其返回值false。由于在我们的例⼦中没有检查返回值，因此函数对合同状态的更改不会被恢复，并且etherLeft变量最终会跟踪⼀个不正确的值：

    
    
    function withdraw(uint256 _amount) public {
    require(balances[msg.sender] >= _amount);
     balances[msg.sender] -= _amount;
     etherLeft -= _amount;
     msg.sender.send(_amount);
    }

其他资源：

  * [未经检查的外部写⼊](https://github.com/trailofbits/not-so-smart-contracts/tree/master/unchecked_external_call "未经检查的外部写⼊")
  * [扫描“未经检查 - 发送”错误的现场以太坊合同](http://hackingdistributed.com/2016/06/16/scanning-live-ethereum-contracts-for-bugs/ "扫描“未经检查 - 发送”错误的现场以太坊合同")

#### 5.拒绝服务

包括达到gas上限，意外抛出，意外杀死，访问控制违规

> 我不⼩⼼杀了它。 devops199 on the Parity multi-sig wallet

在以太坊的世界中，拒绝服务是致命的：尽管其他类型的应⽤程序最终可以恢复，但智能合同可以通过
其中⼀种攻击永远脱机。许多⽅⾯导致拒绝服务，包括在作为交易接受⽅时恶意⾏为，⼈为地增加计算
功能所需的⽓体，滥⽤访问控制访问智能合约的私⼈组件，利⽤混淆和疏忽，...这类攻击包括许多不同的变体，并可能在未来⼏年看到很多发展。

损失：估计为514,874 ETH（当时约3亿美元）

真实世界影响：

  * [政府](https://www.reddit.com/r/ethereum/comments/4ghzhv/governmentals_1100_eth_jackpot_payout_is_stuck/ " 政府")
  * [奇偶校验多信号钱包](http://paritytech.io/a-postmortem-on-the-parity-multi-sig-library-self-destruct/ "奇偶校验多信号钱包")

示例：

  1. ⼀个拍卖合同允许其⽤户在竞标不同的资产。
  2. 为了投标，⽤户必须bid(uint object)⽤期望的以太数来调⽤函数。拍卖合同将把以太保存在第三⽅保存中，直到对象的所有者接受投标或初始投标⼈取消。这意味着拍卖合同必须在其余额中保留未解决出价的全部价值。
  3. 该拍卖合同还包含⼀个withdraw(uint amount)功能，它允许管理员从合同获取资⾦。随着函数发送amount到硬编码地址，开发⼈员决定公开该函数。
  4. ⼀个攻击者看到了潜在的攻击和调⽤功能，指挥所有的合同的资⾦为其管理员。这破坏了托管承诺并阻⽌了所有未决出价。
  5. 虽然管理员可能会将托管的钱退还给合同，但攻击者可以通过简单地撤回资⾦继续进⾏攻击。

代码示例：

在下⾯的例⼦中（受以太王的启发），游戏合同的功能可以让你成为总统，如果你公开贿赂前⼀个。不
幸的是，如果前总统是⼀个聪明的合同，并导致⽀付逆转，权⼒的转移将失败，恶意智能合同将永远保 持总统。听起来像是对我的独裁：

    
    
    function becomePresident() payable {
     require(msg.value >= price); // must pay the price to become president
     president.transfer(price); // we pay the previous president
     president = msg.sender; // we crown the new president
     price = price * 2; // we double the price to become president
    }

在第⼆个例⼦中，调⽤者可以决定下⼀个函数调⽤将奖励谁。由于for循环中有昂贵的指令，攻击者可
能会引⼊太⼤的数字来迭代（由于以太坊中的⽓体阻塞限制），这将有效地阻⽌函数的功能。

    
    
    function selectNextWinners(uint256 _largestWinner) {
    for(uint256 i = 0; i < largestWinner, i++) { 
     // heavy code
     }
     largestWinner = _largestWinner;
    }

其他资源：

  * [奇偶Multisig被⿊客⼊侵。再次](https://medium.com/chain-cloud-company-blog/parity-multisig-hack-again-b46771eaa838 "奇偶Multisig被⿊客⼊侵。再次")
  * [关于Parity multi-sig钱包漏洞和Cappasity令牌众包的声明](https://blog.artoken.io/statement-on-the-parity-multi-sig-wallet-vulnerability-and-the-cappasity-artoken-crowdsale-b3a3fed2d567 "关于Parity multi-sig钱包漏洞和Cappasity令牌众包的声明")

#### 6.错误随机性

也被称为 没有什么是秘密的

> 合同对block.number年龄没有⾜够的验证，导致400个ETH输给⼀个未知的玩家，他在等待256个街区之前揭示了可预测的中奖号码。 Arseny
> Reutov

以太坊的随机性很难找到。虽然Solidity提供的功能和变量可以访问明显难以预测的值，但它们通常要么⽐看起来更公开，要么受到矿⼯影响。由于这些随机性的来源在⼀定程度上是可预测的，所以恶意⽤户通常可以复制它并依靠其不可预知性来攻击该功能。

损失：超过400 ETH

真实世界影响：

  * [SmartBillions彩票](https://www.reddit.com/r/ethereum/comments/74d3dc/smartbillions_lottery_contract_just_got_hacked/ "SmartBillions彩票")
  * [运⾏](https://medium.com/@hrishiolickel/why-smart-contracts-fail-undiscovered-bugs-and-what-we-can-do-about-them-119aa2843007 "运⾏")

示例：

  1. 甲智能合同使⽤块号作为随机有游戏⽤的源。
  2. 攻击者创建⼀个恶意合约来检查当前的块号码是否是赢家。如果是这样，它就称为第⼀个智能合约以获胜; 由于该呼叫将是同⼀交易的⼀部分，因此两个合约中的块编号将保持不变。
  3. 攻击者只需要调⽤她的恶意合同，直到获胜。

代码示例：

在第⼀个例⼦中，a private
seed与iteration数字和keccak256散列函数结合使⽤来确定主叫⽅是否获胜。Eventhough的seed是private，它必须是通过交易在某个时间点设置，并因此在blockchain可⻅。

    
    
    uint256 private seed;
    function play() public payable {
     require(msg.value >= 1 ether);
     iteration++;
    uint randomNumber = uint(keccak256(seed + iteration));
    if (randomNumber % 2 == 0) {
     msg.sender.transfer(this.balance); 
     }
    }

在这第⼆个例⼦中，block.blockhash正被⽤来⽣成⼀个随机数。如果将该哈希值blockNumber设置为当前值block.number（出于显⽽易⻅的原因）并且因此设置为，则该哈希值未知0。在blockNumber过去设置为超过256个块的情况下，它将始终为零。最后，如果它被设置为⼀个以前的不太旧的区块号码，另⼀个智能合约可以访问相同的号码并将游戏合同作为同⼀交易的⼀部分进⾏调⽤。

    
    
    function play() public payable {
    require(msg.value >= 1 ether);
    if (block.blockhash(blockNumber) % 2 == 0) {
     msg.sender.transfer(this.balance);
     }
    }

其他资源： \- [在以太坊智能合约中预测随机数](https://blog.positive.com/predicting-random-numbers-in-ethereum-smart-contracts-e5358c6b8620 "在以太坊智能合约中预测随机数") \-[在以太坊随机](https://blog.otlw.co/random-in-ethereum-50eefd09d33e "在以太坊随机")

#### 7.前台运⾏

也被称为 检查时间与使⽤时间（TOCTOU），竞争条件，事务顺序依赖性（TOD）

> 事实证明，只需要150⾏左右的Python就可以获得⼀个正常运⾏的算法。 Ivan Bogatyy

由于矿⼯总是通过代表外部拥有地址（EOA）的代码获得燃⽓费⽤，因此⽤户可以指定更⾼的费⽤以便
更快地开展交易。由于以太坊区块链是公开的，每个⼈都可以看到其他⼈未决交易的内容。这意味着，
如果某个⽤户正在揭示拼图或其他有价值的秘密的解决⽅案，恶意⽤户可以窃取解决⽅案并以较⾼的费
⽤复制其交易，以抢占原始解决⽅案。如果智能合约的开发者不⼩⼼，这种情况会导致实际的和毁灭性 的前端攻击。

真实世界影响：

  * [班柯](https://hackernoon.com/front-running-bancor-in-150-lines-of-python-with-ethereum-api-d5e2bfd0d798 "班柯")
  * [ERC-20](https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/ "ERC-20")
  * [运⾏](https://www.dasp.co/ "运⾏")

示例：

  1. ⼀个聪明的合同发布的RSA号（N = prime1 x prime2）。
  2. 对其submitSolution()公共功能的调⽤与权利prime1并prime2奖励来电者。
  3. Alice成功地将RSA编号考虑在内，并提交解决⽅案。
  4. 有⼈在⽹络上看到爱丽丝的交易（包含解决⽅案）等待被开采，并以较⾼的天然⽓价格提交。
  5. 由于⽀付更⾼的费⽤，第⼆笔交易⾸先被矿⼯收回。该攻击者赢得奖⾦。

其他资源：

  *     * [在以太坊智能合约中预测随机数](https://blog.positive.com/predicting-random-numbers-in-ethereum-smart-contracts-e5358c6b8620 "在以太坊智能合约中预测随机数")
  *     * [虚拟和解的前卫，悲痛和危险](https://blog.0xproject.com/front-running-griefing-and-the-perils-of-virtual-settlement-part-1-8554ab283e97 "虚拟和解的前卫，悲痛和危险")
  *     * [Frontrunning Bancor](https://www.youtube.com/watch?v=RL2nE3huNiI "Frontrunning Bancor")

#### 8.时间篡改

也被称为 时间戳依赖

> 如果⼀位矿⼯持有合同的股份，他可以通过为他正在挖掘的矿区选择合适的时间戳来获得优势。 Nicola Atzei，Massimo
> Bartoletti和Tiziana Cimoli

从锁定令牌销售到在特定时间为游戏解锁资⾦，合同有时需要依赖当前时间。这通常通过Solidity中的
block.timestamp别名或其别名完成now。但是，这个价值从哪⾥来？来⾃矿⼯！由于交易的矿⼯在报告采矿发⽣的时间⽅⾯具有回旋余地，所以良好的智能合约将避免强烈依赖所宣传的时间。请注意，
block.timestamp有时（错误）也会在随机数的⽣成中使⽤，[如＃6所述。错误的随机性](https://www.dasp.co/#item-6
"如＃6所述。错误的随机性")。

真实世界影响：

[政府](http://blockchain.unica.it/projects/ethereum-survey/attacks.html#governmental "政府")

示例：

  1. ⼀场⽐赛在今天午夜付出了第⼀名球员。
  2. 恶意矿⼯包括他或她试图赢得⽐赛并将时间戳设置为午夜。
  3. 在午夜之前，矿⼯最终挖掘该块。当前的实时时间“⾜够接近”到午夜（当前为该块设置的时间戳），⽹络上的其他节点决定接受该块。

代码示例：

以下功能只接受特定⽇期之后的呼叫。由于矿⼯可以影响他们区块的时间戳（在⼀定程度上），他们可以尝试挖掘⼀个包含他们交易的区块，并在未来设定⼀个区块时间戳。如果⾜够接近，它将在⽹络上被接受，交易将在任何其他玩家试图赢得⽐赛之前给予矿⼯以太：

    
    
    function play() public {
    require(now > 1521763200 && neverPlayed == true);
     neverPlayed = false;
     msg.sender.transfer(1500 ether);
    }

其他资源：

  * [对以太坊智能合约的攻击调查](https://eprint.iacr.org/2016/1007 "对以太坊智能合约的攻击调查")
  * [在以太坊智能合约中预测随机数](https://blog.positive.com/predicting-random-numbers-in-ethereum-smart-contracts-e5358c6b8620 "在以太坊智能合约中预测随机数")
  * [让智能合约变得更聪明](https://blog.acolyer.org/2017/02/23/making-smart-contracts-smarter/ "让智能合约变得更聪明")

#### 9.短地址攻击

也被称为 涉及⾮连锁问题，客户端漏洞

> 为令牌传输准备数据的服务假定⽤户将输⼊20字节⻓的地址，但实际上并未检查地址的⻓度。 PawełBylica

短地址攻击是EVM本身接受不正确填充参数的副作⽤。攻击者可以通过使⽤专⻔制作的地址来利⽤这⼀点，使编码错误的客户端在将它们包含在事务中之前不正确地对参数进⾏编码。这是EVM问题还是客户问题？是否应该在智能合约中修复？尽管每个⼈都有不同的观点，但事实是，这个问题可能会直接影响很多以太⽹。虽然这个漏洞还没有被⼤规模利⽤，但它很好地证明了客户和以太坊区块链之间的交互带来的问题。其他脱链问题存在：重要的是以太坊⽣态系统对特定的javascript前端，浏览器插件和公共节点的深度信任。臭名昭着的链外利⽤被⽤于[Coindash
ICO的⿊客](https://medium.com/crypt-bytes-tech/ico-hack-coindash-ed-dd336a4f1052
"Coindash ICO的⿊客")在他们的⽹⻚上修改了公司的以太坊地址，诱骗参与者将ethers发送到攻击者的地址。

发现时间表： 2017年4⽉6⽇ [如何通过阅读区块链来找到1000万美元](https://blog.golemproject.net/how-to-find-10m-by-just-reading-blockchain-6ae9d39fcd95 "如何通过阅读区块链来找到1000万美元")

真实世界影响：

[未知交换（s）](https://blog.golemproject.net/how-to-find-10m-by-just-reading-blockchain-6ae9d39fcd95 "未知交换（s）")

示例：

  1. 交易所API具有交易功能，可以接收收件⼈地址和⾦额。
  2. 然后，API `transfer(address _to, uint256 _amount)`使⽤填充参数与智能合约函数进⾏交互：它将12位零字节的地址（预期的20字节⻓度）预先设置为32字节⻓
  3. 鲍勃（）要求爱丽丝转让他20个代币。他恶意地将她的地址截断以消除尾随的零。`0x3bdde1e9fbaef2579dd63e2abbf0be445ab93f00`
  4. Alice使⽤交换API和Bob（`0x3bdde1e9fbaef2579dd63e2abbf0be445ab93f`）的较短的19字节地址。
  5. API⽤12个零字节填充地址，使其成为31个字节⽽不是32个字节。有效地窃取以下`_amount`参数中的⼀个字节。
  6. 最终，执⾏智能合约代码的EVM将会注意到数据未被正确填充，并会在`_amount`参数末尾添加丢失的字节。有效地传输256倍以上的令牌。

其他资源：

  * [ERC20短地址攻击说明](http://vessenes.com/the-erc20-short-address-attack-explained/ "ERC20短地址攻击说明")
  * [分析ERC20短地址攻击](https://ericrafaloff.com/analyzing-the-erc20-short-address-attack/ "分析ERC20短地址攻击")
  * [智能合同短地址攻击缓解失败](https://blog.coinfabrik.com/smart-contract-short-address-attack-mitigation-failure/ "智能合同短地址攻击缓解失败")
  * [从标记中删除短地址攻击检查](https://github.com/OpenZeppelin/zeppelin-solidity/issues/261 "从标记中删除短地址攻击检查")

#### 10.未知的 未知物

> 我们相信更多的安全审计或更多的测试将没有什么区别。主要问题是评审⼈员不知道要寻找什么。 Christoph Jentzsch

以太坊仍处于起步阶段。⽤于开发智能合同的主要语⾔Solidity尚未达到稳定版本，⽽⽣态系统的⼯具仍处于试验阶段。⼀些最具破坏性的智能合约漏洞使每个⼈都感到惊讶，并且没有理由相信不会有另⼀个同样出乎意料或同样具有破坏性的漏洞。只要投资者决定将⼤量资⾦⽤于复杂⽽轻微审计的代码，我们将继续看到新的发现导致可怕的后果。对智能合约进⾏正式验证的⽅法尚不成熟，但它们似乎有望成为今⽇摇摇欲坠的现状。随着新类型的漏洞不断被发现，开发⼈员需要继续努⼒，并且需要开发新⼯具来在坏⼈之前找到它们。这个前10名可能会迅速发展，直到智能合约开发达到稳定和成熟的状态。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/603/>


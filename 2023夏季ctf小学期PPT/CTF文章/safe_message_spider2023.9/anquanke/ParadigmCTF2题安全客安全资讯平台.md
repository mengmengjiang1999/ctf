# Paradigm-CTF 2题

阅读量 **91847**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-01 15:30:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

给出了以下合约

  1. Setup.sol
  2. Wallet.sol

* * *

Setup.sol

    
    
    pragma solidity 0.5.12;
    
    import "./Wallet.sol";
    
    contract WETH9 is ERC20Like {
        function deposit() public payable;
    }
    
    contract Setup {
        WETH9 public constant WETH = WETH9(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
        uint public constant WANT = 50 ether;
    
        Wallet public wallet;
    
        constructor() public payable {
            require(msg.value == WANT);
    
            address tokenModule = address(new TokenModule());
    
            wallet = new Wallet();
            wallet.allowModule(tokenModule);
    
            WETH.deposit.value(msg.value)();
            WETH.approve(address(wallet), uint(-1));
    
            wallet.execModule(tokenModule, abi.encodeWithSelector(TokenModule(0x00).deposit.selector, WETH, address(this), msg.value));
        }
    
        function isSolved() public view returns (bool) {
            return WETH.balanceOf(address(this)) == WANT;
        }
    }
    
    
    
    pragma solidity 0.5.12;
    
    contract ERC20Like {
        function transfer(address dst, uint qty) public returns (bool);
        function transferFrom(address src, address dst, uint qty) public returns (bool);
        function approve(address dst, uint qty) public returns (bool);
    
        function balanceOf(address who) public view returns (uint);
    }
    
    contract TokenModule {
        function deposit(ERC20Like token, address from, uint amount) public {
            token.transferFrom(from, address(this), amount);
        }
    
        function withdraw(ERC20Like token, address to, uint amount) public {
            token.transfer(to, amount);
        }
    }
    
    contract Wallet {
        address public owner = msg.sender;
    
        mapping(address => bool) _allowed;
        mapping(address => bool) _operators;
    
        modifier onlyOwner {
            require(msg.sender == owner);
            _;
        }
    
        modifier onlyOwnerOrOperators {
            require(msg.sender == owner || _operators[msg.sender]);
            _;
        }
    
        function allowModule(address module) public onlyOwner {
            _allowed[module] = true;
        }
    
        function disallowModule(address module) public onlyOwner {
            _allowed[module] = false;
        }
    
        function addOperator(address operator) public onlyOwner {
            _operators[owner] = true;
        }
    
        function removeOperator(address operator) public onlyOwner {
            _operators[owner] = false;
        }
    
        function execModule(address module, bytes memory data) public onlyOwnerOrOperators {
            require(_allowed[module], "execModule/not-allowed");
            (bool ok, bytes memory res) = module.delegatecall(data);
            require(ok, string(res));
        }
    }
    

可以看到成功的条件是拿到WETH代币的50ETH。  
我们从头开始审计一下SetUp合约。可以看到首先要求了我们msg.value需要为50ETH。之后他先是新创建了TokenModule合约，以及wallet合约。之后他把50个ETH全部捐献到WETH这个币池中。approve用于定义交易上限。-1
也就是相当于随便使用了。然后调用了wallet的
execModule方法。发现execModule中利用的是delegatecall操作的是Wallet本身的方法。这里可以注意一下。

之后可以看一下Wallet.sol中的合约。ERC20Like类似ERC20代币规则的接口  
估计是WETH实现时候用到的。TokenModule 这里用了一个接口实现Token转账。  
Wallet合约中有两个修饰器。一个只允许发起交易人是合约创建者，还有一个是除了创建者之外的一个operater为真的但是add_operator只能通过onlyOwner来操作。
最后还有我们的execModule是需要满足onlyOwner或者operator条件。  
那么我们就可以开始考虑如何先把两个修饰器通过。

我们这时候可以注意到，他其实给出了这个WETH合约的地址，我们去考虑查看下这个合约我们是否能进行一定方法的调用。

我们可以发现 其实只要我们一方能够给出50ETH这样的一个转账，同时也是可以实现触发Solved成功的。所以考虑只需要进行转账50ETH就足够了。

    
    
    pragma solidity 0.5.12;
    
    import "public/Setup.sol";
    
    contract Exploit {
        WETH9 public constant WETH = WETH9(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    
        constructor(Setup setup) public payable {
            WETH.deposit.value(50 ether)();
            WETH.transfer(address(setup), 50 ether);
        }
    }
    

比较简单。

* * *

## Lockbox

强网杯有一题和这题基本一模一样。但是强网杯未给出源码需要自己逆向。分析一下这题。

    
    
    pragma solidity 0.4.24;
    
    contract Stage {
        Stage public next;
    
        constructor(Stage next_) public {
            next = next_;
        }
    
        function getSelector() public view returns (bytes4);
    
        modifier _() {
            _;
    
            assembly {
                let next := sload(next_slot)
                if iszero(next) {
                    return(0, 0)
                }
    
                mstore(0x00, 0x034899bc00000000000000000000000000000000000000000000000000000000)
                pop(call(gas(), next, 0, 0, 0x04, 0x00, 0x04))
                calldatacopy(0x04, 0x04, sub(calldatasize(), 0x04))
                switch call(gas(), next, 0, 0, calldatasize(), 0, 0)
                    case 0 {
                        returndatacopy(0x00, 0x00, returndatasize())
                        revert(0x00, returndatasize())
                    }
                    case 1 {
                        returndatacopy(0x00, 0x00, returndatasize())
                        return(0x00, returndatasize())
                    }
            }
        }
    }
    
    contract Entrypoint is Stage {
        constructor() public Stage(new Stage1()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
        bool public solved;
    
        function solve(bytes4 guess) public _ {
            require(guess == bytes4(blockhash(block.number - 1)), "do you feel lucky?");
    
            solved = true;
        }
    }
    
    contract Stage1 is Stage {
        constructor() public Stage(new Stage2()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
        function solve(uint8 v, bytes32 r, bytes32 s) public _ {
            require(ecrecover(keccak256("stage1"), v, r, s) == 0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf, "who are you?");
        }
    }
    
    contract Stage2 is Stage {
        constructor() public Stage(new Stage3()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
        function solve(uint16 a, uint16 b) public _ {
            require(a > 0 && b > 0 && a + b < a, "something doesn't add up");
        }
    }
    
    contract Stage3 is Stage {
        constructor() public Stage(new Stage4()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
        function solve(uint idx, uint[4] memory keys, uint[4] memory lock) public _ {
            require(keys[idx % 4] == lock[idx % 4], "key did not fit lock");
    
            for (uint i = 0; i < keys.length - 1; i++) {
                require(keys[i] < keys[i + 1], "out of order");
            }
    
            for (uint j = 0; j < keys.length; j++) {
                require((keys[j] - lock[j]) % 2 == 0, "this is a bit odd");
            }
        }
    }
    
    contract Stage4 is Stage {
        constructor() public Stage(new Stage5()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
        function solve(bytes32[6] choices, uint choice) public _ {
            require(choices[choice % 6] == keccak256(abi.encodePacked("choose")), "wrong choice!");
        }
    }
    
    contract Stage5 is Stage {
        constructor() public Stage(Stage(0x00)) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
        function solve() public _ {
            require(msg.data.length < 256, "a little too long");
        }
    }
    `
    

套娃合约。最重要的是看懂每个的逻辑 以及数据部署。怎么给套娃中的下一个合约传参。  
这里给出了一个Setup.sol

    
    
    pragma solidity 0.4.24;
    
    import "./Lockbox.sol";
    
    contract Setup {
        Entrypoint public entrypoint;
    
        constructor() public {
            entrypoint = new Entrypoint();
        }
    
        function isSolved() public view returns (bool) {
            return entrypoint.solved();
        }
    }
    

相当于告诉我们的入口点是要从Entrypoint()开始。我们首先抛开其他传参布局因素，挨个解决套娃合约。

Entrypoint

    
    
    contract Entrypoint is Stage {
     constructor() public Stage(new Stage1()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
     bool public solved;
    
     function solve(bytes4 guess) public _ {
         require(guess == bytes4(blockhash(block.number - 1)), "do you feel lucky?");
    
         solved = true;
     }
    }
    

这里我们可以看到进行了一个随机数预测。没有什么难点。进入下一个。

### Stage1

    
    
    contract Stage1 is Stage {
     constructor() public Stage(new Stage2()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
     function solve(uint8 v, bytes32 r, bytes32 s) public _ {
         require(ecrecover(keccak256("stage1"), v, r, s) == 0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf, "who are you?");
     }
    }
    

这里进行了一个ecrecover
这是一个利用椭圆曲线进行验证的函数。这个privatekey在一个网站上是给出的。我们直接去查询最终的值就可以。<http://www.privatekeys.info/ethereum/1>

![](https://p5.ssl.qhimg.com/t01cfe467e73c9fe646.png)

可以看到。这里的私钥是0x000000000000000(…)1  
利用这个进行eth-sign。单纯的web3的sign-in是有问题的他会自动加入一个消息头。导致消息的 r s v不太相同。需要利用其它的库。  
给出Sissel👴用的<https://gist.github.com/onyb/cf795c819fdf8aa6015de2772fde24de>  
这里我们可以知道 他要求的就是我们的  
然后我们还知道我们的slot0的高位还需要满足等于bytes32 的前面随机数预测。  
也就是

    
    
    (uint(bytes4(blockhash(block.number - 1))) << 224) | 0xff1c
    

剩下的2个storage正常部署即可。接下来我们可以关注到下一个的Stage2

### stage2

    
    
    contract Stage2 is Stage {
     constructor() public Stage(new Stage3()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
     function solve(uint16 a, uint16 b) public _ {
         require(a > 0 && b > 0 && a + b < a, "something doesn't add up");
     }
    }
    

这里我们可以看到他取了 2个 storage的uint
。因为这里他是从上个合约中直接call的。所以我们可以考虑到这里他使用的就是我们前面已经部署过的数据了。也就是v和r的低位。数据满足溢出条件。可以直接通过。

###  stage3

    
    
    contract Stage3 is Stage {
        constructor() public Stage(new Stage4()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
        function solve(uint idx, uint[4] memory keys, uint[4] memory lock) public _ {
            require(keys[idx % 4] == lock[idx % 4], "key did not fit lock");
    
            for (uint i = 0; i < keys.length - 1; i++) {
                require(keys[i] < keys[i + 1], "out of order");
            }
    
            for (uint j = 0; j < keys.length; j++) {
                require((keys[j] - lock[j]) % 2 == 0, "this is a bit odd");
            }
        }
    }
    

这时的slot部署是这样的。

    
    
    slot0    idx     guess v  a  choices[0]
    slot1    keys[0]       r  b  .....1
    slot2    keys[1]       s     .....2
    slot3    keys[2]             .....3
    slot4    keys[3]             .....4
    slot5    lock[0]             .....5
                                 choice
    

这里我们可以看到他传入一个uint的idx , 但是他做的是%4的运算，所以我们可以理解为他只对后4位是有意义的也就是uint16.  
然后要求了keys[i]<keys[i+1] 并且 keys[0]=idx[0] 最后还有一个部署上的要求。这里是对后面还要接入的数据进行操作的。

###  stage4

    
    
    contract Stage4 is Stage {
        constructor() public Stage(new Stage5()) {} function getSelector() public view returns (bytes4) { return this.solve.selector; }
    
        function solve(bytes32[6] choices, uint choice) public _ {
            require(choices[choice % 6] == keccak256(abi.encodePacked("choose")), "wrong choice!");
        }
    }
    

这里就比较简单了 。再任意的6块slot中部署一个abi.encodePacked(“choose”) .  
这里给出一个值得注意的点。单纯的abi.encode(“choose”)相当于直接进行long_to_bytes到高位。和enocdePacked(“choose”)完全不同。

但是为了满足上面的要求这里只能部署到slot4上。

最后带着selector一起abi.encode之后直接调用data进行调用即可成功绕过。  
所需部署的数据如下

    
    
    entrypoint.solve.selector 调用方法的4字节
    uint(uint16(0xff1c)|(uint(byte4(blockhash(block.number-1))) << 224) 高位为entry的预测随机数。低位是我们的v
    0x274d91564d07600e8076a8843bd13a374cf43dcd2f5277fb61313f3d5c805b61   签名用的s
    0xa129687de0b602825f931363235f7a427088014fb94cde3264efbce58cc04236   签名用的v
    0xa129687de0b602825f931363235f7a427088014fb94cde3264efbce58cc04238   满足差值为偶数
    (keccak256('choose')） 通过stage4的条件
    0x274d91564d07600e8076a8843bd13a374cf43dcd2f5277fb61313f3d5c805b61  lock[0]=key[0]
    0x0000000000000000000000000000000000000000000000000000000000000004 做的choice 也就是指向abi.encodePakced("choose")的指针。
    

最后把这些一起abi.encodePacked来打包整个交易数据。  
就可以成功通过所有的套娃合约。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Retr_0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/251025](/post/id/251025)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [区块链](/tag/区块链)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t010457258f753577cd.png) Retr_0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


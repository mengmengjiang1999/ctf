作者：[启明星辰ADLab](https://mp.weixin.qq.com/s/UXK8-ZN7mSUI3mPq2SC6Og "启明星辰ADLab")

### 1 概述

随着区块链、以太坊技术的兴起和不断成熟，安全问题也随之而来，今年智能合约漏洞已经让多个区块链项目价值瞬间归零。智能合约的开发语言、设计模式、运行机制都与传统应用有较大差异，它既有传统的安全风险(如整数溢出等)，又有独特的新型风险(如私有变量不“私有”和特殊类型变量覆盖等)。研发人员如果不能深刻理解这些核心原理，则很容易编写出存在漏洞的智能合约；恶意合约也可以通过这种方法留下隐蔽漏洞，欺骗合约投资人并暗地里收割。本文以WCTF2018的一道智能合约漏洞赛题[1]为例，从solidity语言特性出发，深度解读以太坊智能合约漏洞原理和攻击利用。

### 2 漏洞合约分析

该合约是一个银行类合约，用户可以存入eth到该合约，并在存入到期之后取出。原题对该合约描述如下：

![](https://images.seebug.org/content/images/2018/08/c9ac1e99-2d13-4b76-a3ce-63a08b153c10.jpg-w331s)

该合约中存在漏洞，攻击者利用漏洞可以盗取合约中的所有余额。漏洞涉及到整数溢出、变量覆盖以及由变量覆盖导致的变量相互影响。

合约源码如下：

![](https://images.seebug.org/content/images/2018/08/669e5704-cee6-4362-ab91-ac3db48d0885.jpg-w331s)

要提取合约的全部合约余额，confiscate 函数是关键，但该函数调用成功必须满足：

  * msg.sender == owner

  * secret == _secret

  * now >= balances[account].deposit_term + 1 years

攻击者可以通过合约存储访问、整数溢出和变量覆盖来依次构造上述条件。

#### 2.1 solidity全局变量存储

在BelluminarBank合约中，一共有4个全局变量，分别是balances、head、owner、secrete。它们的默认访问属性是private，看上去只有合约自己能够访问这些变量。事实上，合约的所有变量数据都是公开存储在链上的区块中，任何人都可以通过访问存储数据来获得这些变量的值[2]。在solidity语言中，全局变量都存储在storage中，根据solidity的变量存储规则，定长的变量在storage中是顺序存储的，数组变量在storage中其索引位置存放的是其数组长度（参见[3]）。该合约storage中的变量存储布局如下：

![](https://images.seebug.org/content/images/2018/08/b3f11b9c-fd8c-4f3b-a839-1b2a3f225ec3.jpg-w331s)

对于在公链部署的合约，可通过以太坊web3接口`web3.eth.getStorageAt(co ntractAddress,
index)`获取某个合约指定storage索引的数据。

因此，secrete并不是一个不可获取的私有数据，攻击者只需要访问该合约storage中的数据就可以构造confiscate 函数的`secret ==
_secret`条件。

#### 2.2 solidity全局变量覆盖

BelluminarBank合约中的confiscate函数要求调用者必须是合约拥有者才可以进行余额提取操作，看上去攻击者是无法提取的。然而，由于solidity语言的局部变量存储特性，导致本合约的owner变量可以被修改，覆盖问题出现在
invest 函数中。

首先来看solidity局部变量覆盖全局storage的问题。solidity语言的变量存储有一个特性，即数组、映射、结构体类型的局部变量默认是引用合约的storage
[4]，而全局变量默认存储在storage中。因此，如果这些局部变量未被初始化，则它们将直接指向storage，修改这些变量就是在修改全局变量。

以如下的简单合约test为例，函数test1中定义了一个局部结构体变量x，但是没有对其进行初始化。根据solidity的变量存储规则，这时候x是存储在storage中的，而且是从索引0开始，那么对其成员变量x,y赋值之后，刚好覆盖了全局变量a和b。有兴趣可以在
remix 中在线对本合约进行调试。

    
    
    pragma solidity 0.4.24;
    
    contract test {
    
        struct aa{
    
            uint x;
    
            uint y;
    
        }
    
        uint public a = 4;
    
        uint public b = 6;
    
        function test1() returns (uint){
    
            aa x;
    
            x.x = 9;
    
            x.y = 7;
    
        }
    
    }

在invest函数的else分支中，使用了一个局部结构变量investment。该局部变量在当前执行分支中并没有被初始化，默认指向合约的storage。执行中对该变量的成员赋值就会直接覆盖全局变量，覆盖关系为：

![](https://images.seebug.org/content/images/2018/08/ed7599e6-2b57-488b-a736-c1ce21af03ce.jpg-w331s)

同时，在变量覆盖之前必须满足如下条件，即存款期限是最末一个存款记录的期限后一年：`deposit_term >=
balances[balances.length - 1].deposit_term + 1
years`。由于deposit_term是用户提供的，轻松就可以满足。

所以，通过精心构造invest函数的参数就可以覆盖stroage中的sender，从而改变该合约的拥有者为攻击者，突破confiscate
函数的msg.sender == owner限制。

#### 2.3 整数溢出

在BelluminarBank合约源码的confiscate函数还有另外一个如下的时间限制，即必须在存款满一年后才能提取，`now >=
balances[account].deposit_term + 1 years`。

上一节用于全局变量覆盖的存款操作使得balances中最末一个存储记录的期限已经是1年后，即攻击者至少在2年后才能调用confiscate函数进行提款。与此同时，deposit_term在赋值给局部变量的时候会把全局变量head覆盖为超大的数，这也使得后续的`for
(uint256 i = head; i <= account; i++)`循环处理无法提取全部的存款，因为head不为0。

显然，必须把head覆盖为0才能提取全部的存款，即invest函数的deposit_term参数必须为0。但如果该参数为0，又无法满足invest函数的全局变量覆盖执行的条件`deposit_term
>= balances[balances.length - 1].deposit_term + 1 years`。

仔细分析可发现，如果`balances[balances.length - 1].deposit_term+ 1
years`恰好等于0，则上述的条件恒为真。显然，`balances[balances.length -1].deposit_term`只要取值为`(uint256_max – 1 years +
1)`，就会导致相加后的值为`uint256_max+1`。这个结果会超过uint256的表达空间，产生溢出导致最后的值为0。

因此，攻击者先做第一次存款，把balances最后一项的`deposit_term`设置为特殊值；然后做第二次存款，`deposit_term`传入0值，就能触发整数溢出，绕过变量覆盖条件限制并修改head为0值。

#### 2.4 “变量纠缠”的副作用

在全局变量覆盖中，很容易产生“变量纠缠”现象，从而触发一些容易被忽视的副作用。这里以一个简单合约test为例，函数testArray中依然存在结构体局部变量a覆盖全局变量x的情况。但由于x是数组变量，其直接索引的storage存储位置仅存储其数组长度，也就是a.x只会覆盖x的数据长度，而a.y将覆盖变量num。

在testArray函数中，赋值操作a.x =
5时，因为x.length与变量a.x处于同一存储位置，赋值后数组x的长度变成了5。接下来，赋值a.y，并将变量a加入到数组x。所以变量a实际上加入到了数组x索引为5的位置。如果调试testArray函数执行，会发现在函数执行完毕之后，x[5].x
= 6, x[5].y = 7。

这是为什么呢？明明代码中赋值写的是 a.x = 5，a.y =
7。这就是全局变量x和局部变量a形成了“纠缠”，首先是局部变量a修改导致全局变量x改变，然后是全局变量x修改导致了局部变量修改，最后把修改后的局部变量又存储到修改后的全局变量。这里即是，赋值操作a.x
= 5时，把数组x的长度变成了5; 接下来x.push操作，实际上是先将该数组x的长度加1，此时a.x = 6; 最后再把a.x = 6,
a.y=7加入到x[5]。所以，存入数据的x就是新数组的长度6。

    
    
    pragma solidity 0.4.24;
    
    contract test {
    
        struct aa{
    
            uint x;
    
            uint y;
    
        }
    
        aa [] x;
    
        uint public num = 4;
    
    
    
        function testArray() returns (uint){
    
            aa a;
    
            a.x = 5;
    
            a.y = 7;
    
            x.push(a);
    
        }
    
    }

### 3 漏洞利用方式

在第2节中对合约
BelluminarBank存在的几个漏洞进行了分析，下面将说明如何利用这个漏洞提取合约的全部余额，这里在Remix在线编译环境中部署该合约，并演示其利用方式。

首先部署合约，在部署参数中设置secrete 为“0x01”，deposit_term为1000，msg.value为 31337 wei。

部署合约后，合约的全局变量如下图所示：

![](https://images.seebug.org/content/images/2018/08/acd39bc3-0620-4729-ab49-748dec759b1f.jpg-w331s)

这样，合约目前的余额是 31337 wei，合约拥有者的地址为：0xca35b7d915458ef54 0ade6068dfe2f44e8fa733c。

下面开始需要构造条件使得攻击者可以成功调用confiscate函数。

**步骤1: 覆盖owner并构造整数溢出条件**

要想转走合约余额，首先必须修改合约的owner。利用局部结构体 investment 修改合约owner，需满足条件：

  1. account < head or account >= balances.length

  2. deposit_term >= balances[balances.length – 1].deposit_term + 1 years

设置攻击者（0x1472…160C）的invest调用参数如下：

  * msg.value = 1 wei (因为在合约初始化时owner已经存入一笔金额，所以此时balances数组长度为1，为了不改变balances数组长度，这里依然将其设置为1 we i

  * depositsit_term = 2^256 - 1 years = 115792089237316195423570985008687907853269984665640564039457584007913098103936 （在步骤2中需要利用这个数值构造溢出，同时这个值可以使源码中 require 条件得到满足）

  * account = 1 (满足条件 account >= balances.length)

调用之后，新的存款记录数据将存放在balances数组索引为1的位置。此时的balances数组情况和全局storage变量情况如下图所示。

![](https://images.seebug.org/content/images/2018/08/8b30abe3-d703-4861-a48a-010058c9565a.jpg-w331s)

可以发现，owner已经修改为攻击者地址，同时head被传入的deposit_term覆盖为一个超大值。

而提取余额是从balances数组中head索引开始的存款记录开始计算数额的。显然，为了提取到合约owner的余额，即balances[0]账户的余额，head必须被覆盖为0。因此，需要进行第二次storage变量覆盖，修改head。

**步骤2: 恢复head并绕过deposit_term限制**

继续设置攻击者调用invest的参数：

  * msg.value = 2wei (同样保证balances的长度覆盖后不出现错误)

  * deposit_term = 0: 恢复head

  * account = 2 (满足条件 account >= balances.length 即可)

因为在步骤 1 中，已经将`balances[1].deposit_term` 设置为 2^256 -1 years，因此在第二次调用 invest
函数时，由于`balances[balances.length - 1].deposit_term + 1
years”`溢出为0满足了require条件，所以可以成功进行第二次覆盖。

这样即满足了调用confiscate函数的条件`msg.sender == owner`，通过读取storage很容易获得secrete，条件`secret
== _secret` 也可以满足，同时还重新覆盖了head使之变为0 。

覆盖之后全局storage变量和balances数组如下图所示：

![](https://images.seebug.org/content/images/2018/08/ed4922d8-89d2-4b84-a754-d30252e923c4.jpg-w331s)

可以发现head已经修改为0了。

现在来看看第三个条件：

`now >= balances[account].deposit_term + 1 years`

account是传入的数据，目前合约中account数量为3。在前面的invest调用后， `balances[2].deposit_term = 0`。
显然条件 `now >= balances[2].deposit_term + 1 years`
成立，所以在恢复head数据的同时，也绕过了confiscate函数中对于存款期限的判定。接下来只要调用函数confiscate时，设置account 为
2，便可使时间判断条件满足，同时也能提取所有账户的余额。

**步骤3: 增加合约余额**

经过步骤1和步骤2，仿佛攻击者已经可以调用confiscate函数提取所有余额了，然而实际上是不行的。交易会发生回滚，这是为什么呢？

仔细分析前面的数据就会发现，步骤1中msg.value为 1 wei，但是最后balances数组中的balances[1].amount 却变成了 2
wei。这是因为变量覆盖过程中产生了“纠缠”副作用，由于msg.value覆盖balances数组的长度，balances更新前增加了数组长度，数组长度又改变了msg.value，最后导致存入的amount变成了新的数组长度，即2。

所以，每次调用invest函数进行变量覆盖，存款记录的账目金额都比调用者实际支付的msg.value大。下图是两次调用invest之后的balances数组情况。

![](https://images.seebug.org/content/images/2018/08/c2def00a-1998-4e32-a6ad-823a0f60c92f.jpg-w331s)

从图中可以看出，存款记录中的账面值会比实际交易的msg.value多 1 wei。通过confiscate函数计算得到的所有账户总额为31342
wei，而实际的合约账户总余额为 31340 wei。

![](https://images.seebug.org/content/images/2018/08/8fac3425-ebae-449b-bdd5-d4f3b0d009fd.jpg-w331s)

为了能够将合约中所有余额提取出来，需要增加合约的真实余额，使其同存款记录中的余额相等。然而，通过invest方式增加的余额都会被计入账面余额，那么怎么在不通过invest函数的情况下增加合约的真实余额呢？

答案是selfdestruct函数。

selfdestruct函数会将该合约的余额转到指定账户，然后从区块链中销毁该合约的代码和storage。该函数的官方文档说明[5]如下：

![](https://images.seebug.org/content/images/2018/08/ab42fb20-791d-494a-92b9-08c51b0535b0.jpg-w331s)

因此，可以构造一个合约，然后在合约中调用selfdestruct函数将合约的余额转给BelluminarBank合约。为此，构造如下合约：

    
    
    contract donar{
    
        function donar() public payable{
    
            selfdestruct(contractAddr);
    
        }
    
    }

该合约创建后马上销毁，同时将自己的余额转给银行合约。

在 remix 中 编译该合约，同时将 contractAddr替换为银行合约地址。然后 在deploy该合约时，设置 msg.value 为2
wei。当合约创建又销毁之后，其余额（2wei）将转给银行账户，使银行合约的账面余额和实际余额一致，这样confiscate函数调用就能够正确执行。

Donar合约部署设置如下：

![](https://images.seebug.org/content/images/2018/08/1a3580d1-0936-4845-8cf5-4e471a26aca4.jpg-w331s)

合约部署完之后，BelluminarBank 合约余额如下图：

![](https://images.seebug.org/content/images/2018/08/e79e7ded-b8c9-4d23-9666-6cc0da3e408b.jpg-w331s)

**步骤4：调用confiscate提取合约余额**

经过上面的操作之后，设置confiscate函数的参数为[2，“0x01”]即可将合约的全部余额转走。

### 参考链接

  1. <https://github.com/beched/ctf/tree/master/2018/wctf-belluminar>

  2. <https://solidity.readthedocs.io/en/v0.4.24/security-considerations.html#private-information-and-randomness>

  3. <https://medium.com/aigang-network/how-to-read-ethereum-contract-storage-44252c8af925>

  4. <http://solidity.readthedocs.io/en/v0.4.24/frequently-asked-questions.html>

  5. <https://solidity.readthedocs.io/en/v0.4.24/introduction-to-smart-contracts.html?highlight=selfdestruct>

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近400个，持续保持国际网络安全领域一流水准。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/661/>


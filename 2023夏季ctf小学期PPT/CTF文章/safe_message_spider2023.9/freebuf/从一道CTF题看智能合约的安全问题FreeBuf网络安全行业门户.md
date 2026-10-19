***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **belluminarbank 是俄罗斯战队在 WCTF 上出的一道 EVM 题目，其中用到了很多 ETH 中经典的漏洞。虽然难度都不是很大，但是如果对
EVM 相关特性不了解的话还是有一定难度的，本文以这个题目为例详细介绍一下 ETH 智能合约中的安全性问题 。**

题目是一个存储交易类合约，用户可以通过给合约发送 ether 实现将 ether 存储在合约中的目的。攻击者的目标就是将存储在这个合约里的所有 ether
全部取走。

合约的代码如下 ：  

    
    
    pragma solidity ^0.4.23;  
    contract BelluminarBank {
        struct Investment {
            uint256 amount;
            uint256 deposit_term;
            address owner;
        }
        Investment[] balances;
        uint256 head;
        address private owner;
        bytes16 private secret;
        function BelluminarBank(bytes16 _secret, uint256 deposit_term) public {
            secret = _secret;
            owner = msg.sender;
            if(msg.value > 0) {
                balances.push(Investment(msg.value, deposit_term, msg.sender));
            }
        }
        function bankBalance() public view returns (uint256) {
            return address(this).balance;
        }
        function invest(uint256 account, uint256 deposit_term) public payable {
            if (account >= head && account < balances.length) {
                Investment storage investment = balances[account];
                investment.amount += msg.value;
            } else {
                if(balances.length > 0) {
                    require(deposit_term >= balances[balances.length - 1].deposit_term + 1 years);
                }
                investment.amount = msg.value;
                investment.deposit_term = deposit_term;
                investment.owner = msg.sender;
                balances.push(investment);
            }
        }
        function withdraw(uint256 account) public {
            require(now >= balances[account].deposit_term);
            require(msg.sender == balances[account].owner);
        msg.sender.transfer(balances[account].amount);
    }
    function confiscate(uint256 account, bytes16 _secret) public {
        require(msg.sender == owner);
        require(secret == _secret);
        require(now >= balances[account].deposit_term + 1 years);
    
        uint256 total = 0;
        for (uint256 i = head; i <= account; i++) {
            total += balances[i].amount;
            delete balances[i];
        }
        head = account + 1;
        msg.sender.transfer(total);
        }
    }

可以看到合约的代码逻辑非常简单，`invest` 函数负责将传入的 ether 保存进 bank；`withdraw`函数负责取出保存的
ether；`confiscate` 函数可以将某些用户的账户全部转走。简单分析可以看出攻击者最终可以通过函数`confiscate`将所有的 ether
都转走。

## 经典的 Integer OverFLow

想要调用函数`confiscate`需要满足几个 require 条件，首先的一个就是要求`require(now >=
balances[account].deposit_term + 1 years);` 调用时间必须在设定的 `deposit_term`
一年之后。这个条件没有对溢出进行判断，可以通过传入一个超长的 deposit_term 绕过判断。  
这里展示了一个智能合约中典型的整数溢出问题。  
EVM 使用的存储单位 uint256，即其中的栈、storage、memory 都是以 0x20 个字节为单位存储的，其可以表示的数据范围为 0 到
2^256 ,`0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF`
可以看的其能够表示的范围是很大的，但是即使是这么大的范围依然存在溢出的可能性，当运算操作的结果大于 0x20 byte
所能表示的范围时，就会造成溢出导致判断失败。  
在这个例子中 1 year 是 Solidity 语法中的时间单位，可以通过下面的单位换算转换成 uint ：

1 years == 31536000

1 == 1 seconds

1 minutes == 60 seconds

1 hours == 60 minutes

1 days == 24 hours

1 weeks == 7 days

1 years == 365 days

如果我们将 deposit_term 设置为
超过`0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF -31536000` 那么在计算 `require(now >= balances[account].deposit_term + 1 years);`
时就会产生溢出，导致加法运算的结果很小从而可以通过检测。  
整数溢出问题在智能合约当中非常常见，合约的编写者或由于考虑不周或由于编写失误导致合约计算产生问题，进而影响整个合约。一个著名的例子
`<https://etherscan.io/address/0x55f93985431fc9304077687a35a1ba103dc1e081#code>`。  
为了应对这问题有很多合约使用 SafeMath 来进行运算操作，一旦在运算过程中产生溢出便会回滚。但是依然有很多合约没有使用 SafeMath 或者使用了
SafeMath 但是忽略了某些操作。

## private 误区  

通过了时间检查之后，合约的调用还需要满足 `require(secret == _secret);` 即传入的 secret
值需要与合约中设定的一个值相同。这个值在合约初始化时设定，属性为 private。  
在传统的编程语言中我们习惯于使用`public`和 `private`来区分类中对象的可见性，一般而言声明为 private
的对象是外部不可见的。智能合约中同样沿用了这一规定，在智能合约给外部提供的接口中确实没有 private
对象的访问路径。但是智能合约与其他传统可执行程序不同，合约本身连同其所有数据（storage） 都是保存在区块上的，而区块对所有人可见，这也就意味着即使是
private 对象在区块上也是可见的（实际上对于传统可执行程序而言，private 属性对象在内存中也是可见的）。  
在本例中，`_secret`是一个全局对象，又称为 StateVarible ，其存储位置为 storage，和合约一起位于区块中。在调试合约时查看合约的
storage ，可以清晰的看到合约存储情况，在 slot 3 位置保存着我们初始化合约时填入的 secret 值  

    
    
    0xc2575a0e9e593c00f959f8c92f12db2869c3395a3b0502d05e2516446f71f85b: Object
    key: 0x0000000000000000000000000000000000000000000000000000000000000003
    value: 0x41000000000000000000000000000000
    

如果合约的编写者对 private 的了解存在误区，将合约的某些敏感功能依赖于 private 对象，那么就有可能出现权限问题。

##  **小心 Storage Pointer**  

最后还需要绕过检查 `require(msg.sender == owner);`，owner 是在合约初始化时设定的一个 StateVarible，存储在
storage 空间中，对应的 slot 为 2。

    
    
    0x405787fa12a823e0f2b7631cc41b3ba8828b3321ca811111fa75cd3aa3bb5ace: Object
    key: 0x0000000000000000000000000000000000000000000000000000000000000002
    value: 0xca35b7d915458ef540ade6068dfe2f44e8fa733c
    

想要绕过这个检查需要将合约的 owner 设置为自己的，但是在合约中我们并没有发现相应的接口。

在 Solidity 的编译阶段存在这样一个奇怪的现象，即函数中声明的临时变量“指针”默认的存储位置 slot 都为 0。按照 EVM
的规定，临时变量的存储位置也在 storage 中，这就造成了一个现象，即临时变量的存储位置和全局变量相重叠，通过修改这个临时变量可以覆盖全局变量的值。

在这个合约中就存在这样的问题，`invest`函数中的临时对象 investment 是结构体`Investment`的一个实例，当新增用户时，这个
inverstment 对象还处于未初始化状态，此时使用这个未初始化的 “对象指针” 就会从默认 slot
开始计算偏移并执行操作。那么在执行`investment.owner = msg.sender;`语句时就会导致问题，覆盖 StateVarible
owner。

一般而言所有在函数中进行的临时 struct 变量或者 Array 变量的操作都存在这种威胁的可能，但是从我们审计过的合约来看，大部分使用了 struct
的合约都是以`Investment storage investment =
balances[account];`这种形式调用的。这种方式初始化的临时对象在实际操作时实际上会转化成直接操作原始对象，即本合约中的`investment.amount
+= msg.value;`在实际操作时会变成`balances[account].amount +=
msg.value;`，因此绝大多数合约还是安全的，但是不排除像本例中的合约一样的可能。

## 不可控的 this.balance  

在绕过了上述的检查之后理论上是可以调用
`confiscate`了，但是在实际的调用中我们发现还是有一点问题。在调用`msg.sender.transfer(total);`
的时候会发生回滚。那么原因自然是 total 计算错误。

正如之前所说的，StateVarible 和临时变量所占用的位置是一样的，通过临时变量可以修改 StateVarible ，同样通过
StateVarible 也可能修改临时变量。`investment.amount = msg.value;` 操作会覆盖 StateVarible
balance 数组，数组成员在 EVM 中是以 hash 的形式存储的，在数组对象对应的 slot 中存放数组的长度。即在这个合约中 数组长度 和
`investment.amount`是存储在同一位置的。`investment.amount =
msg.value;`覆盖了数组的长度，而`balances.push(investment);` 又会将
`investment.amount`增加，从而导致实际加入的 amount 比 msg.value 要大。最终导致 total 比
this.balance 大。

解决这一问题可以通过向合约额外转账来实现，但是合约并没有实现 fallback 是不能以常规路径接收转账的。可以通过调用
`selfdestruct`给合约转账，selfdestruct 的功能是销毁当前合约，并将合约中剩余的 ether 转给指定地址。这样我们就完成了增加
目标合约 ether的功能。

这也就意味[FrogSec](http://www.freebuf.com/wp-admin/edit.php?post_type=post&author=275245)着合约的 balance
属性其实不是自己完全可控的，外部合约完全可以在合约本身未知的情况下给合约转账。那么在合约中使用
`this.balance`来进行判断其实是不安全的。经过我们对现有合约的审计情况来看，this.balance
的使用情况还是很多的，在某些赌博合约中会使用 this.balance 作为某些操作的控制条件，这一系列合约就存在一定的威胁。

这道题是一道相当经典的智能合约综合问题，融合了许多在现实合约中可能出现的问题，对我们理解 ETH 以及审计合约有着很大的帮助。

 ***本文作者FrogSec，转载请注明来自FreeBuf.COM**


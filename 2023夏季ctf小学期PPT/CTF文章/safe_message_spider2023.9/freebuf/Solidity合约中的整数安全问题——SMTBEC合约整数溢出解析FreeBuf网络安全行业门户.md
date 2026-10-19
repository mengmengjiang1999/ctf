***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一. 整数安全回顾

### ​ ** 1\. 整数安全简介**

 **在传统的桌面windows攻防对抗领域，伴随着微软和合作伙伴对软件开发流程推行
SDL规范，同时对安全投入的逐步加大，单一的封包超长和文件特定字段内容超长导致的溢出漏洞在一些大型软件里几乎绝迹。剩余漏洞除了浏览器中的UAF(有隔离堆和延迟释放对关键类进行利用缓解
) ，弱类型语言存在的类型混淆，还零星剩下了一些整数类的漏洞。整数类漏洞，最近的如去年的nginx cve-2017-7529。**

区块链方向，比较早的整数溢出类漏洞可追溯到2010年的比特币大整数溢出，CVE-2010-5139 ，黑客通过整数溢出构造了大概
92233720368.54277039 个比特币，最近的SMT/BEC的整数安全场景与之前比特币的场景类似。

传统安全领域中，整数安全与数据模型和整数运算支持的运算符相关，其中数据模型又跟处理器架构体系和操作系统平台相关。如图1。

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246306798887.png!small)

图1  

C中容易引发整数安全问题的运算符简要罗列如下,如图2。

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/1524630715253.png!small)

图2  

Solidity合约中的整数安全场景与之类似。

### 2\. Solidity中的整数安全场景

SMT 和 BEC 都是以太坊代币生态下的一个普通的 ERC-20 代币。转账流通都是通过以太坊的solidity合约进行实现。

区块链1.0的比特币也有脚本语言，但是为了安全阉割掉了循环和递归等图灵完备性语言才有的功能。以太坊 Solidity设计之初就被定位为图灵完备性语言。
Solidity的图灵完备性也为后续的合约漏洞陆续埋下了伏笔，如 The Dao 漏洞事件直接导致以太坊硬分叉成了eth 和旧链etc。

Solidity语言暂不支持类似于C中的 float double 等浮点型数据类型。支持int/uint变长的有符号或无符号整型。变量支持的步长以8
递增，支持从`uint8` 到`uint256`，以及`int8` 到`int256` 。需要注意的是，`uint`和`int`
默认代表的是`uint256` 和`int256`。`uint8` 的数值范围与 C中的uchar相同，即取值范围是0 到
2^8-1，uint256支持的取值范围是 0 到 2^256-1，余下数据类型以此类推。

Solidity语言中对于运算符的支持如下。

> 比较：`<=` ，`<` ，`==` ，`!=` ，`>=` ，`>` ，返回值为`bool` 类型。
>
> 位运算符：`&` ，`|`，（`^` 异或），（`~` 非）。
>
> 数学运算：`+` ，`-`，一元运算`+` ，`*` ，`/`，（`%` 求余），（`**` 平方）。

Solidity合约代码的逻辑都相对简单，运算符的使用中加法 减法和乘法居多。

以太坊提供有一个Solidity语言的在线编译测试工具。[http://remix.ethereum.org/#optimize=false&version=soljson-v0.4.23+commit.124ca40d.js](http://remix.ethereum.org/#optimize=false&version=soljson-v0.4.23+commit.124ca40d.js)
我们以加法和减法运算作为举例,简单说明下整数溢出在Solidity 语言中的常规情况。

编写如下solidity测试代码。

    
    
    pragma solidity ^0.4.0;  
    
    contract C {  
    
    // (2**256 - 1) + 1 = 0  
    
    function overflow() returns (uint256 _overflow) {  
    
        uint256 max = 2**256 - 1;  
    
        return max + 1;  
        }  
    
    ​  
    
    // 0 - 1 = 2**256 - 1  
    
    function underflow() returns (uint256 _underflow) {  
    
        uint256 min = 0;  
    
        return min - 1;  
        }  
    
    }

在线测试工具中编译运行结果如下如图3图4。

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246307362775.png!small)

图3  
![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246307376905.png!small)

图4

可以看到uint256当取最大整数值，上溢之后直接回绕返回值为0 ， uint256当取0下溢之后直接回绕，返回值为 2^256-1 。这是
solidity中整数溢出场景的常规情况。

### ​ **3\. Solidity中的整数溢出缓解和SafeMath库**

为了减少solidity合约开发中产生的安全问题，以太坊的官方开发博客陆续发布了一些与 solidity开发安全相关的博文。在 2017年 8月 6日
单独发过一篇使用SafeMath 库进行整数安全操作的文章<< SafeMath to protectfrom overflows >> 。详见链接：
<https://ethereumdev.io/safemath-protect-overflows/>

    
    
      
    
    /**  
    
     * @title SafeMath  
    
     * @dev Math operations with safety checks that throw on error  
    
     */  
    
    library SafeMath {  
    
      function mul(uint256 a, uint256 b) internal constant returns (uint256) {  
    
        uint256 c = a * b;  
    
        assert(a == 0 || c / a == b);  
    
        return c;  
    
      }  
    
       
    
      function div(uint256 a, uint256 b) internal constant returns (uint256) {  
    
        // assert(b > 0); // Solidity automatically throws when dividing by 0  
    
        uint256 c = a / b;  
    
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold  
    
        return c;  
    
      }  
    
       
    
      function sub(uint256 a, uint256 b) internal constant returns (uint256) {  
    
        assert(b <= a);  
    
        return a - b;  
    
      }  
    
       
    
      function add(uint256 a, uint256 b) internal constant returns (uint256) {  
    
        uint256 c = a + b;  
    
        assert(c >= a);  
    
        return c;  
    
      }  
    
    }

可以看到相关的可能产生溢出的操作都单独封装成函数，加入assert 断言做判断避免溢出。调用 SafeMath库的方法如图 5。

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246307765987.png!small)

图5

##  **二、SMT** **合约中的整数安全问题简析**

与大型软件或者操作系统动辄十万行甚至千万行代码不同，智能合约的代码行数通常不多，功能也不是很复杂。一起来看下SMT 合约的相关代码。

SMT的合约地址是
<https://etherscan.io/address/0x55f93985431fc9304077687a35a1ba103dc1e081#code>

问题存在于transferProxy()函数 代码如下，如图6

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246308164712.png!small)

图6  
  

在进行加法操作的时候没有采用Safemath库进行约束。 _feeSmt参数和 _value参数均可以被外界进行控制， _feeSmt和 value均是
uint256 无符号整数，相加后最高位舍掉，结果为0。如图7

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246308432401.png!small)

图7

直接溢出绕过代码检查导致可以构造巨大数量的smt代币并进行转账。如图8

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246308607952.png!small)

图8

攻击者的恶意转账记录可以从如下链接进行看到：  

<https://etherscan.io/tx/0x1abab4c8db9a30e703114528e31dee129a3a758f7f8abc3b6494aad3d304e43f>

如图9

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246308916435.png!small)

图9

##  **三、BEC** **合约中的整数安全问题简析**

BEC的合约地址是0xC5d105E63711398aF9bbff092d4B6769C82F793D ，合约代码可以访问
etherscan的如下网址进行查看[https://etherscan.io/address/0xc5d105e63711398af9bbff092d4b6769c82f793d#code](https://etherscan.io/address/0xc5d105e63711398af9bbff092d4b6769c82f793d#code)
。代码一共是299行。  

问题函数如图10。

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246309322057.png!small)

图10

可以看到batchTransfer函数中 ,语句 balances[msg.sender] =
balances[msg.sender].sub(amount)和 balances[_receivers[i]] =
balances[_receivers[i]].add(_value) 中，调用 Safemath库中的安全函数来完成加减操作，但是在第三行代码，
uint256 amount = uint256(cnt) * _value 却直接使用乘法运算符。

其中变量cnt为转账的地址数量，可以通过外界的用户输入 _receivers进行控制，
_value为单地址转账数额，也可以直接进行控制。乘法运算溢出，产生了非预期 amount 数值，并且外界可以通过调整_receivers 和_value
的数值进行操控。紧接着下面有一句对 amount进行条件检查的代码 require(_value > 0&& balances[msg.sender] >=
amount); 其中 balances[msg.sender]代表当前用户的余额。amount代表要转的总币数。代码意思为确保
当前用户拥有的代币余额大于等于转账的总币数才进行后续转账操作。因为通过调大单地址转账数额 _value的数值，amount 溢出后可以为一个很小的数字或者0
，很容易绕过balances[msg.sender] >= amount 的检查代码。从而产生巨大_value数额的恶意转账。

攻击者的恶意转账记录，可以从如下链接看到<https://etherscan.io/tx/0xad89ff16fd1ebe3a0a7cf4ed282302c06626c1af33221ebe0d3a470aba4a660f>
。如图11

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246309591361.png!small)

图11

可以从代码totalSupply进行看到，bec 代币总量共计才 7 000 000 000枚。 如图12

![SMT
BEC合约整数溢出解析](https://image.3001.net/images/20180425/15246309896077.png!small)

图12

但是攻击者通过溢出amount绕过后续 require中的判定条件分别向两个地址恶意转账了
57,896,044,618,658,100,000,000,000,000,000,000,000,000,000,000,000,000,000,000.792003956564819968
枚bec 代币。

## **四、合约整数漏洞事件总结**

单纯从技术上来说，smt和bec的本次合约的漏洞成因和利用都不复杂，均是通过构造恶意的整数溢出绕过条件检查。相信以太坊生态下的其他数千种代币的合约也不同程度的存在类似的整数漏洞安全隐患，由于solidity合约是直接跟钱打交道，合约的安全开发和审计值得ico项目方和solidity开发人员投入更多时间和精力，确保合约的安全性。

## 参考链接：

<https://ethereumdev.io/safemath-protect-overflows/>

[https://zhuanlan.zhihu.com/p/35989258?utm_medium=social&utm_member=ZjZlYmQ1MGZkMjZjZmJkNTE4MGFmMmExZjA5NTM0NmE%3D&utm_source=wechat_session&wechatShare=1&from=timeline&isappinstalled=0](https://zhuanlan.zhihu.com/p/35989258?utm_medium=social&utm_member=ZjZlYmQ1MGZkMjZjZmJkNTE4MGFmMmExZjA5NTM0NmE%3D&utm_source=wechat_session&wechatShare=1&from=timeline&isappinstalled=0)

<<Secure Coding in C andC++>>

 ***本文作者： 360 Aegis 实验室（专注区块链安全研究），转载请注明来自 FreeBuf.COM。**


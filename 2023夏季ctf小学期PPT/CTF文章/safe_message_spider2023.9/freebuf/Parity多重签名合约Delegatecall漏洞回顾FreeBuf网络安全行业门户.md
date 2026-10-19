***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![1.jpg](https://image.3001.net/images/20180718/15318860293319.jpg!small)

## 一、事件始末

2017年7月19日，Parity Multisig 电子钱包合约被爆出漏洞，攻击者从三个高安全的多重签名合约中窃取到超过15万以太坊（约3000万美元）。

## 二、漏洞原理

delegatecall的含义：`<address>.delegatecall(...) returns (bool):`issue low-level
DELEGATECALL, returns false on failure, forwards all available gas,
adjustable。
call与delegatecall的功能类似，区别仅在于后者仅使用给定地址的代码，其它信息则使用当前合约(如存储，余额等等)。注意delegatecall是危险函数，他可以完全操作当前合约的状态。

黑客通过 delegatecall 调用 initWallet 函数， initWallet 没有检查以防止攻击者在合同初始化后调用到
initMultiowned ，漏洞使得黑客能通过 library 库函数，让自己成为多个 Parity 钱包的新主人，然后调用转账函数把钱转走。

## 三、具体分析

1、 `initWallet` 函数可以改变合约的 `owner` 。

    
    
    // line 216
    // constructor - just pass on the owner array to the multiowned and  // the limit to daylimit
    function initWallet(address[] _owners, uint _required, uint _daylimit) {
      initDaylimit(_daylimit);
      initMultiowned(_owners, _required);
    }  
    

2、 代码里使用了 delegatecall() 函数，导致所有 public 函数对所有人可见。包括 initWallet 函数。而且
initWallet 函数也没有作任何防护措施。  

    
    
    // line 424
    function() payable {
      // just being sent some cash?
      if (msg.value > 0)
        Deposit(msg.sender, msg.value);
      else if (msg.data.length > 0)
        _walletLibrary.delegatecall(msg.data);
    }

3、 攻击者先获取`owner`权限，将调用函数的指令放在`Data`中。

行为地址：<https://etherscan.io/tx/0x9dbf0326a03a2a3719c27be4fa69aacc9857fd231a8d9dcaede4bb083def75ec>

    
    
    Function: initWallet(address[] _owners, uint256 _required, uint256 _daylimit) ***
    
    MethodID: 0xe46dcfeb
    [0]:  0000000000000000000000000000000000000000000000000000000000000060
    [1]:  0000000000000000000000000000000000000000000000000000000000000000
    [2]:  00000000000000000000000000000000000000000000116779808c03e4140000
    [3]:  0000000000000000000000000000000000000000000000000000000000000001
    [4]:  000000000000000000000000b3764761e297d6f121e79c32a65829cd1ddb4d32  
    

4、 然后执行`execute`获取所有 funds

行为地址：<https://etherscan.io/tx/0xeef10fc5170f669b86c4cd0444882a96087221325f8bf2f55d6188633aa7be7c>

    
    
    Function: execute(address _to, uint256 _value, bytes _data) ***
    
    MethodID: 0xb61d27f6
    [0]:  000000000000000000000000b3764761e297d6f121e79c32a65829cd1ddb4d32
    [1]:  00000000000000000000000000000000000000000000116779808c03e4140000
    [2]:  0000000000000000000000000000000000000000000000000000000000000060
    [3]:  0000000000000000000000000000000000000000000000000000000000000000
    [4]:  0000000000000000000000000000000000000000000000000000000000000000

## 四、防范方法

> 谨慎使用 `delegatecall()` 函数。
>
> 明确函数可见性，默认情况下为`public`类型，为防止外部调用函数被内部调用应使用 `external`。
>
> 加强权限控制。敏感函数应设置 `onlyOwner` 等修饰器。

## 五、资料

WalletLibrary
合约地址：<https://etherscan.io/address/0xa657491c1e7f16adb39b9b60e87bbb8d93988bc3#code>

The Parity Wallet Hack Explained：<https://blog.zeppelin.solutions/on-the-parity-wallet-multisig-hack-405a8c12e8f7>

## 六、团队介绍

BUGX.IO是一家致力于区块链领域的安全公司。核心团队组建于2014年，我们在区块链生态安全、行业解决方案、安全建设、红蓝对抗等方面有深厚积累与过硬专业素养。

 ***本文作者：BUGX.IO-Tri0nes，转载请注明来自FreeBuf.COM**


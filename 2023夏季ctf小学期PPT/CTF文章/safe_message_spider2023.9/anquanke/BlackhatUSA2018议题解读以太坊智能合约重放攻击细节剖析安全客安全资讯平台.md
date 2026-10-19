# Blackhat USA 2018议题解读 | 以太坊智能合约重放攻击细节剖析

阅读量 **237328**

发布时间 : 2018-08-16 15:30:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01aea4e286be5363be.jpg)

在刚刚结束的 DEF CON 26 全球黑客大会上，来自 360 独角兽安全团队(UnicornTeam)的 Zhenzuan Bai, Yuwei
Zheng 等分享了议题《Your May Have Paid More than You Imagine：Replay Attacks on
Ethereum Smart Contracts》，慢雾安全团队学习并测试实践后，整理了这篇文章供大家交流参考。

## 攻击背景

在资产管理体系中，常有委托管理的情况，委托人将资产给受托人管理，委托人支付一定的费用给受托人。这个业务场景在智能合约中也比较普遍。

###  合约设计

    
    
    function transferProxy(address _from, address _to, uint256 _value, uint256 _fee, uint8 _v, bytes32 _r, bytes32 _s)
    

`transferProxy` 方法涉及的角色：

  * 角色1: 需要转 Token，但自己钱包地址里没有 ETH 的人，即合约中的 `_from`
  * 角色2: 帮助角色1来转 Token，并支付 ETH 的 gas 费用，即合约中的 `msg.sender`，也是调用这个合约的人
  * 角色3: Token 接收方，即合约中的 `_to`

`transferProxy` 方法的目的：

`角色1`想要转 Token 给`角色3`，但自己又没有 ETH 来支付手续费，于是`角色1`找到有 ETH 的`角色2`说：我给你一些 Token
当做手续费，你来通过调用 `transferProxy` 来把我的 Token 转给`角色3`，因为你有 ETH。

###  合约实现

    
    
    function transferProxy(address _from, address _to, uint256 _value, uint256 _fee,
        uint8 _v, bytes32 _r, bytes32 _s) public returns (bool){
    
        if(balances[_from] < _fee + _value 
            || _fee > _fee + _value) revert();
    
        uint256 nonce = nonces[_from];
        bytes32 h = keccak256(_from,_to,_value,_fee,nonce);
        if(_from != ecrecover(h,_v,_r,_s)) revert();
    
        if(balances[_to] + _value < balances[_to]
            || balances[msg.sender] + _fee < balances[msg.sender]) revert();
        balances[_to] += _value;
        emit Transfer(_from, _to, _value);
    
        balances[msg.sender] += _fee;
        emit Transfer(_from, msg.sender, _fee);
    
        balances[_from] -= _value + _fee;
        nonces[_from] = nonce + 1;
        return true;
    }
    

合约中关键的点是`keccak256`和`ecrecover`，即椭圆曲线加密数字签名(ECDSA)函数和验签函数，`keccak256`等同于`sha3`。

如下是签名、验签过程：

  1. `角色1(_from)`先用`sha3`函数对 `_from,_to,_value,_fee,nonce`进行处理得到`msg`值，然后使用`web3.eth.sign(address, msg)`得到签名`signature`；
  2. 将`signature`取前 0~66 个字节作为 r， 66~130 之间的字节作为 s，130~132 的字节作为 v，然后把 v 转为整型，`角色1`把这些信息告知`角色2`，`角色2`调用合约的`transferProxy`进行转账；
  3. 合约内`ecrecover`接收签名数据的哈希值以及r/s/v等参数作为输入，返回实施该签名的账户地址

    
    
    let msg = web3.sha3(_from,_to,_value,_fee,nonce)
    let signature = web3.eth.sign(_from, msg)
    
    let r = signature.slice(0, 66)
    let s = '0x' + signature.slice(66, 130)
    let v = '0x' + signature.slice(130, 132)
    v = web3.toDecimal(v)
    
    console.log('r', r)
    console.log('s', s)
    console.log('v', v)
    console.log(msg)
    

**备注**

`角色1`、`角色2`需要事先沟通好`nonce`、`_fee`，其中`nonce`在合约中定义，从0开始自增，可调用合约的`getNonce(address
_addr)`查询。

## 攻击过程

![](https://cdn.wutui.pro/article_back_5b75074ceb79c.png)

由于合约所有的调用数据（函数参数）都在链上公开可查，所以可从 Transaction 中提取所有签名信息。

流程图  
(图片来自<https://github.com/nkbai/defcon26/blob/master/docs/img/p1.png>)

在智能合约重放攻击中，基于椭圆曲线加密数字签名(ECDSA)和验签的逻辑，可利用不同合约中相同的`transferProxy`实现，把A合约
Transaction 中的签名信息提取出来，在B合约中进行重放，由于涉及签名的所有参数都是一样的，所以可以直接调用B合约并广播到链上。

## 漏洞影响

根据议题《Your May Have Paid More than You Imagine：Replay Attacks on Ethereum Smart
Contracts》中披露的数据，截止4月27日统计发现有52个合约受到重放攻击的影响，其中10个高危、37个中危、5个低危。

从重放攻击目标角度分析，有5个合约因为没有nonce的设计，可在自身合约内进行重放攻击；另外45个合约可跨合约进行重放攻击。

## 防御建议

  1. nonce 生成算法不采用从 0 开始自增的设计，避免和场景的做法相同；
  2. 去除 transferProxy 函数，改成其他方式实现代理的需求；
  3. 在keccak256函数中增加 address(this) 作为参数
  4. 慢雾安全团队合约审计项已加入该类型问题的审计。

## 参考资料

演讲者  
PDF：<https://media.defcon.org/DEF%20CON%2026/DEF%20CON%2026%20presentations/Bai%20Zheng%20and%20Chai%20Wang/DEFCON-26-Bai-Zheng-Chai-Wang-You-May-Have-Paid-more-than-You-Imagine.pdf>

演讲者开放文档：<https://github.com/nkbai/defcon26/blob/master/docs/Replay%20Attacks%20on%20Ethereum%20Smart%20Contracts.md>

演讲者开放工具：<https://github.com/nkbai/defcon26/tree/master/erc20finder>

演讲者开放工具：<https://github.com/nkbai/defcon26/tree/master/proxytoken>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **慢雾安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/156661](/post/id/156661)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Blackhat](/tag/Blackhat)
  * [智能合约](/tag/智能合约)
  * [ETH](/tag/ETH)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t014a191cfd9c749c83.png) 慢雾安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


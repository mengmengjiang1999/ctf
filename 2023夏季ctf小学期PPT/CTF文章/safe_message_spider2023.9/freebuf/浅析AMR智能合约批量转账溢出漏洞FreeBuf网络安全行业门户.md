***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**日前，互联网爆出AMR合约存在高危安全风险的交易，该合约存在批量转账溢出漏洞，当合约实现批量转账功能时，容易在计算通证增加量时发生溢出漏洞，BUGX.IO安全团队经过研究分析发现，同类漏洞仍在以太坊里面部分存在。**

以下为漏洞分析过程：

##  **原理**

    
    
       /**
    
         * @dev Function is used to perform a multi-transfer operation. This could play a significant role in the Ammbr Mesh Routing protocol.
    
         *  
    
         * Mechanics:
    
         * Sends tokens from Sender to destinations[0..n] the amount tokens[0..n]. Both arrays
    
         * must have the same size, and must have a greater-than-zero length. Max array size is 127.
    
         * 
    
         * IMPORTANT: ANTIPATTERN
    
         * This function performs a loop over arrays. Unless executed in a controlled environment,
    
         * it has the potential of failing due to gas running out. This is not dangerous, yet care
    
         * must be taken to prevent quality being affected.
    
         * 
    
         * @param destinations An array of destinations we would be sending tokens to
    
         * @param tokens An array of tokens, sent to destinations (index is used for destination->token match)
    
         */
    
        function multiTransfer(address[] destinations, uint[] tokens) public returns (bool success){
    
            // Two variables must match in length, and must contain elements
    
            // Plus, a maximum of 127 transfers are supported
    
            assert(destinations.length > 0);
    
            assert(destinations.length < 128);
    
            assert(destinations.length == tokens.length);
    
            // Check total requested balance
    
            uint8 i = 0;
    
            uint totalTokensToTransfer = 0;
    
            for (i = 0; i < destinations.length; i++){
    
                assert(tokens[i] > 0);
    
                totalTokensToTransfer += tokens[i];
    
            }
    
            // Do we have enough tokens in hand?
    
            assert (balances[msg.sender] > totalTokensToTransfer);
    
            // We have enough tokens, execute the transfer
    
            balances[msg.sender] = balances[msg.sender].sub(totalTokensToTransfer);
    
            for (i = 0; i < destinations.length; i++){
    
                // Add the token to the intended destination
    
                balances[destinations[i]] = balances[destinations[i]].add(tokens[i]);
    
                // Call the event...
    
                emit Transfer(msg.sender, destinations[i], tokens[i]);
    
            }
    
            return true;
    
        }

`totalTokensToTransfer += tokens[i];` 这一句溢出，溢出后，totalTokensToTransfer
变小了，从而绕过了 `assert (balances[msg.sender] > totalTokensToTransfer);`
的判断，这样就能花极少的token ，任意增加目标地址的token。

看到攻击者的攻击行为：

[
_https://etherscan.io/tx/0xd4ee42c454941fccb5d03f6155e288f28cc00473ba927ee4b19ad4e2bfc68b68_](https://etherscan.io/tx/0xd4ee42c454941fccb5d03f6155e288f28cc00473ba927ee4b19ad4e2bfc68b68)

![图片1.png](https://image.3001.net/images/20180711/15312902915269.png!small)

可以看到这两个 tokens 值都是 uint256 最大值的一半，两个加起来刚好溢出变为 0。

##  **漏洞复现**

### 1\. 部署 AMR 合约。

### 2\. 因为需要攻击者 token 数量大于0，所以先使用管理员账户给攻击者地址充 token。

"0x14723a09acff6d2a60dcdf7aa4aff308fddc160c",1

![图片2.png](https://image.3001.net/images/20180711/15312903609886.png!small)

使用 `balanceOf` 可以查看到 0x14723a09acff6d2a60dcdf7aa4aff308fddc160c 有 balances 为 1

![图片3.png](https://image.3001.net/images/20180711/15312903772272.png!small)

### 3\. 使用漏洞溢出攻击

这里需要两个地址，一个是攻击者，另一个为其它地址，这里设置 0 地址就行。

执行 multiTransfer 就行。

["0x14723a09acff6d2a60dcdf7aa4aff308fddc160c","0x0000000000000000000000000000000000000000"],["57896044618658097711785492504343953926634992332820282019728792003956564819968","57896044618658097711785492504343953926634992332820282019728792003956564819968"]

![图片4.png](https://image.3001.net/images/20180711/15312904434154.png!small)

### 4\. 查看攻击者余额

![图片5.png](https://image.3001.net/images/20180711/15312904583412.png!small)

可以看到攻击者余额已经变得非常大。

##  **修复方案**

### 1\. 使用 safeMath 即可解决此问题。

### 2\. 以太坊的大部分合约是以 transfer 的形式进行转账，此方法也可以避免溢出问题。

    
    
    function multiTransfer(address[] recipients, uint256[] amounts) public {
    
        require(recipients.length == amounts.length);
    
        for (uint i = 0; i < recipients.length; i++) {
    
            transfer(recipients[i], amounts[i]);
    
        }
    
    } 

## **进一步探索**

在对以太坊上做进一步探索的时候，我们发现批量转账功能或者批量充值功能的实现主要有以下几种形式：

### 1\. 合约部署时使用批量充值功能

此功能在构造函数中实现，只有部署的时候能够使用，所以不可利用。

    
    
     /// @title Gnosis token contract
    
    /// @author Stefan George - <stefan.george@consensys.net>
    
    contract GnosisToken is StandardToken {
    
      
      
    
    
        /*
    
         *  Token meta data
    
         */
    
        string constant public name = "Gnosis Token";
    
        string constant public symbol = "GNO";
    
        uint8 constant public decimals = 18;
    
      
      
    
    
        /*
    
         *  Public functions
    
         */
    
        /// @dev Contract constructor function sets dutch auction contract address and assigns all tokens to dutch auction.
    
        /// @param dutchAuction Address of dutch auction contract.
    
        /// @param owners Array of addresses receiving preassigned tokens.
    
        /// @param tokens Array of preassigned token amounts.
    
        function GnosisToken(address dutchAuction, address[] owners, uint[] tokens)
    
            public
    
        {
    
            if (dutchAuction == 0)
    
                // Address should not be null.
    
                throw;
    
            totalSupply = 10000000 * 10**18;
    
            balances[dutchAuction] = 9000000 * 10**18;
    
            Transfer(0, dutchAuction, balances[dutchAuction]);
    
            uint assignedTokens = balances[dutchAuction];
    
            for (uint i=0; i<owners.length; i++) {
    
                if (owners[i] == 0)
    
                    // Address should not be null.
    
                    throw;
    
                balances[owners[i]] += tokens[i];
    
                Transfer(0, owners[i], tokens[i]);
    
                assignedTokens += tokens[i];
    
            }
    
            if (assignedTokens != totalSupply)
    
                throw;
    
        }
    
    }

### 2\. 管理者调用批量转账功能

    
    
     function batchTransfer(address[] _to, uint[] _value) checkAccess("currencyOwner") returns (bool) {
    
            if (_to.length != _value.length) {
    
                Error(7, tx.origin, msg.sender);
    
                return false;
    
            }
    
            uint totalToSend = 0;
    
            for (uint8 i = 0; i < _value.length; i++) {
    
                totalToSend += _value[i];
    
            }
    
            ElcoinDb db = _db();
    
            if (db.getBalance(msg.sender) < totalToSend) {
    
                Error(8, tx.origin, msg.sender);
    
                return false;
    
            }
    
            db.withdraw(msg.sender, totalToSend, 0, 0);
    
            for (uint8 j = 0; j < _to.length; j++) {
    
                db.deposit(_to[j], _value[j], 0, 0);
    
                Transfer(msg.sender, _to[j], _value[j]);
    
            }
    
            return true;
    
        }

即使有漏洞，但受到管理者权限控制，所以一般不可利用。

### 3\. 公开函数中的批量转账功能

    
    
     function transferMulti(address[] _to, uint256[] _value) public returns (uint256 amount){
    
            require(_to.length == _value.length);
    
            uint8 len = uint8(_to.length);
    
            for(uint8 j; j<len; j++){
    
                amount += _value[j];
    
            }
    
            require(balanceOf[msg.sender] >= amount);
    
            for(uint8 i; i<len; i++){
    
                address _toI = _to[i];
    
                uint256 _valueI = _value[i];
    
                balanceOf[_toI] += _valueI;
    
                balanceOf[msg.sender] -= _valueI;
    
                Transfer(msg.sender, _toI, _valueI);
    
            }
    
        }

我们看到了不少这种形式的写法，通过 `amount += _value[j];` 的增加，溢出后绕过了
`require(balanceOf[msg.sender] >= amount);` 的检测。

## **漏洞影响范围**

研究此漏洞原理后，我们使用自研的审计系统"以太坊冲击波"，对以太坊上的合约进行整体监测，发现了以下合约均存在此漏洞。

合约名称 | 地址  
---|---  
AMMBR (AMR) | 0x96c833e43488c986676e9f6b3b8781812629bbb5  
Beauty Coin (BEAUTY) | 0x623afe103fb8d189b56311e4ce9956ec0989b412  
Beauty Coin (Beauty) | 0xb5a1df09ccaa8197d54839c2c9175ec32b560151  
Car Token (CRT) | 0xdf4b22695eeb4a7a1cf9a42162285ce782b8427a  
KoreaShow | 0x330bebabc9a2a4136e3d1cb38ca521f5a95aec2e  
Pasadena Token (PSDT) | 0x80248bb8bd26f449dea5b4d01faf936075b7111d  
Rocket Coin (XRC) | 0x6fc9c554c2363805673f18b3a2b1912cce8bfb8a  
Sinphonim (SPM) | 0x715423a818f1f9a85c66d81d2809e0a4dadf07f3  
Social Chain (SCA) | 0xb75a5e36cc668bc8fe468e8f272cd4a0fd0fd773  
  
## **资料**

AMR 合约地址：<
[_https://etherscan.io/token/0x96c833e43488c986676e9f6b3b8781812629bbb5?a=0x632e68e19107b71fc6e6b94643cc96819017c118_](https://etherscan.io/token/0x96c833e43488c986676e9f6b3b8781812629bbb5?a=0x632e68e19107b71fc6e6b94643cc96819017c118)>

##  **团队介绍**

BUGX.IO是一家致力于区块链领域的安全公司。核心团队组建于2014年，我们在区块链生态安全、行业解决方案、安全建设、红蓝对抗等方面有深厚积累与过硬专业素养。

 ***本文作者：BUGX.IO-Tri0nes，转载请注明来自FreeBuf.COM**


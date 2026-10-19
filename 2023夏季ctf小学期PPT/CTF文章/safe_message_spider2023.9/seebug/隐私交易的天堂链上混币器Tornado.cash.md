**作者：laker & 极光 @知道创宇404区块链安全研究团队  
日期：2021年3月8日**

### 前言

区块链从设计上并不是完全匿名的，充其量是伪匿名的。任何一个人或者组织可以轻而易举的创建一个Hash账户并参与校验，虽然这样的账户不会与个人进行一一对应，但由于交易的公开性、任何人都可以在公共账本上追踪你的交易，并可能利用这些信息找出你的真实身份。

寻求匿名不仅仅是罪犯和有事要隐瞒的人的专利；匿名购买比特币有很多理由。加密货币交易所持有的 know your customer
（KYC）数据是黑客攻击的主要目标，包括 Binance 和 Coinsquare 在内的多家交易所近年来都遭到黑客攻击。

### 什么是零知识证明

零知识证明(Zero—Knowledge Proof)
是由S.Goldwasser、S.Micali及C.Rackoff在20世纪80年代初提出的。它早于区块链诞生，但由于区块链，它被大家所熟知。它指的是
**证明者能够在不向验证者提供任何有用的信息的情况下，使验证者相信某个论断是正确的** 。

零知识证明可以分为 **交互式** 和 **非交互式** 两种。

  * 交互式

零知识证明协议的基础是交互式的。它要求验证者不断对证明者所拥有的“知识”进行一系列提问。证明者通过回答一系列问题，让验证者相信证明者的确知道这些"知识"。然而，这种简单的方法并不能使人相信证明者和验证者都是真实的，两者可以提前串通，以便证明者可以在不知道答案的情况下依然通过验证。

  * 非交互式

非交互式零知识证明不需要交互过程，避免了串通的可能性，但是可能需要额外的机器和程序来确定实验的顺序。

**通俗的来讲，就是既证明了自己想证明的事情，同时透露给验证者的信息为"零"。**

比如：用户在系统注册时，系统不会保存用户的密码明文，而是保存了密码的哈希值；用户在登录系统时，只需要输入注册时的密码，系统会根据用户输入密码产生的哈希值与系统数据库保存的哈希值进行比对。如果一致，则系统认为
**当前登录用户知道该账号的密码** 。

这样， **用户不需要告诉网站密码，就能证明自己的身份。这其实就是一种零知识证明。**

### 混币服务tornado.cash

Tornado.cash 可帮助你收回隐私，以隐藏发送地址的方式将 Ether 发送到任何地址。通过零知识证明实现。你可以使用此应用将 ETH
存入非托管智能合约，然后轻松生成凭据来证明你已经执行了存款，但未透露原始地址。而后，取款时应用会将此证明发送给服务商，服务商会将其提交给智能合约，然后智能合约将
ETH 发送给所需的收件人，并向服务商支付少量费用。

![1614666278721](https://images.seebug.org/content/images/2021/03/08/1615173725000-1614666278721.png-w331s)

在进行存款时，官方会返回凭据，这样你在取出时提供相应的凭据即可进行取出

![](https://images.seebug.org/content/images/2021/03/b1ccc3df-30a9-45f7-a1f8-346d08748da4.png-w331s)

存入了存款，过了一段时间以后，你便可以通过该note将存款取出，而取出时可以使用一个新的地址，这样，就无法追溯到该笔交易了。

![1614666400319](https://images.seebug.org/content/images/2021/03/08/1615173725000-1614666400319.png-w331s)

ETH的交易虽然不匿名，因为点对点的传输永远是存在一个可追溯的连接，但是tornado.cash提供了一种任何人都可以向其进行转发相同存款的方式并提供存款凭证，然后在存款者提供存款凭证时转给存款者代币的方式来尝试去掉这个连接。

### 区块链透明传输环境进行匿名token转移如何实现

在tornado.cash具体实现中采用了Merkle Tree，用户每次存款将会调用insert向Merkle Tree中进行结点插入（存款证明）

    
    
    function deposit(bytes32 _commitment) external payable nonReentrant {
        require(!commitments[_commitment], "The commitment has been submitted");
    
        uint32 insertedIndex = _insert(_commitment);//插入树结点
        commitments[_commitment] = true;//证明置为true
        _processDeposit();
    
        emit Deposit(_commitment, insertedIndex, block.timestamp);
      }
    
    
    function _insert(bytes32 _leaf) internal returns(uint32 index) {
        uint32 currentIndex = nextIndex;
        require(currentIndex != uint32(2)**levels, "Merkle tree is full. No more leafs can be added");
        nextIndex += 1;
        bytes32 currentLevelHash = _leaf;//_commitment传递到currentLevelHash
        bytes32 left;
        bytes32 right;
    
        for (uint32 i = 0; i < levels; i++) {
          if (currentIndex % 2 == 0) {
            left = currentLevelHash;
            right = zeros[i];
    
            filledSubtrees[i] = currentLevelHash;
          } else {
            left = filledSubtrees[i];
            right = currentLevelHash;
          }
    
          currentLevelHash = hashLeftRight(left, right);
    
          currentIndex /= 2;
        }
    
        currentRootIndex = (currentRootIndex + 1) % ROOT_HISTORY_SIZE;
        roots[currentRootIndex] = currentLevelHash;//写入currentLevelHash到Merkle Tree
        return nextIndex - 1;
      }

最终经过添加Merkle Tree叶子节点后给出一个存款证明。形如

![](https://images.seebug.org/content/images/2021/03/c4c894d4-0478-45e7-bc02-76c5470a967d.png-w331s)

当存款者在取钱的时候，则可以通过提供该凭据进行取出，但是这里不禁有人会问，仿佛没有体现零知识证明？

事实上，在存币时，真正被提供的数据为：

![1614842066482](https://images.seebug.org/content/images/2021/03/08/1615173725000-1614842066482.png-w331s)

![](https://images.seebug.org/content/images/2021/03/5556fc35-dd62-4c6a-8c42-3cb5eb466e40.png-w331s)

![](https://images.seebug.org/content/images/2021/03/79c2866c-2890-4b06-8ce0-47969254fe9b.png-w331s)

![](https://images.seebug.org/content/images/2021/03/80ef2706-fe3e-40d1-bdbe-5dbf6748da98.png-w331s)

而在取出时取款者提供的数据则通过note进行解密成为如下参数

_proof：存款证明

_root：表示在哪一个Merkle Tree根

_nullifierHash： 代表是否无效化，置为true则该存款已使用

_recipient ： 取款时代币接受者的地址

![1614842152866](https://images.seebug.org/content/images/2021/03/08/1615173725000-1614842152866.png-w331s)

传入数据是根据存款后返回的note进行解密进行填入的，相当于在交易的过程中，你通过存币后返回的的_proof、_root、_nullifierHash
来证明了你的存款，这便是零知识证明的体现。

在代码层面上，如何通过_proof、_root、_nullifierHash证明这笔存款呢？

这里就要关注withdraw函数了：

    
    
        function withdraw(bytes calldata _proof, bytes32 _root, bytes32 _nullifierHash, address payable _recipient, address payable _relayer, uint256 _fee, uint256 _refund) external payable nonReentrant {
        require(_fee <= denomination, "Fee exceeds transfer value");
        require(!nullifierHashes[_nullifierHash], "The note has been already spent");
        require(isKnownRoot(_root), "Cannot find your merkle root"); // Make sure to use a recent one
        require(verifier.verifyProof(_proof, [uint256(_root), uint256(_nullifierHash), uint256(_recipient), uint256(_relayer), _fee, _refund]), "Invalid withdraw proof");
    
        nullifierHashes[_nullifierHash] = true;
        _processWithdraw(_recipient, _relayer, _fee, _refund);
        emit Withdrawal(_recipient, _nullifierHash, _relayer, _fee);
      }

回撤时采用三部分数据，_root表示对应的Merkle Tree，_nullifierHash同时也表达是否该条存款被使用。

在最后的存款验证阶段使用了一个单独的验证器合约，在此地址进行了部署

<https://etherscan.io/address/0xce172ce1f20ec0b3728c9965470eaf994a03557a#code>
![](https://images.seebug.org/content/images/2021/03/9968b7d3-5c8b-45c2-90cd-94cc0224f12d.png-w331s)

关键函数verifyProof，该函数则是零知识验证的具体实现，载入Proof后将input(uint256(_root),
uint256(_nullifierHash), uint256(_recipient), uint256(_relayer), _fee,
_refund)依次加载进vk_x并交给Pairing.pairing进行校验，具体代码实现如下：

    
    
    function verifyProof(
            bytes memory proof,
            uint256[6] memory input// _proof, [uint256(_root), uint256(_nullifierHash), uint256(_recipient), uint256(_relayer), _fee, _refund]
        ) public view returns (bool) {
            uint256[8] memory p = abi.decode(proof, (uint256[8]));
    
            // Make sure that each element in the proof is less than the prime q
            for (uint8 i = 0; i < p.length; i++) {
                require(p[i] < PRIME_Q, "verifier-proof-element-gte-prime-q");
            }
    
            Proof memory _proof;// 初始化Proof
            _proof.A = Pairing.G1Point(p[0], p[1]);// 将dp上的Prove赋值
            _proof.B = Pairing.G2Point([p[2], p[3]], [p[4], p[5]]);
            _proof.C = Pairing.G1Point(p[6], p[7]);
    
            VerifyingKey memory vk = verifyingKey();// 生成vk
    
            // Compute the linear combination vk_x
            Pairing.G1Point memory vk_x = Pairing.G1Point(0, 0);
            vk_x = Pairing.plus(vk_x, vk.IC[0]);
    
            // Make sure that every input is less than the snark scalar field
            for (uint256 i = 0; i < input.length; i++) {
                require(input[i] < SNARK_SCALAR_FIELD, "verifier-gte-snark-scalar-field");
                vk_x = Pairing.plus(vk_x, Pairing.scalar_mul(vk.IC[i + 1], input[i]));// 加载进vk_x
            }
    
            return Pairing.pairing(
                Pairing.negate(_proof.A),
                _proof.B,
                vk.alfa1,
                vk.beta2,
                vk_x,
                vk.gamma2,
                _proof.C,
                vk.delta2
            );
        }

在通过该验证后（确认已存款并且该存款未被取出）则进行取款标志置为true并利用_processWithdraw函数进行资产取出

    
    
    function _processWithdraw(address payable _recipient, address payable _relayer, uint256 _fee, uint256 _refund) internal {
        // sanity checks
        require(msg.value == 0, "Message value is supposed to be zero for ETH instance");
        require(_refund == 0, "Refund value is supposed to be zero for ETH instance");
    
        (bool success, ) = _recipient.call.value(denomination - _fee)("");
        require(success, "payment to _recipient did not go thru");
        if (_fee > 0) {
          (success, ) = _relayer.call.value(_fee)("");
          require(success, "payment to _relayer did not go thru");
        }
      }

具体算法描述如下

要取出树中位置为 i 的硬币（k，r），用户按以下步骤操作：

![](https://images.seebug.org/content/images/2021/03/5f135d2e-2722-43ee-92d6-5cc4fb0e8585.png-w331s)

智能合约验证了_nullifierHash散列的真实性和唯一性。在验证成功的情况下，它发送（N−f）到指定地址并将h置为true添加到哈希列表中。

> nullifierHashes[_nullifierHash] = true;

![](https://images.seebug.org/content/images/2021/03/343b10d1-2430-4d08-8550-c16797e8f887.png-w331s)

### 思考：tornado.cash真的匿名吗

Tornado通过使用智能合约打破地址之间的链上联系来改善交易隐私，
**该合约接受ETH存款，随后可由不同的地址提取。用户在存款时需要提供秘密的哈希值，之后在提现时提供zkSnark证明，以显示对秘密的了解，而不泄露秘密或之前的存款本身**
。这样就把提现和存款脱钩了。而是否这样已经达到足够的匿名了呢？显然不是

  * 在存取款的过程中，仍旧应该使用代理等手段隐藏自己的网络层数据等信息，ISP可以记录发送到中继层的数据包的时间戳，并将它们与取款事务时间戳相关联。

  * 存取款时间间隔问题，若存取款时间间隔较短，将可能导致存取款交易发生时间关联，造成匿名性的削减。因此官方建议在存款后过一段时间之后再执行取款操作。

除此之外，
**在其他混币服务中可能只设计一个回撤合约调用，这里如果需要直接调用合约并且不涉及接收地址的参数传递进行新地址提现则时，要从一个新生成的地址中执行该回撤函数提现交易，那么用户则需要在里面有一些ETH来支付gas**
。但这个ETH的来源（一般是交易所）会破坏Tornado的隐私。因此，首选的替代方案是再次使用中继器网络。

原本gas的主动支付需要依赖于在KYC后的中心化交易所购买ETH，而替代方案旨在通过将用户的负担转移到中继器上，以减少这种上链用户体验摩擦，其成本由钱包提供商链上/链下和/或用户链下补偿。

### 总结

**零知识证明可以让原本透明的数据（_commitment）进行隐藏和下链（note的不可获取性）**
，但是在下链和上链过程中的隐私安全不被tornado.cash保护，仍需自行做出一些防护。

下链后通过note还原证明数据（_proof, [uint256(_root), uint256(_nullifierHash),
uint256(_recipient), uint256(_relayer), _fee,
_refund])），该凭据note是恢复你的R(_Root)、h(_nullifierHash)、A(_recipient)、f(费用)、P(_proof)的唯一方式，切不可丢失或遗忘。

最后进行存款的证明并转给一个新的地址，从而中断转账中透明的数据连接的效果。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1497/>


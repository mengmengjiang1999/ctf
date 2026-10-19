***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![-1.png](https://image.3001.net/images/20180717/15318115438519.png!small)**

##  **前言**

2017年7月19号发生的 Parity 多重签名合约delegatecall漏洞(Parity Multisig Wallet
delegatecall)事件之后，2017年11月6号再次发生了 Parity 多重签名函数库自杀漏洞事件(Parity Multi-Sig
Library Self-Destruct)事件。此次漏洞影响587个钱包，包含了 513,774.16 Ether($152 million)。

一名叫做 devops199 的开发者能够让自己成为函数库合约的 owner，然后有调用自杀功能，使得合约所有功能、通证均失效。之后，devops199 在
github 提交了 issue，说出了一句经典的话 I accidentally killed it.

![0.png](https://image.3001.net/images/20180717/15318115642897.png!small)

###  **◆ 分析**

Parity Multisig Wallet delegatecall 漏洞之后，官方修复了这个漏洞，

地址在：

<https://etherscan.io/address/0x863df6bfa4469f3ead0be8f9f2aae51c91a907b4#code>

<https://github.com/paritytech/parity/pull/6103/files>。

修复方法就是在init*函数加上only_uninitialized modifier 判断，当 m_numOwners 0 时这个函数就不能使用。

![666.png](https://image.3001.net/images/20180717/1531811630656.png!small)

但是仍然有缺陷，因为函数库没有正确初始化，被利用方式如下：

 **① 所有的 Parity Multisig wallets 都使用单一的函数库：**

<https://etherscan.io/address/0x863df6bfa4469f3ead0be8f9f2aae51c91a907b4#code>
但是，这个函数库合约没有正确地初始化。  

**② 攻击者先获取owner权限，将调用函数的指令放在Data中。**

恶意行为在：

<https://etherscan.io/tx/0x05f71e1b2cb4f03e547739db15d080fd30c989eda04d37ce6264c5686e0722c9>

**![123.png](https://image.3001.net/images/20180717/1531811727442.png!small)**

 **③** **然后获取调用kill函数**

恶意行为在：

<https://etherscan.io/tx/0x47f7cff7a5e671884629c93b368cb18f58a993f4b19c2a53a8662e3f1482f690>

![234.png](https://image.3001.net/images/20180717/15318117602139.png!small)![345.png](https://image.3001.net/images/20180717/1531811771659.png!small)

 **④ 导致两个结果：**

1）所有用户的以太币都被冻结。

2）很多使用这个钱包的合约引入位置都写死，导致很多合约不能运作，如在 Polkadot 里第 451 行就将钱包合约地址写死：

<https://etherscan.io/address/0x3bfc20f0b9afcace800d73d2191166ff16540258#code>

![567.png](https://image.3001.net/images/20180717/15318118866523.png!small)因为所有逻辑判断都在钱包合约中，所以其他相依于钱包合约的现在以太币都被冻结，且看起来无法提款：  

![999.png](https://image.3001.net/images/20180717/15318120152718.png!small)

所有受影响的合约如下：

<https://pastebin.com/ejakDR1f>

###  **◆防范**

这次的事件 Parity
说明有两种预防方式。一种是智能合约不该有自杀的函数，这样即便黑客获得了权限也无法把合约移除。一种是有新的建议及改善时，要及时更新线上的合约或是找寻线上合约可能的漏洞，因为在这问题发生前，就有网友提议在合约部署时要自动呼叫
initWallet(pr) 加強合约的安全。

###  **◆本地复现**

    
    
    git clone
    
    https://github.com/Martin2877/parity_kill_example.git # 下载复现代码
    
    npm install # 安装组件
    
    npm run start-block # 启动tesrRPC
    
    # 打开新窗口
    
    npm start # 运行测试代码  
    

![1.jpg](https://image.3001.net/images/20180717/15318122077703.jpg!small)

不成功的情况：

![2.jpg](https://image.3001.net/images/20180717/15318122203124.jpg!small)

不成功，原因是因为安装的testrpc为6.0.3，改用6.0.1可以解决。可以 `npm list --depth 0` 查看安装的包的情况。

###  **◆资料**

事件脉络：

<https://medium.com/crypt-bytes-tech/parity-wallet-security-alert-vulnerability-in-the-parity-wallet-service-contract-1506486c4160>

其它相关资料：

<https://medium.com/chain-cloud-company-blog/parity-multisig-hack-again-b46771eaa838>

<https://paritytech.io/a-postmortem-on-the-parity-multi-sig-library-self-destruct/>

<https://paritytech.io/security-alert-2/>

<https://github.com/paritytech/parity/issues/6995>

###  **◆团队介绍**  

BUGX.IO是一家致力于区块链领域的安全公司。核心团队组建于2014年，我们在区块链生态安全、行业解决方案、安全建设、红蓝对抗等方面有深厚积累与过硬专业素养。

 ***本文作者：BUGX.IO-Tri0nes，转载请注明来自FreeBuf.COM**


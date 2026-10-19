***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 事情概述

 **近期比特币轻钱包electrum的部分用户遭到了定向的钓鱼弹窗攻击，用户在使用electrum轻钱包转账的时候提示转账失败。**

![1.png](https://image.3001.net/images/20181228/1545989636_5c25ee04c31fe.png!small)

部分electrum用户便按照软件弹出的提示，去弹窗上的地址下载最新版本的钱包，但是此时下载的轻钱包却是恶意的。使用钱包需要导入私钥，用户导入私钥之后，恶意软件便窃取了用户的比特币。

## 事情简析

### 2.1 比特币全节点钱包

全节点钱包除了保存有私钥外，还保存有所有区块的数据，这样就可以在本地直接验证交易数据的有效性。最著名的全节点钱包就是Bitcoin
Core。其他比特币全节点如go语言编写的btcd，javascript编写的bcoin也都是全节点钱包。但是全节点钱包会占用大量硬盘空间，截止到18年底，比特币的全节点要占用将近200gb的硬盘空间。转账之前必须要同步200gb数据，这对于一般用户来说是难以接受的。

###
![2.png](https://image.3001.net/images/20181228/1545989673_5c25ee2924b48.png!small)
2.2 比特币轻钱包

轻钱包只保存跟自己相关的数据，体积很小，大都使用SPV进行交易的验证和支付。(全称“Simplified Payment
Verification”,简单支付验证)，所以也称为SPV钱包。比特币主要的SPV钱包有，MultiBit
Breadwallet等，他们使用SPV协议直接连接到比特币全节点(中本聪客户端或者其他语言版本的比特币客户端)进行验证和支付。

![3.png](https://image.3001.net/images/20181228/1545989693_5c25ee3d1de7d.png!small)

可以看到，一个全节点有大量的比特币SPV轻钱包的连入。

Electrum是比特币比较出名的一个轻钱包，该轻钱包加入了一些新特性，如服务器使用SSL进行身份验证来防止MITM攻击。所以跟其他的比特币轻钱包不同，Electrum无法与不同版本的比特币全节点进行直接通讯，每次启动会连接到electrum
server进行通讯，而electrum server之间通过p2p进行通讯。

 _<https://electrumx.readthedocs.io/en/latest/peer_discovery.html>_

![4.png](https://image.3001.net/images/20181228/1545989713_5c25ee518dea3.png!small)

可以看到用户可以手动指定连接到自己的electrum server。但是大多数用户对原理并不了解，也不会搭建自己的electrum server。

### 2.3 攻击原理

问题最早由用户SomberNight在github上进行了反馈。

Electrum黑客预先在P2P网络埋伏了大量的“正常” electrum server。

![5.png](https://image.3001.net/images/20181228/1545989740_5c25ee6c6aa65.png!small)

从网站监控上可以看到，比特币的electrum server目前只有210个节点在线。 _<https://1209k.com/bitcoin-eye/ele.php?chain=btc>_

![6.png](https://image.3001.net/images/20181228/1545989755_5c25ee7b093d5.png!small)

而比特币全节点bitnodes的统计数据为10205个全节点在线。

![7.png](https://image.3001.net/images/20181228/1545989780_5c25ee943a7b5.png!small)

前面已经说过，由于electrum轻钱包不同于MultiBit或Breadwallet等比特币轻钱包，无法与比特币全节点直接通讯，只能与electrum
server进行通讯。此时有限的electrum server节点中大量混入了黑客的malicous节点。

用户使用钱包转账时，当手续费不足或者缺少输入的时候，钱包会弹error框给用户的。黑客正是利用了这个弹框，当electrum轻钱包用户连接到的几个节点全都是黑客的malicous节点，malicous节点便会拒绝帮用户广播转账消息，然后返回自定义的错误消息，此时electrum轻钱包软件便会弹窗展示malicous
server的自定义消息给用户，自定义消息提示用户需要到[ _https://github.com/electrum-wallet/electrum/releases_](https://github.com/electrum-wallet/electrum/releases) 去下载最新版electrum 软件。由于弹窗在electrum中显示，迷惑性极大。

实际上electrum软件的真正下载地址是[
_https://github.com/spesmilo/electrum/releases_](https://github.com/spesmilo/electrum/releases)，根本不是弹窗中的地址。

![1.png](https://image.3001.net/images/20181228/1545989836_5c25eecc0d3b3.png!small)

## 攻击复盘。

攻击由于以下几点原因产生。

A: electrum server节点过少，网站统计仅仅有210个，使得黑客的malicous server大概率占据用户electrum连接的所有节点。

B: electrum server可以自定义消息在用户的electrum轻钱包软件中展示。

C: 用户的安全意识差，安装重要软件之前不核对下载网址和校验软件发行版本hash。

北京链安在此郑重提醒所有用户提高安全防护意识。

该次攻击只是钓鱼攻击的一种，黑客完全可以侵入钱包官方网站或者IDC的CDN下载服务器埋放恶意钱包软件进行钓鱼。安装软件之前请务必校验软件hash，确保软件安全。

 ***本文作者：北京链安安全实验室，转载请注明来自FreeBuf.COM**


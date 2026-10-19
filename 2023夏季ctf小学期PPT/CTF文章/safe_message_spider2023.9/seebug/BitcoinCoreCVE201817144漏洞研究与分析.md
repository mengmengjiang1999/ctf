**作者：腾讯湛泸实验室  
来源：[微博@腾讯湛泸实验室](https://media.weibo.cn/article?id=2309404305612610623070&from=timeline&isappinstalled=0&display=0&retcode=6102
"微博@腾讯湛泸实验室")**

今年9月18号，比特币主流客户端Bitcoin
Core发表[文章](https://bitcoincore.org/en/2018/09/20/notice/
"文章")对其代码中存在的严重安全漏洞CVE-2018-17114进行了全面披露。该漏洞由匿名人士于9月17日提交，可导致特定版本的Bitcoin
Core面临拒绝服务攻击（DoS，威胁版本: 0.14.x - 0.16.2）乃至双花攻击(Double Spend，威胁版本: 0.15.x -0.16.2)。

Bitcoin Core项目组对于该漏洞进行了及时的修补，在向其他分支项目组（如Bitcoin
ABC）进行了漏洞通告并提醒用户进行版本升级后，公布了上段所提到的漏洞披露文章。该文章中对漏洞的成因、危害、影响版本及修复过程时间线进行了简单介绍，但未对漏洞进行详尽分析。

本文基于该漏洞披露文章及Bitcoin
Core项目组在Github上的漏洞修复和测试代码，着重分析该漏洞的修复方法、触发方法、漏洞成因及其所带来的危害。文中涉及测试脚本及PDF版本可于<https://github.com/hikame/CVE-2018-17144_POC>下载。

### 1\. 漏洞修复

在Bitcoin Core的master代码分支上，[commit
b8f8019](https://github.com/bitcoin/bitcoin/commit/b8f801964f59586508ea8da6cf3decd76bc0e571
"commit b8f8019")对这一漏洞进行了修复，如图 1所示。

![
](https://images.seebug.org/content/images/2018/11/93e66e89-3c50-42e1-8a4d-3c829558f369.jpg-w331s)
图 1 CVE-2018-17144修复方法

这段代码位于src/validation.cpp中的CheckBlock()函数，该函数在节点接收到新的区块时被调用。第3125行调用的CheckTransaction()函数及其第三个参数的意义可以参照其代码实现进行分析。

![
](https://images.seebug.org/content/images/2018/11/6c35564c-60ac-4fd0-a442-62438a4d6f07.jpg-w331s)

CheckTransaction()函数对于传入的交易消息（CTransaction&
tx）进行检测，其中包括了检测一笔交易是否发生双花。检测方案非常简单，将这比交易中使用的所有Coin（即代码中的txin.prevout，代表比特币交易中的[UTXO](https://bitcoin.org/en/glossary/unspent-transaction-output
"UTXO")，本文后续均采用Coin一词进行表述，以便与代码持一致）记入std::set中，如果发现某项记录被重复记录了两次，就会返回处理失败的信息（state.DoS），这一消息最终会通过P2P通道，反馈给该区块的发送者。基于代码段中的备注部分，可以看出，这段检测代码在被CheckBlock()函数的调用过程中被认为是冗余和费时的，并通过将函数的第三个参数设置为False的方式，使其跳过。

CheckBlock()执行选择跳过双花检查，是由于其后续会对于整个区块中的交易进行更为复杂而全面的检查。然而，这些检查代码未能像预期的那样对某些异常情况进行检测和处置，导致了漏洞的存在。

### 2\. 漏洞PoC

Bitcoin Core的Github上提供了实现DoS攻击的测试脚本；但要想进行双花攻击的测试，需要自己编写攻击脚本。

#### 2.1. DoS攻击PoC

Bitcoin的master代码分支上，commit b8f8019（即前文提到的漏洞修复commit）的子[commit
9b4a36e](https://github.com/bitcoin/bitcoin/commit/9b4a36effcf642f3844c6696b757266686ece11a
"commit 9b4a36e")给出了该漏洞的验证代码，如图 2所示。

![
](https://images.seebug.org/content/images/2018/11/ca4271db-a35b-47a1-a836-f1f37bcdc392.jpg-w331s)
图 2 官方漏洞PoC

这段使用Python编写的测试代码，位于test/functional/p2p_invalid_block.py测试脚本中。该脚本构建了一个测试网络，测试代码可以通过RPC接口、P2P接口等方式连接到目标节点，并发送测试数据，如恶意构造的区块数据、交易信息等。图
2中新添加的测试代码的功能是：在block2_orig区块中找到了第二项交易（vtx[2]），并将其交易输入中的第一个Coin（vtx[2].vin[0]）重复加入到了输入序列中，从而构造一个使用vtx[2].vin[0]进行双花的交易消息。如92行所示，向已被修复漏洞的node端发送block2_orig区块时，会收到node反馈的拒绝接收消息，其消息内容即为“bad-txns-duplicate”。

如果利用该测试的代码针对未修复漏洞的节点进行测试，则产生的效果如图
3所示。由于测试脚本恶意构造的区块数据引发了目标节点的崩溃，导致了Python脚本与node进程之间的P2P连接断开，使其抛出了ConnectionResetError。

![
](https://images.seebug.org/content/images/2018/11/de477fee-4e0a-438e-952e-14e9ed9b67fc.jpg-w331s)
图 3 官方PoC测试效果图

#### 2.2. 双花攻击PoC

官方的PoC给出了DoS攻击的示意。然而，这段PoC在仅有一个node的测试网络中运行，并且所有交易数据的解锁脚本均被设定为“任何人均可花费”。由于其特殊性，对于验证双花攻击欠缺一定的说服力。因此，本文基于Bitcoin
Core的测试框架，自行编写了一套漏洞验证脚本。

![
](https://images.seebug.org/content/images/2018/11/abde211c-7519-48a1-b0ba-95228e4f9fb0.jpg-w331s)
图 4 双花攻击网络环境示意图

测试过程中的三个角色如图
4所示。N0代表攻击者，利用Python程序所编写的恶意P2P服务，构造恶意区块数据；N1代表诸多正常节点中的一个，是N0的邻居节点，两者通过P2P接口进行消息传递。测试脚本关键代码如下。

![
](https://images.seebug.org/content/images/2018/11/d3b4250e-199e-4a61-b328-17269de2484f.jpg-w331s)

### 3\. 漏洞细节分析

本文从直接导致DoS的PoC开始进行调试，这可以帮助我们快速定位问题代码的位置。利用GDB进行调试，发现发生崩溃时的代码调用栈如下（线程名：msghand）。

![
](https://images.seebug.org/content/images/2018/11/a67c5ba4-710d-46e3-ba29-76a45f8442f9.jpg-w331s)

崩溃现场代码如图
5，根据函数及变量名称可以大致猜想，在进行Coin的更新过程中，会首先检查每笔交易的是否已被花费，如是，则assert失败，导致DoS（Bitcoin
Core官方发布的客户端程序开启assert）。那么为什么又会存在双花攻击的效果呢？这里需要对inputs.SpendCoin()的实现做进一步的分析。

![
](https://images.seebug.org/content/images/2018/11/449671b7-2892-4c55-a17d-4d2053d33727.jpg-w331s)
图 5 DoS代码现场截图

#### 3.1. CCoinsViewCache::SpendCoin()分析

图
5中，inputs变量的类型为CCoinsViewCache类，每个该类的对象均与一个区块对应，并且在其名为base的域中存储了指向其前驱区块的CCoinsViewCache对象的指针。该类中另一个关键的内部变量为cacheCoins，存储了当前区块的处理过程中新产生的或从前驱区块中查询到的Coin信息，它是一个std::map结构，key值为Coin对象的索引信息（所属交易的Hash、UTXO在该交易输出序列中的序号），value值则为Coin的具体信息（货币数额、解锁脚本等）。

CCoinsViewCache::SpendCoin()函数实现如图
6所示。该函数作用为检查outpoint所代表的某个交易的输出是否被花费过。下面将对于这三点展开详细分析。

![
](https://images.seebug.org/content/images/2018/11/54dc2809-1d9e-4951-93f4-2cca8fae050a.jpg-w331s)
图 6 CCoinsViewCache::SpendCoin()代码

##### 3.1.1. CCoinsViewCache::FetchCoin()功能与实现

该函数用于查询outpoint对应的交易的具体信息。图 7中是该函数的实现代码：

尝试从当前CCoinsViewCache对象的cacheCoins中查询Coin信息，如存在则返回（41-43行）；

  1. 尝试从当前CCoinsViewCache对象的cacheCoins中查询Coin信息，如存在则返回（41-43行）；

  2. 如1) 中未能找到，则从base所代表的前驱区块中进行交易信息的查询，查询方式是调用GetCoin()函数，该函数会进一步调用FetchCoin()函数，也就是在base->cacheCoins中查找Coin信息，当Coin信息被顺利查到，且其未被花费时，返回True（45-46行）；

  3. 如2)从前驱区块中顺利找到Coin信息，则将其加入当前区块的cacheCoins中，以备后续使用（47-52行）。

![
](https://images.seebug.org/content/images/2018/11/41a09b5c-5f7c-4f67-8ea6-2b9f7af5a70b.jpg-w331s)
图 7 CCoinsViewCache::FetchCoin()代码

##### 3.1.2. cacheCoins的内容维护

对于一个区块所维护的cacheCoins，向其添加新的Coins的可能途径有两种：

  1. 第一种即图 8第47行所显示的，CCoinsViewCache::FetchCoin()执行过程中，从其前驱区块中查询到了相应Coin信息；

  2. 第二种发生在区块的交易信息中产生了新的Coin时，其对应的函数为AddCoin()，源码如图 8所示，对于一个普通的Coin（非产生于Coinbase交易），会将其记录到cacheCoins中，并于83行设置相应Coin Flag标志。

![
](https://images.seebug.org/content/images/2018/11/464fb9ed-3258-4eba-b102-841223960d5e.jpg-w331s)
图 8 CCoinsViewCache::AddCoin()代码

##### 3.1.3. Coin Flag的意义与取值

CCoinsViewCache类SpendCoin()、FetchCoin()、AddCoin()函数中均有关于Coin的Flag操作。Coin
Flag存在两个状态标志位Fresh和Dirty，Bitcoin Core中对于这两个状态标志为的定义及注释如图 9，可以看出：

  1. Dirty标志位表示当前缓存的Coin信息与base所指向CCoinsViewCache对象所记录的Coin信息不同；

  2. Fresh标志位表示这个Coin的信息在base所指向的CCoinsViewCache对象中没有记录。

基于其描述，AddCoin()的代码中（图
8中76-83行），对于一个区块中的普通交易所产生的新的Coin，其Fresh标志置1；FetchCoin()的代码中，对于来自前驱区块的Coin，其Flag在当前CCoinsViewCache对象中进行缓存时的flag被置0，即既非Fresh也非Dirty的初始状态（图
7中第47行）。

![
](https://images.seebug.org/content/images/2018/11/03ecb86d-76d7-40b5-bde1-7099f44a8552.jpg-w331s)
图 9 Coin Flag的定义与注释

#### 3.2. 漏洞触发原理分析

在3.1中完成了对于相关代码的细节分析后，我们可以对于代码发生异常时的执行状态开展进一步的分析了。

##### 3.2.1. DoS攻击原理分析

攻击过程关键代码示意如下，攻击代码第4行将block2.vtx[2].vin[0]重复加入了block2.vtx[2].vin中，是实现双花的关键操作。block2.vtx[2]实际上是tx2，其构建代码如第２行所示：可以看出tx2以tx1的输出中序列号为0的Coin作为输入。而tx1、tx2在第三行被加入同一区块block2中。

![
](https://images.seebug.org/content/images/2018/11/0346f3dd-94be-45bf-8276-ffc968ce48b3.jpg-w331s)

被攻击节点在接收到block2后的处理过程如下：

  1. 交易tx1处理。经一系列验证分析后，该交易被认为是一笔有效交易，为了记录其输出，将调用图 8中的AddCoins()函数，该函数会在当前CCoinsViewCache对象的cacheCoins中添加一个新的Coin，并将其Flag设置为Fresh | Dirty；

  2. 交易输入tx2.vin[0]处理。图 7 CCoinsViewCache::FetchCoin()代码被调用以查找对应Coin信息，1) 中的操作已将Coin信息加入当前CCoinsViewCache对象的cacheCoins。因此第43行将直接返回；而图 6 CCoinsViewCache::SpendCoin()代码会因为该Coin有Fresh标签，执行到第106行，并将其从cacheCoins中删除；

  3. 交易输入tx2.vin[1]处理。图 7 CCoinsViewCache::FetchCoin()代码将再次被调用，但是，由于2)中已将相应Coin信息删除，而base->GetCoin()又无法查知该Coin，将导致46行代码返回cacheCoins.end()，进而使SpendCoin()返回False，最终触发assert失败。

##### 3.2.2. 双花攻击原理分析

攻击过程关键代码如下。第1行中，block1的挖矿奖励的接收者被设定为node0的地址。第二行构建的交易消息tx2即以该交易输出的Coin为输入，并且重复使用了两次，而且tx2输出的Coin数量是挖矿奖励的两倍，是典型的双花行为。

![
](https://images.seebug.org/content/images/2018/11/950c607a-0f65-4796-ba89-a0d86d220d2c.jpg-w331s)

被攻击节点在接收到block2的数据后的处理过程为：

  1. 处理第一个交易输入block1.vtx[0]。由于该交易位于前驱节点，需要调用base->GetCoin()以获取相应Coin信息，该信息的flag被默认置0，在图 6 CCoinsViewCache::SpendCoin()代码的执行过程中，将执行108-109行代码，置Dirty位，并将其余额清除，以标记已被花费；

  2. 处理第二个交易输入block1.vtx[0]。由于1)中已经添加了相应的Coin信息，在图 7 CCoinsViewCache::FetchCoin()代码中的43行可以直接返回该信息，但是在SpendCoin()及后续代码中的执行过程中，没有对该Coin是否已被花费进行有效验证，导致双花行为没能检测出来。

### 4\. 危害分析

基于[官方的漏洞通告](https://bitcoincore.org/en/2018/09/20/notice/ "官方的漏洞通告")，Bitcoin
Core的0.14.X-0.16.2版本均面临DoS攻击的威胁，而且其中的0.15.X-0.16.2版本还面临双花攻击的威胁。本文基于[Bitnodes网站](https://bitnodes.earn.com/nodes/
"Bitnodes网站")的数据对相应版本的节点数目做了如下表统计（总数为9970个节点，数据统计于2018-11-09）。

需要注意的事，要想利用此漏洞实现攻击，其限定条件为：

  1. 异常交易数据必须打包到区块中才能触发漏洞。如果攻击者试图利用P2P接口向受害者节点直接发送异常交易数据，会触发CheckTransaction()函数中的双花检查，无法触发漏洞。

  2. 攻击者必须自行挖掘出一个最新的比特币区块。包含恶意交易信息的最新区块必须是有效的，否则，无法通过在交易处理之前的区块头检查。

基于上述分析，在攻击者拥有较大算力以进行区块挖掘的前提下，两种攻击手段所能带来的危害有：

  1. DoS攻击，大约可危害37%的主网节点；

  2. 双花攻击，需要超全网51%的算力认同恶意构造的区块，并进行后续区块的挖掘。基于表 1统计可知面临此类攻击威胁的节点数约占32%，但由于无法统计这些节点的算力占比，所以无法确认双花攻击的危害程度。

### 5\. 总结

本文分析的CVE-2018-17144是近年来较为少见的、存在于比特币主流客户端中的安全漏洞。此漏洞所带来的启示有：一方面，Bitcoin
Core项目组的漏洞修复和处置方案有效遏制了此次漏洞带来的安全威胁，值得其他区块链项目组借鉴；另一方面，区块链节点客户端的安全是整个区块链系统安全的基石，对其开展更加深入和全面的研究是十分有必要的。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/742/>


**作者：Ethan Heilman, Neha Narula, Garrett Tanzer, James Lovejoy, Michael
Colavita, Madars Virza, and Tadge Dryja**  
**原文：[Cryptanalysis of Curl-P and Other Attacks on the IOTA
Cryptocurrency](https://www.semanticscholar.org/paper/Cryptanalysis-of-Curl-P-and-Other-Attacks-on-the-Heilman-Narula/f402d8bed20deb03d1ab8c99c3f81deaf59a4a70 "Cryptanalysis of Curl-P and
Other Attacks on the IOTA Cryptocurrency")**  
**译者：知道创宇404实验室**

### 摘要

本文介绍了使用伪造签名攻击IOTA区块链的方法。加密哈希函数Curl-P-27中存在一些弱点，允许攻击者快速生成可碰撞的短消息，并且这个方法也适用于相同长度的消息，利用这些弱点我们实现了对加密哈希函数Curl-P-27的攻击，破解了前IOTA签名方案（ISS）的EU-CMA。本文最后我们将介绍如何在消息已经被签署的情况下伪造有效支出的签名和多重签名（在IOTA中称为bundle）。

关键词：加密货币，签名伪造，加密哈希函数，密码分析

### 1 介绍

加密货币通过数字签名来鉴别用户的转账行为。为了提高性能，在许多签名方案中，用户签署的是消息的哈希值而不是消息本身。在此情况下，如果底层哈希函数受到了攻击，攻击者便可以在付款时伪造数字签名。

IOTA
的付款操作需要获得签名方案的授权。本文介绍了对该签名方案的攻击，这些攻击利用了哈希函数Curl-P-27的弱点。重要的是，我们在2017年8月披露并修补了此漏洞，由此保证了IOTA签名方案的安全性[20]。

IOTA是一种加密货币，被应用于物联网（IoT）和汽车生态系统。截至2018年7月24日，它以26亿美元的市值成为全球第九大最有价值的加密货币[9]。许多公司与
IOTA 有过合作，包括汽车制造商大众汽车公司和欧洲大型工业公司博世公司。 IOTA 曾发布公告称大众汽车计划在2019年初发布一款使用 IOTA
的产品[7]。 2017年底，博世购买了“大量 IOTA代币”[6]。此外，IOTA 基金会与台北市签署了一项协议，将 IOTA
用于其智能城市计划，其中包括数字市民卡项目[8]。

IOTA使用加密签名来授权用户付款。基于 Winternitz 一次性签名[25]，IOTA建立了自己的签名方案（ISS）。但与传统的 Winternitz
签名不同，IOTA 用户签署的是消息的哈希值。由此可见，ISS的安全性依赖于其加密哈希函数，即
Curl-P-27。通过常见的差分密码分析方法，我们可以使用Curl-P-27快速创建哈希值相同且长度相同的消息，从而打破了功能的碰撞阻力。我们做到了每次都能在一个上限值之内实现碰撞。

使用此碰撞攻击，我们可以在 IOTA
中伪造签名。我们从被签署的消息着手，为攻击者分别创建良性支付和恶意支付，并且使这两种支付具有相同的有效签名。我们的攻击适用于正常付款和多签名付款，并且只针对IOTA
签名方案，而没有包括整个 IOTA
网络。从多签名地址支出需要一个用户为另一个用户签名支付，这完全取决于如何设置被签署消息。我们详细介绍了如何攻击多签名地址支出，并提供了在单签名和多签名付款中生成碰撞的工具，并且评估了攻击的效率。在使用80个核的条件下，我们可以在不到20秒的时间内制造
IOTA 付款碰撞。

#### 1.1 漏洞状况和影响

2017年7月14日，我们与 IOTA 开发人员准备披露这个攻击，并且就修补漏洞的时间安排以及发布日期进行了协商。 2017年8月7日，IOTA
开发人员部署了一个向后兼容的升级，通过将 Curl-P-27 替换为另一个哈希函数来消除漏洞[32]。为了进行升级，Bitfinex
暂停了其存取款业务，时间接近三天 [4]。所有直接持有 IOTA（不通过交易所）的用户都被鼓励升级他们的钱包和地址。
2017年9月7日，我们发布了漏洞报告[20]，描述了此攻击的原理。

在报告中，我们给出了有效碰撞和签名伪造的示例以及验证他们的软件。在此基础上，本文详细分析了破解 Curl-P-27
抗碰撞性的方法，并介绍了开发伪造签名的软件的流程。我们还研发了应对多签名方案的技术——选择消息攻击特别适用于多签名方案。我们没有向 IOTA
发送任何伪造签名或以任何方式攻击 IOTA。由于 Curl-P-27 不再用于 ISS，本文提出的签名伪造不适用于当前的 IOTA，同样不适用的还包括
5.2 节提到的的多重签名攻击。 Curl-P-27 仍然用于 IOTA 的其他部分[14]，但我们不会对他们进行攻击。

### 2 相关工作

在我们发布了初始报告之后，Colavita和Tanzer [10]分别复现了我们的分析，并验证了Curl-P
的round函数，即这个函数通过排列的方法，根据特定的表达式进行舍入。他们二人也参与了本论文的撰写。

1991年，Biham 和 Shamir
[3]首次发布了差分密码分析技术（IBM的研究人员在1974年发现了类似技术但没有对外公布[11]）。在本篇论文中，我们通过平衡三元加密哈希函数实现了差分密码分析的一个简单应用。除了我们的漏洞报告[10]以外，还有其他研究对基于三元的加密伪随机序列发生器进行了设计分析[16]，但是没有研究过此函数的差分密码。

通过对 Curl-P-27 的加密分析，我们对 ISS 的不可伪造性进行了选择消息攻击。或许我们还看不出降低碰撞抵抗性和建立攻击模型有多大的作用，但 MD5
哈希函数的研究过程可以给我们答案。王小云在 2004 年首次实现了 MD5 哈希算法的碰撞[35]，并在随后发布了生成随机碰撞的通用程序[34]。
2005年，Lenstra 与王小云合作将这个加密漏洞应用于X.509 认证中。X.509 支持 HTTPS
等协议，并且能够构建成对的碰撞证书[24]，是公钥基础设施的基石。有人认为证书颁发机构不会签署此类可疑证书，而且由于 X.509
认证缺乏“有意义的”结构，它很有可能被滥用。2007 年, Stevens 加入 Lenstra 等人，将 MD5
的原始随机碰撞攻击扩展到选择前缀碰撞攻击[30]。2009年，Stevens 等人宣布他们已经成功伪造了一个 X.509
证书，其拥有的证书权限能够通过所有主流浏览器的验证 [31] ，导致供应商立即废弃 MD5。

之后，IOTA 开发人员替换了 IOTA 签名方案中的哈希函数， Curl-P-27变成了基于 Keccak 的
Kerl。2017年10月，他们发现了一个名为13攻击（也叫 M
攻击）的无关漏洞[23]。对于哈希值在[-13，13]区间内的消息，数字13的签名（又记作“M”）显示明文是私钥的衍生物，并可以被用于伪造所有的后续消息块，由此造成漏洞。为解决此问题，IOTA
基金会要求用户必须更改消息，直到摘要中没有
13。另一种补救措施是，开发人员将可能受到损害的资金转移到其他地址，用户之后可以通过向基金会提出申请，并收回其资金[27]。

### 3背景

在本节中，为了读者能更好地了解这个攻击，让我们首先简要回顾一下 IOTA 的一些不常见的设计特性和术语。我们还会对 Curl-P 哈希函数和IOTA
签名方案（ISS）进行概述。

#### 3.1 IOTA设计

IOTA 有一些特别之处。首先，IOTA 使用平衡三进制而不是二进制；第二，IOTA 的付款被称为bundle；第三，IOTA 使用一种称为 tangle
的新数据结构而不是传统的块链；第四，IOTA 聘请一个称为协调员的可信方来检查状态并批准付款。

IOTA 的数据结构使用平衡三进制而不是二进制，其中用于计数的符码为{-1，0，1}，一个三进制字节由三位符码组成，每个字节代表了 [-13,13]
的整数。 IOTA经常将三进制字节序列化为字母A-Z和数字9。

IOTA 内的付款方式用一种叫做 bundle 的数据结构来表示。Bundle 由多个交易组成，但 IOTA
交易与其他加密货币交易不同，它们是负责存储输入或输出的缓存，除此之外还有地址，签名，价值和标记等字段。在第 5 节中对这个攻击进行描述时，我们也会详细描述
IOTA 的 bundle 和交易格式。

IOTA 是基于 tangle 的概念建立的[26]，其类似于DAG链，其中每个块可以引用多个块父[29]。然而，在 IOTA
中，没有块可以汇总多笔付款。相反，每个交易必须有一个 nonce 以用于 PoW，还需要含有指向其他两个交易的指针。为了将交易添加到 tangle
中，用户从 tangle
中选择两个小费以在其交易中引用。一旦创建并且得到签名，用户就会有足够的工作证明，并将交易（或bundle的情况下的交易）广播到IOTA网络。

在目前部署的IOTA中，bundle只能在获得协调员的批准之后才可以被接收。协调员是由IOTA开发人员运营的可信方，检查和批准tangle的状态，并对tangle签名。人们担心IOTA是集成的，或者受到IOTA开发人员的控制
[33]。
IOTA开发人员称IOTA不是集成的，协调员是一种临时措施，且IOTA没有公开其源代码。由于我们没有与IOTA沟通，我们无法确定协调员将如何影响我们发起的攻击，但是据我们所知，协调员没有机制可以防止本文提到的攻击。

#### 3.2 IOTA的签名方案（ISS）

受到Winternitz一次性签名（W-OTS）的启发，IOTA使用了类似的签名方案[25]。 W-OTS对Lamport签名进行了优化
[22]，同时操作多位，不惜计算成本来缩短公钥长度。

ISS与W-OTS有很多不同。首先，与传统的W-OTS一样，ISS操作的是消息的哈希值，而不是像
W-OTS那样直接在消息上进行操作。其次，ISS没有使用校验和，而是对消息的哈希值进行规范化。

ISS有三个安全级别。安全级别1仅签署消息的哈希值的三分之一，安全级别1签署前三分之二，安全级别3签署整个哈希值。因为我们的攻击是针对最高安全级别的，所以它也应当适用于其他所有安全级别。因此，当下文涉及到ISS时，我们将默认其使用了安全级别3。

#### 3.3 Curl-P

在本节中，我们将描述Curl-P哈希函数。 Curl-P（有时称为Curl）是一种加密哈希函数，被用于设计IOTA。
它的用途包括创建交易地址、消息摘要，工作证明（PoW）和基于哈希的签名。 在高层次上，Curl-P遵循海绵结构模式[2,18]，但在一些关键位置上有变化。
由于IOTA项目尚未提供任何官方规范说明或分析，我们对Curl-P的开源部分进行说明。

![](https://images.seebug.org/content/images/2019/08/13/1565690049000-fig1.PNG-w331s)

与大多数加密哈希函数不同，Curl-P使用的是平衡三进制。为表达清楚，我们用小写字母表示单个三进制符码，例如a; b; c; x; y; z,
再用大写字母表示连续的三进制符码，如S; N; X; Y。使用下标符号表示一个序列中的单个字符，例如Si。遵循IOTA惯例，Curl-P-R中的R表示轮次（例如，Curl-P-27表示27轮Curl-P）。

Curl-P运行过程如图一所示：（1）Curl-P的初始化状态S是一个长度为729的全零三进制序列。 （2）消息被分成消息块mb0 · · ·
mbn，每块长度为243。 Curl-P不使用消息填充，如果一条消息的长度不是243的倍数，允许最后一个消息块小于243。4（3）每个消息块mb0 · ·
· mbn依次被复制到状态S的前三分之一，并由函数f r进行转换。 （4）当没有消息块之后，Curl-P返回最终状态的前三分之一。有关更详细的描述，请参阅算法1。

![](https://images.seebug.org/content/images/2019/08/13/1565690050000-algorithm1.PNG-w331s)

现在来看负责转换状态S的函数fr 。转换函数fr 就是将f函数递归调用r次，例如f 3(S) = f (f (f (S)))。
Curl-P-27就是Curl-P哈希函数，其变换函数是f27。

调用一次fr 就能获得S的新状态。 如算法2中所述，初始状态中的每相邻两位符码通过简单函数g的转换，变成新状态中的一位数字。
当前状态中的每一位都会被使用两次，一次作为g的第一个参数（由a表示），一次作为g的第二个参数（由b表示）。 在表1中，我们给出g作为替换表（s-box）。

![](https://images.seebug.org/content/images/2019/08/13/1565690050000-algorithm2.png-w331s)

### 4 Curl-P的密码分析

在本节中，我们应用常见的差分密码分析法来构造完全碰撞。我们构造两条相同长度的消息，设置他们只有一个符码不同，而且他们通过 Curl-P-27
会映射到相同的值。我们可以控制碰撞消息的内容，包括任意消息前缀和后缀。在下一节中，我们将利用他们来伪造有效IOTA支付的签名。

除了IOTA开源项目发布的一部分源代码，我们无法找到 Curl-P 或 Curl-P-27 的正式规范文档。此外，IOTA开发人员表示，Curl-P-27
旨在对特定的输入组[5]进行碰撞。事实上，Curl-P-27 是非随机的。正如[10]中详细探讨的那样，可以在相同长度的消息中观察到 Curl-P-27
的非随机行为；碰撞和第二个预成像对于生成不同长度的消息是微不足道的。因此，为了确保我们真正破解了 Curl-P-27，我们表明我们的碰撞攻击破坏了
Curl-P-27 的安全属性（参见第5节）。

在高层次上，我们的攻击工作如下所示。我们选择两条长度至少为三个消息块的消息，并且他们只有一位符码不同。为了降低困难，我们使这两条消息满足某些约束方程（在第
4.2
节中详细说明）。一旦我们进入包含不同符码的消息块，我们就需要确保会发生碰撞。为此，我们在两个消息中随机翻转一组三进制数，并且每组不能超出其所在的消息块。我们的思路是对两条消息做变换处理，并且使不同的那一位在转换完成后处于结果状态的前三分之一的位置。

f 27(S)[243,729] = f27(S‘)[243,729]

因为Curl-P用下一个消息块替换了S的前三分之一，这导致原本的差异被覆盖，造成完全碰撞。我们利用Curl-P-27的不同特性多次强制转换函数，这样的话，在最后一轮时这些差异可能还保持在状态的前三分之一。经过多轮转换之后还保持着一位差异，找到这样的两条消息需要调用Curl-P-27次数的上限是760
万次或 22287次。

![](https://images.seebug.org/content/images/2019/08/13/1565690050000-fig2.PNG-w331s)

在图2中，我们可以看到在Curl-P-27中，不同的轮数会导致不同的结果。我们用颜色代表发生碰撞的可能性，x轴表示差异点的位置，y轴表示在该轮数内差异没有扩散。我们对每个位置和深度执行100个样本（总共11
243 100 = 267300个样本），每个样品随机初始化，差异点的内容设置也是随机的。更多数学分析请参阅[10]中的复现。

我们设置差异符码出现在第 17
位。根据实验结果，知道了轮次和差异点的位置，我们可以计算碰撞的概率。在此条件下递归20次后，碰撞的概率是1.0。因此，只要我们保证差异不会扩散，我们就可以制造碰撞。这种攻击应该同样适用于输入的消息块中的其他位置（如[10]所示）。请注意，这是确保发生碰撞的上限，因为递归次数少于20次时也可能发生碰撞。

#### 4.1 Curl-P变换函数f r的不同性质

在本节中，我们将展示如何找到目标状态，将差异保持至少20轮。这需要我们分析Curl-P变换函数f的不同性质。

差分密码分析涉及研究两组及两组以上的输入之间的差异传播模式。最常见的技术是寻找差异轨迹。差异轨迹是一组概率偏差，表示一组差异如何通过多轮加密函数传播到另一组差异。这里我们只使用特定的差异轨迹，即在转换函数f的重复应用下,两个状态S，S‘之间的某一位的差异。我们证明了
Curl-P 强烈偏向于保持一轮的单符码差异（即f的应用）。

首先介绍其中涉及的术语。由于Curl-P使用三进制符码∈{?1,0,1}，我们必须使用新的三元符号表示法。为了表示两个符码 x 和 x'
之间的差异，我们使用Θ ( 0Θ ?1 代表 x = 0 ，x’ = ?1 或者 x = ?1 ， x‘ =
0)。通过术语扩散，我们指出在调用f之后，两个状态之间的差异的数量已经增加（即，差异已被使用）。

我们的攻击是围绕着一个事实，即s-box g不会一直传播差异。例如，考虑g的两组输入和输出：g: a,b,c and a‘, b’, c‘ such
that g( a, b ) = c and g( a', b' ) = c'。我们做出以下观察：

1.对于所有可能的值，如果 a ≠ a' 且 b = b'，那么 c ≠ c' 。

2.如果a = a' 且 b ≠ b'，则可能有 c = c' 或 c≠c'（例如，a = a'= 1，b = 0且b' = 1，则c = c' = 0）。

每调用一次 f 就是更新一次状态。如3.3节所述，g
中每两位符码经过转换以后变成新状态中的一位符码。先前状态的每一位最多被转换两次：一次作为第一个变量a，一次作为第二个变量b。这意味着单位符码差异将延续到下一轮，因为当它是s-box
g的第一个变量a时，g的输出将与a不同（如图1所示）。因此，如果将f应用于两个状态S，S'，更新后的状态f（S），f（S'）将始终有一位或两位的不同，不会出现无符码差异。

我们模拟了状态在k轮Curl-P后保持单位符码差异的概率。 如图3所示，此马尔可夫模型列举出了所有可能的输入与其转换后的结果。 例如，如果当前的差异为
0Θ1，那么它有 1/9 的概率在下一轮中保持不变（即0 1），2/9 的概率变为 -1Θ0，或者有 6/9
的概率使差异个数从1增加到2（标记为失败状态，因为它未能保持单符码差异）。

![](https://images.seebug.org/content/images/2019/08/13/1565690050000-fig3.PNG-w331s)

![](https://images.seebug.org/content/images/2019/08/13/1565690050000-matrix.PNG-w331s)

顶行表示 0Θ1 的转换到各个结果的概率，第二行是 -1Θ0，第三行 -1Θ1，第四行是差异由一位变为两位。使用这个矩阵，我们计算了在调用 k 次 f
之后差异保持一位的概率的下界，因为我们没有计算差异位数超过 1 位之后再变回1位的情况，所以这是一个下限。

因此，从 0Θ1 开始，通过将矩阵提高到我们希望的轮数并计算概率。例如我们将矩阵幂 3 次，那么得到的矩阵中的数字就是符码在转换 3
次以后变成对应新符码的概率。因此，我们可以测量k轮后也不失败的概率。

之前，我们通过实验验证了，如果经过 20 轮
Curl-P-27（即调用20次f）转换仍保持单符码差异，那么碰撞的概率是1.0。使用我们的状态转移矩阵，我们计算20轮，我们的攻击有一个每个查询成功概率下限为
2-42。也就是说，我们需要尝试242次才有可能找到将差异保持到20轮以后的消息对，这样的消息对可以产生碰撞。在下一节中，我们将展示如何显着减少对
Curl-P-27 的必要查询次数。

4.2差分求解

在本节中，我们将展示如何通过选择具有特定属性的消息来减少 Curl-P-27 的查询次数。我们首先展示如何约束有一位差异符码的状态 S 和
S‘，使得他们需要至少9次递归才能保持一位的差异（即差异没有扩散）。为此，我们将f表示为方程组，并求解状态S和S’中的特定值。

我们可以将变换函数f r(S) 表示为一系列方程。例如，调用一次 f 可以写为

f (S)0 = g(S0,S364),f (S)1 = g(S364,S728),...,f (S)728 = g(S365,S0)

其中f
(S)0是调用f后获得的新状态的第0位的数字。由于每一轮只是f的递归应用，我们可以根据状态S的初始值在f轮后写出特定位的值。我们使用上标来表示轮次。例如，用

f 2(S)6 = g(g(S366,S1),g(S184,S548))

表示在位置6进行两次递归运算。

使用这种表示，我们找到可以使得 0Θ1 的差异保持9轮的方程。然后我们找到满足这些方程的消息前缀。
目前，我们可以在一秒之内查找到此消息前缀（有关我们的性能评估，请参见第 5.3 节）。
另外，给定一个特定的消息模板，我们只需要在两个消息块中更改一小组三进制位，便可以将其转换为令人满意的消息。

#### 4.3 寻找碰撞

攻击需要至少3个信息块：mba, mbb, 和
mbc。其中mbb含有一个差异符码。mba前面的消息块数量没有限制，mba和mbb之间也没有，mbc总是跟在mbb之后并且重写mbb在前三分之一制造的差异。mbc的取值不会对攻击造成影响，可以取任意值。

完整的攻击过程如下。首先，在我们攻击的约束阶段，我们通过调整mba和mbb来找到合适的消息前缀，这样它们可以保证 9 轮的单位符码差异。
接下来，在蛮力阶段，我们在mbb中的特定位置随机改变符码，目的是找到两个消息，使得从位置 17 开始的差异保持 20 轮。
由于约束阶段确保蛮力阶段的每次尝试在 9 轮中保持单符码差异不同，因此蛮力阶段的攻击复杂性从 20 轮减少到 11 轮。
结果，每个查询的成功率的下限减少到大约2 -22.87或 760 万分之一。

正如差分密码所分析的，我们的概率计算简化了假设，即输入值是均匀随机的。考虑到 Curl-P-27 的低扩散率和Curl-P
的非随机性，这种假设可能不会总是成立。 但是，如第 5.3 节所示，本节给出的界限与实际结果相当接近。

### 5 利用Curl-P中的碰撞来伪造签名

本节中，我们将使用Curl-P-27碰撞对IOTA签名方案（ISS）执行签名伪造攻击。结合上一节的内容，我们将展示如何创建两个有效的IOTA
bundle（即支付），这两个bundle最多只有两位不同，并且他们具有相同的Curl-P-27哈希值。然后，我们将描述攻击的设置，利用这些碰撞的
bundle 来伪造签名。最后，我们将展示如何攻击ISS多重签名。

#### 5.1 对ISS的选择消息攻击

我们的攻击是一种选择消息攻击，恶意用户 Eve
欺骗用户Alice，先是要求Alice签署b1，然后根据b1生成相应的b2，这个b2也能通过验证。具体过程如下：

  1. Alice生成密钥对（PK, SK）。

  2. Eve通过碰撞攻击产生两个bundle b1，b2，并使得 b1 ≠ b2 且 CurlHash（b1）= CurlHash（b2）。

  3. Eve将b1发送给Alice并要求Alice签名。Alice检查b1，确认它是安全的。

  4. Alice在夏娃上给b1签名，即Sign（SK, b1）→ σ。

  5. Eve产生一个bundle对（σ，b2），使得 b1≠b2，b2是一个有效的 bundle，就算 Alice从未见过b2，b2也能够通过Alice的公钥验证。

在4.3节中，我们介绍了攻击的一般格式，它至少需要三个消息块 mba，mbb和mbc。 为了执行攻击的第一阶段，我们将 mba 和 mbb
中的某些特性设置为特定值。 在暴力阶段，我们每次尝试更改 mbb 中的其他符码并检查我们是否已经实现了碰撞。 但是，bundle必须通过 IOTA
软件中的有效性检查才能被 IOTA 视作有效bundle，这限制了我们可以修改的位数。

![](https://images.seebug.org/content/images/2019/08/13/1565690050000-fig4.PNG-w331s)

要想计算 bundle
的哈希，需要对每个交易的地址，值，标记，时间戳，当前字节和最后字节的串联结果计算哈希值。交易的格式如图4所示。大多数字段的格式都有严格的规范格式。例如，bundle
中值的求和结果不能为负，时间戳必须在一定范围内，并且索引必须与 bundle 中的交易对齐。标签不会影响 bundle
的语义或有效性，并且可以包含任意的符码。因此，对于约束阶段和暴力阶段中的每次尝试，我们只更改 tag 中的符码。

另一个重要的问题是要在哪里生成碰撞。在最初的漏洞报告中，我们展示了两种不同攻击方式的碰撞 bundle：一种将碰撞置于地址范围内，使得 Alice
无意中签署了一项交易，该交易将取走 Eve 的资金，Eve 可以声明 Alice 犯了一个错误。第二次将两个碰撞放在一个 bundle 中的两个地方，导致
Alice 无意中签署了一个交易，该交易比预期更多地支付 Eve。在下一节中，我们将详细描述需要多个签名的 bundle
的后一种攻击方式，这些签名是我们选择的消息设置。

#### 5.2 多重签名攻击

我们在漏洞报告[20]中伪造的攻击是选择消息攻击，也就是说，Eve必须要求Alice签署bundle。为了证明保障被签署消息的安全性有多么重要，我们现在将攻击扩展到
IOTA
多重签名方案[28]。在多重签名中，只有在多方签名以后才可以支出资金。为了达到这个目的，一方创建一个bundle并要求另一方签名，这便是选择消息攻击。
IOTA基金会鼓励部署热存储/冷藏解决方案5，以达到使用多重签名来安全存储资金[12]的目的。多重签名迫使攻击者必须使多方妥协，这是它被使用在加密货币环境中的一个主要原因。我们的攻击恰好消除了多重签名的这种安全优势。我们将考虑一个2-of-2
的简单案例，其中两方都签署了花费资金。这个攻击还会推广到更复杂的设置。

考虑 Eve 和 Alice 各持一对 ISS 密钥：（PKE，
SKE）和（PKA，SKA），只有Eve的密钥签名和Alice的密钥签名同时存在才能取出资金。这意味着Eve和Alice之前已经进入了 2-of-2
的多重签名，并且现在正共同使用这笔资金。我们的攻击将做如下工作：Eve将计算两个相互碰撞的bundle，一个向Alice支付资金，另一个向Eve支付资金。
Eve将签署并发送bundle给Alice，这个bundle负责向Alice支付资金。一旦Eve拥有 Alice
的签名，她就会在创建一个Alice从未见过或未授权的有效bundle，并且广播这个bundle.6。在此设置中，Eve要么是恶意的，要么已被恶意方攻击。

![](https://images.seebug.org/content/images/2019/08/13/1565690050000-fig5.PNG-w331s)

为了构造这样的bundle，Eve将碰撞置于某个碰撞的某个value字段。图5显示了bundle的前四个消息块。突出显示的字段与攻击相关。通过在碰撞前后操纵标记字段中的特征，Eve导致第二交易（消息块3）中的value字段的第17位发生碰撞。这样，Eve可以在第二个交易中生成两个不同的bundle，这些值具有相同的哈希值。
Eve随后在第四个交易（消息块7）中生成了第二个碰撞，这次使两个bundle的值仍然总和为零。这用于设置向谁支付多少金额。

为了生成这些碰撞，一般需要我们按顺序进行两次攻击。在我们当前的碰撞工具中，我们在两个交易之间还需要一个交易。满足了这个要求，以及冲突不在第一个或最后一个交易中的要求，我们就可以处理具有不同数量的交易的bundle。我们的工具只能在消息块的第17位中产生碰撞，不过这是工具的限制，而不是因为第
4 节中的密码分析有误。我们的工具在生成碰撞时不依赖于交易中特定的地址和值，但是必须保证对应位的符码不同才能产生有效的bundle。例如，如果在 b1 中
Alice 和 Eve 的输出值的 17 位为零，那么在b2中将Eve的输出值的17位变为1会导致b2的总和不为0。在 b1 中，Alice 的输出值的第
17 位应为1，Eve的应为零。

在附录B中，我们展示了使用此技术创建的两个示例bundle。其中bundle为支出500,000,000
IOTA货币，由Alice和Eve控制。Alice丽丝签了一个bundle，它支付Eve 1
IOTA，其余的支付给其他地址。在碰撞的bundle中，Eve收到 129,140,164 IOTA货币，支出地址为Alice的地址。

碰撞单签名bundle的生成方式与此类似。我们在漏洞报告中伪造了bundle的签名，其向三个地址进行支付。在良性bundle
b1中，Alice在她控制的两个地址收到 50,000 和 810,021,667 IOTA 货币并向Eve支付100 IOTA货币。在恶意bundle
b2 中， Eve进行了调整并且收到了 129,140,263
IOTA货币，这些是Alice的钱。我们还没有研究在value和address字段之外制造碰撞会带来哪些影响，可能会生成其他攻击。

#### 5.3 性能分析

我们在 64 位Linux 4.9.74 环境下，使用一台配备了 8 个 2.4GHz 10 核 Intel 芯片和 256 GB RAM 的 Intel
机器运行此攻击。 我们的攻击占用了全部的 CPU，但占用的 RAM 空间可以忽略不计。 如第 4.3
节所述，碰撞包括两个阶段：约束阶段计算约束集，而暴力阶段在 tag 中产生随机数以产生碰撞。

约束阶段生成并求解十八个等式，前九轮 Curl-P-27 中的每一个都有两个。 约束阶段在 Python 中实现，并且是单核运行。
我们没有尝试优化第一阶段。 表2 显示了取第 17 位不同并且在第一阶段运行 5000 次后所需要的平均，最小和最大时间。

![](https://images.seebug.org/content/images/2019/08/13/1565690050000-table2.PNG-w331s)

表2 还显示了强力阶段的测试结果。该阶段使用第一阶段的符码和模板来强制生成碰撞。因为这在 Go 中执行并且并行，因此我们需要使用服务器的所有 80 个核。
使用第一阶段的输出生成碰撞平均只需7.2秒。 一次碰撞平均需要测试 520 万次，最小和最大尝试次数分别超过 5000 次 1279 和 53M。
这证实了我们在4.3节中的分析。

为了实现第 5.2 节中描述的多重攻击，我们必须顺序地运行约束和强制阶段，以生成两次碰撞。 我们的碰撞工具平均 15.2
秒就可以生成两个多重签名的bundle。 表2 显示了各阶段运行5000次所对应的平均时间以及最小和最大时间。

### 6 讨论

IOTA开发人员对漏洞的产生原因及其影响有过多次声明，我们对其进行了总结，并对部分问题作出了回应。

IOTA开发人员认为我们的攻击模型与IOTA网络环境没有联系：具体来说就是，我们无法设置被签署过的消息，因为“在IOTA中，攻击者不会选择签名过的消息“[5]。为了应对这个问题，我们将攻击扩展到多重签名地址，因为多重签名协议明确允许一个用户选择另一个用户签名的消息。

IOTA的开发人员还认为，”即使是大多数有效的攻击“都会在IOTA网络中失败，因为在闭源协调员中存在”保护机制”
[5,13]。漏洞报告和本文中提出的攻击只单纯考虑如何应对IOTA签名方案，未在完整的IOTA系统的环境中分析这些攻击。

此外，他们声称 Curl-P-27 可以接受碰撞输入是他们有意为之，其目的是防止克隆欺诈。其原话是：“IOTA 团队故意引入 Curl-P
哈希函数，以此预防[克隆欺诈]，这还使得克隆欺诈无法用于 DLT 协议，同时保证了整个 IOTA 协议和网络的安全。”他们认为
“协调员会保护IOTA网络，不受故意引入的影响，并且称之为“复制保护机制”[13]。这么看来，我们除了发现一个新型攻击，似乎还发现了一个故意放置的后门。

### 7 结论

本文介绍了如何通过伪造消息签名来攻击IOTA签名方案。我们在两条消息只有一位字符不同的情况下构造了全状态碰撞。并且运用这个方法创建了两个有效的IOTA
bundle，这样，就算两个bundle互不相同也仍然会映射到相同的值，也就是同一个签名将适用于两个bundle。
作为示例，我们在bundle中设置了不同的符码，攻击者可以在几十秒内使用简单的设备生成符合要求的bundle。

### 8 致谢

在此我们对 Andy Sellars, Weijia Gu, Rachael Walker, Joi Ito, Vincenzo Iozzo, Sharon
Goldberg, and Ward Heilman 致以感谢，感谢你们对此论文的指导与建议。

### 9 References

[1] Mihir Bellare and Phillip Rogaway. “The exact security of digital
signaturesHow to sign with RSA and Rabin”. In: International Conference on the
Theory and Applications of Cryptographic Techniques. Springer. 1996, pp. 399–
416.  
[2] Guido Bertoni et al. “On the indiﬀerentiability of the sponge
construction”. In: Lecture Notes in Computer Science 4965 (2008), pp. 181–197.  
[3] Eli Biham and Adi Shamir. “Diﬀerential cryptanalysis of DES-like
cryptosystems”. In: Journal of CRYPTOLOGY 4.1 (1991), pp. 3–72.  
[4] Bitﬁnex. IOTA Protocol Upgrade August 08, 2017.
<https://www.bitfinex.com/posts/215>, archived at
<https://web.archive.org/web/20180722235151/>
<https://www.bitfinex.com/posts/215>.  
[5] Tangle blog. Full Emails of Ethan Heilman and the Digital Currency
Initiative with the IOTA Team Leaked.
<http://www.tangleblog.com/wpcontent/uploads/2018/02/letters.pdf>, archived at
<https://web.
archive.org/web/20180228182122/http://www.tangleblog.com/wpcontent/uploads/2018/02/letters.pdf,
https://archive.is/6imWR>.  
[6] Bosch. Press release: Robert Bosch Venture Capital makes ﬁrst investment
in distributed ledger technology. <https://www.bosch-presse.de/pressportal/de/en/robert-bosch-venture-capital-makesfirst-investment-in-distributed-ledger-technology-137411.html>, archived at
<https://web.archive.org/web/20180724022550/> <https://www.bosch-presse.de/pressportal/de/en/robert-boschventure-capital-makes-first-investment-in-distributed-ledgertechnology-137411.html>.  
[7] Crypt Brieﬁng. First VW IOTA Product Will Be Released Early Next Year.
<https://cryptobriefing.com/vw-iota-product-released/>, archived at
<https://web.archive.org/web/20180724021409/https: //cryptobriefing.com/vw-iota-product-released/>.  
[8] Coindesk. City of Taipei Conﬁrms It’s Testing IOTA Tech for ID.
<https://www.coindesk.com/city-of-taipei-confirms-its-testing-iotablockchain-for-id/>.  
[9] CoinmarketCap. CoinmarketCap IOTA July 23 2018. <https://coinmarketcap>.
com/currencies/iota/, archived at [https://web.archive.org/web/
20180724020019/](https://coinmarketcap "https://web.archive.org/web/
20180724020019/")<https://coinmarketcap.com/currencies/iota/>.  
[10] Michael Colavita and Garrett Tanzer. “A Cryptanalysis of IOTA’s Curl Hash
Function”. In: (2018).  
[11] Don Coppersmith. “The Data Encryption Standard (DES) and its strength
against attacks”. In: IBM journal of research and development 38.3 (1994), pp.
243–250.  
[12] IOTA Foundation. IOTA Guide – Generating Secure Multisig Addresses (hot
and coldwallet). <https://domschiener.gitbooks.io/iota-guide/content/exchange-guidelines/generating-multisignature-addresses.html>, archived at
<https://archive.is/087kP>.  
[13] IOTA Foundation. Oﬃcial IOTA Foundation Response to the Digital Currency
Initiative at the MIT Media LabPart 4 / 4. <https://blog.iota.org/official-iota-foundation-response-to-the-digitalcurrency-initiative-at-the-mit-media-lab-part-4-11fdccc9eb6d>, archived at
[http://web.archive.org/web/20180727155405/](http://web.archive.org/web/2018072
"http://web.archive.org/web/20180727155405/")<https://blog.iota.org/official-iota-foundation-response-to-thedigital-currency-initiative-at-the-mit-media-lab-part-411fdccc9eb6d?gi=4be3ca82ed48>.  
[14] IOTAledger (github). IOTA Kerl speciﬁcation.
<https://github.com/iotaledger/kerl/blob/master/IOTA-Kerl-spec.md>, archived
at <https://web.archive.org/web/20180617175320/>  
<https://github.com/iotaledger/kerl/blob/master/IOTA-Kerl-spec.md>. 2017.  
[15] Oded Goldreich. Foundations of Cryptography: Basic Applications. Vol. 2.
New York, NY, USA: Cambridge University Press, 2004.  
[16] Guang Gong and Shaoquan Jiang. “The editing generator and its
cryptanalysis”. In: International Journal of Wireless and Mobile Computing 1.1
(2005), pp. 46–52.  
[17] Leon Groot Bruinderink and Andreas Hu¨lsing. ““Oops, I Did It Again” –
Security of One-Time Signatures Under Two-Message Attacks”. In: Selected Areas
in Cryptography – SAC 2017. 2018, pp. 299–322.  
[18] Bertoni Guido et al. Cryptographic sponge functions. 2011.  
[19] Paul Handy. Merged Kerl Implementation. <https://github.com/iotaledger/>
iri/commit/539e413352a77b1db2042f46887e41d558f575e5, archived at
<https://archive.is/jCisX>.  
[20] Ethan Heilman et al. IOTA Vulnerability Report: Cryptanalysis of the Curl
Hash Function Enabling Practical Signature Forgery Attacks on the IOTA
Cryptocurrency.  
[21] Jonathan Katz and Yehuda Lindell. Introduction to Modern Cryptography.
Second Edition. CRC Press, 2014.  
[22] Leslie Lamport. Constructing digital signatures from a one-way function.
Tech. rep. Technical Report CSL-98, SRI International Palo Alto, 1979.  
[23] Willem Pinckaers (Lekkertech). IOTA Signatures, Private Keys and Address
Reuse? <http://blog.lekkertech.net/blog/2018/03/07/iotasignatures/>, archived
at <https://archive.is/CnydQ>. 2018.  
[24] Arjen K. Lenstra, Xiaoyun Wang, and Benne de Weger. Colliding X.509
Certiﬁcates. Cryptology ePrint Archive, Report 2005/067. <https://eprint.
iacr.org/2005/067>. 2005.  
[25] Ralph C Merkle. “A certiﬁed digital signature”. In: Conference on the
Theory and Application of Cryptology. Springer. 1989, pp. 218–238.  
[26] Serguei Popov. “The tangle”. In: cit. on (2016), p. 131.  
[27] Ralf Rottmann. IOTA Reclaim Identiﬁcation Veriﬁcation Process.
<https://blog.iota.org/iota-reclaim-identification-verificationprocess-e316647e06e6>, archived at <https://web.archive.org/web/
20180710000243/https://blog.iota.org/iota-reclaim-identificationverification-process-e316647e06e6?gi=b8190e111e7f>.  
[28] Dominik Schiener. IOTA Multi-Signature Scheme. https://github.com/
iotaledger/wiki/blob/master/multisigs.mdIOTA Multi-Signature Scheme. 2017
(accessed February 3, 2018).  
[29] Yonatan Sompolinsky and Aviv Zohar. “Secure high-rate transaction
processing in bitcoin”. In: International Conference on Financial Cryptography
and Data Security. Springer. 2015, pp. 507–527.  
[30] Marc Stevens, Arjen Lenstra, and Benne de Weger. “Chosen-Preﬁx Collisions
for MD5 and Colliding X. 509 Certiﬁcates for Diﬀerent Identities”. In:
Advances in Cryptology – EUROCRYPT 2007. Springer. 2007, pp. 1–22.  
[31] Marc Stevens et al. “Short Chosen-Preﬁx Collisions for MD5 and the
Creation of a Rogue CA Certiﬁcate”. In: Advances in Cryptology – CRYPTO 2009.
Springer, 2009, pp. 55–69.  
[32] David Snsteb. Upgrades & Updates.
<https://blog.iota.org/upgradesupdates-d12145e381eb>, archived at
<https://web.archive.org/web/ 20180722232608/>  
<https://blog.iota.org/upgrades-updates-d12145e381eb?gi=51123f82db22>.  
[33] Eric Wall. IOTA is centralized. <https://medium.com/@ercwl/iotais-centralized-6289246e7b4d>, archived at
<https://web.archive.org/web/20180616231657/https://medium.com/@ercwl/iota-iscentralized-6289246e7b4d>. 2017.  
[34] Xiaoyun Wang and Hongbo Yu. “How to Break MD5 and Other Hash Functions”.
In: Advances in Cryptology – EUROCRYPT 2005. Springer. 2005, pp. 19–35.  
[35] Xiaoyun Wang et al. Collisions for Hash Functions MD4, MD5, HAVAL128 and
RIPEMD. Cryptology ePrint Archive, Report 2004/199.
<https://eprint.iacr.org/2004/199.2004>.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1015/>


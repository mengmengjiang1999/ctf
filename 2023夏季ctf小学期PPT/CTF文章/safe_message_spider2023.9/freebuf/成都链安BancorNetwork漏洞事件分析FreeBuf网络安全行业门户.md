**一、事件简述**

2020-06-18(文中所提及时间均为UTC时间)，以太坊上的智能合约BancorNetwork被爆出存在严重漏洞。该漏洞由BancorNetwork团队和白帽最先发现，并第一时间对存在被盗风险的资金进行了转移，涉及资金50W余美元。

此次事件中，存在漏洞的合约地址主要有如下三个：

0x923cab01e6a4639664aa64b76396eec0ea7d3a5f

0x8dfeb86c7c962577ded19ab2050ac78654fea9f7

0x5f58058c0ec971492166763c8c22632***3f667f

2020-06-18 3:06:48，BancorNetwork团队利用此漏洞对存在被盗风险的用户资金进行转移，截至2020-06-18
6:56，BancorNetwork团队共计转移资金约合$409,656。

另外两个公开邮箱信息的地址:

0x052ede4c2a04670be329db369c4563283391a3ea

0x1ad1099487b11879e6116ca1ceee486d1efa7b00

也于同一时间利用此漏洞对用户资金进行转移，分别转出资金$131,889和$2346。

到目前为止（2020-06-19）：

EtherScan已经将存在此漏洞的合约进行标注，如下图所示

![202006281311343039.png](http://topapi.atopchain.com/upload/img/20200628/202006281311343039.png)

图一

BancorNetwork团队也已对此次事件做出了回应，

![202006281311527953.png](http://topapi.atopchain.com/upload/img/20200628/202006281311527953.png)

详情见

（[https://blog.bancor.network/bancors-response-to-today-s-smart-contract-vulnerability-dc888c589fe4](https://blog.bancor.network/bancors-response-to-today-s-smart-contract-vulnerability-dc888c589fe4)），

并于UTC时间2020-06-17 21:35:53部署了新的BancorNetwork合约，合约地址为

0x2f9ec37d6ccfff1cab21733bdadede11c823ccb0

 **二、原理分析**

漏洞爆出后，成都链安安全团队第一时间对本次事件进行跟踪分析，根据链上分析结果发现，此次事件中漏洞产生的主要原因是智能合约BancorNetwork存在一个调用权限为public的函数safeTransferFrom，通过调用此函数，可以将用户授权给智能合约BancorNetwork的资金转出到任意地址。

由源码可以知，该函数为一个public函数，详细代码如下图所示：

![202006281312335510.png](http://topapi.atopchain.com/upload/img/20200628/202006281312335510.png)

图二

safeTransferFrom函数内部调用了execute函数。而execute函数的功能是调用safeTransferFrom参数中的_token代币智能合约的transferFrom函数进行代理转账。execute函数源码如下图所示：

![202006281312514991.png](http://topapi.atopchain.com/upload/img/20200628/202006281312514991.png)

图三

我们通过一笔链上交易可以清晰的看到调用此函数的具体作用。如地址“0xc802”发起一笔交易，调用了智能合约“0x5f58”（也就是BancorNetwork）的safeTransferFrom函数，使地址”0x8a39”中的0.000000000000000003代币MFG发送到”0x2955”（图中的“Bancor：WhiteHatS...），具体如下图所示：

![202006281313088068.png](http://topapi.atopchain.com/upload/img/20200628/202006281313088068.png)

图四

以上就是本次事件漏洞的原理分析，该漏洞的原理十分简单，是因为函数的调用权限设置错误，将本应该只有合约本身调用的函数，设置成了任何人都可以调用。而当BancorNetwork拥有用户的授权额度时，任何人都可以通过调用safeTransferFrom函数，以BancorNetwork的身份对用户的资金进行代理转账。

针对该漏洞，有两点值得我们进行深入分析：

1\. 为什么BancorNetwork合约的safeTransferFrom函数会将权限设置成public。

2\. BancorNetwork合约的主要功能是代币转换，并非一个钱包，为什么用户会有未使用的授权。

对于第一个问题，我们追踪了safeTransferFrom函数的调用情况，发现safeTransferFrom函数只在handleSourceToken函数中被调用，用于将用户的代币转移到本合约中。handleSourceToken函数源码如下图所示：

![202006281313250444.png](http://topapi.atopchain.com/upload/img/20200628/202006281313250444.png)

图五

既然只是在handleSourceToken函数中调用，那么显然是没有必要设置成public权限，且根据业务来看，BancorNetwork的主要作用是用于代币交换，并不需要用户主动调用safeTransferFrom，也就没有必要将safetransferFrom设置为public权限。于是我们对比了合约中其他的几个函数，这几个函数均被设置成了public权限。如下图所示：

![202006281313409098.png](http://topapi.atopchain.com/upload/img/20200628/202006281313409098.png)

图六

由此，针对第一个问题，我们推测将这些函数设置为public权限可能是因为合约开发人员的疏忽。而目前来看（2020-06-19），BancorNetwork团队新部署的合约也验证了这个推测。根据链上代码显示，官方部署的新合约已经将相关函数权限全部进行了更改（虽然其他的函数与此事件无关）。具体代码如下图所示：

![202006281313560444.png](http://topapi.atopchain.com/upload/img/20200628/202006281313560444.png)

图七

针对第二个问题，我们跟踪了漏洞爆出后被转移资金的地址，发现这些地址在对BancorNetwork授权额度时，往往超过了所需要兑换代币的数量，且在兑换完成后，并没有收回额度。如下图所示：

![202006281314118572.png](http://topapi.atopchain.com/upload/img/20200628/202006281314118572.png)

图八

“0x624f”开头的地址对BancorNetwork合约授权了900000000000000个ONG代币，此额度已经超过了ONG的发行量，相当于将“0x624f”所拥有的ONG代币全部授权给BancorNetwork合约。而跟踪“0x624f”开头地址的交易我们发现，在进行完代币兑换后，未使用完所有授权额度，但并未将授权额度收回。

综上所述，我们推测可能是用户考虑到要随时使用，为了方便，一次性将所有代币都授权给了BancorNetwork合约。也可能是BancorNetwork的前端对授权金额设定了默认值。但这种行为存在巨大的风险，一旦智能合约爆发漏洞，资金极易被攻击者窃取。而在对后续新的BancorNetwork合约进行分析时发现，BancorNetwork团队和用户似乎也意识到了此问题存在的巨大风险，并做出了相应的安全防护。如下图九、十为用户对新合约的授权情况，对比两笔线上交易不难看出，两次授权的时间间隔很短，当用户成功兑换完代币后，剩余授权即被收回。

![202006281314387720.png](http://topapi.atopchain.com/upload/img/20200628/202006281314387720.png)

图九

![202006281314572279.png](http://topapi.atopchain.com/upload/img/20200628/202006281314572279.png)

图十

 **三、结语**

BancorNetwork本次爆出的漏洞，是一个较为简单的漏洞，此类漏洞在代码审计过程中十分容易被发现，但此次漏洞的影响却很大，上线仅两天，涉及的资金就已经超过50w美元。幸而BancorNetwork团队及时发现并修复了漏洞，否则后果不堪设想。成都链安-安全研究团队在此提醒各大智能合约运营商，因区块链合约部署后不可更改的特性，对比传统软件，上线前做好充分的代码审计十分重要，此次事件虽未造成太大的经济损失，但势必会让用户对BancorNetwork团队产品的安全性产生质疑。另外也提醒广大用户和运营商，在授权资金给第三方合约时，都应保持谨慎，切不可盲目相信“大公司”，对任何合约的授权都应当秉承最小原则，不要使自己的资金安全掌握在他人手中。

  


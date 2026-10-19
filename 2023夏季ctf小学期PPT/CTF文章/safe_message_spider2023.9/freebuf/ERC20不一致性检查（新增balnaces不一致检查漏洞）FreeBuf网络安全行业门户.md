***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **一、前言**

 **日前，有相关文章报道了部分合约中的transferFrom中存在不一致性检查漏洞(check effect inconsistency)。**

 **BUGX.IO团队对此漏洞类型进行了深入的分析，发现了不仅存在 `allowed[_from][msg.sender]` 这一语句的检查不一致，还存在
`balances[msg.sender]` 语句的检查不一致漏洞。**

##  **二、漏洞原理**

###  **1、allowed不一致性检查漏洞**

![1.png](https://image.3001.net/images/20180724/15324023479248.png!small)

如上面代码所示：

    
    
    `require(_value <= allowed[_from][msg.sender]);`

这一句的条件检测与

    
    
    `allowed[_from][_to] -= _value;`

这一语句的操作不相符，导致设置转账额度权限后，攻击者能够持续转账，直到转完所有余额。

###  **2、balances 不一致性检查漏洞**

![2.jpg](https://image.3001.net/images/20180724/15324023978837.jpg!small)

如上面代码所示：

    
    
    `require(balances[msg.sender] >= _value);`

这一句的条件检测与

    
    
    `balances[_from] -= _value;`

这一语句的操作不相符，攻击者能够通过溢出，让`_from`账户余额获得极大的token 数量。  

同时，有一些合约中使用了 safeMath 安全方法进行计算 `balances[_from] =
balances[_from].sub(_value);`，所以暂时没有溢出问题，但是条件检查部分是冗余的。

##  **三、漏洞复现**

###  **1、allowed 不一致性检查漏洞复现**

部署 Lightcoin 合约，合约地址：

<https://etherscan.io//address/0xd97579Cea3fE2473682a4C42648134BB982433B9>

管理者：0xca35b7d915458ef540ade6068dfe2f44e8fa733c

攻击者：0x14723a09acff6d2a60dcdf7aa4aff308fddc160

攻击者2：0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db

管理者身份：管理者给予攻击者一定的转账额度权限

    
    
    approve:
    "0x14723a09acff6d2a60dcdf7aa4aff308fddc160c",10000
    

使用 allowance 查看转账额度：  

    
    
    "0xca35b7d915458ef540ade6068dfe2f44e8fa733c","0x14723a09acff6d2a60dcdf7aa4aff308fddc160c" 

**![图片4.png](https://image.3001.net/images/20180724/15324025993893.png!small)**

此时此时攻击者2的余额为 0：

![图片5.png](https://image.3001.net/images/20180724/15324026777500.png!small)

切换为攻击者身份：

攻击者使用 transferFrom 向攻击者2进行转账操作

    
    
    transferFrom：
    "0xca35b7d915458ef540ade6068dfe2f44e8fa733c","0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db",10000

攻击者继续使用 transferFrom 向攻击者2进行转账操作，仍然能转账成功，因为
`allowed[_from][msg.sender]`没有发生变化，而攻击者2的余额依然增加了。

    
    
    transferFrom：
    "0xca35b7d915458ef540ade6068dfe2f44e8fa733c","0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db",10000 

**![图片6.png](https://image.3001.net/images/20180724/15324028024091.png!small)**

通过此攻击，攻击者能够将 _from 账户里的所有余额转移到其它用户余额中。并且`allowed[_from][_to]`是溢出了的。

    
    
    allowance :
    "0xca35b7d915458ef540ade6068dfe2f44e8fa733c","0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db"

###
![图片7.png](https://image.3001.net/images/20180724/15324028611524.png!small)
**2、balances 不一致性检查漏洞复现**

部署 CountryCoin (CCN) 合约进行复现。

合约地址：<https://etherscan.io//address/0x3b912fb1b5b9e07e50e43f0404fee038f9a0353c#code>

管理者：0xca35b7d915458ef540ade6068dfe2f44e8fa733c

攻击者1：0x14723a09acff6d2a60dcdf7aa4aff308fddc160

攻击者2：0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db

攻击者1先通过充值获取一定的 token。

![图片8.png](https://image.3001.net/images/20180724/15324029108605.png!small)

至此即为初始化条件，攻击者有两个账户地址，其中余额分别为 10000 和 0，我们接下来的攻击就是让第二个账户溢出。

切换到攻击者2，攻击者2给予攻击者1一定的转账额度权限

    
    
    approve:
    "0x14723a09acff6d2a60dcdf7aa4aff308fddc160c",10000

切换回攻击者1，攻击者使用 transferFrom 向自己进行转账操作

    
    
    transferFrom：
    "0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db","0x14723a09acff6d2a60dcdf7aa4aff308fddc160c",10000

此时攻击者2地址上余额本来为0，但经过 `` 的减法计算下溢变为了极大值。

![图片9.png](https://image.3001.net/images/20180724/15324029428286.png!small)

## **四、修复方案**

修复方法如下：

![微信图片_20180724114153.png](https://image.3001.net/images/20180724/15324037325278.png!small)

1.使用 safeMath 方法进行计算；

2.使用 `balances[_from] >= _value` 作为条件判断而非 `balances[msg.sender]`；

3.检查 `allowed[_from][msg.sender]` 并对 `allowed[_from][msg.sender]` 进行操作不要与
`allowed[_from][_to]` 混用。

 ****

## ****五、** 漏洞合约监测结果**

通过对以太坊进行此漏洞类型的全面监测，发现存在超过 25 个合约存在此类问题，其中有些是有大量交易的合约。同时，有部分合约使用了 safeMath
库暂无问题。

##  **六、资料**

ERC20代币合约新型漏洞预警及分析，可导致无限授权转账：

[https://mp.weixin.qq.com/s?__biz=MzIwMDk1MjMyMg==∣=2247484278&idx=1&sn=3445efaa758884071885012347219d0c&chksm=96f41c1ba183950d5c0b51d5b668ca35ddec4b22fc47dc17e9f79bd0c17e1fe415e787576685&mpshare=1&scene=1&srcid=0718RlJQHpsBoUXge9GsOJYL#rd](https://mp.weixin.qq.com/s?__biz=MzIwMDk1MjMyMg==&mid=2247484278&idx=1&sn=3445efaa758884071885012347219d0c&chksm=96f41c1ba183950d5c0b51d5b668ca35ddec4b22fc47dc17e9f79bd0c17e1fe415e787576685&mpshare=1&scene=1&srcid=0718RlJQHpsBoUXge9GsOJYL#rd)  

LightCoin合约非一致性检查漏洞分析：

<http://www.freebuf.com/vuls/177565.html>

##  **七、公司介绍**  

BUGX.IO是一家致力于区块链领域的安全公司。核心团队组建于2014年，我们在区块链生态安全、行业解决方案、安全建设、红蓝对抗等方面有深厚积累与过硬专业素养。

 ***本文作者BUGX.IO-Tri0nes，转载请注明来自FreeBuf.COM**


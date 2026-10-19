## 概述

近期，奇安信病毒响应中心在日常跟踪黑产团伙过程中，发现了一个针对在东南亚从事博·彩、狗推相关人员以及海外华人群体的黑客团伙，其业务范围涵盖远控、挖矿、DDOS和流量相关。样本主要在Telegram群组中进行传播，样本免杀效果好，有些诱饵针对性强，且极具诱惑性。

目前已经检测到海外用户大量中招，国内少量中招，鉴于其危害较大， **奇安信病毒响应中心** 对其进行了分析溯源，并结合相关线索，披露了该黑客团伙。

由于该团伙针对博·彩行业，且与我们此前追踪的零零 **狗** 组织有着相似的目标且目的为敛 **金** ，诱饵名恶俗不堪似，不可入 **眼**
，因此我们将该黑客组织取名为金眼狗，英文名GoldenEyeDog。

## 样本分析

十月底，我们捕获到了一个名为《海尔置业福建项目停车场垮塌，造成8死2伤》的测试样本，该初始样本主要功能为下载者，pdb路径：

![图片.png](https://image.3001.net/images/20191209/1575875749_5dedf4a5ae0f6.png!small)  

从该团伙的测试的域名中（test.hhlywsc.cn/q.sct）下载SCT文件并执行，q.sct内容如下：

![图片.png](https://image.3001.net/images/20191209/1575875759_5dedf4af0731a.png!small)  

从远程服务器下载New.jpg保存在C:\ProgramData目录下并打开，用来迷惑用户：

![图片.png](https://image.3001.net/images/20191209/1575875769_5dedf4b920efe.png!small)  

从远程服务器下载Junction.exe，保存在C:\ProgramData目录下，该文件带有百度签名的白文件，为2016年百度输入法相关组件：

![图片.png](https://image.3001.net/images/20191209/1575875775_5dedf4bfcfcfc.png!small)  

从远程服务器下载basicnetutils.dll保存在C:\ProgramData目录下，该文件同样为百度输入法的相关组件，在Junction.exe运行时会被加载，其相关导出函数被修改。

![图片.png](https://image.3001.net/images/20191209/1575875799_5dedf4d781b20.png!small)  

其中有个导出函数作为loader，会解密从远程服务器下载的q.crt，在本地被改名为activeds.crt，内容如下：

![图片.png](https://image.3001.net/images/20191209/1575875805_5dedf4dd94832.png!small)  

获取当前执行目录路径并与“\\\activeds.crt”进行拼接，打开文件：

![图片.png](https://image.3001.net/images/20191209/1575875813_5dedf4e58a0d8.png!small)

  

读取文件数据到新分配的内存中：

![图片.png](https://image.3001.net/images/20191209/1575875825_5dedf4f1b893a.png!small)

  

解密出一个Dll，PDB路径：

![图片.png](https://image.3001.net/images/20191209/1575875874_5dedf522d02e6.png!small)

通过反射式DLL注入，内存加载dll并调用dll中的导出函数，并进行内存加载。

![图片.png](https://image.3001.net/images/20191209/1575875902_5dedf53e5b67f.png!small)  

SCT脚本最后执行Junction.exe，通过上述这种DLL-SideLoading技术，免杀效果很好：

![图片.png](https://image.3001.net/images/20191209/1575875913_5dedf54984e94.png!small)  

创建两个线程连接远程服务器

![图片.png](https://image.3001.net/images/20191209/1575875919_5dedf54f8a87c.png!small)  

连接的C2：

103.233.8.24:5768

223.199.1.113:5767

从代码中的一些函数名来看，其有些功能还处于测试阶段：

![图片.png](https://image.3001.net/images/20191209/1575875926_5dedf5569096c.png!small)  

后期我们通过对正式投递的样本进行分析我们发现，核心功能实际上是魔改版的大灰狼远控。攻击者出现的相关文件，表格整理如下：

![图片.png](https://image.3001.net/images/20191209/1575875969_5dedf581a7ed2.png!small)  

执行流程如下：

![图片.png](https://image.3001.net/images/20191209/1575876005_5dedf5a519c2d.png!small)  

# 关联分析

通过代码特征关联，我们发现该团伙2019年三月份开始使用这种手法进行攻击，利用的白样本各种各样，整理后的表格如下：

![图片.png](https://image.3001.net/images/20191209/1575876023_5dedf5b7184de.png!small)  

且投放时这些payload大部分都在该团伙注册的七牛云服务器上：

![图片.png](https://image.3001.net/images/20191209/1575876096_5dedf600335f0.png!small)  

关联到四个域名：

![图片.png](https://image.3001.net/images/20191209/1575876123_5dedf61b3b52f.png!small)  

通过关联test.microsft-update.com的子域名可以得到一批2017-2018年的老样本，可以看到在这两年的时间里该团伙的水平还仅限于对大灰狼源码的修改阶段，免杀效果很差。

PDB：

![图片.png](https://image.3001.net/images/20191209/1575876151_5dedf6374b8e0.png!small)  

  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  

其释放的DLL有两个模块。

第一个模块为远控：

![图片.png](https://image.3001.net/images/20191209/1575876191_5dedf65f40c84.png!small)  

第二个模块是挖矿程序，XMRig 2.4.3版本：

![图片.png](https://image.3001.net/images/20191209/1575876198_5dedf666488ef.png!small)  

我们通过研究该团伙成员注册的域名，大致了解了团伙成员的一些习惯，注册的域名大部分为字母加数字，且喜欢注册Test子域名用来测试样本。以[www.bestriven123.com](http://www.bestriven123.com)为例，bestriven一词源于《英雄联盟》游戏，意为“最强锐雯”，该词被广大英雄联盟玩家作为ID使用，该团伙成员应该为游戏玩家。

![图片.png](https://image.3001.net/images/20191209/1575876206_5dedf66e6ebc9.png!small)  

我们再研究sudaqiang123.com，sudaqiang拼音转成汉字为苏大强，《都挺好》电视剧的男主角，该域名注册时间为4月份：

![图片.png](https://image.3001.net/images/20191209/1575876212_5dedf674d8da0.png!small)  

而电视剧上映时间为3月份，可以大致推测该团伙成员可能看了电视剧之后注册的这个域名，由于该名称非常罕见，通过Google搜索，我们发现了其在欧洲跳蚤市场上注册的账号，账号注册时间和域名注册时间很接近，且最近还在活跃，可以基本确认该团伙成员应该位于海外。

![图片.png](https://image.3001.net/images/20191209/1575876219_5dedf67b418ac.png!small)  

经过海量数据查询，使用该团伙木马的诱饵名如下：

![图片.png](https://image.3001.net/images/20191209/1575876256_5dedf6a07b69e.png!small)  

  
  
  
  

通过开源蜜罐数据，我们得到了一个疑似符合该团伙命名习惯的动态域名chiji.f3322.net，该域名曾经用于投递上述payload，VT上显示有一个关联样本，时间为2018年初。主要功能为DDOS，有趣的是该样本的PDB路径：

![图片.png](https://image.3001.net/images/20191209/1575876362_5dedf70a7dba6.png!small)

![图片.png](https://image.3001.net/images/20191209/1575876417_5dedf7414015f.png!small)  

通过PDB关联到另一批样本，其中包含了linux平台的DDOS样本，提交时间仍是2018年初。

![图片.png](https://image.3001.net/images/20191209/1575876423_5dedf74723f3b.png!small)  

经过多维度关联，我们发现了一个手法相似的样本，名为链接.exe，初始样本都是Downloader，后续使用Dll-SideLoading技术。

![图片.png](https://image.3001.net/images/20191209/1575876430_5dedf74e2b0e4.png!small)  

本次劫持的是苏州蜗牛游戏（fxgame.exe）：

![图片.png](https://image.3001.net/images/20191209/1575876441_5dedf7596e280.png!small)  

同时从远程服务器上下载JPG或者txt并打开来迷惑用户，由于其TTP相似，我们将其归类为该黑产组织，其中从远程服务器下载的1.txt引起了我们的兴趣，内容如下：

![图片.png](https://image.3001.net/images/20191209/1575876446_5dedf75ee9f93.png!small)  

该网址为博·彩网站：

![图片.png](https://image.3001.net/images/20191209/1575876453_5dedf7650cc14.png!small)  

且封禁了大陆的IP访问：

![图片.png](https://image.3001.net/images/20191209/1575876459_5dedf76bbdba9.png!small)  

这再次说明了，该团伙是针对在东南亚从事博·彩，狗推行业的人员。通过代码特征进行关联，我们发现有的样本还伪装成360软件管家：

![图片.png](https://image.3001.net/images/20191209/1575876465_5dedf771440c1.png!small)  

同时我们找到了下载的另一个诱饵：

![图片.png](https://image.3001.net/images/20191209/1575876471_5dedf777cc443.png!small)  

湾汇支付是菲律宾的一个第三方支付平台，目前已经跑路

![图片.png](https://image.3001.net/images/20191209/1575876479_5dedf77f860b7.png!small)  

该团伙可能还参与了诈骗在菲华人的活动，其中有个同源样本连接了39399883.f3322.net动态域名，通过该域名我们又发现了一批样本，PDB路径：

![图片.png](https://image.3001.net/images/20191209/1575876515_5dedf7a306a87.png!small)

![图片.png](https://image.3001.net/images/20191209/1575876523_5dedf7ab7f0fd.png!small)  

连接域名：chenyon1314.xyz。域名符合该团伙命名习惯，通过该域名又关联到了一批样本：

![图片.png](https://image.3001.net/images/20191209/1575876548_5dedf7c44414f.png!small)

  

通过PDB我们关联到了一批使用大灰狼远程管理(V9.06)的样本，内存加载利用的程序如下：

![图片.png](https://image.3001.net/images/20191209/1575876574_5dedf7de93cc9.png!small)

  

又关联到了另一个域名[www.xunqing888.xyz](http://www.xunqing888.xyz)，该域名最近还在活跃，投递的文件名整理如下：

![图片.png](https://image.3001.net/images/20191209/1575876599_5dedf7f792d53.png!small)

碰巧的是，我们刚好在Telegram相关群组中偶遇了正在投递木马的该团伙成员：

![图片.png](https://image.3001.net/images/20191209/1575876628_5dedf81487b84.png!small)

  

该样本回连的域名还是[www.xunqing888.xyz](http://www.xunqing888.xyz)，同时我们还在群组中找到了该团伙最新投递的样本：

![图片.png](https://image.3001.net/images/20191209/1575876643_5dedf823a43b1.png!small)

TTP发生了细小的改变，第一阶段Downloader从远程服务器下载3个文件：

q0drurhbs.bkt.clouddn.com/z.rar

q0drurhbs.bkt.clouddn.com/z.sct

q0drurhbs.bkt.clouddn.com/temp.exe

z.sct内容如下：

![图片.png](https://image.3001.net/images/20191209/1575876708_5dedf86483205.png!small)  

Dll-SideLoading所需的文件被打包成了RAR：

![图片.png](https://image.3001.net/images/20191209/1575876714_5dedf86ae32c7.png!small)  

Temp.exe为UNRAR解压程序：

![图片.png](https://image.3001.net/images/20191209/1575876721_5dedf87111cea.png!small)  

后续的攻击流程与之前一致。

连接的C2：

103.233.10.85:5769

112.67.34.32:5767

# 诱饵名研究

我们通过各方渠道对收集的200多个样本的诱饵名进行分析，绘出如下图云。

![图片.png](https://image.3001.net/images/20191209/1575876730_5dedf87a06215.png!small)  

从图中可以看出，高频词汇为：“**”、“骗子”、“色图”、“薅羊毛”、“菲律宾”、“柬埔寨”、“赌博”等，这与样本上传地的数据相吻合，上述样本上传地大部分为柬埔寨和菲律宾。

通过对完整诱饵名进行归纳，可以分为如下几类：

1、色情类诱饵名

2、时事新闻类

![图片.png](https://image.3001.net/images/20191209/1575876788_5dedf8b492c4e.png!small)

3、UC震惊体，类似于国内导航站上面娱乐新闻的标题

![图片.png](https://image.3001.net/images/20191209/1575876810_5dedf8cad056f.png!small)

4、马来西亚相关诱饵

![图片.png](https://image.3001.net/images/20191209/1575876833_5dedf8e15af5b.png!small)

5、杀猪盘、狗推、博·彩、网贷相关的诱饵名

![图片.png](https://image.3001.net/images/20191209/1575876855_5dedf8f72a025.png!small)

6、资源共享类

![图片.png](https://image.3001.net/images/20191209/1575876875_5dedf90b4c3e1.png!small)

可见诱饵名内容遍及各行各业，诱惑性极强，应该是经过精心挑选出来的。为了满足我们的好奇心，现在要解决的一个问题是:这些诱饵名是从哪里来的呢？

# 攻击者在哪？

目前我们已知的是：攻击者应该是位于柬埔寨的华人。从测试域名入手，在奇安信平台中寻找时间在十月底和十一月初，与测试域名有关联性，且地址位于柬埔寨的IP，通过简单筛选我们发现了一个可疑的IP：49.156.XXX.XXX。

通过一些渠道，我们发现了一些端倪，以下为攻击者经常访问的一些站点。

![图片.png](https://image.3001.net/images/20191209/1575876903_5dedf92750338.png!small)  

![图片.png](https://image.3001.net/images/20191209/1575876997_5dedf98505183.png!small)  

新闻相关的站点诸如：大河网，网易新闻，东方网，北方网，齐鲁网，鲁网，以及一些政府相关的网站。

**相关网站，可能为攻击者的娱乐活动：

![图片.png](https://image.3001.net/images/20191209/1575877009_5dedf991ceb4b.png!small)  

  

![图片.png](https://image.3001.net/images/20191209/1575877027_5dedf9a396615.png!small)  

工作相关的站点

![图片.png](https://image.3001.net/images/20191209/1575877037_5dedf9ad18508.png!small)  

![图片.png](https://image.3001.net/images/20191209/1575877042_5dedf9b2aa5d0.png!small)  

![图片.png](https://image.3001.net/images/20191209/1575877047_5dedf9b764fdf.png!small)  

![图片.png](https://image.3001.net/images/20191209/1575877081_5dedf9d924a5e.png!small)  

生活相关站点

![图片.png](https://image.3001.net/images/20191209/1575877086_5dedf9dec9235.png!small)  

![图片.png](https://image.3001.net/images/20191209/1575877092_5dedf9e4e224f.png!small)  

![图片.png](https://image.3001.net/images/20191209/1575877098_5dedf9ea9fbcb.png!small)  

![图片.png](https://image.3001.net/images/20191209/1575877103_5dedf9ef5f8c8.png!small)  

# 总结

鉴于该金眼狗(GoldenEyeDog)黑产团伙的目标为东南亚地区的博·彩从业人员，并且使用的诱饵极具诱惑性，从我们的对样本的名称统计词云图便可以看出：这些诱饵有极大的可能被普通用户点击并运行。

为了防止用户误点击而导致个人财产和信息受到窃取，因此，奇安信病毒响应中心负责任的披露了这篇报告，并以学术性质的进行安全研究探讨：如何遏制此类极具诱惑力的样本攻击，才是我们当下应该要做的事情。

目前，奇安信全系产品已经支持本报告中提及的所有样本家族的查杀。

安全最脆弱的地方在于人心，当攻击者想方设法利用人性弱点进行攻击，那么当人疏忽的那一刻，悲剧便已经产生，加强安全意识培训，不要点击来历不明的exe，不要上不正规的网站，不要浏览博·彩网站，才是发扬社会主义核心价值观的处世之道。

# IOC

MD5：

79a4f8c5fe33b162187e2341e3fac004

b65b16cb38101fe83edc4afc50cdf100

6ae80424599498af8bcb128f0a24f9d1

03d8614a18a2d4bf1d6478fd216da2e2

7762605dcb35118fb69546affd096ac8

7b3ba2f713f05906b6241144f3979628

f3b32e9b5632230769de0abf150288a2

0d0e93676954f41af2b7885f6b788d1e

30ec1d1dabe0cd4e757f84a3052f3465

2f4329446849a13600aab4f03a7427a2

2de1a991b799bc11a67e9b5112947182

C2：

103.233.8.24:5768

223.199.1.113:5767

103.233.10.85:5769

112.67.34.32:5767

223.199.14.229:5767

202.181.24.16:8596

202.181.24.16:9118

103.76.87.126:9772

域名：

[test.hhlywsc.cn](https://www.virustotal.com/gui/search/behaviour_network%253A%2522http%253A%252F%252Ftest.hhlywsc.cn%252Fq.sct%2522)

[www.bestriven123.com](http://www.bestriven123.com)  
[www.xunqing888.xyz](http://www.xunqing888.xyz)

xunqing8888.xyz

chenyon1314.xyz

dpcq999.com

sudaqiang123.com

globaltopgarlic.com

test.microsft-update.com


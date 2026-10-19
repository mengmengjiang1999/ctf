## **一、** **概述**

**2018年至今，国内先后有多家安全厂商分别发现幽虫、独狼、双枪、紫狐、贪狼等多个病毒木马家族，这些木马利用盗版Ghost系统、激活破解工具、热门游戏外挂等渠道传播，在用户电脑上安装Rootkit后门，通过多种流行的黑色产业变现牟利：包括，云端控制下载更多木马、强制安装互联网软件、篡改锁定用户浏览器、刷量、挖矿等等。**

自诞生以来，这个超大的病毒团伙和国内众多杀毒厂商斗智斗勇，一个团伙在安全软件联合打击下消退，很快就有一个新的团伙取而代之。

腾讯安全御见威胁情报中心通过多个维度分析幽虫、独狼、双枪、紫狐、贪狼等病毒木马的技术特点、病毒代码的同源性分析、C2服务器注册、托管等线索综合分析，最终判断这5个影响恶劣的病毒团伙背后是由同一个犯罪组织操控。

该病毒团伙在2018年7-8月为活跃高峰，当时被感染的电脑在3000万-4000万台之间。之后，该病毒的传播有所收敛，在2018年8-11月感染量下降到1000万-2000万之间。至今，被该病毒团伙控制的电脑仍在200-300万台。

![1.png](https://image.3001.net/images/20190429/1556519275_5cc6996b09144.png!small)

传播趋势

该病毒团伙的受害者分布在全国各地，其中广东、山东、江苏受害最为严重。该病毒团伙受害者地域分布如下图所示：

![2.png](https://image.3001.net/images/20190429/1556519313_5cc69991660ed.png!small)

地域分布

腾讯安全专家最终依靠腾讯安图高级威胁追溯系统，将多个危害严重的病毒家族关联为一个大团伙，让人们更清晰的感知到网络病毒黑产规模之庞大，体系之成熟。

## **二、** **超大病毒团伙的发现**

腾讯安全专家通过例行的智能分析系统查询发现，双枪、紫狐、幽虫和独狼系列木马都被聚类到同一个自动家族T-F-8656。

（注：病毒家族智能分析系统是腾讯安全大数据平台的子系统，由腾讯安全御见威胁情报中心自主研发，集威胁发现、威胁分析、报告输出及可视化展示等能力于一身的高级威胁分析系统。自动家族是通过机器学习算法聚类得到的可疑木马家族，无须人工干预，系统可自动将存在关联关系的病毒家族聚类到一起。）

![4.png](https://image.3001.net/images/20190429/1556519315_5cc699939a432.png!small)

智能分析系统

利用智能分析系统从自动家族T-F-8656中筛选出部分关键节点，并使用3D模式进行可视化展示，发现幽虫、独狼、双枪、紫狐以及关联到的盗号、恶意推装木马之间联系非常紧密，但又层次分明，这一布局就像有人专门设计的结构。

![5.png](https://image.3001.net/images/20190429/1556519336_5cc699a8179b6.png!small)

T-F-8656家族3D可视化展示

进一步将上图中涉及到的所有信息进行分析整理，可以发现，幽虫和独狼木马通过盗版GHOST系统、系统激活工具、游戏外挂等多种渠道进行传播，负责在受害者系统中安装Rootkit，并将自身进行持久化（通过安装木马长时间控制目标系统，业内俗称“持久化”），然后再通过下载者木马投递双枪、紫狐、盗号木马等多种恶意程序，同时还在中毒电脑上推广安装多个软件、弹出广告或刷量。各个木马家族之间分工明确，环环相扣，组成了一个完整的产业链。

![6.png](https://image.3001.net/images/20190429/1556519334_5cc699a633cbb.png!small)

幽虫、独狼、双枪、紫狐等木马组成的产业链

##  **三、** **溯源分析**

不仅如此，以上这些木马还有更深入的联系，证明这些传播广泛的木马背后实属一个网络犯罪团伙控制。

### 1.幽虫==独狼系列

其他安全厂商披露的幽虫木马，实为御见威胁情报中心多次报道的独狼系列木马，为保证结果的可靠性，下面我们从不同的维度对此进行交叉验证。

**（1）攻击手法**

在幽虫和独狼2的分析报告中都有提到，独狼2和幽虫木马均通过伪装的系统激活工具进行传播，利用到的技术手段和最终的获利方式都如出一辙，同时受害用户中招之后，受害主机系统信息都被上传至同一C2域名[www.tj678.top](http://www.tj678.top)。

表1 幽虫、独狼2基本信息对比

|  **幽虫** |  **独狼2**  
---|---|---  
**传播渠道** |  系统激活工具  |  系统激活工具  
**技术手段** |  Rootkit、恶意驱动  |  Rootkit、恶意驱动  
**获利方式** |  恶意推装、锁主页  |  恶意推装、锁主页  
**C2** |  [www.tj678.top](http://www.tj678.top) |
[www.tj678.top](http://www.tj678.top)  
  
**（2）驱动代码相似同源**

独狼木马和幽虫木马的驱动代码相似度极高，如下图所示：

![7.png](https://image.3001.net/images/20190429/1556519347_5cc699b3dde3d.png!small)

独狼驱动部分代码

![8.png](https://image.3001.net/images/20190429/1556519364_5cc699c452c77.png!small)

幽虫驱动部分代码

如下图所示，对比独狼木马和幽虫木马驱动的关键函数代码流程图，发现它们的整体流程基本一致，可以确定它们属于同一木马家族。

![9.png](https://image.3001.net/images/20190429/1556519374_5cc699cee8a6a.png!small)

关键函数代码流程

 **（3）pdb名称**

通过腾讯安图高级威胁追溯系统进行查询，可以看到，幽虫木马和独狼1木马的pdb名称完全一致。

![10.png](https://image.3001.net/images/20190429/1556519394_5cc699e20b160.png!small)

幽虫木马pdb名称

![11.png](https://image.3001.net/images/20190429/1556519407_5cc699efc33fe.png!small)

独狼木马pdb名称

 **（4）样本签名**

幽虫木马和独狼木马的部分样本数字签名如下表所示，可见它们重复盗用相同的数字签名。

表2 幽虫、独狼木马签名对比

**_家族名_** |  **_MD5_** |  **_签名_**  
---|---|---  
**幽虫** |  01ccb04891ef1c19a5d750e79b3e2dac  |  浙江恒歌网络科技有限公司  
31aee7df1b47a6183061d94e6479e551  |  Beijing Founder Apabi Technology Limited  
b98b041ae51316cd0f544900ccbf76a4  |  GLOBAL BENEFIT NETWORK COMPANY LLC  
**独狼** |  0cea624e48f20f718198ab7349bb1eea  |  浙江恒歌网络科技有限公司  
419f1f778e1405354fd34e5293edd52d  |  Beijing Founder Apabi Technology Limited  
a0daebcd97f1ddc5c9cce3b838c39bb7  |  双双 何  
  
综上所述，幽虫木马和独狼木马其实属于同一个木马家族，并出自同一作者之手的可能性极大。

### 2.一根绳子上的蚂蚱

前面已经给出了充分的证明表示，幽虫木马和独狼木马属于同一个木马家族，并且出自同一作者之手。那么双枪、紫狐、贪狼是否也与该作者存在更深层次的联系呢？

为了帮助大家理清思路，首先，整理出各个木马家族的基本信息。

表3 各木马家族基本信息

**家族名** |  **传播渠道** |  **技术手段** |  **恶意行为**  
---|---|---|---  
**幽虫 &独狼** |  盗版GHOST系统、系统激活工具、游戏外挂  |  Bootkit/Rootkit、恶意驱动程序、盗用数字签名  |
主页锁定、刷量、传播盗号木马、恶意推装  
**双枪** **(外挂幽灵)** |  游戏外挂、下载站、第三方流氓软件  |
Bootkit/Rootkit、恶意驱动程序、盗用数字签名、利用公共网络服务（比如百度贴吧服务器）  |  锁主页、浏览器劫持、盗号、恶意推广、下发恶意程序  
**紫狐** **(外挂幽灵)** |  游戏外挂、下载站  |  恶意驱动程序  |  恶意推装  
**贪狼** |  盗版GHOST系统  |  Rootkit、恶意驱动程序、盗用数字签名  |  锁主页、浏览器劫持、刷量、挖矿、网络攻击、下发恶意程序  
  
由上表可见，这几个木马在传播渠道、技术手段、恶意行为上相似而又不尽相同，无法简单地判断它们是否是同一作者所为。

接着，再挑选各个木马家族的部分代表性样本，并提取它们的签名信息，如下表所示：

表4 各木马家族签名信息

**家族名** |  **MD5** |  **签名**  
---|---|---  
**幽虫 &独狼** |  01ccb04891ef1c19a5d750e79b3e2dac  | 浙江恒歌网络科技有限公司  
31aee7df1b47a6183061d94e6479e551  |  Beijing Founder Apabi Technology Limited  
b98b041ae51316cd0f544900ccbf76a4  |  GLOBAL BENEFIT NETWORK COMPANY LLC  
a0daebcd97f1ddc5c9cce3b838c39bb7  |  双双 何  
**双枪** |  fc0d16ffc6d384493cc4b31bba443c4a  |  浙江恒歌网络科技有限公司  
cfe79da256441e45195d6f47049cb2a8  |  Beijing Founder Apabi Technology Limited  
97f904690c228077c77d17fe675546c9  |  上海域联软件技术有限公司  
**贪狼** |  2ecee431a394538dd8b451b147d684ad  |  Hubei Xianning Wantong Security
Engineering Co., LTD  
  
幽虫&独狼与双枪木马使用的大部分签名是一样的，贪狼则使用不一样的签名信息。从盗用的签名上看，幽虫&独狼和双枪木马存在着很大的猫腻，而贪狼则貌似很“清白“。

友商曾于2018年10月份披露过，通过对比”贪狼“和多个版本的”双枪“的pdb，可以发现“双枪“中进行流量劫持的模块”AppManage.dll“与”贪狼“中实现相同功能的模块”AppManage.dll“出自同一木马作者之手，如下图所示，它们的pdb名称极其相似，并且频繁出现”ppzos“和”ivipm“字眼。

![12.png](https://image.3001.net/images/20190429/1556519433_5cc69a09b7a45.png!small)

双枪、贪狼pdb对比

![13.png](https://image.3001.net/images/20190429/1556519446_5cc69a16b1572.png!small)

双枪、贪狼pdb对比

而进一步通过腾讯安图高级威胁追溯系统进行关联发现，ppzos.com和ivipm.com的多个子域名均为双枪的C2，而且都在2018年8月~9月之间解析到了同一个ip地址103.35.72.205。

![14.png](https://image.3001.net/images/20190429/1556519465_5cc69a292f7e3.png!small)

双枪C2

另外，在差不多的时间节点，ppzos.com，ivipm.com等子域名又与贵阳市海云世纪科技有限公司的多个站点解析到同一个ip地址121.42.43.112。

![15.png](https://image.3001.net/images/20190429/1556519481_5cc69a399c133.png!small)

双枪C2

贵阳市海云世纪科技有限公司曾通过其公司官网[www.qhaiyun.com](http://www.qhaiyun.com)利用开心输入法等产品传播双枪木马，而该公司的产品点点输入法安装包的pdb名称与双枪、贪狼pdb名称高度相似，工程项目的父目录都在”E:\Code\Ivipm\source”和”E:\Code\ppzos\source”之下。

![16.png](https://image.3001.net/images/20190429/1556519495_5cc69a4748cf7.png!small)

开心输入法pdb

表5 双枪、贪狼、开心输入法pdb对比

**名称** |  **PDB** **路径**  
---|---  
**贪狼_AppManage.dll** |
E:\Code\Ivipm\source\AppManger\AppManger\x64\Release\AppManage.pdb  
**双枪_AppManage.dll** |
E:\Code\ppzos\source\AppManger\AppManger\x64\Release\AppManage.pdb  
**DDpxSetup19525_10057.exe(** **双枪)** |  E:\Code\Ivipm\source\diandianpy
\Dianinstall \Release\DiandianpySetup.pdb  
  
可以更进一步地证明，双枪和贪狼确实出自同一作者之手，该病毒作者与贵阳市海云世纪科技有限公司之间的存在相关性。

通过“天眼查”检索发现该公司目前已被注销。

![17.png](https://image.3001.net/images/20190429/1556519507_5cc69a534c860.png!small)

贵阳市海云世纪科技有限公司注册信息

而该公司旗下的多个站点已变成博彩网站，这可能意味着病毒作者在获得丰厚收益之后，有疑似跑路的嫌疑。

![18.jpg](https://image.3001.net/images/20190429/1556519532_5cc69a6c9b2b4.jpg!small)

官网变博彩站点

综上，可以确定幽虫&独狼、双枪、紫狐和贪狼木马其实出自同一团伙（作者）。为了方便回顾，将该团伙使用的各个木马家族之间的关系使用韦恩图整理如下：

![21.png](https://image.3001.net/images/20190429/1556519535_5cc69a6f3a9ef.png!small)该团伙的产业链整理如下图所示：

##
![22.png](https://image.3001.net/images/20190429/1556519551_5cc69a7fd5c30.png!small)
**四、** **解决方案**

1.建议网民使用正规软件，尽量不要下载运行各类外挂辅助工具，外挂和游戏辅助工具是病毒木马、违规软件传播的主要渠道之一。

2.几乎所有外挂网站都会诱导、欺骗游戏玩家退出或关闭杀毒软件后再运行外挂。一旦照办，杀毒软件有很高的概率被隐藏在外挂中的病毒木马破坏，从而令电脑失去安全防护能力。

3.激活工具、Ghost镜像历来都是Rootkit病毒传播的重要渠道，“独狼”Rootkit系列病毒具有隐蔽性强，反复感染，难查杀的特点。建议用户使用正版操作系统，如果杀毒软件报告发现激活破解补丁带毒，建议停止使用。

## IOCs（注：由于IOC过多，这里只给出部分未披露的IOC）

###  **紫狐**

f.pbipkierrqom.life

m.pbipkierrqom.life

l.pbipkierrqom.life

2.pbipkierrqom.life

6.pbipkierrqom.life

4.pbipkierrqom.life

8.pbipkierrqom.life

h.pbipkierrqom.life

5.pbipkierrqom.life

a.pbipkierrqom.life

9.pbipkierrqom.life

c.pbipkierrqom.life

i.pbipkierrqom.life

k.pbipkierrqom.life

g.pbipkierrqom.life

j.pbipkierrqom.life

e.pbipkierrqom.life

d.pbipkierrqom.life

0.pbipkierrqom.life

arildsdsxqls.info

216.250.99.26

216.250.99.42

###  **双枪**

white.icbc1234.com

white1.icbc1234.com

white2.icbc1234.com

125.7.29.26

###  ** _幽虫 &独狼_**

[www.dqzsy.com](http://www.dqzsy.com)

123dh.579609.com

[www.taolea.top](http://www.taolea.top)

dl.taolea.top

update.taolea.top

###  **贪狼**

e1.nchiu.com

e2.nchiu.com

m1.nchiu.com

m2.nchiu.com

### **五、参考链接**

1.盗版Ghost系统携“独狼”Rootkit来袭，锁定浏览器主页超20款

<https://mp.weixin.qq.com/s/6I-1YGs1o9hMMw6bW_JoPQ>

2.Rootkit病毒“独狼2”假冒激活工具传播，锁定23款浏览器主页

<https://mp.weixin.qq.com/s/-Pg-4MoD9LyQN5hmS-HOow>

3.幽虫木马分析

<https://www.anquanke.com/post/id/164372#h2-0>

4.酷玩游戏盒子伪造知名公司数字签名，传播Steam盗号木马

<https://mp.weixin.qq.com/s/mISZzxLJ5l9R__NmIatObQ>

5.“外挂幽灵”团伙曝光 系双枪、紫狐两大病毒家族的幕后推手

<https://mp.weixin.qq.com/s/EyzMIjEDO2OJWyaI-3gqOw>

6.“紫狐木马”暴力来袭

<http://www.360.cn/n/10386.html>

7.“双枪”木马专攻游戏外挂玩家，锁定主页强推开心输入法

<https://mp.weixin.qq.com/s/bnbT7nY6QeGJJS_6tVonVw>

8.“双枪”木马借“逆战契约”外挂，转战“流量劫持”

<http://www.360.cn/n/10439.html>

9.“双枪”木马的基础设施更新及相应传播方式的分析

<https://www.anquanke.com/post/id/168866#h2-12>

10.贪狼Rootkit僵尸家族再度活跃：挖矿+DDOS+劫持+暗刷

<https://www.freebuf.com/articles/paper/178927.html>

11.一款恶性Rootkit木马分析 ——“狼人杀”木马潜伏数十万台电脑

<https://slab.qq.com/news/tech/1534.html>

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**


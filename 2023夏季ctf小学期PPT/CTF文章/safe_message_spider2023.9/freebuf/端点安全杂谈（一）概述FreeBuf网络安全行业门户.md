## **写在开始**

为了记录自己了解端点安全的一些内容和想法，方便以后的对比并且能够与大家讨论和继续学习。内容有错误还是有遗漏希望大家能给予提点，涉及COPY的部分我会尽量标识出处，因为有些内容我也记不清要是没标出处还望大家指正。

## 什么是端点安全

端点安全、端点保护等等叫法的就是保护端点免受恶意活动危害的安全方法。EPP、EDR、CWPP等都是端点安全的一种解决方案，用不同的方式方法、角度、作用提供端点安全能力、功能。

## 什么被称为端点

端点通常是有权参与预定义活动的计算平台，是各种数据生产、处理、存储、应用的主体，所有的端点都是组织的资产为组织提供价值。目前终端范围已经从传统PC终端扩大到包括移动终端、云主机和物联网IoT（Internet
of
Thing）终端在内的形式多样的“泛终端”，或者说是新一代终端，传统的哑终端、非智能终端也开始向不同程度的智能终端方向靠拢，基于虚拟化的云主机也出现爆炸增长。

我理解现在的端点除了常见的PC、服务器、移动设备、IoT设备等，其他部署在网络边缘的带操作系统的任何设备被叫做端点都应该是可以的。

## 端点安全产品

Gartner2021年度的终端安全成熟度曲线显示，端点安全新兴技术主要体现在虚拟桌面基础架构（VDI）、桌面即服务（DaaS）统一终端安全（UES）、扩展检测和响应（XDR）、“基于AI”的端点安全引擎等方面。统一终端安全UES仍处于创新启动期；扩展检测和响应XDR快进入期望膨胀期；端点安全引擎从“基于规则”发展到了“基于AI”；杀毒判定方式从基于代码特征，变成基于用户行为进行恶意判定，从由本地判定，到云和端结合来判定，再结合威胁情报来进行防护；终端安全管理扩展到了移动终端和物联网终端层；主机安全向云端发展。Gartner2021技术成熟度曲线显示，扩展检测和响应（XDR）在膨胀期，终端检测与响应（EDR）、安全信息和事件管理（SIEM）、漏洞评估（VA）等发展多年的技术已经比较成熟稳定。

![1671784158_63a566de2ff647996fe2a.png!small?1671784158239](https://image.3001.net/images/20221223/1671784158_63a566de2ff647996fe2a.png!small?1671784158239)

Gartnet2022安全运营技术成熟度曲线显示，扩展检测和响应（XDR）站上了Peak of Inflated
Expectations的顶端，成为安全运营体系中最炙手可热的技术之一。Gartner给出的XDR定义为：XDR是一种基于SaaS的、绑定于特定供应商的安全威胁检测和事件响应工具，它将多个安全产品集成到一个统一了所有许可安全组件的内聚安全运营系统中。理想中的XDR技术，其实是安全信息和事件管理（SIEM）、安全编排自动化和响应（SOAR）、端点检测与响应（EDR）以及网络流量分析（NTA）等产品综合起来的结果。

![1671784186_63a566fabab5269da179b.png!small?1671784186818](https://image.3001.net/images/20221223/1671784186_63a566fabab5269da179b.png!small?1671784186818)

### 端点相关产品分类

在产品名称和分类上貌似国内一直赶不上进度的感觉，各厂商为产品能够在祖国市场上销售都是需要花费点心思的，目前销售许可证就那么几个分类，无论是新产品还是老产品都要匹配这些检测标准里明确规定的功能。比如EDR大多数厂商都选择了HIDS主机入侵检测这条道路，但也有个别厂商选择网络防病毒等其他产品分类。单看HIDS分类除了EDR还有PC沙箱、蜜罐产品也在其中，各产品功能、性能、作用都有很大差别但还用一样的检测标准，变成为了拿个证而做一些和产品无关的功能。这些检测标准之间也存在相互重复的功能项，重新定义产品标准又是任重道远的事了。HIDS在EDR推出之前应该没几个申请这个证的产品，看看现在那么多厂商做产品是不是应该有个HIPS什么的来单独划分个分类。

### 国内端点安全产品

国内端点安全产品按销售许可证产品分类主要分为：防病毒产品、主机安全加固、主机入侵检测、主机安全检查、主机文件监测、主机型防火墙、内网主机监测、主机安全检测、主机资源访问控制、终端接入控制、主机防泄露。

![1671784236_63a5672c8c7a4c4911b45.png!small?1671784236570](https://image.3001.net/images/20221223/1671784236_63a5672c8c7a4c4911b45.png!small?1671784236570)

###  **1.** ** **主机安全检查****

####  **1.1** ** **产品描述****

《GAT 1142-2014 信息安全技术
主机安全检查产品安全技术要求》：产品由代理和管理控制台组成，根据预先定义的安全策略模板，通过管理控制台对安装了代理的主机进行安全性检查，搭理收集数据，管理控制台分析数据并生成报告，达到发现其安全配置方面存在的问题的目的，此外主机安全检查产品本身及其内部的重要数据也是受保护的资产。

检查的项目场景的包括几个方面：配置检查，系统资源（CPU、内存、硬盘），杀毒软件、进程、服务，系统共享资源，启动项，外围接口设备，系统账户，软件安装，硬件配置，网络连接，系统漏洞。

主机安全检查产品以C/S方式部署或者单机方式部署，并执行安全功能。其安全检查的目标是安装了引擎的主机。

####  **1.2** ** **主要产品****

 ** **产品名称****

|

 ** **送检单位****  
  
---|---  
  
[安全基线管理系统Ultra-BMS](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=4f13d66a-2bfb-4e85-b15a-b76f96231a55)

|

北京神州泰岳软件股份有限公司  
  
[蜂眼主机计算环境安全监控平台](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=90e4e0ce-8a0e-4822-ab8d-fef7798354c5)

|

北京零平数据处理有限公司  
  
[博智工控终端基线核查系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=cdd2e8f3-31bc-4745-9e54-cd667196a279)

|

江苏博智软件科技股份有限公司  
  
[梆梆主机程序安全监控系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=1262235c-9dcb-45cb-86a6-d36755b47ed0)

|

北京梆梆安全科技有限公司  
  
[亿阳安全评估与检测平台软件](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=788ca958-897a-44fd-8150-813192bcbe33)

|

亿阳安全技术有限公司  
  
[天镜主机安全检测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=031013fd-5a9e-4f94-80e7-69960a0dc227)

|

上海喜数信息科技有限公司  
  
[安识主机安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=c6ec35cd-5f39-4834-95b2-bd1f04cb3a89)

|

上海安识网络科技有限公司  
  
[绿盟安全配置核查系统BVS](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=e0eea3a4-da19-45d5-aab0-edc30f4330c0)

|

北京神州绿盟科技有限公司  
  
[艾科网络桌面安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=b352a05b-e1a4-45bd-9532-4c60cc642726)

|

北京艾科网信科技有限公司  
  
[深信服基线核查系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=64af127e-c7a4-4420-9c29-034e2235c77d)

|

深信服科技股份有限公司  
  
[安全合规管理设备](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=bdfa0260-8650-4e9b-a450-fc8a7f88c71d)

|

工信通（北京）信息技术有限公司  
  
[通号安全基线核查系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=3bfac595-b405-4786-bb7f-a347afc99891)

|

北京全路通信信号研究设计院集团有限公司  
  
[北信源安全配置核查管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=ccf59f9a-9529-4db9-9332-be51d369ba2c)

|

北京北信源软件股份有限公司  
  
[天融信基线管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=abcd812f-398c-4cdf-bb45-1225de8e22b1)

|

北京天融信网络安全技术有限公司  
  
[百度主机安全客户端系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=214035ed-3c95-4d73-818c-d28f49900306)

|

北京百度网讯科技有限公司  
  
[安全基线管理系统Ultra-BMS](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=dc24711d-3c7e-4bd4-8009-0355924185a6)

|

北京神州泰岳软件股份有限公司  
  
  

###  **2** ** **数据泄露防护****

####  **2.1** ** **产品描述****

《GA∕T 912-2018 信息安全技术
数据泄露防护产品安全技术要求》：数据泄露防护产品通过对运行、存储于主机内或者网络中传输的文件、数据进行内容识别，对数据的操作和传输过程进行监视和控制，实现对数据以非授权的形式流出安全域进行防护的功能；同时该类产品还应具有基本的身份鉴别、安全管理、审计和报警功能，该类产品的部署和实现方式可分为主机型、网络型或综合型（包含数据客户端和网络设备）。

####  **2.2** ** **主要产品****

 ** **产品名称****

|

 ** **送检单位****  
  
---|---  
  
[Chinasec（安元）数据防泄漏系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=a74b26c6-a488-437a-8104-c77e0a7456d5)

|

北京明朝万达科技股份有限公司  
  
[华途数据防泄漏（DLP）系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=4408d5be-5d2b-46fc-8918-8a57389b5c7f)

|

浙江华途信息安全技术股份有限公司  
  
[亿赛通数据泄露防护（DLP）系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=eae2a9d0-034d-42d3-a6b1-f6976c75abd2)

|

北京亿赛通科技发展有限责任公司  
  
[联软UniDLP数据防泄露系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=4f5451e3-3c6e-4fb1-a619-5756fdb72aad)

|

深圳市联软科技股份有限公司  
  
[Data Loss
Prevention](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=88ec926e-0427-49b4-8681-34f99029a8b4)

|

迈克菲（上海）软件有限公司  
  
[北信源数据泄露防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=1b113e84-d8a3-4c9f-b9bd-10b8d56f9359)

|

北京北信源软件股份有限公司  
  
[中保网盾数据泄露防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=66364c46-b150-4ec5-8d52-c3fa5381f982)

|

北京市中保网盾科技有限公司  
  
[天清汉马数据防泄露系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=f56ce18c-af50-4384-9397-9bd36d425e04)

|

北京启明星辰信息安全技术有限公司  
  
[网御数据防泄露系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=08d23d5c-e580-468b-aafb-bc0cac0dfe68)

|

北京网御星云信息技术有限公司  
  
[山石网科数据泄露防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=0c31a390-8819-4364-9811-c6ec1b267308)

|

北京山石网科信息技术有限公司  
  
[云盾·数据泄密防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=bbcda03a-4428-4ee6-bac6-295d0d81007f)

|

阿里云计算有限公司  
  
[天融信数据防泄漏系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=6c6a0423-73c2-4e80-8a2c-8a3d91eee0f3)

|

北京天融信网络安全技术有限公司  
  
[Symantec Data Loss
Prevention](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=d71c68d0-3c2a-485f-907a-3c0fb6837e0a)

|

赛门铁克软件（北京）有限公司  
  
[天锐数据泄漏防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=987fb3cc-1f43-4199-98b9-001c5350ed70)

|

厦门天锐科技股份有限公司  
  
[奇安信网神数据防泄漏系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=0deb0671-2f28-47fa-a591-4b0d237ed557)

|

网神信息技术（北京）股份有限公司  
  
[美创诺亚数据防泄漏系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=c526d3f3-452c-4971-aa13-30898e159db5)

|

杭州美创科技有限公司  
  
[绿盟数据泄露防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=bad2531a-e6dc-482b-a1aa-9632810c9c29)

|

北京神州绿盟科技有限公司  
  
[Ultra-SmartDLP神州泰岳数据防泄漏系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=5dee0002-1226-4141-b776-f8fefcd481bc)

|

北京神州泰岳软件股份有限公司  
  
[润联软件数据安全防护平台](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=89aab0e8-a0d3-4232-8fc8-5f4bcc895040)

|

润联软件系统（深圳）有限公司  
  
[红途创程数据安全保护平台](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=57b712c8-6dbc-402d-8c01-92d41bcc2557)

|

深圳红途创程科技有限公司  
  
[Forcepoint Data Loss
Prevention](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=0772e404-cd7e-47fb-a5fd-61d0a5734367)

|

上海睿是信息科技有限公司  
  
[SecGator安全鳄数据防泄漏系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=2218fc9c-604b-4423-b9ed-75ad2c81e5d2)

|

北京天空卫士网络安全技术有限公司  
  
[思睿嘉得数据泄露防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=63f883de-11f8-4c77-b1e9-8a18e051c7d7)

|

思睿嘉得（北京）信息技术有限公司  
  
[前沿数据信息防泄漏系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=2ea5c6ee-2394-490d-95ff-adde3f81edba)

|

北京前沿信安科技股份有限公司  
  
 **3** ** **主机型防火墙****

####  **3.1** ** **产品描述****

《GA∕T 1177-2014 信息安全技术
第二代防火墙安全技术要求》：主机型防火墙以软件形式安装在最终用户计算机（包括个人计算机和服务器）上，阻止由外到内和由内到外的威胁。主机型防火墙不仅可以监测和控制网络级数据流，而且可以监测和控制应用程序，弥补网关防火墙和防病毒软件等传统防御手段的不足。此外，一般运行于服务器上的主机型防火墙还可以对所有的节点进行统一控制，实施统一的安全策略与响应。

主机型防火墙保护的资产是受安全策略保护的主机服务和文件等。此外，主机型防火墙软件本身及安全策略等重要数据也是受保护的资产。

####  **3.2** ** **主要产品****

 ** **产品名称****

|

 ** **送检单位****  
  
---|---  
  
[视频数据资源联网前置安全网关（全网通）](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=82815371-275d-4767-b726-dab5b40de2ba)

|

上海远哲电子技术有限公司  
  
[物联网安全网关](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=14866f9a-49d1-4fce-85d7-e7f4bfa289e6)

|

福建省酒窝网络科技有限公司  
  
[数据资源联网安全网关](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=f220443f-cd76-4d3d-99aa-5a4b7c78abe5)

|

深圳市海清视讯科技有限公司  
  
[蔷薇灵动蜂巢主机防火墙](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=eb5d308c-0908-4444-9554-41d7f1fffce7)

|

北京蔷薇灵动科技有限公司  
  
[神威主机防火墙系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=cb8a4e11-dce9-4b58-ae3d-da28204eb625)

|

江南信安（北京）科技有限公司  
  
[视频数据安全网关系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=f65aaa39-1075-47cf-9883-f247ffbcdd92)

|

上海远哲电子技术有限公司  
  
###  **4** ** **主机资源访问控制****

####  **4.1** ** **产品描述****

《GA∕T 1138-2014 信息安全技术
主机资源访问控制产品安全技术要求》：主机资源访问控制产品针对受控主机，统一分配用户的登录权限和对主机资源的访问权限，从而保证用户根据预先定义的访问控制策略对受控主机的资源（包括系统登录权限、文件和文件夹、外设接口、应用程序、进程等）进行访问，以此来保护主机资源不被未授权访问和使用

主机资源访问控制产品一般由服务器、客户端和管理控制台三部分组成，由服务器下发访问控制策略到客户端。其保护的资产是主机资源，此外主机资源访问控制产品本身及其内部的重要数据也是受保护的资产。

####  **4.2** ** **主要产品****

产品名称

|

送检单位  
  
---|---  
  
[信达主机安全访问控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=004d755e-50c7-4de4-a919-b756d105032c)

|

北京信达环宇安全网络技术有限公司  
  
 **5** ** **防病毒****

####  **5.1** ** **产品描述****

《GBT 37090—2018信息安全技术
病毒防治产品安全技术要求和测试评价方法》：病毒防治产品是一种以恶意软件防护作为其全部或部分功能的产品，用于检测发现或阻止恶意软件的传播以及对主机操作系统、应用软件和用户文件的篡改、窃取和破坏等。

####  **5.2** ** **主要产品****

[AhnLab Endpoint Protection System
Software](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=e394cd77-ac1a-4f5d-9f1f-225bd8f75dda)

|

北京安博士信息安全技术有限公司  
  
---|---  
  
[安天智甲终端防御系统V5.0](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=6809a04a-b4c3-42fc-be21-ab64df52e363)

|

北京安天网络安全技术有限公司  
  
[北信源防病毒系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=42ddb6e0-e6c5-4cd3-828d-59f145c68fbd)

|

北京北信源软件股份有限公司  
  
[辰信领创防病毒系统V7.0](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=a9a33eba-6fbe-41ca-8912-bbbb2c758d0c)

|

北京辰信领创信息技术有限公司  
  
[微点主动防御软件网络版软件V2.2](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=ec5eee38-b835-4921-9519-ae689f64232d)

|

北京东方微点信息技术有限责任公司  
  
[网络版防病毒系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=348123f3-1130-4a2f-a778-75b5e3e7a256)

|

北京冠群金辰软件有限公司  
  
[恒安嘉新僵尸网络木马和蠕虫监测与处置系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=3974c83a-0160-4338-a89b-32bdb6480c02)

|

北京恒安嘉新安全技术有限公司  
  
[火绒终端安全管理系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=319325f0-9c13-48aa-a86a-1df394278a68)

|

北京火绒网络科技有限公司  
  
[江民网络版杀毒软件](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=6fb918db-3a0f-4496-95ec-2d1d2eea149d)

|

北京江民新科技术有限公司  
  
[金山安全防病毒系统（专用网络版）](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=c2b5d8bb-cc49-41e3-ae91-8de35dd3e91c)

|

北京猎鹰安全科技有限公司  
  
[天珣内网安全风险管理与审计系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=42c06844-4542-4752-a32f-39cd453fae12)

|

北京启明星辰信息安全技术有限公司  
  
[瑞星杀毒软件网络版](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=324be36b-99e4-498d-ac8f-1d6f6b364b6c)

|

北京瑞星网安技术股份有限公司  
  
[绿盟终端安全系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=5b798346-2244-4491-ba08-8dd8e0153e1a)

|

北京神州绿盟科技有限公司  
  
[天融信终端威胁防御系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=78005918-68da-4af2-967d-3d74bc8546bd)

|

北京天融信网络安全技术有限公司  
  
[天蝎终端侦测与响应系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=47a94713-906a-4982-a1a8-cb370ba2c574)

|

北京网思科平科技有限公司  
  
[网御内网安全管理系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=903fc13f-f129-4642-a204-5496a59e2d09)

|

北京网御星云信息技术有限公司  
  
[安恒明御杀毒软件-RA专版
3.0](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=6d38bc76-5854-4fb4-8548-bd4468acd1f2)

|

杭州安恒信息技术股份有限公司  
  
[恒安嘉新僵尸网络木马和蠕虫监测与处置系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=cd9f3df7-6a3e-474f-bec0-1c455716e7bb)

|

恒安嘉新（北京）科技股份公司  
  
[Kaspersky Industrial CyberSecurity for
Node](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=d0d909f9-ac5c-4971-81a6-3a32ce46927c)

|

卡巴斯基技术开发（北京）有限公司  
  
[MOVE
AntiVirus](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=452d1bb3-bc99-4d0b-9b51-c7a3563ddfa5)

|

迈克菲（北京）安全软件有限公司  
  
[奇安信防病毒系统（专用网络版）](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=bc9c6245-095f-436a-b086-0a1cbc37e594)

|

奇安信科技集团股份有限公司  
  
[深信服终端检测响应平台](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=21c97a4c-ac9e-47b1-aec4-7d7beea5f146)

|

深信服科技股份有限公司  
  
[Bitdefender
GravityZone](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=7d7dda3d-2869-4c2b-b9e9-51a608bb912c)

|

深圳市比特梵德科技有限公司  
  
[联软UniEDR终端检测与响应系统（防病毒）](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=58314b58-5cec-4cfd-a2d4-58cda6b12cc4)

|

深圳市联软科技股份有限公司  
  
[腾讯御点](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=6c6f576f-06f2-47ca-a8ba-6c1ba84b5342)

|

深圳市腾讯计算机系统有限公司  
  
[东软NetEye终端安全管理系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=94684005-9d70-45e4-b202-ef3c3c3832a4)

|

沈阳东软系统集成工程有限公司  
  
[System Center 2012 R2 Endpoint
Protection](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=bd03f253-5320-49ed-9873-d5013f33d362)

|

微软(中国)有限公司  
  
[亚信安全防毒墙网络版软件OfficeScan](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=a09c2f23-faa3-44e9-8b56-59cb9b5db34d)

|

亚信科技（成都）有限公司  
  
 **6** ** **内网主机监测****

####  **6.1** ** **产品描述****

《GA∕T 910-2010 信息安全技术 内网主机监测产品安全技术要求》：采用代理/服务器结构，对受控主机上的各项活动进行监控的产品。

####  **6.2** ** **主要产品****

 ** **产品名称****

|

 ** **送检单位****  
  
---|---  
  
[北信源内网安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=4fdacd13-98d3-45f9-8fbd-dfd38509eb1e)

|

北京北信源软件股份有限公司  
  
[鼎普主机监控与审计系统ANK](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=e30b8ace-8988-4202-aa91-3f1b56d90d6e)

|

北京鼎普科技股份有限公司  
  
[终端安全监测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=10d84b85-7ddd-470f-aaaf-caafb8c77e66)

|

北京立思辰计算机技术有限公司  
  
[猎鹰桌面安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=9f6d1ca6-546c-4ca4-a2a0-6ac823d1a6e7)

|

北京猎鹰安全科技有限公司  
  
[科云主机监控与审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=3dfea59b-e6dd-4242-9ca7-1e2159ee5682)

|

北京普世时代科技有限公司  
  
[天珣内网安全风险管理与审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=9a2223de-760c-40f7-95a5-b2fd929a9e3f)

|

北京启明星辰信息安全技术有限公司  
  
[主机安全防护代理软件](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=a60d6491-0ab8-4ea5-8f1d-d5034145322c)

|

北京赛搏长城信息科技有限公司  
  
[LanSecS内网安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=419eded5-1435-4285-9fed-d8d33a345f0e)

|

北京圣博润高新技术股份有限公司  
  
[天融信主机监控与审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=eea7e7d9-78e7-410a-a574-e598710cf9d0)

|

北京天融信网络安全技术有限公司  
  
[万里红主机监控与审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=6dc512cd-2c84-49a5-85d5-363235a8d98a)

|

北京万里红科技股份有限公司  
  
[网御内网安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=ce38b024-1e91-46cc-b6a2-a653d9ecfb6c)

|

北京网御星云信息技术有限公司  
  
[信达信息安全防护系统-安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=14160b3e-7c61-4d07-894b-1564a078713f)

|

北京信达环宇安全网络技术有限公司  
  
[立思辰终端防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=52dc8890-7454-485c-a0d2-367d25871b4d)

|

杭州立思辰安科科技有限公司  
  
[盈高多维终端安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=fc510d40-70cc-4b72-b775-85b3ce366b06)

|

杭州盈高科技有限公司  
  
[蓝盾内网安全管理及审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=5ac58bd1-163b-48e7-a058-e7cf6590f8f1)

|

蓝盾信息安全技术股份有限公司、蓝盾信息安全技术有限公司  
  
[奇安信终端安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=7406db76-e5a3-4a07-9475-0452f9a961a0)

|

奇安信科技集团股份有限公司  
  
[高重主机安全及管理软件](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=313f093f-8338-4b3a-a20a-23efc112b497)

|

上海高重信息科技有限公司  
  
[e盾安全网络管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=75a2833c-c997-473c-98ad-f6bbafd680c9)

|

上海信安信息技术发展股份有限公司  
  
[联软主机监控与审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=5d74cff9-a64e-406f-b186-5a286eb1e345)

|

深圳市联软科技股份有限公司  
  
[腾讯IoA](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=6522249f-4e7f-42b8-b5ba-213d23b069ca)

|

腾讯云计算（北京）有限责任公司  
  
[捷普主机监控与审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=b15afafe-418f-496a-aec9-40e58e985eeb)

|

西安交大捷普网络科技有限公司  
  
[亚信安全终端安全管理系统 AINSG-TSM](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=8e21024d-c525-47ec-9b7e-21152a7d6e6f)

|

亚信科技（成都）有限公司  
  
 **7** ** **终端接入控制****

####  **7.1** ** **产品描述****

《GA∕T 1105-2013 信息安全技术
终端接入控制产品安全技术要求》：对采用802.1x等认证方式接入局域网的终端，实现基于用户身份和终端安全状态接入控制的产品。该类产品能够发现终端接入网络的行为，并能根据接入控制策略采取相应措施，保证未被授权或不符合安全策略的终端设备无法接入网络，并设置可补救的隔离区供终端修正自身安全状态已满足安全策略要求。

####  **7.2** ** **主要产品****

 ** **产品名称****

|

 ** **送检单位****  
  
---|---  
  
[艾科网络接入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=963fbaaf-06ab-4acc-acc9-e6bf16e45676)

|

北京艾科网信科技有限公司  
  
[北信源网络接入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=5dfd7681-5f9a-458d-bebc-cb8a31f4bb7f)

|

北京北信源软件股份有限公司  
  
[江南天安网络准入管理系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=3416721f-9fd2-4ba1-b804-a59557f3f147)

|

北京江南天安科技有限公司  
  
[网络准入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=12fcd0ea-1675-4a0f-9f24-b48a40e9227a)

|

北京立思辰计算机技术有限公司  
  
[天清网络安全接入控制防护系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=10a767ec-6860-4b72-9b78-f397a158bea6)

|

北京启明星辰信息安全技术有限公司  
  
[LanSecS网络终端接入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=2e24db45-1e9f-440d-a347-e693c77a8ed9)

|

北京圣博润高新技术股份有限公司  
  
[网络准入管理系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=861064c8-eb18-45fb-a2a1-e3538dd6d272)

|

北京天地和兴科技有限公司  
  
[天融信网络准入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=82371be4-1fb2-4295-a216-278eba45e9cc)

|

北京天融信网络安全技术有限公司  
  
[万里红网络接入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=0fd99991-226b-44ac-a156-779fed712f06)

|

北京万里红科技股份有限公司  
  
[网御网络安全接入控制防护系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=ef59651e-ea6c-4eae-80ef-d673b3b2ddb1)

|

北京网御星云信息技术有限公司  
  
[网络准入系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=71df0e49-a174-4aea-8c35-dffb1302fe0e)

|

北京威努特技术有限公司  
  
[锐捷易安全系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=c3d4cab4-1f25-4db1-afb8-f2a77ce7ba7b)

|

北京星网锐捷网络技术有限公司  
  
[格尔网络接入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=ad578df9-2657-4a68-9462-0a58149d2822)

|

格尔软件股份有限公司、上海格尔安全科技有限公司  
  
[世安网络准入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=57cb1b99-f9ef-464d-97d5-5ecbe81705f9)

|

广州世安信息技术股份有限公司  
  
[南瑞定制化网络准入系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=7454cce1-9099-463f-a862-7295694a0a56)

|

国电南瑞科技股份有限公司  
  
[盈高入网规范管理系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=2c071f93-63a4-4b16-9a22-d7b76d3d9507)

|

杭州盈高科技有限公司  
  
[立思辰网络准入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=e9e46254-2cf5-42c6-8853-bb804498c24c)

|

杭州域晓科技有限公司  
  
[华为敏捷控制器Agile Controller-Campus](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=fbedf773-9158-4643-bf2f-b34a4d8b6101)

|

华为技术有限公司  
  
[网络接入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=6a3191d2-46ff-40ff-bf4c-e573af977ba6)

|

山东华软金盾软件股份有限公司  
  
[中网云安网络准入及服务管理系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=d617c043-9ea8-4281-8234-c0762da49b9d)

|

山东中网云安智能科技有限公司  
  
[深信服全网行为管理系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=9c59a138-f138-433d-83e6-43c40d4164c2)

|

深信服科技股份有限公司  
  
[联软网络接入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=c6fe0df4-b19c-4244-9eeb-ea31ed0e2c7c)

|

深圳市联软科技股份有限公司  
  
[谛听网络准入管理系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=e81500dd-e549-424a-9d6b-2770ae166a2f)

|

唐僧（北京）安全科技有限公司  
  
[H3C iMC EPS
鹰视接入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=d81c0f00-a68d-4955-8184-06a6e968b876)

|

新华三技术有限公司  
  
[英赛克网络准入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=61b80182-e0b2-4252-ba07-ed8554384746)

|

英赛克科技（北京）有限公司  
  
[中软网络接入控制系统](https://ispl.mps.gov.cn/ispl/jsp/common/ProductInfo.jsp?productID=4cbb26a3-74c6-4c62-a848-18a91b8dd671)

|

中国软件与技术服务股份有限公司  
  
 **8** ** **主机安全检测****

####  **8.1** ** **产品描述****

《GA∕T 1536-2018 信息安全技术
计算机主机安全检测产品测评准则》：此类产品指标要求中涉及检测病毒能力、身份鉴别、访问控制、安全审计、剩余信息保护、入侵防范、恶意代码防范、资源控制、数据检测。

####  **8.2** ** **主要产品****

 ** **产品名称****

|

 ** **送检单位****  
  
---|---  
  
[安天拓痕主机安全检查系统(TDS)V3.0](https://www.ispl.com.cn/ispl/)

|

北京安天网络安全技术有限公司  
  
[主机安全防护系统](https://www.ispl.com.cn/ispl/)

|

北京天地和兴科技有限公司  
  
 **9** ** **主机型入侵检测****

####  **9.1** ** **产品描述****

《GAT 403.2-2014 信息安全技术 入侵检测产品安全技术要求
第2部分：主机型产品》：主机型入侵检测产品以系统日志、应用程序日志等作为数据源，或者通过其他手段（如监督系统调用）从所在的目标主机收集信息进行分析，从而发现异常行为的入侵检测系统。

####  **9.2** ** **主要产品****

 ** **产品名称****

|

 ** **送检单位****  
  
---|---  
  
[安天智甲终端检测与响应系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=10816714-58fc-4146-816b-4fd5a7c71fc0)

|

北京安天网络安全技术有限公司  
  
[杰思猎鹰主机安全响应系统](https://www.ispl.com.cn/ispl/)

|

北京杰思安全科技有限公司  
  
[360攻击欺骗防御系统](https://www.ispl.com.cn/ispl/)

|

北京奇虎科技有限公司  
  
[天阗欺骗防御系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=3d39c3ab-ec37-4526-b4a2-ba08a1d50bbc)

|

北京启明星辰信息安全技术有限公司  
  
[青藤猎鹰主机威胁检测平台](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=f46b2e18-13bc-4f0a-9550-949196c6939d)

|

北京升鑫网络科技有限公司  
  
[天融信潜听威胁发现系统](https://www.ispl.com.cn/ispl/)

|

北京天融信网络安全技术有限公司  
  
[网御欺骗防御系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=22514e3f-e744-4e82-bd73-1e234a0e0c76)

|

北京网御星云信息技术有限公司  
  
[镜界容器安全防护平台](https://www.ispl.com.cn/ispl/)

|

北京小佑科技有限公司  
  
[有饵主机威胁发现系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=57f51819-0dbc-49f8-a179-314686906d4b)

|

北京元支点信息安全技术有限公司  
  
[云戟主机型入侵检测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=e630a430-1505-4ec2-8336-c8a1d5f258c9)

|

北京云弈科技有限公司  
  
[长亭牧云主机安全管理平台](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=13ea85c1-6a4b-4512-80a8-66cf63ecaa63)

|

北京长亭未来科技有限公司  
  
[网络安全预警系统](https://www.ispl.com.cn/ispl/)

|

北京智仁智信系统集成有限公司  
  
[智域主机入侵检测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=ae6c0138-76b9-4565-bbc6-eb96c3fa74b5)

|

北京中安网星科技有限责任公司  
  
[非凡攻击诱捕与威胁检测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=cbe6e9d0-10ab-4c9f-8f4d-549fd67622ab)

|

广州非凡信息安全技术有限公司  
  
[国利终端检测响应系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=b354fa28-9722-4778-8e42-805f1927a056)

|

国利灏业科技有限公司  
  
[明鉴迷网系统](https://www.ispl.com.cn/ispl/)

|

杭州安恒信息技术股份有限公司  
  
[安石Cornerstone端点检测与响应系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=cc2c73bb-feeb-4854-b400-a255b6f78b1a)

|

杭州义盾信息技术有限公司  
  
[华为云企业主机安全产品](https://www.ispl.com.cn/ispl/)

|

华为技术有限公司  
  
[幻视(H-Sensor)入侵感知与威胁溯源系统](https://www.ispl.com.cn/ispl/)

|

江苏创宇盾安全技术有限公司  
  
[安全狗云眼—(云)主机入侵监测及安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=07e33282-5544-43dc-90e1-5d7c5fb7aa91)

|

厦门服云信息科技有限公司  
  
[魅影威胁监测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=1ff2ff7e-ca15-499a-8485-97597d095358)

|

上海观安信息技术股份有限公司  
  
[深信服云主机安全保护平台](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=48fca382-a615-4ed3-a83d-070fb9095e56)

|

深信服科技股份有限公司  
  
[联软UniEDR终端检测与响应系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=b3c8030c-67d3-468b-b059-e1cf67514a22)

|

深圳市联软科技股份有限公司  
  
[腾讯安全入侵欺骗防御系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=2795c4f8-5f7a-4674-aaed-22c82d91979a)

|

腾讯云计算（北京）有限责任公司  
  
[奇安信网神终端安全响应系统](https://www.ispl.com.cn/ispl/)

|

网神信息技术（北京）股份有限公司  
  
[网宿主机入侵检测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=01b4a3d6-751f-4bf8-bda5-4963ab14041f)

|

网宿科技股份有限公司  
  
[主机入侵检测系统UHIDS](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=3b33cbbb-43de-404d-b021-e7c51745e85d)

|

优刻得科技股份有限公司  
  
 **10** ** **主机文件监测****

####  **10.1** ** **产品描述****

《GAT 1392-2017 信息安全技术
主机文件监测产品安全技术要求》：主机文件监测产品依据预先定义的安全策略，通过文件完整性检查、文件属性检查、关键字检查等手段对主机文件（包括存放在主机上的重要系统文件、配置文件，以及预定义的其他文件）的状态、修改行为等作出监测并报警，从而保证主机上的文件资源不被未授权访问和操作。

####  **10.2** ** **主要产品****

 ** **产品名称****

|

 ** **送检单位****  
  
---|---  
  
[内存保护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=942c6081-27cf-4457-af0f-8cf02b5ae41a)

|

安芯网盾（北京）科技有限公司  
  
[云锁适应性主机安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=f567d2fb-bb11-4d1a-8a82-c895d32c873b)

|

北京椒图科技有限公司  
  
[青藤主机自适应安全平台](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=46b2bc37-8f84-4a52-ad87-5f75bfa25710)

|

北京升鑫网络科技有限公司  
  
[微步主机安全监测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=53b8a4e6-5238-4038-8415-428d59bc0db7)

|

北京微步在线科技有限公司  
  
[应用主机综合防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=ddf0c740-122d-4bfb-af74-bbe1624ca863)

|

北京中盾安全技术开发公司  
  
[焱杰主机文件监测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=a38b650c-2895-40e1-8148-c8b09612d01e)

|

广东焱杰电子科技有限公司  
  
[WAPPSEC主机环境文件监测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=1d9fded5-14a3-4db0-a387-0e5a9ae6864d)

|

广州市安鸿网络科技有限公司  
  
[明御主机安全及管理系统 Endpoint security management
system](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=6f201e5b-2483-4fe1-8c71-112babf1f7b8)

|

杭州安恒信息技术股份有限公司  
  
[美创诺亚防勒索主机防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=5bc83caa-7c6a-496f-b055-4a7d2f50972a)

|

杭州美创科技有限公司  
  
[盈高入网保密审查辅助系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=c77b96dc-52a0-4f2c-bd7b-3d2fec03c532)

|

杭州盈高科技有限公司  
  
[金骑士主机安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=c59a89c5-3ce7-48eb-863e-6ec4abca0f57)

|

恒安嘉新（北京）科技股份公司  
  
[慧盾数据安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=badede2f-320c-4049-847f-e94475a2d817)

|

慧盾信息安全科技（苏州）股份有限公司  
  
[Integrity
Control](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=fa9551bb-e6e3-4efe-b263-972436b3e7aa)

|

迈克菲（上海）软件有限公司  
  
[主机文件监测管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=978f9c9a-7f9d-4242-a468-439641d3b924)

|

上海观安信息技术股份有限公司  
  
[意恒应用安全监测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=44c0d815-425b-472c-bc74-51695b20347a)

|

上海意恒软件有限公司  
  
[深密计算机终端安全预警平台](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=0dce31e8-61ed-4b3b-b3d9-9d0b498e4a12)

|

深圳市深密信安科技有限公司  
  
[完璧完整性安全监测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=7749da02-b845-4d52-9c3d-0ce3e225a354)

|

苏州冠辰计算机信息技术有限公司  
  
[腾讯云镜主机安全监测软件](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=93cf3747-6714-43b5-8cf3-471750b9df96)

|

腾讯云计算（北京）有限责任公司  
  
[奇安信网神云锁服务器安全管理系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=ad34bf9d-7bba-4ae6-8b52-cc488f315d0b)

|

网神信息技术（北京）股份有限公司  
  
[H3C SecPath SSMS
服务器安全监测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=3897f826-0739-44af-872e-e0acaf358f70)

|

新华三技术有限公司  
  
 **11** ** **主机安全加固****

####  **11.1** ** **产品描述****

《GAT 1393-2017 信息安全技术
主机安全加固系统安全技术要求》：主机安全加固系统是在通用操作系统的基础上，通过对操作系统主客体进行安全标记、增加强制访问控制、完整性保护等技术手段，对操作系统进行安全功能增强，弥补通用操作系统安全性不高的缺陷，提高了操作系统的安全保护能力。

####  **11.2** ** **主要产品****

 ** **产品名称****

|

 ** **产品类型****

|

 ** **送检单位****  
  
---|---|---  
  
[EdgeDefender
恩创工业安全卫士](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=bcd2bebe-d6a5-4ea5-a96a-568e0da013d3)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

安通恩创信息技术（北京）有限公司  
  
[节点-操作系统安全加固系统软件](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=1bd25b01-797d-4096-8b4a-0d5371dc6459)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

北京北信源软件股份有限公司，北京中软华泰信息技术有限责任公司  
  
[创安恒宇计算节点主动免疫系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=2ce87d4e-01cb-4cfe-8c63-dad9fdefd22e)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

北京创安恒宇科技有限公司  
  
[主机安全加固系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=a1ccb3c0-82e7-445e-b57a-b8e3ec5434dd)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

北京国基华电科技有限公司  
  
[主机防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=0793ee8a-f1bb-4db7-adec-22538ac029b5)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

北京三实众智信息科技有限公司  
  
[主机安全防护系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=4a40f04d-9f06-4882-b33f-54c19ff70861)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

北京天地和兴科技有限公司  
  
[主机环境安全增强系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=5e4ffd1d-b032-4d12-8a29-7f27a9de21bd)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

北京西南交大盛阳科技股份有限公司  
  
[操作系统安全增强系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=1a72e40e-6068-4a93-af36-9d770c9f302b)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

北京优炫软件股份有限公司  
  
[主机安全加固系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=037ea62d-7e63-4d97-82df-bb7042ff619c)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

北京中能科越电力技术有限公司  
  
[听风云主机防护与监测系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=8ac865fd-edce-4bff-a62c-ea90829606cf)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

杭州听风云科技有限公司  
  
[主机安全加固系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=80a32769-9607-4781-9957-aa89e157fe40)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

懋晟智慧（北京）科技有限公司  
  
[NARI
TMAC-3000内核安全增强软件](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=11572aa5-b25e-4a36-949a-188694a3c73d)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

南京南瑞信息通信科技有限公司  
  
[计算机免疫系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=2cadf8eb-fffd-432d-8a9a-5005f98f5634)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

深圳可信计算技术有限公司  
  
[终端安全卫士](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=8a6d0b74-1e4d-4da5-a20b-335488408a17)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

深圳融安网络科技有限公司  
  
[奇安信网神云锁服务器操作系统安全增强系统（Linux版）](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=7fa16838-dcc5-4673-bc96-eac55ce88a4f)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

网神信息技术（北京）股份有限公司  
  
[亚信安全终端安全加固软件AOS-ISL-PLUS](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=62c5f4ed-22e7-4dc6-a164-8d2a99be083b)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

亚信科技（成都）有限公司  
  
[主机安全加固系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=5b61d028-ceda-4895-bf8e-827ffdd42d4f)

|

[主机安全加固(基本级)](https://www.ispl.com.cn/ispl/jsp/common/ProductList_Public.jsp?productTypeGroup1=001160001)

|

英赛克科技（北京）有限公司  
  
  

###  **12** ** **主机安全审计****

####  **12.1.** ** **产品描述****

《GBT 20945—2013信息安全技术 信息系统安全审计产品技术要求和测试评价方法》：对主机系统的事件进行记录和分析，并针对特定事件采取相应比较动作。

####  **12.2.** ** **主要产品****

 ** **产品名称****

|

 ** **送检单位****  
  
---|---  
  
[零知云数据安全系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=78d06a11-6b82-4b1c-9fd2-576fc6ec7c6e)

|

北京古盘创世科技发展有限公司  
  
[Kvall审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=0ec0c914-561f-4b85-83da-8a6d3930937b)

|

北京坤源恒泰科技发展有限公司  
  
[天地和兴日志审计与分析系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=4e86a8e4-d76b-4f7f-8178-0206abd3520e)

|

北京天地和兴科技有限公司  
  
[ITC安全审计管理平台](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=520a5b9f-bfed-4122-b289-8f33c762e08f)

|

北京英孚泰克信息技术股份有限公司  
  
[中科富星集中监控审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=8c36ee6b-24c6-43b0-aac1-a01365bf9a1d)

|

北京中科富星信息技术有限公司  
  
[锦行幻云主机行为审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=ff1c1d6e-ce15-46fd-8492-7b9d863f73a5)

|

广州锦行网络科技有限公司  
  
[蓝盾主机安全审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=eb7230be-67e4-483f-b6be-31d1b84dbb53)

|

蓝盾信息安全技术有限公司  
  
[电力监控系统安全监测装置（II型）](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=9e1ff940-4015-4364-93d6-805c10ef3521)

|

山东金煜电子科技有限公司  
  
[汉邦主机监控与审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=093cc6fb-a4f5-4f33-a401-e46bce0247a8)

|

上海汉邦京泰数码技术有限公司  
  
[华安达主机监控与审计系统](https://www.ispl.com.cn/ispl/jsp/common/ProductInfo.jsp?productID=b9bc2a42-22f3-4971-b93b-9525918b3c21)

|

上海华安达信息技术发展有限公司  
  
###  ** **端点安全国际分类****

分类

|

说明性定义  
  
---|---  
  
EDR

|

Endpoint Detection and
Response：端点检测与响应；端点检测和响应是一种主动式端点安全解决方案，通过记录终端与网络事件，并将这些信息本地存储在端点或集中数据库。结合已知的攻击指示器(Indicators
of
Compromise，IoCs)、行为分析的数据库来连续搜索数据和机器学习技术来监测任何可能的安全威胁，并对这些安全威胁做出快速响应。还有助于快速调查攻击范围，并提供响应能力。  
  
EPP

|

Endpoint protection
platforms：终端防护平台；是一个集成解决方案，具有反恶意软件、个人防火墙、端口和设备控制等功能。EPP解决方案通常还包括:漏洞评估、应用程序控制和应用程序沙箱化、企业移动性管理(EMM)(通常在并行非集成产品中)、内存保护、应用程序代码的行为监控、端点检测和修复技术全磁盘和文件加密，也称为移动数据保护;端点数据丢失预防(DLP)  
  
CWPP

|

Cloud Workload Protection
Platforms：云工作保护平台；面向多云/混合云环境，大规模分布式部署，安全防护能力对云工作负载（虚机和容器）始终跟随的产品形态。为信息安全负责人提供了一种集成方式，通过统一管理平台保护这些工作负载，并提供了一种无论工作负载运行在哪些基础设施上，都能表达安全策略的方法。  
  
UES

|

Unified Endpoint Security：统一端点安全；由IT组织内部需求将所有安全事件在同一个安全管控中心呈现。  
  
UEM

|

Unified Endpoint Management：统一端点管理；超越管理pc和移动设备，提供更深入的端点分析和身份和访问管理集成  
  
XDR

|

Extended Detection and Response：扩展威胁检测；为特定供应商的威胁检测和事件响应工具，它将多个安全产品统一为一个安全操作系统  
  
MDR

|

Managed Detection and
Response：运营检测与响应；为那些希望改善威胁检测、事件响应和持续监控功能，但自身缺乏专业知识或资源的购买者提供服务  
  
## 端点相关标准

列了一些标准不知道全不全

![1671786468_63a56fe48ccc0372fdb0f.png!small](https://image.3001.net/images/20221223/1671786468_63a56fe48ccc0372fdb0f.png!small)

  

  


**作者：启明星辰ADLab  
原文链接：<https://mp.weixin.qq.com/s/ilColY9FgOrKAzKepmTL2A>**

# 1\. 概述

《中华人民共和国数据安全法》于今日起（2021年9月1日）正式施行，这是一部数据领域的基础性法律，也是国家安全领域的一部重要法律。数字化改革推动着国家生产模式的变革，随着经济数字化、政府数字化、企业数字化的建设，数据已经成为我国政府和企业最为核心的资产之一。而针对这些核心数据资产的网络攻击却逐年递增，除了越来越频繁的数据泄露安全事件外，日益猖獗的勒索攻击是数据安全面临的最为严重且危险的威胁，其具有破坏性大、匿名性高、恢复难等特点。一旦数据资产遭到攻击，除了大量宝贵的数据被破坏外，还会导致工厂停工停产（如：富士康勒索攻击导致停工的事件），甚至会威胁到国家安全（如：燃油管道公司Colonial
Pipeline勒索攻击事件）。

目前勒索组织普遍利用漏洞或者人工渗透的手段进入企业/组织内部系统，并在其中植入勒索病毒，并利用勒索病毒对其企业的重要数据资产进行加密然后实施赎金勒索。仅今年以来，就出现了多起重大的勒索病毒攻击事件。5月份，美国最大的燃油管道公司Colonial
Pipeline遭遇勒索病毒攻击，从而导致美国东部17个州和首都所在的华盛顿特区宣布进入紧急状态；
7月份，美国IT管理软件制造商Kaseya受到供应链攻击，黑客利用其软件中存在的漏洞向其客户发送勒索软件，超过1500家企业受到勒索攻击影响。

随着市场和技术的变革，勒索组织也在不断寻求新的攻击目标和攻击手段以获取更丰厚的赎金。据调查发现，自去年开始，勒索组织将目标扩展到了VMware的企业产品vSphere中并且对相应勒索软件进行针对性升级以适配针对VMware虚拟机的勒索。到目前为止，多家使用vSphere的企业已经遭到勒索，由于使用vSphere的企业需要在VMware
ESX/ESXi主机上部署多台虚拟机以满足日常的服务器或数据库需求，勒索组织只要设法登录到企业的VMware
ESX/ESXi主机，就能部署勒索软件对主机上的多台虚拟机源文件进行加密实施勒索。与以往传统的勒索攻击不同，以往的勒索攻击仅仅是针对某台或数台服务器中的部分重要数据加密，而系统依旧可以正常运行；而针对vSphere的勒索攻击可直接加密VMware
ESX/ESXi主机中的所有的虚拟机源文件，这将直接导致数台工作服务器或数据库服务器无法正常运行，使企业/组织的主要业务中断甚至系统瘫痪，这对企业/组织来说将是致命的打击。

勒索攻击已经成为各大企业/组织的重要网络安全威胁来源，这种新流行的针对vSphere的勒索攻击将带来比以往的勒索攻击更大的威胁。本文对“针对VMware
vSphere的勒索攻击”进行了全面地分析，通过结合技术背景和相关事件活动分析了勒索组织将攻击目标扩展到VMware
vSphere的原因，并且根据相关攻击样本的分析揭露了此类勒索攻击的勒索流程，同时根据相关材料为广大企业/组织提供了相关的防御建议。

# 2\. 攻击目标：vSphere

VMware
vSphere（简称vSphere）是VMware旗下的一整套云计算基础架构虚拟化平台，自发布更新以来在全球已经拥有超过250000客户，其客户包括政府、军队、医疗、能源、交通、教育等在内的基础设施领域，如图1所示；同时，谷歌云、阿里云、亚马逊云等云服务提供厂商均对客户提供完整的vSphere虚拟化服务，相关市场也同样庞大，如图2所示。拥有如此庞大的市场，vSphere被勒索组织盯上也不足为奇，但是其客户几乎涵盖所有领域，一旦产品出现漏洞被攻击者利用导致主机被勒索病毒攻击，不仅将造成财产损失，更有可能直接威胁国家安全。

![img](https://images.seebug.org/content/images/2021/09/53a18090-a77e-4eaa-9e74-4c0f04ebc61e.png-w331s)
图1.vSphere的客户领域分布

![](https://images.seebug.org/content/images/2021/09/575893f5-5bc6-424c-8b13-d1e51662b5c2.png-w331s)
![](https://images.seebug.org/content/images/2021/09/19e69b13-905b-4e1c-a5a6-3e04bd1a4c06.png-w331s)
图2.云服务商提供VMware服务示例

VMware
ESX/ESXi（简称ESX/ESXi）是vSphere的核心组件之一。在vSphere中，ESX/ESXi是一个虚拟机管理程序，用于创建、运行和管理虚拟机进程的中间软件层，运行在基础物理服务器和操作系统之间，并且允许多个操作系统共享主机硬件。其实，ESX/ESXi并不依赖其它操作系统，而是直接安装在物理设备上，然后以ISO
的形式提供服务；用户直接在ESX/ESXi中创建、运行和管理自己的虚拟机，如图3所示。

在实际场景中，企业为了提高性能和成本效益同时实现简化数据中心和方便大规模管理，往往会在一台ESX/ESXi服务器中部署数台甚至数十台虚拟机作为日常的工作服务主机或者数据库。所以，ESX/ESXi主机中会保存着与它在同一物理主机上的其他虚拟机的源文件以便对这些虚拟机进行管理，它就好比存放着数台服务器的机房，如果机房被人劫持，将对一个企业或组织造成难以估量的损失，这也是ESX/ESXi主机会成为勒索组织攻击目标的主要原因之一；另一个原因则是，ESX/ESXi上部署的服务器/数据库可能需要向客户提供服务，这也使得攻击者有机会直接从网络接触到VMware
ESX/ESXi主机，为攻击者提供了入侵的可能性。VMware公司当然也非常清楚其产品安全的重要性，vSphere 5.0
之前的版本中均采用ESX体系结构来实现对虚拟机的管理，ESX是依赖于Linux的控制台操作系统 (COS)
来实现可维护性和基于代理的合作伙伴集成的，而Linux作为开源系统，与Linux相关的漏洞在各大安全社区和地下产业中层出不穷，这将VMware
ESX架构置于一个高风险处境；为了提高基础架构的安全性，vSphere 5.0之后的版本中则采用了独立于操纵系统的新 ESXi
体系结构，并且在自己研发的核心 VMkernel 中实现了必备的虚拟机管理功能，这也就规避了与通用操作系统相关的安全漏洞引发的安全风险。

![img](https://images.seebug.org/content/images/2021/09/593711ae-c69f-4664-ab31-39fbf403ade7.png-w331s)
图3. VMware ESX/ ESXi 工作结构

VMware vCenter Server（简称vCenter
Server）是vSphere的另外一个核心组件，它是一个可以帮助用户管理多个VMware虚拟化平台的软件，需要单独安装在一台服务器中。在vSphere中，用户可以将多个ESX/ESXi
主机添加到vCenter Server 管理平台中，然后通过vCenter
Server管理ESX/ESXi主机和其中创建的所有虚拟机，整个工作结构如图4所示。虽然目前发现的勒索软件针对的是ESX/ESXi主机，但vCenter
Server可以直接管理ESX/ESXi多台主机。如果vCenter
Server存在漏洞被攻击者利用，那么就无疑将数台ESX/ESXi主机的大门向攻击者敞开，攻击者可以肆意在ESX/ESXi中部署勒索软件，其后果的严重性可想而知。

![](https://images.seebug.org/content/images/2021/09/6774318a-afd2-4a72-8a89-1947e306977b.png-w331s)
图4. vCenter Server 工作结构

# 3\. 针对vSphere勒索的相关活动

病毒勒索作为近年来流行的网络攻击手段，逐渐获得黑客团伙青睐，越来越多的勒索组织出现在大众视野，各大病毒勒索事件也逐渐占据了重大网络攻击事件的头版头条。近几年，勒索攻击事件层出不穷，对受害企业/组织造成重大财产损失，勒索病毒已经成为各政府部门、组织和企业需要面临的重要网络危害之一。自去年开始，勒索组织逐渐开始把目标延伸到VMware
vSphere平台上，通过对其中ESX/ESXi服务器上的数台虚拟机系统文件进行加密从而向受害组织/企业勒索高额的赎金。去年7月，Sprite
Spider勒索组织就开始对其勒索软件进行升级，使其在检测到ESXi主机后部署RansomEXX恶意程序试图窃取登录凭证向vCenter进行身份认证；同样对勒索软件进行ESX/ESXi针对性升级的还有勒索组织carbon
spider、BabukLocker、REvil和BlackMatter。自去年开始，针对VMware虚拟机的勒索病毒攻击事件也开始频发，去年11月巴西高等法院（STJ）受到大规模
RansomExx 勒索软件攻击，超过1000台虚拟机文件被加密，此次事件与7月份进行VMware ESX/ESXi软件升级的Sprite
Spider勒索组织是否有关联，我们无从得知；不仅国外用户遭遇了针对VMware
ESX/ESXi的勒索攻击，国内用户同样也遭遇了此类攻击，在今年3月，国内某公司运维人员发现公司内部VMware
ESXi主机上大量虚拟机文件被加密，我们整理的相关的事件时间线如图5。

![](https://images.seebug.org/content/images/2021/09/e9956dce-ef26-46df-aebe-986f6e9ccf89.png-w331s) 图5. 勒索病毒针对vSphere相关事件时间线

从去年开始，IABs团队逐渐与勒索病毒一起进入公众的视野。IABs团队作为网络攻击地下产业的长期活跃参与者，通过在各大论坛出售主机权限来获取利益，它们将受害者主机的root权限出售给其他网络攻击从业者，由其他网络攻击者开展下一步的攻击活动，IABs团队并不直接参与攻击，这也减少了它们被其他执法机构追踪的风险。在以往的勒索攻击中，我们无法确定勒索组织是否是从IABs团队手中购买受害者主机权限，勒索组织与IABs团队合作这种模式可能早已出现，但是这种合作模式正在逐渐被各个勒索组织采用：据消息称，美国最大燃油管道勒索事件中的主角DarkSide在勒索美国石油管道运营商Colonial
Pipeline之前就曾在地下论坛发文寻找能够让其接触到市值4亿美元公司的IABs合作，如图6，美国燃油管道勒索事件是否有IABs团队参与，我们无从考证；另外，在地下论坛中，我们也观察到有多个IABs正在寻求勒索团队合作并出售vCenter/ESXi的Root权限，如图7。

![](https://images.seebug.org/content/images/2021/09/2f49398d-00b7-43bb-9576-878ba550bce6.png-w331s)
图6. DarkSide寻求与IABs团队合作
![](https://images.seebug.org/content/images/2021/09/35d6363d-17a7-4263-9c66-054a2b8a1d59.png-w331s)
图7. IABs团队寻求与勒索组织合作

# 4\. 针对vSphere勒索的原因分析

众多勒索组织开始将目标延伸到vSphere平台上，无非是为了加密更多更重要的数据以勒索更高额的赎金。针对vSphere平台的勒索攻击，能够使勒索组织像控制一间企业服务器的机房一样对数台服务器进行控制，攻击者对这些虚拟机的源文件进行加密，可能直接造成数据库被加密、对外提供服务中断甚至公司系统瘫痪，勒索组织往往开出更高额的赎金。如此釜底抽薪的勒索方式，让受害者企业/组织短时间难以应付，极大地增加了勒索攻击的成功率和收益。其实，随着互联网技术的革新，勒索组织一直在不断寻找新的攻击目标和攻击手段，勒索组织做出
“针对vSphere平台攻击” 的这种改变并非偶然，结合相关资料，我们将在本章对勒索组织的这种改变进行一个原因分析。

**背景条件：**
随着互联网技术的快速更新，网络用户量剧增，各个政府部门、组织和企业对计算资源和存储资源的需求骤增；云计算和虚拟技术的兴起让各大云服务提供商和虚拟化技术公司为各个政府部门、组织和企业提供了定制化资源服务和虚拟化解决方案以满足日常资源需求。VMware作为云服务和虚拟化领域的领头企业，其客户几乎涵盖所有领域；除此之外，各大云服务提供商也为其客户提供间接的VMware虚拟化服务，从图8
“2020年服务器虚拟化市场分布” 中可以看出，VMware已经成为虚拟化市场的绝对霸主。针对VMware
vSphere进行勒索可以拥有众多勒索对象，同时能够通过虚拟化平台vSphere控制企业/组织的大量数字资产，极大地提高了勒索的收益和成功率。

![](https://images.seebug.org/content/images/2021/09/1001b166-1dc3-4aee-ab13-de24e17b5d12.png-w331s) 图8. 2020年服务器虚拟化解决方案的业务市场分布（来源：spiceworks）

**技术条件：** 2019年底和2020年，VMware分别发布安全通告修复了多个产品漏洞，其中VMware
ESXi的两个漏洞CVE-2019-5544和CVE-2020-3992将导致VMware
ESXi服务器上的远程代码执行，VMware已经对这两个漏洞进行了评估，并定级为严重，CVSSv3 评分 9.8。这两个漏洞将影响多个版本的VMware
vSphere用户，随后VMware提供修复补丁，但仍有大批客户因为各种原因并未对其使用的ESX/ESXi进行补丁，这为攻击者提供了便捷的入侵VMware
ESX/ESXi主机的方法和手段。

**外部条件：** 自2020年起，IABs也将其目标扩展到了VMware
vSphere平台上。对大部分勒索组织来说，与IABs合作是一项共赢的选择,因为从IABs手上购买ESX/ESXi主机权限的价格也仅仅只是赎金的极小部分，通过这种方式，他们能够省去大量的人力、时间、资源去获取ESX/ESXi主机的Root权限，直接通过购买的主机Root权限进行受害者主机登录，然后开始部署勒索软件进行勒索。同时，我们观察到有IABs（Initial
access
brokers）开始在地下黑客论坛上以250美金到500美金之间价格出售ESX/ESXi的Root权限，并展示出更多关于受害主机的信息来吸引客户购买，比如地区信息、权限信息、CPU信息、硬盘信息等，如图9所示，国内某用户的VMware
ESX主机的Root权限在地下黑客论坛被出售。

![](https://images.seebug.org/content/images/2021/09/0bfce33e-4f0a-4aff-a2cf-d0ecb4687f33.png-w331s)
图9. IABs在地下论坛上售卖ESX权限

# 5\. 针对vSphere的勒索样本分析

自去年开始，各大勒索组织开始发布针对VMware
vSphere虚拟平台版本的勒索程序，已经有多家企业/组织遭到攻击并且损失惨重。在本小节中，我们将以ADLab对勒索家族的持续研究为基础，结合部分国外安全厂商对此类攻击活动的披露来对部分勒索组织的样本进行分析，同时结合实际攻击案例对此类攻击的攻击流程进行了总结。如图10，在实际场景中，ESX/ESXi主机上会部署多台虚拟机对普通用户提供基本服务，如果配置不当，普通用户能通过网络能访问ESX/ESXi主机，这就会给黑客提供可乘之机；通常情况下，黑客首先会在地下论坛中寻求指定版本的ESX/ESXi漏洞利用程序或root登录权限，当获取到漏洞利用程序或root登录权限后，黑客就能直接入侵ESX/ESXi主机并且在其中部署勒索软件对其中的虚拟机进行加密并勒索赎金。从图中可以看出，如果勒索攻击对象是云服务提供商/虚拟服务提供商的ESX/ESXi主机，那么该提供商的众多客户都将受到影响，大面积的企业用户主机将遭到勒索病毒感染，这将带来与今年美国IT管理软件制造商Kaseya遭到的供应链式勒索攻击相似的结果，而Kaseya的勒索攻击已经感染了超过100万个系统，超过1500家企业受到影响。

![](https://images.seebug.org/content/images/2021/09/23b3b1e9-4cb9-4fc1-bdf5-c2f69544958c.png-w331s)
图10. 针对vSphere虚拟平台的勒索攻击场景

接下来，我们将对部分勒索组织的样本进行详细技术分析，通过横向比对，可以总结出这些针对VMware
vSphere虚拟平台勒索程序的执行特点：通常情况下，勒索软件首先会使用ESX/ESXi的esxcli指令查找虚拟机进程；然后，恶意程序会使用esxcli指令关闭虚拟机，这一步通常是为了防止对虚拟机文件进行加密时对虚拟机原文件造成破坏，从而导致加密失败；接下来，恶意程序将在对指定路径进行虚拟机相关文件搜索（通常包含虚拟机虚拟磁盘文件vmdk、虚拟机虚拟内存文件vmem、虚拟机页交换文件vswp，日志文件log、虚拟机快照文件vmsn等）；最后，恶意程序将对搜索到的虚拟机相关文件进行加密，同时告知受害者缴纳赎金。

## 5.1 DarkSide

DarkSide勒索软件最早于2020年8月被发现，是一支非常活跃的新兴勒索团伙。DarkSide组织自2020年8月开始频繁活动，并在今年5月攻击了美国最大的燃油管道公司Colonial
Pipeline，导致美国东部沿海主要城市输送油气的管道系统被迫下线，17个州和首都所在的华盛顿特区宣布进入紧急状态，引起了巨大的轰动和全球的关注。最终，Colonial
Pipeline支付了近75比特币（约合近500万美元）才使数据得以恢复，运输工作正常运行。同时我们也发现，DarkSide在去年就已经具备攻击ESXi的功能。

#### 样本技术分析

为了更好地加密虚拟机，DarkSide使用了许多ESXi上独有的esxcli命令，如在加密虚拟机前会使用esxcli命令来遍历出ESXi上正在运行的虚拟机。

命令: `esxcli --format-param=fields=="WorldID,DisplayName” vm process list`

![](https://images.seebug.org/content/images/2021/09/522d4c18-b3cf-47a7-acf4-7c5679188828.png-w331s)
图11. DarkSide使用esxcli命令遍历正在运行的虚拟机

并且使用esxli命令强制关闭正在运行的虚拟机，这么做的目的就是为了避免虚拟机文件在加密的时候遭到破坏。

命令：`esxcli vm process kill --type= force --world-id= <WorldNumber>`

![](https://images.seebug.org/content/images/2021/09/1120bb3f-d7c7-4ddd-a344-75fdfc259b99.png-w331s)
图12. DarkSide使用esxcli命令强制关闭正在运行的虚拟机

除了以上命令，在DarkSide还用了许多esxcli命令，具体如下表所示：

**命令** | **含义**  
---|---  
**esxcli --formatter=csv --format-param=fields== "Device,DevfsPath” storage
core device list** | 列出当前在存储中注册的设备的Devfs路径  
**esxcli --formatter=csv storage filesystem list** | 列出所有文件系统信息  
**esxcli vsan debug vmdk list** | 列出所有vSan中VMDK文件的信息  
**esxcli --format-param=fields== "Type,ObjectUUID,Configuration” vsan debug
object list** | 列出vSAN对象的UUID  
  
为了能够快速的加密虚拟机文件，DarkSide设置加密路径起点为ESXi主机上虚拟机文件默认存放路径："/vmfs/volumes"。

![](https://images.seebug.org/content/images/2021/09/6f1b99f7-a304-4c33-a6af-05c29b8c7b09.png-w331s)
图13. DarkSide加密起始路径

DarkSide通过遍历文件，并且判断文件后缀是否为vmdk（虚拟机虚拟磁盘文件），vmem（虚拟机虚拟内存文文件），vswp（虚拟机页交换文件），log（日志文件），vmsn（虚拟机快照文件）来决定是否进行加密，加密成功后会在原文件后缀后加入darkside。

![](https://images.seebug.org/content/images/2021/09/a07e60e4-425c-40fc-88c7-87906d122dfc.png-w331s)
图14. DarkSide针对的虚拟机文件后缀

在加密文件之前，为了避免加密一些无关重要的文件，DarkSide会对文件大小进行检查，判断是否小于配置文件中文件大小的最小值。

![](https://images.seebug.org/content/images/2021/09/26e1cc51-7ef8-4ed6-b4ce-1c930839058e.png-w331s)
图15. DarkSide对文件大小进行判断

最后，DarkSide会留下勒索信警告受害者，并且在信中留下还原数据的方式以及交赎金的地址

![](https://images.seebug.org/content/images/2021/09/3c41862a-8221-44a0-b2c2-cdcbd913d89c.png-w331s)
图16. DarkSide的勒索信

## 5.2 REvil

REvil也被称为Sodinokibi，是一个臭名昭著的勒索团伙，其攻击最早可以追溯到2019年4月。该勒索团伙作案频繁，并曾攻击过多个大型公司如美国领先的视频传输提供商SeaChange
International、著名硬件和电子公司宏基公司、全球再生能源巨擘Invenergy公司、全球最大肉类供应商JBS公司。而在今年7月美国远程IT管理软件厂商Kaseya也遭受到了REvil的攻击，导致全球超过10000家的Kaseya客户，其中包括50%以上的全球100强IT管理服务提供商及各大龙头受到勒索攻击的风险。据称此次攻击是REvil有史以来规模最大的一次攻击，据其官网宣称，他们已经锁定了超过100万个系统，并向Kaseya索取70000000美元的赎金。而在今年5月，我们观察到REvil运营商在地下黑客论坛上发布了针对Vmware
ESXi的Linux版本。

#### 样本技术分析

为了避免虚拟机相关的文件受到不必要的损坏，REvil在加密前也同样会先关闭ESXi上正在运行的虚拟机，但与DarkSide不同的是REvil先使用pkill
-9的命令关闭与虚拟机相关的进程。

命令：`pkill -9 vmx-*`

![](https://images.seebug.org/content/images/2021/09/caebb94b-04fc-4a91-a773-08015acb6ca0.png-w331s)
图17. REvil使用pkill命令关闭与虚拟机相关的进程

然后REvil使用excli命令遍历出所有正在运行的ESXi虚拟机并且关闭它们，使用此命令会关闭存储在 /vmmfs/ 文件夹中的虚拟机磁盘 (VMDK)
文件，防止REvil对这些文件进行加密时因为被 ESXi 锁定而导致加密失败。

命令：`esxcli --formatter=csv --format-param=fields=="WorldID,DisplayName" vm
process list | awk -F "\"*,\"*" '{system("esxcli vm process kill --type=force
--world-id=" $1)}`

![](https://images.seebug.org/content/images/2021/09/88b08ba4-47e3-481b-8857-522f7f2c3110.png-w331s)
图18. REvil使用esxcli命令关闭虚拟机

与其他针对ESXi的勒索软件不同的是，REvil不会对虚拟机文件的后缀进行判断，而是对加密路径下所有的文件都进行加密，并判断该文件是否已经被加密了和是否具有RWX权限或者RW权限（如果具有这些权限，则这些文件是被系统保护的）来决定是否进行加密。

![](https://images.seebug.org/content/images/2021/09/bd84ae30-0d02-4807-bf41-f9850ec1996c.png-w331s)
图19. REvil加密文件过程

最后，REvil留下勒索信警告受害者并且在信中留下还原数据的方式以及交赎金的地址。

![](https://images.seebug.org/content/images/2021/09/cbcef602-4170-4b8f-89e5-ed8203e8777e.png-w331s)
图20. REvil的勒索信

## 5.3 HelloKitty

HelloKitty勒索软件攻击活动最早可以追溯到2020年，主要针对Windows系统。其在2021年2月攻击了CD Projekt
Red公司并声称窃取了该公司出品的“Cyberpunk 2077”、“Witcher 3”、“Gwent
”和其他游戏的源代码。而在今年7月，我们观察到该木马的Linux变体开始针对Vmware
ESXi进行攻击。其中，被攻击的目标包括意大利和荷兰的制药公司、一家德国制造商、一家澳大利亚提供工业自动化解决方案的公司以及美国一家医疗办公室和股票经纪人。在赎金方面，攻击者会因攻击目标公司的规模不同，而要求支付不同金额的赎金，其勒索的赎金最高可达1000万美金。

#### 样本技术分析

HelloKitty勒索软件首先会使用esxcli命令来遍历出当前受感染机器上正在运行的虚拟机进程，并尝试关闭这些虚拟机。为了避免虚拟机相关的文件遭到不必要的损坏，该病毒在加密文件前会先将虚拟机关闭。

该勒索软件首次关闭虚拟机，会使用软终止来结束该进程。

命令：`esxcli vm process kill -t=soft -w=%d`

如果仍有虚拟机正在运行，该病毒将会使用硬终止来结束该进程。

命令：`esxcli vm process kill -t=hard -w=%d`

如果还有虚拟机未被关闭，则会使用强制终止来结束该进程。

命令：`esxcli vm process kill -t=force -w=%d`

![](https://images.seebug.org/content/images/2021/09/b36b8689-c5ec-46b0-9e9f-3d4a126675c9.png-w331s)
图21. HelloKitty勒索软件使用esxcli命令结束虚拟机进程

随后，HelloKitty病毒会遍历文件，并判断文件后缀是否为.vmdk（虚拟机虚拟磁盘文件）、.vmx（虚拟机配置文件）、.vmsd（虚拟机快照元素）、.vmsn（虚拟机快照文件）来加密与虚拟机相关的文件。

![](https://images.seebug.org/content/images/2021/09/71f22dbe-187c-427a-a546-db0aa8c3d221.png-w331s)
图22. HelloKitty勒索软件加密文件并对文件后缀进行判断

最后，每个加密文件都有一个相应的文件，扩展名为.README_TO_RESTORE，其中包含赎金记录。文本内容如下图所示。

![](https://images.seebug.org/content/images/2021/09/c650d23f-4e90-45b5-8756-04c51a24feb8.png-w331s)
图23. 赎金文本内容

## 5.4 BlackMatter

2021年7月，一个名为BlackMatter的新勒索软件组织正在购买企业网络的访问权限，同时声称其项目已将REvil和DarkSide的最佳功能融入其中。BlackMatter还表示，他们的勒索软件适用于多种不同的操作系统版本和架构，并以多种格式提供。包括支持安全模式的Windows变体（Windows
Server2003+x86/x64和Windows7+x86/x64）和支持NAS的Linux变体（ESXI5+、Ubuntu、Debian和CenOs），且这些变体在相同系统上均已测试成功。

#### 样本技术分析

BlackMatter在ESXI服务器上运行时，其首先使用esxcli命令列出所有正在运行的VMware虚拟机。

![](https://images.seebug.org/content/images/2021/09/4611b5c1-ffc0-469a-a4b3-c06b039f6105.png-w331s)
图24. BlackMatter使用esxcli命令列出所有正在运行的VMware虚拟机

再将正在运行的VMware虚拟机全部强行关闭。之所以这样做，是由于在加密文件之前如果没有正确的关闭虚拟机磁盘（VMDK）文件，则会导致数据的损坏。

![](https://images.seebug.org/content/images/2021/09/480d596b-925b-4292-8b63-6a991484200e.png-w331s)
图25. BlackMatter强制关闭ESXi上正在运行的VM虚拟机

接着，BlackMatter会获取当前系统所有正在运行的进程，并将这些进程强制结束。

![](https://images.seebug.org/content/images/2021/09/37d858e7-81c8-4d5e-acb4-be7ad71707ea.png-w331s)
图26. BlackMatter强制关闭所有正在运行的进程

同时，其会使用esxcli network firewall set –enabled 命令禁用ESXI主机的防火墙。

![](https://images.seebug.org/content/images/2021/09/8dbef233-f94d-4aae-979f-ef258177c31f.png-w331s)
图27. BlackMatter使用excli命令禁用防火墙

接下来，判断文件系统，遍历其配置文件里（或给定的参数）所指定的路径目录下的所有文件。

![](https://images.seebug.org/content/images/2021/09/3b9f877e-3f64-46d4-95c4-34402138c11c.png-w331s)
图28. BlackMatter遍历指定路径下的所有文件

最后，并针对后缀名为vmdk（虚拟磁盘文件）、vmem、vswp、log等文件进行加密操作，生成并释放勒索信。

![](https://images.seebug.org/content/images/2021/09/fc6cfe60-ce13-444d-903f-62073aa4d31a.png-w331s)
图29. BlackMatter加密文件的后缀

![](https://images.seebug.org/content/images/2021/09/6eda4cdc-69c3-40f8-a075-8c9593afc4ea.png-w331s)
图30. BlackMatter勒索文本信息

# 6\. 总结与建议

针对虚拟化平台VMware vSphere的勒索攻击成为勒索组织的新型攻击方向，本文从多个角度对此类攻击进行了综合分析。针对虚拟化平台VMware
vSphere的勒索攻击可能会更加频繁：首先，攻击者对虚拟机管理平台的ESX/ESXi主机进行感染后可以对其中的数台虚拟机源文件进行加密，将直接影响受害企业/组织的多台应用服务器/数据库，这种方式控制了更加重要的企业/组织数字资产，能够勒索更高额的赎金并且大大提高成功率，这正是勒索组织的核心目的；其次，越来越多的黑客将目标转向了VMware
vSphere，相关的安全漏洞频频被发现，但许多客户由于各种原因限制并未能及时补丁，这也为勒索组织入侵到企业的ESX/ESXi主机提供了便利；另外，IABs团队在地下论坛中针对VMware
vSphere的活动也越加频繁，同时它们也在积极寻求与勒索组织进行合作，IABs团队能够提供专业ESX/ESXi主机的入侵服务，它与勒索组织的合作将会把针对vSphere的勒索攻击推上新一轮的高潮。

可以看出，随着互联网技术的不断革新和市场的变化，勒索组织也在不断扩展它们的攻击方向和寻求更有效的攻击手法，以便在勒索攻击中获取更高额的赎金同时大幅提高勒索的成功率。VMware
vSphere只是众多虚拟化平台的其中一个，只是由于它的市场庞大，成为了攻击者的首选目标；随着时间的推移，其他虚拟化平台如：Microsoft、Oracle和Red
Hat等很可能会成为攻击者的新目标，各大企业/组织应当注意提前做好针对性防御。针对vSphere虚拟平台的勒索攻击将对受害者企业带来难以估量的损失，我们将结合本文的分析和相关资料向vSphere用户提出下面几条针对性防御建议：

  * 建议使用 TPM 2.0 芯片进行vSphere进行安全配置。
  * 在物理服务器上启用UEFI安全启动功能，通过确保在引导中加载的所有代码都经过数字签名且未被篡改，从而加强操作系统的安全性。
  * 禁止在ESX/ESXi 主机上执行自定义代码，保证ESX/ESXi主机拒绝执行任何未通过认证合作伙伴签名的 VIB 包安装的代码。
  * 当vSphere平台相关的产品存在安全补丁发布时，积极参与系统及相关的虚拟化平台组件（vCenter服务器、ESX/ESXi主机、VMware工具等）的更新。
  * 对虚拟机平台的管理账户使用高强度密码。
  * 在内部网络中进行网络区域划分，将对外服务的主机和仅内部访问的主机进行分开管理，并且为虚拟平台管理员提供专用的vCenter服务器和ESX/ESXi管理接口以及专用的工作站。
  * 配置集中式的记录日志，防止管理系统配置和环境遭到篡改。
  * 尽可能高频率地进行系统备份，以便在遭到勒索攻击后能尽快地实现系统恢复。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1707/>


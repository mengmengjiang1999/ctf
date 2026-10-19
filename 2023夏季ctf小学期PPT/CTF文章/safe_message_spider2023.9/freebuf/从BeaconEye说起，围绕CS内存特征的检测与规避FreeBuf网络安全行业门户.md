## **背景**

2021年8月BeaconEye项目发布，这是一个基于CobaltStrike内存特征进行检测的威胁狩猎工具。BeaconEye具有优秀的检出率与检测效率，使大多数已有规避技术无效化，在网络安全圈内掀起了关于CS内存攻防的新一轮讨论热潮。

## 为何BeaconEye切中要害

BeaconEye能够扫描运行中的程序或 Minidump中的程序，识别出被Beacon注入的进程，并以上帝视角窥视其内部行为。

· 提取Beacon配置

· 获取执行命令的返回结果

· 检测使用了sleep_mask功能的Beacon

BeaconEye利用对解密后配置特征值进行匹配，简单的几行规则便将无数隐匿手段斩于马下，达到这种令人瞠目结舌的效果并非一日之功。能在攻击技术与检测技术都高度内卷的今天一枝独秀则源于两点：

1\. 将Beacon Config作为特征匹配对象

2\. 将堆作为内存扫描的对象

## 阿喀琉斯之踵-Beacon Config

Beacon
Config存储了Beacon运行时的配置信息包含了C2配置，通讯参数，内存隐匿方式等重要信息。这些配置数据以典型的TLV格式来组织，偏移与内容相对固定，因而这些敏感信息非常易于根据特征被提取与解析。

![1639624968_61bab108d2c5be071d458.png!small?1639624973569](https://image.3001.net/images/20211216/1639624968_61bab108d2c5be071d458.png!small?1639624973569)

使用分析工具从Beacon二进制中提取的配置信息

![1639624978_61bab112ae8f0e1ac2dbe.png!small?1639624983255](https://image.3001.net/images/20211216/1639624978_61bab112ae8f0e1ac2dbe.png!small?1639624983255)

Becon执行流程的两次解密过程

Beacon默认加密存储于加载器中，执行时释放到堆内存空间中。无论何种加密方式，解密后的配置将一直存在，即便开启sleepmask功能也仅会对代码段进行保护。无论采用何种加解密方式，最终Beacon
Config都将裸露于堆内存中，这便是Beacon Config的死门，也是BeaconEye针对堆进行扫描的原因。

![1639625003_61bab12b1fef4bb68d36c.png!small?1639625007922](https://image.3001.net/images/20211216/1639625003_61bab12b1fef4bb68d36c.png!small?1639625007922)

BeaconEye中内置的yara规则

近期Tom Bonner研究在推特披露，Beacon
Config中除了包含诸如域名/IP等关于Teamserver的情报之外，还包含了每个攻击者独一无二的身份水印信息。

![1639625033_61bab1497bdda5c751f06.png!small?1639625038109](https://image.3001.net/images/20211216/1639625033_61bab1497bdda5c751f06.png!small?1639625038109)

CobaltStrike服务端源码中嵌入水印信息的部分

当Teamserver解析c2profile嵌入二进制中时，将从c2profile中读取名为self，记录着Teamserver文件哈希的值。对于大部分使用重编译的方式对CobaltStrike进行破解修改的攻击者来说，这个泄露的文件哈希可能暴露样本归属信息。研究者对一些在野样本中Beacon
Config包含的Teamserver哈希进行了有效的分析聚类，更加精确地对在野攻击利用进行追踪分类。

![1639625052_61bab15c1860c4c2b8cd5.png!small?1639625056689](https://image.3001.net/images/20211216/1639625052_61bab15c1860c4c2b8cd5.png!small?1639625056689)

研究员利用Beacon Config的水印信息进行归因聚类

## 奇招迭出，致盲BeaconEye

从BeaconEye的原理出发，规避扫描无非三种思路：

1\. 规避BeaconEye的内存扫描，让它扫不到自己

2\. 寻找内置yara规则的漏洞，绕过匹配

3\. 彻底修改Beacon配置的数据结构

第三种方法无疑是最治标又治本的，但也是攻击成本最大的方案，接下来要介绍的两种BeaconEye绕过方法皆是前两种思路，以最小代价多快好省地绕过BeaconEye。

 **利用数据类型差异“修改1字节”绕过yara规则**

TeamServer与Becon
DLL中表示Type的数据类型长度不一致，导致其中存在数据Gap，可填充为任意数据绕过yara规则。通过这种方式可以实现所谓的“修改1字节绕过BeaconEye”。

以32位Beacon为例：

在TeamServer的Java代码中使用长度为4 byte的Int类型来表示type，而在Beacon DLL中实际使用的只有前两位
byte。因此下图红框区域的数据可任意填充而在不影响Beacon功能的情况下实现BeaconEye的绕过。

![1639625105_61bab191983366ae4176e.png!small?1639625110282](https://image.3001.net/images/20211216/1639625105_61bab191983366ae4176e.png!small?1639625110282)

 **利用堆遍历算法缺陷躲过内存扫描**

BeaconEye所检测的Beacon
Config数据存在于堆中，因而BeaconEye的有效性非常依赖对堆的扫描。旧版本BeaconEye存在堆块扫描不全的问题，究其根源是使用了NtQueryVirtualMemory函数进行堆的枚举。使用该函数获得的堆大小存在天然的缺陷：只会计算属性一致的内存页，而实际上堆段中的内存属性是不同且不连贯的。这导致BeaconEye在获取堆信息时实际只获取了第一个堆段的内容。但是这种问题并不一定会触发，而是有特定的触发条件。

通过调用SymInitialize函数或反复调用HeapAlloc等方式，可手动造成Beacon
配置存在于BeaconEye无法扫描的堆段的情况。但该方法的发现者在披露绕过方式后就向BeaconEye官方提交了正确的堆块遍历方法，官方在接收提交后该方法也将生效。

## 朝花夕拾- Beacon检测技术与对抗发展历程

 **简单有效-可疑内存属性与静态特征**

针对可疑的内存属性进行威胁狩猎是一种常见的思路。在默认情况下Beacon会在RWX（可读可写可执行）权限的内存空间执行，这种敏感的内存属性会使得Beacon存在的内存空间更易被发现。

![1639625131_61bab1abaaeac4fc97c09.png!small?1639625136250](https://image.3001.net/images/20211216/1639625131_61bab1abaaeac4fc97c09.png!small?1639625136250)

未使用C2 Profile下RWX的内存区域中存储的即是完整的明文Beacon。

![1639625144_61bab1b8ab73db238f116.png!small?1639625149372](https://image.3001.net/images/20211216/1639625144_61bab1b8ab73db238f116.png!small?1639625149372)

RWX内存区域的明文Beacon

在明文Beacon中DLL头及命名管道名称字符串等静态特征明显，部分厂商利用这些静态特征进行内存中Beacon的识别扫描。

![1639625166_61bab1ce161ec47506cab.png!small?1639625170673](https://image.3001.net/images/20211216/1639625166_61bab1ce161ec47506cab.png!small?1639625170673)

 **官方救火员-C2 profile改变静态特征**

但通过Malleable C2 profile这一官方提供的定制化配置文件，攻击者可对Beacon的内存属性静态特征等做进一步的定制和隐匿：

· 自定义内存属性 rwx/rx

· 自定义或删除文件头

· 自定义命名管道名称、替换字符串

通过其强大而灵活的特性，C2 profile帮助Beacon成功规避大部分针对内存属性与静态特征的检测，大大增强了Beacon的隐匿能力，增加了检测的成本。

 **固定密钥异或？直接解密提取Beacon配置**

由于某些原因，CobaltStrike在导出Beacon时仅会对其中包含的Beacon配置信息用简单的异或加密进行保护。更致命的是加密密钥是固定的，对3.x版本的CobaltStrike默认是0x69，对4.x版本的CobalStrike默认是0x2e，用户并不能通过C2
Profile等方式对加密方式或密钥进行修改。

![1639625184_61bab1e037b500ec283a5.png!small?1639625188779](https://image.3001.net/images/20211216/1639625184_61bab1e037b500ec283a5.png!small?1639625188779)

用于匹配的固定开始特征

结构相对固定的明文配置的特征在经过异或后的值依然具有明确的特征，可通过简单的特征匹配捕获。

 **自己动手-魔改Beacon Config密钥**

Beacon
Config的默认密钥可以通过手动patch的方式进行修改，虽然较为繁琐，但只要同时对服务端与beacon二进制模板中的异或密钥同时进行修改，便可以逃过利用默认异或密钥来进行特征扫描的工具。

![1639625207_61bab1f714d51eb27169f.png!small?1639625211627](https://image.3001.net/images/20211216/1639625207_61bab1f714d51eb27169f.png!small?1639625211627)

Beacon
Config默认以固定密钥加密的孱弱的加密方式给检测工具提取Beacon配置提供了可乘之机，攻击者仍可通过魔改二进制的手段修改该密钥。但只要加密方式不变，通过爆破异或等方式依然不难提取加密后的配置。

##  **小结**

BeaconEye的检测思路切中CobaltStrike要害，除非彻底变更数据结构，不存在一劳永逸的绕过方法。未来类似BeaconEye将C2框架内的固定数据结构作为检测对象的工具将会更多出现，各种隐匿技术也会相伴而生，将这场拉锯战继续下去。

CS内存检测与对抗技术的发展,显示了攻防双方在博弈中共同成长的路径。由内存特征到Beacon配置，随着理解的加深，攻防阵地越来越接近底层；由C2profile官方定制到动手魔改，社区研究在实战驱使下补全官方未提供的对抗能力。

## 参考

[1]https://blogs.blackberry.com/en/2021/11/all-your-beacon-are-belong-to-us-new-blackberry-book-cracks-code-of-cobalt-strike-threat-actors

[2]https://mp.weixin.qq.com/s/6kRg0_BmXYExy4_-pEAcLw

[3]https://mp.weixin.qq.com/s/_gSPWVb1b-xuvhU6ynmw0Q


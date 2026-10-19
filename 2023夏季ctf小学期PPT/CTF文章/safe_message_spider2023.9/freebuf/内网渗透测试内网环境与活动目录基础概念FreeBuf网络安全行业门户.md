![20210721000627.png](https://image.3001.net/images/20210806/1628258038_610d3ef6d7395c5786d4d.png!small)

## 前言

这又是一个关于域内基础概念与原理的系列。如果你熟悉内网渗透，那么应该都对域环境、Active Directory、LDAP、Naming
Context、域用户、域用户组、访问控制、组策略这些老生常谈的词汇有所了解。但是如果你对这些概念与原理一知半解的话，那么本系列的文章你一定不能错过。

本系列将包含以下几篇文章：

> 《内网渗透测试：内网环境与活动目录基础概念》
>
> 《内网渗透测试：活动目录 Active Directory 的查询》
>
> 《内网渗透测试：域用户组及域内权限划分》
>
> 《内网渗透测试：OU 组织单位》
>
> 《内网渗透测试：域用户和机器用户》
>
> 《内网渗透测试：域内权限访问控制》
>
> 《内网渗透测试：Windows 令牌窃取》
>
> 《内网渗透测试：Windows 组策略讲解》
>
> 《内网渗透测试：Windows 组策略后门》

在本篇文章中，我们主要介绍一些基本概念，为后续的文章做下铺垫。

在初学内网的时候，经常会遇到工作组、域、域控制器、父域、子域、域树、域森林、活动目录等概念，他们到底是什么，又有何区别呢？

![20210722180831.png](https://image.3001.net/images/20210806/1628258039_610d3ef721a1f211b393d.png!small)

## 工作组

在一个大型的单位中，成百上千台计算机相互连接组成局域网，为了避免造成网络混乱，引入了 **工作组** （Work
Group）这个概念。工作组是最常见的一种资源管理模式，默认情况下计算机都是采用工作组方式进行资源管理的。将不同的计算机按功能或者部门分别列入不同的工作组，以方便管理。例如技术部的计算机都列入“技术部”工作组、行政部的计算机都列入“行政部”工作组。要想访问某个部门的资源，只要在“网络”里双击该部门的工作组名，就可以看到该部门的所有计算机了。

工作组资源管理模式适合于网络中计算机不多，对管理要求不严格的情况。大部分中小公司都采取工作组的方式对资源进行权限分配和目录共享。相同组中的不同用户通过对方主机的用户名和密码可以查看对方共享的文件夹，默认共享的是
Users 目录。不同组的不同用户通过对方主机的用户名和密码也可以查看对方共享的文件夹。所以工作组并不存在真正的集中管理作用 ,
工作组里的所有计算机都是对等的 , 也就是没有服务器和客户机之分的。

### 工作组的加入

工作组的加入很简单，右击桌面上的“计算机” —> “属性” —> “更改设置” —>
“更改”，在“计算机名”一栏中键入一个自定义的主机名称，在“工作组”一栏中键入你想加入的工作组名称。单击“确定”按钮后，重新启动计算机，再进入“网络”就可以看到你所加入的工作组成员了。

默认情况下所有计算机都处在名为 WORKGROUP 的工作组中：

![image-20210721011232430](https://image.3001.net/images/20210806/1628258039_610d3ef7749a6b18208f3.png!small)

### 工作组的访问

加入工作组后，别人便可以访问我们的共享资源了，只需打开“文件夹” —>
“网络”，就可以查看到当前所在的工作组中的其他计算机了，当你要访问某台计算机时，点击该计算机图标，然后输入对方主机的用户名和密码即可看到该主机共享的文件夹了。工作组就像一个可以自由进入和退出的社团，方便同组的计算机之间的互相访问。

## 域环境

计算机通过工作组进行分类，使得我们访问资源更加具有层次化。工作组情况下资源可以相当随机和灵活的分布，更方便资源共享，管理员只需要实施相当低级的维护。但是工作组只适用于网络中计算机不多，资产规模较小，对管理要求不严格的情况。当计算机的数量变得越来越多，大型企业中网络规模越来越大，需要统一的管理和集中的身份验证，并且能够给用户提供方便的搜索和使用网络资源的方式时，这种没有集中的统一帐户管理，没有对资源实施更加高效率的集中管理，没有实施工作站的有效配置和安全性严密控制的工作组模式便不再合适了，于是引入了
**域** （Domain）的概念。

 **域**
（Domain）是一个有安全边界的计算机集合。安全边界的意思是，在两个域中，一个域中的用户无法访问另一个域中的资源。相比工作组来说，域的安全管理控制机制更加严格。用户要想访问域内的资源，必须以合法的身份登录域，而用户对域内的资源拥有什么样的权限，还取决于用户在域内的身份。

在域环境中，域管理员可以通过域控制器集中地管理企业中成千上万分布于本地或者异地的计算机和域用户，域用户依次登录就可以访问整个网络资源，由域控制器集中进行身份验证。域环境既可以适用于几十台计算机的小规模网络，也可以用于跨国公司。

在域环境中，由域控制器（Domain
Controller，DC）来管理域内所有的客户端，负责每一台连入的电脑和用户的验证工作，域内主机如果想互相访问首先都得经过它的审核，域控是整个域架构的核心。

### 单域

单域就是一个域环境，在一个地理位置固定，规模较小的公司内，建立一个域就可以满足需要。

![image-20210721014101197](https://image.3001.net/images/20210806/1628258041_610d3ef974a77dee397b9.png!small)

### 父域和子域

在某些企业中，出于管理及其他需求，需要在网络中划分多个域。第一个域称为父域，
各分部的域称为该域的子域。例如，一个大型企业的各个分公司位于不同的地点，如果把不同地点的分公司放在同一个域内，那么它们之间在信息交互上花费的时间就会比较长，占用的带宽也会比较大，此时就需要使用父域及子域。

![image-20210721014859226](https://image.3001.net/images/20210806/1628258041_610d3ef9aa93661d7e711.png!small)

### 域树

域树是多个域通过建立信任关系组成的一个域集合。一个域的域管理员只能管理本域，不能访问 或者管理其他域。如果两个域之
间需要互相访问则需要建立信任关系（Trust
Relation）。域树内的父域与子域，不但可以按照需要互相管理，还可以跨网络分配文件和打印机等设备及资源，从而在不同的域之间实现网络资源的共享与管理、通信及数据传输。

![image-20210721020055273](https://image.3001.net/images/20210806/1628258041_610d3ef9f091bd20cf064.png!small)

### 域森林

域森林是指多个域树通过建立信任关系组成的域树集合。例如，在一个公司兼并场景中，某公司使用域树 abc.com，被兼并的公司本来有自己的域树
xyz.com，域树 xyz.com 无法挂在域树 abc.com 下。所以，域树 abc.com与域树 xyz.com
之间需要通过建立信任关系来构成域森林。通过域树之间的信任关系，不仅可以管理和使用整个域森林中的资源，还可以保留被兼并公司自身原有的特性。

## 域控制器

 **域控制器** （Domain
Controller，DC）是域中的一台用来管理所有客户端主机的服务器计算机，其负责负责每一台连入的电脑和用户的身份与权限验证工作，域内主机如果想互相访问首先都得经过它的审核，可以说是整个域架构的核心。

域控制器上包含了一个活动目录数据库（NTDS.dit），在该数据库中存储着整个域的账户、密码、属于这个域的计算机等各种信息。当计算机连接到这个域时，域控制器会首先鉴别这台计算机是否属于这个域，以及用户使用的登录账号是否存在、密码是否正确，正确后是否有权限访问本资源等。如果以上信息有一项错误，域控制器便会拒绝这个用户通过这台计算机登录，也就不能访问服务器中的资源。

一个域环境可以有多台域控，每一台域控的地位几乎是平等的，他们各自存储着一份相同的活动目录数据库，一台域控瘫痪后另一台域控可以继续工作，以至于不影响域环境的正常运行。当你在任何一台域控制器内添加一个用户账号或其他信息后，此信息默认会同步到其他所有域控的活动目录数据库中。当域中的一台计算机安装了活动目录后，它就成了域控了。

## 活动目录

到这里，你可能已经大致了解活动目录这个概念了。 **活动目录** （Active
Directory，AD）是指域环境中提供目录服务的组件，用于存储例如用户、组、计算机、共享资源、打印机和联系人等各种网络对象的信息。活动目录实现了帮助用户快速、准确地从目录中找到其所需要的信息的目录服务，为企业提供了网络环境的集中式管理机制。

活动目录主要提供以下功能：

> 账号集中管理：所有账号均存储在服务器中，以便执行命令和重置密码等。
>
> 软件集中管理：统一推送软件、安装网络打印机等。利用软件发布策略分发软件，可以让用户自由选择需要安装的软件。
>
> 环境集中管理：统一客户端桌面、IE、TCP/IP协议等设置。
>
> 增强安全性：统一部署杀毒软件和病毒扫描任务、集中管理用户的计算机权限、统一制定用户密码策略等。可以监控网络，对资料进行统管理。
>
> 更可靠，更短的宕机时间：例如，利用活动目录控制用户访问权限，利用群集、负载均衡等技术对文件服务器进行容灾设置。网络更可靠，宕机时间更短。

### Ntds.dit

Ntds.dit
文件是域环境中域控上会有的一个二进制文件，是主要的活动目录数据库，其文件路径为域控的`%SystemRoot%\ntds\ntds.dit`，活动目录始终会访问这个文件，所以文件禁止被读取。Ntds.dit
包括但不限于有关域用户、组和组成员身份和凭据信息、GPP 等信息。它包括域中所有用户的密码哈希值，为了进一步保护密码哈希值，使用存储在 SYSTEM
注册表配置单元中的密钥对这些哈希值进行加密。

而在非域环境也就是在工作组环境中，用户的密码等信息存储在 SAM 文件，想要破解 SAM 文件与 Ntds.dit 文件都需要拥有一个 System
文件。和 SAM 文件一样，Ntds.dit 是默认被 Windows 系统锁定的。

### LDAP

活动目录是一种目录服务数据库，其实现了目录服务，既然有了目录服务数据库，那必然需要有用来访问目录服务数据库的协议。LDAP
协议就是设计用来访问目录服务数据库的协议之一。

LDAP（Lightweight Directory Access Protocol），即轻量目录访问协议。顾名思义，LDAP
是设计用来访问目录服务数据库的一个协议。活动目录就是利用 LDAP 名称路径来描述对象在活动目录内的位置。

目录服务是指帮助用户快速、准确地从目录中找到所需要信息的服务。目录服务数据库也是一种数据库，由目录服务数据库和一套访问协议（如
LDAP）组成。目录服务数据库区别于我们熟知的关系型数据库，其成树状结构组织数据，类似文件目录。目录服务数据库是为查询、浏览和搜索而优化的数据库。为了能够访问目录数据库，必须设计一台能够访问目录服务数据库的协议，LDAP
就是其中实现的一种协议。

![image-20210722173722458](https://image.3001.net/images/20210806/1628258042_610d3efa4eb50dedc2751.png!small)

如上图实例就是一个目录服务数据库，它成树状结构组织数据。下面介绍一些基本概念：

> 目录树：如上图所示，在一个目录服务系统中，整个目录信息集可以表示为一个目录信息树，树中的每个节点是一个条目。
>
> 条目：每个条目就是一条记录，每个条目有自己的唯一可区别的名称（DN）。比如图中的每个圆圈都是一条记录。
>
> DN：DN 即绝对可分辨名称，用于指向一个LDAP对象，其由对象本体开始，向上延伸到域顶级的 DNS 命名空间的一串路径，其中 CN
> 代表通用名（Common Name），OU 自然代表着组织单位，而 DC 代表着域组件（Domain Component）。比如上图中 DC
> 1（DC01）的这个条目，他有一个唯一可区分的名称 DN：`CN=DC01,OU=Domain
> Controllers,DC=whoamianony,DC=org`，类似于文件系统目录中的绝对路径，如果我们类比文件系统的话，可被看作如下文件路径：`org/whoamianony/Domain
> Controllers/DC01`，其中`CN=DC01`代表这个主机一个对象，`OU=Domain Controllers`代表一个 Domain
> Controllers 组织单位，这句话的含义就是 DC01 这个对象处在 whoamianony.org 域的 Domain Controllers
> 组织单元中。
>
> RDN：即相对可分辨名称，即在 DN 中在第一个 OU 或容器之前的部分，他与目录结构无关，比如之前咱们提过的`CN=DC01,OU=Domain
> Controllers,DC=whoamianony,DC=org`，他的 RDN 就是`CN=DC01`。类似于文件目录的相对路径。
>
> 属性：用于描述条目的具体信息。

### Active Directory 的访问

我们可以使用 AD Explorer 工具连接域控来访问活动目录，它可以方便的帮助用户进行浏览 Active Directory
数据库、自定义快速入口、查看对象属性、编辑权限、进行精确搜寻等操作。如下，在域内任意一台主机上，以域用户身份进行连接即可：

![image-20210721130756115](https://image.3001.net/images/20210806/1628258042_610d3efa91b751de77057.png!small)

连接上之后便可以查看域内的各种信息：

![image-20210721130825516](https://image.3001.net/images/20210806/1628258042_610d3efadaeb3b3a2a43d.png!small)

可以看到里面有很多的条目，下面我们对其中的一些概念进行讲解。

### Naming Context

微软将 Active Directory 活动目录划分为若干个分区，这个分区我们称为 Naming Context，简称 NC，每个 Naming
Context 都有其自己的安全边界。

由于 Active Directory 活动目录具有分布式的特性，一个林中可能有若干个域，每个域内可能有若干台域控，每台域控又都有一个独立的 Active
Directory。这个时候如果不将数据隔离到多个分区中的话，则每个域控制器都必须复制林中的所有数据。若隔离为若干个分区之后，就可以有选择性的复制某几个分区。

每一个域都有一个域 Naming Context，不同的域环境有不同的域 Naming Context，其中包含特定域的数据。这个域 Naming
Context 的跟由域的专有名称 DN 表示，比如 whoamianony.org 域的 DN 为`DC=whoamianony,DC=org`。

Active Directory 活动目录预定义了以下三个 Naming Context（下图红框中的部分）：

![image-20210721131715726](https://image.3001.net/images/20210806/1628258043_610d3efb3d3bb0a6f033c.png!small)

 **域目录分区**

域目录分区，即 Domain NC (DomainName
NC)，每一个域各有一个域目录分区，其中存储着与该域有关的对象。每一个域控各自拥有一份域目录分区，它只会被复制到该域内的所有域控中，并不会复制到其他域的域控中。前
Naming Context 图中的`DC=whoamianony,DC=org`就是域目录分区。

我们之前说过域内所有计算机、域用户的信息都存储在 Active Directory 活动目录下，具体来说就是存储在 Active Directory
活动目录的这个域的 Naming Context 里面。下面我们使用 AD Explorer 工具查看域目录分区中的内容有哪些：

![image-20210721133129956](https://image.3001.net/images/20210806/1628258043_610d3efb7d820b9c479d6.png!small)

主要包括以下内容：

RDN| 说明  
---|---  
CN=Builtin| 该容器内置了本地域组的安全组  
CN=Computers| 机器用户容器，其中包含了所有加入域的主机  
OU=Domain Controllers| 域控制器的容器，其中包含了域内所有的域控制器  
CN=ForeignSecurityPrincipals| 包含了域中所有来自森林外部域的组中的成员  
CN=Managed Service Accounts| 托管服务帐户的容器  
CN=System| 各种预配置对象的容器，其中包括了信任对象，DNS 对象和组策略对象  
CN=Users| 用户和组对象的默认容器  
  
 **配置目录分区**

配置目录分区，即 Configuration NC (Configuration
NC)，整个林共享一份相同的配置目录分区，是域林配置信息的主要存储库，其中存储着有关站点、服务以及整个活动目录结构，例如有哪些域、哪些域控等信息。配置目录分区会被复制到林中所有域的所有域控上。前
Naming Context 图中的`CN=Configuration,DC=whoamianony,DC=org`就是配置目录分区。

下面我们使用 AD Explorer 工具查看域目录分区中的内容有哪些：

![image-20210721134242347](https://image.3001.net/images/20210806/1628258043_610d3efbc227cdb795ecc.png!small)

主要包括以下内容：

RDN| 说明  
---|---  
CN=DisplaySpecifiers| 定义了 Active Directory 活动目录管理单元的各种显示格式  
CN=Extended-Rights| 扩展权限对象的容器  
CN=ForestUpdates| 包含用于表示森林状态和与域功能级别更改的对象  
CN=Partitions| 包含每个 Naming Context，Application Partitions 以及外部 LDAP 目录引用的对象  
CN=Physical Locations| 包含位置对象，可以将其与其他对象关联以表示该对象的位置  
CN=Services| 存储有关服务的配置信息，比如文件复制服务  
CN=Sites| 包含所有站点拓扑和复制对象  
CN=WellKnown Security Principals| 包含常用的外部安全性主题的对象，比如 Anonymous，Authenticated
Users，Everyone 等等  
  
 **架构目录分区**

架构目录分区，即 Schema NC (Schema
NC)，整个林内所有域共享一份相同的架构目录分区，其中存储着整个林中所有对象与属性的定义数据，也存储着如何建立新对象与属性的规则。架构目录分区会被复制到林中所有域的所有域控制器中。前
Naming Context 图中的`CN=Schema,CN=Configuration,DC=whoamianony,DC=org`就是架构目录分区。

## Schema NC

Schema NC 里面包含 Schema 条目信息，定义了 Active Directory 活动目录中使用的类和属性。 与 Domain NC 和
Configuration NC 不同，Schema NC 是具有 classSchema ，attributeSchema 和 subSchema
对象的单个容器。

### LDAP 中的类和继承

我们先来介绍一下 LDAP
里面的类和继承。域内每个条目都是类的实例，而类是一组属性的集合。例如，域内机器`CN=EWS,CN=Computers,DC=whoamianony,DC=org`在
Active Directory 里面是一个条目，里面有众多属性来描述条目的具体信息：

![image-20210721220820027](https://image.3001.net/images/20210806/1628258044_610d3efc0d5737522c66f.png!small)

而这个条目有哪些属性是由他的类决定的。比如，在`objectClass`属性中可以看到，条目`CN=EWS,CN=Computers,DC=whoamianony,DC=org`是类
Computer 的实例：

![image-20210721221104273](https://image.3001.net/images/20210806/1628258044_610d3efc585bca5d0bc1c.png!small)

类是可继承的，子类继承父类的所有属性，top 类是所有类的父类。所以我们看到的 objectClass 里面的值除了 computer 外还有
top、person、organizationalPerson 和 user。根据类的继承关系可知，computer 是 user 的子类，user 是
organizationalPerson 的子类，organizationalPerson 是 person 的子类，person 是 top 的子类。

### Schema NC 中的类

域内每个条目都是类的实例，所有的类都存储在 Schema NC 里面，是 Schema NC
的一个条目。例如前面说过的条目`CN=EWS,CN=Computers,DC=whoamianony,DC=org`是类 Computer 的实例，那么类
Computer 就存储在 Schema NC 里面，是Schema
NC的一个条目，即下图中的`CN=Computer,CN=Schema,CN=Configuration,DC=whoamianony,DC=org`：

![image-20210721222127869](https://image.3001.net/images/20210806/1628258044_610d3efcb519313058721.png!small)

前面说过域内每个条目都是类的实例，所有的类都存储在 Schema NC 里面，是 Schema NC 的一个条目。因此 Schema NC
中的类条目也是一个类的实例，这个类是 classSchema，即下图中的`CN=Class-Schema,CN=Schema,CN=Configuration,DC=whoamianony,DC=org`：

![image-20210721222449391](https://image.3001.net/images/20210806/1628258045_610d3efd41d6c8524e3ad.png!small)

所有的类条目都是 classSchema 类的实例。

### Schema NC 中的属性

Schema NC 中除了定义了 Active Directory 中使用的类以外，还定义了 Active Directory
中使用的属性。每个属性都是一个条目，是类`attributeSchema`的实例。

## Application Partitions

从 Windows Server 2003 开始，微软允许用户自定义分区来扩展 Naming Context。Application Partitions
其实就是 Naming Context 的一个扩展，它本质上还是属于 Naming
Context。管理员可以自定义创建分区（这个分区我们称为区域），以将数据存储在他们选择的特定域控制器上。

## Ending......

![33-334647_networking-png-transparent-images-computer-network-png-png](https://image.3001.net/images/20210806/1628258045_610d3efd982c17be6d983.png!small)

> 参考：
>
> <https://docs.microsoft.com/en-us/windows/win32/ad/active-directory-domain-> services>
>
> <https://docs.microsoft.com/en-us/windows/win32/ad/naming-contexts-and-> partitions>
>
> <https://docs.microsoft.com/en-us/windows/win32/ad/about-application-> directory-partitions>
>
> <https://docs.microsoft.com/en-us/windows/win32/ad/domain-trees>
>
> <https://daiker.gitbook.io/windows-protocol/ldap-pian/8>
>
> <https://blog.csdn.net/qq_36119192/article/details/107529527>
>
> <https://blog.csdn.net/qq_36119192/article/details/83268793>
>
> <https://blog.csdn.net/qq_36119192/article/details/107529805>
>
> 《内网安全攻防：渗透测试指南》


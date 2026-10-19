## 一、漏洞信息

CVE-2022-24481是发生在CLFS驱动中的一个类型混淆漏洞，通过精巧的对blf文件的部分数据进行构造，可使LogBlockHeader中的ClientContextOffset指向ContainContext，从而造成类型混淆。

## 二、测试环境及漏洞复现

测试环境

  * POC： 4c1579c6a14bb8f3985be8a1a83c731c
  * 靶机： win10 x64 专业版，21H2

漏洞复现

![wKg0C2Q2sNCADGRmAACqApdDnHs835.png](https://image.3001.net/images/20230724/1690167992_64bdeab8a4071ab86897f.png!small)

## 三、漏洞成因分析

### CLFS内部结构

 **CLFS即通用日志文件系统是在 Windows**  
Vista 和 Windows Server 2003 R2
中为实现高性能而引入的日志框架，它负责提供一个高性能、通用的日志文件子系统，供专用客户端应用程序使用，提供 API
函数来创建、存储和读取日志数据。并且多个客户端可以共享以优化日志访问。CLFS驱动本质上的作用就是对BLF 日志进行格式解析及处理。

![wKg0C2Q2sO6AYagaAACpvUlkLHQ344.png](https://image.3001.net/images/20230724/1690167993_64bdeab972260f13d17a2.png!small)

BLF日志的格式如上图所示，每个日志块都以一个名为**_CLFS_LOG_BLOCK_HEADER**的结构开始：

![wKg0C2Q2sPqARrwEAABiqSCl374584.png](https://image.3001.net/images/20230724/1690167994_64bdeaba12b36f1217d91.png!small)

Checksum(0xC)字段是该Log文件的CRC校验和，在对Log文件进行编码/解码操作时都需要对文件进行校验，通常在CLFS漏洞利用实现过程中都需要绕过CRC校验。

![wKg0C2Q2sQOAHLjXAABIvr5kmE952.png](https://image.3001.net/images/20230724/1690167994_64bdeaba873119ecca4c7.png!small)

RecordOffsets(0x28)是日志块内记录的偏移量数组。CLFS  
只处理指向 **_CLFS_LOG_BLOCK_HEADER** 末尾的第一个记录偏移量
(0x70)。当基本日志文件存储在磁盘上时，必须对其日志块进行编码。

基本日志记录存储用于将基本日志文件与容器相关联的元数据。其结构如下：

![wKg0C2Q2sQ6AcDusAAC7eLRM5CM015.png](https://image.3001.net/images/20230724/1690167994_64bdeabaebe907dec279c.png!small)

rgClients（0x1a8）和rgContainers(0x398)字段分别是存储着ClientContext和ContainerContex偏移值的数组。

ClientContext的结构：

![wKg0C2Q2sRqAc1pBAACd23BAMr8699.png](https://image.3001.net/images/20230724/1690167995_64bdeabb7520c56c3a9fc.png!small)

ContainerContext的结构：

![wKg0C2Q2sSaARHRPAABWErwiK7Y466.png](https://image.3001.net/images/20230724/1690167996_64bdeabc101578ae2cb63.png!small)

pContainer(0x18) 实际上包含一个内核指针,
指向在运行时描述容器的类CClfsContainer。当Log文件在磁盘上时，该字段必须设置为零。

![wKg0C2Q2sTAE3FfAAA0tptjrGE910.png](https://image.3001.net/images/20230724/1690167996_64bdeabc76a6e7be044f4.png!small)

获取ClientContext/ContainerContext的函数分别是CClfsBaseFile::AcquireClientContext及

CClfsBaseFile::AcquireContainerContext，大致流程均是先通过CClfsBaseFile::GetBaseLogRecord获取基本日志块的地址，然后通过GetSymbol函数通过偏移找到对应的Context结构。

![wKg0C2Q2sUqAF56AAABjhkWofRg013.png](https://image.3001.net/images/20230724/1690167996_64bdeabce7e2677b1bec1.png!small)

### 漏洞触发

CVE-2022-24481漏洞原因在于CClfsBaseFile::GetSymbol获取ClientContext时对其字段的校验不够严格，攻击者进行精巧的数据布局后使rgClients的偏移指向ContainerContext。

  1.  **添加容器（Container）**

为Log文件添加容器，以便 BaseLogRecord中拥有ContainerContext。

![wKg0C2Q2sWOAVGqdAAFu8CNwg6Y117.png](https://image.3001.net/images/20230724/1690167997_64bdeabd6ee77dd7f4974.png!small)

  2.  **数据构造**

成功创建Log文件并为其添加容器后，BaseLogRecord
0x1368和0x1528的偏移处分别存储着ClientContext和ContainerContext

![wKg0C2Q2sYSASijsAAEP8IuGlCM728.png](https://image.3001.net/images/20230724/1690167998_64bdeabe4a6f40a292232.png!small)

![wKg0C2Q2sZOAMxTdAADQVotuEug002.png](https://image.3001.net/images/20230724/1690167998_64bdeabee05f303867514.png!small)

数据构造的目的是为了绕过CLFS在解析Log文件对context的校验。

第一部分绕过Log文件的crc校验。Log文件的BaseLogRecord在进行编码和解码都会进行CRC校验。

![wKg0C2Q2sZAfgXeAACLwg0zqks834.png](https://image.3001.net/images/20230724/1690167999_64bdeabf7d2c793d377d2.png!small)

在触发过程中，为绕过CLFS对Checksum字段的检查，需要自己实现一次CRC校验并将结果填充至Checksum（0xc）

![wKg0C2Q2sbmAQ6tAAAB9gRKYZpA918.png](https://image.3001.net/images/20230724/1690167999_64bdeabfece91d902f13d.png!small)

第二部分，对ClientCotext的数据进行修改，使其能够成功的绕过CLFS的检查最后指向ContainerContext。

首先，更新_CLFS_LOG_BLOCK_HEADER中
rgClients（0x1a8）字段，使rgClients存储的偏移值变为0x1520(ContainerContext offset为0x1528)

![wKg0C2Q2sdqAeXPxAAAwci9d8Tg191.png](https://image.3001.net/images/20230724/1690168000_64bdeac06a81689dafe67.png!small)

然后在0x1510及0x1514偏移处分别存储ClientContext新的起始偏移地址（0x1520）以及ClientContext的结尾偏移地址（0x1520+size(0x88)。

![wKg0C2Q2seOAdBwcAAB2xq6F1o761.png](https://image.3001.net/images/20230724/1690168000_64bdeac0d4e467c82c5a8.png!small)

构造这两处值是为了绕过在CClfsBaseFile::GetSymbol函数中的相关检查，以使CLFS在调用

CClfsBaseFile::AcquireClientContext能够成功获取ClientContext。

![wKg0C2Q2se2ABCfFAAByAhTY3O4401.png](https://image.3001.net/images/20230724/1690168001_64bdeac154a1374118bf3.png!small)

完成以上步骤之后，rgClients已成功指向ContainerContext。

## 四、漏洞利用分析

漏洞成功触发之后，下一步就是要实现提权利用，对于此漏洞我们需要重点关注以下两个点：

  * 借助ClientContext对ContainerContext的修改能力
  * ContainerContext中pContainer(可将其指向R3内存)

  1. ### 修改pContainer

成功利用该漏洞前提就是能够控制pContainer指向的值，第一步就是通过ClientContext修改ContainerContext->pContainer的值。由于为Log文件添加容器之后，需要再次调用CreateLogFile对BaseLogRecord进行一次初始化更新

![wKg0C2Q2shyAFjMAAAEiIeQLOj4265.png](https://image.3001.net/images/20230724/1690168001_64bdeac1c00d6ba181f73.png!small)

大致逻辑首先获取ClientContext

![wKg0C2Q2siaAHMn5AACSyNqsSFY827.png](https://image.3001.net/images/20230724/1690168002_64bdeac24bd07fd016b54.png!small)

将ClientContext中的数据保存到CclfsLogFcbPhysical类中，此处重点关注rcx+20h处的值，现存储着我们pContainer的目标值（r3可控地址0x40000000）。

![wKg0C2Q2siANRAkAACwXmg05ek578.png](https://image.3001.net/images/20230724/1690168002_64bdeac2bb267246c4382.png!small)

随后会调用CClfsBaseFilePersisted::LoadContainerQ函数加载Container并更新pContainer,让其指向在运行时描述容器的类CclfsContainer

![wKg0C2Q2sjmARHHeAAE3PWG4QIo455.png](https://image.3001.net/images/20230724/1690168003_64bdeac3404881cf68e52.png!small)

CclfsContainer类的前8个字节指向虚表

![wKg0C2Q2skGAf0W1AADZ71E8Y8745.png](https://image.3001.net/images/20230724/1690168003_64bdeac3cab96622b09c1.png!small)

此时pContainer还是指向内核的CclfsContainer类，我们的可控地址0x40000000被保存到了CclfsLogFcbPhysical类的0x1a0处，经过分析发现，在close
Log文件句柄过程中，CLFS会调用CClfsLogFcbPhysical::FlushMetadata对ClientContext进行更新

![wKg0C2Q2smKAEF4wAAEEdO5btwg933.png](https://image.3001.net/images/20230724/1690168004_64bdeac46f120c1526852.png!small)

实际上就是将存储在CclfsLogFcbPhysical类中的数据重新写回到ClientContext。

![wKg0C2Q2sm6ACqt8AAD9KVK4Qg173.png](https://image.3001.net/images/20230724/1690168004_64bdeac4f1064e595278d.png!small)

由于ClientContext指向ContainerContext-0x8，这里将0x40000000赋给ClientContext+0x20就是修改ContainerContext+0x18(pContainer)为0x0x40000000。

  2. ### 修改previousMode

执行CloseHandle时，内核中首先会将当前线程的previousMode修改为内核态（0）

![wKg0C2Q2soAMVOwAAAuaXuXbos431.png](https://image.3001.net/images/20230724/1690168005_64bdeac5751a3c211dfbb.png!small)

![wKg0C2Q2spKADHFtAACUELQO1cM234.png](https://image.3001.net/images/20230724/1690168006_64bdeac6154a526a5cae7.png!small)

待到成功执行完返回R3前，又会将当前线程的previousMode修改为用户态（1）

![wKg0C2Q2spuAXM7RAAAte8qciKo991.png](https://image.3001.net/images/20230724/1690168006_64bdeac6a92f47da440ca.png!small)

![wKg0C2Q2spAFuzyAABLLZpj4uM685.png](https://image.3001.net/images/20230724/1690168007_64bdeac71440774d99b14.png!small)

此漏洞的提权原理就是在返回R3前，修改当前线程的previousMode为0，下图为我们自定义构造由pContainer指向的”
CclfsContainer”.

![wKg0C2Q2sqqAKuA5AACvuQHhFKw934.png](https://image.3001.net/images/20230724/1690168007_64bdeac77da69b872cf80.png!small)

0x0为“虚表指针“，0x20为文件句柄，0x30为previousMode+0x30 address

![wKg0C2Q2sreATIyAAAA5Ms7iMYs168.png](https://image.3001.net/images/20230724/1690168008_64bdeac80cb661f475c1e.png!small)

漏洞利用是发生在CClfsLogFcbPhysical::CloseContainers函数中

![wKg0C2Q2ssOAZuK4AAEy4Awwuw003.png](https://image.3001.net/images/20230724/1690168008_64bdeac87b2f1b02ca80a.png!small)

在CClfsLogFcbPhysical::CloseContainers首先通过ContainerContext获取到pContainer，然后对CclfsContainer类进行一个清理释放。这里我们拥有一个可控函数的执行！

![wKg0C2Q2ssAHEnsAACCLfaq9iU653.png](https://image.3001.net/images/20230724/1690168009_64bdeac9117b7c4a6df1c.png!small)

CClfsContainer::Close实现：

![wKg0C2Q2st2AKUqzAAA8XMWT9ek894.png](https://image.3001.net/images/20230724/1690168009_64bdeac983d73ecc079a2.png!small)

提权过程：

![wKg0C2Q2suaAdRxWAABckHfKlsI239.png](https://image.3001.net/images/20230724/1690168010_64bdeaca35897e4dbeb28.png!small)

随后调用ObfDereferenceObjectWithTag传入的参数为previousMode+0x30，并利用该函数的减数机制，将previousMode修改为0（内核态）

![wKg0C2Q2su2Ab1pqAADLYlp1zYE046.png](https://image.3001.net/images/20230724/1690168010_64bdeacaa7b2703ae0112.png!small)

此时，已到达提权目的。

最后，调用可控函数ClfsSetEndOfLog返回错误码到R3。

![wKg0C2Q2svaAVMgRAABfAo5dj0M647.png](https://image.3001.net/images/20230724/1690168011_64bdeacb2a2900bb5b419.png!small)

在提权样本中，利用当前线程的内核执行能力将当前线程的token替换为system token。

![wKg0C2Q2swmAFiZhAAAwOpcW1aI998.png](https://image.3001.net/images/20230724/1690168011_64bdeacb92f8c44012f3d.png!small)

Token替换之后，在将previousMode改回1（目的是混淆）

![wKg0C2Q2sxSAQjbQAAAzynuLjuE853.png](https://image.3001.net/images/20230724/1690168012_64bdeacc084eded187514.png!small)

至此，分析完毕！


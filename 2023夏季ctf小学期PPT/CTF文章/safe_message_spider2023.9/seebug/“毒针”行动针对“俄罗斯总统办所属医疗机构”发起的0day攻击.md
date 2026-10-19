**作者：360 Core Security  
博客：[http://blogs.360.cn/post/PoisonNeedles_CVE-2018-15982.html?from=timeline&isappinstalled=0](http://blogs.360.cn/post/PoisonNeedles_CVE-2018-15982.html?from=timeline&isappinstalled=0)**

### 概述

近年来，乌克兰和俄罗斯两国之间围绕领土问题的争执不断，发生了克里米亚半岛问题、天然气争端、乌克兰东部危机等事件。伴随着两国危机事件愈演愈烈之时，在网络空间中发生的安全事件可能比现实更加激烈。2015年圣诞节期间乌克兰国家电力部门受到了APT组织的猛烈攻击，使乌克兰西部的
140 万名居民在严寒中遭遇了大停电的煎熬，城市陷入恐慌损失惨重，而相应的俄罗斯所遭受的APT攻击，外界却极少有披露。

2018年11月25日，乌俄两国又突发了“刻赤海峡”事件，乌克兰的数艘海军军舰在向刻赤海峡航行期间，与俄罗斯海军发生了激烈冲突，引发了全世界的高度关注。在2018年11月29日，“刻赤海峡”事件后稍晚时间，360高级威胁应对团队就在全球范围内第一时间发现了一起针对俄罗斯的APT攻击行动。值得注意的是此次攻击相关样本来源于乌克兰，攻击目标则指向俄罗斯总统办公室所属的医疗机构。攻击者精心准备了一份俄文内容的员工问卷文档，该文档使用了最新的Flash
0day漏洞cve-2018-15982和带有自毁功能的专属木马程序进行攻击，种种技术细节表明该APT组织不惜代价要攻下目标，但同时又十分小心谨慎。在发现攻击后，我们第一时间将0day漏洞的细节报告了Adobe官方，Adobe官方及时响应后在12月5日加急发布了新的Flash
32.0.0.101版本修复了此次的0day漏洞。

![
](https://images.seebug.org/content/images/2018/12/f564a540-d5a7-4787-9a93-dd9d9d79b824.png-w331s)
图1：漏洞文档内容

按照被攻击医疗机构的网站（<http://www.p2f.ru>）
介绍，该医疗机构成立于1965年，创始人是俄罗斯联邦总统办公室，是专门为俄罗斯联邦最高行政、立法、司法当局的工作人员、科学家和艺术家提供服务的专业医疗机构。由于这次攻击属于360在全球范围内的首次发现，结合被攻击目标医疗机构的职能特色，我们将此次APT攻击命名为“毒针”行动。目前我们还无法确定攻击者的动机和身份，但该医疗机构的特殊背景和服务的敏感人群，使此次攻击表现出了明确的定向性，同时攻击发生在“刻赤海峡”危机的敏感时段，也为攻击带上了一些未知的政治意图。

![
](https://images.seebug.org/content/images/2018/12/da13c129-c430-4ab3-b20d-d39e17e15a5c.png-w331s)
图2： 该医院机构介绍

### 攻击过程分析

攻击者通过投递rar压缩包发起攻击，打开压缩包内的诱饵文档就会中招。完整攻击流程如下：

![ ](https://images.seebug.org/content/images/2018/12/d36a30c6-b948-45bf-bd3a-fd674084890c.png-w331s)

图3： 漏洞文档攻击过程

当受害者打开员工问卷文档后，将会播放Flash 0day文件。

![
](https://images.seebug.org/content/images/2018/12/dd540b9a-f79b-401b-89cb-d8ac4bee1b58.png-w331s)

图4： 播放Flash 0day漏洞

触发漏洞后， winrar解压程序将会操作压缩包内文件，执行最终的PE荷载backup.exe。

![
](https://images.seebug.org/content/images/2018/12/55065e88-f9f4-49c9-bb35-5bc901650a66.png-w331s)
图5： 漏洞执行进程树

### 0day漏洞分析

通过分析我们发现此次的CVE-2018-15982
0day漏洞是flash包com.adobe.tvsdk.mediacore.metadata中的一个UAF漏洞。Metadata类的setObject在将String类型（属于RCObject）的对象保存到Metadata类对象的keySet成员时，没有使用DRCWB（Deferred
Reference Counted, with Write
Barrier）。攻击者利用这一点，通过强制GC获得一个垂悬指针，在此基础上通过多次UAF进行多次类型混淆，随后借助两个自定义类的交互操作实现任意地址读写，在此基础上泄露ByteArray的虚表指针，从而绕过ASLR，最后借助HackingTeam泄露代码中的方式绕过DEP/CFG，执行shellcode。

![
](https://images.seebug.org/content/images/2018/12/84964d61-a2a3-4d78-b064-3f74c6de7e89.png-w331s)

#### 漏洞成因分析

在漏洞的触发过程，flash中Metadata的实例化对象地址，如下图所示。

![
](https://images.seebug.org/content/images/2018/12/437a2a99-19de-41c7-8047-f75ce3543ad5.png-w331s)

循环调用Metadata的setObject方法后，Metadata对象的keySet成员，如下图所示。

![
](https://images.seebug.org/content/images/2018/12/1e06f2a7-cdcc-4323-8b87-90e0464d266a.png-w331s)

keySet成员的部分值，如下图所示。

![
](https://images.seebug.org/content/images/2018/12/8e75e1ec-727a-4595-8723-92b8eed1c782.png-w331s)

强制垃圾回收后keySet成员被释放的内存部分，如下图所示。

![
](https://images.seebug.org/content/images/2018/12/52af7263-6c4c-407b-9780-6b44466f20e8.png-w331s)

在new Class5重用内存后，将导致类型混淆。如下图所示。

![
](https://images.seebug.org/content/images/2018/12/ab0e7a2a-8841-4e51-a3e8-6ed153a62d3e.png-w331s)

后续攻击者还通过判断String对象的length属性是否为24来确定漏洞利用是否成功。（如果利用成功会造成类型混淆，此时通过获取String对象的length属性实际为获取Class5的第一个成员变量的值24）。

通过进一步反编译深入分析，我们可以发现Metadata类的setObject对应的Native函数如下图所示，实际功能存在于setObject_impl里。

![
](https://images.seebug.org/content/images/2018/12/4ce367a5-b261-4eda-b318-2e615365f69d.png-w331s)

在Object_impl里，会直接将传入的键（String对象）保存到Metadata的keySet成员里。

![
](https://images.seebug.org/content/images/2018/12/21044c6e-c4e3-4982-b909-6a3ec556fdb7.png-w331s)

Buffer结构体定义如下（keySet成员的结构体有一定差异）。

![
](https://images.seebug.org/content/images/2018/12/95edb777-7a8e-497d-a86e-e9650fa48db9.png-w331s)

add_keySet中保存传入的键(String对象)，如下代码所示。

![
](https://images.seebug.org/content/images/2018/12/7fa0a60c-e521-4ddf-b1c2-97ce4caff859.png-w331s)

这个时候垃圾回收机制认为传入的键未被引用，从而回收相应内存，然而Metadata对象的keySet成员中仍保留着被回收的内存的指针，后续通过new
Class5来重用被回收的内存，造成UAF漏洞。

#### 漏洞利用分析

在实际的攻击过程中，利用代码首先申请0x1000个String对象，然后立即释放其中的一半，从而造成大量String对象的内存空洞，为后面的利用做准备。

![ ](https://images.seebug.org/content/images/2018/12/3a3206cd-eb22-4307-aaca-255b4e5b7331.png-w331s)

随后，利用代码定义了一个Metadata对象，借助setObject方法将key-value对保存到该对象中，Metadata对象的keySet成员保存着一个指向一片包含所有key(以String形式存储)的内存区域的指针。紧接着强制触发GC，由于keySet成员没有使用DRCWB，keySet成员内保存着一个指向上述内存区域的垂悬指针，随后读取keySet到arr_key数组，供后面使用。

![
](https://images.seebug.org/content/images/2018/12/ff625d61-98c1-4c79-b1e3-ad3f1fb7c7fb.png-w331s)

得到垂悬指针后，利用代码立即申请0x100个Class5类对象保存到vec5（vec5是一个向量对象），由于Class5类对象的内存大小和String对象的内存大小一致（32位下均为0x30字节），且相关对象分配在同一个堆内，根据mmgc内存分配算法，会有Class5对象占据之前被释放的String对象的内存空间。

![
](https://images.seebug.org/content/images/2018/12/33dcc695-24af-4517-b123-4bf4e9863f23.png-w331s)

其中Class5对象定义如下，可以看到该Class5有2个uint类型的成员变量，分别初始化为0x18和2200(0x898)。

![
](https://images.seebug.org/content/images/2018/12/e83a3489-adfe-4c87-8c3a-edf57970fb8b.png-w331s)

随后遍历key_arr数组，找到其中长度变为为0x18的字符串对象（在内存中，String对象的length字段和Class5的m_1成员重合），在此基础上判断当前位于32位还是64位环境，据此进入不同的利用分支。

![
](https://images.seebug.org/content/images/2018/12/6681e7ac-a007-48ca-b125-af66000e432e.png-w331s)

接上图，可以看到：在找到被Class5对象占用的String索引后，利用代码将arr_key的相关属性清零，这使得arr_key数组内元素（包括已占位Class5对象）的引用计数减少变为0，在MMgc中，对象在引用计数减为0后会立刻进入ZCT（zero
count table）。随后利用代码强制触发GC，把ZCT中的内存回收，进入后续利用流程。下面我们主要分析32位环境下的利用流程。

下面我们主要分析32位环境下的利用流程，在32位分支下，在释放了占位的Class5对象后，利用代码立即申请256个Class3对象并保存到另一个向量对象vec3中，此过程会重用之前被释放的某个（或若干）Class5对象的内存空间。

![
](https://images.seebug.org/content/images/2018/12/2feefab8-83e3-4ddb-8081-2a3313dd1b99.png-w331s)

其中Class3对象的定义如下，它和Class5非常相似，两者在内存中都占用0x30字节。

![
](https://images.seebug.org/content/images/2018/12/edef019c-6e65-4dfb-a203-a34d81bf6ef4.png-w331s)

可以看到Class3有一个m_ba成员和一个m_Class1成员，m_ba被初始化为一个ByteArray对象，m_Class1被初始化为一个Class1对象，Class1对象定义如下：

![
](https://images.seebug.org/content/images/2018/12/3520a7a0-b82e-48b2-b6cf-1662fdd2396c.png-w331s)

Class3对象占位完成后，利用代码立即遍历vec5寻找一个被Class3对象占用内存的原Class5对象。找到后，保存该Class5对象的索引到this.index_1，并保存该对象（已经变为Class3对象）的m_Class1成员到this.ori_cls1_addr，供后续恢复使用。

![
](https://images.seebug.org/content/images/2018/12/d8eada4b-0e6f-4221-8eb2-05fd5a9dd664.png-w331s)

两轮UAF之后，利用代码紧接着利用上述保存的index_1索引，借助vec5[index_1]去修改被重用的Class3对象的m_Class1成员。随后立即遍历vec3去寻找被修改的Class3对象，将该对象在vec3中的索引保存到this.index_2。

![
](https://images.seebug.org/content/images/2018/12/ebc1971f-69b4-4bd4-b817-4963f0a5a9b3.png-w331s)

到目前为止，利用代码已经得到两个可以操纵同一个对象的vector(vec5和vec3)，以及该对象在各自vec中的索引(index_1和index_2)。接下来利用代码将在此基础上构造任意地址读写原语。

我们来看一下32位下任意地址读写原语的实现，从下图可以看到，借助两个混淆的Class对象，可以实现任意地址读写原语，相关代码在上图和下图的注释中已经写得很清楚，此处不再过多描述。关于减去0x10的偏移的说明，可以参考我们之前对cve-2018-5002漏洞的分析文章。

![
](https://images.seebug.org/content/images/2018/12/6f47ee95-68f7-4830-b20d-35a65c59b326.png-w331s)

64位下的任意地址读写原语和32位下大同小异，只不过64位下将与Class5混淆的类对象换成了Class2和Class4。此外还构造了一个Class0用于64位下的地址读取。

以下是这三个类的定义。

![
](https://images.seebug.org/content/images/2018/12/dd5b154f-ee87-4a89-b4e6-6319bb753a3c.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/a841012f-8b8c-4da3-82de-76a432d43e61.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/7790adcb-7e78-4d95-894f-9a60535d7ac0.png-w331s)
以下是64位下的任意地址读写原语，64位下的读写原语一次只能读写32位，所以对一个64位地址需要分两次读写。

![
](https://images.seebug.org/content/images/2018/12/d184e058-69f5-4003-b89f-55a1c891404f.png-w331s)

利用代码借助任意地址读写构造了一系列功能函数，并借助这些功能函数最终读取kernel32.dll的VirtualProtect函数地址，供后面Bypass
DEP使用。

![
](https://images.seebug.org/content/images/2018/12/52e519c6-74c6-4c4c-b258-afee3a499642.png-w331s)

利用最终采用与HackingTeam完全一致的手法来Bypass
DEP/CFG。由于相关过程在网上已有描述，此处不再过多解释。32和64位下的shellcode分别放在的Class6和Class7两个类内，
shellcode最终调用cmd启动WINRAR相关进程，相关命令行参数如下：

![
](https://images.seebug.org/content/images/2018/12/38cb100c-ab0c-426a-a4dd-e8f2402996d1.png-w331s)

#### 漏洞补丁分析

Adobe官方在12月5日发布的Flash
32.0.0.101版本修复了此次的0day漏洞，我们通过动态分析发现该次漏洞补丁是用一个Array对象来存储所有的键，而不是用类似Buffer结构体来存储键，从而消除引用的问题。

1、某次Metadata实例化对象如下图所示，地址为0x7409540。

![
](https://images.seebug.org/content/images/2018/12/51268655-02a4-4c81-af07-fad0e32eb21a.png-w331s)

2、可以看到Metadata对象的偏移0x1C处不再是类似Buffer结构体的布局，而是一个Array对象，通过Array对象来存储键值则不会有之前的问题。

![
](https://images.seebug.org/content/images/2018/12/a956e69b-601f-4ce4-bc5d-f8b1b60548e2.png-w331s)

3、循环调用setObject设置完键值后keySet中的值如下所示。

![
](https://images.seebug.org/content/images/2018/12/f8af6062-92ab-4e94-8266-6217b9dd19e9.png-w331s)

4、强制垃圾回收发现保存的ketSet中的指针仍指向有效地字符串，说明强制垃圾回收并没有回收键值对象。

![
](https://images.seebug.org/content/images/2018/12/dfa56637-c0eb-458f-9007-05d3d5fbee68.png-w331s)

### 最终荷载分析

PE荷载backup.exe将自己伪装成了NVIDIA显卡控制台程序，并拥有详细文件说明和版本号。

![
](https://images.seebug.org/content/images/2018/12/2b01426f-73fe-4972-a58c-56907e96ed37.png-w331s)

文件使用已被吊销的证书进行了数字签名。

![
](https://images.seebug.org/content/images/2018/12/d517aad9-e932-4519-8e25-707d25836fb1.png-w331s)

PE荷载backup.exe启动后将在本地用户的程序数据目录释放一个NVIDIAControlPanel.exe。该文件和backup.exe文件拥有同样的文件信息和数字签名，但文件大小不同。

![
](https://images.seebug.org/content/images/2018/12/80f44548-54a8-4a2e-baa1-e1a405f09074.png-w331s)

经过进一步的分析，我们发现PE荷载是一个经过VMP强加密的后门程序，通过解密还原，我们发现主程序主要功能为创建一个窗口消息循环，有8个主要功能线程，其主要功能如下：

线程功能：

![
](https://images.seebug.org/content/images/2018/12/04a2a240-bef7-437b-a2dc-a6dcdd05520d.png-w331s)

主消息循环功能：

![
](https://images.seebug.org/content/images/2018/12/2220b2ba-60a5-4c38-a850-aa0b6939538d.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/f10f5bef-3b75-4819-87c0-4e463dfe5bcf.png-w331s)

#### 线程功能分析

##### 0 分析对抗线程

![
](https://images.seebug.org/content/images/2018/12/f3d1547d-97fb-4eb9-bd56-2903411af225.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/37f19782-3189-401f-80ae-272fa45ad85e.png-w331s)

检验程序自身的名称是否符合哈希命名规则,如符合则设置自毁标志。

##### 1 唤醒线程

监控用户活动情况，如果用户有键盘鼠标活动则发送0x401消息给主窗口程序，唤醒创建注册计划任务线程。

![
](https://images.seebug.org/content/images/2018/12/4495a6b1-d46c-44a1-beac-56e26177100d.png-w331s)

##### 2 休眠线程

取当前TickCount 进行比较，低位小于100则发送 WM_COPYDATA指令 主窗口循环在接收这一指令后，会休眠一定时间

![ ](https://images.seebug.org/content/images/2018/12/79ac6d46-40a3-4577-a6ae-bb991666e0bd.png-w331s) ![
](https://images.seebug.org/content/images/2018/12/74ca47ea-678c-44dd-bcaf-d73e8f077679.png-w331s)

##### 3 定时自毁线程

解密程序中的时间字符串与当前系统时间进行比较，如果当前系统时间较大，则设置标志位，并向主窗口发送0x464消息（执行自毁）。

![
](https://images.seebug.org/content/images/2018/12/eb7dd2cf-7f03-465c-a23a-478badeb0a9f.png-w331s)

##### 4 通信线程

获取机器信息 包括CPU型号,内存使用情况,硬盘使用情况,系统版本,系统语言,时区 用户名,SID,安装程序列表等信息。

![
](https://images.seebug.org/content/images/2018/12/b93ff551-c864-48fb-b1f3-c5cf1b806817.png-w331s)

向 188.241.58.68 发送POST

![
](https://images.seebug.org/content/images/2018/12/d16bac91-93a1-41b6-9adb-b79d39ba49a5.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/417681a5-81de-4fff-80ef-c60438908483.png-w331s)

连接成功时,继续向服务器发送数据包

![
](https://images.seebug.org/content/images/2018/12/432cabac-4344-47c6-9dad-2838b47451b1.png-w331s)

符合条件时,进入RunPayload函数（实际并未捕获到符合条件的情况）

![
](https://images.seebug.org/content/images/2018/12/81cb4998-915d-477c-af8c-b56726ce4531.png-w331s)

RunPayload函数

![ ](https://images.seebug.org/content/images/2018/12/49a715a3-8c4b-42d5-aaed-ce39c0ca72fc.png-w331s)

LoadPE

![
](https://images.seebug.org/content/images/2018/12/782e1580-db29-4655-82b5-285e650183f6.png-w331s)

RunShellCode

![
](https://images.seebug.org/content/images/2018/12/9e8bb2b4-6355-4590-b05a-fb503ec32226.png-w331s)

##### 5 注册自启动线程

1、首先拿到线程6中保存的AppData\Local目录下的NVIDIAControlPanel文件路径，使用该路径或者该路径的短路径与当前文件模块路径判断是否相同。

![
](https://images.seebug.org/content/images/2018/12/3c2e5946-b212-44ff-889b-4c1dd0b6fc39.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/87bbe86c-05d5-443b-a2da-2841d10c48a7.png-w331s)

2、随后尝试打开注册表HKEY_CURRENT_USER下SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder。

![
](https://images.seebug.org/content/images/2018/12/877a55b7-3599-45f1-a1f2-eae36ffbed25.png-w331s)

3、查询当前注册表路径下NVIDIAControlPanel键值是否存在，如果不存在或者为禁用状态则设置键值为启用的键值02,00,00,00,00,00,00,00,00,00,00,00。

![ ](https://images.seebug.org/content/images/2018/12/ca5d6e5a-3c2b-49f0-96fb-abc061348d22.png-w331s)

##### 6 注册计划任务线程

###### 检查自身是否运行在System进程

如果运行在system进程, 则弹出Aborting消息, 退出进程,并清理环境

![
](https://images.seebug.org/content/images/2018/12/a16456f6-2fa1-45d7-bb4f-a9a1ceb0fb51.png-w331s)

并不断向 Windows Update窗口投递退出消息

![
](https://images.seebug.org/content/images/2018/12/a15da783-f218-4f9d-8924-9d64771eee54.png-w331s)

###### 三种文件拷贝方式

其使用了三种不同的方式去拷贝自身文件：

  1. 在监测到杀软相关进程之后, 会使用Bits_IBackgroundCopyManager方式进行自拷贝
  2. 如果没有相关杀软进程, 会使用iFileOperation 方式进行自拷贝
  3. 如果在以上工作方式之行结束, 仍未有文件拷贝到目标目录, 则执行释放BAT方式进行自拷贝

###### Bits_IBackgroundCopyManager

(5ce34c0d-0dc9-4c1f-897c-daa1b78cee7c)

![
](https://images.seebug.org/content/images/2018/12/59918a25-eda8-4a2b-9624-d6cc919c0c33.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/60dad243-4268-42b4-9bef-313fb09293d4.png-w331s)

###### iFileOperation

{3ad05575-8857-4850-9277-11b85bdb8e09}

![
](https://images.seebug.org/content/images/2018/12/dc5c1764-5f0f-4c11-9f8f-74e0191bdcf5.png-w331s)

###### 批处理文件释放

创建批处理文件，拷贝自身来释放文件。

![
](https://images.seebug.org/content/images/2018/12/022c9043-2006-44a9-8be3-6dbc71fcb860.png-w331s)
![ ](https://images.seebug.org/content/images/2018/12/e99f3cc4-707b-46fa-bbb4-1ea71ae12caf.png-w331s)

固定释放常驻后门: F951362DDCC37337A70571D6EAE8F122

###### 检测杀软

检测的杀软包括F-Secure, Panda, ESET, Avira, Bitdefender, Norton, Kaspersky
通过查找名称和特定驱动文件实现

![
](https://images.seebug.org/content/images/2018/12/bb6be38f-4f4d-461b-8c82-606c64356d5e.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/e99d8045-adb0-4593-a230-2bc08330ddd8.png-w331s)
![ ](https://images.seebug.org/content/images/2018/12/1036e5ea-362e-49ef-aed9-e8a96057b882.png-w331s)

检测的杀软之后会执行自毁流程

###### 添加计划任务

![
](https://images.seebug.org/content/images/2018/12/18be8971-ebd1-4d9f-b86f-796fc7717443.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/e9b1554f-d825-4abb-b0dd-a68d2b1abae2.png-w331s)

##### 7 自毁线程

判断系统版本后分别使用ITask和ITaskService 停止NVIDIAControlPanel这个计划任务

Win7以前采用ITask接口：

![
](https://images.seebug.org/content/images/2018/12/265797f6-95b7-4802-8838-f4dacde78a74.png-w331s)
![
](https://images.seebug.org/content/images/2018/12/8eddc9a5-985b-4208-a131-88f7dc8898e1.png-w331s)

Win7和Win7以后采用ITaskService接口：

![
](https://images.seebug.org/content/images/2018/12/da528ccf-9264-473f-84d6-c7e032d2972b.png-w331s)

在完成后清理文件。

### 附录IOC

**MD5：**

92b1c50c3ddf8289e85cbb7f8eead077

1cbc626abbe10a4fae6abf0f405c35e2

2abb76d71fb1b43173589f56e461011b

**C &C：**

188.241.58.68

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/753/>


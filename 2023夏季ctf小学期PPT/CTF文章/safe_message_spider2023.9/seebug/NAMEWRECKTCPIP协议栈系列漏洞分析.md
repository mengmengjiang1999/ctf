**作者：启明星辰ADLab  
原文链接：<https://mp.weixin.qq.com/s/ThaUYbsWhCAfGXMVp21L2g>**

### 1\. 漏洞概述

2021年04月13日，Fourscore研究实验室与JSOF合作，披露了一组新的DNS漏洞，被称为NAME:WRECK。这些漏洞影响了四种流行的TCP/IP堆栈
--即FreeBSD、IPnet、Nucleus
NET和NetX，它们普遍存在于知名的IT软件和流行的IOT/OT固件中，并有可能影响全球数百万的物联网设备。
攻击者可以利用这些漏洞使受影响的设备脱机或对设备进行控制。

### 2\. 相关介绍

#### 1、DNS协议之压缩指针

在之前的文章中，我们介绍了基础的DNS协议，其中域名是由一连串的label组成的，如下图所示:

![
](https://images.seebug.org/content/images/2021/04/bb7e5998-ed45-4ab8-bfe3-7e9f15779c5a.png-w331s)

其中红框所示为每个label的长度，每个label最长为63字节，并且处理的时候，除了第一个长度字节，将每个长度字节替换为”.”，最后遇到null字节结束，从而组成了最后的域名。

不过在一些回复包中，会包含多次A记录或CNAME记录，这就造成了DNS数据过于冗长，因此DNS协议的设计者设计出了压缩指针。在压缩指针的机制中，通过指针指向之前出现过的一连串label从而达到压缩的目的。这个指针由两个字节组成，第一个字节的前两个bits为11，后面14个bits为偏移地址。

![
](https://images.seebug.org/content/images/2021/04/f47781af-5ad0-48df-95d6-01eaa14bb71f.png-w331s)

下面举一个具体的例子，如下图数据包所示，红框内为压缩指针，指向偏移0x0c的位置，也就是www.example.com的开头处。

![
](https://images.seebug.org/content/images/2021/04/92c4c6fa-6db5-45b5-be08-cd5f8b880694.png-w331s)

#### 2、DHCP协议

DHCP动态主机配置协议，前身是BOOTP协议，是一个局域网的网络协议，使用UDP协议工作，通常被用于局域网环境，主要作用是集中地管理、分配IP地址，使客户端动态的获得IP地址、Gateway地址、DNS服务器地址等信息，并能够提升地址的使用率。

DHCP报文共有8种，分别如下所示：

  * DHCPDISCOVER ：客户端开始DHCP过程发送的报文，是DHCP协议的开始。
  * DHCPOFFER：服务器接收到DHCPDISCOVER之后做出的响应，包括了给予客户端的IP（yiaddr）、客户端的MAC地址、租约过期时间、服务器的识别符以及其他信息。
  * DHCPREQUEST：客户端对于服务器发出的DHCPOFFER所做出的响应。在续约租期的时候同样会使用。
  * DHCPACK：服务器在接收到客户端发来的DHCPREQUEST之后发出的成功确认的报文。在建立连接的时候，客户端在接收到这个报文之后才会确认分配给它的IP和其他信息可以被允许使用。
  * DHCPNAK：DHCPACK的相反的报文，表示服务器拒绝了客户端的请求。
  * DHCPRELEASE：一般出现在客户端关机、下线等状况。这个报文将会使DHCP服务器释放发出此报文的客户端的IP地址。
  * DHCPINFORM：客户端发出向服务器请求一些信息的报文。
  * DHCPDECLINE：当客户端发现服务器分配的IP地址无法使用（如IP地址冲突时），将发出此报文，通知服务器禁止使用该IP地址。

DHCP数据包发送过程，如下图所示：

![ ](https://images.seebug.org/content/images/2021/04/f70c5582-e91b-47fa-ae29-23a679fa7b0d.png-w331s)

DHCP报文格式如下图所示：

![
](https://images.seebug.org/content/images/2021/04/31dd2d72-47bc-4ae1-8fba-d0db4bd352d5.png-w331s)

部分数据域定义，如下所示：

  * xid：随机生成的一段字符串，两个数据包拥有相同的xid说明他们属于同一次会话。
  * ciaddr：客户端会在发送请求时将自己的IP放在此处。
  * yiaddr：服务器会将想要分配给客户端的IP放在此处。
  * siaddr：引导程序中使用的下一个服务器的IP地址；由服务器在DHCPOFFER，DHCPACK中返回。
  * chaddr：客户端的MAC地址。
  * giaddr：如果需要跨子网进行DHCP地址发放，则在此处填入经过的路由器的IP地址。
  * sname：服务器主域名。
  * options：可以自由添加的部分，用于存放客户端向服务器请求信息和服务器的应答信息。

DHCP域搜索选项，该选项从DHCP服务器传递到DHCP客户端，以指定在使用DNS解析主机名时使用的域搜索列表。该选项的代码为119，格式如下图所示：

![
](https://images.seebug.org/content/images/2021/04/5e3929fd-c762-4821-89bb-f393cd9603f2.png-w331s)

举个例子，下图是“eng.apple.com”和“marketing.apple.com”组成的搜索列表的示例编码：

![
](https://images.seebug.org/content/images/2021/04/52d6f206-6dcc-410d-ae75-fe95f25ce300.png-w331s)

该示例编码已分为三个“域搜索选项”。
在客户端解析之前，所有域搜索选项在逻辑上都串联到一个数据块中。以第一个“域搜索选项”为例，第一个字节为119，第二个字节为9，表示后面Searchstring的长度，剩下的数据均为Searchstring。这三个“域搜索选项”的Searchstring组合成一个完整聚合块，可表示为：

|3|’e’|’n’|’g’|5|’a|’p’|’p|’l’|’e’|3|’c’|’o’|’m’|0|9|’m’|’a’|’r’|’k’|’e’|’t’|’i’|’n’|’g’|0xC0|0x04|。

“eng.apple.com”的编码以零结尾，以标记名称的结尾。“marketing”（针对marketing.apple.com）的编码以两个八位字节的压缩指针C004（十六进制）结尾，该指针指向DomainSearchOption数据的完整聚合块（从第一个“域搜索选项”中的Searchstring开始）中的偏移量4，其中另一个有效编码可以找到完整的域名（“apple.com”）。如下图所示：

![
](https://images.seebug.org/content/images/2021/04/8993c216-77b2-451e-9e18-434940498354.png-w331s)

每个搜索域名都必须以零或两个八位位组压缩指针结尾。如果接收器到达搜索列表选项数据的完整汇总块的末尾时正在通过搜索域名进行解码，而没有找到零或有效的两个八位位组压缩指针，那么必须将部分读取的域名视为无效域名。

### 3\. 漏洞分析

#### 1、Nucleus NET系列漏洞

![
](https://images.seebug.org/content/images/2021/04/15e8e4b7-56b6-4b6b-9736-4c07cd62510f.png-w331s)

上图为Nucleus
NET协议栈中的DNS_Unpack_Domain_Name()函数，这个函数用来处理DNS应答记录。第一个参数dst是指向一个buffer，用于拷贝解析的域名。第二个参数src指向域名的第一个字节，第三个参数指向DNS
Header的第一个字节。

代码通过while循环去解析域名（第7行），直到src为null字节，也就是域名的结尾。之后将第一个label的长度赋值给size（第9行）。下面，也就是最重要的一步就是检查该字节是否为压缩指针。如果不是，src指针前移一个字节，然后将src拷贝到dst。然后每个label之间加”.”。为正常的解析域名流程。如果是压缩指针而且是第一个压缩指针，retval加两个字节（第10，11行），然后根据偏移计算label起始位置，然后将长度赋值给size，之后正常处理。

这段代码看起来没有问题实际上包含4个非常严重的问题，其造成的漏洞编号分别为CVE-2020-27736、CVE-2020-27738、
CVE-2020-15795、CVE-2020-27009。

1.对label长度没有做验证

根据上文讲述的内容，每个label的第一个字节代表长度（第8，16行），但是程序没有检查这个长度是否代表真实数据包中label的长度，这可导致读取超过已分配结构体的buffer，造成拒绝服务。

2.对压缩指针的偏移没有做验证

根据上文讲述的内容，程序判断为压缩指针后，便会通过给出的偏移去寻找解析label（第14,15,16行），但是程序没有验证偏移的范围，这导致偏移值可以任意给定，这导致可以越界读写，从而RCE。

3.缺少NULL终止判定
根据RFC1035的表述，NULL字节(0x00)表示name的结尾（第7行）。但是在很多DNS解析程序中缺乏对NULL字节的验证，这导致攻击者可以通过控制NULL字节在特定的位置，通过和前几个问题相结合，同样可以实现可控的内存读写。

4.对域名的长度没有做限制

根据RFC1035的陈述，从DNS记录里提取的域名不应该超过255字节，尽管每个label限制了不超过63个字节（第15行），但是这只是一次性拷贝的长度，并没有限制实际拷贝的长度。

如下图所示，通过NU_Allocate_Memory()函数分配给name
255个字节个空间（第50行），即DNS_MAX_NAME_SIZE。后面调用DNS_Unpack_Domain_Name的过程中，显然可以通过构造恶意的数据包溢出这255字节。

![
](https://images.seebug.org/content/images/2021/04/25a3b810-2193-4dcd-84c5-d64bbec649ba.png-w331s)

所以根据以上内容，PoC的编写的思路有很多方法，比如可以让程序永远无法退出循环，类似下图：

![
](https://images.seebug.org/content/images/2021/04/15e25a91-bc8e-4274-9fce-098f4801e800.png-w331s)

c0为压缩指针，1e为偏移量，而偏移的位置正好重新指向c0，造成无限循环。

#### 2、FreeBSD漏洞（CVE-2020-7461）

该漏洞出现在dhclient解析DHCP数据包中的“域搜索选项”数据时，由于边界检查错误而导致堆溢出。dhclinet是FreeBSD系统中用于提供DHCP服务的二进制程序，执行命令：dhclient
em0便可进行DHCP配置，em0为网卡。源码位于sbin\dhclient\options.c，从do_packet()函数开始，代码清单如下图所示：

![
](https://images.seebug.org/content/images/2021/04/b29b37c8-90e2-4abf-84b3-9148e302d576.png-w331s)

该函数用于处理DHCP客户端接收到的数据包，行890，调用parse_options()函数解析数据包中的options，代码清单如下图所示：

![
](https://images.seebug.org/content/images/2021/04/813eb705-2407-4f40-928a-ca8f1b37d397.png-w331s)

行106，调用expand_domain_search()函数进一步解析DHCP域搜索选项数据，该函数进行两个操作，第一步操作是先获取所有域名标签的总长度，第二步操作是根据第一步获取的长度进行内存分配，并拷贝所有域名标签。

先看第一操作，如何获取所有域名标签的长度，关键代码实现如下图所示：

![
](https://images.seebug.org/content/images/2021/04/837127e2-6a42-4326-90bb-a7d74975c283.png-w331s)

首先判断options是否为空，不为空就获取options，行229，然后进入while循环，调用find_search_domain_name_len()函数处理options，该函数通过一个while循环逐个字节解析Searchsting并分类处理，第一种情况的关键代码实现如下图所示：

![
](https://images.seebug.org/content/images/2021/04/53ca0577-3c3a-4d48-9bd8-ebb71319bd4e.png-w331s)

如果读取到data[i]为0，表示域名标签的结尾，并返回该域名标签长度。接着第二种情况的关键代码实现如下图所示：

![
](https://images.seebug.org/content/images/2021/04/2bbb61de-58e0-4e66-81d1-7f9b8bed63ae.png-w331s)

如果读取到data[i]为0xC0，表示为压缩指针，指向另一个域名标签，行287，计算pointer，然后对该指针进行范围检查判断是否越界（第299行），递归调用find_search_domain_name_len()函数解析压缩指针指向的另一个域名标签（第301行），递归调用返回后，进行domain_name_len
+= pointer_len累加。如果既不是0结尾也不是压缩指针，则依次累加并移位游标，实现代码如下图所示：

![
](https://images.seebug.org/content/images/2021/04/d9281aad-e8a9-47f8-a81c-2566f8a22625.png-w331s)

在第299行和第301行之间是存在问题的，如果递归处理压缩指针指向的另一个域名标签不合法时，返回的pointer_len为-1，这里并没有将其视为无效并进行返回，而是依旧返回部分域名标签长度。

再看第二操作，分配缓冲区并进行域名标签拷贝，关键代码如下图所示：

![ ](https://images.seebug.org/content/images/2021/04/8f876b66-35d0-41ae-aa68-a60332af9318.png-w331s)

这里expanded_len为计算出来的域名标签的长度（第242行），分配一段内存（第248行），进入while循环，调用expand_search_domain_name()函数进行域名标签拷贝，实现代码如下图所示：

![
](https://images.seebug.org/content/images/2021/04/d7258760-c2e8-4bb0-8710-e2e55d94b145.png-w331s)

该函数和find_search_domain_name_len()函数实现基本是一样的，分类处理0结尾和压缩指针，但是在处理压缩指针的情况时，并没有判断指针范围的合理性。行366，调用memcpy进行域名标签拷贝，拷贝长度为label_len。

根据前文分析，第一步操作在递归处理压缩指针的情况时，是存在问题的，并没有丢弃包含无效压缩指针的域名标签。可以构造一个特殊的域名标签混淆lebal的递归解析，该域名标签表示为：|
1 |x3F|x00| 1 |'A'|xC0|x01|。

依次读取到label_len为0xC0时，进一步递归调用解析，这次读取到label_len为0x3f，将0x3f当成了域名长度，但是第305行，判断发生越界，因此返回-1。

![
](https://images.seebug.org/content/images/2021/04/5b6b1407-d7d9-4406-8b7a-7dab215b0b91.png-w331s)

但是这里仍然计算出domain_name_lan为1，因此第二个域名包含一个0x41。

![
](https://images.seebug.org/content/images/2021/04/a44a4de1-534a-450e-906d-14b95e5afaa9.png-w331s)

最后计算出expanded_len为0x5，如下图所示：

![
](https://images.seebug.org/content/images/2021/04/e076c65d-2361-475d-b038-f8361dc02b75.png-w331s)

然后开始进行第二步拷贝操作，先拷贝第一个domain：0x3f。如下图所示：

![
](https://images.seebug.org/content/images/2021/04/008138f8-7fca-4d7a-9a6f-918f5ceef271.png-w331s)

第二次拷贝第二个domain：0x41。如下图所示：

![
](https://images.seebug.org/content/images/2021/04/7e78d3b0-4334-4466-bc1a-1e10bba53a36.png-w331s)

递归解析压缩指针0XC004时，发生了混淆，如下图所示：

![
](https://images.seebug.org/content/images/2021/04/a1b0b723-a370-46c3-8008-3b1f414fa27c.png-w331s)

错误地将0x3f当成label_len，这明显是大于expanded_len的，直接拷贝导致溢出。不过在实际测试中，并未产生内存破坏，而可以构造其他的域名标签陷入无限递归，让dhclient进程堆栈耗尽导致崩溃，造成拒绝服务。

![
](https://images.seebug.org/content/images/2021/04/8da0220c-ecc5-4a39-b028-b3f7e95809a3.png-w331s)

### 4\. 处置建议

FreeBSD、Nucleus NET和 NetX，建议先实施以下安全建议，再及时更新设备供应商发布的安全更新。

安全建议：

  * 使用一些缓解信息来开发检测DNS漏洞的签名；
  * 发现并清点运行易受攻击堆栈的设备；
  * 实施分段控制和适当的network hygiene；
  * 监视受影响的设备供应商发布的补丁；
  * 配置设备依赖内部DNS服务器；
  * 监控所有网络流量中的恶意数据包。

### 5\. 参考链接

[1] <https://www.bleepingcomputer.com/news/security/name-wreck-dns-vulnerabilities-affect-over-100-million-devices/>  
[2] <https://www.freebsd.org/security/advisories/FreeBSD-SA-20:26.dhclient.asc>  
[3] <https://github.com/Forescout/project-memoria-detector>  
[4] <https://github.com/Forescout/namewreck>  
[5] <https://www.venustech.com.cn/new_type/aqtg/20210413/22594.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1572/>


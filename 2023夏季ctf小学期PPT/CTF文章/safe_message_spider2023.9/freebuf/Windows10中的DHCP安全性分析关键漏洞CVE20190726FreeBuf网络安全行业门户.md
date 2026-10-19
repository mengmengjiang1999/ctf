![1.png](https://image.3001.net/images/20190705/1562324926_5d1f2fbe297c2.png!small)

## 写在前面的话

**微软在今年一月份发布的更新，让公众对DHCP客户端中的关键漏洞CVE-2019-0547有了一个新的认识。这个漏洞的CVSS评分非常高，而且微软也没有立即发布相关的可利用性评价，因此用户也很难决定是否需要立即更新他们的系统。但是某些研究人员认为，这个漏洞在不久的将来很可能会被大量网络犯罪分子利用。**

因此，为了更好地检测针对DHCP漏洞的攻击以及相关的漏洞，并更新我们的产品，我们需要深入了解所有的细节。而我们要做的第一件事，就是网络侦察。

## 网络侦查

一开始我们打算使用搜索引擎来寻找关于该漏洞的信息，但并没有找到太多的细节，而且大部分内容都是来自MSRC网站发布的安全公告。不过在浏览这些安全公告的过程中，我们发现我们面对的是Window10（版本1803）中客户端和服务器端系统的一个内存崩溃漏洞，当攻击者向DHCP客户端发送专门设计的响应信息时，就会触发该漏洞。

![2.png](https://image.3001.net/images/20190705/1562324938_5d1f2fca531e0.png!small)

我们可以看到，MSRC给出的评分为2，被利用的可能性比较小，这意味着这个漏洞可能无法被利用，或者利用难度大。不过，我们还是想通过自己的分析，看看这个漏洞到底是什么情况。

在这个网站中，我们下载了这个安全更新补丁（.msu文件），将其解压，然后查找跟客户端处理DHCP响应相关的文件。但是这很困难，因为这个补丁包里面包含的是当月修复的所有漏洞补丁，而不是针对单个漏洞的补丁。在大量的文件中，我们用过滤器找到了几个匹配的代码库，然后对系统的版本进行了比较。其中，dhcpcore.dll库是最接近的：

![3.png](https://image.3001.net/images/20190705/1562324943_5d1f2fcf464fa.png!small)

实际上，只有DecodeDomainSearchListData这个函数进行了较大的改动，如果你熟悉DHCP协议的话，你就会知道它其实很少使用函数。

### DecodeDomainSearchListData函数

DHCP中的域名搜索选项号为0x77（119），它允许服务器再客户端上设置DNS后缀，但不适用于Windows设备，因为之前的Windows系统会忽略这个选项。在必要的时候，可以通过组策略来配置DNS的名称后缀。不过Windows
10在新版本1803中引入了针对域名搜索选项的处理库。

![4.png](https://image.3001.net/images/20190705/1562324951_5d1f2fd7805e9.png!small)

DecodeDomainSearchListData的处理过程如下：首先从服务器端接收信息，然后根据域名搜索选项的配置来解码数据。针对输入，它接收封装好的数据数组，并输出一个以空字节结尾的字符串，这个字符串包含由逗号分隔的域名列表。比如说，该函数会对下面这个域名后缀进行转换：

.eng.apple.com

.marketing.apple.com

    
    
    eng.apple.com,marketing.apple.com

DecodeDomainSearchListData会在UpdateDomainSearchOption的处理过程中被调用，并将返回的结果列表写入注册表键的"DhcpDomainSearchList"参数中：

    
    
    HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{INTERFACE_GUID}\

然后将主参数存储至特定的网络接口：

![5.png](https://image.3001.net/images/20190705/1562324971_5d1f2feb1a309.png!small)

DecodeDomainSearchListData函数会进行两次数据传递。第一次，它会执行除设置输出缓冲区进入点之外的所有操作，即计算保存返回数据所需要的内存大小。第二次，它会为数据分配内存，并进行数据填充。这个函数大约有250条指令，主要任务就是处理传入的字节流。它还会检查缓冲区的大小，如果大小为零，则不会为缓冲区分配内存，并完成执行然后返回错误信息：

![6.png](https://image.3001.net/images/20190705/1562324975_5d1f2fef60343.png!small)

因此，只有当目标缓冲区大小为零时，才可以触发漏洞。

## 漏洞利用

首先，我们可以使用重解析点来确保非空输入数据生成并输出一个空字符串：

![7.png](https://image.3001.net/images/20190705/1562324981_5d1f2ff5b51ff.png!small)

设置一个服务器来响应内容请求，并让未更新的客户端出现访问冲突。在每一个步骤中，函数完成一部分域名解析时，就会将这部分数据复制到目标缓冲区：

    
    
    1).eng.
    
    2).eng.apple.
    
    3).eng.apple.com.

接下来，当数据中出现大小为0的域名时，函数就会将目标缓冲区中的句号改为逗号：

    
    
    4).eng.apple.com,

然后继续解析：

    
    
    5).eng.apple.com,marketing.
    
    6).eng.apple.com,marketing.apple.
    
    7).eng.apple.com,marketing.apple.com.
    
    8).eng.apple.com,marketing.apple.com,

输入数据解析完成后，剩下的就是用空字符替换最后的逗号：

    
    
    9).eng.apple.com,marketing.apple.com

当攻击者发送如上所述的缓冲区数据时会发生什么呢？我们可以看到，它包含的列表是有一个空字符串组成的。那么在函数第一次计算输出数据大小后，由于数据并没有包含非零域名，所以大小为零。在第二次传递时，它会给数据分配堆内存块，并复制数据。但解析函数会立即遇到指示域名结尾的空字符，并将句号改为逗号。

![8.png](https://image.3001.net/images/20190705/1562324995_5d1f3003ee999.png!small)

因此，如果想要利用这个漏洞CVE-2019-0726，攻击者必须要在DHCP客户端上执行远程堆喷射，并对堆内存分布要有完整控制权。否则，将数据写入未选中的地址会导致svchost.exe进程崩溃。

 *** 参考来源：[ptsecurity](http://blog.ptsecurity.com/2019/05/dhcp-security-in-windows-10-analyzing.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


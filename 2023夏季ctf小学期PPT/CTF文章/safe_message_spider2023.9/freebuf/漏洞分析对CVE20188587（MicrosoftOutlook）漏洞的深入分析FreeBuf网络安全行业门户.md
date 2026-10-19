***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![image.png](https://image.3001.net/images/20190216/1550289949_5c678c1d25a10.png!small)  

## 写在前面的话

**MicrosoftOutlook是微软Office套件中的一个组件，它可以用来发送和接收电子邮件，管理联系人，记录和跟踪日程计划，或执行其他任务。近期，研究人员在Outlook
2010至Outlook 2019版本以及Office 365
ProPlus中发现了一个堆崩溃漏洞，Windows平台下的32/64版本均会受到该漏洞影响。攻击者可使用恶意RWZ文件来触发该漏洞，当Outlook收到恶意RWZ文件内容时，它只会分配少量堆内存，并且缺少恰当的边界检测，最终导致堆内存越界写入。**

## 复现漏洞

为了复现该漏洞，我们需要运行Microsoft
Outlook，然后点击“规则=>管理规则&警报=>选项=>导入规则”，选择可以触发Outlook崩溃的PoC文件。

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289622_5c678ad624110.png!small)  

下面给出的就是发生崩溃时的栈调用情况：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289632_5c678ae00c757.png!small)

## 分析漏洞

我们可以从栈调用数据中看到，当堆内存被释放时就发生程序崩溃了。因为我们无法判单堆释放时发生了什么情况，所以我们需要打开完整的堆内存页表来跟踪堆内存的数据变化，命令如下：

    
    
    YOUR_WINDBG_INSATALL_LOCATION\gflags.exe/p /enable outlook.exe /full

上述命令返回的结果如下，表明命令已成功执行了。

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289656_5c678af847399.png!small)

接下来，我们再次打开Outlook，选择PoC文件并监控崩溃发生时新的栈空间情况：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289665_5c678b0190c79.png!small)

现在我们可以看到，ECX指向的非0内存地址时不可读的，并且在向这个内存地址写入数据时会发生异常，很有可能是因为程序在尝试向未分配（或未释放）的内存地址写入数据。我们可以通过检测内存页分配情况来验证这种猜想，此时我们会看到内存仍然拥有Reserve属性：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289676_5c678b0c5a148.png!small)

现在我们需要弄清楚，为什么程序会向未使用的内存页写入数据。通过静态分析，我们可以看到ECX的值来自于EDI，而EDI貌似会在程序调用MAPIAllocateBuffer后被修改：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289689_5c678b1956ed1.png!small)

静态分析的结果表明，MAPIAllocateBuffer函数其实是RtlAllocateHeap的封装函数，而这个函数会确保请求的内存大小参数不会超过0x7FFFFFF7。但是，它无法检测该参数的值是否为0，因为实际分配的堆大小为8字节，超过了请求的堆大小，这8个字节填充值为0x0000000001000010。接下来，MAPIAllocateBuffer会返回这8个字节后面的堆地址。因此，在调用MAPIAllocateBuffer之后EDI的值为8
+ 分配的堆地址（来自RtlAllocateHeap）：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289707_5c678b2b92fcc.png!small)![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289709_5c678b2d41e2a.png!small)

根据上面的静态分析结果，我们可以大致判断导致漏洞出现的原因为整型溢出问题。通过调式后我们发现，调用MAPIAllocateBuffer时的堆大小参数为0，因为MAPIAllocateBuffer请求分配的堆大小为0+8=8，此时RtlAllocateHeap不会返回错误，而是返回正确的堆地址。MAPIAllocateBuffer会使用这8字节来写入地址0x0000000001000010，然后把无效的内存地址返回给用户：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289725_5c678b3d60125.png!small)

接下来，我们需要弄清楚请求的堆大小值为什么会变成0。原来，0值来自于当前的一个函数参数：arg_4(eax = arg_4 * 4 +
4)。但是，当这个函数被调用时，arg_4的值并非传递进来的参数值，这也就意味着arg_4的值被修改了。分析后我们发现，罪魁祸首是其子函数sub_65F7DA：

  
![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289742_5c678b4e86fa0.png!small)

在对子函数sub_65F7DA进行分析后，我们发现它也是一个封装函数。原来，这个函数是ReadFile，而arg_4得值实际上来自于PoC文件：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289763_5c678b6332f04.png!small)![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289766_5c678b6602d0c.png!small)![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289766_5c678b66a533c.png!small)

调试结果表明，arg_4读取到的文件内容为0xFFFFFFFF，因此堆内存的分配大小就是0xFFFFFFFF * 4 + 4 =
0（整型溢出）。然而，程序并不会检测这种错误，最终导致了越界写入的情况出现：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289787_5c678b7b84980.png!small)

在PoC文件中我们可以看到，并不存在0xFFFFFFFF这个值：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289804_5c678b8c77b21.png!small)

将其修改为0xAABBCCDD后再次进行调试，我们就可以证实溢出就是由这4个字节造成的：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289888_5c678be0c7e6f.png!small)![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289888_5c678be0ec70f.png!small)

在安装了修复补丁之后，我们对前后的程序代码进行了对比，我们发现补丁增加了对请求分配堆内存大小的验证：

![对CVE-2018-8587（Microsoft
Outlook）漏洞的深入分析](https://image.3001.net/images/20190216/1550289822_5c678b9e3fc02.png!small)

因此，广大用户请尽快安装更新补丁以防止攻击者利用该漏洞实施攻击。

### 漏洞信息

    
    
    MS.Outlook.CVE-2018-8587.Remote.Code.Execution

 *** 参考来源：[fortinet](https://www.fortinet.com/blog/threat-research/a-deep-analysis-of-the-microsoft-outlook-vulnerability-.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


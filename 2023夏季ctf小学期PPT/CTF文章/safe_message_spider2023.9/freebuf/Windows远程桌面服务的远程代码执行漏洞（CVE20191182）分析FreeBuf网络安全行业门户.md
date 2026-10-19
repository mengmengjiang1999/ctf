## 0x00 漏洞背景

019年8月14日微软官方发布安全补丁，修复了两个Windows远程桌面服务的远程代码执行漏洞CVE-2019-1181/CVE-2019-1182，这两个漏洞影响了几乎所有目前受支持的Windows系统。此漏洞是预身份验证且无需用户交互，这就意味着这个漏洞可以通过网络蠕虫的方式被利用。利用此漏洞的任何恶意软件都可能从被感染的计算机传播到其他易受攻击的计算机，与2019年5月14日修补的远程桌面服务的远程代码执行漏洞CVE-2019-0708和2017年WannaCry恶意软件的传播方式类似。  

## 0x01 分析环境

> 系统版本:Windows10 1903
>
> 补丁:windows10.0-kb4512508-x64_1893edc9a11d760be11e49d2500170ceee8026d7

## 0x02 成因分析

分别提取补丁前和补丁后RDS(Remote Desktop
Service)进程相关bin文件及相关驱动模块，经过ida和bindiff分析后定位到rdpbase.dll。该模块改动很少(只有一处函数差异)，可以很快定位到问题函数，如下图所示。

![T-1.jpg](https://image.3001.net/images/20191105/1572948867_5dc14b83cd4fe.jpg!small)

分析差异函数DecompressUnchopper::Decompress发现存在一处整型溢出漏洞

![T-2.jpg](https://image.3001.net/images/20191105/1572948871_5dc14b87ec2f7.jpg!small)

上图左边是patch之后的代码，右边是patch之前的代码，可以看到pcach之前指令eax+0x2000作为函数new的参数使用，patch后增加了对size的校验，会判断edx+0x2000是否大于edx,什么情况下一个值加上0x2000会大于之前的值呢？对于无符号整数来说当0xffffe000<size<0xffffffff时，size+0x2000将位于(0,0x2000)这个区间，size>size+0x2000.补丁后的反编译代码如下

![T-3.jpg](https://image.3001.net/images/20191105/1572948886_5dc14b967f77c.jpg!small)

patch的思路很简单，当size>size+0x2000时，new(-1)后续逻辑函数直接return。

下面我们根据DecompressUnchopper::Decompress的逻辑梳理一下该漏洞可能的利用思路。

![T-4.jpg](https://image.3001.net/images/20191105/1572949233_5dc14cf14ee8b.jpg!small)  

如上图所示，可以看到函数尾部调用了memcpy，第一个参数dest指向的内存为前面new分配的内存空间。如果我们把decompressedSize设置为[0xffffe000,0xffffffff]的一个值，当加上0x2000后decompressedSize小于原值，此时如果buff还是原来的大小，会导致memcpy的操作覆盖掉dest后面buff-(decompressedSize+0x2000)个字节，如果后面的地址空间保存有虚表指针之类的地址则可以导致控制流劫持。

## 0x03 poc构造

以上的分析基于对相关模块的逆向分析及靠经验猜测，为了验证思路是否正确首先需要能够有触达漏洞函数的rdp包。下面的叙述基于对CVE-2019-0708
poc的理解以及微软官方提供的rdp协议文档。

首先看一下微软的官方公告[1]：

![T-5.jpg](https://image.3001.net/images/20191105/1572949246_5dc14cfe8c752.jpg!small)

从公告的描述来看这个漏洞跟CVE-2019-0708类似，都可以造成蠕虫传播的效果，所以也是不需要进行登录认证即可利用该漏洞远程代码执行，感觉大部分代码可以复用所以决定在CVE-2019-0708的poc
[2]基础上构造CVE-2019-1182的poc。

通过研究CVE-2019-0708的poc和微软官方文档[3]可以了解到rdp协议的通信流程，如下图所示：

![T-6.png](https://image.3001.net/images/20191105/1572949265_5dc14d11701a8.png!small)

至此找不到触达漏洞函数的任何线索，思路还是要回到逆向漏洞函数周围的处理逻辑上。交叉引用并没有发现对DecompressUnchopper::Decompress的静态调用，搜索一下DecompressUnchopper这个类相关的函数：

![T-7-1.jpg](https://image.3001.net/images/20191105/1572949350_5dc14d66d86dc.jpg!small)

经过分析发现是DecompressRdp8__CreateInstance这个函数创建了DecompressUnchopper对象，继续查看DecompressRdp8__CreateInstance没有找到对此函数的静态调用，发现这个函数是个导出函数，最后经过搜索发现该函数在rdpserverbase.dll中进行了导入，交叉引用发现有两处调用  

![T-7.jpg](https://image.3001.net/images/20191105/1572949275_5dc14d1be8ae6.jpg!small)

上图中可以看到是在CRdpDynVC这个类的成员函数中进行了调用，因此猜测可能和rdp的dvc(Dynamic Virtual
Channel)信道有关，关于dvc信道的详细信息可参考微软官方文档[4]。通过查阅官方文档初步定位到通过dvc信道发送加密数据可能会触达漏洞函数。

dvc信道的建立流程如下：

(1) dvc init.

![T-8.png](https://image.3001.net/images/20191105/1572949365_5dc14d7571c8e.png!small)

(2) dvc open

![T-9.png](https://image.3001.net/images/20191105/1572949384_5dc14d88d8eb1.png!small)

(3) dvc send&recv data

![T-9.png](https://image.3001.net/images/20191105/1572949401_5dc14d994b36a.png!small)

dvc信道可分片传输超大数据(最大不超过2^32-1字节)，并支持非加密和加密数据传输。

![T-11.jpg](https://image.3001.net/images/20191105/1572949451_5dc14dcb34684.jpg!small)

(4) dvc close

![T-10.png](https://image.3001.net/images/20191105/1572949410_5dc14da2b435b.png!small)

基于以上的研究，下面尝试构造一个可触达漏洞函数的dvc pdu。加密的dvc pdu结构如下图所示，详细信息参见官方文档。

![T-12.jpg](https://image.3001.net/images/20191105/1572949469_5dc14ddd6d0c4.jpg!small)

发送的数据包：

    
    
    dvc_send = ( #pdu header"0300004002F08064000503EC70322A00000003000000" #1st byte cid length
    "68" + channel_id[-2:] + "01110000"#data
    "414141414141414141414141414141414141414141414141414141"
    "414141414141414141414141414141414141414141414141414141"
    "414141414141414141414141414141414141414141414141414141"
    "414141414141414141414141414141414141414141414141414141"
    "414141414141414141414141414141414141414141414141414141" 
    "414141414141414141414141414141414141414141414141414141") tls.sendall(Packer(dvc_send).bin_unpack())

对DecompressUnchopper::Decompress下断，运行脚本，触发断电，证明之前的猜测是正确的。

![T-13.jpg](https://image.3001.net/images/20191105/1572949485_5dc14ded0ffb1.jpg!small)

通过调试分析及参考官方文档，构造如下数据包可导致crash:

    
    
    dvc_send2 = ("0300004002F08064000503EC70322A00000003000000" "68" +channel_id[-2:] + "01E0FFFF" "e122550e0ffff080000002690ce0a2b9f6401070000002630d2b4fc0402") tls.sendall(Packer(dvc_send).bin_unpack()) 

崩溃现场：

![T-14.jpg](https://image.3001.net/images/20191105/1572949500_5dc14dfc45e4b.jpg!small)

调试分析导致crash的原因如下:DecompressedSize为0xffffe001,加0x2000之后为1，new(1)分配了一个字节的堆空间，memcpy多次像new分配的内存拷贝数据，导致数据一直向后覆盖，图中覆盖到了RdpBoundsAccumulator对象，当执行clear操作时访问无效地址造成memory
corruption。

关于利用的一些思考：精准控制memcpy拷贝长度，覆盖到某对象的虚表指针或其他可劫持控制流的内存单元，可导致任意代码执行，需要考虑cfg等漏洞利用缓解措施的bypass。

### References:

[1] <https://msrc-blog.microsoft.com/2019/08/13/patch-new-wormable-vulnerabilities-in-remote-desktop-services-cve-2019-1181-1182/>

[2] <https://github.com/algo7/bluekeep_CVE-2019-0708_poc_to_exploit>

[3] <https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/5073f4ed-1e93-45e1-b039-6e30c385867c>

[4] <https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpedyc/3bd53020-9b64-4c9a-97fc-90a79e7e1e06>


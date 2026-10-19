## 专栏·供应链安全

数字化时代，软件无处不在。软件如同社会中的“虚拟人”，已经成为支撑社会正常运转的最基本元素之一，软件的安全性问题也正在成为当今社会的根本性、基础性问题。

随着软件产业的快速发展，软件供应链也越发复杂多元，复杂的软件供应链会引入一系列的安全问题，导致信息系统的整体安全防护难度越来越大。近年来，针对软件供应链的安全攻击事件一直呈快速增长态势，造成的危害也越来越严重。

为此，我们推出“供应链安全”栏目。本栏目汇聚供应链安全资讯，分析供应链安全风险，提供缓解建议，为供应链安全保驾护航。

注：以往发布的部分供应链安全相关内容，请见文末“推荐阅读”部分。

## 前言

2020年12月和2021年2月，微软两次针对“照片”应用的Raw格式图像编码器发布安全更新，其中2月9日修复的是CVE-2021-24091。笔者从事文件格式方面的安全研究工作，找到研究人员提供的poc
后，对该漏洞进行了漏洞验证和分析。

根据MSRC 和漏洞发现者公开的信息，该漏洞存在于Windows Imaging Component解码Olympus E300
相机拍摄的原始图像的相关函数中。由于互联网并没有过多公开资源介绍 E300 RAW
格式（笔者仅找到一份公开资料，见https://myolympus.org/E300/#RAW），所以本文将从漏洞产生机制的角度，分析漏洞产生的原因。

## 0x00 漏洞验证

1、在Win10 1903
x64系统上，使用gflags工具为图片app开启页堆，双击图片文件打开（图片默认应用为照片App）。一段时间后，App退出进程。

2、使用Windbg附加照片App（Windbg 调试UWP方法详见微软文档），敲击g运行程序。一段时间后，进程崩溃。如下图所示：

![1617156486_6063d986a3a5104881fc6.png!small?1617156486928](https://image.3001.net/images/20210331/1617156486_6063d986a3a5104881fc6.png!small?1617156486928)

## 0x01 漏洞分析

使用ida pro 加载崩溃的dll，可以确认崩溃发生在一个将数据写入缓冲区的循环之中。

![1617156495_6063d98fbe3815c4add6f.png!small?1617156496036](https://image.3001.net/images/20210331/1617156495_6063d98fbe3815c4add6f.png!small?1617156496036)

通过这段代码，可初步大致判断循环体条件语句导致循环次数过多，造成越界写入。函数部分变量的初始化如下：

![1617156502_6063d996e774fd76c9432.png!small?1617156503456](https://image.3001.net/images/20210331/1617156502_6063d996e774fd76c9432.png!small?1617156503456)

结合函数开始时局部变量的初始化和变量交叉引用的情况来看，可以得出：

1、代码通过读取某个类型对象的成员值，并加以运算，计算结果即为需要申请的缓冲区的大小；

2、缓冲区分为两部分，一部分为size 为*(this+12320*4) *
2的数据块（chunk2）另一部分数据块（chunk1）的大小为*(this+0x12320*4) * 16 / 10个字节。

![1617156511_6063d99fa99ba23237276.png!small?1617156511949](https://image.3001.net/images/20210331/1617156511_6063d99fa99ba23237276.png!small?1617156511949)

3、执行初始化后，代码首先执行一个for循环，在这个循环体的内部执行另一个for循环，向chunk2内写入数据。

所以，这段代码的伪代码如下：

    
    
    chunk2_size = this->mem_12320;chunk1_size = chunk2_size * 16 / 10;char * data = (char *)malloc(chunk1_size + 2 * chunk2_size);for (char *i = data+chunk1_size; v12 < this->mem_12325; a5 = v12){…expresions;…for (char *pdata = data, char *j = i; j < chunk+chunk1_size+2*chunk2_size; pdata += 3, j += 4){if ((pdata – data) %15) pdata++;*(word *)j = pdata[1] << 8 | pdata[0];      //写入两个字节*(word *)(j+1) = pdata[2] << 4 | pdata[1] >> 4; //写入两个字节 }…expressions;…}

按照上面的伪代码，每次循环都写入四个字节，循环次数应该是(chunk2_size * 2 / 4)向上取整的值。在第一个for循环中，当 i =
&data[chunk1_size]，即从第二个chunk头部开始循环写入字节时，如果chunk2_size为奇数，循环次数 * 4
将大于chunk2_size。也就是说，最后一次循环中，写入后两个字节时，将造成越界，产生访问违例。

## 0x02 漏洞调试

使用windbg 附加App进程，并在崩溃函数设置断点：

    
    
    bu WindowsCodecsRaw!COlympusE300LoadRaw::olympus_e300_load_raw

图片App 加载poc 文件时，获取的chunk2_size为0xd79,是一个奇数。

![1617156538_6063d9ba32525d15f7586.png!small?1617156538429](https://image.3001.net/images/20210331/1617156538_6063d9ba32525d15f7586.png!small?1617156538429)

通过上文的伪代码可得：

chunk1_size = 0x158e

data 指向的内存区域是一个大小为0x3080的缓冲区。

![1617156527_6063d9af9cf4a3316f9db.png!small](https://image.3001.net/images/20210331/1617156527_6063d9af9cf4a3316f9db.png!small)

代码执行到第二个for循环时，需要写入数据的指针存放在r15中，即为chunk2 缓冲区的起始地址（r15 == data + chunk1_size）：

![1617156557_6063d9cd1b154d66d1f52.png!small?1617156557332](https://image.3001.net/images/20210331/1617156557_6063d9cd1b154d66d1f52.png!small?1617156557332)

所以，在这种情况下，循环次数应为⌈ (0xd79 * 2 / 4) ⌉，即为1725 次。而缓冲区只有2 * chunk2_size,
共6898个字节，不能支持1725*4 = 6900个字节的写入。由此可知，最后一次循环将产生两个字节的越界。至此，漏洞分析完毕。

循环次数记录如下：共命中725次，与分析无误。

![1617156597_6063d9f5bc4273d638b14.png!small?1617156598190](https://image.3001.net/images/20210331/1617156597_6063d9f5bc4273d638b14.png!small?1617156598190)

## 0x03 关于这段代码的来源

该漏洞的发现者提到：通过函数名查找，这段代码与LibRaw
Lite库的同名函数有较大的相似性，但是这个库目前已经停止维护和更新了，源代码下载地址失效，所以笔者在github上找到了类似的代码片段。(https://github.com/coolshou/DIR-850L_A1/blob/92b64054ac75795429b9a6678baef5b3e69dfc10/progs.gpl/image_tools/netpbm-10.35.81/converter/other/cameratopam/camera.c)

![1617156611_6063da03ab33b2663f30c.png!small?1617156612030](https://image.3001.net/images/20210331/1617156611_6063da03ab33b2663f30c.png!small?1617156612030)

对比可知，这段代码与漏洞函数在实现上基本一致，所以微软的代码应该是在此基础上重新实现了一遍。

因此， **基于代码供应链安全的考量，建议使用LibRaw Lite 库函数的代码，由相关人员自行更新补丁。**

## 0x04 微软代码补丁

微软官方在2月9日推出的补丁内容如下：

![1617156621_6063da0d96f2803a39b3a.png!small?1617156621829](https://image.3001.net/images/20210331/1617156621_6063da0d96f2803a39b3a.png!small?1617156621829)

这个补丁比较简单粗暴，即：复制第二个像素（第二次写入双字节）时，判断指针是否指向缓冲区末端。

## 0x05 小结

笔者认为这个函数也存在其它问题。首先，从分析来看，缓冲区分配基于16个字节对齐的原则，而如果计算错误，不确定是否会导致像素解析不完全或产生其它影响；其次，由于在执行free之前，并没有对解析的像素数量进行判断，因此如果文件大小不符合规范，可能会将未初始化的数据解码，并产生意外的像素值。由于笔者对olympus
e300 raw格式了解粗浅，所以并没有从poc 文件构造方式的角度进行解读，仅给出漏洞产生的原因。希望大家多多交流。

 **推荐阅读**[Windows DNS Server 远程代码执行漏洞 (CVE-2021-24078)
的详细原理分析](http://mp.weixin.qq.com/s?__biz=MzI2NTg4OTc5Nw==&mid=2247501430&idx=1&sn=79490c44228e33e2837c2d3cc9abe989&chksm=ea94f71cdde37e0a7ef08e3f21735c8c19683a5eda1a3584be379d284d7a98f0cb9280d8a9dc&scene=21#wechat_redirect)[FireEye
红队失窃工具大揭秘之：分析复现SolarWinds RCE 0day
(CVE-2020-10148)](http://mp.weixin.qq.com/s?__biz=MzI2NTg4OTc5Nw==&mid=2247499899&idx=1&sn=3fce06e76234bb30825c048e57fc2cbe&chksm=ea94f111dde37807f8c51f88287fcd5c09dcd0f3e991e1f3152bb4eb07cb1a6a85ad37e8196f&scene=21#wechat_redirect)[APACHE
OFBIZ XML-RPC 反序列化漏洞 (CVE-2020-9496)
的复现与分析](http://mp.weixin.qq.com/s?__biz=MzI2NTg4OTc5Nw==&mid=2247499436&idx=1&sn=9840c0d3081395075594f458f389e90e&chksm=ea94cfc6dde346d0d098a2ad1c162a43b1823bb74a58f73f3295f6af5f36f7e7aba53d77d3be&scene=21#wechat_redirect)

题图：Pixabay License

 **转载请注明“转自奇安信代码卫士 https://codesafe.qianxin.com”。**


***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：TueurCalme，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  

## 0\. 前言

 **上个周末在 FreeBuf 上看到[Adobe Acrobat
Reader中存在远程代码执行漏洞](http://www.freebuf.com/news/163795.html)
这篇文章后，决定自己尝试去复现一下这个漏洞，至少能弹个计算器吧，结果一些事情出乎意料，这里把自己的研究过程写下来。**

## 1\. POC构造

根据国外的一篇文章
[talos](https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0505)
中介绍,漏洞原理是在 pdf 中 trailer
内部的ID字段如果过长，在执行JavaScript脚本this.docID的时候会触发漏洞，漏洞模块位于一个dll文件EScript.api中。那么，是应该先构造javaScript还是先构造trailer后面的ID呢？javaScript我是通过Acrobat
Pro DC添加上去，如果先构造trailer，那么会被Acrobat Pro
DC修复，所以先构造javaScript。另外，最初的文档怎么才能包含trailer呢？说实话之前并不熟悉pdf文件格式，在进行了很多尝试之后，发现使用wps将空白doc文档转化为pdf之后，文档很简洁，并且包含有trailer。那么流程就很清晰了：

###  **1.1 生成包含trailer的pdf**

**![1.1生成包含trailer的pdf.png](https://image.3001.net/images/20180310/15206528946493.png!small)**

**![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206529932591.png!small)**

###  **1.2 javaScript的构造**

使用Acrobat Pro
DC编辑刚刚生成的文件，使用javaScript工具，在保存pdf文件的这个动作的时候添加javaScript命令this.docID即可。

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/1520653041894.png!small)

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206530542345.png!small)

###  **1.3 trailer的构造**

在保存上面的文档后，使用notepad打开文档，将trailer后面的ID改为 ,需要更改的地方有两处。

![5.png](https://image.3001.net/images/20180310/15206531225401.png!small)

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206531569517.png!small)

### 1.4 poc效果

注意前面构造的javaScript是在保存文档的时候触发，但是如果开启沙盒，保存文档时就总是弹出另存为进而无法触发漏洞，所以要先设置Adobe,[ADOBE
保存PDF文件，总是弹出另存为的解决办法](https://jingyan.baidu.com/article/46650658c24d65f549e5f887.html)

测试：在文档中添加注释，然后点击保存，Adobe崩溃，模块为EScript.api

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206532101069.png!small)

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206532347235.png!small)

## 2\. 调试分析

###  **2.1 崩溃原因**

使用OD载入AcroRd32.exe，并打开文档，之后就在模块中就可以看到EScript，根据TALOS的那篇文章，在其中搜索触发漏洞的代码。

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206759167607.png!small)

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206759964440.png!small)  

这段代码简单的说就是，我们构造的样本中ID的字符串已经被转化为16进制数了，hexStr("AAAAAA..") -> hexArray（0xAA
0xAA....），而触发漏洞的这一块是将hexArray（0xAA 0xAA....）又转为hexStr("AAAAAA..") .

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206760551908.png!small)  

但是漏洞具体是如何触发的需要结合动态调试，在循环开始出下断点，和之前触发崩溃的方式进行相同的操作，程序会断在断点处，可以获得如下图所示的初始信息。

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206760999463.png)  

一开始，edx指向hexStr，edi指向hexArray，并且hexStr的首地址就在hexArray首地址上方0x100的地方。esi是循环的次数。

具体看看每一项的数据的情况：

> hexStr是目的地，也就是它没过返回地址；
>
> hexArray很奇怪，只有0x80个0xAA,我们传入了0x200个‘A’,那么理应由0x100个0xAA；
>
> esi是循环次数，值为0x100,正好符合我们的预期。

假如没有啥保护机制,我们要淹没的返回地址是0x2Bc8c8处的0x693a3168

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206762293219.png!small)

进一步观察，0x80个0xAA正好转化为0x100个‘A’,那么执行0x80次，就应该会到hexArray首地址之前了。这里下一个条件断点，让它执行0x80次

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206763681737.png!small)

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206775033108.png!small)  

但是一切还会往后继续，如果再执行0x40次，那么hexArray就会被自己后面的数据给覆盖。同样下条件断点，再执行0x40次

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206764314671.png!small)

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206764348517.png!small)

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206764386209.png!small)  

记得之前要淹没的返回地址吗，它在这个地方

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206765687527.png!small)  

那么只要再执行0xC次，它就会被覆盖了

![关于CVE-2018-4901的研究690](https://image.3001.net/images/20180310/15206766109907.png!small)  

同样是下条件断点，继续执行

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206766614748.png!small)

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206776977778.png!small)  

地址被覆盖为0x30303030了

而触发漏洞代码片段下方的两个函数分别是string()和__security_check_cookie，这里先不去管它。因为我们能控制的只有0x80,是真的只有0x80吗?

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206767199813.png!small)  

### **2.2 疑问**  

结合IDA来分析分析

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206768648495.png!small)  

可以看到，在漏洞触发之前HexArray的数据来源有两种情况：  

> 1.memcpy(&v17, v14, (size_t )&v15[1]);
>
> 2.nCircleIndex = ((int (__cdecl **)(int, int, char , signed
> int))(dword_23A59CB0 + 320))(a2, a3, &v17, 0x80);

对于1，(size_t )&v15[1]在其上的if判断中被限制为<=0x80.

对于2，其中的参数被设置为0x80.

对于第2种情况，我们还需要调试来验证是否是这个参数限制了hexArray

###  **2.3 OD动态调试验证**  

我们在push 0x80下断点重新触发漏洞中断下来了，说明hexArray的数据来源是第二种情况，然后我们将push 0x80改为push 0x100

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206770865102.png!small)

执行到漏洞开始处，内存转到edi，发现现在有0x100个0xAA了，说明之前的判断是正确的  

![关于CVE-2018-4901的研究](https://image.3001.net/images/20180310/15206778505969.png!small)  

## 3\. 结论

我们能够控制的只有拷贝的次数和拷贝的前0x80个字节HexArray的内容。而函数分配给HexStr
0x100固定大小的栈空间，程序流程是HexArray转化到HexStr，所以我们可控的能覆盖的空间也就只有HexStr那一块空间。以上是我关于CVE-2018-4901的研究。另外，经过尝试,不是trailer，其他标签下的ID如果超长也会出发漏洞。行文匆匆，如果有误，还请多多指正。

 ***本文作者：TueurCalme，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


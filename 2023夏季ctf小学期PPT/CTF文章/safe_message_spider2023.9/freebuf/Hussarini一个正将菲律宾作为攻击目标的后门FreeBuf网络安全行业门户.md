![1.png](https://image.3001.net/images/20180814/1534215002_5b72435acb06d.png!small)

## 写在前面的话

 **就在两周之前，FortiGuard安全实验室发现了一份名为“Draft PH-US Dialogueon Cyber
Security.doc”的可疑文件，而这个名字中带有政治色彩的恶意文档利用了漏洞CVE-2017-11882，一旦攻击成功，它将会向目标主机的%temp%目录中投放恶意软件。**

研究人员的分析表明，这份恶意文件属于Hussarini（又名Sarhust），从2014年开始，很多网络犯罪组织都在各自的APT攻击中使用这款后门来对东盟各国实施攻击。研究报告指出，在这一系列攻击活动中，受影响最大的为菲律宾。

## 恶意文档分析

首先，我们对这个标题为“Draft PH-US Dialogue on Cyber
Security.doc”的恶意文档进行了分析。它利用的是漏洞CVE-2017-11882，一旦利用成功，恶意文档将会向目标主机的%temp%目录中投放下列恶意软件：

    
    
    ·       Outllib.dll
    
    ·       OutExtra.exe

OutExtra.exe是一个由微软签名的合法应用程序，这个文件是MicrosoftOffice套件中的一个组件，可以用来寻找Outlook数据文件中的关键词。但是在此次攻击中，该文件主要用来通过DLL劫持技术加载Hussarini后门。

很多APT恶意软件都会使用到DLL劫持技术，这种技术不会通过合法应用程序来加载正常的DLL，而是利用合法应用来加载包含了恶意代码的DLL。这样一来，恶意软件就能够绕过主机入侵防御系统（HIPS）并执行恶意操作了。大多数HIPS工具使用的都是白名单机制，因此会忽略那些使用了DLL劫持以及拥有合法签名的应用，OutExtra.exe就是如此，接下来，它便会加载上面那个伪装成合法Outllib.dll的恶意文件。

### 诱饵文件

为了不让目标用户起疑心，恶意软件会从一个看似正常的地址（hxxp://157.52.167.71:29317/office/word/2003/ph2/philip.varilla）下载一份诱饵文件。在我们的分析过程中，这个诱饵文件托管地址已经无法访问了。但是我们可以从URL中发现，“ph”应该指的是菲律宾（ph-Philippines），2指的是第二个版本的诱饵文档。在Google上搜索一番之后，“philip.varilla”这个名字竟然跟菲律宾省信息通信技术司（DICT）司长有关，而这个部分负责的是菲律宾国内的信息通信技术领域，其中也包括网络安全在内。

## Hussarini

实际上，Outllib.dll就是Hussarini后门，这个dll可以导出包含了恶意代码的函数，当OutExtra.exe执行之后，会调用其中的某些函数，并执行相应的恶意代码。

![2.png](https://image.3001.net/images/20180814/1534215057_5b7243910c234.png!small)

虽然原始的Outllib.dll也有上述的某些功能，但是这个后门的功能要远远强于后门dll。

![3.png](https://image.3001.net/images/20180814/1534215063_5b7243974dd04.png!small)

而且各自的文件大小也不同，原始的Outllib.dll只有4-8MB（取决于不同版本），伪造的文件只有40-50KB。造成文件大小不同的其中一个原因是后门DLL中只有一个导出函数包含恶意代码，因此我们的分析将主要集中在这个包含了后门代码的函数-RenInitInstance@12。

这个函数首先初始化了一个类来设置bot，然后创建了两个并发线程，并以创建的bot对象作为参数：

![4.png](https://image.3001.net/images/20180814/1534215070_5b72439e6775d.png!small)

第一个线程是一个客户端线程，负责跟命令控制服务器进行通信，并监听命令。第二个线程负责解析并向worder传递响应信息，worker线程负责执行命令并向客户端线程报告结果。

在跟C&C服务器通信之前，恶意软件会在注册表中保存一个ServerID（随机生成的值），这个ID用于在僵尸网络中识别bot身份。

![5.png](https://image.3001.net/images/20180814/1534215077_5b7243a5b1ca5.png!small)

## C&C通信

有趣的是，代码中包含了一个私人IP（10.1.0.105），这很可能是当初用来测试的C&C服务器，这个IP会在运行时过程中被替换成真正的地址（publicdfaph.publicvm.com）。

在通信过程中，Hussarini使用了自定义的协议（Base64编码），数据通过HTTP发送：

![6.png](https://image.3001.net/images/20180814/1534215091_5b7243b3b6ccb.png!small)

从协议结构中，我们可以看到生成的ServerID、数据大小和消息的校验和。数据采用了Base64编码，并作为一个参数在HTTP Get请求中传递。

![7.png](https://image.3001.net/images/20180814/1534215103_5b7243bf353c9.png!small)

C&C的响应包含在<CHECK></CHECK>标签中，同样采用了Base64编码，解码后我们可以看到类似的数据结构：

![8.png](https://image.3001.net/images/20180814/1534215126_5b7243d6e48ec.png!small)

校验之后，恶意软件便会获取下列系统信息，并通过HTTP POST请求进行发送：用户名、主机名、操作系统及CPU信息。

![9.png](https://image.3001.net/images/20180814/1534215134_5b7243dec4af6.png!small)

C&C发送的命令包含在<COMMAND></COMMAND>标签中，在解码之后我们发现命令的数据结构其实跟通信协议的数据结构是相同的。

![10.png](https://image.3001.net/images/20180814/1534215142_5b7243e6d58cb.png!small)

第一个命令包含字符串“cache.txt“，并且会调用worker线程来创建下列文件（恶意软件所在目录）：

    
    
    ·       cache.txt
    
    ·       cache.txt.cfg

第二个命令包含cmd命令：

![11.png](https://image.3001.net/images/20180814/1534215160_5b7243f8cf7e5.png!small)

C&C将会发送下列命令，并传递给worker线程，最后写入到cache.txt文件中：

![12.png](https://image.3001.net/images/20180814/1534215170_5b724402cc1df.png!small)

Hussarini利用了动态域名来保持恶意活动的匿名性，但是我们在分析的过程中，我们只看到样本解析到了IP地址157.52.167.71，而这个地址也是托管诱饵文档的地址。

![13.png](https://image.3001.net/images/20180814/1534215179_5b72440b0f710.png!small)

## 入侵威胁指标IoC

### SHA256:

    
    
    154261a4aab73f1ceef28695d8837902cc1e8b5cca0b8fc81ddeda350564adc0- MSOffice/CVE_2017_11882.A!tr
    
    05dcc7856661244d082daa88a074d2f266c70623789a7bb5a919282b178d8f98- W32/Sarhust.D!tr

### CC:

    
    
    hxxp://157.52.167.71:29317/office/word/2003/ph2/philip.varilla
    
    hxxp://publicdfaph.publicvm.com:8080/

 ***参考来源：[fortinet](https://www.fortinet.com/blog/threat-research/hussarini---targeted-cyber-attack-in-the-philippines.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


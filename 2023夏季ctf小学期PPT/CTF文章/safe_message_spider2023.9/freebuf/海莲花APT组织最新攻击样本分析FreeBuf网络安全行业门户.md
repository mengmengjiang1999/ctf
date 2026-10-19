## **0x1 概况**  

**海莲花（OceanLotus）也叫APT32或APT-C-00，是一个长期针对中国及其他东亚国家（地区）政府、科研机构、海运企业等领域进行攻击的APT组织。近日腾讯御见威胁情报中心捕获到了一个该组织的最新攻击样本。在本次攻击事件中，该组织使用了CVE-2017-11882漏洞并结合白签名利用程序来最大化隐藏自己的后门木马。后门木马将常驻用户电脑，并根据云控指令伺机窃取机密信息或进行第二阶段攻击。**

![1.png](https://image.3001.net/images/20180427/15248169205010.png!small)

（攻击流程图）

##  **0x2 载荷投递**

本次攻击时使用了CVE-2017-11882漏洞文档，诱饵文档文件名为《Document_GPI Invitation-UNSOOC
China.doc》，内容为一模糊的图片。

![2.png](https://image.3001.net/images/20180427/15248169324796.png!small)

（诱饵文档）

漏洞触发后，公式编辑器进程会在“C:\Program Files\Microsoft-Windows-DiskDiagnosticResolver_2021325962”目录下释放MicrosoftWindowsDiskDiagnosticResolver.exe、OUTLFLTR.DAT、rastls.dll
3个文件。其中MicrosoftWindowsDiskDiagnosticResolver.exe有有效签名，原始名为dot1xtra.exe，这是典型的白加黑利用技术，带有效签名的exe运行后会自动加载木马文件rastls.dll。

![3.png](https://image.3001.net/images/20180427/15248169471313.png!small)

（签名信息）

![4.png](https://image.3001.net/images/20180427/15248169611428.png!small)

（文件详细信息）

##  **0x3 RAT分析**

###  **1.rastls.dll 行为分析**

该组织在本次攻击中使用的关键模块文件都加入了大量混淆，混淆代码如下所示。此dll会在DLLMain函数中加载OUTLFLTR.DAT，进行解密后得到一段shellcode。接着会将宿主exe即MicrosoftWindowsDiskDiagnosticResolver.exe
0x401000（默认基址为0x400000）开始的一大片代码修改为无实际作用的指令，宿主exe
oep位置的指令也被修改了。当宿主exe从OEP位置开始执行时，就会跳转到木马的shellcode部分。

![5.png](https://image.3001.net/images/20180427/15248169966764.png!small)

（混淆代码）

![6.png](https://image.3001.net/images/20180427/15248170061959.png!small)

（宿主exe 0x401000处被修改后的指令）

![7.png](https://image.3001.net/images/20180427/15248170197958.png!small)

（宿主exe 被修改后OEP附近的代码）

![8.png](https://image.3001.net/images/20180427/1524817033138.png!small)

（rastls.dll 跳转到shellcode执行）

OUTLFLTR.DAT中的shellcode被执行后，会自加载shellcode中存储的一个名为{92BA1818-0119-4F79-874E-E3BF79C355B8}.dll。接着执行此dll的导出函数DllEntry。

![9.png](https://image.3001.net/images/20180427/15248170478576.png!small)

（dll内部名称及导出函数）

{92BA1818-0119-4F79-874E-E3BF79C355B8}.dll
又会从资源中解密出木马功能文件{A96B020F-0000-466F-A96D-A91BBF8EAC96}.dll，并自加载此dll，执行此dll的导出函数DllEntry。

![10.png](https://image.3001.net/images/20180427/1524817074235.png!small)

（木马功能文件导出函数及内部文件名）

###  **2\. {A96B020F-0000-466F-A96D-A91BBF8EAC96}.dll 行为分析**

该dll执行后，会解密资源得到木马的c2等配置信息及3个通信相关的dll，名称分别为HttpProv.dll、DnsProvider.dll、HttpProv.dll。每个通信dll都导出一个"CreateInstance"函数。

![11.png](https://image.3001.net/images/20180427/15248170866468.png!small)

（加载资源）

![12.png](https://image.3001.net/images/20180427/15248170961319.png!small)

（解密资源）

![13.png](https://image.3001.net/images/20180427/15248171093008.png!small)

（解密资源的函数代码片断）

![14.png](https://image.3001.net/images/20180427/15248171204980.png!small)

（资源解密后的明文内容）

将解密后的资源进行分析后得到资源中各字段的值及部分含义

**字段序号** |  **字段内容**  
---|---  
1  |  Unicode 字符串“ghijklmnop”  
2  |
Unicode字符串，注册表键值“SOFTWARE\App\AppXbf13d4ea2945444d8b13e2121cb6b663\Application”  
3  |
Unicode字符串，注册表键值“SOFTWARE\App\AppXbf13d4ea2945444d8b13e2121cb6b663\DefaultIcon”，存储发包时用的guid  
4  |  Unicode字符串“Data”  
5  |  “ghi” 此值与计算机用户名进行运算后得到互斥体名称  
6  |  andreagahuvrauvin.com c2  
7  |  byronorenstein.com c2  
8  |  straliaenollma.xyz c2  
9  |  0x54400字节的pe文件，名称为HttpProv.dll  
10  |  0x35c00字节的pe文件，名称为DnsProvider.dll  
11  |  0x073a00字节的pe文件，名称也为HttpProv.dll  
12  |  4字节，值为0x88a36523，可以理解为版本号  
13  |  4字节，值为0x13  
14  |  Unicode字符串“46405”，即c2端口号  
15  |  8字节，Hex值为”2B CA 18 AF D7 11 EA 59”，发包时会带上此值  
16  |  8字节，Hex值为“80 A9 03 00 30 75 00 00”，根据此值Sleep一定时间后再执行木马功能  
  
![15.png](https://image.3001.net/images/20180427/15248171905798.png!small)

（通信dll导出函数）

接着此dll会根据资源中的配置信息Sleep一定的时间后再开始后续的操作。后续会再利用自加载的方式将3个通信相关的dll全部加载起来。自加载时用到的函数主要有VirtualAlloc、RtlMoveMemory。木马还会创建名为“Microsoft-Windows-DiskDiagnosticResolver“的任务计划，达到常驻的目的。

![16.png](https://image.3001.net/images/20180427/15248172059060.png!small)

（根据资源中的配置的信息，sleep一段时间）

![17.png](https://image.3001.net/images/20180427/15248172179730.png!small)

（自加载时分配内存）

![18.png](https://image.3001.net/images/20180427/15248172317368.png!small)

（自加载时填充内存）

木马会根据资源中的c2，使用DGA（域名生成算法）生成通信时的域名信息，木马上线时会将用户名、计算机名、操作系统等信息加密后上报给c2。

![19.png](https://image.3001.net/images/20180427/15248172472518.png!small)

（DGA得到的通信域名）

![20.png](https://image.3001.net/images/20180427/15248172617510.png!small)

（上线时的第一个明文包）

木马上线后，根据服务器下发的指令执行相应的功能，主要功能有：

>  文件操作，比如创建文件或目录、删除文件或目录、查找文件
>
>  注册表读写
>
>  远程执行代码，比如创建进程、执行dll等
>
>  设置环境变量

##  **0x4 溯源**

从该RAT通信的C&C地址154.16.138.89在腾讯御见威胁情报中心平台进行反查，得到下列结果：

![21.png](https://image.3001.net/images/20180427/15248173009647.png!small)

随便选一个域名orinneamoure.com继续反查：

![22.png](https://image.3001.net/images/20180427/15248173163104.png!small)

可以发现，该域名被腾讯御见威胁情报平台标注为海莲花。而该域名也在之前友商对海莲花的报告中披露过。此外，该攻击使用的技术、网络通信协议等和以往的海莲花的攻击样本进行比对也完全一致。因而我们可以确认，该次攻击属于海莲花APT团队所为。

##  **0x5 总结**

从上文的分析可以看出该组织在漏洞利用、白加黑利用技术、代码混淆等方面都有着很深的技术积累。后门木马不落地直接内存执行、签名程序白利用、shellcode隐藏可执行文件、多变的网络通信等技术手段大大增加了杀软的查杀难度。因此，我们提醒政府、企业等广大用户，切勿随意打开来历不明的文档，同时安装安全软件。

目前，腾讯御界高级威胁检测系统已经可以检测该轮攻击的连接行为。御界高级威胁检测系统，是基于腾讯反病毒实验室的安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。

凭借基于行为的防护和智能模型两大核心能力，御界高级威胁检测系统可高效检测未知威胁，并通过对企业内外网边界处网络流量的分析，感知漏洞的利用和攻击。通过部署御界高级威胁检测系统，及时感知恶意流量，检测钓鱼网址和远控服务器地址在企业网络中的访问情况，保护企业网络安全。

![23.png](https://image.3001.net/images/20180427/15248173308329.png!small)

##  **0x6 附录(IOCs)**

###  **Hash:**

> 02AE075DA4FB2A6D38CE06F8F40E397E (Document_GPI Invitation-UNSOOC China.doc)
>
> D7C172D4A88573B7E373F2B666C011AC(GPI Invitation-UNSOOC China.doc)
>
> 72A5AD375401F33A5079CAEE18884C9D
> ({92BA1818-0119-4F79-874E-E3BF79C355B8}.dll)
>
> 79D06DD20768FD8CD4A043833C1F2D4B
> ({A96B020F-0000-466F-A96D-A91BBF8EAC96}.dll)\
>
> EC505565E4CB5A22BFD3F63E4AD83FF3(HttpProv.dll)
>
> 2559738D1BD4A999126F900C7357B759(HttpProv.dll)
>
> 2DFAEDD9265642E430E6635F210FABB4(DnsProvider.dll)
>
> F775CC387A55831386E44DD00EF9723E(rastls.dll)
>
> B10F93CDBCDF43D4C5C5770872E239F4(OUTLFLTR.DAT)

###  **C &C:**

> andreagahuvrauvin.com
>
> byronorenstein.com
>
> straliaenollma.xyz
>
> dieordaunt.com
>
> christienoll.xyz
>
> illagedrivestralia.xyz
>
> 154.16.99.85
>
> 154.16.47.41
>
> 154.16.138.89

###  **注册表 **:****

> “SOFTWARE\App\AppXbf13d4ea2945444d8b13e2121cb6b663\DefaultIcon”
>
> “SOFTWARE\App\AppXbf13d4ea2945444d8b13e2121cb6b663\Application”

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**


信捷电气股份有限公司（XINJE）是一家专注于工业自动化产品研发与应用的国内知名企业，该公司拥有可编程控制器（PLC）、人机界面（HMI）、工业信息化、伺服控制系统、变频步进等核心产品，在北京奥运会、上海工博会等国家重点工程项目上都有信捷产品的正式应用。

信捷PLC编程软件是一款功能强大的PLC编程软件，能够帮助用户使用各种编程模式进行PLC的编程管理工作，提高工作效率，让编程更加方便快捷。

![v2-d02bd19fd21c6f60a34498d824020c7a_720w.jpg](https://image.3001.net/images/20220526/1653544538_628f165ae2441a9360d8f.jpg!small)

 **Part1 漏洞状态**

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 无| 无  
  
 **Part2 漏洞描述**

信捷PLC编程软件V3.5.1存在DLL劫持漏洞，该漏洞源于DLL搜索顺序劫持，结合 _[信捷PLC编程软件zip
slip漏洞](https://link.zhihu.com/?target=http%3A//mp.weixin.qq.com/s%3F__biz%3DMzU3ODQ4NjA3Mg%3D%3D%26mid%3D2247525281%26idx%3D1%26sn%3D6684be87d4640f617c35ac080e8730bc%26chksm%3Dfd7689f6ca0100e018a8f6a21f0117b1c79ed9388f2d4ca8d33d0a7228b82113ddbbf38c6807%26scene%3D21%23wechat_redirect)_
，本地攻击者可以通过打开项目文件方式将恶意DLL 文件写入信捷PLC编程软件所在目录，其结果可导致攻击者执行任意命令。

漏洞名称| 信捷PLC编程软件DLL劫持漏洞  
---|---  
CVE编号| CVE-2021-34606  
漏洞类型| DLL劫持  
漏洞等级| 中危（6.9）  
公开状态| 公开  
受影响产品| V3.5.1（可能其他版本也存在）  
时间线| 2021.06.10– 获得CVE ID  
  
 **Part3 漏洞复现**

 **1\. 实验环境**

实验主机：win7 32 软件版本：信捷PLC编程软件V3.5.1 **2.涉及工具** Python2.7VC++ 6.0Process monitor
**3.漏洞复现** 1）第一步通过Processmonitor寻找可以劫持的dll 文件，打开PLC项目文件后，点击打开Process
monitor并设置几个过滤条件，分别是进程名、路径以及结果，如下图所示：

![v2-80f528b09048c85559d222dd7efa7b55_720w.jpg](https://image.3001.net/images/20220526/1653544539_628f165b44beb2ac1a1ea.jpg!small)

然后点击“添加TCP/IP设备设置”，发现有两个dll文件被加载，如下如所示：

![v2-0d1401ab2e28cc0af4344930b104328d_720w.jpg](https://image.3001.net/images/20220526/1653544539_628f165b8b603b750cd19.jpg!small)

其中，加载rasadhlp.dll在程序所在目录没找到后，在C:\Windows\System32目录下面查找，如下图所示：

![v2-9ddb7478d05c261a4f12bb00c3485e5f_720w.jpg](https://image.3001.net/images/20220526/1653544539_628f165bd0ea9a59bedd9.jpg!small)

且与注册表对比，rasadhlp.dll不是受保护的dll文件，说明rasadhlp.dll可以被劫持，如下图所示：

![v2-b15b62ba10bc140710021bce5bf3241f_720w.jpg](https://image.3001.net/images/20220526/1653544540_628f165c17ad459fd7303.jpg!small)

2）生成源码CPP文件和dll文件。

首先要配置Python2.7环境，安装好后，pip下载所需要的包pefile，并借助DLL_Hijacker.py获取rasadhlp.dll的导出函数，生成源码cpp文件在命令行中执行如下命令：python
DLL_Hijacker.py
C:\Windows\System32\rasadhlp.dll在该目录下，rasadhlp.cpp文件也已经生成，如下图所示：

![v2-1ae85c751c57bf846bc0ec40cc2a52da_720w.jpg](https://image.3001.net/images/20220526/1653544540_628f165c59cd0adb08586.jpg!small)

然后使用VC++6.0将rasadhlp.cpp编译为rasadhlp.dll。首先在VC++6.0中新建一个Win32 Dynamic-Link
Library工程，如下图所示：

![v2-d8cca5cdc2afbb4954fcbb1bb0a6e9bf_720w.jpg](https://image.3001.net/images/20220526/1653544540_628f165c9b90a97547302.jpg!small)

然后将rasadhlp.cpp中的代码复制到该工程Source File文件夹下的rasadhlp.cpp文件中。

![v2-bb2001cea7df701eaa8a43645cfaefe1_720w.jpg](https://image.3001.net/images/20220526/1653544540_628f165ce4f32ba4dd604.jpg!small)

更改程序，将代码中劫持成功后为弹窗改为弹出计算器，如上图所示。通过点击“组建-->组建rasadhlp.cpp”，编译，编译无误后，点击“组建-->组建rasadhlp.dll”，正确完成后，可以在工程目录下的Debug文件夹下找到生成的dll文件。

![v2-f98475dde87ffe39cce25259fadf7876_720w.jpg](https://image.3001.net/images/20220526/1653544541_628f165d4143ee759d260.jpg!small)

3）结合 _[信捷PLC编程软件zip
slip漏洞](https://link.zhihu.com/?target=http%3A//mp.weixin.qq.com/s%3F__biz%3DMzU3ODQ4NjA3Mg%3D%3D%26mid%3D2247525281%26idx%3D1%26sn%3D6684be87d4640f617c35ac080e8730bc%26chksm%3Dfd7689f6ca0100e018a8f6a21f0117b1c79ed9388f2d4ca8d33d0a7228b82113ddbbf38c6807%26scene%3D21%23wechat_redirect)_
，将该dll文件压缩成恶意项目文件，根据如下脚本可以生成一个名为“poc.zip”文件，阅读脚本可知，一旦在有漏洞的环境加载“poc.zip”后，“rasadhlp.dll”文件会被解压到程序所在目录下。

![v2-0bc032c6aa209d03b2070858d4110247_720w.jpg](https://image.3001.net/images/20220526/1653544541_628f165d7bc03ce64f89a.jpg!small)

将生成的“poc.zip”重命名为“poc.xdp”。

4）使用信捷PLC编程软件打开“poc.xdp”项目文件，此时发现恶意dll已被成功解压至程序所在目录，如下图所示：

![v2-e63d0ba6afa88a94120a1e594b3722ba_720w.jpg](https://image.3001.net/images/20220526/1653544541_628f165dbda2bd0a094ab.jpg!small)

之后关闭程序，再次打开程序，之后点击选项下的“添加TCP/IP设备设置”，进行添加，此时会弹出计算器，劫持成功，说明此时加载的是C:\Users\admin\Desktop\[http://xinjieplcbcrj_xz7.com](https://link.zhihu.com/?target=http%3A//xinjieplcbcrj_xz7.com)\XDPPro\rasadhlp.dll，如下图所示：

![v2-225a366afe62d883def96da81fe546ec_720w.jpg](https://image.3001.net/images/20220526/1653544542_628f165e40a0a306d1985.jpg!small)

 **Part4 漏洞分析**

DLL劫持之所以被称为漏洞，要从负责加载DLL的系统API
LoadLibrary来看，调用LoadLibrary时可以使用DLL的相对路径。这时，系统会按照特定的顺序搜索一些目录，以确定DLL的完整路径。而所谓的劫持，就发生在系统按照顺序搜索这些特定目录时，只要攻击者能够将恶意的DLL放在优先于正常DLL所在的目录，就能够欺骗系统优先加载恶意DLL，来实现“劫持”。

从上面的原理来看，LoadLibrary
API并不会去检查即将要加载进来的DLL是否为恶意，微软为了防御DLL劫持漏洞，提供了“安全DLL搜索模式”和“KnownDLLs注册表项”机制保护DLL。但是这些还不够，开发人员必须采取更多额外措施来保护应用程序，开发过程中，调用LoadLibrary、LoadLibraryEx等会进行模块加载操作的函数时，使用模块的物理路径作为参数。在程序调用DLL时使用“白名单”+
“签名”进行DLL的验证，或者在开发应用程序时，在代码开头调用SetDllDirectory函数，把当前目录从DLL的搜索顺序列表中删除。


## 一 漏洞简介

前段时间，微软公布Windows
PrintNightmare两个安全漏洞，分别为[CVE-2021-1675](https://nvd.nist.gov/vuln/detail/CVE-2021-1675)和[CVE-2021-34527](https://nvd.nist.gov/vuln/detail/CVE-2021-34527)。公布几天后，minikatz率先工具化集成了CVE-2021-1675和CVE-2021-34527的EXP。通过查看minikatz源码，在CVE-2021-1675的EXP中，调用的RPC函数为RpcAddPrinterDriverEx；在CVE-2021-34527的EXP中，调用的RPC函数为RpcAsyncAddPrinterDriver。系统处理这两个RPC函数后，都调用了YAddPrinterDriverEx函数，但是没有对参数[dwFileCopyFlags](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/b96cc497-59e5-4510-ab04-5484993b259b)进行条件判断。由此可设置APD_INSTALL_WARNED_DRIVER标志，使添加打印机驱动时，以高权限加载DLL。

![image-20210714104510164](https://image.3001.net/images/20210723/1627038419_60faa2d3da057822dc067.png!small)

![image-20210714104611566](https://image.3001.net/images/20210723/1627038420_60faa2d484368dccecad9.png!small)

(补丁前后对比：[Windows
PrintNightmare漏洞和补丁分析](https://www.freebuf.com/vuls/279876.html))

本文复现和分析的环境为 Windos Server 2016
Standard。通过[afwu发布的EXP](https://github.com/afwu/PrintNightmare)进行修改修改，复现CVE-2021-1675。[复现文章](https://422926799.github.io/posts/c257aa46.html)也挺多，这里推荐一篇，不复现了。值得一提的是，在复现时，除了修改UNIDRV.DLL文件路径以外，还需要修改pConfigFile赋值的路径。如果采用1方式的路径，由于在打开文件句柄之后执行驱动文件的更新，Old目录还未生成，所以打开句柄时，找不到文件。采用2方式的路径，文件句柄打开后，并未释放处于占用状态，导致后面加载DLL的时候，加载失败。

![image-20210714104805328](https://image.3001.net/images/20210723/1627038421_60faa2d5447cda404e7f4.png!small)

## 二 漏洞分析

### 2.1 动态查看CVE调用

 **1）CVE-2021-1675**

通过Process Moniter抓取到EXP加载DLL时，执行过程中的堆栈调用。

![image-20210714104840494](https://image.3001.net/images/20210723/1627038422_60faa2d61998fa757206d.png!small)

该漏洞点在于，调用YAddPrinterDriverEx函数时，没有对参数dwFileCopyFlags做校验，能够使用APD_INSTALL_WARNED_DRIVER标志，导致后面对驱动合法性校验失效，可以任意的加载DLL，并且为system权限。

![image-20210714104951017](https://image.3001.net/images/20210723/1627038422_60faa2d6e919f975fa99f.png!small)

 **2）CVE-2021-34527**

同样通过process moniter抓取mimikatz中CVE-2021-34527的EXP执行数据，加载DLL的堆栈调用。

![image-20210714105024830](https://image.3001.net/images/20210723/1627038423_60faa2d7d64d85f6af5b3.png!small)

通过地址可以找到，spoolsv.exe的调用的处理函数为NThreadingLibrary::TWorkCrew::tpSimpleCallback。

![image-20210714105059900](https://image.3001.net/images/20210723/1627038424_60faa2d8bd14f19db7b15.png!small)

继续调用TFunction4<unsigned short *,_DRIVER_CONTAINER *,unsigned long,enum
Call_Route>::Run(__int64
a1)函数，最后调用YAddPrinterDriverEx。由此可知CVE-2021-34527和CVE-2021-1675，最终都是调用YAddPrinterDriverEx函数，只是RPC调用不同，所以可以说这个漏洞是CVE-2021-1675的补丁绕过。引发思考，如果再有不同RPC调用了YAddPrinterDriverEx函数，也是能绕过CVE-2021-1675补丁的。

![image-20210714105135916](https://image.3001.net/images/20210723/1627038425_60faa2d9ad602d71ef464.png!small)

### 2.2 功能分析

EXP会通过RpcBindingSetAuthInfoExW函数，绑定句柄的认证，授权和安全质量的服务信息。当函数执行成功时，identity.User设置用户名，代表了权限。如果是低权限用户，执行ValidateObjectAccess函数后结果为0，administrator用户的权限执行ValidateObjectAccess函数后结果为1。

![image-20210714105206263](https://image.3001.net/images/20210723/1627038426_60faa2da71f0d7ecf8a5f.png!small)

 **1）绕过ValidateObjectAccess检测**

CVE-2021-1675是逻辑漏洞，通过RPC添加打印机驱动程序的时候，参数dwFileCopyFlags（v7）的标志位APD_INSTALL_WARNED_DRIVER（0x8000）为1时，_bittest函数的结果为1，则v12被赋值为0，从而不执行ValidateObjectAccess的检查。

![image-20210714105259590](https://image.3001.net/images/20210723/1627038427_60faa2db5553caa08f1f8.png!small)

但在Server 12的中，a7的值是固定为1，一定会执行ValidateObjectAccess检测。

![image-20210714105324374](https://image.3001.net/images/20210723/1627038428_60faa2dc2ad7992b2ce7f.png!small)

![image-20210714105348314](https://image.3001.net/images/20210723/1627038428_60faa2dcc2993315f481f.png!small)

 **2）检查驱动基本信息**

![image-20210714105413311](https://image.3001.net/images/20210723/1627038429_60faa2dd6d3a0dc6c6fd9.png!small)

MyName：检查驱动名称是否合法，ValidateDriverInfo的执行流程。

> 检查是否为本地文件
>
> 核对初始化key
>
> 校验驱动文件的合法性

![image-20210714105440049](https://image.3001.net/images/20210723/1627038430_60faa2de04e06ee6aba8d.png!small)

![image-20210714105459596](https://image.3001.net/images/20210723/1627038430_60faa2de92244715a5560.png!small)

但是当dwFileCopyFlags含有 APD_INSTALL_WARNED_DRIVER(0x8000)标志位时，dwFileCopyFlags &
0x8000的结果为0x8000，0x8000取非后值为0，将会跳过驱动进一步的校验。

![image-20210714105521194](https://image.3001.net/images/20210723/1627038431_60faa2df8a52d3b05adb5.png!small)

 **3）获取文件句柄**

v13的值是由dwFileCopyFlags的低8位取反后，右移4位，再跟1做与运算得出。v13的值决定CreateInternalDriverFileArray函数的第5个参数（a5）。经过计算，当dwFileCopyFlags低8位的值为0x1X时(X可为0-F中任意值)，可以使a5为0。当a5的值为0，可以规避对驱动文件的合法性检查。

通过CreateFile打开文件，得到3个文件句柄，并保存到DllAllocSplMem申请的空间中，用于后面文件更新使用。

![image-20210714105600993](https://image.3001.net/images/20210723/1627038432_60faa2e08fd5593a5ba76.png!small)

 **4）拷贝文件到驱动空间**

dwFileCopyFlags的成员pConfigFile、pDataFile、pDriverPath分别保存了配置文件、数据文件、驱动文件的文件路径。将上述成员中的文件路径下的文件，移动到C:\Windows\System32\spool\drivers\x64\3下时，需要经过以下操作：

> 文件句柄的文件信息进行核对
>
> 将文件拷贝到C:\Windows\System32\spool\drivers\x64\3\new
>
>
> 通过WaitRequiredForDriverUnload函数下的MoveNewDriverRelatedFiles函数，将spool\drivers\x64\3下的同名文件移动到spool\drivers\x64\3\old\x
> (x∈[1,3] )
> 目录下，再把spool\drivers\x64\3\new目录文件，移动到spool\drivers\x64\3下，从而实现更新文件。

![image-20210714105633247](https://image.3001.net/images/20210723/1627038433_60faa2e1cc0615277d6f7.png!small)

 **5）更新驱动文件**

通过更新Config文件，将spool\drivers\x64\3下新的配置文件加载起来。

![image-20210714105655115](https://image.3001.net/images/20210723/1627038434_60faa2e293209e186016f.png!small)

## 三 总结

CVE-2021-1675绕过用户权限检查，可以低用户的权限添加打印机驱动，由于是RPC执行打印机添加驱动，所以也能称为RCE漏洞。不过实现RCE条件是比较苛刻的，至少需要有域控的普通用户，且还需要有共享目录。个人认为该漏洞可用于持久化的操作，得到域控的administrator的账号和密码时，在有共享目录、能访问到域控的情况下，打上6月份的补丁，也能远程的加载共享目录下的DLL。

更多内容请前往微信公众号： **天玄安全实验室**

## 四 参考链接

> [1]<https://www.freebuf.com/vuls/279876.html>
>
> [2]<https://422926799.github.io/posts/c257aa46.html>
>
> [3]<https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-> rprn/b96cc497-59e5-4510-ab04-5484993b259b>
>
> [4] <https://github.com/afwu/PrintNightmare>


**Emotet银行木马自2014年被发现之后，一直活跃到至今，目前已经成为最具有影响力的恶意软件家族之一。该木马经常通过垃圾邮件进行传播，传播至今，已经迭代很多版本。在早期通过恶意的JavaScript脚本进行投递，后来转为通过含有恶意宏代码的文档下载后进行传播。我们在去年9月份对其进行过披露，截止目前，该木马的基础设施仍然在不断更新。**  

![image.png](https://image.3001.net/images/20200612/1591951921_5ee34231e04b6.png!small)![image.png](https://image.3001.net/images/20200612/1591951926_5ee342364c9b8.png!small)
本文将会在EMOTET银行木马的shellcode、基础设施和通讯加密等方面进行分析。

## 事件分析

### 主机分析

 **程序入口分析**

此恶意样本属于MFC类程序，程序主函数入口如下：

![image.png](https://image.3001.net/images/20200612/1591951934_5ee3423e81249.png!small)

通过静态和动态调试分析，从整个的主函数执行流程中无法定位到核心的功能函数。

![image.png](https://image.3001.net/images/20200612/1591951940_5ee34244cf780.png!small)通过查看字符串、程序使用的导入函数以及动态调试，如下函数为主要的功能模块入口函数。

![image.png](https://image.3001.net/images/20200612/1591951948_5ee3424cd25ba.png!small)![image.png](https://image.3001.net/images/20200612/1591951953_5ee34251e8ed5.png!small)它会使用windows资源操作相关的函数查找资源节，然后导入资源，解密相关数据。

![image.png](https://image.3001.net/images/20200612/1591951964_5ee3425c09fac.png!small)![image.png](https://image.3001.net/images/20200612/1591951967_5ee3425fc9351.png!small)程序中资源节相关数据如下：

![image.png](https://image.3001.net/images/20200612/1591951973_5ee3426566559.png!small)

程序转入到shellcode处执行，然后多次进行解密等操作，使用VirtualProtectEx函数对下一步的执行代码所在的内存页进行属性修改，改为可读可执行。

![image.png](https://image.3001.net/images/20200612/1591951983_5ee3426f423b1.png!small)![image.png](https://image.3001.net/images/20200612/1591951987_5ee34273618a3.png!small)然后转入到相应入口执行主要的恶意功能。

![image.png](https://image.3001.net/images/20200612/1591951993_5ee3427974242.png!small)
**病毒“自删除”**

通过使用SHFileOperationW函数将病毒文件移动到系统目录（同时会删除原来的文件）。

![image.png](https://image.3001.net/images/20200612/1591952000_5ee342808a6ed.png!small)![image.png](https://image.3001.net/images/20200612/1591952004_5ee342840c4e1.png!small)

然后删除Zone.Identifier结尾的相关文件。Zone.Identifier类型文件属于目标文件的其他附属信息流文件，里面内容会包括目标文件来自哪里等信息，例如本地、共享和网络。

![image.png](https://image.3001.net/images/20200612/1591952012_5ee3428c991fb.png!small)然后通过创建新进程运行。

![image.png](https://image.3001.net/images/20200612/1591952017_5ee34291df739.png!small)
**病毒持久化**

通过创建windows服务的方式进行持久化。

![image.png](https://image.3001.net/images/20200612/1591952023_5ee342978cf77.png!small)

通过创建自启动注册表的方式进行持久化。

![image.png](https://image.3001.net/images/20200612/1591952039_5ee342a74ab1a.png!small)

![image.png](https://image.3001.net/images/20200612/1591952032_5ee342a035957.png!small)

### 基础设施分析

 **C2** **基本信息分析**

**请求IP** |  **请求端口** |  **请求方式**  
---|---|---  
200.119.11.118  |  443  |  HTTP POST  
103.83.81.141  |  8080  |  HTTP POST  
  
请求的ip和端口具体信息如下：

![image.png](https://image.3001.net/images/20200612/1591952064_5ee342c0e386e.png!small)![image.png](https://image.3001.net/images/20200612/1591952068_5ee342c479b74.png!small)

 **通讯过程分析**

获取要远程访问的IP地址。

![image.png](https://image.3001.net/images/20200612/1591952075_5ee342cb54dc1.png!small)

创建HTTP请求报文所需要的参数。通过使用RtlRandom函数随意生成字符串。

![image.png](https://image.3001.net/images/20200612/1591952082_5ee342d244a03.png!small)![image.png](https://image.3001.net/images/20200612/1591952085_5ee342d5d7076.png!small)

由于要使用post表单上传文件方式进行数据上传，所以需要boundary相关的字段。

![image.png](https://image.3001.net/images/20200612/1591952092_5ee342dcecd17.png!small)

![image.png](https://image.3001.net/images/20200612/1591952098_5ee342e2cacec.png!small)

通过调用InternetOpen函数初始化网络请求。

![image.png](https://image.3001.net/images/20200612/1591952108_5ee342ecec2f1.png!small)通过调用InternetConnectW函数连接远程服务器，我们可以从参数看到具体的请求端口号。

![image.png](https://image.3001.net/images/20200612/1591952119_5ee342f774663.png!small)然后通过POST的方式进行请求。

![image.png](https://image.3001.net/images/20200612/1591952125_5ee342fd69362.png!small)

最后通过HttpSendRequestW函数发送相关的请求体。请求体是通过表单上传文件的方式。内容类型为multipart/form-data。

![image.png](https://image.3001.net/images/20200612/1591952133_5ee34305239f2.png!small)![image.png](https://image.3001.net/images/20200612/1591952138_5ee3430a312ac.png!small)提交内容分析

恶意样本上传到远端服务器的内容包括加密秘钥，计算机名称和当前运行的进程等信息。这些数据在传输的时候是加密的。

获取计算机名称，系统目录和驱动器信息等后，然后拼接。

![image.png](https://image.3001.net/images/20200612/1591952147_5ee34313322c8.png!small)![image.png](https://image.3001.net/images/20200612/1591952151_5ee343176fe50.png!small)

最后的组装字符串如下：

![image.png](https://image.3001.net/images/20200612/1591952157_5ee3431d00179.png!small)

获取计算机当前运行的进程列表信息。

![image.png](https://image.3001.net/images/20200612/1591952162_5ee343225931c.png!small)如下是需要加密的内容和加密后的内容。

![image.png](https://image.3001.net/images/20200612/1591952168_5ee34328f35cb.png!small)![image.png](https://image.3001.net/images/20200612/1591952173_5ee3432d14fd8.png!small)然后将加密的数据上传。通过网络请求实体参数也可以知道上传的数据包括秘钥和加密的收集的信息。

![image.png](https://image.3001.net/images/20200612/1591952178_5ee34332d38c7.png!small)![image.png](https://image.3001.net/images/20200612/1591952183_5ee343371621e.png!small)

### 加密算法分析

该恶意软件在上传信息时，会将上传的数据进行加密，通讯过程的加密算法是RSA_AES模式。

首先通过CryptAcquireContextW函数创建密钥容器。我们通过参数可以知道是创建的RSA_AES密钥容器，PROV_RSA_AES = 24。

![image.png](https://image.3001.net/images/20200612/1591952189_5ee3433d29212.png!small)

然后通过调用CryptImportKey函数导入RSA的公钥。通过该函数的参数也可以获取具体RSA公钥的相关信息，例如公钥模长、公钥指数和公钥的模等。

![image.png](https://image.3001.net/images/20200612/1591952197_5ee343457bace.png!small)

然后调用CryptGenKey函数生成秘钥，我们从参数可以看到，秘钥算法是AES_128。

![image.png](https://image.3001.net/images/20200612/1591952203_5ee3434b71980.png!small)使用的哈希是SHA1。

![image.png](https://image.3001.net/images/20200612/1591952209_5ee343513c957.png!small)

然后调用CryptEncrypt函数对收集的信息数据进行加密。

![image.png](https://image.3001.net/images/20200612/1591952217_5ee34359134d7.png!small)

使用CryptExportKey函数导出之前生成的AES秘钥信息，导出时使用RSA公钥加密作为上传数据的一部分，服务器接收到之后可通过RSA私钥解密出AES的秘钥，然后进一步解密主要数据。CALG_AES_128=0x0000660e。

![image.png](https://image.3001.net/images/20200612/1591952223_5ee3435f0a268.png!small)

![image.png](https://image.3001.net/images/20200612/1591952241_5ee343712f1c1.png!small)

shellcode分析  

此样本在进入核心功能模块之前做了2次重要的修正操作，第一次是将资源数据加载到内存，然后进行解密出第一段shellcode，后跳转到此处执行。如下图所示：

![image.png](https://image.3001.net/images/20200612/1591952253_5ee3437da4c7b.png!small)

第二次操作是跳转到此shellcode处执行后进行整理，然后再次分配内容，复制相关内容，对此段内存修改为可读可执行，然后跳转至此次的核心功能。首先他通过windows
api hash的方式调用系统函数，而不是直接使用。

![image.png](https://image.3001.net/images/20200612/1591952259_5ee343833f781.png!small)

然后调用VirtualAlloc函数分配空间。

![image.png](https://image.3001.net/images/20200612/1591952265_5ee34389cdf08.png!small)

然后准备开始复制数据，值得注意的是，他先对0027053F开始的数据进行了操作。我们可以从之前的内存地址可以看到此处正好是MZ头的开始。所以之前解密出来的shellcode中是完整包含有此程序核心模块的PE数据。

![image.png](https://image.3001.net/images/20200612/1591952277_5ee343957fd9f.png!small)![image.png](https://image.3001.net/images/20200612/1591952282_5ee3439aa6f17.png!small)然后复制后的数据如下，是缺失了MZ头的PE数据，作者这样做，可能是为了防止我们较为容易的看到核心模块其实是一个完整的PE格式文件，以防止dump进行静态辅助分析。

![image.png](https://image.3001.net/images/20200612/1591952290_5ee343a20b162.png!small)

然后修改内存属性，跳转到核心功能入口执行。

![image.png](https://image.3001.net/images/20200612/1591952298_5ee343aab2888.png!small)![image.png](https://image.3001.net/images/20200612/1591952303_5ee343af081ca.png!small)

我们将此模块dump出来，同时可以看到完整的核心模块入口。

![image.png](https://image.3001.net/images/20200612/1591952312_5ee343b81e3db.png!small)![image.png](https://image.3001.net/images/20200612/1591952316_5ee343bcb253d.png!small)核心模块的大致流程如下：

![image.png](https://image.3001.net/images/20200612/1591952322_5ee343c2aab89.png!small)

也同时可以通过代码的形式辅助查看，由于此程序用到的函数等都是在运行后内部动态获取的，所以仍然需要动态的方式进行分析。不过有了静态的反汇编后，可以更加方便辅助查看。

![image.png](https://image.3001.net/images/20200612/1591952330_5ee343ca412d0.png!small)我们也可以看到数据段有很多加密的字符串，基本都是通过如下函数sub_402B80进行解密的。

![image.png](https://image.3001.net/images/20200612/1591952336_5ee343d0e07f5.png!small)![image.png](https://image.3001.net/images/20200612/1591952342_5ee343d66c898.png!small)我们在动态调试中也可以看到相关信息，当然，除了动态调试，有了静态反编译后，也可以通过IDAPython的方式进行解密。

![image.png](https://image.3001.net/images/20200612/1591952350_5ee343de34da5.png!small)![image.png](https://image.3001.net/images/20200612/1591952354_5ee343e202f27.png!small)

我们可以看到此函数一共调用了31次。

![image.png](https://image.3001.net/images/20200612/1591952361_5ee343e9782e6.png!small)
**解决方案**

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 请到正规网站下载程序；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装；

 **IOC**

文件MD5  |  文件名称  |  亚信安全检测名  
---|---|---  
cc4f5e25d48bbb315b6076273eb55a37  |  WebGrabber.exe  |  TROJ_GEN.R002C0PF320


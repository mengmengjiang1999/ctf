## 一、前言  

 **攻击者在获取到Windows
shell之后，有可能会上传Mimikatz提取用户凭证。由于提取密码是本地操作，在执行时并没有网络流量产生，而ips，waf网络设备能检测到的Mimikatz相关流量主要是通过上传、下载、写入到目标及其上的过程，这一部分属于对菜刀、冰蝎工具的检测，所以要识别攻击者使用Mimikatz的动作，基本还是需要靠edr等终端安全产品。**

##  二、Mimikatz提取用户凭证

Mimikatz提取用户凭证功能，其主要集中在sekurlsa模块，该模块又包含很多子模块，如msv,wdigest,kerberos等，使用这些子模块可以提取相应的用户凭证，如sekurlsa::wdigest提取用户密码明文，sekurlsa::kerberos提取域账户凭证，sekurlsa::msv提取ntlm
hash凭证，在kuhl_m_c_sekurlsa这个数组里面有各个子模块功能的注释，如下：

![image.png](https://image.3001.net/images/20200304/15833049322348.png!small)

Mimikatz使用了一个的框架，来处理对内存的操作。以wdigest子模块为例，如果在目标机器上运行mimikatz，会跨进程读取读取lsass.exe进程的wdigest.dll模块的数据，如果是用dump文件方式提取密码则是直接打开文件。

###
![image.png](https://image.3001.net/images/20200304/1583304941438.png!small)2.1获取用户凭证信息

通过遍历加载的DLL模块名称，来初始化Mimikatz关注的一些DLL的统计信息结构体。

![image.png](https://image.3001.net/images/20200304/1583304962404.png!small)

重点是第二步和第三步。

第二步调用了kuhl_m_sekurlsa_utils_search继而调用kuhl_m_sekurlsa_utils_search_generic如下，

![image.png](https://image.3001.net/images/20200304/15833049759619.png!small)

搜索的是LsaSrv.dll的特征码，结合偏移量找到所有的登录会话信息。

![image.png](https://image.3001.net/images/20200304/15833049854120.png!small)

最后打印出来的会话信息

###
![image.png](https://image.3001.net/images/20200304/15833049944353.png!small)
2.2获取加密用户密码的密钥

第三步调用了lsassLocalHelper->AcquireKeys(&cLsass,
&lsassPackages[0]->Module.Informations);，实际对于NT6系统实际调用的是kuhl_m_sekurlsa_nt6_acquireKeys

![image.png](https://image.3001.net/images/20200304/15833050097309.png!small)

用PTRN_WALL_LsaInitializeProtectedMemory_KEY作为特征码进行搜索

![image.png](https://image.3001.net/images/20200304/15833050347292.png!small)

获取初始化向量和密钥本身

![image.png](https://image.3001.net/images/20200304/15833050495087.png!small)

###  2.3解密账户密码

基于2.1得到的登录会话信息（包含加密后的用户密码）和2.2得到的加密密钥和初始化向量，mimikatz的wdigest子模块便可以提取用户密码明文。

![image.png](https://image.3001.net/images/20200304/15833050667155.png!small)

kuhl_m_sekurlsa_genericCredsOutput实际调用kuhl_m_sekurlsa_nt6_LsaEncryptMemory进行密码的密文解密。

![image.png](https://image.3001.net/images/20200304/15833050827750.png!small)

最后根据密文长度是否是8的倍数，来调用Aes解密和Des解密（BCryptDecrypt）。

##  三、总结

Mimikatz的提取密码流程主要分为三步1、获取登录会话的信息，包含了用户密码的加密后密文；2、提取用于加密的密钥值，3、调用Windows导出函数BCryptDecrypt进行解密。由于提取会话信息和密钥都用的是特征码，因此这些特征码作为杀毒软件和edr产品的特征值会非常合适，而攻击者也会采用动态加载的方式防止这种特征的静态扫描。由于水平有限，欢迎大家指出文中的错误和交流指教。

 **参考资料：**

> <https://blog.xpnsec.com/exploring-mimikatz-part-1/>

一并感谢参考过的其他技术分享博客

 ***本文作者：新华三攻防团队，转载请注明来自FreeBuf.COM**


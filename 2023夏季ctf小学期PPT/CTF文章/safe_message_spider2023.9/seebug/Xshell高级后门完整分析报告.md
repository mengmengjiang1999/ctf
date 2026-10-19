作者：[bird@TSRC](https://security.tencent.com/index.php/blog/msg/120)

#### 1\. 前言

近日，Xshell
官方发布[公告](https://www.netsarang.com/news/security_exploit_in_july_18_2017_build.html)称其软件中存在后门。我们的实习生同学对该后门进行了详细的分析，确认这是一个具备恶意代码下载执行和数据回传等能力的高级木马。

![](https://images.seebug.org/content/images/2017/08/bae3a633-d2eb-44a6-830b-194e89540f56.png-w331s)

后门代码存在于 `nssock2.dll` 中，采用了多层加密 shellcode、花指令、线程注入等各种方式逃避杀软查杀和对抗人工分析。总体流程如下

![](https://images.seebug.org/content/images/2017/08/bdffe465-f0a6-4bdf-8cfb-de45a65380d5.png-w331s)

#### 2\. 详细过程分析

##### 2.1 第一层功能分析

通过 BinDiff 跟最新版的 `nssock2.dll` 比较可以很容易的发现一个解密 shellcode 的函数

![](https://images.seebug.org/content/images/2017/08/0c8bb4b8-db1b-448b-97c6-c3a890c58272.png-w331s)

去掉花指令分析，进入到shellcode后主要功能是先查询 `HKCU\SOFTWARE\%d` 或 `HKLM\SOFTWARE\%d` 下的
`Data` 值是否存在，`%d` 是把硬盘的序列号异或`0xD592FC92`

![](https://images.seebug.org/content/images/2017/08/45867bab-bd75-4769-82ea-11e01bbae5b7.png-w331s)

如果`Data`值存在就用其中的 key 解密第二层的 shellcode 并执行，反之就会发送 DNS 请求获取配置信息存储到 `Data`
键再解密第二层的 shellcode 并执行

![](https://images.seebug.org/content/images/2017/08/4489e407-60a9-46fc-8466-0d14cc93ef41.png-w331s)

获取配置信息时首先通过根据当前年月的 DGA（域名生成算法）生成一个域名，其算法如下

![](https://images.seebug.org/content/images/2017/08/7e9224e3-5280-4eef-97a0-33248dcebbcd.png-w331s)

然后会根据 GUID、主机名和用户名等信息生成一个前缀进行加密与之前生成的域名拼接后发送 DNS 请求并获取配置信息

![](https://images.seebug.org/content/images/2017/08/51b6add4-68a1-47e7-ad7c-4fa247c1dec7.png-w331s)

加密主要分两步，第一步如下

![](https://images.seebug.org/content/images/2017/08/00846e11-1ce1-4c1c-b677-e718a49faddd.png-w331s)

第二步如下

![](https://images.seebug.org/content/images/2017/08/966ad395-a423-4f88-93de-7670b82b9e17.png-w331s)

DNS服务器为`8.8.8.8`、`8.8.4.4`、`4.2.2.1`、`4.2.2.2`和当前主机的 DNS 服务器，接收到 key 后解密第二层
shellcode 的代码如下

![](https://images.seebug.org/content/images/2017/08/ee338a45-ccaa-40cd-a9eb-e7fc4ae6e4d7.png-w331s)

这里非常有意思，算法跟从dll进入第一层 shellcode 时的解密算法一致，想到CTF的套路尝试设为相同的
key，key1为`0xC9BED351`，key2为`0xA85DA1C9`，然后就成功解密出了第二层 shellcode。

##### 2.2 第二层功能分析

根据卡巴斯基的报告，第二层 shellcode 为 `Root` 插件，入口函数很像 `DllMain`

![](https://images.seebug.org/content/images/2017/08/727ccb68-241b-4163-8286-c10386e625fe.png-w331s)

主要功能是先设置异常处理函数，并会把异常记录到
`%ALLUSERSPROFILE%\error.log`，然后初始化函数指针表（会在其他插件中被调用），并加载5个插件

![](https://images.seebug.org/content/images/2017/08/10bd9189-95fa-480c-9b2b-a8b6144c8f0f.png-w331s)

动态调试步入 `load_plugin` 函数就能把5个插件的 shellcode dump 出来，加载完5个插件后会调用ID为 `103`
的插件（Install）的第二个函数

![](https://images.seebug.org/content/images/2017/08/2fb1ac18-8754-4f79-a0c7-4a2d56c1a5ae.png-w331s)

##### 2.3 插件功能分析

###### 2.3.1 Install插件(103)

主要功能是先修改当前进程权限，再调用ID为 `102` 的插件（Config）的第二个函数

![](https://images.seebug.org/content/images/2017/08/c667012a-97b9-4e3b-bed7-ca8024007981.png-w331s)

另外还会用 `winlogon.exe` 进程的权限创建 `svchost.exe` 进程进行线程注入，调试线程注入的 shellcode
可以先在`VirtualAllocEx`后下断获取到相应进程中的虚拟地址，然后在 `ResumeThread`
时下断，中断后附加相应进程并在之前获取的虚拟地址处下断，执行 `ResumeThread`
后会在之前的虚拟地址处中断，之后就可以继续调试了，初步分析注入的shellcode就是 `Root` 插件

![](https://images.seebug.org/content/images/2017/08/a9fd964c-f42a-492f-abb1-7a5c1fd106ce.png-w331s)

根据磁盘序列号创建互斥体：`Global\% 16-48 random latin characters%`

![](https://images.seebug.org/content/images/2017/08/4e50b085-a6fb-48e0-927b-ce8764ffffa5.png-w331s)

###### 2.3.2 Plugins插件(101)

主要功能是监听根据磁盘序列号生成的注册表项 `HKLM` 或 `HKCU\SOFTWARE\Microsoft\%5-12 random
characters%`

![](https://images.seebug.org/content/images/2017/08/580e059c-16c8-4dae-b09a-12ae765ddd5c.png-w331s)

监听到有值改变后会解密并校验是否是合法的插件并加载和初始化

![](https://images.seebug.org/content/images/2017/08/d86c94e7-c0ee-4645-abbe-42e909272060.png-w331s)

###### 2.3.3 Config插件(102)

此插件主要是跟配置信息的读写相关，其路径根据磁盘序列号生成，本机是
`C:\ProgramData\MQGOMQQ\TOYMWGMQ\UMGSAIE\DIWEYK` ，在每次初始化插件时都会被重写

![](https://images.seebug.org/content/images/2017/08/6018047f-7411-4c37-8ccf-aaf59be2968f.png-w331s)

默认的 `C&C` 地址是 `dns://www.notped.com`

###### 2.3.4 Online插件(104)

此插件主要是跟 `C&C` 服务器通信并把命令分发到相应的插件执行，首先根据协议类型选择发送请求的插件

![](https://images.seebug.org/content/images/2017/08/0a784bfd-30e0-422c-878b-4378fc23b02a.png-w331s)

如果是 `URL` 就会向根据年月的DGA生成的域名发送 `HTTP` 请求来得到真正的 `C&C` 服务器地址

![](https://images.seebug.org/content/images/2017/08/a1ca4c67-dbd2-451a-b612-7ce1f3f42cb6.png-w331s)

另外此插件也会收集更详细的主机信息，依次调用
`GetSystemTime`、`gethostbyname`、`GlobalMemroryStatusEx`、`GetNativeSystemInfo`、`GetDiskFreeSpaceExA`、`EnumDisplaySettingsW`、`GetSystemDefaultLCID`、`QueryPerformanceFrequency`、`QueryPerformanceCounter`、`GetCurrentProcessId`、`RtlGetVersion`、`GetSystemMetrics`、`GetNetworkParams`和`GetAccountSid`

###### 2.3.5 DNS插件(203)

此插件主要是用于基于 DNS 协议的 `C&C` 通信

![](https://images.seebug.org/content/images/2017/08/848a0c8c-8e71-49c3-a4cb-ebb96a76cdba.png-w331s)

#### 3\. 总结

此后门用了多种手段来增加分析难度，是一个基于插件的完善的攻击平台，请尽快升级到最新版本。以上分析如有谬误之处，欢迎斧正。

#### 4\. 附录

##### 4.1 shellcode字符串解密脚本

    
    
    from idaapi import *
    from ctypes import *
    addr = 0x274DFC8
    seed = c_uint(Byte(addr) | (Byte(addr + 1) << 8))
    result = [None] * 4096
    for i in range(4090):
        result[i] = chr((seed.value & 0xff) ^ Byte(addr + 2 + i))
        seed = c_uint(c_uint(c_uint(0x41120000 * seed.value).value - c_uint(0x434CBEEE * (seed.value >> 16)).value).value - 0x2F878E0F)
    end = result.index('\x00')
    print ''.join(result[:end])

##### 4.2 IOC相关域名

![](https://images.seebug.org/content/images/2017/08/c14f6749-bc93-41ae-97bf-cf97dce903ea.png-w331s)

#### 5\. 参考

<https://www.netsarang.com/news/security_exploit_in_july_18_2017_build.html>
<https://cdn.securelist.com/files/2017/08/ShadowPad_technical_description_PDF.pdf>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/377/>


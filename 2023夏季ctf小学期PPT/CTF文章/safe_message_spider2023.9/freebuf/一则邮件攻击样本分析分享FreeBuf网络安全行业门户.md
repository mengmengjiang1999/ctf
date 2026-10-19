## 一、 **前言**

**通过邮件投递病毒文件是网络攻击常用的一种方式，因此防御邮件攻击是每个安全团队都需要重点考虑的内容。中兴通讯每天都会收到数万封外部邮件，为了及时检测每封邮件是否含有恶意文件，中兴ZInsight团队部署了自研的高级邮件防御系统，针对每个邮件附件，通过动态行为分析的方式检测是否存在威胁。本文介绍近期捕获的一起攻击事件，分析其攻击过程。**

## 二、 **攻击邮件的捕获与分析**

近日，中兴高级邮件防御系统捕获了一批使用高危word附件进行定向攻击的钓鱼邮件，攻击对象均为同一项目团队成员，引起了安全人员的重视。下面是邮件附件的分析报告：

![image.png](https://image.3001.net/images/20181105/1541413499_5be01a7b2268e.png!small)

从分析报告中可以清晰的看到，此word文件有创建进程的异常行为，另外也发现了异常的网络行为，可以猜测这是一个下载器。经安全人员进一步分析发现，在word附件中使用了宏病毒，宏病毒由vb写成，采用了加密混淆等方式逃避杀软的检测，见下图：  

![image.png](https://image.3001.net/images/20181105/1541413532_5be01a9ce1f26.png!small)

vb脚本经过混淆，但依然可以看出有联网的痕迹，如下段代码可见http://和.com的痕迹：  

![image.png](https://image.3001.net/images/20181105/1541413551_5be01aaf8a95b.png!small)

启用宏后打开此文档会自动运行脚本，ProcessExplorer上可见其调用cmd.exe执行脚本命令：

![image.png](https://image.3001.net/images/20181105/1541413564_5be01abca7fb3.png!small)该脚本首先通过dns查询若干个恶意网址，连接成功后通过http下载exe文件并运行。通过跟踪，发现其连上solvolab.com/sdB这个恶意网址，下载PE文件并运行。data
chunk中可见可执行文件的PE头中的标识和字段：  

![image.png](https://image.3001.net/images/20181105/1541413648_5be01b104a554.png!small)![image.png](https://image.3001.net/images/20181105/1541413654_5be01b1684028.png!small)下载的可执行文件会自动运行并添加到服务，名称为buildbuild：  

![image.png](https://image.3001.net/images/20181105/1541413697_5be01b416f62c.png!small)

## 三、 **下载的恶意样本分析**

对下载的buildbuild.exe样本进行分析，主要功能如下：

### 1. **搜集smartcard信息**

该样本通过注册表查询smartCards信息：

![image.png](https://image.3001.net/images/20181105/1541413710_5be01b4e7e4ad.png!small)逆向分析可见其存在查找4G卡的服务提供商，获取虚拟按键等较明显的搜集敏感信息的行为：  

![image.png](https://image.3001.net/images/20181105/1541413721_5be01b59a07a5.png!small)

###
![image.png](https://image.3001.net/images/20181105/1541413729_5be01b619e711.png!small)2.
**自写壳**  

该样本在PEiD中显示“查无此壳”，也没有任何语言信息，推测为不常见的壳，很有可能是自写的。

![image.png](https://image.3001.net/images/20181105/1541413753_5be01b79e40eb.png!small)

此类壳没法用工具自动脱壳，只能手脱。调试过程中发现这个壳的写法还是比较常规的思路：

1)
调用VirtualAlloc为各个区段分配内存，将加密的区段数据解密到各自对应的内存空间，并调用VirtualProtect根据区段的属性修改内存操作权限：

![image.png](https://image.3001.net/images/20181105/1541413766_5be01b86d8261.png!small)2)
调用LoadLibrary加载dll，调用GetProcAddress分别获取dll中目标函数地址。

3) 跳到解密后的代码执行，如下图001A1000存放的为解码后的.text区段代码：

![image.png](https://image.3001.net/images/20181105/1541413777_5be01b915e0c8.png!small)4)
中间穿插了GetTickCount等反调试手法：

![image.png](https://image.3001.net/images/20181105/1541413783_5be01b97cb39a.png!small)

若发现处在调试状态，会通过遍历进程的方式找到并结束自身进程。进程遍历也是常规手法：

调用CreateToolhelp32Snapshot建立进程快照，通过Process32FirstW和Process32NextW进行遍历来找到当前进程，然后通过CloseHandle直接结束进程。

![image.png](https://image.3001.net/images/20181105/1541413796_5be01ba443169.png!small)

![image.png](https://image.3001.net/images/20181105/1541413801_5be01ba90198c.png!small)判断是否为当前进程的方法是在上图Call
ebx函数中实现，通过调用GetCurrentProcessId获取当前进程ID，和保存的遍历到的进程ID对比，相同就说明当前遍历的进程信息为目标进程。  

![image.png](https://image.3001.net/images/20181105/1541413813_5be01bb5f3b3a.png!small)

### 3. **创建子进程**

为干扰逆向分析，该样本在运行过程中会调用CreateProcessW创建子进程。

![image.png](https://image.3001.net/images/20181105/1541413831_5be01bc74454f.png!small)

在内存中修改CreationFlags入参为0x00000004（CREATE_SUSPENDED），使子进程创建后自动挂起，然后直接在od中找到其进程号attach即可调试子进程。

![image.png](https://image.3001.net/images/20181105/1541413843_5be01bd3c6028.png!small)子进程创建成功后，病毒主要功能都在子进程中进行，而父进程将退出。  

![image.png](https://image.3001.net/images/20181105/1541413850_5be01bda465e6.png!small)

以下皆为子进程中运行的功能。

### 4. **信息收集和系统监控**

样本没有自己实现该功能，而是调用了第三方动态库winimhc3.dll、winbrohc.dll、winhafnt.dll等。这些dll是 [OCular
Agent](https://file.info/search.html?q=OCular+Agent)产品的重要组件。OCular
Agent为一电脑监控软件，由SurveilStar Inc开发，数字签名为T.E.C Solutions
(G.Z.)Limited，可以记录电子邮件,聊天和即时信息,网站访问,搜索历史,计划活动,文件操作等等。其动态库常被杀软识别为恶意软件。

![image.png](https://image.3001.net/images/20181105/1541414079_5be01cbf329b2.png!small)

![image.png](https://image.3001.net/images/20181105/1541414093_5be01ccd9847f.png!small)

winimhc3逆向显示很多监控的痕迹，如IMHook、枚举窗口等：  

![image.png](https://image.3001.net/images/20181105/1541414107_5be01cdb76a25.png!small)

![image.png](https://image.3001.net/images/20181105/1541414147_5be01d03d69fd.png!small)

Winbrohc中实现了很多监控功能诸如文件遍历、监控应用程序数据、检索杀软、搜索数据库、修改history文件和注册表等。

调用FindFirstFileW和FindNextFileW进行文件遍历：

![image.png](https://image.3001.net/images/20181105/1541414161_5be01d110766d.png!small)

监控包括explorer、cmd、winword在内的多个程序：

![image.png](https://image.3001.net/images/20181105/1541414170_5be01d1a7d466.png!small)

![image.png](https://image.3001.net/images/20181105/1541414180_5be01d24dac06.png!small)

获取磁盘信息：

![image.png](https://image.3001.net/images/20181105/1541414191_5be01d2f0d83d.png!small)获取各种浏览器和云盘中的用户信息及历史数据：  

![image.png](https://image.3001.net/images/20181105/1541414206_5be01d3e66d6f.png!small)

![image.png](https://image.3001.net/images/20181105/1541414212_5be01d44d7b5c.png!small)

检测杀软：

![image.png](https://image.3001.net/images/20181105/1541414221_5be01d4d93875.png!small)

监控explorer、cmd等常用程序：

![image.png](https://image.3001.net/images/20181105/1541414232_5be01d5885e20.png!small)

获取ProcessToken，提权：  

![image.png](https://image.3001.net/images/20181105/1541414245_5be01d6599b66.png!small)![image.png](https://image.3001.net/images/20181105/1541414252_5be01d6c5b7e8.png!small)

查找账户信息：  

![image.png](https://image.3001.net/images/20181105/1541414284_5be01d8ce1cba.png!small)![image.png](https://image.3001.net/images/20181105/1541414291_5be01d93f31b4.png!small)

监控邮件：  

![image.png](https://image.3001.net/images/20181105/1541414302_5be01d9ec1e72.png!small)

###
![image.png](https://image.3001.net/images/20181105/1541414308_5be01da4ef75e.png!small)5.
**自删除**  

![image.png](https://image.3001.net/images/20181105/1541414317_5be01dade5f44.png!small)

![image.png](https://image.3001.net/images/20181105/1541416282_5be0255a131f2.png!small)

### 6. **自我复制**  

自我复制到在c:\windows\system32目录下，目的是为了后续创建服务用：

![image.png](https://image.3001.net/images/20181105/1541414332_5be01dbce764c.png!small)

4F4句柄在OD中查知为c:\windows\system32\buildbuld.exe：

![image.png](https://image.3001.net/images/20181105/1541414342_5be01dc6e1d39.png!small)这个过程并没有直接调用kernel32的WriteFile实现，而是通过外壳函数SHFileOperationW实现，该函数最终会去调用WriteFile函数：  

![image.png](https://image.3001.net/images/20181105/1541414352_5be01dd08c7c6.png!small)SHFileOperation是一种外壳函数，用它可以实现各种文件操作，如文件的拷贝、[删除](https://baike.baidu.com/item/%E5%88%A0%E9%99%A4/13020275)、移动等，该函数使用起来非常简单，它只有一个指向SHFILEOPSTRUCT结构的参数。使用SHFileOperation(
)函数时只要填写该专用结构--SHFILEOPSTRUCT，告诉Windows执行什么样的操作，以及其它重要信息就行了。  

###  7. **创建服务**

使用之前自我复制的c:\windows\system32\buildbuild.exe文件创建服务：

![image.png](https://image.3001.net/images/20181105/1541414364_5be01ddc11025.png!small)

##
![image.png](https://image.3001.net/images/20181105/1541414373_5be01de59e3aa.png!small)
**四、样本分析总结**  

该样本采用了很多方法干扰逆向，例如自写壳、子进程、反调试、以及调用第三方监控软件的dll等等。并且调试过程中发现该样本总是用VirtualAlloc分配内存，然后将要执行的部分代码拷入内存中执行，同时喜欢用类似call
eax的函数调用手法，使得无法使用IDA等工具查看其代码逻辑，只能依靠手调。

功能比较常规，但是并没有自己实现，而是调用了第三方的监控软件中的dll，一方面功能大而全，另一方面其庞大的代码量也可以起到干扰逆向的效果。

##  **五、防御建议**

邮件攻击是非常普遍的一类网络攻击，当企业收到的攻击邮件集中于某一团队时，需要格外注意，很可能是有目的的定向攻击，需要及时预警，提醒团队加强防范，不要轻易打开邮件的附件和链接，对可疑文件进行杀毒，必要时通过沙箱进行动态行为检测。

buildbuild.exe样本MD5：

    
    
    95240732d90027df7cb2c6c74804253b

 ***本文作者：ZInsight团队，转载请注明来自FreeBuf.COM**


**近期Check Point发现Naikon APT组织正在对亚太地区（APAC）国家政府进行网络攻击活动，使用了名为Aria-body的新后门控制受害者的网络。本报告将详细分析Naikon APT组织在过去5年中使用的战术，技术，程序和基础设施。**

## 目标分析

过去的十年中，Naikon APT一直目标锁定同一地区，包括澳大利亚，印度尼西亚，菲律宾，越南，泰国，缅甸和文莱，使用了名为Aria-body的后门。目标实体包括外交部，科学技术部以及政府所有的部门，攻击者会利用已被攻陷的政府组织发动攻击，来试图感染其他目标，利用受信任的已知联系人渗透到新的组织中并扩展网络。

该小组目的是收集情报并监视该国政府，攻击者会从政府部门内受感染的计算机和网络中查找和收集特定文档，从可移动驱动器中提取数据，屏幕截图和键盘记录。该组织将受感染的内部服务器用作攻击和控制服务器，防止被目标发现。

![](https://image.3001.net/images/20200508/1588922809_5eb509b9538ba.png!small)

## 感染链

研究过程中发现几种不同的感染链用于传播Aria-body。最开始时发现从亚太地区政府使馆发送给澳大利亚州政府的恶意电子邮件，该电子邮件名为The
Indians Way.doc，含有恶意软件RoyalRoad，加载程序尝试从spool.jtjewifyn.com下载并执行下一阶段的有效负载。

观察到了几种不同的感染方法：

> 1、RoyalRoad漏洞利用的RTF文件
>
> 2、包含合法可执行文件和恶意DLL的存档文件，利用Outlook和Avast代理加载恶意DLL
>
> 3、直接通过可执行文件加载程序

![](https://image.3001.net/images/20200508/1588923147_5eb50b0b14662.png!small)

## 基础设施

最近的行动中，攻击者C＆C服务器使用了相同的托管和DNS服务，在多个域中重用了相同的IP地址：

![](https://image.3001.net/images/20200508/1588923224_5eb50b5815123.png!small)

域名使用情况：

![](https://image.3001.net/images/20200508/1588923273_5eb50b89b6dba.png!small)

## 工具分析

### 加载程序分析

自2017年以来，Aria-body加载程序功能未发生重大变化，加载程序负责以下任务：

> 1、通过启动文件夹或注册表建立持久性
>
> 2、将自身注入到另一个进程，例如rundll32.exe和dllhost.exe
>
> 3、解密两个Blob：“导入表”和“加载器配置”
>
> 4、使用DGA算法
>
> 5、与C＆C地址通信，检索下一阶段有效载荷
>
> 6、解密收到的有效载荷DLL（Aria-body后门）
>
> 7、加载并执行DLL的导出功能

![](https://image.3001.net/images/20200508/1588923498_5eb50c6a536a4.png!small)

Configuration & DGA

加载程序配置经过加密，包含以下信息：C＆C域，端口，用户代理和域生成算法（DGA）种子。
如果种子不为零，加载程序将根据种子和通信日期使用DGA生成C＆C域。 加载程序的配置使用以下算法解密：

def decrypt_buf(buf): k = 8 j = 5 for i in range(len(buf)): xor_byte = (k + j)
% 0xff buf[i] = buf[i] ^ xor_byte j = k k = xor_byte

C&C服务器

获取C＆C域后，加载程序会与下载下一阶段程序。
攻击者每天在有限的窗口期操作C＆C服务器，每天仅在线几个小时。加载程序的最后一个阶段，接收XOR密钥对下载的RAT进行解密。

### Aria-body RAT分析

下载的有效负载是一个自制RAT，称为Aria-body，有32位和64位两种。RAT功能包括：

> 1、创建/删除文件/目录
>
> 2、截屏
>
> 3、搜索文件
>
> 4、使用ShellExecute启动文件
>
> 5、枚举进程
>
> 6、收集文件的元数据
>
> 7、收集TCP和UDP表状态列表
>
> 8、关闭TCP会话
>
> 9、收集操作系统信息
>
> 10、使用checkip.amazonaws.com验证位置

Aria-body的变体还包括其他模块，例如：

> 1、USB数据采集模块
>
> 2、键盘记录器模块
>
> 3、反向代理模块
>
> 4、加载扩展模块

## 特征分析

### 初始化

后门包含一个导出的函数，执行程序后，它将初始化一个名为MyDerived的结构以及用于HTTP和TCP连接的结构。

### 信息收集

Aria-body首先在受害者的机器上收集数据，包括：主机名，计算机名，用户名，域名，Windows版本，处理器MHz，MachineGuid，公共IP。

![](https://image.3001.net/images/20200508/1588926312_5eb5176880c2c.png!small)

### C＆C通信

通过HTTP或TCP协议与C＆C服务器进行通信。 恶意软件通过程序配置标志来决定使用哪种协议。 收集的数据与XORed密码和XOR密钥一起送到C＆C域：

![](https://image.3001.net/images/20200508/1588926391_5eb517b74bfa2.png!small)

### Outlook DLL

研究中发现了非常独特的Aria-body变体，变体DLL名为outllib.dll，它是Office.rar的一部分。它没有从加载程序获得任何配置，在变体中包含了硬编码配置。

有效负载具有两个不同的C＆C域：blog.toptogear [.] com、202.90.141 [.]
25，如果无法解析第一个C＆C域，将使用IP地址。

![](https://image.3001.net/images/20200508/1588926557_5eb5185d73fc7.png!small)

![](https://image.3001.net/images/20200508/1588926584_5eb51878ade20.png!small)

## 归属分析

### 字符串相似

Aria-body后门具有几个描述恶意软件功能的调试字符串。这些调试字符串也可以在XsFunction后门中找到：

![](https://image.3001.net/images/20200508/1588926814_5eb5195e4d11e.png!small)

### 散列函数相似

XsFunction和Aria-body加载程序都使用相同的哈希算法djb2。 在XsFunction中，该函数的名称为XS02，在Aria-body中，其名称为AzManager。

![](https://image.3001.net/images/20200508/1588926865_5eb5199122d8c.png!small)

### 代码相似

Aria-body后门中的某些功能与旧XsFunction后门中的功能相同。

![](https://image.3001.net/images/20200508/1588926899_5eb519b384d89.png!small)

### 基础设施重叠

四台C＆C服务器与mopo3 [.] net域共享IP，该域解析IP为与卡巴斯基报告中提到的域myanmartech.vicp [.] net相同。

![](https://image.3001.net/images/20200508/1588926976_5eb51a00d3056.png!small)

## 总结

从这次活动中发现了Naikon APT组织针对亚太地区政府的最新工具，攻击者利用了RoyalRoad RTF等通用工具集和特制的后门Aria-body。Naikon APT组织过去5年中一直处于活动中，通过利用新服务器，不断变化加载程序，无文件加载以及新后门程序阻止自身被发现分析追溯。

## 附录

### Aria-body支持命令集

![](https://image.3001.net/images/20200508/1588928593_5eb5205152d3b.png!small)

![](https://image.3001.net/images/20200508/1588928607_5eb5205f9f0c9.png!small)

### DGA

![](https://image.3001.net/images/20200508/1588928630_5eb520768195a.png!small)

### IOC

> realteks.gjdredj[.]com
>
> spool.jtjewifyn[.]com
>
> blog.toptogear[.]com
>
> mon-enews[.]com
>
> wdrfjkg129[.]com
>
> n91t78dxr3[.]com
>
> kyawtun119[.]com
>
> [www.ajtkgygth](http://www.ajtkgygth/)[.]com
>
> news.nyhedmgtxck[.]com
>
> dathktdga[.]com
>
> [www.rrgwmmwgk](http://www.rrgwmmwgk/)[.]com
>
> dns.jmrmfitym[.]com
>
> [www.kyemtyjah](http://www.kyemtyjah/)[.]com
>
> rad.geewkmy[.]com
>
> cpc.mashresearchb[.]com
>
> [www.qisxnikm](http://www.qisxnikm/)[.]com
>
> dns.seekvibega[.]com
>
> sugano.trictalmk[.]com
>
> bbs.forcejoyt[.]com

 ***参考来源：[checkpoint](https://research.checkpoint.com/2020/naikon-apt-cyber-espionage-reloaded/)，由Kriston编译，转载请注明来自FreeBuf.COM**


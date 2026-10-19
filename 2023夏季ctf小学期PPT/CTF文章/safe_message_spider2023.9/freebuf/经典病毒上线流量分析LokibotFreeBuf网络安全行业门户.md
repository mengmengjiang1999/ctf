## 一、概述

Lokibot于2015年面世，持续活跃至今，是一种高度危险且隐匿的恶意软件，旨在窃取受害主机的敏感信息，包括存储的密码、浏览器登录凭据以及加密货币钱包等，并将这些信息上送到远程C2服务器上。本文将重点针对Lokibot家族的上线包进行分析，让读者可以更深入了解经典病毒Lokibot的流量特征，进行有效防御。

## 二、本地行为分析

文件基本信息如下：

![1688003806_649ce4de96efb34637cbd.png!small?1688003807064](https://image.3001.net/images/20230629/1688003806_649ce4de96efb34637cbd.png!small?1688003807064)

### 2.1 脱壳

使用反编译工具分析文件发现该文件使用了壳保护。为了更好的分析病毒行为，需要对样本进行脱壳处理。尝试在沙箱运行发现如下行为：

![1688003872_649ce5209617711c7784e.png!small?1688003873814](https://image.3001.net/images/20230629/1688003872_649ce5209617711c7784e.png!small?1688003873814)

根据行为可知，文件调用WriteProcessMemory(),向进程中注入文件

WriteProcessMemory()作用：将数据写入指定进程中的内存区域。

    
    
    BOOL WriteProcessMemory(
      [in]  HANDLE  hProcess,
      [in]  LPVOID  lpBaseAddress,  ；目标地址
      [in]  LPCVOID lpBuffer,     ；预备写入的地址
      [in]  SIZE_T  nSize,        ；写入数据大小
      [out] SIZE_T  *lpNumberOfBytesWritten
    );
    
    

定位可疑函数位置，对该函数下硬件断点

![1688004017_649ce5b11e5fe81ae25fd.png!small?1688004017879](https://image.3001.net/images/20230629/1688004017_649ce5b11e5fe81ae25fd.png!small?1688004017879)

![1688004025_649ce5b91d46aa2d1d849.png!small?1688004025800](https://image.3001.net/images/20230629/1688004025_649ce5b91d46aa2d1d849.png!small?1688004025800)

查看stdcall窗口，主要关注2，3，4这三个参数，通过这三个参数可以判断出需要进行dump文件的起始地址以及文件大小。经调试确定WriteProcessMemory()被调用五次,整理可知写入数据大小为0x1A000。

![1688004037_649ce5c5517acda726fca.png!small?1688004037919](https://image.3001.net/images/20230629/1688004037_649ce5c5517acda726fca.png!small?1688004037919)

通过savedata命令dump数据到文件中

savedata命令格式：文件名，起始地址，文件大小。实际命令如下：savedata 1234，0x040AF0F8,0x1A000

![1688004051_649ce5d3ae0257070425e.png!small?1688004052605](https://image.3001.net/images/20230629/1688004051_649ce5d3ae0257070425e.png!small?1688004052605)

使用反编译工具查看保存的文件，可以看到清楚的逻辑，确定脱壳成功。

### 2.2 动态获取API

该样本未通过导入表使用关键API，只有当需要调用API时才会接收索引值以及名称的hash值获取对应API的地址直接调用，而非将API恢复或者存储到某个地方以后再运行。使用该方式可以防止分析者一次性恢复使用的所有API，实现细节见下文。

GET_dll_base函数会以a1作为索引值从包含DLL名称的内存数组中获取DLL名称，进而获取其基址。

![1688004098_649ce60271547bed44a66.png!small?1688004099070](https://image.3001.net/images/20230629/1688004098_649ce60271547bed44a66.png!small?1688004099070)

parse_export_tbl函数会加载DLL并解析导出表，遍历导出表中函数并通过LO_caculate_hash函数计算出函数名字符串的hash与参数api_hash对比，相同则成功获取到API地址。

![1688004111_649ce60f906a69822cda2.png!small?1688004112089](https://image.3001.net/images/20230629/1688004111_649ce60f906a69822cda2.png!small?1688004112089)

LO_caculate_hash函数负责计算当前调用API的HSAH值，计算步骤如下：该函数使用了循环嵌套，外层循环运行n次（n为API名称字符串的长度）。每循环一次获取当前存储在*api_str中的字符与v3进行异或后存储在v3中，并将*api_str的值修改为下一个字符存储的地址。接着进行内层循环，内层循环运行8次
判断v3的值是否为0，不为0则与常数0x4358AD54进行异或，再右移1位。最后将输出结果v3取反。通过上述过程最终获取当前API名称的hash。

![1688004125_649ce61dc4f80ecb5abb5.png!small?1688004126769](https://image.3001.net/images/20230629/1688004125_649ce61dc4f80ecb5abb5.png!small?1688004126769)

使用x64dbg调试相关逻辑

系统API调用示例如下：

![1688004138_649ce62af093054ead80b.png!small?1688004139440](https://image.3001.net/images/20230629/1688004138_649ce62af093054ead80b.png!small?1688004139440)

计算并对比API名称的hash获取相应地址

![1688004153_649ce639ad14964f24178.png!small?1688004154235](https://image.3001.net/images/20230629/1688004153_649ce639ad14964f24178.png!small?1688004154235)

![1688004159_649ce63f2a77d5e1e5dee.png!small?1688004159867](https://image.3001.net/images/20230629/1688004159_649ce63f2a77d5e1e5dee.png!small?1688004159867)

上述分析确定了获取API地址与调用函数的地址，由于该样本是通过API_HASH去获取相关API地址，同时也可以获取相关API的名称。获取被调用API名称的方法如下：

通过下条件断点，直接输出API的名称和相关地址。

在地址0x403260下条件断点，断下后可从EAX获取API名称，从栈顶获取调用API的函数信息。

![1688004172_649ce64c421e021048c77.png!small?1688004173351](https://image.3001.net/images/20230629/1688004172_649ce64c421e021048c77.png!small?1688004173351)

最终获取的API信息与相关地址如下：

![1688004184_649ce658c96cfd18b5534.png!small?1688004185420](https://image.3001.net/images/20230629/1688004184_649ce658c96cfd18b5534.png!small?1688004185420)

### 2.3 创建互斥量

调用成功会根据受害者主机系统的GUID创建互斥量。

![1688004220_649ce67ccc6dd47dcdf92.png!small?1688004221335](https://image.3001.net/images/20230629/1688004220_649ce67ccc6dd47dcdf92.png!small?1688004221335)

### 2.4 窃取数据

Lokibot会构造两个数组，第一个数组中的值作为全局变量充当标识符，第二个数组中的函数实现了各种窃取数据的逻辑。

![1688004247_649ce697f03a2066bd0ee.png!small?1688004248500](https://image.3001.net/images/20230629/1688004247_649ce697f03a2066bd0ee.png!small?1688004248500)

firefox窃密函数功能为：判断是否存在firefox浏览器信息，根据不同的系统版本执行对应的窃密操作。其他窃密函数的逻辑类似。

![1688004262_649ce6a634b4074350033.png!small?1688004262781](https://image.3001.net/images/20230629/1688004262_649ce6a634b4074350033.png!small?1688004262781)

Lokibot会给每个窃密函数绑定一个全局变量标识符，C2服务器会根据这些全局标识符来存储/解析被盗数据。

![1688004272_649ce6b0229da4a7631d0.png!small?1688004272562](https://image.3001.net/images/20230629/1688004272_649ce6b0229da4a7631d0.png!small?1688004272562)

![1688004278_649ce6b6cf9be85df0dfb.png!small?1688004279586](https://image.3001.net/images/20230629/1688004278_649ce6b6cf9be85df0dfb.png!small?1688004279586)

窃取信息的目标程序包含浏览器，远控，邮件等常用工具,部分工具示例如下：

firefox browser 火狐浏览器  
notepadplusplus Notepad++  
myftp myftp上传工具  
ftpgetter ftp上传软件  
syncovery Super Flexible Synchronizer自动备份工具  
bitkinex bitkinex手机ftp工具  
putty putty远控工具  
incredimail incredimail邮件管理软件  
outlook outlook邮件  
---  
  
同时，LoKibot会尝试从 Windows Credential Manager 中窃取凭据信息。

![1688004312_649ce6d88fbbd5549ccfc.png!small?1688004313183](https://image.3001.net/images/20230629/1688004312_649ce6d88fbbd5549ccfc.png!small?1688004313183)

为了窃取凭证信息，Lokibot遍历读取指定目录下以“.lck”为后缀的所有文件。

![1688004340_649ce6f494b673d0e03ab.png!small?1688004341159](https://image.3001.net/images/20230629/1688004340_649ce6f494b673d0e03ab.png!small?1688004341159)

elevate_privilege函数的主要功能是调整进程令牌的权限。以便find_file获取凭据信息。

![1688004354_649ce7020e0266f290cc4.png!small?1688004354836](https://image.3001.net/images/20230629/1688004354_649ce7020e0266f290cc4.png!small?1688004354836)

find_file函数主要功能是查找%s\\\Microsoft\\\Credentials与%s\\\Microsoft\\\Credentials下的凭据信息。

![1688004370_649ce712174182efde8cd.png!small?1688004370703](https://image.3001.net/images/20230629/1688004370_649ce712174182efde8cd.png!small?1688004370703)

![1688004376_649ce7185b990ee37c140.png!small?1688004376903](https://image.3001.net/images/20230629/1688004376_649ce7185b990ee37c140.png!small?1688004376903)

将窃取的数据再次打包发送到C2服务器。

![1688004386_649ce72287d7b31412d35.png!small?1688004387198](https://image.3001.net/images/20230629/1688004386_649ce72287d7b31412d35.png!small?1688004387198)

### 2.5 持久化

为了实现持久化，Lokibot 将自身复制到%APPDATA%内的一个文件夹，创建注册表启动项，隐藏创建的目录和复制的可执行文件。

创建目录并复制原始可执行文件。

![1688004413_649ce73d4e19477235be2.png!small?1688004413979](https://image.3001.net/images/20230629/1688004413_649ce73d4e19477235be2.png!small?1688004413979)

创建注册表启动项并隐藏文件夹和可执行文件。

![1688004426_649ce74ac5fd90c0172bc.png!small?1688004427304](https://image.3001.net/images/20230629/1688004426_649ce74ac5fd90c0172bc.png!small?1688004427304)

## 三、网络行为分析

### 3.1 解密并连接C2

Lokibot会将获取的信息和系统信息一起打包发送至目标服务器。

![1688004485_649ce785bd2456f0d0acd.png!small?1688004486637](https://image.3001.net/images/20230629/1688004485_649ce785bd2456f0d0acd.png!small?1688004486637)

获取宿主机用户名、桌面等相关信息。

![1688004498_649ce79219a29f1883026.png!small?1688004498583](https://image.3001.net/images/20230629/1688004498_649ce79219a29f1883026.png!small?1688004498583)

![1688004504_649ce798318ea6dd3b80e.png!small?1688004504634](https://image.3001.net/images/20230629/1688004504_649ce798318ea6dd3b80e.png!small?1688004504634)

![1688004508_649ce79cea426b1f24a50.png!small?1688004509382](https://image.3001.net/images/20230629/1688004508_649ce79cea426b1f24a50.png!small?1688004509382)

将获取的信息拼接在一起，并传入send_data。

![1688004519_649ce7a7814bb23a8583d.png!small?1688004520056](https://image.3001.net/images/20230629/1688004519_649ce7a7814bb23a8583d.png!small?1688004520056)

Lokibot将C2以3DES加密算法加密后存储在样本中，建立连接前先进行解密，解密结果如下图。

![1688004530_649ce7b26b4a7dac66fdb.png!small?1688004531021](https://image.3001.net/images/20230629/1688004530_649ce7b26b4a7dac66fdb.png!small?1688004531021)

上线报文示例如下：

![1688004543_649ce7bf9c0039d2f95c1.png!small?1688004544451](https://image.3001.net/images/20230629/1688004543_649ce7bf9c0039d2f95c1.png!small?1688004544451)

### 3.2 上线包详细分析

将上线报文的关键数据导出，使用Imhex标注，各部分含义如下

1.下图标记处四个字节为样本中硬编码的定值数据

![1688004582_649ce7e67dbc17ea1044a.png!small?1688004583664](https://image.3001.net/images/20230629/1688004582_649ce7e67dbc17ea1044a.png!small?1688004583664)

2.下图标记处为定值，使用了Lokibot存储数据的特殊结构

字节[0,1]代表是否为宽字节，宽字节为1否则为0

字节[2,5]代表后续数据长度

字节[6,12]代表存储的数据，此处为“ckav.ru”

![1688004600_649ce7f8077d6953b94bb.png!small?1688004601072](https://image.3001.net/images/20230629/1688004600_649ce7f8077d6953b94bb.png!small?1688004601072)

3.下图标记处使用了Lokibot特殊数据结构，含义为用户名

![1688004637_649ce81de05ae06236fb2.png!small?1688004638732](https://image.3001.net/images/20230629/1688004637_649ce81de05ae06236fb2.png!small?1688004638732)

4.下图标记处使用了Lokibot特殊数据结构，含义为主机名

![1688004645_649ce825d75f9c2fed89a.png!small?1688004646497](https://image.3001.net/images/20230629/1688004645_649ce825d75f9c2fed89a.png!small?1688004646497)

5.下图标记处使用了Lokibot特殊数据结构，含义为widnows域名称

![1688004652_649ce82cce7fc3bf565fc.png!small?1688004653738](https://image.3001.net/images/20230629/1688004652_649ce82cce7fc3bf565fc.png!small?1688004653738)

6.下图标记处表示屏幕宽高

字节[0,3]代表屏幕宽度

字节[4,7]代表屏幕高度

![1688004662_649ce836b060a17e0a73c.png!small?1688004663453](https://image.3001.net/images/20230629/1688004662_649ce836b060a17e0a73c.png!small?1688004663453)

7.下图标记处值如下

字节[0,1]代表检索指定用户账户信息成功

字节[2,3]代表当前用户不属于管理员组

字节[4,5]代表当前系统为x64框架

![1688004670_649ce83e002339671052c.png!small?1688004671017](https://image.3001.net/images/20230629/1688004670_649ce83e002339671052c.png!small?1688004671017)

8.下图标记处表示操作系统的版本号为6.1 次版本为1

![1688004675_649ce843dd237c9011fe2.png!small?1688004676624](https://image.3001.net/images/20230629/1688004675_649ce843dd237c9011fe2.png!small?1688004676624)

9.下图标记处为定值，为“k.r.o.t.i.k.\\.W.i.n.b.o.x.”的第一个字符

![1688004687_649ce84f52c2db9e64798.png!small?1688004688057](https://image.3001.net/images/20230629/1688004687_649ce84f52c2db9e64798.png!small?1688004688057)

![1688004693_649ce855d0a61ea495c2d.png!small?1688004694513](https://image.3001.net/images/20230629/1688004693_649ce855d0a61ea495c2d.png!small?1688004694513)

10.下图标记处为定值

![1688004706_649ce8622f85a6032d6e7.png!small?1688004707107](https://image.3001.net/images/20230629/1688004706_649ce8622f85a6032d6e7.png!small?1688004707107)

11.下图标记处使用了Lokibot特殊数据结构，含义为机器的GUID

![1688004740_649ce88471f5e9466abae.png!small?1688004741237](https://image.3001.net/images/20230629/1688004740_649ce88471f5e9466abae.png!small?1688004741237)

12.下图标记处为随机生成的字符串

字节[0,3]代表生成的字符串长度

字节[4,8]代表生成的字符串

## 四、防护方案

### 处置建议

  1. 定期修改重要账户的密码
  2. 重要数据做好备份工作
  3. 及时更新系统补丁，减少系统漏洞带来的风险

### IPS特征库

针对Lokibot家族上线流量，新华三IPS特征库能够有效检测并拦截，请及时开启相关功能。

![1688004850_649ce8f2eb9b996aca3c5.png!small?1688004851828](https://image.3001.net/images/20230629/1688004850_649ce8f2eb9b996aca3c5.png!small?1688004851828)

  

  


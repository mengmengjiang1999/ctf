***本文作者： findream ，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

**偶然在论坛上看到一篇关于CoinMiner介绍，文章从该病毒的流行趋势，入侵路径，关联分析等多个角度对病毒进行的分析，对样本的分析寥寥几句就概括完了。想到之前分析的多为勒索类病毒，对于挖矿类病毒研究较少。故斗胆尝试小小分析一次，如有不到之处望师傅们指教。**

## 一、样本信息

> 1、样本名称：antspywares.exe
>
> 2、样本md5：3846b42b7ac29f8f92f6222230207cb5
>
> 3、是否加壳：无壳
>
> 4、编译语言：Microsoft Visual C++ ver. ~6.0~7.10 - Linker 14 - Visual 2015
>
> 5、样本来源：<http://93.174.93.149/>

## 二、行为分析

样本在技术上有所创新，首先没有直接使用Kernel32下的API函数，而是利用Knowdlls注册表优先在家Ntdll，然后获取其中的Nt*函数。第二，使用了进程替换技术，利用svchost.exe这一宿主进程，去启动挖矿进程，这样有效避免的被查杀的风险。但是实际操作中没有有效控制CPU的占用率，导致了被害者很容易觉察到。

![行为分析](https://image.3001.net/images/20181119/15426079265974.png!small)

## 三、样本分析

1、程序在执行了初始化操作后，创建了一个名为4e064bee1f3860fd606a的互斥体，这一步目的是保证程序在此主机上是唯一的。如果检测到已存在次互斥体，程序退出。

![样本分析](https://image.3001.net/images/20181119/1542607946876.png!small)

2、通过异或运算，解密得到配置文件地址，通过访问配置文件，我们可以看到钱包地址，矿池等相关配置信息。

![样本分析](https://image.3001.net/images/20181119/15426079576361.png!small)

![样本分析](https://image.3001.net/images/20181119/15426079795734.png!small)

![样本分析](https://image.3001.net/images/20181119/15426079964433.png!small)

3、再次通过相同的异或运算得到钱包地址，矿池地址pool.monero.hashvault.pro:3333

![样本分析](https://image.3001.net/images/20181119/15426080129964.png!small)

![样本分析](https://image.3001.net/images/20181119/1542608049371.png!small)

![样本分析](https://i.imgur.com/tyZob4d.png)

![样本分析](https://image.3001.net/images/20181119/15426080808663.png!small)

4、对病毒文件进行Hash加密

> 初始化CSP；
>
> 创建空的Hash对象；
>
> 将文件读入内存；
>
> 将读入数据添加到指定Hash对象。

![对病毒文件进行Hash加密](https://image.3001.net/images/20181119/15426081073766.png!small)

![对病毒文件进行Hash加密](https://image.3001.net/images/20181119/15426081231616.png!small)

5、根据之前获得的系统位数(32位or64位)分别利用注册表KnownDlls32或者KnowDlls注册表项加载ntdll.dll，然后通过GetProcAddress函数获取指定函数地址。这样一来可以直接用Nt*函数，不需要Kernel32分发，也增大了分析人员分析的难度。

![直接用Nt*函数，不需要Kernel32分发](https://i.imgur.com/oTnCKoj.png)

![直接用Nt*函数，不需要Kernel32分发](https://image.3001.net/images/20181119/15426081664998.png!small)

6、通过注册表\\\SOFTWARE\\\Microsoft\\\Cryptography获取主机GUID值，目的是唯一的标志主机，在理论上GUID是每台主机唯一拥有的。也就是说每台主机的GUID值是不一样的。

![获取主机GUID值](https://image.3001.net/images/20181119/15426082254804.png!small)

![获取主机GUID值](https://i.imgur.com/T29WIq7.png)

![获取主机GUID值](https://i.imgur.com/otkfSVm.png)

![获取主机GUID值](https://image.3001.net/images/20181119/15426082663596.png!small)

7、创建病毒释放目录：

![创建病毒释放目录](https://i.imgur.com/LGFvRuR.png)

![创建病毒释放目录](https://i.imgur.com/dUNDo2k.png)

8、从网络中读取配置信息，可以发现这里的数据和前面的new.txt是一致的：

![从网络中读取配置信息](https://image.3001.net/images/20181119/15426083084532.png!small)

![从网络中读取配置信息](https://image.3001.net/images/20181119/15426083245832.png!small)

![从网络中读取配置信息](https://image.3001.net/images/20181119/15426083384944.png!small)

9、判断svchost和wuapp.exe是否存在，这两个文件是系统文件，svchost是服务宿主程序，wuapp用于windows的更新，检查这两个程序存在的目的是为了后期利用这两个程序创建挖矿进程。

![判断svchost和wuapp.exe是否存在](https://image.3001.net/images/20181119/15426083631796.png!small)

10、创建两个配置文件

![创建两个配置文件](https://image.3001.net/images/20181119/15426083826048.png!small)

11、在启动目录下创建HpuEtzbXyw.url文件，用于自启动。

![创建HpuEtzbXyw.url文件](https://image.3001.net/images/20181119/15426084273144.png!small)

12、创建挖矿进程，这里使用了进程替换技术。首先将代码跨进程写入svchost.exe中，然后通过sysenter汇编关键字resume。

![创建挖矿进程](https://image.3001.net/images/20181119/15426084438671.png!small)

![创建挖矿进程](https://image.3001.net/images/20181119/15426084585962.png!small)

![创建挖矿进程](https://image.3001.net/images/20181119/15426084742555.png!small)

![创建挖矿进程](https://image.3001.net/images/20181119/15426085015369.png!small)

## 四、溯源分析

根据管家团队的分析显示8220团队使用多个C&C服务器，这样可以有效的避免被检测到。一下是8220团队使用到的C&C服务器。

    
    
    159.65.155.17
    
    93.174.93.149
    
    198.50.179.109
    
    193.169.252.253
    
    192.99.142.235

同时样本中使用到的矿池地址是pool.monero.hashvault.pro:3333发现和其他厂商团队所报告的不符，可能是团队修改了其中的矿池。

![溯源分析](https://image.3001.net/images/20181119/15426085415742.png!small)

 ***本文作者：findream，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


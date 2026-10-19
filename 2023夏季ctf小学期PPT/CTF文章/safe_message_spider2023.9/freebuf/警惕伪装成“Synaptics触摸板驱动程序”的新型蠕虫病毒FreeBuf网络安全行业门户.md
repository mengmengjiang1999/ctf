**近期，亚信安全截获伪装成“Synaptics触摸板驱动程序”的新型蠕虫病毒，该病毒具有很强的传播性，既可以通过带有恶意宏代码的Excel文档传播，也可以通过对正常的EXE文件进行偷梁换柱（将正常的EXE文件内容复制更新到病毒自身的资源段中）的方式传播。亚信安全将其命名为Worm.Win32.OTORUN.KAT。**

当机器感染该病毒后，其会拦截用户新建Excel文档或者打开Excel文档的行为，并将新建或者打开的Excel文档替换成带有恶意宏代码的文档（亚信安全检测为：TROJ_FRS.0NA103BE18），恶意的宏代码主要功能是下载并执行病毒的主体文件Synaptics.exe（亚信安全检测为：Worm.Win32.OTORUN.KAT），进一步感染其他机器。

## 执行流程

![](https://image.3001.net/images/20191216/1576489130_5df750aae2e2f.png!small)

## 详细分析

当用户在桌面上打开EXE可执行文件时，该病毒首先会复制自身，然后将用户打开的文件更新到刚刚复制的病毒文件的资源段中，最后替换原始的文件，这个感染过程不会破坏原始的文件功能，用户点击该文件后，仍然会执行原始文件的功能，但实际该文件已经被病毒文件所替换，机器感染了病毒，由于其感染方式较为隐蔽，所以用户很难察觉到异常。

病毒主体信息和伪装的安装过程如下所示：

![](https://image.3001.net/images/20191216/1576489154_5df750c293723.png!small)

![](https://image.3001.net/images/20191216/1576489188_5df750e40eb38.png!small)

## 宏文档分析

该病毒主体文件的资源段内包含此恶意的宏文档，如下图所示：

![](https://image.3001.net/images/20191216/1576489213_5df750fddff19.png!small)

使用oletools工具dump此宏代码，主要的功能是从远程服务器下载病毒主体文件Synaptics.exe，并将其设置成系统隐藏文件后执行。具体信息如下：

![](https://image.3001.net/images/20191216/1576489240_5df75118ec75b.png!small)

![](https://image.3001.net/images/20191216/1576489257_5df751290c4f2.png!small)

首先会在系统临时目录创建随机文件，并将此XLSM资源段内的数据复制到该文件中：

![](https://image.3001.net/images/20191216/1576489270_5df751361cef6.png!small)

![](https://image.3001.net/images/20191216/1576489279_5df7513fd9c9b.png!small)

然后用临时目录的随机文件替换桌面上新建的Excel文档：

![](https://image.3001.net/images/20191216/1576489293_5df7514de4a2e.png!small)

![](https://image.3001.net/images/20191216/1576489307_5df7515becf36.png!small)

病毒感染后的效果如下：

![](https://image.3001.net/images/20191216/1576489320_5df751684d911.png!small)

## 主体Synaptics.exe病毒文件分析

该病毒为了隐蔽自身的恶意行为，其会在同目录下释放保存在资源段“EXERESX”的安装程序，然后运行。之后对EXE文件进行偷梁换柱的行为也是将EXE文件重新更新到这个资源段内，达到传播和伪装的目的。

![](https://image.3001.net/images/20191216/1576489332_5df7517439f43.png!small)

查找资源段“EXERESX”数据：

![](https://image.3001.net/images/20191216/1576489347_5df75183195b8.png!small)

在病毒同目录中创建一个“._cache_+Synaptics.exe”文件，用于存放该资源段内的可执行文件。（伪装的安装程序或者被感染的正常EXE文件）：

![](https://image.3001.net/images/20191216/1576489364_5df7519414de0.png!small)

![](https://image.3001.net/images/20191216/1576489375_5df7519f8ff79.png!small)

然后调用ShellExecute函数执行此文件。如下所示：

![](https://image.3001.net/images/20191216/1576489395_5df751b380692.png!small)

添加注册表自启动项目：

![](https://image.3001.net/images/20191216/1576489408_5df751c003049.png!small)

## 正常EXE文件替换分析

首先会将病毒自身复制到临时目录中的随机文件中：

![](https://image.3001.net/images/20191216/1576490058_5df7544af2a13.png!small)

![](https://image.3001.net/images/20191216/1576489457_5df751f11d412.png!small)

![](https://image.3001.net/images/20191216/1576489486_5df7520e756a4.png!small)

然后为其创建一个图标文件并写入数据：

![](https://image.3001.net/images/20191216/1576489517_5df7522d21d8b.png!small)

![](https://image.3001.net/images/20191216/1576489529_5df752396f929.png!small)

使用UpdateResourceA函数将资源段EXERESX中的内容更新到临时文件的PE资源段，这样就达到了替换和隐藏的目的。用户在执行替换后的文件时（由于图标已经替换，表面上很难识别），由于病毒总是优先执行其资源段EXERESX中释放出来的文件，所以并不影响客户原始的EXE文件的功能：

![](https://image.3001.net/images/20191216/1576489545_5df7524976584.png!small)

最后将这个临时文件更换为原始文件，并删除临时文件：

![](https://image.3001.net/images/20191216/1576489558_5df752565a7fc.png!small)

![](https://image.3001.net/images/20191216/1576489571_5df752632a6b8.png!small)

整体的替换过程代码如下所示：

![](https://image.3001.net/images/20191216/1576489656_5df752b8625c2.png!small)

正常EXE文件感染替换后的效果如下：

![](https://image.3001.net/images/20191216/1576489669_5df752c5107e0.png!small)

## 网络请求功能分析

该病毒会创建线程进行网络请求和邮件发送等：

![](https://image.3001.net/images/20191216/1576489682_5df752d260409.png!small)

判断网络状态，从远程服务器下载文件到本地：

![](https://image.3001.net/images/20191216/1576489697_5df752e10cf38.png!small)

![](https://image.3001.net/images/20191216/1576489708_5df752ecbc653.png!small)

发送邮件相关代码如下：

![](https://image.3001.net/images/20191216/1576489737_5df75309e2d2c.png!small)

![](https://image.3001.net/images/20191216/1576489752_5df753183d129.png!small)

![](https://image.3001.net/images/20191216/1576489763_5df7532380049.png!small)

## 解决方案

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 打全系统及应用程序补丁；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 尽量关闭不必要的文件共享；

## IOC

**文件** **SHA-1** | **文件名** | **亚信安全检测名**  
---|---|---  
FF01C2EC1513C2EA11BDE2E**F91CFE2 | Synaptics.exe | Worm.Win32.OTORUN.KAT  
00BC96**8B98676ECD67E81A6F1D7754E 4156044 | XLSM | TROJ_FRS.0NA103BE18  
  
***本文作者：亚信安全，转载请注明来自FreeBuf.COM**


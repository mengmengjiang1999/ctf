## 一、背景介绍

**昨天接到朋友电话，说客户现场存在PowerShell的异常进程，初步情况了后认为可能就是PowerShel挖矿，没有太留意。当拿到朋友提供的异常文件后才发现并非自己想的那样，再此针对现象进行分析，本次分析未涉及逆向。**

## 二、分析过程

### 2.1 异常文件信息

首先查看获取的异常文件，提供的文件中包含conhost、1.bat、sqlservr.exe、test.ps1、test2.sp1和update.bat：

![](https://image.3001.net/images/20200517/1589725784_5ec14a587005d.png!small)

![](https://image.3001.net/images/20200517/1589725841_5ec14a919c8c6.png!small)

这里我们可以看到一个比较熟悉的sqlservr.exe程序，第一感觉是这是Microsoft SQL
Server服务套装的一部分吗？看到conhost文件夹时，这不是也是系统上的文件吗？但实际并非如此，这里我们分别对sqlservr.exe和conhost.exe这两个程序进行属性查看，详细如下：

 **2.1.1 sqlservr.exe程序文件属性查看**

这里可以看到该文件的属性中，主要是微软的一些签名，第一眼的感觉这是正常的，详细查看便会发现该文件是异常的，其他不说，看到原始文件名SSMS.EXE时，我们便应该留心了，正常文件不会出现这种标签，而该文件存在这样的标签，说明该文件并非是Microsoft
SQL Server服务套装的一部分，而是其他文件重命名。

![](https://image.3001.net/images/20200517/1589729582_5ec1592e9842d.png!small)

 **2.1.2 conhost.exe程序文件属性查看**

看到该文件的图标，这不是文件夹吗？里面还有文件？看到文件类型却为：应用程序，确实挺有意思的。

![](https://image.3001.net/images/20200517/1589725964_5ec14b0c81ce9.png!small)

其次在查看该程序的文件属性，发现该程序与sqlservr.exe相同，是被重名了。

![](https://image.3001.net/images/20200517/1589729629_5ec1595dddfc5.png!small)

 **2.1.3 1.bat文件查看**

查看1.bat文件时发现，该文件是使用powershell执行test2.ps1 powershell脚本，并且无回显。

![](https://image.3001.net/images/20200517/1589726174_5ec14bdeb7873.png!small)

 **2.1.4 update.bat文件查看**

查看updata.bat文件时发现，该文件使用wevtutilcl +名称，删除系统日志、安全日志和应用日志；并且使用sc config服务名称start=
disabled(设置服务为禁用)关闭很多应用，从而释放跟多空间。

![](https://image.3001.net/images/20200517/1589726215_5ec14c072c1bb.png!small)

### 2.2 进程分析

看到这些异常文件后，不免对该问题感兴趣，不，应该是很感兴趣。于是便远程接入该电脑进行分析。首先使用了ProcessExplorer查看了各个进程间的调用关系，这里可以看到在两个conhost.exe父进程下分别存在sqlservr.exe和cmd.exe下的powershell这两个子进程，并且路径均在C:\Windows\Fonts\路径下。

![](https://image.3001.net/images/20200517/1589726460_5ec14cfc518a1.png!small)

![](https://image.3001.net/images/20200517/1589726529_5ec14d41d8645.png!small)

顺势找到C:\Windows\Fonts\路径下，查看这些文件，当切换到该路径下，发现路径中未发现这些文件，于是便猜测该文件被隐藏了，于是在cmd命令行中切换到C:\Windows\Fonts\路径下，使用dir
/a:h查看隐藏文件（由于忘记截图，因此该截图中缺少了1.bat文件和sqlservr.exe这两个文件，只剩下test.ps1和test2.ps1），如下：

![](https://image.3001.net/images/20200517/1589726721_5ec14e0119c27.png!small)

这里确认到异常进程sqlservr.exe和conhost.exe。

 **2.2.1 sqlservr.exe进程分析**

这里我提取了sqlservr.exe这个程序，并将这个程序在虚拟机中运行，通过查看回显信息确认，该病毒挖矿病毒，详细如下：

![](https://image.3001.net/images/20200517/1589726811_5ec14e5b7124d.png!small)

failed to allocate RandomX dataset，switching to slow
mode（这里我使用的是虚拟机，内存较小，因此切换到了低速模式）。

> 备注：[RandomX-> 门罗币XMR的挖矿新算法：优化抗ASIC+降低GPU优势](https://www.hellobtc.com/kp/bi/06/1852.html)

当运行sqlservr.exe程序时，创建外联访问信息，外联IP为：175.194.147.234。

![](https://image.3001.net/images/20200517/1589726927_5ec14ecf57ff5.png!small)

使用微步对175.194.147.234进行分析，发现该IP表现为CoinMiner，详细如下：

![](https://image.3001.net/images/20200517/1589726965_5ec14ef51b8ed.png!small)

### 2.3 服务项分析

通过对sqlservr.exe和conhost.exe两个进程进行分析，异常的conhost.exe程序所在的路径为：C:\Windows\conhost，并且发现异常的conhost.exe进程服务为update，详细如下：

conhost.exe进程信息：

![](https://image.3001.net/images/20200517/1589727085_5ec14f6d93416.png!small)

conhost.exe进程所对应的文件位置（右键conhost.exe—>打开文件位置）：

![](https://image.3001.net/images/20200517/1589727124_5ec14f944b024.png!small)

conhost.exe进程服务为update（右键conhost.exe—>转到服务；或者根据PID进行确认）：

![](https://image.3001.net/images/20200517/1589727161_5ec14fb9b7993.png!small)

这里我发现该病毒进程主要依赖于服务，服务停止所有异常进程停止，服务启动所有异常进程启用。

### 2.4 注册表分析

由于上述章节我们确认了异常服务项，因此我们可以根据服务器项确认注册表信息。

首先确认该注册表项：HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\update

首先在update键中我们可以发现存在lmagepath路径为C:\Windows\conhost\conhost.exe

![](https://image.3001.net/images/20200517/1589727212_5ec14fecd116c.png!small)

其次在parameters中发现下述素信息。：

![](https://image.3001.net/images/20200517/1589727256_5ec15018a7921.png!small)

在AppExit中发现下述信息：

![](https://image.3001.net/images/20200517/1589727302_5ec1504668b7a.png!small)

其次确认HKEY_LOCAL_MACHINE\SYSTEM\ControlSet002\Servic\update，同样也发现上述信息

首先在update键中我们可以发现存在lmagepath路径为C:\Windows\conhost\conhost.exe

![](https://image.3001.net/images/20200517/1589727335_5ec15067ac143.png!small)

其次在parameters中发现下述素信息：

![](https://image.3001.net/images/20200517/1589727364_5ec15084337b6.png!small)

在AppExit中发现下述信息：

![](https://image.3001.net/images/20200517/1589727398_5ec150a668c79.png!small)

### 2.5 病毒清理

在2.3节服务项分析中，我们发现服务停止，异常进程停止，服务项启动，异常进程启动。因此我们首先停止服务，停止服务后异常进程同时也会消失，剩余步骤是删除注册表信息和清理异常文件。

 **2.5.1删除注册信息**

首先根据2.4节注册表分析中的两个注册表路径：HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\update；HKEY_LOCAL_MACHINE\SYSTEM\ControlSet002\Servic\update；

分别删除update键信息。

 **2.5.2隐藏文件删除**

这里隐藏文件删除有两种办法：

> 第一种：使用火绒剑，在火绒剑中的文件管理进行删除；
>
> 第二种：使用cmd命令行命令del /a:h {文件名称}；

![](https://image.3001.net/images/20200517/1589727462_5ec150e6e621f.png!small)

使用这两种办法都能很快清除异常文件，重启后未发现异常问题则清理干净。

## 三、总结

在该事件中主要针对进程、异常文件、服务注册表等信息进行分析，并针对分析结果进行病毒处理，这也是典型的病毒事件处理思路。

 ***本文作者：bbbbbbig，转载请注明来自FreeBuf.COM**


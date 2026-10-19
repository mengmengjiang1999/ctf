## 介绍

勒索软件千差万别，从几乎没有检测逃避手段的简单病毒到具有复杂反分析、反沙盒技巧的高级威胁，攻击者利用这些勒索软件进行牟利。幸运的是，勒索软件家族都有许多共同点，这有助于进行检测与分类。

## 勒索信息

实际上，所有的勒索软件都会在明显的位置创建可读文件，文件中提供的勒索信息告知用户已经被感染并指导其支付赎金。这些文件通常包含易于识别的信息，这些信息可以帮助识别勒索软件的详细信息（如家族和版本），或者可用于进一步调查的信息，如比特币支付地址和联系信息。

通常在加密过程完成后创建勒索信息文件，这种检测方法想要实时保护系统显然是不够的，但是在沙盒环境中检测勒索软件不失为一种好办法。勒索信息文件通常遵循非常特别的命名方式，并且会在文件系统中创建多个副本。下面列出了一些文件的示例：

家族| 文件路径  
---|---  
Cerber| C:\Users\admin\Documents_R_E_A_D___T_H_I_S___1UCQ90_.txt  
Cerber| C:\Users\admin\Desktop_R_E_A_D___T_H_I_S___Z7NS2O31_.txt  
WannaCry| C:\Users\Admin\AppData\Local\Temp\@Please_Read_Me@.txt  
WannaCry| C:\Users\Admin\Downloads\@Please_Read_Me@.txt  
Sodin| C:\Users\Public\Pictures\Sample Pictures\gltiw7kx7b-readme.txt  
Sodin| C:\Users\Public\Pictures\Sample Pictures\gltiw7kx7b-readme.txt  
  
大多数勒索软件家族都有不同的释放这些勒索信息的方法，勒索信息中会使用不同的措辞方式（甚至有的还会提到家族名称），这使得这成为分类和识别勒索软件非常有效的方法。![](https://image.3001.net/images/20210928/1632806239_6152a55f54fa50c2f45c5.png!small)

如上所示，该勒索信息包含了受害者为了支付赎金需要访问的定制化链接地址。此外还有一些会带有比特币钱包地址或者与运营者联系的电子邮件地址。这些在调查勒索软件时有用的信息，通常只能在样本动态分析时才能得到。在沙盒环境中，可以清楚地看到样本创建和修改的文件。通过检查这些文件的内容，特别是开头的部分内容，通常就可以确定是否为勒索信息文件，提取后可以进一步分析。

家族| 文件  
---|---  
Cerber| \r\n CERBER RANSOMWARE\r\n \r\n -----\r\n  
Cerber| \r\n Hi, I'am CRBR ENCRYPTOR ;)\r\n  
CryptoMix| \---CryptoMix---\r\n\r\nNOT YOUR LANGUAGE?  
Dharma| \r\nATTENTION!\r\nAt the moment, your system is not protected.\r\nWe
can fix it and restore files.\r\nTo restore the system write to this
address:\r\n  
Ordinypt| ============================ WELCOME
============================\r\n============== DO NOT DELETE THIS FILE UNTIL
ALL YOUR DATA HAS BEEN RECOVERED! ==============\r\n  
Ryuk| \n\r\nRyuk\n  
Sodinokibi| Hello dear friend!\r\n\r\nYour files are encrypted,  
WannaCry| Q: What's wrong with my files?\r\n\r\nA: Ooops, your important files
are encrypted.  
  
发现相关文件后，只需解析内容提取有用的信息即可：![](https://image.3001.net/images/20210928/1632806539_6152a68be7ef20165ea37.png!small)

## 阻止系统恢复

### 删除卷影副本

卷影副本是 Windows Server 2003 首次引入的备份功能。最初，通过跟踪文件系统随时间的变化而起作用，可以在每次修改时恢复文件，这与 git
等 SCM
方法不同。目前卷影副本已经扩展到包括用于创建卷影副本的多种模式，包括在特定时间点创建文件系统的完整快照。这些备份旨在最小化花费的时间和硬盘空间，差异备份技术的存储需求比传统全盘存储的要求小得多。

默认情况下，卷影副本是在 Windows 创建系统还原点时创建的，许多时候还原点是系统的日常任务。不管使用哪种创建模式，卷影副本现在都是 Windows
内置备份和恢复工具的核心，这也使得卷影副本成为勒索软件攻击的目标，从而让受害者更难从勒索中恢复文件。实际上，这通常是通过 Windows 命令
vssadmin 或者 wmic 来实现的：

> vssadmin delete shadows /all /quiet
>
> wmic shadowcopy delete /nointeractive

在动态分析时很容易检测，它们都创建了新的进程。WannaCry
是一个很好的例子，它同时包含了两种方法：![](https://image.3001.net/images/20210928/1632806548_6152a69494d8e68359269.png!small)

### 禁用恢复模式

Windows 恢复模式使用户可以访问安全引导以及大多数内置系统还原功能，包括从恢复设备修复
Windows。许多勒索软件家族会禁用该模式使恢复更加困难。在引导系统时访问恢复模式，通过使用 bcdedit 编辑引导配置设置来禁用此模式。

    
    
    bcdedit /set {default} recoveryenabled no

尽管此功能不如删除卷影副本常见，但在 Phobos、WannaCry 和 Cerber
等许多家族中都可以看到该功能。![](https://image.3001.net/images/20210928/1632806554_6152a69a078bf3de039cc.png!small)

### 删除备份

除了已经讨论过的卷影副本外，Windows
还支持全盘备份，该方式使用整个文件系统的副本。如前所述，这种方式要大得多，会占用更多的资源。在大多数系统中，都不会作为自动进行的任务，但是对于任何试图阻止系统恢复的人来说，这也是一个不得不清除的障碍。可以通过
Windows 备份工具 wbadmin 访问这些备份：

    
    
    wbadmin delete catalog -quiet

大多数恶意软件家族都具备此功能，因为备份恢复是绕过支付赎金的好办法。

### 清除日志

某些勒索软件在感染过程中也会清除系统事件日志，该特性对勒索软件的针对性较小，但是为了完整起见也进行简要介绍。可以通过 wevtutil 清除事件日志，例如
[MalwareHunterTeam](https://twitter.com/malwrhunterteam/status/973523764607639558)在
2018 年发现的 Zenis 勒索软件使用它来清除日志：

> cmd.exe /C wevtutil.exe cl Application
>
> cmd.exe /C wevtutil.exe cl Security
>
> cmd.exe /C wevtutil.exe cl System

据推测，这样做的目的是是分析感染源变得困难，而且还可以隐藏恶意行为。

### 更换壁纸

许多勒索软件会使用某种方法更改桌面壁纸，可以使用 DrawText
生成图片。桌面壁纸的内容通常与勒索信息类似，但是对于非勒索软件而言，这是一种不常见的操作。![](https://image.3001.net/images/20210928/1632806677_6152a715035d15d9b2e74.png!small)

也可以通过 Hook 相关 API（如 DrawText）拦截写入的图片，或者采用如 OCR
的方式来解析图像。但是，如前所述，通常从勒索信息文件中更容易获得此类信息。

## 文件操作

勒索软件通常遵循一个特殊的流程：

> 1.遍历文件夹中的文件
>
> 2.读取并加密文件的内容
>
> 3.加密内容写回文件，覆盖原始文件或创建新文件
>
> 4.如果未覆盖原始文件即清除原始文件，或者按照勒索软件的命名规则来重命名加密文件

勒索软件重命名文件包括其特定的文件扩展名，实际上是执行文件移动操作。如果对系统中的每个文件都执行该操作，这将会涉及大量几乎相同的操作。最常见的文件移动是
MoveFile 函数，其他实现可能会抽象化该过程，如使用 ReadFile 复制文件内容，然后使用 CreateFile
创建带有修改后的文件名的新文件并将加密内容写入其中。如下所示，在 procmon 中检查 WannaCry
的样本会出现以下模式：![](https://image.3001.net/images/20210928/1632806779_6152a77bef6bcb26a4d31.png!small)

监控大量的文件写入可能是检测各种勒索软件的好办法。如果可以在分析过程中 Hook 这些 API
还可以检查缓冲区确认正在进行加密操作，并消除是良性文件操作的可能性。或者另一种检测勒索软件的方式是检查文件的类型，原始文件一定包含明显的文件头，但是加密后的文件将不再具有这些显著的特征。产生大量无法识别
MIME 类型文件的样本很可能是勒索软件。

## 结论

本文对动态环境中的勒索软件检测进行了基本分析，当然上述行为只是一部分恶意行为，各个家族通常包含的功能远远超过上面的功能。

## 参考来源

> [Hatching](https://hatching.io/blog/ransomware-part1)


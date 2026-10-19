**作者：zoemurmure**  
**原文链接：<https://www.zoemurmure.top/posts/cve_2023_21752_1/>**

## 0\. 前言

CVE-2023-21752 是 2023 年开年微软第一个有 exploit
的漏洞，原本以为有利用代码会很好分析，但是结果花费了很长时间，难点主要了两个：漏洞点定位和漏洞利用代码分析，因此在本文中花费了更多的篇幅介绍了这两部分内容，欢迎指正。

## 1\. 漏洞简介

根据官方信息，该漏洞是 Windows Backup Service 中的权限提升漏洞，经过身份认证的攻击者可利用此漏洞提升至 SYSTEM
权限。成功利用此漏洞需要攻击者赢得竞争条件。

EXP 代码位于 [Github](https://github.com/Wh04m1001/CVE-2023-21752)，提供了两个版本，版本 1
可以实现任意文件删除，可稳定复现；版本 2 尝试利用任意删除实现本地提权，但是复现不稳定。

## 2\. 漏洞点定位的曲折之路

这部分内容是一些失败的过程记录，以及我自己的碎碎念，防止自己之后犯同样的错误，只对漏洞分析感兴趣的可以略过 2.1 和 2.3 小节。

### 2.1 失败的过程

首先尝试复现，提权版本的利用程序在虚拟机上没有复现成功，任意文件删除版本的利用程序由于我没有使用完整路径，也没有复现成功（但是此时我还不知道原因）。

之后我尝试进行补丁对比，但是想要进行补丁对比首先要确定漏洞位于哪个文件中，根据漏洞利用程序的文件命名 `SDRsvcEop`，找到了文件
sdrsvc.dll，但是补丁对比后并没有发现差异。

> 这期间我还搜索了关于这个漏洞的信息，但是除了漏洞通告和 GitHub 的 exp
> 代码外，没有找到其他内容。这里吐槽一下某数字站的漏洞通告，竟然说这个漏洞是 Windows Server Backup (WSB) 上的……

这个时候我已经开始对漏洞利用代码进行分析了，一方面通过微软的文档，了解代码中一些函数和参数的使用，一方面开始在 Windbg 上进行调试，并由此找到了
rpcrt4.dll、combase.dll 这些和漏洞无关的文件。

在调试过程中，我花费了很多时间在 `DeviceIoControl` 这个函数上，因为之前看的很多漏洞最终定位的文件都是 sys
驱动文件，因此虽然我在心里仍旧为 dll 文件留了一些位置，但是在方法选择上，我仍旧趋向去寻找某个 sys 文件。所以我想要在利用程序执行到
`DeviceIoControl` 的时候，在用户态转内核态的入口位置设置一个断点，然后监控系统究竟执行到了哪里。当然，这个方法失败了，并且搞得我心烦意乱。

我在这个时候才想起来要把利用程序参数的相对路径改成绝对路径，并且成功复现了任意文件删除。虽然但是，这之后我又走了弯路……

> 之前学习病毒分析的时候，有一个算是标准的流程，就是要先执行病毒，看一下它的动态特征，以此方便后面的动态分析。之前看的很多漏洞分析文章，也都是要执行一下
> poc 或者 exp，进行进程监控，但是我完全忘记了，或者说我虽然想到了这个方法，但是并没有十分重视。

我在继续分析漏洞利用代码，在此期间看了一些关于 DCOM 的资料，确定 sdrsvc.dll 是依赖 rpcss.dll 文件功能的（明明可以通过
process hacker 直接确定的……），通过补丁对比发现函数 `CServerSet::RemoveObject` 被修改，我尝试在 Windbg
中在这个函数设置断点，但是利用程序没有执行到这里，所以漏洞点不在这个文件。

> 其中这个时候我的潜意识已经告诉我我的路走错了，因为微软的漏洞说明上明明白白的写着 Windows backup
> service，所以漏洞文件肯定是和这个功能直接相关的文件，要不然它就直接写 RPC 漏洞了。

### 2.2 转入正轨

此时我仍旧没有使用 procmon
对利用程序进行监控，我选择在安装补丁前后的系统上执行利用程序，并检查输出（输出内容做了一些修改），得到以下结果（因为只是测试功能，并没有选择对高权限文件进行删除）：

补丁修复前

    
    
    PS C:\Users\exp\Desktop> C:\Users\exp\Desktop\SDRsvcEop.exe C:\Users\exp\Desktop\test.txt
    [wmain] Directory: C:\users\exp\appdata\local\temp\23980418-9164-497e-8ce7-930949d1af55
    [Trigger] Path: \\127.0.0.1\c$\Users\exp\AppData\Local\Temp\23980418-9164-497e-8ce7-930949d1af55
    [FindFile] Catch FILE_ACTION_ADDED of C:\users\exp\appdata\local\temp\23980418-9164-497e-8ce7-930949d1af55\SDT2C35.tmp
    [FindFile] Start to CreateLock...
    [cb] Oplock!
    [CreateJunction] Junction \\?\C:\Users\exp\AppData\Local\Temp\23980418-9164-497e-8ce7-930949d1af55 -> \RPC Control created!
    [DosDeviceSymLink] Symlink Global\GLOBALROOT\RPC Control\SDT2C35.tmp -> \??\C:\Users\exp\Desktop\test.txt created!
    [Trigger] Finish sdc->proc7
    [wmain] Exploit successful!
    [DeleteJunction] Junction \\?\C:\Users\exp\AppData\Local\Temp\23980418-9164-497e-8ce7-930949d1af55 deleted!
    [DelDosDeviceSymLink] Symlink Global\GLOBALROOT\RPC Control\SDT2C35.tmp -> \??\C:\Users\exp\Desktop\test.txt deleted!

补丁修复后

    
    
    PS C:\Users\exp\Desktop> C:\Users\exp\Desktop\SDRsvcEop.exe C:\Users\exp\Desktop\test.txt
    [wmain] Directory: C:\users\exp\appdata\local\temp\183c772e-f444-4aec-a489-7d9f734ee719
    [Trigger] Path: \\127.0.0.1\c$\Users\exp\AppData\Local\Temp\183c772e-f444-4aec-a489-7d9f734ee719
    [FindFile] Catch FILE_ACTION_ADDED of C:\users\exp\appdata\local\temp\183c772e-f444-4aec-a489-7d9f734ee719\SDT1F8A.tmp
    [Trigger] Finish sdc->proc7
    _

由此可知修复后利用程序无法再获取一个 tmp 文件的句柄，我猜测应该是补丁修复之前，漏洞文件创建了这个 tmp
文件，并且创建的权限有问题（这个猜测不一定准确），但是这个猜测目前没什么用，还是没办法定位漏洞文件。

然后，几乎走投无路的我终于想起来要用 procmon 了，谢天谢地。

根据上面利用程序输出结果的对比，确定漏洞修复的位置和创建的 tmp 文件有关，因此格外注意 procmon 中该文件的创建操作：

![](https://images.seebug.org/content/images/2023/02/01/1675240126000-2023-01-17-11-02-32.png-w331s)

并在 Stack 选项卡中，定位到 sdrsvc.dll 调用的功能位于 sdengin2.dll 中：

![](https://images.seebug.org/content/images/2023/02/01/1675240127000-2023-01-17-11-05-46.png-w331s)

根据 `SdCheck + 0x490c2`，在 IDA 中定位到函数
`CSdCommonImpl::QueryStorageDevice`，该地址为这个函数调用 `QueryStorageDevice` 的位置。

经过补丁对比，发现了函数 `IsWritable`，这个函数进行了修改，并且被 `QueryStorageDevice` 所调用。

### 2.3 反思

这次漏洞分析遇到了几个障碍：

  1. 无法通过漏洞名称直接确认漏洞文件，导致无法使用常用的补丁对比的分析方法；
  2. exp 一开始未成功复现，这种情况对我来说很常见，但是由于不清楚原因，我以为是对备份服务的功能以及 exp 代码不熟悉导致；
  3. 由于不熟悉利用代码：
  4. 花费很多时间查找相关资料；
  5. 需要对辅助功能代码和直接漏洞利用代码进行区分。

除此之外，我之前极少分析带有 exp 且 exp 可以正常复现的漏洞，习惯从静态分析入手，再使用 windbg 动态辅助分析。一般遇到可以使用的
poc，我也是直接触发崩溃，然后使用 windbg 从崩溃开始进行调试分析，从没有使用过 procmon
进行动态监控，并且这样的方法也都成功对漏洞进行了分析，因此轻视了 procmon 动态监控方法的有效性。

不过 procmon 也不是万能的，目前看来，这个方法在漏洞点定位上十分有效，但是如果通过其他信息已经能够对漏洞点进行定位，那么 procmon
提供的帮助就不那么显著了，而且通过其他方法也能够完成漏洞分析。

## 3\. 漏洞原理

### 3.1 补丁对比

漏洞修复前：

    
    
    __int64 __fastcall IsWritable(unsigned __int16 *a1, int a2, int *a3)
    {
      ...
      v7 = -1;
      if ( a2 == 7 )
      {
        if ( !GetTempFileNameW(a1, L"SDT", 0, TempFileName) )// 如果获取 temp 文件名失败，进入 if 语句
        {
          rtnValue = v17;
    LABEL_28:
          *a3 = v6;
    toend2:
          if ( v7 != -1 )
          {
            CloseHandle(v7);
            rtnValue = v17;
          }
          goto end;
        }
        rtnValue = SxDeleteFile(TempFileName);      // 删除之前可能存在的 tmp 文件
        v17 = rtnValue;
        v8 = 0x148;
        if ( rtnValue >= 0 )                        // 删除成功
        {
          v18 = 0x148;
    LABEL_27:
          v6 = 1;
          goto LABEL_28;
        }
    toend:
        v19 = v8;
        goto end;
      }
      ...
    }

上述代码中的 a2 和传入的路径类型有关，由于利用程序传入的是 UNC 路径，因此最终程序执行流程到达此处。

根据 `GetTempFileNameW` 函数的文档说明，当其第三个参数为数值 0
时，该函数会尝试使用系统时间生成一个唯一数字文件名，如果该文件已存在，数字递增直至文件名唯一，在这种情况下，该函数会创建一个该文件名的空文件并释放其句柄。因此在漏洞修复之前，系统通过
`GetTempFileNameW` 创建临时文件是否成功的方式检查传入的 unc 路径是否可以写入，如果可以写入，再删除创建的这个临时文件。

漏洞修复后：

    
    
    __int64 __fastcall IsWritable(unsigned __int16 *a1, int a2, int *a3)
    {
      ...
      v7 = -1;
      if ( a2 == 7 )
      {
        if ( CheckDevicePathIsWritable(a1) < 0 )
        {
    LABEL_10:
          rtnValue = v16;
          *a3 = v6;
    toend2:
          if ( v7 != -1 )
          {
            CloseHandle(v7);
            rtnValue = v16;
          }
          goto end;
        }
    LABEL_9:
        v6 = 1;
        goto LABEL_10;
      }

漏洞修复后，原本 `GetTempFileNameW` 函数的位置变成了
`CheckDevicePathIsWritable`，`GetTempFileNameW` 函数的实现位于 kernelbase.dll
文件中，如果你仔细对比，会发现这两个函数中的大部分代码相同，只有一处差异点需要注意，就是在创建临时文件的时候，两者的代码如下：

    
    
    // GetTempFileNameW
    v24 = CreateFileW(lpTempFileName, GENERIC_READ, 0, 0i64, 1u, 0x80u, 0i64);
    
    // CheckDevicePathIsWritable
    v22 = CreateFileW(FileName, GENERIC_READ, 0, 0i64, 1u, 0x4000080u, 0i64);

可以看到在 `CheckDevicePathIsWritable` 函数中，`CreateFileW` 函数的第六个参数
`dwFlagsAndAttributes` 数值由 `0x80` 变成了 `0x4000080`，即从 `FILE_ATTRIBUTE_NORMAL`
变成了 `FILE_ATTRIBUTE_NORMAL | FILE_FLAG_DELETE_ON_CLOSE`。

根据文档说明，`FILE_FLAG_DELETE_ON_CLOSE` 表示文件会在所有句柄关闭时直接删除，并且之后打开该文件的请求必须包含
`FILE_SHARE_DELETE` 共享模式，否则会失败。

简单来说，修复后的代码将临时文件的创建和删除操作整合成为了一个元操作。

### 3.2 漏洞原理分析

上面补丁对比的结果可以确定这是一个条件竞争漏洞，由于临时文件的创建操作和删除操作接次发生，并且在两个操作之间没有对文件进行限制，这就导致攻击者可以创建另一线程，在临时文件创建之后，删除之前，获取文件句柄并创建机会锁阻止其他线程操作，同时将文件删除，并设置原文件路径指向其他文件，当机会锁释放后，指向的其他文件就会被删除。

## 4\. 漏洞利用

### 4.1 文件删除漏洞利用代码流程总结

  1. 在临时文件夹下，使用 `FULL_SHARING` 模式创建目录 dir ，作为上述临时文件的保存位置;
  2. 创建线程 FindFile，监控 dir 目录下的文件创建操作：
  3. 获取创建文件句柄并创建机会锁；
  4. 将创建的文件移动到其他目录下；
  5. 创建符号链接，将原文件路径指向要删除的目标文件；
  6. 释放机会锁；
  7. 主线程将目录 dir 的路径转换为 unc 格式，并通过 `CoCreateInstance` 的方式调用 sdrsvc 服务的 `CSdCommonImpl::QueryStorageDevice` 接口；
  8. sdrsvc 服务在 unc 格式目录下创建临时文件，之后删除文件。

如下图所示：

![](https://images.seebug.org/content/images/2023/02/01/1675240127000-2023-01-17-18-41-08.png-w331s)

### 4.2 提权漏洞利用

#### 4.2.1 原理分析

这部分内容基本上看 [ZDI 的文章](https://www.zerodayinitiative.com/blog/2022/3/16/abusing-arbitrary-file-deletes-to-escalate-privilege-and-other-great-tricks)就可以，这里做一下介绍。

简单来说，从 **任意文件删除** 到本地提权，需要与 MSI installer 文件运行过程进行条件竞争。

Windows Installer 服务负责应用程序的安装，而 msi
文件定义了安装过程中会发生的变化，例如创建了哪些文件夹、复制了哪些文件、修改了哪些注册表等等。因为程序安装过程中会对系统进行修改，为了避免安装出错导致系统无法恢复，msi
会在运行时创建文件夹 `C:/Config.msi`，将安装过程中做的所有更改记录到 .rbs 后缀的文件中，同时将被替换的系统文件存储为 .rbf
格式放入该文件夹。所以如果可以替换其中的 rbf 文件，就能将系统文件替换为任意恶意文件。正是因为有文件替换的风险，所以 `C:/Config.msi`
及其中的文件默认具有强 DACL。

但是如果攻击者能做到 **任意目录删除** ，就可以将 `C:/Config.msi` 删除，重新创建一个弱 DACL 的 `C:/Config.msi`
目录，并在 msi 程序创建完 rbs 和 rbf 文件之后，对其进行替换，使用恶意 rbf 文件实现提权。

具体来看，msi 在运行时经历了 **创建- >删除->再创建** 的过程，之后才会开始创建 rbs 文件，因此 **任意目录删除** 需要在
**再创建** 之后，rbs 文件创建之前删除 `C:/Config.msi` 目录，并监控 rbs 文件的产生，对文件进行替换，条件竞争就发生在这里。

上面提到的漏洞是 **任意目录删除** ，如果发现的是 **任意文件删除** ，可以删除
`C:/Config.msi::$INDEX_ALLOCATION` 数据流，同样可以实现目录的删除。

利用任意文件删除漏洞实现提权的流程如下图所示：

![](https://images.seebug.org/content/images/2023/02/01/1675240127000-2023-01-18-08-23-32.png-w331s)

#### 4.2.2 失败原因分析

上面介绍的流程把 **Config.msi 的删除** 当作一个元操作，但在 CVE-2023-21752
这个漏洞中，文件删除同样需要条件竞争才能实现，具有相对繁琐的步骤。也就是说想要利用这个漏洞实现本地提权，需要同时实现赢得两个条件竞争，这也是我一开始复现总是失败的原因。

为了方便了解利用代码的执行流程，我对代码中的注释进行了添加和修改，得到了如下的执行结果：

    
    
    PS C:\Users\exp\Desktop> C:\Users\exp\Desktop\SDRsvcEop.exe
    [wmain] Config.msi directory created!
    [wmain] Directory: C:\users\exp\appdata\local\temp\3bbbd2cf-7baf-42b7-98ea-242f703b08f8
    [wmain] Got handle of uuid directory
    [wmain] Finish create oplock for config.msi
    
    [Trigger] Path: \\127.0.0.1\c$\Users\exp\AppData\Local\Temp\3bbbd2cf-7baf-42b7-98ea-242f703b08f8
    [FindFile] Found added file C:\users\exp\appdata\local\temp\3bbbd2cf-7baf-42b7-98ea-242f703b08f8\SDT73B.tmp
    [FindFile] Got handle of C:\users\exp\appdata\local\temp\3bbbd2cf-7baf-42b7-98ea-242f703b08f8\SDT73B.tmp
    [cb] Oplock!
    [Move] Finish moving to \??\C:\windows\temp\c5b82788-8133-4971-b351-38f58233ced1
    [CreateJunction] Junction \\?\C:\Users\exp\AppData\Local\Temp\3bbbd2cf-7baf-42b7-98ea-242f703b08f8 -> \RPC Control created!
    [DosDeviceSymLink] Symlink Global\GLOBALROOT\RPC Control\SDT73B.tmp -> \??\C:\Config.msi::$INDEX_ALLOCATION created!
    [FindFile] End
    
    [Move] Finish moving to \??\C:\windows\temp\0f1161f2-a8c5-4798-a71d-f32ebba87125
    [install] MSI file: C:\windows\temp\MSI72F.tmp
    [install] Start ACTION=INSTALL
    [cb1] Detect first create
    [cb1] Detect first delete
    [install] Start REMOVE=ALL
    [install] Start delete msi file
    
    [Fail] Race condtion failed!
    [DeleteJunction] Junction \\?\C:\Users\exp\AppData\Local\Temp\3bbbd2cf-7baf-42b7-98ea-242f703b08f8 deleted!
    [DelDosDeviceSymLink] Symlink Global\GLOBALROOT\RPC Control\SDT73B.tmp -> \??\C:\Config.msi::$INDEX_ALLOCATION deleted!

我在不同流程的结果之间添加了回车，方便观察，可以看到在 **删除文件**
流程中，程序监控到了临时文件的生成，也创建了符号链接，但是由于符号链接将临时文件链接到了
`C:/Config.msi::$INDEX_ALLOCATION` 上，而 `C:/Config.msi` 的机会锁又掌握在 msi
线程上，因此删除操作停滞了。

于此同时 msi 线程上只监测到了 `C:\\Config.msi`
的第一次创建和删除，并没有监测到第二次创建，因为这里使用了循环对创建行为进行检测，因此该线程也陷入了无限循环。

与 msi 的条件竞争失败，导致两个线程发生死锁，漏洞利用失败。

#### 4.2.3 问题解决

首先，我将利用代码的整个流程画成了如下的流程图：

![](https://images.seebug.org/content/images/2023/02/01/1675240127000-2023-01-18-16-30-28.png-w331s)

红框部分就是条件竞争失败的地点。

我尝试增加虚拟机的 CPU 数量，对监控 Config.msi 创建的代码进行优化，但是都没有成功。同时我也单独使用 procmon 监控了 msi
文件的运行过程，确定 Config.msi 目录确实发生了二次创建。

所以结论只有一个，Config.msi 目录的二次创建发生的太快了。但是既然 Config.msi
目录的二次创建是确实发生的，同时利用代码已经监测到了第一次删除的行为，那么如果这个时候就释放机会锁 2，又会如何呢？

如果不对 Config.msi 目录的二次创建进行监控，直接释放机会锁 2，因为 Config.msi 目录的二次创建时间间隔非常短，等待良久的
sdrsvc 就有机会成功删除 Config.msi。此时漏洞利用流程可以继续进行下去，并成功实现漏洞利用！

![](https://images.seebug.org/content/images/2023/02/01/1675240127000-2023-01-18-16-57-08.png-w331s)

### 3.2 符号链接的问题

之前我对利用代码中如何链接向待删除文件存在疑问，实际上这种利用手法[来自 James
Forshaw](https://vimeo.com/showcase/3416096/video/133002251)，参考链接 5 和 6
对其进行了介绍。

重分析点/Junction 是一种 NTFS 文件系统中文件夹的属性，NTFS
驱动在打开文件夹的时候会对它进行读取。可以使用它对目录之间进行链接，假设要建立目录 A 向目录 B 的重分析点，只要普通用户对目录 A
具有可写权限就能够进行，而对目录 B 的权限没有任何要求。

在 Windows 系统中，我们常提到的 C 盘目录并不是一个真的文件夹，它实际上是一个指向设备物理地址的符号链接对象，你可以使用 WinObj 在
`\GLOBAL??` 中看到 `C:` 项是一个 `SymbolicLink`。当我们访问 C
盘中的某个文件时，系统会对访问路径进行转换，转换成真正的设备物理地址。普通用户也可以在对象管理器中添加或删除符号链接，但是该行为只能在有限的目录下进行，例如
`\RPC Control`.

在上面利用代码执行结果中，有下面两行输出：

    
    
    [CreateJunction] Junction \\?\C:\Users\exp\AppData\Local\Temp\3bbbd2cf-7baf-42b7-98ea-242f703b08f8 -> \RPC Control created!
    [DosDeviceSymLink] Symlink Global\GLOBALROOT\RPC Control\SDT73B.tmp -> \??\C:\Config.msi::$INDEX_ALLOCATION created!

首先创建了攻击者可控的目录 `3bbbd2cf-7baf-42b7-98ea-242f703b08f8` 指向 `\RPC Control`
的重分析点，这样访问 `\RPC Control` 就相当于访问这个可控目录；之后在 `\RPC Control` 下面创建了一个由
`SDT73B.tmp` 指向待删除文件的符号链接，这一步就相当于将可控目录下的 `SDT73B.tmp` 指向了待删除文件，删除 `SDT73B.tmp`
就相当于删除了目标文件。

## 6\. 参考资料

  1. <https://mp.weixin.qq.com/s/dhKtb8EeBwJnBEjepHXPpg>
  2. [Windows Exploitation Tricks: Exploiting Arbitrary Object Directory Creation for Local Elevation of Privilege](https://googleprojectzero.blogspot.com/2018/08/windows-exploitation-tricks-exploiting.html)
  3. [CVE-2023-21752 exp](https://github.com/Wh04m1001/CVE-2023-21752)
  4. [ABUSING ARBITRARY FILE DELETES TO ESCALATE PRIVILEGE AND OTHER GREAT TRICKS](https://www.zerodayinitiative.com/blog/2022/3/16/abusing-arbitrary-file-deletes-to-escalate-privilege-and-other-great-tricks)
  5. [Follow the Link: Exploiting Symbolic Links with Ease](https://www.cyberark.com/resources/threat-research-blog/follow-the-link-exploiting-symbolic-links-with-ease)
  6. [Understanding and Exploiting Symbolic links in Windows - Symlink Attack EOP](https://nixhacker.com/understanding-and-exploiting-symbolic-link-in-windows/)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2045/>


## 系统信息和系统帐户

上篇已经学了如何读取注册表数据，让我们找出在注册表中的哪个位置来执行我们的取证分析。当我们开始进行取证分析时，第一步是了解系统信息。

###  **操作系统版本：**

假设我们只有分类数据来执行取证，我们可以确定从注册表中提取此数据的操作系统版本。要查找操作系统版本，我们可以使用注册表项：

  *  **SOFTWARE\Microsoft\Windows NT\CurrentVersion**

![1665800614_634a19a6ecb3e7313c734.png!small?1665800616701](https://image.3001.net/images/20221015/1665800614_634a19a6ecb3e7313c734.png!small?1665800616701)

###  **当前控制集：**

包含用于控制系统启动的机器配置数据的配置单元称为控制集。通常，我们会在一台机器的 SYSTEM 配置单元中看到两个控制集，ControlSet001 和
ControlSet002。在大多数情况下，ControlSet001 将指向机器启动时使用的控制集，而 ControlSet002 将是`last
known good`配置。他们的位置将是：

  *  **SYSTEM\ControlSet001**
  *  **SYSTEM\ControlSet002**

Windows 在机器运行时会创建一个易失性控制集，称为 CurrentControlSet
(`HKLM\SYSTEM\CurrentControlSet`)。为了获得最准确的系统信息，这是我们将参考的配置单元。可以通过查看注册表值来找出哪个控制集被用作
CurrentControlSet：

  *  **SYSTEM\Select\Current**

同样，`last known good`可以使用注册表值找到配置：

  *  **SYSTEM\Select\LastKnownGood**

![1665801065_634a1b69bc2deba8d4673.png!small?1665801067426](https://image.3001.net/images/20221015/1665801065_634a1b69bc2deba8d4673.png!small?1665801067426)

###  **计算机名称：**

在执行取证分析时确定计算机名称至关重要，以确保我们正在使用我们应该使用的机器。我们可以从以下位置找到计算机名称：

  *  **SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName**

![1665801220_634a1c0412615852b8e0f.png!small?1665801221695](https://image.3001.net/images/20221015/1665801220_634a1c0412615852b8e0f.png!small?1665801221695)

###  **时区信息：**

为了准确起见，确定计算机所在的时区很重要。将有助于我们了解事件发生时的时间顺序。要查找时区信息，可以查看以下位置：

  *  **SYSTEM\CurrentControlSet\Control\TimeZoneInformation**

![1665801307_634a1c5b82ad9d58362d7.png!small?1665801309367](https://image.3001.net/images/20221015/1665801307_634a1c5b82ad9d58362d7.png!small?1665801309367)

###  **网络接口和历史的网络：**

注册表项将提供我们正在调查的机器上的网络接口列表：

  *  **SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces**

![1665801431_634a1cd79704938504a76.png!small?1665801433419](https://image.3001.net/images/20221015/1665801431_634a1cd79704938504a76.png!small?1665801433419)

每个接口都用一个唯一标识符 (GUID) 子键表示，其中包含与接口的 TCP/IP 配置相关的值。该密钥将为我们提供 IP 地址、DHCP IP
地址和子网掩码、DNS 服务器等信息。此信息很重要。

可以在以下位置找到给定机器连接的过去网络：

  *  **SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Unmanaged**
  *  **SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Managed**

![1665801561_634a1d593395315988dcc.png!small?1665801563079](https://image.3001.net/images/20221015/1665801561_634a1d593395315988dcc.png!small?1665801563079)

这些注册表项包含过去的网络以及它们上次连接的时间。注册表项的最后写入时间指向这些网络最后一次连接的时间。

###  **自动启动程序:**

注册表项包含有关用户登录时运行的程序或命令的信息。

  *  **NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Run  
NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\RunOnce  
SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce  
SOFTWARE\Microsoft\Windows\CurrentVersion\policies\Explorer\Run  
SOFTWARE\Microsoft\Windows\CurrentVersion\Run**

![1665801737_634a1e0989389af133861.png!small?1665801739314](https://image.3001.net/images/20221015/1665801737_634a1e0989389af133861.png!small?1665801739314)

注册表项包含有关服务的信息：

  *  **SYSTEM\CurrentControlSet\Services**

请注意下面屏幕截图中 Start 键的值

![1665801956_634a1ee41a9a42fb8b433.png!small?1665801957939](https://image.3001.net/images/20221015/1665801956_634a1ee41a9a42fb8b433.png!small?1665801957939)

在此注册表项中，如果该项设置为 0x02，这意味着该服务将在启动时启动。

###  **SAM 配置单元和用户信息：**

SAM 配置单元包含用户帐户信息、登录信息和组信息。该信息主要位于以下位置：

  *  **SAM\Domains\Account\Users**

![1665802128_634a1f9070cb173cf88fe.png!small?1665802130499](https://image.3001.net/images/20221015/1665802128_634a1f9070cb173cf88fe.png!small?1665802130499)

## 执行证据

###  **用户助手** ：

Windows 会跟踪用户使用 Windows 资源管理器启动的应用程序，以便在 User Assist
注册表项中进行统计。这些密钥包含有关启动的程序、启动时间和执行次数的信息。但是，在用户辅助键中找不到使用命令行运行的程序。用户辅助键存在于 NTUSER
配置单元中，映射到每个用户的 GUID。可以在以下位置找到它：

  *  **NTUSER.DAT\Software\Microsoft\Windows\Currentversion\Explorer\UserAssist\\{GUID}\Count**

![1665802344_634a206860c8c4afb8d85.png!small?1665802346139](https://image.3001.net/images/20221015/1665802344_634a206860c8c4afb8d85.png!small?1665802346139)

###  **系统缓存：**

ShimCache 是一种用于跟踪应用程序与操作系统的兼容性并跟踪机器上启动的所有应用程序的机制。它在 Windows
中的主要目的是确保应用程序的向后兼容性。它也被称为应用程序兼容性缓存（AppCompatCache）。它位于 SYSTEM 配置单元中的以下位置：

  *  **SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache**

ShimCache 存储可执行文件的文件名、文件大小和上次修改时间。

我们的 goto 工具 Registry Explorer 不会以人可读的格式解析 ShimCache 数据，因此使用另一个名为
AppCompatCache Parser 的工具，它也是 Eric Zimmerman 工具的一部分。它将 SYSTEM
配置单元作为输入，解析数据，并输出如下所示的 CSV 文件：

![1665802503_634a210716eb11ba8cec6.png!small?1665802505083](https://image.3001.net/images/20221015/1665802503_634a210716eb11ba8cec6.png!small?1665802505083)

可以使用以下命令来运行 AppCompatCache Parser Utility：

  *  **AppCompatCacheParser.exe --csv <path to save output> -f <path to SYSTEM hive for data parsing> -c <control set to parse>**

可以使用 Eric Zimmerman 的另一个工具 EZviewer 查看输出。

###  **缓存：**

AmCache 配置单元是与 ShimCache 相关的工件。这执行与 ShimCache
类似的功能，并存储与程序执行相关的附加数据。该数据包括执行路径、安装、执行和删除时间，以及已执行程序的 SHA1 哈希值。此配置单元位于文件系统中：

  *  **C:\Windows\appcompat\Programs\Amcache.hve**

可以在 hive 中的以下位置找到有关最后执行的程序的信息：

  *  **Amcache.hve\Root\File\\{Volume GUID}\**

![1665802661_634a21a5905cc7b6f495f.png!small?1665802663490](https://image.3001.net/images/20221015/1665802661_634a21a5905cc7b6f495f.png!small?1665802663490)

###  **BAM：**

后台活动监视器或 BAM 保留后台应用程序活动的标签。类似的桌面活动主持人或 DAM 是 Microsoft Windows
的一部分，可优化设备的功耗。这两者都是 Microsoft Windows 中现代待机系统的一部分。

在 Windows 注册表中，以下位置包含与 BAM 和 DAM 相关的信息。此位置包含有关上次运行程序、其完整路径和上次执行时间的信息。

  *  **SYSTEM\CurrentControlSet\Services\bam\UserSettings\\{SID}**
  *  **SYSTEM\CurrentControlSet\Services\dam\UserSettings\\{SID}**

![1665802810_634a223a70ed6c42831e7.png!small?1665802812517](https://image.3001.net/images/20221015/1665802810_634a223a70ed6c42831e7.png!small?1665802812517)


## **Windows 计算机取证简介**

计算机取证是网络攻防战的一个重要领域，涉及收集在计算机上执行的活动的证据。它是更广泛的数字取证领域的一部分，负责对所有类型的数字设备进行取证分析，包括恢复、检查和分析在数字设备中发现的数据。数字和计算机取证的应用范围很广。

##  **Windows 注册表信息取证**

###  **注册表：**

Windows
注册表是包含系统配置数据的数据库集合。该配置数据可以是关于硬件、软件或用户信息的。它还包括有关最近使用的文件、使用的程序或连接到系统的设备的数据。从取证的角度来看，这些数据对取证是非常有益的。可以使用
regedit.exe 查看注册表，这是一个用于查看和编辑注册表的内置 Windows 实用程序。

###  **注册表结构：**

Windows 系统上的注册表都包含以下五个根键：

  1. HKEY_CURRENT_USER
  2. HKEY_HKEY_USERS
  3. HKEY_LOCAL_MACHINE
  4. HKEY_CLASSES_ROOT
  5. HKEY_CURRENT_CONFIG

![1665717063_6348d34773e304882d4fa.png!small?1665717064035](https://image.3001.net/images/20221014/1665717063_6348d34773e304882d4fa.png!small?1665717064035)

以下是 Microsoft 如何定义这些根密钥。有关以下 Windows 注册表项的更多详细信息和信息，请访问 [Microsoft
文档](https://docs.microsoft.com/en-US/troubleshoot/windows-server/performance/windows-registry-advanced-users)。

文件夹/预定义键| 描述  
---|---  
 **HKEY_CURRENT_USER**|
包含当前登录用户的配置信息的根目录。用户的文件夹、屏幕颜色和控制面板设置都存储在这里。此信息与用户的个人资料相关联。该键有时缩写为 HKCU。  
 **HKEY_USERS**|  包含计算机上所有主动加载的用户配置文件。HKEY_CURRENT_USER 是 HKEY_USERS
的子项。HKEY_USERS 有时缩写为 HKU。  
 **HKEY_LOCAL_MACHINE**|  包含特定于计算机的配置信息（对于任何用户）。此密钥有时缩写为 HKLM。  
 **HKEY_CLASSES_ROOT**|

是 的子项`HKEY_LOCAL_MACHINE\Software`。此处存储的信息可确保在您使用 Windows
资源管理器打开文件时打开正确的程序。此键有时缩写为 HKCR。

从 Windows 2000 开始，此信息存储在 HKEY_LOCAL_MACHINE 和 HKEY_CURRENT_USER 键下。该
`HKEY_LOCAL_MACHINE\Software\Classes`密钥包含可应用于本地计算机上所有用户的默认设置。
该`HKEY_CURRENT_USER\Software\Classes`键具有覆盖默认设置并仅适用于交互式用户的设置。

HKEY_CLASSES_ROOT 键提供了一个注册表视图，它合并了来自这两个源的信息。HKEY_CLASSES_ROOT 还为为早期版本的 Windows
设计的程序提供此合并视图。要更改交互式用户的设置，必须在 HKEY_CLASSES_ROOT 下
`HKEY_CURRENT_USER\Software\Classes`而不是在 HKEY_CLASSES_ROOT 下进行更改。

要更改默认设置，必须在 下进行更改`HKEY_LOCAL_MACHINE\Software\Classes`。如果您将密钥写入
HKEY_CLASSES_ROOT 下的密钥，系统会将信息存储在 下 `HKEY_LOCAL_MACHINE\Software\Classes`。

如果您将值写入 HKEY_CLASSES_ROOT 下的某个键，并且该键已经存在于
下`HKEY_CURRENT_USER\Software\Classes`，系统会将信息存储在那里而不是下
`HKEY_LOCAL_MACHINE\Software\Classes`。  
  
 **HKEY_CURRENT_CONFIG**|  包含有关本地计算机在系统启动时使用的硬件配置文件的信息。  
  
## 离线访问注册表配置单元

如果只能访问磁盘映像，则必须知道注册表配置单元在磁盘上的位置。这些配置单元中的大多数都位于`C:\Windows\System32\Config`目录中，并且是：

  1.  **默认** （安装在`HKEY_USERS\DEFAULT`）
  2.  **SAM** （安装在`HKEY_LOCAL_MACHINE\SAM`）
  3.  **安全** （安装在`HKEY_LOCAL_MACHINE\Security`）
  4.  **软件** （安装在`HKEY_LOCAL_MACHINE\Software`）
  5.  **系统** （安装在`HKEY_LOCAL_MACHINE\System`）

除了这些配置单元之外，还可以在用户配置文件目录中找到另外两个包含用户信息的配置单元。对于 Windows 7
及更高版本，用户的配置文件目录位于`C:\Users\<username>\`配置单元所在的位置：

  1.  **NTUSER.DAT** （当用户登录时安装在 HKEY_CURRENT_USER 上）
  2.  **USRCLASS.DAT** （安装在 HKEY_CURRENT_USER\Software\CLASSES 上）
  3.  **NTUSER.DAT 和 USRCLASS.DAT 是隐藏文件**

USRCLASS.DAT 配置单元位于目录中`C:\Users\<username>\AppData\Local\Microsoft\Windows`

![1665718458_6348d8bab2d9e27db89d3.png!small?1665718459412](https://image.3001.net/images/20221014/1665718458_6348d8bab2d9e27db89d3.png!small?1665718459412)

![1665725772_6348f54c2ebf2fb4b941f.png!small?1665725772871](https://image.3001.net/images/20221014/1665725772_6348f54c2ebf2fb4b941f.png!small?1665725772871)

###  **Amcache**

AmCache 配置单元。位于`C:\Windows\AppCompat\Programs\Amcache.hve`. Windows
创建此配置单元以保存有关最近在系统上运行的程序的信息。

###  **事务日志和备份：**

取证数据来源是注册表事件日志和备份。事件日志可以被认为是注册表配置单元更改日志的日志。在将数据写入注册表配置单元时，Windows
经常使用事件日志。这意味着事务日志通常可以在注册表中包含尚未进入注册表配置单元本身的最新更改。每个 hive 的事件日志作为 .LOG 文件存储在与
hive 本身相同的目录中。它与注册表配置单元同名，但扩展名为 .LOG。例如，SAM
配置单元的事务日志将位于`C:\Windows\System32\Config`在文件名 SAM.LOG
中。有时也可能有多个事务日志。在这种情况下，它们将具有 .LOG1、.LOG2 等作为其扩展名。

  

注册表备份与事件日志相反。这些是位于`C:\Windows\System32\Config`目录中的注册表配置单元的备份。`C:\Windows\System32\Config\RegBack`这些配置单元每十天被复制到
目录中。如果怀疑某些注册表项最近可能已被删除/修改，可查看此位置。

## Windows取证数据采集

虽然我们可以通过注册表编辑器查看注册表，但取证正确的方法是获取此数据的副本并对其进行分析。但是，当从复制注册表配置单元时`%WINDIR%\System32\Config`，我们不能，因为它是受限制的文件。那么，现在该怎么办？

为了获取这些文件，可以使用以下工具之一：

  1. [KAPE](https://www.kroll.com/en/services/cyber-risk/incident-response-litigation-support/kroll-artifact-parser-extractor-kape)是一种实时数据采集和分析工具，可用于获取注册表数据。它主要是一个命令行工具，但也带有一个 GUI。![1665727525_6348fc25c42274ebe6ad8.png!small?1665727526638](https://image.3001.net/images/20221014/1665727525_6348fc25c42274ebe6ad8.png!small?1665727526638)![1665727551_6348fc3f0d71cd592f736.png!small?1665727552067](https://image.3001.net/images/20221014/1665727551_6348fc3f0d71cd592f736.png!small?1665727552067)
  2. [Autopsy](https://www.autopsy.com/)使你可以选择从实时系统或磁盘映像中获取数据。添加数据源后，导航到要提取的文件的位置，然后右键单击并选择提取文件选项。它看起来与您在下面的屏幕截图中看到的相似。![1665727598_6348fc6e730b497a79dbb.png!small?1665727599423](https://image.3001.net/images/20221014/1665727598_6348fc6e730b497a79dbb.png!small?1665727599423)![1665727618_6348fc82c4160df0563e5.png!small?1665727620069](https://image.3001.net/images/20221014/1665727618_6348fc82c4160df0563e5.png!small?1665727620069)
  3. [FTK Imager](https://www.exterro.com/ftk-imager)类似于 Autopsy，允许通过在 FTK Imager 中安装所述磁盘映像或驱动器来从磁盘映像或实时系统中提取文件。

![1665727725_6348fced28b7cf934c218.png!small?1665727726844](https://image.3001.net/images/20221014/1665727725_6348fced28b7cf934c218.png!small?1665727726844)

## Windows 探索注册表

一旦提取了注册表配置单元，需要一个工具来查看这些文件，就像我们在注册表编辑器中一样。由于注册表编辑器仅适用于实时系统并且无法加载导出的配置单元，因此可以使用以下工具：

###  **注册表查看器：**

[AccessData 的注册表查看器](https://accessdata.com/product-download/registry-viewer-2-0-0)具有与 Windows 注册表编辑器类似的用户界面。但是，有一些限制。它一次只加载一个配置单元，并且不能考虑事务日志。

  * 如图所示

![1665728244_6348fef42762f19fe3111.png!small?1665728244828](https://image.3001.net/images/20221014/1665728244_6348fef42762f19fe3111.png!small?1665728244828)

###  **Zimmerman 的注册表浏览器：**

Eric Zimmerman
开发了一些对执行数字取证和事件响应非常有用的[工具。](https://ericzimmerman.github.io/#!index.md)其中之一是注册表浏览器。它可以同时加载多个配置单元，并将事务日志中的数据添加到配置单元中，以使用更多最新数据制作更“干净”的配置单元。它还有一个方便的“书签”选项，其中包含取证调查人员经常寻找的重要的取证注册表项。调查人员可以通过书签菜单项直接访问感兴趣的注册表项和值。

  * 如图所示

![1665728965_634901c5ca5802f118cde.png!small?1665728966631](https://image.3001.net/images/20221014/1665728965_634901c5ca5802f118cde.png!small?1665728966631)

[RegRipper](https://github.com/keydet89/RegRipper3.0)是一个实用程序，它将注册表配置单元作为输入并输出一个报告，该报告从该配置单元中的一些取证重要的键和值中提取数据。输出报告在一个文本文件中，并按顺序显示所有结果。

  * 如图所示

![1665729136_63490270656e753ebcad0.png!small?1665729137281](https://image.3001.net/images/20221014/1665729136_63490270656e753ebcad0.png!small?1665729137281)


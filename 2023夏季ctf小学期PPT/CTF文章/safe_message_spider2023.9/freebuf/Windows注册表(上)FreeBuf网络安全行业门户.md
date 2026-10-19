# Windows注册表

>
> 注册表是Windws操作系统的核心，它实际上是一个非常庞大的树状分层结构数据库(以键和子键的方式组织起来)，其中存储着系统用户、硬件、软件和用户环境等所有配置信息

![此图像的alt属性为空；文件名为2230-1024x650.png](https://image.3001.net/images/20201129/1606642667_5fc36beb53c831139a382.png!small)

  

## 概述(几点关于注册表的补充)

1：注册表中记录了用户安装在计算机上的软件和每个程序的相关信息。 **通过注册表可以修改、配置硬件、软件等数据信息**

2：注册表 **允许对硬件、系统参数、应用程序和设备驱动程序进行跟踪配置**

3：当 **Windows检测到机器上的新设备时，就把有关数据保存在注册表中，可以避免新设备与原设备之间的资源冲突**

4： **注册表文件的数据信息保存在C:/Windows中的system.dat和user.dat** 中，利用regedit.exe对其读取

5： **HKEY即Hot KEY，指一些快捷方式**

6：Windows使用键值的方式来管理热键注册表， **所有的快捷操作都需要通过定义键值并且把键值添加（注册）到注册表之后才能生效** ；

## 注册表中的文件类型

 **REG_SZ** ：字符串，文本字符串。  
 **REG_MULTI_SZ** ：多字符串，含有多个文本值的字符串。  
 **REG_BINARY** ：二进制数，二进制值，以十六进制显示。  
 **REG_DWORD** ：双字，一个32位的二进制值，显示为8位的十六进制值。

## 注册表中的五大根键

 **1：HKEY_CLASSES_ROOT**

 **2：HKEY_CURRENT_USER**

 **3：HKEY_LOCAL_MACHINE**

 **4：HKEY_USERS**

 **5：HKEY_CURRENT_CONFIG**

### HKEY_CLASSES_ROOT

 **(由HKEY_LOCAL_MACHINE\Software\classes复制而来)**

> 该根键 **包括启动每个应用程序的全部所需信息** ， **当点击启动一个应用程序时，就会在注册表中所引导与该程序相关的所有信息**
> (包括拓展名、应用程序与文档之间的关系、驱动程序名、OLE信息、类ID编号和对应图表等)

![此图像的alt属性为空；文件名为捕获2306-1024x646.png](https://image.3001.net/images/20201129/1606642672_5fc36bf04b2ffd0f178ec.png!small)

  

#### 名称由来

 **ROOT** 表示这是某种类型的HKEY(快捷方式)的根目录， **该种类型的所有HKEY都存放在这个目录下**

#### 分类

 **1：已经注册的各类文件的扩展名**

如上图所示

 **2：各种文件类型的有关信息**

![此图像的alt属性为空；文件名为捕获1704-350x1024.png](https://image.3001.net/images/20201129/1606642678_5fc36bf688c710d08aefd.png!small)

图为HKEY_CLASSES_ROOT表中关于QQ音乐支持格式的信息

  

![此图像的alt属性为空；文件名为注册表ROOT主键-506x1024.png](https://image.3001.net/images/20201129/1606642693_5fc36c052f626ec4068fe.png!small)

Bandzip支持解压的文件拓展名

  

#### HKEY_CLASSES_ROOT子键介绍：

 **文件拓展名子键** (后缀键)： **以‘.’开头的键** ，Windows会将这样的键当作文件的后缀名，其包含了关联文件类型、打开方式等

 **类存储子健** ： **以‘*’开头的键，以及所有不以‘.’开头的键** ，其中包括文件类型、类标识符以及程序标识符

* * *

##### 每个子键中的可配置参数

![此图像的alt属性为空；文件名为101-1.png](https://image.3001.net/images/20201129/1606642696_5fc36c082671407bea7e4.png!small)

  

 **DefaultIcon**
：定义默认图标，若在.PNG键下建立defaulticon子键，并为其配置一个Icon的绝对路径，那么所有以.PNG结尾的图片都会以该图标作为自己的默认图标

 **shell** ：定义命令解释器(所有在GUI界面下打开的应用，实则都是通过命令解释器输入命令打开的)

 **open** ：shell子键下可定义open子建，用来定义如何用命令解释器打开一个文件

 **command** ：open子键下可定义command子键，表示用一条命令来打开一个文档或程序，command的键值就是指定应用程序的绝对路径(
**%1：启动；%0：不启用；%2：二进制** )

![此图像的alt属性为空；文件名为捕获1013.png](https://image.3001.net/images/20201129/1606642700_5fc36c0c3fa6e0454c21d.png!small)

  

* * *

### HKEY_CURRENT_USER

 **根据不同用户，从HKEY_USERS复制而来**

![此图像的alt属性为空；文件名为1036-1024x254.png](https://image.3001.net/images/20201129/1606642705_5fc36c110040df14cde1d.png!small)

  

> 管理系统当前的用户信息， **保存了本地计算机中存放的当前登录用户的全部信息** (包括程序的配置等等)

在一个用户登陆Windows时， **会将该用户对应的信息从HKEY_USERS拷贝到HKEY_CURRENT_USER中**

#### HKEY_CURRENT_USER子键介绍

#####  **AppEvents**

![此图像的alt属性为空；文件名为1123捕获-1.png](https://image.3001.net/images/20201129/1606642708_5fc36c14b731c33bda376.png!small)

  

> 该子键存储了系统时间的声音设置

在下面分为 **EventLabels** 和 **Schemes** 两个子键

 **EventLabels**

储存了每个事件的标识及名称

 **Schems**

 **关联了每个事件和声音** 。

下有“Apps”和“Name”两个子键

 **Apps子键** ：下储存了系统事件的声音设定，一般每个事件下有两个子键 **.Current和.Default**
，它们分别指明了当前的声音文件和默认的声音文件的位置。

![此图像的alt属性为空；文件名为1124.png](https://image.3001.net/images/20201129/1606642712_5fc36c18b1036f6f3c634.png!small)

  

![此图像的alt属性为空；文件名为1126-1024x444.png](https://image.3001.net/images/20201129/1606642726_5fc36c26d9e0b50863e1e.png!small)

  

![此图像的alt属性为空；文件名为1127-1024x447.png](https://image.3001.net/images/20201129/1606642733_5fc36c2d2df771846e24c.png!small)

  

 **Name子键** ：储存了声音配音方案的名称

#####  **Control Panel**

> 包含的内容与桌面、光标、键盘和鼠标等设置有关

其中包含：Accessibility、Appearance、Cursors、Desktop、Input
Method、International、Keyboard、PowerCfg

 **Accessibility**

![此图像的alt属性为空；文件名为1151.png](https://image.3001.net/images/20201129/1606642737_5fc36c31c13ca0ab28741.png!small)

  

> 只有在安装了Windows系统辅助选项后才会出现，

  *  **高对比度显示设置子键** “HighContrast”
  *  **键盘设置子键** “KeyboardResponse”
  *  **鼠标设置子键** “MouseKeys”
  *  **声音显示设置子键** “ShowSounds”
  *  **声音卫士设置子键** “SoundSentry”
  *  **粘滞键设置子键** “StickyKeys”
  *  **自动重新设置辅助选项子键** “TimeOut”
  *  **切换键设置子键** “ToggleKeys”

 **Appearance**

![此图像的alt属性为空；文件名为815-1024x252.png](https://image.3001.net/images/20201129/1606642741_5fc36c35cfee0f7434bef.png!small)

  

该子键存储了 **系统中可供选择的各种颜色设置方案**

 **Cursors**

![此图像的alt属性为空；文件名为11111-1024x815.png](https://image.3001.net/images/20201129/1606642750_5fc36c3ed04b35f457be2.png!small)

  

该子键存储了 **系统中使用光标的图案、大小等一系列与光标有关的参数**

 **Desktop**

![此图像的alt属性为空；文件名为2222.png](https://image.3001.net/images/20201129/1606642756_5fc36c44915c0dfdb7f91.png!small)

  

![此图像的alt属性为空；文件名为3333-1024x843.png](https://image.3001.net/images/20201129/1606642759_5fc36c47bcaebafe21915.png!small)

  

该子键 **储存了系统桌面和窗口的设置信息，如窗口边界、标题、图标、菜单、滚动条等的设置**

WindowsMetrics：储存了系统窗口的各项设置(如长宽、图标等等)

 **Input Method**

![此图像的alt属性为空；文件名为55555.png](https://image.3001.net/images/20201129/1606642764_5fc36c4cba4f142f63f6a.png!small)

  

![此图像的alt属性为空；文件名为66666.png](https://image.3001.net/images/20201129/1606642767_5fc36c4f7742894356b7e.png!small)

  

该子键 **储存了相关热键的搭配** (可以通过修改Hot Keys中的值来修改操作对应的热键)

Microsoft官方文档(不过好像是Win7的，与Win10在编号上有一定区别)

<https://docs.microsoft.com/en-us/previous-versions/windows/embedded/ms904626(v=msdn.10)?redirectedfrom=MSDN>

* * *

如何 **禁用shift+ctrl切换输入法** (在IDE中会很烦)：将编号为00000070子键中的Key Modifiers修改为00 c0 00
00；Virtual Key修改为ff 00 00 00

* * *

![此图像的alt属性为空；文件名为7777.png](https://image.3001.net/images/20201129/1606642771_5fc36c53405232bce210c.png!small)

  

 **Internatonal**

区域设置的有关信息

 **Keyboard**

键盘击键的重复延时和重复速率

 **Mouse**

![此图像的alt属性为空；文件名为8888.png](https://image.3001.net/images/20201129/1606642773_5fc36c55e53dd73a1b0af.png!small)

  

鼠标点击有关信息

 **PowerCfg**

电源管理的有关设置

#####  **Environment**

Windows中默认先便利系统环境变量，再遍历用户环境变量

![此图像的alt属性为空；文件名为Environment变量-1024x317.png](https://image.3001.net/images/20201129/1606642778_5fc36c5a0a5d9af9ac630.png!small)

  

>  **环境变量** 作用：当要求系统运行一个程序而没有告诉它程序所在的完整路径时，系统除了在当前目录下面寻找此程序外，还应到 **path**
> 中指定的路径去找(当在命令行中键入一条命令时，cmd会先到该目录下寻找该文件，若未寻找到，就到环境变量中进行遍历)

 **环境变量分为** ：用户环境变量(只对单个用户起作用)与系统环境变量(对所有用户起作用)

 **Environment**
对应的为当前用户的环境变量(但由于目前绝大部分个人PC只有Administrator一个用户，所以在用户变量中配置与在系统变量中配置却别不大)

 **HKEY_CURRENT_USER中的用户环境变量与HKEY_USER中的用户环境变量是相互影响的** ，改变一个后，另外一个也会变化

 **环境变量调用方法** ：在运行界面中输入 %名称%(在cmd中可以用 echo %环境变量名称% 来查看环境变量对应的值)

* * *

 **1：其中TMP、TEMP为Windows运行期间产生的临时文件对应的存放路径**
(这些临时文件与虚拟内存的却别在于：临时文件时针对于每个程序的，也就是说TMP、TEMP中有对应每个程序在运行期间的临时文件)

其路径中的 **%USERPROFILE%** 在系统环境变量中定义并指向 /USERS/1186 (本机用户的文件路径)

![此图像的alt属性为空；文件名为userprofile.png](https://image.3001.net/images/20201129/1606642781_5fc36c5d95f54712b6a2e.png!small)

  

 **2：其中path变量** 的值是用户变量中的值与系统变量中的值的叠加。系统环境变量对全部用户起作用,而用户环境变量仅仅对当前用户起作用

* * *

##### Software

 **储存了系统中各种软件的配置信息** ，它是HKEY_CURRENT_USER主键下最主要的子键，也是USER.DAT文件的主要部分

##### Volatile Environment

![此图像的alt属性为空；文件名为Volatile-Environment.png](https://image.3001.net/images/20201129/1606642784_5fc36c6087486068a8b87.png!small)

  

 **APPDATA** 对应的路径是应用程序默认数据存放目录  
 **HOMEDRIVE** 对应的内容就是系统安装盘符  
 **HOMEPATH** 对应的路径就是用户目录  
 **LOCALAPPDATA** 对应的路径是用户程序数据本地存放目录  
 **LOGONSERVER** 对应的是本机服务器地址(带\是用于服务器访问的，就相当于网址http:后面的\\)  
 **USERDOMAIN** 对应的是本机用户域名名称(因为只是一个名称，所以不需要\\)  
 **USERNAME** 对应的内容是本机的用户名  
 **USERPROFILE** 对应的路径就是本机用户名的相关配置存储目录

###  **HKEY_LOCAL_MACHINE**

![此图像的alt属性为空；文件名为HKEY_LOCAL_MACHINE.png](https://image.3001.net/images/20201129/1606642787_5fc36c635ee1ec349c490.png!small)

  

> HKEY_LOCAL_MACHINE上注册表的核心主键， **记录了计算机上的所有硬件和软件的配置**

##### BCD00000000

![此图像的alt属性为空；文件名为bcd1.png](https://image.3001.net/images/20201129/1606642790_5fc36c66d7df3f75b37dc.png!small)

  

> BCD全称 **Boot Configuration Data(引导配置数据)** ，
> **BCD含有Windows的参数配置信息以及控制如何启动Windows的所有信息**
> ，若机器安装了多个系统，每个系统的启动程序也在BCD中(在Windows
> Visita前的操作系统这些信息是保存在Boot.ini文件或非易失性内存里面的，但由于Boot.ini可被修改，所以安全性不高)

* * *

关于BCD详细参数的介绍，网上资料不多，一些英文文档中也只有已知常见的几种GUID代表的含义，所以本文章直接只介绍目前了解到的几种已知BCD中的含义(我已知的......)，未来再学习到会及时更新

* * *

###### BCD主要的几种查看/修改的方式

1：通过在cmd中 **调用bcdedit**

2：注册表 **HKEY_LOCAL_MACHINE中查看**

3： **Windows为BCD提供了编程接口** ：BCD Windows管理规范（WMI）提供程序是一个管理界面，可用于编写修改BCD的实用程序的脚本

###### BCD位置：

 **基于BIOS的操作系统** ：BCD注册表文件位于活动分区的\ Boot \ bcd目录中

 **基于EFI的操作系统** ：BCD注册表文件位于EFI系统分区上

###### BCD相关字段含义及结构：

 **结构(在注册表中有特殊含义子键的含义都位于Object的Element中)：**

![此图像的alt属性为空；文件名为bcd文件分类.png](https://image.3001.net/images/20201129/1606642794_5fc36c6aaddb99a81b08f.png!small)

利用bootice工具图形化查看Object中子键代表的含义是(不全)

  

 **精细化介绍1(通过注册表)：**

在注册表中随意打开一个GUID查看其中Element的结构：

![此图像的alt属性为空；文件名为1642.png](https://image.3001.net/images/20201129/1606642797_5fc36c6d69a84fe53e863.png!small)

  

1： **120000002键** ：用于指定调用文件的路径(如该目录 **表示启动windows启动管理器的位置**
，为了加快启动速度，在没有双系统的情况下启用fast boot后，会禁用windows boot
manager直接windows启动加载器winload.efi)

![此图像的alt属性为空；文件名为12oooooo2.png](https://image.3001.net/images/20201129/1606642801_5fc36c71ef4b3df834586.png!small)

  

* * *

关于Windows启动管理器与Windows启动加载器的介绍见(写的很详细)：<https://www.win10zjb.com/win10jc/8455.html>

鉴于大家可能懒得看，所以就Copy一份来

  

Windows10/8/7 的启动过程和开机加载数据流程介绍。Windows10虽然是微软 Windows操作系统的最新版本，但是其启动过程与
Windows Vsta/7/8类似。下面以在基于BIOS的计算机中启动 Windows10操作系统为例，介绍了从按下计算机电源按钮到启动并登录
Windows10 操作系统的整个过程中所发生的操作，具体如下。  
1.按下计算机电源按钮后，首先进行通电自检(POST， Power On Self
Test)，由BlOS检测和识别硬件并完成硬件的基本配置。然后查找第一启动设备，接着从该设备读取并运行主引导记录(MBR， Master Boot
record)，之后将控制权交给MBR。  
2.MBR查找其所在硬盘的硬盘分区表，找到标记为“活动”的主分区。然后在该分区的根目录中找到并运行操作系统的加载程序(文件名为 Bootmgr)，即
Windows启动管理器，之后将控制权交给 Windows启动管理器。  
3.Window启动管理器读取启动配置数据(BCD， Boot Configuration Data)存储中的内容以决定操作系统的启动方式。  
◆ 如果计算机中只安装了一个操作系统，或将操作系统列表的显示时间设置为0，那么将不会显示系统启动列表， Windows启动管理器会直接运行
Windows启动加载器(Windows Boot Loader，文件名为Winload. exe)。  
◆ 如果计算机中同时安装了多个操作系统，Windows启动管理器会根据 BCD 存储中的内容创建并显示一个系统启动列表，用户可以从中选择要启动的操作系统。  
◆ 如果是从休眠状态恢复计算机，那么Windows启动管理器将会运行 Windows 恢复加载器(文件名为 Winresume.exe)。  
4.Windows启动管理器运行 Windows启动加载器，启动加载器使用固件接口的启动服务完成操作系统的启动工作并加载操作系统及其相关数据。  
◆ 加载操作系统内核 Ntoskrnl.exe和硬件抽象层HAL(文件名为Had)。  
◆ 加载注册表中的 HKEY LOCAL MACHINE SYSTEM 子键。  
◆ 加载注册表中的 HKEY- LOCAL MACHINE Systemservices 子键中存储的硬件设备驱动程序。  
◆ 启用内存分页。  
5.加载完所需数据后， Windows启动加载器将控制权交给操作系统内核。系统内核和HAL开始初始化 Windows操作系统并处理位于注册表中的HKEY
LOCAL MACHINE SYSTEM Curentcontrolse 子键中的配置信息，然后启动设备驱动程序和系统服务。  
6.内核启动会话管理器(文件名为 Smss.exe)，然后执行以下操作。  
◆ 创建系统环境变量并对系统环境进行初始化。  
◆ 启动Wn32子系统(文件名为Csrss.exe)将文本显示模式切换为图形显示模式。  
◆ 启动Windows登录管理器(文件名为Winlogon.exe)，然后启动服务控制管理器(文件名为 Services.eXe)和本地安全机构(文件名为
Lsass. exe)并等待用户登录。  
◆ 创建虚拟内存页面文件。  
◆ 对一些必要的文件进行重命名。  
7.在使用用户名和密码进行登录后，登录用户界面和默认凭据提供程序会将用尸名和密码等信息传递给本地安全机构以进行身份验证。验证通过后
Windows登录管理器会运行 Userinit.exe 和 Windows外壳， Userinit.
ex会创建用户环境变量以便初始化用户环境，还会运行所有需要自动启动的 Windows服务。最后完成系统登录并显示 Windows桌面。  
当使用安全模式等非常规模式启动系统时实际上只是临时修改了系统的启动方式，而并没有永久性地修改BCD存储中的内容。此外，用户可以通过编辑BCD存储中的内容来控制操作系统的启动方式。BCD存储包含在一个名为BCD的注册表文件中，固件接口的类型决定了BCD文件在磁盘中的位置。  
◆ 基于 BIOS 的计算机:BCD文件位于活动分区的Boot文件夹中。  
◆ 基于 EFIUEF 的计算机:BCD文件位于EFI系统分区中。

  

* * *

2： **12000004键** ：设定在 Boot Manager 的启动菜单上显示内容的(在安装双系统启动时，选择系统的页面代表Windows的名称)

![此图像的alt属性为空；文件名为12400.png](https://image.3001.net/images/20201129/1606642803_5fc36c73b5bba83f69db5.png!small)

  

3： **12000005 键** ：用于指定Boot Manager的语言，如果安装了 Windows Vista 的简体中文版本，那么这里的内容一定是
zh-CN，如果你想使用英文版的Boot Manager，那么只需要修改为 en-US即可(不过前提是需要在C:\Boot 目录下有一个 en-US的目录，而且里面有相应的en-US语言的资源文件)

![此图像的alt属性为空；文件名为12000005.png](https://image.3001.net/images/20201129/1606642806_5fc36c767b15ae6269a37.png!small)

  

 **以上三个参数在有该参数的Elememt子键中含义相同**

 **精细化介绍2(通过bcdedit)**

>  **bcdedit命令可以增删改查BCD**
> (前提在Administrator模式下)，下面将介绍bcdedit查看的BCD与对BCD的操作(具体详细命令自己搜索即可)
    
    
    C:\WINDOWS\system32>bcdedit
      
      
    Windows Boot Manager
      
    --------------------      
    identifier              {bootmgr}
      
    device                  partition=\Device\HarddiskVolume2
      
    description             Windows Boot Manager
      
    locale                  en-US
      
    inherit                 {globalsettings}
      
    integrityservices       Enable
      
    default                 {current}
      
    resumeobject            {ce153eb7-3786-11e2-87c0-e740e123299f}
      
    displayorder            {current}
      
    toolsdisplayorder       {memdiag}
      
    timeout                 30
      
      
    Windows Boot Loader
      
    -------------------      
    identifier              {current}
      
    device                  partition=C:
      
    path                    \WINDOWS\system32\winload.exe
      
    description             Windows 10  
    locale                  en-US
      
    inherit                 {bootloadersettings}
      
    recoverysequence        {ce153eb9-3786-11e2-87c0-e740e123299f}
      
    integrityservices       Enable
      
    recoveryenabled         Yes
      
    allowedinmemorysettings 0x15000075
      
    osdevice                partition=C:
      
    systemroot              \WINDOWS
      
    resumeobject            {ce153eb7-3786-11e2-87c0-e740e123299f}
      
    nx                      OptIn
      
    bootmenupolicy          Standard
      
    hypervisorlaunchtype    Auto
    

由于BCD采用二进制的方式存储，所以在注册表中其余参数阅读较为困难，可以采用bcdedit来查看具体信息(bcdedit只能查看到BCD中Windows
Boot Manager与Windows Boot Loader的信息，其余信息无法查看)

 **bcdedit基础命令格式(通过实际命令介绍)**

    
    
    bcdedit /set {current} description deutsh

解释：将identifier为current(也就是Windows启动加载器)中的description修改为deutsh(对于启动路径切记不可随意修改，否则系统崩溃)

![此图像的alt属性为空；文件名为修改BCD后.png](https://image.3001.net/images/20201129/1606642808_5fc36c7864a788534c6c3.png!small)

  

    
    
    bcdedit /default current 

解释： **将当前系统设为默认启动系统** (同样，如果后面接一串其它系统的GUID，就表示将那个系统设为默认启用系统)

 **精细化介绍3(通过工具bootice)**

通过工具就简单许多，具体看图即可

![此图像的alt属性为空；文件名为BCD.png](https://image.3001.net/images/20201129/1606642812_5fc36c7c0af827ee3d411.png!small)

  

  


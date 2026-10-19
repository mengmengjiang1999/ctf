## Windows计算机取证

### Windows现场取证流程

![Windows现场取证流程](https://image.3001.net/images/20230606/1686023383_647eacd70300a0d52e31f.png!small)

去现场勘察之前要准备好案件同步，物证，取证工具，现场取证的U盘硬盘，录像机，物证袋，封条等等。

收集相关的物证比如电脑，手机，外设(光盘，硬盘，U盘，数据连接线)，设备等。

如果计算机在开机状态要准备好在线取证，对于在计算机上正在运行的重要数据，重要程序，执行的指令等进行固定。

如果计算机在关机状态就要使用到离线启动的方式，因为正常取证流程是不应该对它进行开机的，要使用引导启动。(比如取证U盘插入后使用U盘里的系统引导着启动)，如果开启了固件加密，那么只能启动本身的系统，无法引导启动。

### 计算机存储介质的封存方法

windows的设备有主机，一体机，笔记本，平板，手机等。

#### 笔记本电脑

将笔记本电脑闭合，使用封条封住笔记本电脑的开合口，数据接口和硬盘拆卸口，使之在拆封前无法打开电源，无法使用任何数据接口，无法拆卸硬盘。

#### 台式机

记录台式电脑所有外设的接口位置，然后拔出，使用封条封住电脑的数据接口，电源接口和侧面版接缝，使之在拆封前无法通电，无法使用任何数据接口，无法拆卸硬盘。封好后贴上标签
-> 属于谁，封存的时间，运行状况。

#### 其他存储介质的封存方法

硬盘，U盘：直接用物证袋进行封存，使之在拆封前无法使用。封好后贴上标签 -> 编号，名称，提取时间，签名，备注。

### Windows开机状态处理方法

![Windows开机状态处理方法](https://image.3001.net/images/20230606/1686023383_647eacd7b6bf340aaf712.png!small)

首先查看下电脑里面正在运行的程序，重点查看加密文件，加密容器，运行的聊天软件，登录的网站后台等重要程序，查找涉案关键性数据，文件内容可能为加密容器的解密密钥。同时要查看下计算机是否有远程，远程分为主控方和被控方，如果计算机是主控方要及时的进行远程数据固定，如果是被控方要先保证好网络环境避免被他人远程破坏。

要优先固定易失数据，比如电脑正在运行的网站后台，远程连接，正在运行的程序等，及时制作内存镜像。

#### 网页现场紧急固定

首先看一下网页设置里是否关闭了`关闭窗口时清除数据`，如果设置了要及时把这个取消。

![image-20230516202649936](https://image.3001.net/images/20230606/1686023384_647eacd84050c5e08e5f7.png!small)

  1. 录屏：注意不要存储在涉案计算机，可以借用摄像机，执法记录仪，手机等工具，要进行时间校准。

  2. 网站账号密码固定：注意电脑桌面的便签，记事本，有道笔记等应用。

  3. 厂商网站固定工具截长图：如果有长截图工具可以利用长截图工具。

 **网站密码获取**

有些浏览器有记录密码自动填写功能，要获取明文需要浏览器密码进行获取，如果不知道浏览器密码可以前往目标网站进行自动填写，然后修改网页源代码密码这一栏中type属性password修改为text再回车，就可以显示明文密码。

![image-20230516203019077](https://image.3001.net/images/20230606/1686023384_647eacd8e5d88dcd2e44e.png!small)

![image-20230516203038324](https://image.3001.net/images/20230606/1686023385_647eacd984042eb0f6e2b.png!small)

#### 通联工具现场紧急固定

qq，微信，境外软件等查看里里面有没有跟上下级进行联系或者有没有重要数据，浏览完后进行固定。

可以使用软件自带的记录备份与恢复功能，然后需要进行录屏或者截图备份。

#### 远程运维管理工具勘查

 **向日葵**

手机号登录的可以在软件中点击升级跳到浏览器界面后可以查看完整的手机号。

微信登录的需要在向日葵的日志文件中搜索account0就可以看到登录微信号所绑定的手机号。

![image-20230516203507908](https://image.3001.net/images/20230606/1686023386_647eacda2e3873f820c55.png!small)

![image-20230516203554913](https://image.3001.net/images/20230606/1686023386_647eacdaa2a48c6915f0f.png!small)

#### 远程运维管理工具日志勘查

 **向日葵**

​ 一般对于文件名有shell和service这两类文件进行重点排查，里面一般有被控制或者控制端的ip地址(sunlogin_service.时间-数字.log)。

搜索关键字：

  * P2Phelper: 被控制端IP地址；

  * P2PStream: 控制端IP地址(公网IP)；

  * P2Phelper和P2PStream只对主控机有效；

  * P2PAccepter和service只对被控机有效；

  * udpwrapper和udp对双端都有效；

#### 虚拟币钱包识别及固定

注意电脑中涉及的虚拟币交易程序和地址，交易程序目前以手机居多，计算机多以web方式，这块要注意查看浏览器浏览记录，同时要注意虚拟币地址，如:`1QasfaWSXA5SdlS7SDSFhjxcewCFHN5Uz3`

助记词：用来进行虚拟钱包如果密码忘记时一个密码登录的方式，一般是英文单词有12个，如果嫌疑人持有的设备上有见到类似与12个英文单词时注意下可能是虚拟钱包的助记词。

#### 计算机快速访问记录

快速访问中的数据(常用文件/夹)，文档中的最近打开记录，百度网盘应用程序，浏览器最近访问的历史记录等。

固定关键涉案证据时，建议记录操作，将涉案文档进行压缩操作并且进行hash校验操作，并记录在勘查笔录中。

#### 计算机中的其他数据（手机外围）

手机备份电脑上也可能存在。

 **iOS设备的iTunes备份**

    
    
    C:\Users\XXX\AppData\Roaming\Apple Computer\MobileSync\Backup\
    

**iOS设备的lockdown文件**

    
    
    C:\ProgramData\Apple\Lockdown\
    

**华为助手备份文件**

    
    
    C:\Users\Administrator\Documents\HiSuite\backup
    

**各类安卓手机备份文件**

 **安卓模拟器**

#### 注意

  1. 对所有的操作进行记录和校验。

  2. 录像和截图不要存储在涉案计算机上。

### 磁盘映像取证

Autopsy是一款功能强大且易于使用的数字取证工具，它具有用户友好的界面和强大的功能，提供在磁盘映像中进行字符串提取，恢复文件，时间轴分析，chrome，firefox等浏览历史分析，关键字搜索和邮件分析等功能，可以帮助取证人员快速而准确地分析和提取证据。

下面进行一次实验，演示基础使用。

#### 配置Autopsy

选择Nev Case，开启一个新的环境。

![image-20230518203027831](https://image.3001.net/images/20230606/1686023387_647eacdb17ae77e82fbde.png!small)

要求为新案例命名以及要放置案例的目录。

![image-20230518204256666](https://image.3001.net/images/20230606/1686023387_647eacdba518bc787f115.png!small)

填入一些信息，比如相应的编号，名称，手机号，描述等，然后点击Finish。

![image-20230518204554623](https://image.3001.net/images/20230606/1686023388_647eacdc4bed963fec136.png!small)

![image-20230518204809749](https://image.3001.net/images/20230606/1686023388_647eacdcc03a1b0111431.png!small)

![image-20230519101033981](https://image.3001.net/images/20230606/1686023389_647eacdd4c35a7630c166.png!small)

![image-20230519101142497](https://image.3001.net/images/20230606/1686023390_647eacde509bd8530654d.png!small)

等待索引完成此映像像以进行分析。

#### 关键字搜索

可以在右上角的搜索窗口输入关键词进行查询，这时候Autopsy 将开始在每个文件中搜索该关键字。在实际调查中，这个关键词是特定于调查的。

![image-20230519102305986](https://image.3001.net/images/20230606/1686023390_647eacdec87d0afd9b93c.png!small)

![image-20230519102822196](https://image.3001.net/images/20230606/1686023391_647eacdfad000b513dfbc.png!small)

#### 专门的搜索类型

点击屏幕右上角附近的“眼睛”图标，它会打开一个下拉窗口。在这里我们可以进行非常专业的类型搜索，这可能是我们调查的关键。

电话号码，IP地址，电子邮件地址，URL，信用卡号码

![image-20230519111131340](https://image.3001.net/images/20230606/1686023392_647eace0d2db5a162996f.png!small)

例如想要在这些文件中找到一些网站，也许能帮助我们确定在系统被查封之前嫌疑人在做什么。

在下拉窗口中单击url旁边的复选框。它将填充用于查找URL的正则表达式。

![image-20230519111648155](https://image.3001.net/images/20230606/1686023393_647eace14b194f5a80e24.png!small)

点击“搜索”按钮后，Autopsy将会开始在每个文件中寻找所指定的文本模式。

![image-20230519112220457](https://image.3001.net/images/20230606/1686023393_647eace1bbdb3622afb35.png!small)

除此之外，我们还可以创建自定义的正则表达式，以搜索任何我们想寻找的文本模式。这一功能可以帮助我们更有效地搜索目标，提高数字取证的效率。

#### 恢复已"删除"的文件

在数字取证研究人员的基本技能中，恢复被删除的文件或许是其中最基本的。正如你所了解的，大多数情况下，系统只是删除了文件的位置信息或将其标记为已删除，而实际上这些“已删除”的文件仍然保留在存储介质中，直到被覆盖为止。这意味着，如果嫌疑人删除了证据文件，只要我们在文件系统覆盖之前采取行动，我们仍然可以将这些文件恢复出来。

在对象资源管理器中，可以看到一个名为“已删除文件”的文件类型。它会显示所有被删除的文件。

![image-20230519113116084](https://image.3001.net/images/20230606/1686023394_647eace248bdccf19b0b2.png!small)

当点击一个已删除的文件时，可以在右下角的窗口中进行一些分析。在那里，会看到标签名为
Hex、字符串、文件元数据、结果和索引文本的选项。单击“文件元数据”选项卡，它将显示文件的元数据，包括名称、类型、大小、修改、访问和创建等信息。

![image-20230519113427241](https://image.3001.net/images/20230606/1686023395_647eace3133a7cc42e967.png!small)

要恢复已删除的文件，右键单击已删除的文件并选择“extract file”提取出该文件。

![image-20230519113537756](https://image.3001.net/images/20230606/1686023395_647eace395202a0bd6238.png!small)

![image-20230519113616765](https://image.3001.net/images/20230606/1686023396_647eace40d49cfbafca16.png!small)

嫌疑犯经常试图通过删除关键证据文件来掩盖他们的踪迹。作为一名取证研究员，我们知道在这些文件被文件系统覆盖之前它们是可以恢复的。使用像Autopsy和几乎所有其他取证套件(case,
ProDiscover, FTK, Oxygen等)这样的工具，恢复这些被删除的文件非常简单。

### 内存映像取证

内存取证是对传统基于磁盘取证的重要补充同时也是计算机取证调查中的重要手段之一，它可以帮助我们获取易失性内存中的有价值数据，如临时缓存(文字，图片，聊天记录，电子邮件)、解密密钥(如Bitlocker，TrueCrypt，PGP等全盘加密的解密密钥)等，并深入了解受损系统的状态，以及对手可能如何攻击系统。

需要注意的是，内存是易失性的，一旦电脑关闭，RAM
中的信息都可能丢失，因此必须在关闭系统之前捕获。同时，当涉及恶意软件攻击时，易失性内存有时是调查此类攻击的唯一来源，因为大多数恶意软件只是驻留在内存中的。这意味着对非易失性证据的分析根本不会为我们提供关于恶意软件存在的令人信服的线索。因此，内存取证在计算机取证调查中具有不可替代的重要性。

#### 内存镜像获取

##### Windows系统镜像获取

###### 基于用户登录状态下的内存获取方法

在Windows系统处于开机，并且用户已经登录的状态时，可以通过制作内存镜像的软件来获取内存镜像，即使不是管理员用户权限，也可以对内存中的镜像进行获取。比较常用的工具有AccessData
FTK lmager、Dumplt和Magnet RAM Capture等。

下面使用AccessData FTK lmager获取镜像。

单击“File”下拉菜单并点击“Capture Memory...”获取内存选项。

![image-20230517160853645](https://image.3001.net/images/20230606/1686023396_647eace47014477f82fb1.png!small)

创建一个名为“memory”的目录，命名为 memdump.mem 文件，包含页面文件，但没有创建 AD1 文件。

当完成了这些，点击“Capture Memory”按钮。

![image-20230517161624198](https://image.3001.net/images/20230606/1686023396_647eace4ed872bf587942.png!small)

![image-20230517161639528](https://image.3001.net/images/20230606/1686023397_647eace562853bb772cfe.png!small)

![image-20230517162908708](https://image.3001.net/images/20230606/1686023397_647eace5c9cf1a1a5f75e.png!small)

###### 基于系统休眠文件的获取方法

当Windows系统进入休眠模式，Windows系统会自动将内存中的全部数据转存至硬盘的一个休眠文件中。(Hiberfil.sys)，该文件默认生成在系统盘的根目录，当数据转存完毕后，停止对硬件供电。

当恢复到正常状态后，系统会从硬盘中将之前存入的休眠文件中的信息读入内存中。当系统进入休眠模式时很省电，但是进入休眠模式的前提是需要电脑的硬盘剩余的容量大于计算机的内存大小即可实现。而获得了休眠文件，即相当于获得了系统休眠前时刻的内存文件。

##### Linux和Mac OS系统镜像获取

在Linux和Mac OS系统中，获取内存镜像可以通过以下方式获取。

LiME(Linux Memory Extractor)工具可以获取Linux系统内存镜像；

Mac Memory Reader工具可以获取Mac OS系统内存镜像。Hibernation File工具；

也可以通过提取休眠文件来获取内存镜像，休眠文件包含了系统的内存镜像。

在Linux系统中，休眠文件通常位于“/var/lib/systemd/hibernate/”和“/var/lib/systemd/sleep/”目录下；

在Mac OS系统中，休眠文件通常位于“/private/var/vm/”目录下，通常以sleepimage开头；

还有一种方法是通过/dev/mem获取。

/dev/mem是操作系统提供的一个对物理内存的映射。“/dev/mem”是linux系统的一个虚拟字符设备，无论是标准linux系统还是嵌入式linux系统，都支持该设备。首先使用open函数打开/dev/mem设备，然后使用mmap映射到用户空间实现应用程序对内存信息的读取。

#### Volatility内存分析工具

在内存分析中，使用最广泛的工具是名为 **Volatility** 的开源工具。可以从 **www.volatilityfoundation.org**
下载Volatility。它有Window、Linux 和 Mac OS X的版本。

下面我将展示Volatility 3版本基础使用，2版本请看我之前写的文章，个人感觉可以2和3版本一起用，在一些情况下vol 2比较方便。

命令格式：volatility -f [image] [plugin]

相较于volatility 2版本使用方法是差不多的，但volatility 3版本不需要指定profile，只是插件调用方式改变，插件对应了操作系统。

`python3 vol.py -h`查看帮助，这将显示出命令选项列表和插件。

![image-20230518091758621](https://image.3001.net/images/20230606/1686023398_647eace646720c3142e98.png!small)

    
    
    常用插件：
        layerwriter：列出内存镜像platform信息
        linux.bash：从内存中恢复bash命令历史记录
        linux.check_afinfo：验证网络协议的操作功能指针
        linux.check_syscall：检查系统调用表中的挂钩
        linux.elfs：列出所有进程的所有内存映射ELF文件
        linux.lsmod：列出加载的内核模块
        linux.lsof：列出所有进程的所有内存映射
        linux.malfind：列出可能包含注入代码的进程内存范围
        linux.proc：列出所有进程的所有内存映射
        linux.pslist：列出linux内存映像中存在的进程
        linux.pstree：列出进程树
        mac.bash：从内存中恢复bash命令历史记录
        mac.check_syscall：检查系统调用表中的挂钩
        mac.check_sysctl：检查sysctl处理程序的挂钩
        mac.check_trap_table：检查trap表中的挂钩
        mac.ifconfig：列出网卡信息
        mac.lsmod：列出加载的内核模块
        mac.lsof：列出所有进程的所有内存映射
        mac.malfind：列出可能包含注入代码的进程内存范围
        mac.netstat：列出所有进程的所有网络连接
        mac.psaux：恢复程序命令行参数
        mac.pslist：列出linux内存映像中存在的进程
        mac.pstree：列出进程树
        mac.tasks：列出Mac内存映像中存在的进程
        windows.info：显示正在分析的内存样本的OS和内核详细信息
        windows.callbacks：列出内核回调和通知例程
        windows.cmdline：列出进程命令行参数
        windows.dlldump：将进程内存范围DLL转储
        windows.dlllist：列出Windows内存映像中已加载的dll模块
        windows.driverirp：在Windows内存映像中列出驱动程序的IRP
        windows.driverscan：扫描Windows内存映像中存在的驱动程序
        windows.filescan：扫描Windows内存映像中存在的文件对象
        windows.handles：列出进程打开的句柄
        windows.malfind：列出可能包含注入代码的进程内存范围
        windows.moddump：转储内核模块
        windows.modscan：扫描Windows内存映像中存在的模块
        windows.mutantscan：扫描Windows内存映像中存在的互斥锁
        windows.pslist：列出Windows内存映像中存在的进程
        windows.psscan：扫描Windows内存映像中存在的进程
        windows.pstree：列出进程树
        windows.procdump：转储处理可执行映像
        windows.registry.certificates：列出注册表中存储的证书
        windows.registry.hivelist：列出内存映像中存在的注册表配置单元
        windows.registry.hivescan：扫描Windows内存映像中存在的注册表配置单元
        windows.registry.printkey：在配置单元或特定键值下列出注册表项
        windows.registry.userassist：打印用户助手注册表项和信息
        windows.ssdt：列出系统调用表
        windows.strings：读取字符串命令的输出，并指示每个字符串属于哪个进程
        windows.svcscan：扫描Windows服务
        windows.symlinkscan：扫描Windows内存映像中存在的链接
    

##### 实操

###### 系统基本信息

`python3 vol.py -f memdump.mem windows.info`

![image-20230518101601988](https://image.3001.net/images/20230606/1686023398_647eace6b8187b4e084e9.png!small)

通过SystemTime可以看到镜像制作的时间。

###### 获取进程列表

`python3 vol.py -f memdump.mem windows.pstree.PsTree`

![image-20230518103506982](https://image.3001.net/images/20230606/1686023399_647eace765bbaa6d860b9.png!small)

使用windows.pstree.PsTree可以查看所有进程和依赖关系，通过寻找PPID大于PID的进程和查看进程依赖寻找可疑的进程。

###### 获取正在运行的DLL

`python3 vol.py -f memdump.mem windows.dlllist.DllList`

![image-20230518110805099](https://image.3001.net/images/20230606/1686023399_647eace7da9e6fdef0e40.png!small)

Volatility 解析出所有正在运行的 DLL 的列表。

###### 获取事件的时间轴

`python3 vol.py -f memdump.mem timeliner.Timeliner `

![image-20230518192350282](https://image.3001.net/images/20230606/1686023400_647eace8a954a5d414d48.png!small)

一般来说，为了证明嫌疑人是否真正实施了他们被指控的行为，我们可能需要知道该系统上已发生事件的时间表。

可以使用下面的时间轴插件从内存镜像中检索出时间线信息。

###### 寻找恶意软件

`python3 vol.py -f memdump.mem windows.malfind.Malfind`

![image-20230518195457266](https://image.3001.net/images/20230606/1686023401_647eace93afa9059a2162.png!small)

主要用处是列出可能包含注入代码的进程内存范围，更好得让我们寻找在可疑系统内存中运行的任何恶意软件。


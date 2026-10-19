## [TOC]

### 关于`volatility`的一些常用命令：

 **imageinfo**

识别操作系统：

    
    
    volatility -f example.raw imageinfo
    

**pslist/pstree/psscan**

扫描进程：

    
    
    volatility -f example.raw --profile=Win7SP1x64 pslist  #win7SP1x64为操作系统
    

**filescan**

扫描文件：

    
    
    volatility -f example.raw --profile=Win7SP1x64 filescan | grep -E 'txt|png|jpg|gif|zip|rar|7z|pdf|doc'
    
    
    
    volatility -f example.raw --profile=Win7SP1x64 filescan | grep TMP_User   #搜索指定文件夹下的文件
    

**Dumpfiles**

    
    
    volatility -f wuliao.data --profile=Win7SP1x64 dumpfiles -Q 0x000000007f142f20 -D ./ -u
    

**cmdscan**

#查看终端输入历史

 **dumpfile/memdump**

导出文件：

    
    
    volatility -f example.raw --profile=Win7SP1x64 memdump -p [PID] -D ./   # -D ./  导出到当前目录
    
    or
    
    volatility -f example.raw --profile=Win7SP1x64 dumpfiles -Q [Offset] -D ./
    

**调用插件**

    
    
    volatility [plugins] -f example.raw --profile=Win7SP1x64
    

##### 提取内存中保留的 cmd 命令使用情况

    
    
    volatility -f mem.vmem --profile=WinXPSP2x86 cmdscan
    

##### 获取到当时的网络连接情况

    
    
    volatility -f mem.vmem --profile=WinXPSP2x86 netscan
    

#分析计算机内存镜像，以下哪个远程地址与本地地址建立过 TCP 连接？ 一般不使用插件而使用本命令

##### 获取 IE 浏览器的使用情况。

    
    
    volatility -f mem.vmem --profile=WinXPSP2x86 iehistory
    

##### hivelist：查看缓存在内存的注册表

    
    
    volatility -f bb.raw --profile=Win7SP1x86 hivelist
    

##### userassist:提取出内存中记录的 当时正在运行的程序有哪些，运行过多少次，最后一次运行的时间等信息

    
    
    volatility -f bb.raw --profile=Win7SP1x86 userassist
    

##### 获取内存中的系统密码，我们可以使用 hashdump 将它提取出来

    
    
    volatility -f mem.vmem --profile=WinXPSP2x86 hashdump -y （注册表 system 的 virtual 地址 ）-s （SAM 的 virtual 地址）
    
    volatility -f mem.vmem --profile=WinXPSP2x86 hashdump -y 0xe1035b60 -s 0xe16aab60
    

##### printkey: 获取SAM表中的用户

    
    
    比如：volatility -f mem.vmem –-profile=WinXPSP2x86  printkey  -K  “SAM\Domains\Account\Users\Names” 
    发现账户四个用户，分别为：
    Administrator 
    Guest 
    HelpAssistant
    SUPPORT_388945a0
    

##### hashdump:获取内存中的系统密码

    
    
    volatility -f bb.raw --profile=Win7SP1x86 hashdump
    

##### 最大程度上将内存中的信息提取出来，那么你可以使用 timeliner 这个插件。它会从多个位置来收集系统的活动信息

    
    
    volatility -f mem.vmem --profile=Win7SP1x86 timeliner
    
    
    
    volatility -f mem.vmem --profile=Win7SP1x86 timeliner | grep Company_Files #查找指定文件夹下的文件的访问详细情况，可以导出 > 文件
    

#这个可以看到谁谁谁在什么时候做了什么 ，一般导出的数据很多，可以导入进文件中，之后搜索查找

#若无法找到此文件夹下某些文件或文件夹的访问记录，我们可以通过dump访问此文件夹的进程，然后使用strings语句进行查找关键字

#例如 strings 3484.dmp | grep 'Stephen'

##### getsids：查看SID

    
    
    volatility -f bb.raw --profile=Win7SP1x86_23418 getsids
    

#查看到的用户sid 可能分散在四处，仔细找

### 常见的插件

##### 查看当前展示的 notepad 文本

    
    
    volatility notepad -f file.raw --profile=WinXPSP2x86
    

##### 查看当前操作系统中的 password hash，例如 Windows 的 SAM 文件内容

    
    
    volatility hashdump -f file.raw --profile=WinXPSP2x86
    

##### 查看所有进程

    
    
    volatility psscan -f file.raw --profile=WinXPSP2x86
    

##### 扫描所有的文件列表

    
    
    volatility filescan -f file.raw --profile=WinXPSP2x86
    

##### 扫描 Windows 的服务

    
    
    volatility svcscan -f file.raw --profile=WinXPSP2x86
    

##### 查看网络连接

    
    
    volatility connscan -f file.raw --profile=WinXPSP2x86
    

##### 查看命令行上的操作

    
    
    volatility cmdscan -f file.raw --profile=WinXPSP2x86
    

##### 根据进程的 pid dump出指定进程到指定的文件夹dump_dir

    
    
    volatility memdump -p 120 -f file.raw --profile=WinXPSP2x86 --dump-dir=dump_dir
    

dump 出来的进程文件，可以使用 foremost 来分离里面的文件，用 binwak -e 经常会有问题，需要重新修复文件

##### 对当前的窗口界面，生成屏幕截图

    
    
    volatility screenshot -f file.raw --profile=WinXPSP2x86 --dump-dir=out
    

### 一些思路

1.计算机安装windows的时间

在Microsoft路径下寻找系统信息。

    
    
    volatility -f  memdump.mem --profile=Win7SP1x86_23418 -o 0x8bd898e8 printkey -K "WOW6432Nod\Microsoft"
    

printkey: 打印注册表项及其子项和值

-o 指定注册表的virtual地址

一般系统信息存在于

我们可以指定 -o virtual 地址去printkey 获取key

之后一步一步来即可

InstalledDate对应的键值，但是可以通过Last
updated进行大致判断。正常的系统信息会记录在如下路径：(HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindows
NTCurrentVersionInstallDate）。

2.计算机名称

在注册表SYSTEM里面存在计算机名称

具体位置：ControlSet001\Control\ComputerName\ComputerName

我们可以使用命令：

    
    
    volatility -f memdump.mem  --profile=Win7SP1x86_23418 -o 0x8bc1a1c0 printkey -K "ControlSet001\Control\ComputerName\ComputerName"
    

3.查看tcp

    
    
    volatility -f memdump.mem  --profile=Win7SP1x86_23418  timeliner | grep TCP
    

4.外接存储设备的取证 -USB

1.首先使用命令volatility -h | grep service查找与设备相关的命令。

    
    
    volatility -h | grep service
    

2.然后使用设备扫描命令查询是否有USB使用痕迹。

    
    
    volatility -f memdump.mem --profile=Win7SP1x86_23418 svscan | grep usb
    

3.在虚拟地址内存中查找key，在注册表中查询USB设备使用情况（注册表中与USB设备相关的路径为：ControlSet001\Enum\USBSTOR

路径：ControlSet001\Enum\USBSTOR

使用命令：

    
    
    volatility -f memdump.mem --profile=Win7SP1x86_23418  -o 0x8bc1a1c0 printkey -K "ControlSet001\Enum\USBSTOR"
    


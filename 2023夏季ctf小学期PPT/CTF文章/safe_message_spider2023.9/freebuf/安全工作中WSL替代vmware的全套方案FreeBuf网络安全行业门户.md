# **前言**

由于我的破thinkpad x1 carbon只有500g的磁盘，在面对所需要用到多台vmware虚拟机(Kali Linux + Ubuntu 16.04
+ Ubuntu 18.04 + Ubuntu 20.04 + Ubuntu
22.04)时，硬盘容量捉襟见肘。偶然发现windows下WSL可以虚拟化Linux系统。

通过移动硬盘去开vmware虚拟机偶尔会出现卡顿，而且万一usb接口脱出，也特别尴尬。

#  **Windows Terminal安装与配置**

Windows terminal通过MircoSoft直接搜索进行安装

![1662634954_6319cbca155f609847c1c.png!small?1662634953785](https://image.3001.net/images/20220908/1662634954_6319cbca155f609847c1c.png!small?1662634953785)

##  **Windows Terminal兼容cmder**

由于之前用了较长时间的cmder，寻找了一下Windows Terminal对Cmder的兼容方案

现在环境变量的用户环境变量中添加CMDER的相关路径

变量名: CMDER_ROOT

变量值: PATH_TO_CMDER

![1662634961_6319cbd1c8b5fbf3c0c80.png!small?1662634961568](https://image.3001.net/images/20220908/1662634961_6319cbd1c8b5fbf3c0c80.png!small?1662634961568)

变量名：ConEmuDIr

变量值:%CMDER_ROOT%\vendor\conemu-maximus5

![1662634965_6319cbd5c189edf418090.png!small?1662634965506](https://image.3001.net/images/20220908/1662634965_6319cbd5c189edf418090.png!small?1662634965506)

在powershell中执行 new-guid获取一个GUID

![1662634972_6319cbdc3cf139e4cf982.png!small?1662634972143](https://image.3001.net/images/20220908/1662634972_6319cbdc3cf139e4cf982.png!small?1662634972143)

打开Windows Terminal的设置，点击左下角的打开JSON文件

![1662634977_6319cbe1d6d919109a18e.png!small?1662634977478](https://image.3001.net/images/20220908/1662634977_6319cbe1d6d919109a18e.png!small?1662634977478)

在JSON配置文件中找到 list属性

添加(YOUR_NEW_GUID替换为之前申请的new-guid)

{

"commandline": "cmd.exe /k %CMDER_ROOT%\\\vendor\\\init.bat",

"guid": "{YOUR_NEW_GUID}",

"icon": "%CMDER_ROOT%\\\icons\\\cmder.ico",

"name": "Cmder",

"startingDirectory": "%USERPROFILE%"

},

保存配置文件后就可以通过Windows Terminal开启cmder了

![1662634984_6319cbe861a9af52dcda9.png!small?1662634984145](https://image.3001.net/images/20220908/1662634984_6319cbe861a9af52dcda9.png!small?1662634984145)

#  **WSL虚拟机的安装与配置**

其中Kali linux,Ubuntu 18.04,Ubuntu 20.04,Ubuntu 22.04都可以直接通过Mircosoft Store进行获取。

##  **Windows10 获取 WSL Ubuntu 16.04**

Ubuntu 16.04的获取方式为

管理员权限开启Powershell

启用 WSL,执行完毕后重启电脑

PS > Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

下载Ubutnu 16.04,本地保存为 Ubuntu.appx数据包

PS > Invoke-WebRequest - Uri https://aka.ms/wsl-ubuntu-1604 - OutFile
Ubuntu.appx - UseBasicParsing

导入ubuntu16

PS > Add-AppxPackage .\Ubuntu.appx

之后可以在开始菜单栏 最新添加中找到新安装的虚拟机

开启虚拟机后会需要输入 用户名 和 创建密码

# Installation successful!# Please create a default UNIX user account. The
username does not need to match your Windows username.# For more information
visit: https://aka.ms/wslusers# Enter new UNIX username:

jambolt

# Enter new UNIX password:

*********

# Retype new UNIX password:

*********

##  **WSL虚拟机的一些特性**

在linux shell上可以通知执行linux elf 和 exe

![1662634998_6319cbf634c40adafb0ad.png!small?1662634998070](https://image.3001.net/images/20220908/1662634998_6319cbf634c40adafb0ad.png!small?1662634998070)

Linux与windows贡献磁盘 通过 /mnt/盘符/******* 来访问windows的文件系统

![1662635006_6319cbfe79d18cadfa62a.png!small?1662635006523](https://image.3001.net/images/20220908/1662635006_6319cbfe79d18cadfa62a.png!small?1662635006523)

wsl虚拟机与

从使用体验来说，速度和性能较于vmware有非常大的提升

##  **WSL 版本升级**

为了更好地使用一些Linux的图形化界面，需要将虚拟机从WSL v1 升级到 WSL v2

管理员启动Powershell

PS>Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

重启计算机

管理员启动Powershell

![1662636139_6319d06bdd70397083747.png!small?1662636139201](https://image.3001.net/images/20220908/1662636139_6319d06bdd70397083747.png!small?1662636139201)

PS>dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

重启计算机

下载WSL2 KERNEL 并安装 [_https://aka.ms/wsl2kernel_](https://aka.ms/wsl2kernel)

需要注意自己计算的架构是 X64还是 AMD 64

通过windows terminal下的命令 wsl -l -v 查看当前已安装的WSL虚拟机与版本(截图时所有使用的wsl虚拟机已经升级为 wsl v2)

![1662635019_6319cc0b8f440dd852ae1.png!small?1662635019328](https://image.3001.net/images/20220908/1662635019_6319cc0b8f440dd852ae1.png!small?1662635019328)

WSL 升级的命令为 wsl --set-version NAME 2

例如(wsl --set-version Ubuntu-22.04 2)

升级需要windows 开启如下功能

![1662635029_6319cc155ac36123e7d12.png!small?1662635029232](https://image.3001.net/images/20220908/1662635029_6319cc155ac36123e7d12.png!small?1662635029232)

并且需要在BIOS中开启虚拟化支持。

我遇到了 DMA保护 与 BIOS 虚拟化冲突的情况，需要关闭windows DMA保护，开启BIOS虚拟化后，才能进行 WSL2 的升级

##  **通过 win-kex启动 kali的图形化界面**

通过wsl安装的kali为最小版本

可以通过apt来安装下列可选项

kali-linux-default

kali-linux-large

kali-linux-everything

先将kali-linux 升级为 WSL2

安装 kali-win-kex

sudo apt install -y kali-win-kex

个人喜欢通过 kex --sl -s 来启动kali图形化界面可以兼容windows的图形化

![1662635042_6319cc2245226cb43144a.png!small?1662635041997](https://image.3001.net/images/20220908/1662635042_6319cc2245226cb43144a.png!small?1662635041997)

##  **WSL kali虚拟机的端口转发**

如果遇到msf反弹shell的情况需要对wsl虚拟机进行端口转发

管理员启动windows terminal，并开一个kali的shell

netsh.exe Interface portproxy add v4tov4 listenport=4444 listenaddress=0.0.0.0
connectport=4444 connectaddress=kali_wsl_ip_address

![1662635628_6319ce6c1148c7274345f.png!small?1662635627711](https://image.3001.net/images/20220908/1662635628_6319ce6c1148c7274345f.png!small?1662635627711)

##  **配置 ubuntu gnome-terminal 启动**

windows上安装 VcXsrv Windows X Server

[
_https://sourceforge.net/projects/vcxsrv/_](https://sourceforge.net/projects/vcxsrv/)

通过桌面上的 XLanch启动

个人比较喜欢 Multiple windows,可以开启多台虚拟机的图形化应用不冲突。

![1662635056_6319cc304ccebf3a6e847.png!small?1662635056082](https://image.3001.net/images/20220908/1662635056_6319cc304ccebf3a6e847.png!small?1662635056082)

勾选 Disable access control，不然会出现报错

![1662635060_6319cc345cc8782df9b44.png!small?1662635060179](https://image.3001.net/images/20220908/1662635060_6319cc345cc8782df9b44.png!small?1662635060179)

linux安装 gnome-terminal

Sudo apt install gnome-terminal

由于我的ubuntu都安装了 oh my zsh。

我在 ~/.zshrc配置文件中添加了配置

![1662636195_6319d0a3001a3adf926dc.png!small?1662636194455](https://image.3001.net/images/20220908/1662636195_6319d0a3001a3adf926dc.png!small?1662636194455)

在windows terminal启动的ubuntu中输入 gnome-terminal

![1662635071_6319cc3fcb540a98f6786.png!small?1662635071321](https://image.3001.net/images/20220908/1662635071_6319cc3fcb540a98f6786.png!small?1662635071321)

得到了4个ubuntu版本的gnome-terminal,并且和windows自身的图形化界面没有冲突，非常好用且方便。

![1662635077_6319cc45c14ac1cfc0600.png!small?1662635077502](https://image.3001.net/images/20220908/1662635077_6319cc45c14ac1cfc0600.png!small?1662635077502)

##  **ubuntu 16 pwndbg的安装**

对于pwn环境安装的pwntools,LibcSearcher,ROPgadget,one_gadget,ropper不进行过多赘述。

Ubuntu16使用了python3.5,在安装时要选择较早的pwndbg版本进行安装

[
_https://github.com/pwndbg/pwndbg/archive/refs/tags/2019.12.09.zip_](https://github.com/pwndbg/pwndbg/archive/refs/tags/2019.12.09.zip)

![1662635084_6319cc4c8a872b8854914.png!small](https://image.3001.net/images/20220908/1662635084_6319cc4c8a872b8854914.png!small)

对于pwn的gdb.attach调试而言,使用 gnome-terminal是比较方便的。

在windows上有一个兼容的gnome-terminal是特别方便的事情

gdb.attach动态调试的效果

![1662635142_6319cc86b71c3eff2fcb3.png!small?1662635142384](https://image.3001.net/images/20220908/1662635142_6319cc86b71c3eff2fcb3.png!small?1662635142384)

 **本文作者：Jambolt@涂鸦智能安全实验室**


近源渗透中经常遇到电脑存在登录密码的情况。某些安全措施严格的目标，还会启用Bitlocker磁盘加密。本文将介绍两个工具，帮助绕过锁屏和Bitlocker。

它们安装在U盘上。近源渗透时，将U盘插入电脑，并从U盘引导。即可绕过登录密码或Bitlocker。

# Kon-Boot

![](https://image.3001.net/images/20220827/1661542058_63091eaa2c2cd83d2bff7.png!small)

Kon-Boot是最著名的密码绕过工具。其原理可谓神奇：在系统引导阶段，通过修改Windows内核，使验证用户凭证的代码失效。它不会删除密码，而是使登录时的密码验证失效，输入任意密码即可登录。

## 配置与使用

完整版本的Kon-Boot是付费软件，个人许可证价格为$50，商业许可证价格为$140。

如果不打算购买许可证，也可以使用免费版本。本文使用最后一个免费版本V2.5。该版本可以绕过除Windows 10的在线账户之外的密码。在绕过失败时，Kon-Boot可以添加账号，或安装Shift键后门。

  * 下载Kon-Boot后进入其根目录下的kon-bootUSB目录，目录结构如图：![](https://image.3001.net/images/20220827/1661542077_63091ebddfeea8f2456ed.png!small)
  * 准备一个空白U盘，接入电脑。注意：后续操作需要格式化此U盘。
  * 右键，以管理员身份运行bat。在弹出的对话框中点击确定![](https://image.3001.net/images/20220827/1661542099_63091ed328c881ed47f5e.png!small)
  * 如果显示的U盘信息无误，点击确定![](https://image.3001.net/images/20220827/1661542113_63091ee135595890d151d.png!small)

此时Kon-Boot已经成功安装

  * 在渗透测试时，将U盘插入目标电脑。重启电脑后，在开机时进入BIOS

（不同主板的方式不同。常见的有按下ESC、DEL、F2或F12键）

  * 选择从U盘启动，或设置U盘为第一启动项。如图所示，最后一个启动项是U盘，选择其启动即可。

（如果BIOS开启了Security Boot，还需将其设置为DISABLE）

![](https://image.3001.net/images/20220827/1661542128_63091ef03957e3873f683.png!small)

  * 如果Kon-Boot启动正常，将会显示如下画面：![](https://image.3001.net/images/20220827/1661542150_63091f061693a5f834fbf.png!small)

按下回车键，即可正常启动系统。

  * 在登录界面，输入任意密码即可登录
  * 如果绕过密码失败，也可按下五次Shift键，呼出命令提示符。借此执行任意命令，或删除账号密码、添加新账号。此处的命令提示符是System权限。![](https://image.3001.net/images/20220827/1661542165_63091f1549f6ade0f27ad.png!small)

## Kon-Boot的缺陷

Kon-Boot可以满足大多数渗透场景的需求，但它有着几个缺点：

  * 是付费软件，全功能版价格为140美元
  * 无法绕过Bitlocker磁盘加密
  * Kon-Boot绕过密码的成功率差强人意，经常需要重试

为弥补这些缺陷，我们介绍第二个密码绕过工具：GrabAccess。

# GrabAccess

和Kon-Boot类似，GrabAccess也是密码绕过工具。对比起Kon-Boot，GrabAccess的优点有：

  * 免费，并基于GPL协议开源
  * 可以绕过Bitlocker植入后门
  * 只要引导环境符合要求，成功率接近百分百
  * 自动化植入木马。只需要一步操作，耗时短，适合近源渗透场景

其最主要的优势是成功率高。在实战中我们发现Kon-boot绕过成功率非常之不稳定，尤其是针对Windows 10。

但在目前，GrabAccess仅支持UEFI引导的64位系统。针对Windows xp，或MBR引导的Windows 7，仍推荐Kon-Boot。

## 快速开始

GrabAccess最基础的功能是安装Shift键后门，将Windows粘滞键替换为任务管理器。在不登陆的情况下，也可以执行系统命令或读写文件。

  * 准备一个U盘。如果是FAT、FAT16或FAT32格式，则可以不删除已有的文件。否则需要格式化为上述格式。
  * 下载GrabAccess，解压，将EFI文件夹拷贝到U盘根目录。![](https://image.3001.net/images/20220827/1661542193_63091f31a38d122d475fb.png!small)

至此GrabAccess的最简安装完成。

  * 将U盘插入电脑，重启电脑。在启动时进入BIOS菜单。
  * 选择从U盘启动，或设置U盘为第一启动项。如图所示，最后一个启动项是U盘，选择其启动即可。

（如果BIOS开启了Security Boot，还需将其设置为DISABLE）

  * 如果在Windows引导阶段，出现了伪造的CHKDSK界面，说明后门已经植入成功。![](https://image.3001.net/images/20220827/1661542236_63091f5c7e033097bf8a9.png!small)
  * 在登录界面，连续按下五次Shift键，即可唤出任务管理器。![](https://image.3001.net/images/20220827/1661542250_63091f6acf5b95eb25257.png!small)
  * 点击文件-运行新任务-浏览，将右下角的“文件类型”选择为所有文件，即可查看、读写电脑上的所有文件。![](https://image.3001.net/images/20220827/1661542273_63091f81ad8d01cb3d2d0.png!small)
  * 或者运行cmd，执行任意代码。例如删除当前账号的密码、添加新账号等。

（新建任务时需要勾选“以系统管理权限创建此任务“）

![](https://image.3001.net/images/20220827/1661542287_63091f8fd6d3b5b618df6.png!small)

## 自动化植入木马

GrabAccess可以自动化植入木马。写入指定的程序，并设置自启动。操作过程与上一章节类似，但需提前将GrabAccess与木马程序打包。关键步骤如下：

  * 下载GrabAccess，解压。
  * 将要植入的木马程序命名为exe，覆盖GrabAccess_Builder目录下的同名文件。![](https://image.3001.net/images/20220827/1661542304_63091fa0543c32260567a.png!small)
  * 运行bat。![](https://image.3001.net/images/20220827/1661542323_63091fb325e6c50d8f036.png!small)
  * 将EFI文件夹拷贝到U盘根目录。其后操作与上一章相同。

在Windows启动后，木马就已经完成植入。拔出U盘，跑路即可。

（如果目标存在Bitlocker，在出现Bitlocker界面时，就可以拔U盘跑路。但在此之后目标电脑须正常登录，木马才会植入。如果在Bitlocker界面直接关机，GrabAccess会失效）

![](https://image.3001.net/images/20220827/1661542354_63091fd21ee309c3581a3.png!small)

## 项目地址

可以在GrabAccess的项目页面下载其Released版本和源代码：

https://github.com/Push3AX/GrabAccess


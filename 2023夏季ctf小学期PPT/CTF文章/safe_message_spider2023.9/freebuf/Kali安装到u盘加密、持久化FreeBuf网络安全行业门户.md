**Kali Linux系统简单介绍：**  
Kali Linux是基于Debian面向网络安全人员的Linux发行版，由BackTrack发展而来。现由Offensive
Security公司开发和维护，其内置许多网络安全工具，因此常用来做渗透测试和数字鉴证。关于Kali
Linux系统的详细信息还请自行网上搜索，这里不多阐述。

 **前期准备：**  
u盘（或移动硬盘）

kali linux 镜像文件（官网下载地址：https://www.kali.org/）

Universal-USB-Installer写盘工具（官网下载地址：https://www.pendrivelinux.com/universal-usb-installer-easy-as-1-2-3/）

MiniTool Partition Wizard分区工具（官网下载地址：https://www.partitionwizard.com/free-partition-manager.html）

注：文章末尾有软件合集

 **安装步骤：**  
 **1.制作Kali Linux 启动盘**  
首先使用USB installer写盘工具制作Kali Linux启动盘，打开USB installer软件，点击I Agree进入下一步  
![图片.png](https://image.3001.net/images/20210501/1619870717_608d43fd135557f716395.png!small)  
选择你要写入的系统（比如这里要写入Kali linux，就选择Kali linux），选择Kali Linux系统镜像，选择你要写入的U盘  
![图片.png](https://image.3001.net/images/20210501/1619870725_608d440579890478ce3ab.png!small)  
注意最后要勾选FAT32文件系统，之后点击Create进行解压写入，  
![图片.png](https://image.3001.net/images/20210501/1619870732_608d440c303dd495b85fb.png!small)  
之后会弹出确认是否写入信息，点击是，  
![图片.png](https://image.3001.net/images/20210501/1619870737_608d44119203a3ed1dd5d.png!small)  
稍等片刻就写入完成了（大概需要3~10分钟看你的U盘写入速度了~）

![图片.png](https://image.3001.net/images/20210501/1619870744_608d44184cadda68d3fce.png!small)  
![图片.png](https://image.3001.net/images/20210501/1619870750_608d441eb910d4434989e.png!small)  
之后软件会复制三个它们的介绍文档到你的U盘中 ，点击close结束

![图片.png](https://image.3001.net/images/20210501/1619870758_608d442659c26cb221815.png!small)

 **2.调整分区大小**  
首先先调整启动分区的大小  
打开 MiniTool Partition Wizard分区工具 ，点击Launch Application按钮进入分区界面，  
![图片.png](https://image.3001.net/images/20210501/1619870777_608d443916203f020af5d.png!small)  
找到你的U盘选中需要调整的分区右键，然后选择Move/Resize选项设置分区的大小  
![图片.png](https://image.3001.net/images/20210501/1619870782_608d443e9b958c3739757.png!small)  
进入到分区大小调整界面，设置启动分区的大小  
![图片.png](https://image.3001.net/images/20210501/1619870786_608d4442f38b806d83a16.png!small)

大小随意，只要大于系统镜像即可  
然后就是创建和调整持久化分区的大小  
点击剩余的灰色的区域，点击右键，选择create选项创建分区，  
![图片.png](https://image.3001.net/images/20210501/1619870793_608d4449e12e53b446ef1.png!small)  
弹出确认面板点击YES，  
![图片.png](https://image.3001.net/images/20210501/1619870799_608d444f41161d0b5159a.png!small)  
大小可以自定义，文件系统先选择Unformatted(不格式化)之后再在kali linux系统里面在设置  
![图片.png](https://image.3001.net/images/20210501/1619870803_608d445345d8eaaa17b5e.png!small)

文件系统选择Unformatted(不格式化) :)  
![图片.png](https://image.3001.net/images/20210501/1619870809_608d44597abb71ae68871.png!small)

大小自定义，我这里先给个10G^_^  
如果你的U盘容量比较大，那么剩下的容量就可以用来存储文件，比如我这里就还剩下10多个G，就把它当做储存盘用了，跟刚才的操作一样，只是文件系统选择为NTFS或者FAT32。  
全部设置完后，点击apply提交修改。弹出确认窗口，点击YES，等待修改完成。

![图片.png](https://image.3001.net/images/20210501/1619870829_608d446d622708a376708.png!small)  
也可以全部给持久化分区ㄟ( ▔, ▔ )ㄏ  
至此分区就调整完成了，接下来进行下一步，加密并持久化。  
3.加密并持久化  
将U盘插入电脑，开机按热键进入BIOS或进入快速启动项设置为U盘启动，BIOS启动热键和快速启动项的热键，请根据你的电脑型号在网上搜索你电脑的启动热键。BIOS设置方法也请自行百度。（也可以选择在虚拟机中启动）。  
进入到kali linux grub启动菜单，选择第一项以LIVE模式进到kali linux系统。

关于kali linux启动中，提示a start job is running....的解决方法：  
如果你使用的N卡，特别是双显卡的笔记本，在启动中可能就会出现 a start job is running
......这一长条提示，然后就会一直卡着......。  
这是因为kali linux 预置的N卡驱动
Nouveau的兼容性不行而导致的，因此我们需要先把这个预置驱动给禁用，最方便的方法就是在grub启动菜单中添加nouveau.modeset=0代码，在grub菜单中选择需要启动的模式，然后按tab键下方就会出现关于该模式的启动代码，在代码后方添加nouveau.modeset=0这一行代码，再次进入系统就不会提示a
start job...了，但是这种方法是一次性的，下一次进入时依然会卡住。最有效的方法是直接修改kali
linux的启动菜单的启动文件，在其他系统中打开kali
linux所在的U盘，进入isolinux文件夹找到live.cfg，用记事本打开或用其他文本工具打开，推荐使用Notepad++。可以看到各个启动模式的代码，找到append这一行，在后面添加nouveau.modeset=0这一代码，可以为你需要的启动模式添加也可为全部启动模式添加，建议为全部启动模式添加。之后启动kali
linux系统就不会在出现提示了。

接下来就是设置加密分区了，如果你嫌麻烦不想设置加密分区，可以省略这一步。打开终端，输入fdisk
-l可以看到目前你的磁盘情况，找到u盘的位置，视个人情况而定，我这里电脑已经有两块硬盘了，所以U盘为/dev/sdc，找到需要加密的分区为位置，我这里为/dev/sdc2，使用luks命令为分区加密  
![图片.png](https://image.3001.net/images/20210501/1619870852_608d4484a2f87f537d6cf.png!small)

cryptsetup --verbose --verify-passphrase luksFormat /dev/sdc2

提示确定选项，输入YES注意是大写哦，提示输入密码，输入密码，提示在次输入密码，luks加密完成  
![图片.png](https://image.3001.net/images/20210501/1619871464_608d46e82da288281186f.png!small)  
使用luksOpen命令输入密码打开加密分区并创建可挂载的逻辑分区kali，路径为dev/mapper/kali

![图片.png](https://image.3001.net/images/20210501/1619871474_608d46f2f2bc52ae9be6a.png!small)  
cryptsetup luksOpen /dev/sdc2 kali

将分区格式化为Ext4文件系统，并将卷标设置为 persistence  
![图片.png](https://image.3001.net/images/20210501/1619871488_608d47008ca42285d3ff0.png!small)

mkfs.ext4 -L persistence /dev/mapper/kali

之后就是将分区持久化，大概操作就是创建一个目录，将分区挂载到目录下，创建persistence.conf文件到目录下，并为persistence.conf写入参数

![图片.png](https://image.3001.net/images/20210501/1619871504_608d47108beda77c4dd57.png!small)  
创建一个目录，路径为/kali/usb

mkdir -p /kali/usb  
将加密分区挂载到/kali/usb目录下

mount /dev/mapper/kali /kali/usb  
写入配置文件到目录下

echo "/ union" > /kali/usb/persistence.conf  
卸载挂载

umount /dev/mapper/kali  
退出luks加密

cryptsetup luksClose /dev/mapper/kali  
以上就是加密并持久化的详细操作步骤，到此就算是制作完成了，但是不要忘了进行最后一步，测试持久化是否生效。

 **4，测试持久化是否生效**  
最后一步就是测试持久化是否生效，先重启电脑，在 grub菜单中选择持久化模式启动，有两个模式分别是， “Live USB Persistence”
是使用未加密分区（可以叫做未加密持久化模式），“Live USB Encrypted Persistence”
是使用加密分区（可以叫做加密持久化模式）。因为前面我们创建的是加密分区，所以这里启动模式选择加密持久化模式，（如果你没有加密，则选择未加密持久化模式。）启动过程中会叫你输入加密分区的密码，输入密码，进入卓面，在卓面创建一个文件夹以此来检验十分生效，然后在重新启动电脑，同样选择使用加密持久化模式启动，输入密码，进入到卓面，可以看到我们创建的文件夹还在，证明持久化成功。反之文件夹不在了，则证明持久化失败了，可以选择在系统中用分区工具，将持久化分区给删除了，重新创建分区。也可以选择把整个U盘给格式化了，重新开始

至此为U盘安装kali
linux加密并持久化就制作完成了，因为最近时间不是很充足所以文章写的比较潦草，有许多没说清楚的地方。如果你有什么看不懂的地方，可以看下面的官方参考文章，也可以私信咨询我。

参考文章：https://docs.kali.org/downloading/kali-linux-live-usb-persistence


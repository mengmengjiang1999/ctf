![](https://image.3001.net/images/20201116/1605486988_5fb1c98c888c28a56a5e1.png!small)

## SSJ

SSJ是一个功能强大的脚本，这个脚本可以通过[
_Docker_](https://www.docker.com/)来将你每天使用的Linux发行版系统（比如Ubuntu和Debian等等）打造成一个安装了成百上千渗透测试和安全取证工具的工具箱。

## 技术细节

SSJ可以在我们的Linux发行版系统上安装一个使用[ _Kali
Linux_](https://www.kali.org/)作为基础系统镜像的Docker镜像。这个镜像使用的是kali.download/kali和kali-last-snapshot分支。我们可以通过使用--privileged容器功能来在主机Linux发行版上添加对xhost的通用访问控制支持，然后在主机系统上运行BurpSuite、WireShark和Ettercap之类的GUI应用程序。该脚本将帮助我们创建一个.desktop文件作为应用程序启动器，然后帮助我们初始化Docker运行命令并启动容器。所以，我们唯一需要做的事情，就是在应用程序菜单中点击并启动SSJ，此时将会弹出一个命令行终端窗口，里面将包含我们所需的全部渗透测试和安全取证工具。在这里，我们可以启动BurpSuite代理、Wireshark包分析工具以及其他工具。这样一来，只需一个终端窗口，我们便能够在Linux发行版访问和使用Kali
Linux中成百上千的工具和包了。

跟虚拟机不同的是，虚拟机需要使用虚拟NAT或桥接的形式来使用主机操作系统的网络连接，而SSJ按原样使用主机网络堆栈（使用--net=host），这意味着SSJ容器将可以作为主机Linux发行版直接访问所有网络接口，并且还将共享相同的IP地址。

## 工具依赖

  * 网络连接；
  * 必须安装curl、wget和iputils-ping；
  * 必须安装Docker，用户账户必须在docker组中；

## 工具安装

广大研究人员可以使用下列命令安装和配置SSJ：

    
    
    curl -sL https://raw.githubusercontent.com/thirdbyte/ssj/main/install.sh | bash

安装速度具体取决于大家的网速，该命令将会从Docker Hub上下载Docker镜像，大小约为4GB。

安装完成后，别忘了重启电脑。

## 工具使用

当前版本的SSJ已在Ubuntu v20.04.1 LTS（GNOME）和Linux Mint 20 Ulyana（Cinnamon）上进行了测试。

  * 访问你Linux发行版系统中的应用程序菜单，找到SSJ。
  * 启动SSJ。
  * 此时，系统将弹出一个terminator终端窗口。
  * 我们可以通过输入对应的包名，然后直接在这个终端窗口中启动任意命令。比如说，直接运行msfconsole、burpsuite和wireshark等等。
  * 我们可以直接在容器中的/root目录下存储任意文件，然后在Linux主机系统中的$HOME/.ssj路径下找到我们存储的文件。

## 插件

  * [ _Add Tools_](https://github.com/thirdbyte/ssj-plugin-add-tools)：这里提供了一个非常方便的脚本来帮助我们向SSJ中添加更多的工具；

## 更新

由于SSJ使用的是Kali Linux库中的kali-last-snapshot分支，我们就无需去手动更新它了。因为一旦Kali
Linux发布了最新版本的快照，我们的也会自动更新。不过，如果你使用了Add Tools插件的话，我们就需要重新运行一下安装命令以及add-tools脚本了。

## 工具卸载

    
    
    curl -sL https://raw.githubusercontent.com/thirdbyte/ssj/main/uninstall.sh | bash
    
    sudo rm -rf $HOME/.ssj/

## 工具运行截图

注意：下列截图中现实的xfce4-terminal现在已经被替换成了terminator。

![](https://image.3001.net/images/20201116/1605487428_5fb1cb44ba02666ae3e5e.png!small)![](https://image.3001.net/images/20201116/1605487444_5fb1cb5473eca3717c4ae.png!small)![](https://image.3001.net/images/20201116/1605487456_5fb1cb6060f023fb0051b.png!small)![](https://image.3001.net/images/20201116/1605487471_5fb1cb6fe181351432f05.png!small)![](https://image.3001.net/images/20201116/1605487516_5fb1cb9c1e3d2d492a839.png!small)![](https://image.3001.net/images/20201116/1605487529_5fb1cba9e5b8afd7949e9.png!small)![](https://image.3001.net/images/20201116/1605487538_5fb1cbb2a7ca2ddf11201.png!small)![](https://image.3001.net/images/20201116/1605487548_5fb1cbbcb6dafb6cda7ba.png!small)![](https://image.3001.net/images/20201116/1605487572_5fb1cbd426a18b738bd5e.png!small)![](https://image.3001.net/images/20201116/1605487582_5fb1cbdec0db36923e1af.png!small)

## 项目地址

SSJ：【[ _GitHub传送门_](https://github.com/thirdbyte/ssj)】


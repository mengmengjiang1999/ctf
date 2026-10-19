***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

hi，大家好，今天和大家聊聊ANDRAX。

ANDRAX是一套专为Android定制的渗透测试框架，这个东西是用来安装在手机上面的，但是开发者莫名其妙的把他整成了桌面版....

当然，这不是重点，因为ANDRAX足够强大，甚至核电站也...（详细参考我以前写的[文章](https://www.freebuf.com/articles/ics-articles/283349.html)）

所以我今天来和大家聊聊如何在Kali安装ANDRAX。

## ANDRAX Desktop 下载

首先，从我们的官方网站下载 ANDRAX-Desktop 文件：

https://andrax.thecrackertechnology.com/download/

> 注意：
>
> 切勿从其他来源下载 ANDRAX，ANDRAX 是一个开源项目，任何人都可以创建恶意构建。
>
> 一个俄罗斯孩子曾在4pda上传播恶意软件，称这是“自定义”ANDRAX 构建。

## ANDRAX Desktop 安装

ANDRAX 现在是 100% 多平台！我们的个人计算机构建可以安装在您喜欢的任何 Linux 发行版之上！

注意：ANDRAX目前暂时不支持Windows系统。

这里以我的vmware为例子：

我将把“ANDRAX Desktop”安装到“Kali linux （Debian）”这个系统上面。具体步骤如下：

1、把下载的ANDRAX-Desktop.zip拖入到“Kali linux （Debian）”系统中，我放在：/usr/local/share

2、进入 /usr/local/share

    
    
    root@kali:~/桌面# cd /usr/local/share
    root@kali:/usr/local/share# ls
    ANDRAX-Desktop.zip ca-certificates fonts man texmf zsh

3、解压 ANDRAX-Desktop.zip

    
    
    root@kali:/usr/local/share# unzip ANDRAX-Desktop.zip 
    Archive:  ANDRAX-Desktop.zip
       creating: ANDRAX-Desktop/
      inflating: ANDRAX-Desktop/andraxdesktopv1001.tar.xz.cpt  
      inflating: ANDRAX-Desktop/install.sh  
       creating: ANDRAX-Desktop/res/
      inflating: ANDRAX-Desktop/res/andrax.desktop  
      inflating: ANDRAX-Desktop/res/andrax.ico  
      inflating: ANDRAX-Desktop/HOW-TO-INSTALL.txt  
       creating: ANDRAX-Desktop/bin/
      inflating: ANDRAX-Desktop/bin/andrax  
      inflating: ANDRAX-Desktop/bin/ccrypt  
    
    root@kali:/usr/local/share# ls
    ANDRAX-Desktop  ANDRAX-Desktop.zip  ca-certificates  fonts  man  texmf  zsh

3、进入 ANDRAX-Desktop

    
    
    root@kali:/usr/local/share# cd ANDRAX-Desktop
    
    root@kali:/usr/local/share/ANDRAX-Desktop# ls
    andraxdesktopv1001.tar.xz.cpt  bin  HOW-TO-INSTALL.txt  install.sh  res

4、安装 ANDRAX-Desktop

    
    
    root@kali:/usr/local/share/ANDRAX-Desktop# sudo bash install.sh
    Unpacking ANDRAX Desktop... This can take a while, wait!
    Extracting ANDRAX File system... this will realy take a while!
    Everything is installed, Happy Hacking!

注意：这里大概要等5~10分钟左右就才可以安装成功，请耐心等待。

## 三、ANDRAX-Desktop 使用教程

ANDRAX-Desktop安装的路径是在：/opt/ANDRAX/

ANDRAX-Desktop启动时默认用户名是：andrax；

ANDRAX-Desktop启动时名称是：ANDRAX Hackers Platform

ANDRAX-Desktop的root用户默认密码是：andrax

 **1、启动ANDRAX**

root@kali:/# /usr/bin/andrax或者直接andrax``

ANDRAX图形界面启动并使用

上面讲的启动的都是ANDRAX命令行界面，ANDRAX图形界面需要用上

> 客户端计算机一台（以我的物理机：192.168.1.2）
>
> 要求：
>
> 1）、与远程计算机网络互通。
>
> 2）、装有VNC Viewer。
>
> 由于我的物理机是Windows，VNC Viewer下载地址：
>
> https://www.realvnc.com/en/connect/download/viewer/windows/
>
> 服务器计算机一台（装有ANDRAX Desktop系统的vmware虚拟机：192.168.44.130）
>
> 要求：
>
> 1）与本地计算机网络互通。
>
> 2）装有VNC Server。
>
> 由于ANDRAX已经自带的有VNC Server，我们就不需要管了，只需要直接使用即可！

``

 **第一步：**

ANDRAX系统里执行命令

> 注意：
>
> 刚开始这里会让你设置VNC Viewer连接所需要的密码，我设置的密码是：andrax；
>
> 7代表的是序号；
    
    
    ╭─andrax@ANDRAX-Hackers-Platform ~ [8:18:58]  
    ╰─➤  vncserver                                                                                                                                                                                                1 ↵
    
    You will require a password to access your desktops。
    Password：
    verify：
    Would you Like to enter a view-only password ( y / n ) ? n
    
    New 'X' desktop is ANDRAX-Hackers-Platform:7
    
    Starting applications specified in /root/.vnc/xstartup
    Log file is /root/.vnc/ANDRAX-Hackers-Platform:7.log

https://www.freebuf.com/articles/mobile/282741.html 这个可以参考nh

 **第二步：**

客户端物理机打开“VNC
Viewer”软件，输入IP、序号/端口号、密码，就可以成功通过VNC进入ANDRAX图形界面了。例如：192.168.44.130:7 或
192.168.44.130:5907

建议ANDRAX下用vncserver的时候不要用root用户。

下面让大家看下两者的区别：少了“Hacking tools”菜单栏选项。有没有觉得这个图形界面和blackarch很像？``

好了，今天就到这里，我是铁汉FhoeniX，再见~


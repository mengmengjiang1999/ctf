![](https://image.3001.net/images/20210429/1619690028_608a822c1d2795c360720.jpg!small)

## 关于OverRide

OverRide是一款功能强大的代码研究工具，OverRide以类似“游戏”的形式提供了十个小挑战，广大研究人员可以使用OverRide来学习和了解关于反汇编、代码漏洞利用和逆向工程分析相关的知识。

 **在该项目的每一个等级文件夹中，你将会看到：**

> flag：针对下一关卡的密码；
>
> md：告诉你如何找到过关密码；
>
> c：逆向工程代码；
>
> md：ASM相关内容；

最终分数：125/100

## 工具下载

广大研究人员可以从下列地址下载OverRide：

    
    
    https://projects.intra.42.fr/uploads/document/document/2096/OverRide.iso

## 虚拟机配置

在macOS上，首先需要安装VirtualBox。然后在VirtualBox中，创建一台新的虚拟机。

 **虚拟机配置清单如下：**

> 内存大小：4MB
>
> 磁盘文件类型：VDI
>
> 物理磁盘存储：动态分配
>
> 文件大小：12GB

接下来，点击设置->网络->适配器1->绑定至：桥接适配器。

还是在设置界面，加载我们之前下载好的ISO磁盘镜像。

然后启动虚拟机，运行之后将会显示虚拟机的IP地址并提示用户进行登录。

## SSH连接

在一个单独的Shell中登录，用户名为level00，密码也是level00：

    
    
    ssh level00@{VM_IP} -p 4242

![](https://image.3001.net/images/20210429/1619690059_608a824b9cfb08d8484f6.png!small)

## Level过关

作为level00用户身份，其目标就是读取用户level01的登录密码，密码可以在/home/users/level01/.pass处找到。但是，用户level00并没有权限去读取这个文件。

在用户level00的主目录下，有一份level00源码，我们可以通过这个文件来处理用户level01的权限：

![](https://image.3001.net/images/20210429/1619690269_608a831d656b2275ecf34.png!small)

我们必须使用gdb找出level00源码中的安全漏洞，然后利用这个漏洞来运行“system("/bin/sh")”，并以用户level01的身份打开一个Shell，最终拿到读取密码的权限：

    
    
    cat /home/users/level01/.pass

接下来，以用户level01登录:

    
    
    su level01

![](https://image.3001.net/images/20210429/1619690075_608a825b48153e1f012dd.png!small)

以此类推，不断继续过关。

## 关卡概述

> 0 - 硬编码密码
>
>  
>
>
> 1 - Ret2Libc攻击
>
>  
>
>
> 2 - printf()格式字符串攻击
>
>  
>
>
> 3 - 暴力破解密码
>
>  
>
>
> 4 - gets()栈溢出 + libc攻击
>
>  
>
>
> 5 - Shellcode + printf()格式字符串攻击
>
>  
>
>
> 6 - 使用gdb发现哈希值
>
>  
>
>
> 7 - 针对未受保护的数据表执行Ret2Libc攻击
>
>  
>
>
> 8 - 通过符号链接备份源码密码
>
>  
>
>
> 9 - Off-by-one错误

## 项目地址

 **OverRide：** https://github.com/anyaschukin/OverRide

## 参考资料

https://github.com/anyashuka/Override/blob/main/subject.pdf

https://github.com/anyaschukin/RainFall

https://projects.intra.42.fr/uploads/document/document/2096/OverRide.iso

https://www.virtualbox.org/


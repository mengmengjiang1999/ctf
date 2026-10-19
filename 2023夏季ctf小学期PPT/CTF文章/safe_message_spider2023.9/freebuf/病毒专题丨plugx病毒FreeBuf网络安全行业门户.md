# 一、病毒简述

之前分析了一下，分析的较为简单，这次又详细分析了一下。  
文件名称  
00fbfaf36114d3ff9e2c43885341f1c02fade82b49d1cf451bc756d992c84b06  
文件格式  
RAR  
文件类型(Magic)  
RAR archive data, v5  
文件大小  
157.74KB  
SHA256  
00fbfaf36114d3ff9e2c43885341f1c02fade82b49d1cf451bc756d992c84b06  
SHA1  
1c251974b2e6f110d96af5b23ad036954ba15e4e  
MD5  
c1c9624b21f71e4565b941a37db3815a  
CRC32  
59832D3D  
SSDEEP  
3072:c8BHz/pBz9AycS0lEm2DchuhmE62duNkKa2W75u57cXehC9v:cgz/pnUS5chuHfu/aTI4Xeha  
TLSH  
T1A8F323A63B4FFB50C74C35A6EC2B4D09068B929D14CBB6093F14C7722F5A0667D1BB92  
Tags  
rar,contains_pe

# 二、环境准备

系统版本  
  
---  
  
Win7x86  
  
# 三、行为分析

打开火绒剑监控：

![](https://image.3001.net/images/20230707/1688718663_64a7cd477145611903432.png!small)

可以看到这里创建了文件夹，文件夹中创建了三个文件。最后有设置了注册表自启动，并退出当前进行，启动了拷贝入新目录的进程。

![](https://image.3001.net/images/20230707/1688718664_64a7cd4859230b646f6c9.png!small)

之后就是很多的网络链接。

![](https://image.3001.net/images/20230707/1688718664_64a7cd48e581707874ab1.png!small)

这里又对文件进行了创建写入移动等操作，然后一直有网络链接的操作。

# 四、静态分析

## 1、病毒本体

病毒本体拖入Ida，打开start，F5

![](https://image.3001.net/images/20230707/1688718665_64a7cd49970384316064a.png!small)

可以看到这里很纯洁，加载了wsc.dll，并调用run函数，我们继续调试wsc.dll中run函数。

## 2、wsc.dll

跟进run函数，到达后到最下面：

![](https://image.3001.net/images/20230707/1688718666_64a7cd4a927fc1cac1401.png!small)

这里主要是一个LocalAlloc，申请了一段空间，然后进行for循环解密赋值，随后进入100015D0函数。

![](https://image.3001.net/images/20230707/1688718667_64a7cd4b259b6b2ff75da.png!small)

这是函数VirtualProtect函数，修改了内存属性，随后开始调用这段Shellcode。我们动态附加病毒，跟进run函数，记录LocalAlloc函数申请空间地址，等for循环结束之后，二进制复制拷出这段内存，在010Editor中进行保存为文件，拖到Ida中，可以发现是一个dll。

## 3.shellcode分析

跟进dllmain函数，到了这里：

![](https://image.3001.net/images/20230707/1688718667_64a7cd4be658b31cf05db.png!small)

通过进程参数，进行不同的函数功能，首先分析case1：

### 3.1、case1

进入sub_100090E0：  
图1：

![](https://image.3001.net/images/20230707/1688718668_64a7cd4c83cc5918399bf.png!small)

图2：

![](https://image.3001.net/images/20230707/1688718669_64a7cd4d0a961fcbc0f22.png!small)

图3：

![](https://image.3001.net/images/20230707/1688718669_64a7cd4d901005c4d43d8.png!small)

可以看到这里是对exe，dll，dat三个文件在系统目录中的一个拷贝过程。

![](https://image.3001.net/images/20230707/1688718670_64a7cd4e2bf3aa6f6715b.png!small)

之后在这里设置了程序自启动，结合病毒行为分析，这里的createProcess函数是启动了拷贝之后的exe，case1第二个函数是ExitProcess函数，这里很简单很简单，就到这里。

### 3.2、case2

![](https://image.3001.net/images/20230707/1688718670_64a7cd4ebb6b72ecd1875.png!small)

第一个函数是创建互斥体，完事后面进行参数比较，首先看函数sub_10014580：

![](https://image.3001.net/images/20230707/1688718671_64a7cd4f48b9d3c7b7d49.png!small)

这里是设置了出册表network/version为1，返回去。  
函数sub_100090E0和case1中一样，继续看函数sub_100153A0：

![](https://image.3001.net/images/20230707/1688718671_64a7cd4fcac6dc0d63f79.png!small)

先看第一个函数：

![](https://image.3001.net/images/20230707/1688718672_64a7cd50487f538f98dd3.png!small)

看addtoken：

![](https://image.3001.net/images/20230707/1688718673_64a7cd51105faaffa9f7b.png!small)

可以看到这里是一个提权操作，接下来返回去看第二个函数：

![](https://image.3001.net/images/20230707/1688718673_64a7cd51cff4ac0b68179.png!small)

这里有四个函数，第一个是找到传入进程名，完事通过KillProcess函数杀掉。先看第一个函数：

![](https://image.3001.net/images/20230707/1688718674_64a7cd52697c596961d24.png!small)

退出来，返回上一层看第三个函数：

![](https://image.3001.net/images/20230707/1688718675_64a7cd53187ca716e3073.png!small)

![](https://image.3001.net/images/20230707/1688718675_64a7cd539b5f0d343b3d2.png!small)进入MyFileDeleandDir：

![](https://image.3001.net/images/20230707/1688718676_64a7cd54340fe7a443236.png!small)

可以看到这里就是删除文件，删除目录等操作。返回上层，看第四个函数sub_100119A0：

![](https://image.3001.net/images/20230707/1688718676_64a7cd54b135901b7660c.png!small)

删掉注册表自启动。  
返回到case2，看函数sub_100019B0：

![](https://image.3001.net/images/20230707/1688718678_64a7cd5645a4e915f46b4.png!small)

分析函数sub_100164D0：

![](https://image.3001.net/images/20230707/1688718678_64a7cd56cb0ef30a8de57.png!small)

简单的创建一个窗口。看函数sub_100165A0：

![](https://image.3001.net/images/20230707/1688718679_64a7cd57567809ab6198f.png!small)

这里是获取消息并处理。DestroyWindow是销毁窗口。最后看79行MySub_0,里面是创建了一个线程，跟进去回调：

![](https://image.3001.net/images/20230707/1688718679_64a7cd57da6bf391f4318.png!small)

这里简单看了一下，都是网络连接之类的和获取本机信息的操作。

### 3.3、case3

![](https://image.3001.net/images/20230707/1688718680_64a7cd586667bbd434eeb.png!small)

![](https://image.3001.net/images/20230707/1688718681_64a7cd5903c287235c024.png!small)

![](https://image.3001.net/images/20230707/1688718681_64a7cd598fe99adbe3b90.png!small)

这里是文件拷贝，查找窗口发送消息，打开了shell的操作。


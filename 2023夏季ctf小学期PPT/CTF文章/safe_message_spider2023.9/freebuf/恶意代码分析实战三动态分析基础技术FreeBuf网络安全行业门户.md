这节课主要是通过以下的例子，学会如何使用动态分析基础技术的一些工具。

![image](https://image.3001.net/images/20210908/1631066236_6138187cdfe39ee6524d5.png!small)

通过例子来学习使用Process Monitor(行为监控)、Process
Explorer(进程监控)、WireShark抓包、Regshot注册表比对、Rundll32运行dll动态库、net start 启动服务命令等等。

## Lab03-01 题目：

题目及实验例子下载：[点我传送](https://github.com/Vxer-Lee/MalwareAnalysis/tree/master/3.%20%E5%8A%A8%E6%80%81%E5%88%86%E6%9E%90%E5%9F%BA%E7%A1%80%E6%8A%80%E6%9C%AF/Labs)

题目1：找出这个恶意代码的导入函数与字符串列表？

题目2：这个恶意代码在主机上的感染特征是什么？

题目3：这个恶意代码是否存在一些有用的网络特征码？如果存在，他们是什么？

实验对象：Lab03-01.exe

    
    
    使用工具：
    1. Process Explorer
    2. Strings
    3. Process Monitor
    4. StudyPE
    5. WireShark
    

### 题目1解答：

导入表里面只有一个API函数，`ExitProcess`退出进程相关的api函数。

所以这个程序有可能的功能是打开后就退出。

![image-20210813130730115](https://image.3001.net/images/20210907/1631003714_6137244263c91ab7d704c.png!small)

查看字符串发现有几处可疑的地方：一个网址、三个注册表值，其中一个注册表值还是自启动的注册表键值。

说明恶意程序有可能会打开这个恶意网址，并且添加到自启动。

![image-20210813131229616](https://image.3001.net/images/20210907/1631003715_6137244319f04c95d9004.png!small)

### 题目2解答：

题目2中问了`这个恶意代码在主机上的感染特征是什么？`，那么我们只靠静态分析是看不出来的，这时候就用到了动态分析的基础技术了。

#### Process Explorer

![image-20210813132112725](https://image.3001.net/images/20210907/1631003715_61372443bea1ac8201391.png!small)

需要注意的是这里创建了一个互斥量`WinVMX32`。

恶意程序经常会创建互斥量，也为这样的话他就可以对计算机中的某个资源在同一时刻只有一个对象对其进行访问。

![image-20210813132259382](https://image.3001.net/images/20210907/1631003716_613724444014b92783500.png!small)

接着再来看看DLL，操作方法和上面的Handles一样。

值得注意的是标红色标记那里，他调用了ws2_32.dll，说明这个程序他有网络通讯的功能。

![image-20210813132645985](https://image.3001.net/images/20210907/1631003716_61372444c470774b42ae8.png!small)

#### Process Monitor

打开Process Monitor选择过滤器，过滤掉不必要的进程信息。

![image-20210813131939272](https://image.3001.net/images/20210907/1631003717_6137244556ab138d5acb4.png!small)

可以看到`Process Monitor`帮我们监控到了很多信息，但是我们不需要这么多信息，我们只关心我们需要关注的操作。

![image-20210813132924446](https://image.3001.net/images/20210907/1631003718_6137244605f9d32393659.png!small)

对其就行行为`WriteFile`和`RegSetValue`进行过滤，分别的功能是写入文件和注册表操作。

过滤后看图2，发现监控到3处敏感地方：

程序在`windows\system32`出写出了文件`vmx32to64.exe`

程序添加了自启动注册表值`CurrenVersion\Run\VideoDriver`

程序操作了随机数，注册表值`RNG\Seed`

用Process Monitor分析后可知该恶意程序会添加自启动，会写出文件到系统目录，会操作随机数。  
![image-20210813133217400](https://image.3001.net/images/20210907/1631003718_61372446a5e5994de27fc.png!small)![image-20210813141613537](https://image.3001.net/images/20210907/1631003719_613724473b851bdcb6f7f.png!small)

#### WireShark

wireshark打开后，直接监听网卡流量即可。

WireShark监控中看到有DNS协议，恶意软件解析了域名`www.practicalmalwareanalysis.com`。

监控到SSL协议，发送了256字节的随机乱码数据。

![image-20210813142249004](https://image.3001.net/images/20210907/1631003719_61372447d329bb40a90c9.png!small)

![image-20210813142541906](https://image.3001.net/images/20210907/1631003720_613724485fc1e7c104a17.png!small)

### Lab03-01 实验总结：

我们通过了使用Process Monitor和Process Explorer与WireShark等动态监控的软件对实验一进行了分析，并且得出如下结论：

    
    
    Lab03-01.exe会创建互斥量，会将自身拷贝到系统\Windows\system32\vmx32to64.exe中，恶意程序会创建启动项，恶意程序还会有网络通讯功能，访问www.practicalmalwareanalysis.com并且发送随机的256字节乱码数据。
    

## Lab03-02 题目

我们主要通过Lab03-02题目对DLL动态库进行研究，（动态分析不可运行的DLL）。  
dll说明：`.dll，动态链接库英文为DLL，是Dynamic Link Library的缩写。`

> 题目1：你怎么样让这个恶意代码自行安装？
>
> 题目2：在安装之后，你如何让这个恶意代码运行起来？
>
> 题目3：你怎么能找到这个恶意代码是在哪个进程下运行的？
>
> 题目4：你可以在Process Monitor工具中设置什么样的过滤器，才能收集这个恶意代码的信息？
>
> 题目5：这个恶意代码在主机上的感染迹象特征是什么？
>
> 题目6：这个恶意代码是否存在一些有用的网络特征码？
>
> 实验对象：Lab03-02.dll
    
    
    使用工具：
    1. Process Explorer
    2. Strings
    3. Process Monitor
    4. StudyPE
    5. WireShark
    6. Regshot
    

由于DLL不能像EXE那样单独运行，他需要由EXE来装载动态调用，下面我们就来介绍如何对DLL进行动态分析。

### 题目1：让恶意代码自行安装

#### 静态分析

这里和之前分析EXE时候有些不一样的地方，之前我们都是通过分析导入表看EXE引用了哪些api函数，而分析dll的时候会额外的多出一个`导出表`，顾名思义就是dll导出了他的函数，供应加载他的exe去调用他，所以我们这里需要关注的点就是导出表中的函数。

其中这里有5个导出函数，其中第二个和第三个导出函数猜测应该是和服务相关，那么这个dll可能会创建一个服务，而第四个是installA有可能该dll通过此dll进行安装。

![image-20210813144324734](https://image.3001.net/images/20210907/1631003720_61372448f3c028b7b85f4.png!small)

那么我们继续看导入表，看看该dll调用了哪些api函数。

其中`Reg`带头的都是注册表相关的api函数，带Service的是服务相关的api函数，那么我们就可以说此dll具有操作注册表和服务相关的功能。

![image-20210813144659756](https://image.3001.net/images/20210907/1631003721_6137244982c1ac2e9f298.png!small)

继续看，该dll还具有操作http相关的功能。

![image-20210813145047850](https://image.3001.net/images/20210907/1631003722_6137244a05d165f1dc090.png!small)

在其字符串中有出现网址，并且有出现`svchost`,这是Windows的一个宿主程序，有许多的系统dll都附着在该程序中运行，所以本次使用目的有可能也是需要通过附着到svchost上到达代码运行的效果。

![image-20210813145415001](https://image.3001.net/images/20210907/1631003722_6137244a9668751f4539c.png!small)

![image-20210813145523398](https://image.3001.net/images/20210907/1631003723_6137244bc023607e5726e.png!small)

#### 让恶意代码自行安装

在静态分析中，我们得到了导出函数中有一个`installA`函数，所以我们这里大胆猜测是用这个函数进行dll的安装。

那么在Windows系统中有这么一个程序`rundll32.exe`， 专门用来安装dll程序的。

    
    
    #命令行
    rundll32.exe Lab03-02.dll,installA
    

这里先不急着运行，因为我们运行后也看不到任何结果，而我们这里主要关注下其文件对注册表进行了哪些修改，所以我们需要用到`Regshot`工具。

![image-20210813151031718](https://image.3001.net/images/20210907/1631003724_6137244ca9124d08f4356.png!small)

恶意程序添加了一个名为`IPRIP`的服务，并且服务显示名与描述信息如第二处标红位置。

![image-20210813151122548](https://image.3001.net/images/20210907/1631003725_6137244d2062028d866cf.png!small)

### 题目2：运行恶意代码

![image-20210813151233979](https://image.3001.net/images/20210907/1631003725_6137244d836e69eacf7e1.png!small)

![image-20210813151345696](https://image.3001.net/images/20210907/1631003725_6137244de391c40bb6c8f.png!small)

然后你可以点击上面的启动来运行dll，当然也可以用如下的命令进行服务的启动。

    
    
    #命令行
    net start IPRIP
    

### 题目3：找到恶意代码附着的进程

在`Process Explorer`中点击Find菜单，并且输入需要查找的dll回车后即可得到dll附加进程的信息。

![image-20210813152245120](https://image.3001.net/images/20210907/1631003726_6137244e593d664c69231.png!small)

### 题目4：Process Monitor设置过滤dll监控

因为dll是需要exe加载运行，所以我们设置Process Name为dll名字是无效的,而我们这里的Process
Name是`svchost.exe`，但是系统中有很多的svchost.exe导致我们不好定位，这里解决的办法是得到进程的pid如上图`1108`

`我们先运行Process Monitor然后再启动服务，最后在进行如下数据的过滤。`

![image-20210813153418421](https://image.3001.net/images/20210907/1631003726_6137244ee15b7e43892b4.png!small)

![image-20210813153358434](https://image.3001.net/images/20210907/1631003727_6137244f5bf22ad218a33.png!small)

### 题目5：感染迹象特征

程序会附着在系统进程`svchost.exe`中

### 题目6：网络特征

解析域名，访问http

![image-20210813153913318](https://image.3001.net/images/20210907/1631003727_6137244fd23a91110e670.png!small)  
![image-20210813154004062](https://image.3001.net/images/20210907/1631003728_6137245043bafb7a9cddc.png!small)

### Lab03-02 实验总结：

通过实验二，我们知道了用rundll32.exe来安装dll，知道了`svchost.exe`可以让dll附着并运行服务，还知道了Process
Monitor可以用过用pid的方式来过滤我们想要的dll监控数据。

## 总结：

在动态分析基础技术中的实验，我们学习到了如下技能

> Process Monitor可以用来监控程序的行为
>
> Process Explorer可以用来查看进程的信息
>
> WireShark可以抓到应用程序的网络流量包
>
> Regshot可以对比程序运行前后的注册表值
>
> rundll32.exe 可以用来安装dll
>
> svchost.exe 即服务可以用来运行dll，或附着dll。

有兴趣的可加QQ群：1145528880 （一起学习 逆向、PWN二进制安全、Web信息安全、IoT安全、游戏逆向分析原理交流）


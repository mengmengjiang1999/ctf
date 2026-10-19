原文来自：[https://bbs.ichunqiu.com/thread-41359-1-1.html](https://bbs.ichunqiu.com/thread-41359-1-1.html?from=beef)

  

病毒分析中关闭ASLR

分析病毒的时候，尽可能用自己比较熟悉的平台，这样可以大大地节省时间，像我就喜欢用xp了，然而有时候病毒非要在更高版本的系统上运行，如win7,server2008等。然而这些平台都使用了ASLR技术，每次od载入时，其映像基址都是会变化的，而你有时候需要计算一些地址，基址老是变，烦不烦？

  
![image.png](https://image.3001.net/images/20180607/15283570078603.png!small)![image.png](https://image.3001.net/images/20180607/15283570113422.png!small)  

那么我们要怎么关闭ASLR呢？这就要从ASLR技术背景开始说了。

微软从windows vista/windows server 2008（kernel version
6.0）开始采用ASLR技术，主要目的是为了防止缓冲区溢出。

ASLR技术会使PE文件每次加载到内存的起始地址随机变化，并且进程的栈和堆的起始地址也会随机改变。

该技术需要操作系统和编译工具的双重支持（主要是操作系统的支持，编译工具主要作用是生成支持ASLR的PE格式）。

关闭ASLR

 _操作系统方面_

操作系统方面关闭ASLR支持，但是我们姿势不够，不知道在哪里关闭怎么办呢？没关系，我们可以看看别人是怎么做的。

网上随便down一个关闭ASLR工具。

使用sysinternals的工具processmonitor，监控一下别人是怎么做的。

![image.png](https://image.3001.net/images/20180607/15283570212786.png!small)监控好之后点击关闭ASLR，我们就可以看到软件对应的操作了。  

![image.png](https://image.3001.net/images/20180607/15283570334422.png!small)可以看到注册表添加了一个DWORD键值项HKLM\System\CurrentControlSet\Control\SESSION
MANAGER\MEMORY MANAGEMENT\MoveImages，其值为0。  

![image.png](https://image.3001.net/images/20180607/1528357052376.png!small)  

打开ASLR就是删除掉MoveIMages键值项

![image.png](https://image.3001.net/images/20180607/15283570588818.png!small)![image.png](https://image.3001.net/images/20180607/15283570683702.png!small)

  

好，现在我们知道了关闭ASLR只需要在添加了一个DWORD键值项HKLM\System\CurrentControlSet\Control\SESSION
MANAGER\MEMORY MANAGEMENT\MoveImages，其值为0。然后重启电脑就行了。  
  
那么，要是我们不想重启电脑呢，那可以通过编译工具入手，若不想使用ASLR功能，可以在VS编译的时候将“配置属性->链接器->高级->随机基址”的值修改为否即可。然而我们分析病毒，怎么可能有源码让我们来编译呢。  
  
  
 _pe头_

那么这个时候我们可以通过修改pe头中可选头的DllCharacteristics来达成我们的目的。  
就拿wannamine这个病毒来举例，wannnamine内的spoolsv.exe是基址是动态变化的。  
  
![image.png](https://image.3001.net/images/20180607/15283570905160.png!small)![image.png](https://image.3001.net/images/20180607/15283571028451.png!small)![image.png](https://image.3001.net/images/20180607/15283571069467.png!small)

  

现在修改pe头DllCharacteristics，将动态基址选项去掉。即将DllCharacteristics值8140改为8100。

可以看到其基址变回我们熟悉的0x400000了。  
最后给出修改pe头的python脚本![image.png](https://image.3001.net/images/20180607/15283571523458.png!small)  

i春秋推出优享会员制，开通会员可以免费畅享多类课程、实验、CTF赛题等付费内容，并可享有包括会员日专属福利、就业推荐等多种特权福利，更多活动详情可点击：[https://bbs.ichunqiu.com/thread-40795-1-1.html](https://bbs.ichunqiu.com/thread-40795-1-1.html?from=qd)了解哦~


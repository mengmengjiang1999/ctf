经过本人一些尝试，将自己的一些经验记录如下。

首先，我们知道， **GUP在hashcat中加速，需要满足两个条件 ：1.可加速的显卡（GPU）；2.安装cuda。**

我的电脑 **win10** 系统， **n卡3060**

## 一、失败的总结

起初我想在kali linux中完成hashcat的加速，但是虚拟机中的显卡是算法生成的，并不能用来加速。当我看到 **n卡可以直通虚拟机**
，抱着希望找了一圈，可我没找到适合kali
linux的显卡直通教程，且网上只有linux宿主机直通windows虚拟机，本身和我要从windows系统直通linux是相反的，于是我没有合适的方式完成这一步。而即使完成了，还要来回切换显卡，而我主要还是用win10系统，如果有能力是可以写切换显卡的程序，但目前不适合我，就告终了，希望以后可以完善这一步。

##  **二、宿主机的妥协**

于是选择了在宿主机上完成hashcat的加速，主机默认显卡是3060，所以只要安装cuda和hashcat就能正常使用GPU加速。[cuda直接下载安装，一直下一步就能安装（链接）](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=10)，hashcat稍微要注意下，[hashcat建议直接下载官网二进制文件（链接）](https://hashcat.net/hashcat/)，解压就能用，注意
**hashcat是命令行应用** ，双击打开hashcat.exe会 **闪退** ，要在 **系统终端cmd** 中使用命令行打开。

##  **三、可避免的问题**

 **（msys2安装hashcat的问题：CUDA SDK toolkit not installed or incorrectly
installed）**

如果使用github上的安装说明安装的hashcat我是有一些问题的(CUDA SDK toolkit not installed or
incorrectly installed)。

![](https://image.3001.net/images/20220423/1650683523_62636e833e7e646239845.png!small)这个问题可以看到是检测不到cuda，但是cuda我已经安装了，因为没发现cuda，系统将api默认到了opencl上，我个人不清楚问题在哪，逛了一些英文网站，尝试了一些操作，也没效果，放弃了。可同时因为下载了二进制的hashcat，于是尝试了一下，反而成功了，不知道为什么。

 **上面用msys2安装的hashcat不管是在msys2的shell中还是系统shell中都会冒出同样的问题**

 **用系统shell打开直接下载的二进制hashcat没有出现这方面问题**

![](https://image.3001.net/images/20220423/1650684238_6263714e53ffa502d0546.png!small)
api自动检测到cuda，没有报错。

##  **四、hashcat的总结感悟**

通过hashcat
-b可以知道hashcat撞击各类hash的速度，有的很快，有的并不快，不同类型的哈希，每秒哈希数差距是很大的。通过有无GPU加速的对比，hashcat经过GPU加速比未加速快60倍。

  


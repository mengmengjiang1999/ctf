**概述：**  

**病毒伪装成一个DLL文件，QQ游戏启动的同时，病毒DLL也会被加载启动。病毒加载之后，会在内存中释放出远控模块，通过建立本地端口映射的方式，意图绕过某些安软的网络拦截，从而控制目标计算机。**

病毒目录文件如下：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708850_5b890eb204d26.png!small)

整体流程如下：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708854_5b890eb69ab31.png!small)

##  **详细分析：**

###  **1、启动方式：**

首先，病毒作者将关键文件全部隐藏打包了起来，只留了了一个快捷方式，通过调用CMD的方式，打开目录下的QQ游戏大厅程序：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708861_5b890ebd72e74.png!small)

而QQ游戏大厅程序在启动的过程中，会去加载一个名为：factory.dll的文件，由于Windows本身所设定的DLL加载顺序，目录下的这个factory.dll文件将会被QQ游戏大厅所加载：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708865_5b890ec185ef3.png!small)

### **2、factory.dll**  

将原版factory.dll和这个病毒的factory.dll进行比较，发现后者多了一些额外的导出函数，仔细观察甚至还会发现，后者有两个导出函数的地址竟然相同，通常一个正常的DLL文件不会这样：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708869_5b890ec5dc681.png!small)

在factory.dll的导出函数中，被调用的是CreateFactorys函数，这个函数的主要作用是执行病毒的初始化安装操作：  

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708872_5b890ec8d4cb2.png!small)

在病毒的初始化安装操作中，会先获取加载当前DLL的模块的路径，然后检查此路径下是否存在io.dat文件（被加密的DLL文件），若不存在则直接退出，猜测是用这种方法来反自动化检测程序，防止被发现。若文件存在，则读取到内存中，然后进行解密操作，解密出来发现是另一个恶意DLL文件（远控的核心部分）：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708876_5b890eccd200b.png!small)

此处所使用的解密算法，通过对比LZMA的压缩算法库（右边是LZMA压缩库的源代码），可以看出，作者采用的其实就是LZMA压缩库：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708880_5b890ed0e793f.png!small)

解密io.dat文件到内存，并且完成校验（检查是否有正常的PE结构）后，将会被加载执行：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708885_5b890ed525fea.png!small)

程序运行后，会去获取这个新DLL的导出函数地址，并且通过判断当前加载模块的名称是否含有crossfire.exe字样，来执行不同的功能（因为病毒成功加载一次之后，会将文件名改成crossfire.exe，所以从文件名就能够判断是否是首次加载）：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708894_5b890ede623ad.png!small)

###  **3、** **解密出来的新DLL**  

这个新DLL拥有2个导出函数QtxVGA和Update，从前面的分析我们可以得知：Update函数用于首次加载执行，而QtxVGA函数用于非首次加载执行。

 **(1).Update导出函数**

在Update函数中，病毒会首先检测是否存在360的进程，若存在，则直接退出。接着，通过检查互斥体（c91fbfd3142a697886）的存在，来判断系统是否已经被感染，以确定是否是否继续执行，若未感染，则继续执行。

  
![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708899_5b890ee31930a.png!small)接着，将同目录下的文件全部复制到C:\Users\Administrator\AppData\Roaming\MenuStar，并将加载模块的重命名为crossfire.exe：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708902_5b890ee696c21.png!small)为了不让双击快捷方式的人产生怀疑，病毒还会释放打开一张准备好的图片，让人放松警惕，图片被加密保存在了temp,dat文件中，解密后调用命令行打开图片：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708905_5b890ee9a7cc0.png!small)

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708917_5b890ef5ec6f3.png!small)

图片打开之后，病毒会以无窗口的形式运行crossfire.exe，并且在在C盘下创建kwoyou.ini文件，来保存记录病毒运行的日志：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708926_5b890efeb6695.png!small)

 **(2).QtxVGA导出函数**  

函数一开始会去读取之前的日志文件，然后会创建一个线程去配置电脑上的网络代理信息，如果存在360的话，还会配置端口转发，将96端口的访问全部转发到116.28.191.115:96上去。

此处设置端口转发的目的，是和目标服务器之间建立SSH隧道连接，从而绕过防火墙的拦截(猜测。。。)。将本机的某个端口（96）转发到远端指定机器的指定端口（116.28.191.115:96）；本地端口转发是在localhost上监听一个端口，所有访问这个端口的数据都会通过SSH隧道传输到远端的对应端口。

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708931_5b890f0344ba2.png!small)

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708941_5b890f0d969cb.png!small)

接着，就进入到了远控的关键函数F_HackKernelModule_0了。

在F_HackKernelModul_0中，主要包含了两方面的内容：

1、获取计算机的IP、名称、系统版本号等信息，加密送给黑客。

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708987_5b890f3b25d21.png!small)![Clipboard
Image.png](https://image.3001.net/images/20180831/1535708993_5b890f410c16e.png!small)

2、根据黑客发来的指令，执行相应的操作，如：关闭注销系统、读取模拟键盘、鼠标的操作、屏幕监控、修改注册表、系统服务等。

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535709002_5b890f4ade34c.png!small)

具体如下：

1、对键盘、鼠标、剪切板的操作：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535709016_5b890f58594b5.png!small)

2、对硬盘文件的操作：  

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535709026_5b890f620c994.png!small)

3、对系统服务的操作：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535709030_5b890f66c0107.png!small)

4、记录按键记录，并保存到dump.log文件中：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535709037_5b890f6d39311.png!small)

5、对注册表的操作：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535709042_5b890f72dc1bd.png!small)

6、获取屏幕监控截图：  

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535709049_5b890f795e7bb.png!small)

病毒的远控地址为：116.28.191.115:947（已下线）。另外，病毒在与控制端建立连接是，并未直接连接，而是在系统本地利用netsh，创建了一个本地的端口代理：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535709055_5b890f7f7004b.png!small)

猜测创建端口代理的做法，是为了隐藏其所创建的网络连接，当用户在查看网络连接时，不会被发现该连接是由病毒自身所创建：

![Clipboard
Image.png](https://image.3001.net/images/20180831/1535709060_5b890f84df73f.png!small)

 ***本文作者：dsb2468，转载请注明来自FreeBuf.COM**


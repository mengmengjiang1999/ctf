本周斗哥给大家带来的议题是磁盘镜像文件在杂项类题目中的知识点，与前几周斗哥的《CTF |
攻击取证值内存分析》的区别是上周的议题讨论是内存的文件，而本周我们要讨论的是磁盘中的文件。

先来了解一下目前常见的取证有如下分类：

![分类.webp.jpg](https://image.3001.net/images/20190604/1559633034_5cf61c8a5b82e.jpg!small)

从上图我们知道了取证的主要分类，以PC端的取证为例展开，斗哥主要整理了PC端有关windows系列的取证相关的知识点框架（初稿），本周我们主要要分享的是NFTS交换数据流的隐写以及FTK这款工具的使用。

![使用.webp.jpg](https://image.3001.net/images/20190604/1559633055_5cf61c9f50e9c.jpg!small)  

 **0x01工具FTK使用**

在实际的磁盘文件的取证过程中我们一定不能直接在原PC上直接进行，正确的方法应该是通过相关的工具将磁盘文件备份一份下来，然后在备份文件的基础进行取证操作，那么今天斗哥为大家介绍的就是这款提取磁盘文件的工具FTK，FTK支持多种操作系统，本次主要讲的是windows下的FTK，毕竟图形化的操作工具使用界面对初学者是比较友好的。

FTK下载链接： https://pan.baidu.com/s/1de5dJYGSfhZ32OYHK-QiNw 提取码：ik3k

![3k.webp.jpg](https://image.3001.net/images/20190604/1559633097_5cf61cc9b2468.jpg!small)  

FTK主要有上面5个功能，本次我们先来学习证据的获取这部分：

 **证据的获取：**

(1) FTK运行打开，选项卡点击File，选择Create Disk Imager（创建磁盘镜像）：

![创建.webp.jpg](https://image.3001.net/images/20190604/1559633203_5cf61d33d9f95.jpg!small)  

(2) 选择磁盘镜像的类型，有如下5种分类，本次演示以逻辑磁盘为例：

![为例.webp.jpg](https://image.3001.net/images/20190604/1559633237_5cf61d553cb68.jpg!small)

  

(3) 选定J盘，点击Finish：

![finish.webp.jpg](https://image.3001.net/images/20190604/1559633281_5cf61d8151d6d.jpg!small)  

(4) 有三个复选框，根据需要进行选择，通常按照默认即可：

verify images after they are created（创建完成后进行校验）、precalculate progress
statistics（显示预估处理进度）

create directory listings of all files in the images after they are
created（创建镜像文件清单）

![清单.webp.jpg](https://image.3001.net/images/20190604/1559633306_5cf61d9ae4264.jpg!small)

  

(5) 选择生成进行的文件类型，通常选择E01格式：

![E01.webp.jpg](https://image.3001.net/images/20190604/1559633333_5cf61db5224c8.jpg!small)  

(6) 然后填写镜像文件的相关描述信息，如下所示：

![所示.webp.jpg](https://image.3001.net/images/20190604/1559633362_5cf61dd2d738f.jpg!small)

  

(7) 最后根据下图进行选填，点击finis即可完成证据的保存：

![保存.webp.jpg](https://image.3001.net/images/20190604/1559633393_5cf61df12130e.jpg!small)  

(8) 根据上述配置，最后生成文件如下：

![如下.webp.jpg](https://image.3001.net/images/20190604/1559633412_5cf61e04dc0b1.jpg!small)  

● **证据的读取**

  

除了可以用FTK对磁盘文件进行获取，FTK还支持对制作好的磁盘镜像文件进行读取，从而查看磁盘中的文件内容，FTK支持两种镜像读取的方式：

1.FTK直接加载镜像文件进行读取查看：

(1) 菜单选项卡点击File，选择Add Evidence Item。

![tem.webp.jpg](https://image.3001.net/images/20190604/1559633451_5cf61e2b45c1d.jpg!small)  

(2) 然后选择Images File。

![le.webp.jpg](https://image.3001.net/images/20190604/1559633470_5cf61e3e3877a.jpg!small)  

(3) 选择要加载的镜像文件。

![文件.webp.jpg](https://image.3001.net/images/20190604/1559633490_5cf61e5256bc6.jpg!small)  

(4) 载完成后即可在FTK软件内对镜像文件进行调查取证：

![取证.webp.jpg](https://image.3001.net/images/20190604/1559633511_5cf61e67124dc.jpg!small)  

2.第二种证据读取的方式是通过将镜像文件直接挂在到操作系统文件系统上来对进行内的文件进行操作。

(1) 菜单选项卡点击File，选择Images Mounting。

![image.webp.jpg](https://image.3001.net/images/20190604/1559633538_5cf61e82cf613.jpg!small)  

(2) 添加以及选择挂载选项后，点击mount，即可在Mapped Image List看到挂载的情况：

![挂载.webp.jpg](https://image.3001.net/images/20190604/1559633574_5cf61ea646156.jpg!small)  

(3) 直接在操作系统的文件系统上就可查看到挂载的磁盘镜像：

![镜像.webp.jpg](https://image.3001.net/images/20190604/1559633678_5cf61f0e2ed88.jpg!small)

  

 **0x02 NTFS交换数据流初了解**

 **  
**

NTFS交换数据流是一项比较早期的技术，最早是因为Windows系统与苹果的HFS系统的交互需求。

NTFS使用Master File
Table（MFT）来管理文件，因此在windows系统中每个文件都对应一个MFT记录，并且每个记录由若干个属性组成，属性主要用来描述该文件的具体信息。比如
$FILE_NAME 属性描述了该文件的文件名和创建修改访问时间，而$DATA属性包含了该文件的具体内容。

![具体.webp.jpg](https://image.3001.net/images/20190604/1559633745_5cf61f51d4570.jpg!small)

当某个文件存在多个属性时，第一个属性称为主数据流供（primary data
stream），主数据流在文件创建的同时就被创建，并且默认是没有名称，因此也被未名数据流（unnamed data
stream）。除了主数据流之外还可以创建供选数据流（alternate data stream，ADS），并且可以赋予名称（This is an
ADS），绝大部分情况下用户智慧与主数据流打交道，因此从用户角度来说，ADS即供选数据流对用户是隐藏的。用常规的dir命令和windows文件管理器都没法发现ADS。正常我们查看文件内容的时候也仅仅显示主数据流的内容。因此利用这个特性我们可以将数据隐藏在ADS中以达到隐写的目的。

  

 **0x03 牛刀小试**

在了解上面的两个知识点之后，斗哥尝试利用这个特性来出一个CTF题：

（注：由于真实的物理磁盘证据保存下来文件较大，因此斗哥这里使用U盘来制作）

在本机的磁盘管理工具中创建逻辑磁盘如下：

![创建.webp
\(1\).jpg](https://image.3001.net/images/20190604/1559633798_5cf61f86e3bd3.jpg!small)

  

 **Try one：**

在磁盘中创建system文件夹，同时创建一个system.txt文本，并且写入一些数据进行保存：

![保存.webp.jpg](https://image.3001.net/images/20190604/1559633875_5cf61fd3da86c.jpg!small)

使用命令创建ADS隐写数据：

![隐写.webp.jpg](https://image.3001.net/images/20190604/1559633966_5cf6202e04689.jpg!small)  

正常无法看到隐写数据：

![无法.webp.jpg](https://image.3001.net/images/20190604/1559633986_5cf620425c5fc.jpg!small)  

kali下使用binwalk也不能看到隐写的数据：

![数数.webp.jpg](https://image.3001.net/images/20190604/1559634007_5cf62057b04ff.jpg!small)  

使用FTK将整个磁盘文件保存下来就成为我们的题目，注意选择保存镜像文件类型E01，然后解题时我们通过用FTK读取就可以看到我们的ADS隐写数据：

![可以.webp.jpg](https://image.3001.net/images/20190604/1559634057_5cf620895c9df.jpg!small)  

备注：当然通过dir /r 参数或者powershell的命令我们可以直接在本地磁盘系统中直接看到我们隐写的flag数据：

![啦啦.webp.jpg](https://image.3001.net/images/20190604/1559634078_5cf6209e939ac.jpg!small)  

 **0x04 写在最后:**

由于篇幅有限，本次斗哥仅简单演示了FTK的部分功能使用，以及ADS的文本隐写，相信聪明的小伙伴肯定能举一反三进行其他有趣的扩展，纸上得来终觉浅，还需动动小手来实践，赶快来尝试在图种、程序、压缩包等文件上进行ADS的数据隐藏吧~~~

![tu.webp.jpg](https://image.3001.net/images/20190604/1559634108_5cf620bc0051b.jpg!small)

参考资料：https://www.freebuf.com/articles/73270.html

![qrcode_for_gh_223e082fe8a7_430.jpg](https://image.3001.net/images/20190604/1559634122_5cf620cab35d9.jpg!small)


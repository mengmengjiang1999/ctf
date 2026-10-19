## 恶意代码分析

### 1.样本种类：远控后门

首先拿到样本文件，放置到虚拟机中，虚拟机做好快照防止因运行样本导致不可逆的损失，样本截图：

![image](https://image.3001.net/images/20220710/1657413856_62ca20e086bc0a82ae9dd.png!small)

### 2.样本PE分析

使用工具EXEinfo 分析，发现该样本未加壳，为Microsoft Visual C++ ver 5.0/6.0编译，程序入口点为00002D4C。

![image](https://image.3001.net/images/20220710/1657413874_62ca20f2239a24e6ea4f9.png!small)查看文件节表发现共有6个节表。  
![image](https://image.3001.net/images/20220710/1657414631_62ca23e72d6d01774a38b.png!small)

并且.text节有可执行权限。

![image](https://image.3001.net/images/20220710/1657413994_62ca216a363ecbb8d82d4.png!small)

查看文件导入表发现引用了kernel32.dll中的一些敏感api，大致可以看出有申请内存，释放内存，创建文件，写入文件，获取api地址基址等操作。

![image](https://image.3001.net/images/20220710/1657414032_62ca2190ec16aeb46c4d6.png!small)

### 3.静态分析：

从main函数开始，先是调用了一些函数初始化环境，没有什么特别大的分析价值。  
![image](https://image.3001.net/images/20220710/1657414052_62ca21a40508d6a8666bd.png!small)

我们把目光放到sub_4010F5这个函数上发现向里面传递了两个参数aShellex和lpCmdLine，跟进去看看。

![image](https://image.3001.net/images/20220710/1657414064_62ca21b0314a2d8e4cbd7.png!small)  
里面有很多函数挨个点进去看看，先看sub_4010AF是个解密函数具体内容看不懂。

![image](https://image.3001.net/images/20220710/1657414115_62ca21e3634a9168a16a8.png!small)

再看sub_401168，第一眼看见有申请内存的操作，先是申请一段空间然后进行了拷贝，sub_401168里的其他几个函数也有申请内存，还有加载dll
的功能，推断这个函数是一个加载器。

![image](https://image.3001.net/images/20220710/1657414130_62ca21f2d39bcb37562ab.png!small)继续往下看sub_40113B发现对传入的参数a1进行操作二a1正是aShellex，打开函数看发现看不懂，应该是加解密功能。

![image](https://image.3001.net/images/20220710/1657414152_62ca220843183012e09a7.png!small)

接下来看就是有复制参数127.0.0.1给v5变量，然后sub_4010AA是一个释放空间的函数，大体功能分析完毕，进行注释如图。

![image](https://image.3001.net/images/20220710/1657414161_62ca221111a0822552b60.png!small)

分析到这里我很疑惑，这就结束了？没有看到shellcode，就是一些申请内存的一些api和调用dll的api一定有东西漏掉了，那么到底是哪个地方有缺漏，那么最有可能的地方就是那个解密的地方，因为那个地方分析的很模糊，所以用od来进行调试。

发现解密函数地址为00402317，用od转到该地址。![image](https://image.3001.net/images/20220710/1657414186_62ca222a584d7d6439b7a.png!small)

![image](https://image.3001.net/images/20220710/1657414200_62ca2238160a2f5f5e2f3.png!small)然后F2再F4，运行到该地址，然后单步步入F7。

![image](https://image.3001.net/images/20220710/1657414215_62ca22471d5dbc27cbf29.png!small)

继续F7，然后一直按F7运行完循环，发现结果最后有一个出栈pop
对应地址为0x408578，查看下该地址内容发现了MZ格式pe文件，所以这些就应该明白了，刚刚静态分析的只是一个外部加载器，真正的核心恶意代码是这个pe文件，然后用od进行导出。

![image](https://image.3001.net/images/20220710/1657414224_62ca22506f5f870fd5156.png!small)

![image](https://image.3001.net/images/20220710/1657414233_62ca225940da706886db7.png!small)

导出以后用01editor打开把mz头前面部分鼠标右键删除掉保证他是一个pe文件。

![image](https://image.3001.net/images/20220710/1657414246_62ca226635692e6efc7d9.png!small)

![image](https://image.3001.net/images/20220710/1657414263_62ca2277933fee03008c4.png!small)

删完之后用EXEinfo打开确实可以看到为pe文件，并且是一个dll文件并且还加了壳，imagebase为10000000入口点为10000000+0002647c。

![image](https://image.3001.net/images/20220710/1657414291_62ca22939c46e12837df8.png!small)

继续向下运行OD发现，发现在0040235e地方调用了dll文件中的内容，由于在此之前调用了qmemcpy拷贝DLL各个区段到新内存，以及进行了一系列LoadLibrary和GetPorcAddress操作，猜测这是样本在对DLL进行脱壳，因此这个时候尝试再次dump，代码基址和数据基址可以在内存中定位。![image](https://image.3001.net/images/20220710/1657414312_62ca22a8c99610401ad8e.png!small)

所以把内存中的东西dump出来。

![image](https://image.3001.net/images/20220710/1657414334_62ca22bece6ede60222c7.png!small)

得到了脱壳后的文件，然后用ide打开，进入dllentrypoint里先进行内存格式化然后加载本地dll创建互斥体。

![image](https://image.3001.net/images/20220710/1657414359_62ca22d798c5d8b40ac05.png!small)

下面创建了一个线程然后继续往下看。

![image](https://image.3001.net/images/20220710/1657414371_62ca22e379fbc4835b6bf.png!small)  
sub_1000B580创建了一个事件，事件里有sub_1000_00。

![image](https://image.3001.net/images/20220710/1657414381_62ca22ed3770d40198187.png!small)

分析sub_1000bi500![image-20220709154740098]。![image](https://image.3001.net/images/20220710/1657414395_62ca22fbc015ea07d1cbd.png!small)

查看sub_10009ba0。

![image](https://image.3001.net/images/20220710/1657414413_62ca230d49dad1718e758.png!small)

分析sub_100099d0。

![image](https://image.3001.net/images/20220710/1657414428_62ca231c7b553f4f61f62.png!small)

回到主程序继续往下走如果dword_10023378=1就继续往下走有创建文件复制文件操作，然后进行休眠。

![image](https://image.3001.net/images/20220710/1657414494_62ca235ef2ef23f9296c6.png!small)

反之如果dword_10023C04=1就进行文件操作和创建的文件设置注册表启动服务操作。

![image](https://image.3001.net/images/20220710/1657414466_62ca234203efc91be0fad.png!small)

## 总结

静态分析大致可以看出该样本从互联网下载程序并执行并且在本地有监听端口怀疑是后门命令交互，该样本有对注册表修改的操作应急排查需要重点排查注册表。  
动态分析没有去跟，这个样本当时脱壳卡住了好久，勉勉强强分析完，还是不够全面，其实说白了还是自己的分析水平不高。


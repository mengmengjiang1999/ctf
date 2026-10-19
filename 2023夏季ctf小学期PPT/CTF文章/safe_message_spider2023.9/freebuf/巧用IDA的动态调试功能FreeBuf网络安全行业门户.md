原创： 萌新 合天智汇

原创投稿活动：https://mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ

IDA还有动态调试功能，原谅我是萌新，之前居然都不知道。后来听老师傅介绍之后，才发现kali下还是阿D最好使（手动滑稽）。本文就来介绍下如何配置IDA的动态调试环境，以及使用动态调试功能快速定位端口通信中接收数据的代码段。

配置动态调试环境 在IDA目录下，进入dbgsrv文件夹，里面有针对不同系统的调试文件，将对应的文件拷贝到要调试的系统中并运行，默认会监听23946端口

![0Y2GlyTDMAK](http://si1.go2yd.com/get-image/0Y2GlyTDMAK)

​

使用IDA加载要调试的程序文件，然后选择RemoteLinux debugger

![0Y2Glz0Qbp2](http://si1.go2yd.com/get-image/0Y2Glz0Qbp2)

​

选择好后在Debugger中选择Processoptions，配置远程调试

![0Y2Glyf4gm8](http://si1.go2yd.com/get-image/0Y2Glyf4gm8)

​

配置内容中，Application填写要调试的文件的文件名，Inputfile填写包括文件在调试体用中的路径+文件名，Directory填写文件在调试体用中的路径，Parameters填写运行时的参数，Hostname填写要调试系统的IP地址或域名，Port为端口，Password为服务器密码（一般为空即可）

![0Y2GlyHYxge](http://si1.go2yd.com/get-image/0Y2GlyHYxge)

​

配置完成后，即可开始进行调试了。和OllyDBG一样，IDA支持直接运行程序进行调试

![0Y2GlwJOalU](http://si1.go2yd.com/get-image/0Y2GlwJOalU)

​

注：遇到如下错误提示时，需检查IDA和服务器之间是否可以通信，服务器的iptables是否放行了IDA服务器程序开启的端口通信

![0Y2GlwI6D6e](http://si1.go2yd.com/get-image/0Y2GlwI6D6e)

​

![0Y2GlxNsDXk](http://si1.go2yd.com/get-image/0Y2GlxNsDXk)

​

如果iptables中INPUT表配置为默认禁止，可以添加如下策略 iptables-A INPUT -p tcp --dport 23946 -j
ACCEPT IDA也支持直接调试正在运行的进程

![0Y2Glw7KXnE](http://si1.go2yd.com/get-image/0Y2Glw7KXnE)

​

![0Y2GlwE5n8K](http://si1.go2yd.com/get-image/0Y2GlwE5n8K)

​

注：遇到如下错误提示时，需检查IDA和服务器之间是否可以通信，服务器的iptables是否放行了IDA服务器程序开启的端口通信

![0Y2Glu9iTUO](http://si1.go2yd.com/get-image/0Y2Glu9iTUO)

​

如果iptables中INPUT表配置为默认禁止，可以添加如下策略 iptables-A INPUT -p tcp --dport 23946 -j
ACCEPT 进入调试后，可能会弹出如下图所示框

![0Y2GltvypqC](http://si1.go2yd.com/get-image/0Y2GltvypqC)

​

这里是请求加载本地对应的库文件，如果需要可以添加，不需要可以一直OK->Apply

![0Y2GltQBHkm](http://si1.go2yd.com/get-image/0Y2GltQBHkm)

​

这样就进入了调试模式

![0Y2Gltay9ZY](http://si1.go2yd.com/get-image/0Y2Gltay9ZY)

​

图形界面布局和OllyDBG很相似。

方法论。定位代码段还是不外两种方法：静态，动态。 1）静态
实现端口通信功能时有些基础函数会被调用，在定位接收数据的代码时可以对这些基础函数进行搜索，查看对应的调用代码，很多情况下都能直接定位到接收数据的代码段，有时即使无法一下就确定，也可以极大地缩小范围。
关键函数： accept:从队列中接受一个连接，该函数会在就收数据之前调用，一般该函数到接收函数之间会进行一些初始化或限制ip等工作。
recv:一般是tcp链接中接收数据的函数。 recvfrom:一般是udp链接中接收数据的函数。 recvmsg:通用接收数据的函数。
read:有些时候也会用于接收链接中的数据流。 方法概述：
使用IDA加载程序文件，在Imports表中搜索recv，查看程序是否调用了recv、recvfrom或recvmsg函数，根据要分析的端口类型（tcp/udp）选择对应的接收函数，查看_recv函数的被调用地方，如果只有一处，那么很有可能就是对应的地方，如果有多处，那么可以查看调用之前对应的代码，查看监听的端口是否为对应的端口，不过在可以进行动态调试的情况下不推荐这么做。之后通过动态调试的方式进一步定位和确认是很方便的。
2）动态定位 方法概述：
通过静态定位端口通信的关键函数，并在对应函数在plt表中的位置下断点，之后向端口发送任意数据包，程序如果中断在接收函数出，则让程序执行到retrn处(快捷键Ctrl+F7)，返回后的位置即是接收数据的代码段；如果没有中断，可能有两种情况，一是程序在对应端口接收数据时没有调用对应的函数，此时需要寻找其它函数下断点尝试，二是程序没有运行到接收数据的分支，这个原因可能是在accept之后对客户端ip地址进行了限制，此时可以在_accept处下断点，看函数是否会中断，分析中断的代码端分析什么原因导致没有进行接收。

实战 1）通过静态分析和动态调试相结合的方式定位tcp端口接收数据的代码段 使用IDA加载端口程序，在Imports页面搜索recv

![0Y2GlrhK3Lk](http://si1.go2yd.com/get-image/0Y2GlrhK3Lk)

​

因为是tcp端口，首先分析recv函数的调用情况。双击recv，查看recv的引用

![0Y2GlqF5KAy](http://si1.go2yd.com/get-image/0Y2GlqF5KAy)

​

双击进入，在got表中双击进入plt表中的_recv

![0Y2GlpcDg6C](http://si1.go2yd.com/get-image/0Y2GlpcDg6C)

​

![0Y2GlpGRsI4](http://si1.go2yd.com/get-image/0Y2GlpGRsI4)

​

查看_recv函数的调用关系

![0Y2GlqmrO9Q](http://si1.go2yd.com/get-image/0Y2GlqmrO9Q)

​

发现该程序总共有五处地方调用了_recv函数，很大的概率运行中的程序接收数据的代码段就在其中。为了进一步定位和确认，需要进行动态调试。
在_recv函数处下断点

![0Y2GlomOh9c](http://si1.go2yd.com/get-image/0Y2GlomOh9c)

​

将IDA附加到端口的进程上，F9继续运行

![0Y2Gln7D39U](http://si1.go2yd.com/get-image/0Y2Gln7D39U)

​

向对应端口发送任意数据包，观察程序是否暂停

![0Y2GlmTyofQ](http://si1.go2yd.com/get-image/0Y2GlmTyofQ)

​

![0Y2GlnZvrG4](http://si1.go2yd.com/get-image/0Y2GlnZvrG4)

​

可以看到程序暂停在_recv函数处，让程序执行到返回(快捷键Ctrl+F7)，可以看到程序调用_recv函数的代码段

![0Y2GlmSPhFw](http://si1.go2yd.com/get-image/0Y2GlmSPhFw)

​

该位置即为程序实际接收数据的代码段 2）在accept函数之后限制客户端ip的tcp端口的程序
使用IDA加载端口程序文件，在Imports页面下搜索recv

![0Y2GlkPMFZg](http://si1.go2yd.com/get-image/0Y2GlkPMFZg)

​

只有一个recv函数，查看_recv函数的调用情况

![0Y2GljRFGxU](http://si1.go2yd.com/get-image/0Y2GljRFGxU)

​

只有两个调用，在_recv函数出下断点，让IDA调试器附加到端口的进程上，并向端口发送数据包

![0Y2GliKOwXQ](http://si1.go2yd.com/get-image/0Y2GliKOwXQ)

​

![0Y2GliSg5Wy](http://si1.go2yd.com/get-image/0Y2GliSg5Wy)

​

发现程序没有中断，表示程序没有运行到_recv的分支，取消_recv的断点，在_accept函数处下断点

![0Y2Glh0h5sG](http://si1.go2yd.com/get-image/0Y2Glh0h5sG)

​

再次向端口发送任意数据，发现程序中断在了_accept处，运行到返回处

![0Y2Glg7Qeum](http://si1.go2yd.com/get-image/0Y2Glg7Qeum)

​

分析对客户端ip地址的处理逻辑

![0Y2GlfQK31M](http://si1.go2yd.com/get-image/0Y2GlfQK31M)

​

![0Y2GldRAuCu](http://si1.go2yd.com/get-image/0Y2GldRAuCu)

​

从截图中可以看出，如果CPipdConfig::IsEnableLB()返回值为假时，客户端IP地址只能为127.0.0.1。经过调试可以发现进程运行是它的返回值为假，所以远程IP的链接都会被强制中断。
3）没有调用recv函数接收数据的tcp端口程序 使用IDA加载端口程序文件，在Imports页面下搜索recv

![0Y2GlevJ92e](http://si1.go2yd.com/get-image/0Y2GlevJ92e)

​

发现没有recv相关函数，而该程序又确实监听端口，这时只能猜测程序没有使用recv函数接收数据（或封装在其它库文件中进行调用，这种情况很少），搜索另一个基础函数accept

发现存在，然后查看_accept函数相关调用

![0Y2GlchyosK](http://si1.go2yd.com/get-image/0Y2GlchyosK)

​

可以看到，只有一个调用，基本可以确定这里是和客户端建立链接的开始，正向追踪_accept的返回值

![0Y2GlaijaO8](http://si1.go2yd.com/get-image/0Y2GlaijaO8)

​

在sub_4048C5函数中作为参数使用了_accept的返回值（sub_403306函数经过确认，函数内没有接收数据相关内容），进入sub_4048C5函数

![0Y2GleYYJn6](http://si1.go2yd.com/get-image/0Y2GleYYJn6)

​

发现使用read函数读取了套接字里面的数据，所以该处为接收端口数据的代码段，后续动态调试验证就不列出了

相关实验
IDA教程系列：学习ida常用的使用方法和对程序分析的相关技巧；长按下面二维码，或点击http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182014111317165000001，，可预览学习（PC端操作最佳哟）

![0Y2GlaKdOhk](http://si1.go2yd.com/get-image/0Y2GlaKdOhk)

​

长按开始学习

![0Y2Gla9Jvn6](http://si1.go2yd.com/get-image/0Y2Gla9Jvn6)

​

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

  


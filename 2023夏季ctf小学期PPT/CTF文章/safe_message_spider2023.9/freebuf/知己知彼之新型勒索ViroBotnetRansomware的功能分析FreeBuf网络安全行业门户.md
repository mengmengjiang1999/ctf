***本文原创作者：si1ence，本文属FreeBuf原创奖励计划，未经许可禁止转载**

##  **0x0 背景**

 **最近发现一个伪装成Office
Update的勒索软件差一点手抖就双击点击运行了，上网一查发现还是个新的样本叫VIBOROT，就简单的看了一下相关介绍与功能。**

Viro僵尸网络与任何已知的勒索软件系列无关。在我们分析了一个类似locky勒索软件变种的7天后，Viro僵尸网络首次在2018年9月17日被观察到，将Viro僵尸网络下载到计算机后，它将检查是否存在注册表项（计算机GUID和产品密钥），以确定系统是否应加密。该病毒具有勒索软件和僵尸网络功能影响了较多美国互联网用户，
一旦Viro僵尸网络感染机器，它也会成为垃圾邮件僵尸网络的一部分，该僵尸网络将勒索软件分发给更多的受害者。

链接如下：<https://blog.trendmicro.com/trendlabs-security-intelligence/virobot-ransomware-with-botnet-capability-breaks-through/>

![](https://image.3001.net/images/20180928/1538126054_5badf0e6ba554.png!small)

![](https://image.3001.net/images/20180928/1538126067_5badf0f3b2295.png!small)

##  **0x1 程序主体**

伪装成Office Updater整体的功能分部大致如下，主要功能包括勒索的加密与解密、僵尸网络、获取主机信息、键盘记录、进程创建、恶意文件下载等功能。

![](https://image.3001.net/images/20180928/1538126085_5badf105bc705.png!small)

##  **0x2 勒索模块**

加密算法主要使用了AES+RSA加密算法，采用256位的密钥、128位的分组大小同时使用了CBC模式(密码分组链接Cipher-block
chaining)，之后再使用RSA算法进行非对称加密。

![](https://image.3001.net/images/20180928/1538126103_5badf117d5ce2.png!small)

调用函数RNGCryptoServiceProvider 生成随机的32位的密码

![](https://image.3001.net/images/20180928/1538126115_5badf123b678c.png!small)

读取RindaelManaged的向量和经过RSA加密后的密文长度，转化成32 位无符号的整数值。同时调用
CryptoStream、FileStream函数生成文件数据流与加密数据流，最后生成经过AES与RSA加密后的.enc的文件。

![](https://image.3001.net/images/20180928/1538126132_5badf134b2bd3.png!small)

加密完成之后同时在跟目录下面生成readme.txt文件

![](https://image.3001.net/images/20180928/1538126145_5badf141d43de.png!small)

源语言为法语，经过翻译之后如下图

![](https://image.3001.net/images/20180928/1538126173_5badf15d0e37a.png!small)

使用递归函数对目录进行循环的加密

![](https://image.3001.net/images/20180928/1538126200_5badf1784ae6e.png!small)

主要加密的文件类型如下

![](https://image.3001.net/images/20180928/1538126209_5badf18192650.png!small)

##  **0x3 命令执行**

本地的命令执行有三种实现方式依次为Cmd、Powershell、CSharp（C#）

![](https://image.3001.net/images/20180928/1538126250_5badf1aa87eca.png!small)

新建了一个Process进程设置为隐藏属性，将命令保存在stringReader里通过方法StandardInput.WriteLine进行执行

![](https://image.3001.net/images/20180928/1538126268_5badf1bcedad7.png!small)

将返回结果传回C2服务器

![](https://image.3001.net/images/20180928/1538126622_5badf31ebefdb.png!small)

##  **0x4 键盘记录**

使用windows钩子(Hook)抓取键盘消息

![](https://image.3001.net/images/20180928/1538126396_5badf23c0e0d0.png!small)

新建一个WebClient将本地抓取到的键盘记录上传到C2服务器上([https://viro.mleydier.fr](https://viro.mleydier.fr/))

![](https://image.3001.net/images/20180928/1538126559_5badf2df0adab.png!small)

##  **0x5 进程操作**

依次调用系统函数CreateProcess、VirtualAlloc、WriteVirualMemory分配虚拟内存,,然后在该块内存中写入代码可以执行代码

![](https://image.3001.net/images/20180928/1538126504_5badf2a8aa562.png!small)

依次调用系统函数NtGetContextThread、NtWriteVirtualMemory、NtSetContextThread、NtResumeThread实现进程注入。

![](https://image.3001.net/images/20180928/1538126497_5badf2a1e20a6.png!small)

##  **0x6 总结**

病毒主要通过钓鱼邮件进行传播，对于陌生邮件的附件或者来路不明的文件一定要警惕。

 ***本文原创作者：si1ence，本文属FreeBuf原创奖励计划，未经许可禁止转载**


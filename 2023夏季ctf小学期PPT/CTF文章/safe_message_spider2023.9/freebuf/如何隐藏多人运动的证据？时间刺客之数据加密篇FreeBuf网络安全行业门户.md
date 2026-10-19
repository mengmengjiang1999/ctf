**多人运动心潮澎湃，深夜开黑，饥渴难耐。**

欢迎来到时间刺客系列之 数据加密篇。

我们知道，多人运动的成功关键，不仅在于时间管理，保密工作更是重要环节，也是最容易出问题的环节。

这次的事件，真是时隔多年（陈老师恍若隔世），重新唤起我们对设备物理安全的重视。

而加密数据，正是物理安全得不到保障时的重要安全防护手段。

下面我们依次按照从小到大的密级来讨论数据的加密姿势。

##  一、小电影级：巧设系统文件

如何保护硬盘里的小姐姐？

这类数据，食之无味，弃之可惜，只是不想被人发现罢了，我们归为”小电影级“。

对于它们，我们没有必要花费加密的开销，

只需把那个容量1T的伪装名为”梅西进球集锦“的文件夹设为系统文件夹即可。

原理：系统文件默认不可见，一般人也绝不会打开这个选项，最多只把隐藏文件设为可见。

###  打开CMD

在目录下按住Shift键+鼠标右键，打开Powershell，然后键入cmd进入命令提示符。

![](https://image.3001.net/images/20200509/1589036351_5eb6c53f027ce.png!small)

![](https://image.3001.net/images/20200509/1589036365_5eb6c54d849f8.png!small)

###  设置系统文件夹

使用attrib命令设置文件夹属性为隐藏和系统：

    
    
     attrib +h +s <文件夹名>

![](https://image.3001.net/images/20200509/1589036381_5eb6c55d38376.png!small)

此时，在当前目录下右键刷新，发现”梅西进球集锦“文件夹已经消失不见。

![](https://image.3001.net/images/20200509/1589036385_5eb6c5613b234.png!small)

当需要操作这个文件夹的文件时，可以用以下命令重新设为可见：

    
    
     attrib -h -s <文件夹名>

![](https://image.3001.net/images/20200509/1589036392_5eb6c5683db0c.png!small)

或者，打开系统文件可见的选项：

![](https://image.3001.net/images/20200509/1589036396_5eb6c56c38a64.png!small)

![](https://image.3001.net/images/20200509/1589036399_5eb6c56f86df8.png!small)

注意：使用everything等全盘搜索软件，依然可以搜索到文件夹里的文件，如下图

![](https://image.3001.net/images/20200509/1589036403_5eb6c573410f9.png!small)

所以，如果想万无一失，打个包或批处理改名吧各位绅士（滑稽）。其实无所谓了，都已经这样藏了，找得到算你狠咯，应付一般场景比如借个电脑啥的，已经够用了。

##  二、私房照级：PGP

个人私房照，公司涉密数据…这些，当然要加密啦。

PGP——全球顶级的加密软件，不了解的自行谷歌。

可能有人质疑为什么用PGP，我用EFS/GPG/WINRAR/……行不行？

好了，大家说的都有道理，我再补充一点，没有绝对安全的加密方式和加密软件，PGP的历史版本也曝过致命漏洞，将来也会存在漏洞，其他软件也是一样，这是从安全的角度看。

从便利通信的角度看，PGP的公私钥体系使不同人之间共享涉密文件更方便也安全，用对方的公钥加密邮件/文件，对方用他的私钥才能解密查看。以下是我的公钥环，可见大量联系人：

![](https://image.3001.net/images/20200509/1589036408_5eb6c578335fc.png!small)

最后，国家某个经常请人喝茶的部门也用PGP，咳咳，好了，现在简单说说PGP桌面版的功能之一”虚拟磁盘“。

首先，要创建自己的密钥（公钥和私钥）：

![](https://image.3001.net/images/20200509/1589036654_5eb6c66e812e2.png!small)![](https://image.3001.net/images/20200509/1589036656_5eb6c670d419e.png!small)![](https://image.3001.net/images/20200509/1589036660_5eb6c67444207.png!small)
![](https://image.3001.net/images/20200509/1589036663_5eb6c6770bdf9.png!small)

![](https://image.3001.net/images/20200509/1589036674_5eb6c682dcc12.png!small)

密钥创建好了。

在PGP窗口点击”新建虚拟磁盘“：

![](https://image.3001.net/images/20200509/1589036599_5eb6c637cd5f5.png!small)

设置虚拟磁盘文件名及保存路径等，用户密钥记得添加的是自己的密钥，然后点击”创建“：

![](https://image.3001.net/images/20200509/1589037082_5eb6c81ad65b3.png!small)

输入自己私钥的使用口令：

![](https://image.3001.net/images/20200509/1589036721_5eb6c6b195994.png!small)

新创建的虚拟磁盘已经挂载出来了：

![](https://image.3001.net/images/20200509/1589036738_5eb6c6c22cb85.png!small)

不用的时候在任务栏的PGP图标上右键，卸载：

![](https://image.3001.net/images/20200509/1589036741_5eb6c6c59867e.png!small)

想挂载的时候，进入虚拟磁盘文件的存储路径，双击运行：

![](https://image.3001.net/images/20200509/1589036747_5eb6c6cb9cf45.png!small)

键入自己私钥的使用口令：

![](https://image.3001.net/images/20200509/1589036753_5eb6c6d16032f.png!small)

在PGP虚拟磁盘里存入涉密文件：

![](https://image.3001.net/images/20200509/1589036756_5eb6c6d4bd65d.png!small)

##  三、坐牢级：Bitlocker+PGP

顾名思义，泄露了就要坐牢的级别。可能涉及国家安全的重要信息，或是成为犯罪证据的信息。

当然，我未达到这样的密级，不知道这类层次的人用什么方法，有清楚的大佬请评论一波，谢谢。

我能想到的是双重加密，例如Bitlocker+PGP。如前言，Bitlocker也不是百分百安全，只能说相对安全，虽然有阴谋论说微软有办法解密所有用Bitlocker的硬盘，但我也没有实质证据，不然乱发言。

下面说说Windows 1909专业版系统创建虚拟驱动器+Bitlocker+PGP的数据加密方式。

打开“磁盘管理”：

![](https://image.3001.net/images/20200509/1589036762_5eb6c6da202ab.png!small)

创建VHD：

![](https://image.3001.net/images/20200509/1589036799_5eb6c6ff4c398.png!small)

![](https://image.3001.net/images/20200509/1589036803_5eb6c7032b904.png!small)

在窗口下边找到刚创建的10G空间的虚拟磁盘，右键点击“初始化磁盘”：

![](https://image.3001.net/images/20200509/1589036807_5eb6c707918d1.png!small)

![](https://image.3001.net/images/20200509/1589036813_5eb6c70d12f99.png!small)

在该磁盘上右键，点击“新建简单卷”：

![](https://image.3001.net/images/20200509/1589036860_5eb6c73c64013.png!small)![](https://image.3001.net/images/20200509/1589036865_5eb6c741ce766.png!small)![](https://image.3001.net/images/20200509/1589036869_5eb6c745f13f7.png!small)

![](https://image.3001.net/images/20200509/1589036876_5eb6c74c6bf4b.png!small)

打开”我的电脑“，虚拟磁盘已经挂载出来了：

![](https://image.3001.net/images/20200509/1589036931_5eb6c7839ad4b.png!small)

右键，使用Bitlocker加密该磁盘：

![](https://image.3001.net/images/20200509/1589036939_5eb6c78b7c0f7.png!small)

![](https://image.3001.net/images/20200509/1589036944_5eb6c790593b7.png!small)

![](https://image.3001.net/images/20200509/1589036948_5eb6c794b0620.png!small)

恢复密钥一定要独立保存好（不要保存到本机上。也可打印出来物理保存），一旦忘记解锁口令，只能用恢复密钥来解锁硬盘：

![](https://image.3001.net/images/20200509/1589036958_5eb6c79e0207c.png!small)

![](https://image.3001.net/images/20200509/1589036963_5eb6c7a329a6c.png!small)

![](https://image.3001.net/images/20200509/1589036968_5eb6c7a8deda9.png!small)

![](https://image.3001.net/images/20200509/1589036972_5eb6c7ac7b818.png!small)

加密完成：

![](https://image.3001.net/images/20200509/1589036976_5eb6c7b07ff18.png!small)

想卸载该虚拟磁盘时，在图标上右键点击“弹出”：

![](https://image.3001.net/images/20200509/1589036979_5eb6c7b3f0cae.png!small)

想加载时，在刚才设置的虚拟磁盘文件的存储目录双击运行：

![](https://image.3001.net/images/20200509/1589036983_5eb6c7b739de4.png!small)

然后键入解锁口令即可：

![](https://image.3001.net/images/20200509/1589036987_5eb6c7bb11414.png!small)

接着，在这个用Windows系统创建的虚拟磁盘里再创建一个PGP虚拟磁盘文件，步骤同前文所述。

这样，就有了双重保护。想获取这个加密盘中的数据，必须干掉Bitlocker和PGP。即便干掉了Bitlocker，还有PGP，即便物理入侵从本机获得了PGP私钥，还要破解高强度的私钥使用口令。我认为难度是很大的。

这里不讨论内存转储取证获得PGP/Bitlocker密钥的情况，这相当于在现场抓到并且来不及断电（FBI OPEN THE DOOR
！！）。也不讨论通过木马/系统漏洞/软件漏洞等已经渗透进本机的情况，这类情况下私钥已经不安全。

 ***本文作者： 阿哥有鸟无巢，转载请注明来自FreeBuf.COM**  
  
  


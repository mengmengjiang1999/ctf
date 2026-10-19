## 简介

 **本文主要是向大家演示，如何找到物联网（IOT）设备中的漏洞。查找以下命令注入的过程可以分为3个步骤，有点类似于100 point CTF
challenge：下载二进制文件，运行字符串，跟踪系统调用到原点的输入。**

### DLINK DCS-5020L

> “DCS-5020L无线N
> Day＆Night云台/倾斜云台摄像机是一款日夜型网络摄像机，可轻松连接到您现有的家庭网络，并支持在各种移动设备上进行远程观看。
> 它具有平移，倾斜和数码变焦功能，可让您使用单台相机查看更为广阔的区域，内置Wi-> Fi扩展器，轻松扩展无线覆盖范围，夜视距离达5米，声音和运动检测终极的安心无忧，H.264视频压缩为高质量的图像。“

## 提取固件

与任何物联网设备一样，我们需要做的第一件事就是（如果我们有权访问它）从固件映像中提取文件系统。而对于这种设备，第一次binwalk扫描不会显示任何东西：

![1.png](https://image.3001.net/images/20180507/15256512707714.png!small)

我们正在寻找的是某种形式的嵌入式文件系统，比如squashfs。如果找不到它，通常是因为它被使用了分层压缩。 我们需要做的就是使用-M选项，递归运行binwalk。最终，我们在2层压缩下发现了cpio文件系统。

![2.png](https://image.3001.net/images/20180507/15256512852167.png!small)

让我们来查看下负责Web服务器的httpd二进制文件。

文件名：alphapd

Md5sum: ea622a926c435e4637f4852536aafa8c

## 漏洞

就像文章开头所说的那样，首先我们在二进制文件上运行字符串，看看会发生什么：

![3.png](https://image.3001.net/images/20180507/15256513025053.png!small)

这些看起来像是传递给系统的命令。这里的'sed'命令非常有趣，看起来好像是从某个地方输入的。下一步是跟踪输入，看看我们是否可以控制它。

我们可以看到这里有两个引用我们感兴趣的字符串的函数。

![4.png](https://image.3001.net/images/20180507/15256513247467.png!small)

反过来，每个函数都在setFormDefineManagement中被引用：

![5.png](https://image.3001.net/images/20180507/15256513412089.png!small)

这些都是我们可以发送请求的POST表单。 例如，如果我们以下面的形式更改密码，我们向setSystemAdmin发出POST请求：

![6.png](https://image.3001.net/images/20180507/15256513605367.png!small)

应该注意的是，您需要拥有管理员凭据才能访问此页面，稍后再介绍。还有一点需要注意的是，setSystemUserModify表单总是返回一个404，所以我们坚持分析setSystemAdmin。

因此，从sub_42DCCC开始，代码将从非易失性RAM以及websGetVar中取值。

![7.png](https://image.3001.net/images/20180507/15256513769772.png!small)

这里的一个关键信息是对CheckSystemVar的调用，这段代码调用websGetVarCheck来处理大量的输入值，包括AdminID。

![8.png](https://image.3001.net/images/20180507/15256513942487.png!small)

然后websGetVarCheck调用checkVarString，如下所示：

![9.png](https://image.3001.net/images/20180507/15256514122383.png!small)

这显然只是一个switch/case结构。我们感兴趣的值是AdminID，可以看到它的值必须小于13个字节。

![10.png](https://image.3001.net/images/20180507/15256514306965.png!small)

所以我们知道AdminID的约束是它必须少于13个字节。完成所有这些后，通过格式字符串传递给我们的AdminID参数来调用DoSystem。

![11.png](https://image.3001.net/images/20180507/15256514483655.png!small)

很显然，攻击者可以使用一个简单的payload来躲避'sed'命令，比如‘`touch a`’。
另一个例子是AdminID=a’`telnetd`’，它允许用户登录为“a”，并将此视作新的root帐户：

![12.png](https://image.3001.net/images/20180507/15256514656591.png!small)

注意，我们使用空密码登录。

## 进一步说明

我们还发现，我们可以通过在大多数密码字段中发送长密码，来对web server
segfault。如果我们发送198个字节，服务会发生段错误，并且会导致总线错误。

不过可惜的是，我找不到让gdbserver进入设备的方法，因此也无法转储核心文件并抓取它。

以下是使用210A的DDNSPassword参数向/setSystemNetwork发出POST请求的示例。

![13.png](https://image.3001.net/images/20180507/15256514963589.png!small)

掌握凭据的攻击者可以利用该漏洞，在摄像机的Web界面上导致其拒绝服务。如果我们能找到在设备上调试二进制文件的方法，也有可能做到RCE。

## 影响

目前，这些设备中有近7000个连接到互联网：

![14.png](https://image.3001.net/images/20180507/15256515156850.png!small)

## MISC

受影响的版本 - 固件1.14.09

受影响的二进制文件 - Alphapd - ea622a926c435e4637f4852536aafa8c

补丁 -[DLink的公告](http://supportannouncement.us.dlink.com/announcement/publication.aspx?name=SAP10084)

## TIMELINE

> 2017.11.21 - 向厂商披露，收到William Brown的回复，并发送给研发部门
>
> 2017.11.29 - MITRE CVE请求，分配CVE 2017-17020，然后发送给Dlink并更新它们。 W.
> Brown询问公开披露时间，我们告诉他没有时间限制，只有在补丁发布后才会被公开披露。
>
> 2018.4.27 - Dlink的解决方案正式上线
>
> 2018.4.27 - 博客上线并更新了CVE

 ***参考来源：[fidusinfosec](https://www.fidusinfosec.com/dlink-dcs-5030l-remote-code-execution-cve-2017-17020/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  


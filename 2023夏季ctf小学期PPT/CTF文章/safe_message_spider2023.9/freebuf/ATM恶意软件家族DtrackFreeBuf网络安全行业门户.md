**2018年夏末，发现了一款针对印度银行的atm恶意软件，进一步的分析表明，该恶意软件被设计用于植入目标的自动柜员机，可以读取和存储插入机器的卡中数据，在之后又发现了180多个恶意软件样本，现称之为DTrack。**

最初发现的所有dtrack样本都是已经弃用的样本，真实的有效载荷是用不同的dropper加密的，解密了有效载荷后发现了与[DarkSeoul](https://unit42.paloaltonetworks.com/tdrop2-attacks-suggest-dark-seoul-attackers-return/)
攻击活动相似之处，该活动可以追溯到2013年，归属于Lazarus组织。样本中重用了部分旧代码来攻击印度的金融部门和研究中心。根据检测，DTrack的最后一次活动是在2019年9月初。

##  技术细节

下载器将pe文件加密并嵌入数据段且不会在正常执行中运行，解密是可执行开始于start（）和winmain（）函数之间的patch。恶意软件作者将恶意代码嵌入到一个无害的可执行二进制文件中。在某些情况下，默认是visual
studio mfc项目，但也可以是任何其他程序。

解密数据包含：

> 1、可执行文件；
>
> 2、shellcode；
>
> 3、预定义进程列表

在解密数据之后，根据预定义进程列表重新命名进程名,所有名称都来自%system32%文件夹，如下面的解密文件列表所示。

    
    
    fontview.exe
    dwwin.exe
    wextract.exe
    runonce.exe
    grpconv.exe
    msiexec.exe
    rasautou.exe
    rasphone.exe
    extrac32.exe
    mobsync.exe
    verclsid.exe
    ctfmon.exe
    charmap.exe
    write.exe
    sethc.exe
    control.exe
    presentationhost.exe
    napstat.exe
    systray.exe
    mstsc.exe
    cleanmgr.exe

##  下载器

下载器中包含各种可执行文件，其目的都是监视受害者。下面是找到的各种dtrack中可执行文件功能列表：

> 1、键盘记录，
>
> 2、浏览器历史记录，
>
> 3、收集主机IP地址、网络连接的信息，
>
> 4、列出所有正在运行的进程，
>
> 5、列出所有可用磁盘卷上的所有文件。

其中一些可执行文件将收集到的数据打包加密保存到磁盘，而另一些则直接将数据发送到C&C服务器。

除了上述可执行文件外，下载器中还包含远程访问木马。木马允许攻击者在主机上执行各种操作，例如上传/下载、执行命令等。

有关操作的完整列表，请参阅下表。

![](https://image.3001.net/images/20191001/1569928346_5d93349ad5dd2.png!small)

## dtrack和atmdtrack恶意软件相似性

atmdtrack是dtrack系列的一个变种。尽管它们有相似之处，但它们也存在一些不同点。

例如，Dtrack的有效载荷在下载器中被加密，但ATMdTrand样本根本没有加密，在解密Dtrack有效载荷之后，可以看出开发人员是同一组人，两个项目具有相同的代码风格并使用相同的方式实现的功能。其中最常见的功能是字符串操作功能：在参数字符串的开头是否存在CCSI子串，将其截断后返回子串；否则，它使用第一个字节作为XOR参数，并返回一个解密的字符串。

![](https://image.3001.net/images/20191001/1569928678_5d9335e64e6ad.png!small)

##  总结

第一次发现ATMDtrack时，我们认为只是另一个ATM恶意软件家族，但是通过代码及功能分析，发现其与过去出现过的恶意软件家族的关联。可以确定是Lazarus组织武器库中的的另一个家族。

我们能够找到的大量Dtrack样本表明，Lazarus组是恶意软件开发中最活跃的APT组之一。他们快速开发恶意软件并扩展功能。第一次看到了这个恶意软件家族的早期样本是2013年，其目标为Seoul。六年后，在印度再次发现他们攻击金融机构和研究中心，可见该组织一直在使用同种工具来进行经济攻击活动和间谍攻击活动。

##  IOCs

    
    
    8f360227e7ee415ff509c2e443370e56
    3a3bad366916aa3198fd1f76f3c29f24
    F84de0a584ae7e02fb0ffe679f96db8d

 ***参考来源：[securelist](https://securelist.com/my-name-is-dtrack/93338/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  


## 一、背景介绍

Ghostscript是一款Adobe
PostScript语言的解释器软件。可对PostScript语言进行绘图，支持PS与PDF互相转换。目前大多数Linux发行版中都默认安装，并移植到了Unix、MacOS、Windows等平台，且Ghostscript还被ImagineMagic、Python
PIL和各种PDF阅读器等程序所使用。

### 1.1漏洞描述

8月21日，Google安全研究员Tavis Ormandy披露了多个 GhostScript
的漏洞，通过在图片中构造恶意PostScript脚本，可以绕过SAFER安全沙箱，从而造成命令执行、文件读取、文件删除等漏洞，其根本原因是GhostScript解析restore命令时，会暂时关闭SAFER。

### 1.2受影响的系统版本

Ghostscript <= 9.23（全版本、全平台），目前官方暂未发布更新。

## 二、漏洞细节  

### 2.1 Ghostscript安全模式（SAFER mode）

Ghostscript包含一个可选的-dSAFER选项，设置该选项启动安全沙箱模式后，与文件相关的操作符将被禁止，具体作用有如下：

> （1）禁用deletefile和renamefile操作符，能够打开管道命令（％pipe％cmd），同时只能打开stdout和stderr进行写入
>
> （2）禁用读取stdin以外的文件
>
> （3）设置设备的LockSafetyParams参数为True，从而防止使用OutputFile参数写入文件
>
>
> （4）阻止/GenericResourceDir，/FontResourceDir，/SystemParamsPassword或/StartJobPassword被更改

下面是关于该选项的简单演示：

未加上-dSAFER参数时，成功读取了/etc/passwd文件

![image001.png](https://image.3001.net/images/20180824/1535102086_5b7fcc860ce59.png!small)

加上-dSAFER参数后，出现invalidfileaccess错误  

![WX20180824-171907@2x.png](https://image.3001.net/images/20180824/1535102394_5b7fcdba316b4.png!small)

### 2.2 漏洞验证

多个PostScript操作可以绕过-dSAFER提供的保护，允许攻击者使用任意参数执行shell命令。首先对PoC进行测试，在开启了安全沙箱的情况下（-dSAFER），成功执行任意命令：

![poc_test.png](https://image.3001.net/images/20180824/1535102451_5b7fcdf3ae60c.png!small)![poc_test2.png](https://image.3001.net/images/20180824/1535102507_5b7fce2b81b9f.png!small)

使用ImageMagick工具中的convert命令测试PoC，可以看到ImageMagick同样受到影响：  

![Imaginemagick_test.png](https://image.3001.net/images/20180824/1535102558_5b7fce5eb262e.png!small)

在源码目录下使用命令“grep -r
dSAFER”找到和该选项相关的操作，下面这段注释中说明了该选项具体功能——将LockSafetyParams设置为True。

![grep-dSAFER.png](https://image.3001.net/images/20180824/1535102608_5b7fce90d3866.png!small)

再使用grep查看和LockSafetyParams相关操作，通过注释可知，这个布尔类型变量值为True时，可以防止某些不安全的操作。同时在文件psi/zdevice2.c的第269行，该变量被设置为了False，且仅有此处修改了LockSafetyParams的值为False，因此可以猜测：PoC中某条PostScript语句解析时导致了这个改变。  

![grep-LockSafetyParams.png](https://image.3001.net/images/20180824/1535102690_5b7fcee20b7da.png!small)

### 2.3 调试分析

接下来使用GDB进行验证，首先设置好程序参数：

    
    
    set args -q -sDEVICE=ppmraw -dSAFER -sOutputFile=/dev/null

根据前面grep的输出，找到“dev_old->LockSafetyParams = false;
”语句在函数restore_page_device()中，并在此处下断，运行程序输入PoC：  

设置成像区域——legal（a4、b5、letter等也可以，不是重点）

![a4.png](https://image.3001.net/images/20180824/1535102773_5b7fcf35c620e.png!small)

接着输入{null restore} stopped {pop} if，程序中断在此处：

![restore.png](https://image.3001.net/images/20180824/1535102796_5b7fcf4cec84b.png!small)

再对dev_old->LockSafetyParams变量设置观察点，继续运行程序，和预想的一样，LockSafetyParams的值在这里被改变了。

![LockSafetyParams_change.png](https://image.3001.net/images/20180824/1535102832_5b7fcf70ab4f7.png!small)

查看栈回溯，发现当前函数在一系列带有“interpret”的函数中被调用，从名称推断这些函数用于解释PostScript语句。  

![bt.png](https://image.3001.net/images/20180824/1535102868_5b7fcf94a2d21.png!small)

这里我们在#2处下断，观察到了解释器处理stopped、null、restore等关键字的过程，至此绕过SAFER沙箱过程就逐渐清晰了。

![stopped.png](https://image.3001.net/images/20180824/1535102928_5b7fcfd0d7ab5.png!small)

![null.png](https://image.3001.net/images/20180824/1535102953_5b7fcfe9273b2.png!small)

![op_restore.png](https://image.3001.net/images/20180824/1535103001_5b7fd01996188.png!small)

### 2.4 漏洞成因  

现在让我们来看看{null restore} stopped {pop} if这条语句是如何绕过SAFER安全沙箱的。  

PostScript是一种“逆波兰式”（Reverse Polish
Notation，也称为后缀表达式）的语言。简单来说就是操作数在前，操作符在后。PoC中这条语句是一条典型的PostScript异常处理语句，stopped操作符用于PostScript的异常处理，也就是说stopped执行前面{}中给出的过程，如果解释器在执行该过程期间出现错误，它将终止该过程并执行stopped操作符之后{}中的过程。

null restore会引起类型检查错误（/typecheck
error），同时restore的执行将LockSafetyParams设置为False，stopped捕获到异常，弹出栈顶元素null，GS继续运行，但此时LockSafetyParams的值还没恢复为True。

![poc.png](https://image.3001.net/images/20180824/1535103061_5b7fd05552e72.png!small)

值得一提的是，GhostScript的官方文档中也提到了restore操作符存在导致绕过SAFER沙箱的风险。  

![doc1.png](https://image.3001.net/images/20180824/1535103081_5b7fd06996ff7.png!small)

## 三、漏洞利用

OutputFile参数用于设置输出文件名，另外在Linux/Unix上，可以通过设备%pipe%将输出发送到管道（Windows中也可以，需要使用两个%）。例如，要将输出通过管道传输到lpr可以使用：/OutputFile
(%pipe%lpr）  

查阅官方文档可知，%pipe%功能由popen函数支持，在调试中也能确认这一点：

![doc2.png](https://image.3001.net/images/20180824/1535103133_5b7fd09d39f5a.png!small)

![pipe.png](https://image.3001.net/images/20180824/1535103145_5b7fd0a94b2db.png!small)

popen()函数通过创建管道的方式，调用fork()启动一个子进程，并将传入popen()的命令送到/bin/sh以-c参数执行。因此可以通过在此处注入命令实现漏洞利用，如下图中演示的那样，另外通过将PostScript编码到图像中，也可以在使用ImageMagick的Web服务器上执行任意指令。  

![exp.png](https://image.3001.net/images/20180824/1535103180_5b7fd0cc3b0df.png!small)

![end.png](https://image.3001.net/images/20180824/1535103209_5b7fd0e9aabd2.png!small)

## 四、修复建议  

截至笔者分析该漏洞时，官方还没修复该漏洞。Artifex
Software，ImageMagick，Redhat，Ubuntu等厂商已声明受到此漏洞影响，其他平台暂时未对此漏洞进行说明，目前临时解决方案如下：  

1.卸载GhostScript；

2.可在/etc/ImageMagick/policy.xml文件中添加如下代码来禁用PostScript、EPS、PDF以及XPS解码器：

    
    
    <policy domain =“coder”rights =“none”pattern =“PS”/> 
    <policy domain =“coder”rights =“none”pattern =“EPS”/> 
    <policy domain =“coder”rights =“none”pattern =“PDF”/> 
    <policy domain =“coder”rights =“none”pattern =“XPS”/>

另外，北京天融信阿尔法实验室常年招人，实验室专注漏洞相关技术研究，二进制和WEB方向岗位均可，诚挚欢迎各位有志从事逆向分析、样本检测、漏洞挖掘、渗透测试以及移动端安全研究相关工作的小伙伴。有兴趣的请投递简历到：[http://blog.topsec.com.cn/人才招聘/](http://blog.topsec.com.cn/%E4%BA%BA%E6%89%8D%E6%8B%9B%E8%81%98/)  

参考资料：  

[1][More Ghostscript Issues: Should we disable PS coders in policy.xml by
default?](http://seclists.org/oss-sec/2018/q3/142)

[2][PostScript Language Reference(third
edition)](https://www.adobe.com/content/dam/acom/en/devnet/actionscript/articles/PLRM.pdf)

[3][PostScript语言安全研究(ImageMagick新漏洞分析)](https://paper.seebug.org/68/)

[4][ImageMagick
漏洞利用方式及分析](http://blog.topsec.com.cn/ad_lab/imagemagick-%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E6%96%B9%E5%BC%8F%E5%8F%8A%E5%88%86%E6%9E%90/)

[5][Ghostscript官方文档](https://www.ghostscript.com/doc/9.23/Language.htm)

[6][A GHOST FROM POSTSCRIPT](https://ruxcon.org.au/assets/2017/slides/hong-ps-and-gs-ruxcon2017.pdf)


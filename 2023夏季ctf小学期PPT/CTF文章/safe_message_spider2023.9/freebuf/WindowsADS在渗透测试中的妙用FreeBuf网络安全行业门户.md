***本文作者：3unshine，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  

## 前言

 **NTFS交换数据流（Alternate
DataStreams，简称ADS）是NTFS磁盘格式的一个特性，在NTFS文件系统下，每个文件都可以存在多个数据流。通俗的理解，就是其它文件可以“寄宿”在某个文件身上。利用ADS数据流，我们可以做很多有趣的事情，同时对于企业安全来说这类问题也隐藏着巨大的风险。本文主要讨论利用方式以及如何防御这类攻击。**

## 利用方式

### 文件隐藏

在NTFS分区创建ADS数据流文件有 **两种形式** ：一是指定宿主文件；二是创建单独的ADS文件。常用的创建命令有两个： **echo** 和
**type** ，echo用于输入常规字符，type则用于将文件附加到目标文件，此类用法通常为CTF出题时候使用。

 **指定宿主文件**

这类情况可以使用命令

    
    
    echo 9527 > 1.txt:flag.txt 

创建目标文件：

![](https://image.3001.net/images/20190214/1550113801_5c64dc09bbdbf.png!small)

正常情况文件无法查看到，可以使用命令：

    
    
     dir /r

文件内容可以使用命令notepad 1.txt:flag.txt 进行查看和编辑 查看到文件名：

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550113974_5c64dcb64c8a6.png!small)文件内容可以使用命令：

    
    
    notepad 1.txt:flag.txt

进行查看和编辑：

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550113987_5c64dcc378bfd.png!small)

此类文件可以通过直接删除宿主文件清除。  

**单独的ADS** **数据流文件**

这类可以通过命令

    
    
    echo hide > :key.txt 

来进行创建：![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114058_5c64dd0ae17c0.png!small)

创建之后在目录下无文件，也没有依赖的宿主文件，并且此类文件在当前目录命令行下是无法查看的，因为它是依赖于文件夹的ADS数据流文件：

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114069_5c64dd15dbd14.png!small)因此需要退到上级目录进行查看：

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114081_5c64dd214a2d6.png!small)使用命令：

    
    
    notepad test:key.txt

可以进行编辑：

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114095_5c64dd2fd379c.png!small)

像这类文件的清除一种是通过删除文件夹的方式，但是假如这个文件是创建在系统根目录如何进行处理，此时需要用到 **WinHex** **Tools** \-**Open Disk** 功能。

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114149_5c64dd6527197.png!small)选中目标盘符，找到目标文件夹。

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114161_5c64dd7137af9.png!small)可以进行查看：

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114173_5c64dd7d4bc17.png!small)如需删除只需在
**WinHex** 选中之后按 **Delete** 即可。

### webshell后门

由于 **windows xp** 之后的系统对于ADS文件都没有执行权限，因此隐藏此类webshell需要用到文件包含来进行配合。

首先创建被包含文件 **index.php:s.txt。**

内容为：

    
    
    <?php phpinfo();?>

![](https://image.3001.net/images/20190214/1550114370_5c64de426b0ec.png!small)

然后参考：<https://blog.csdn.net/nzjdsds/article/details/81260524>的方法，Hex之后通过利用PHP
可变变量进行二次转换， **696e6465782e7068703a732e747874** 为 **index.php:s.txt**
的hex编码，最终test.php中内容如下:

    
    
    <?php 
    
    $a="696e6465782e70"."68703a732e747874";
    
    $b="a";
    
    include(PACK('H*',$$b))
    
    ?>

访问test.php即可：

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114344_5c64de28c68fa.png!small)

使用最新版 **D盾** 扫描也无法发现问题。

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114398_5c64de5e7cb16.png!small)PS：这边另外补充一点，文件最好寄宿在纯静态文件，因为像php文件修改后会改变属性，系统层相当于生成了一个新的文件，导致ADS文件失去宿主而消失。

### 文件上传

这一块主要是用于 **Bypass** 上传黑名单验证，因为在我们上传数据流文件时，形如 **test.php::$DATA** 、
**test.php:a.txt** 这样的后缀， **windows**
系统必定需要创建一个对应的宿主文件test.php，同时假设我们需要上传的文件内容为：

    
    
    <?php phpinfo();?>

下面是上传是会出现的现象：

上传的文件名  
| 服务器表面现象  
| 生成的文件内容  
  
---|---|---  
Test.php:a.jpg  
| 生成Test.php  
| 空  
  
Test.php::$DATA  
| 生成test.php  
| <?phpphpinfo();?>  
  
Test.php::$INDEX_ALLOCATION  
| 生成test.php文件夹  
|  \  
  
Test.php::$DATA\0.jpg  
| 生成0.jpg  
|  <?phpphpinfo();?>  
  
  
可以注意到上传文件名为 **Test.php::$INDEX_ALLOCATION**
时会生成对应的文件夹，利用此种特性也可以用于突破UDF提权时遇到无法创建文件夹的问题。  

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114649_5c64df59e45ef.png!small)

### 病毒免杀

前面提到过在 **windows xp 03**
之后的版本的数据流文件都被禁止了执行权限，因此可以使用wscript来运行vbs，此处在C盘根目录使用命令：

    
    
    type1.vbs > :2.vbs

创建了依赖C盘存在的数据流文件 **c::2.vbs** ，没有工具正常是无法清除的。

使用命令：

    
    
    wscript c::2.vbs

可以成功执行vbs。

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114748_5c64dfbce1368.png!small)

当然我们今天主要是来测试病毒免杀的，所以首先使用 **msf** 生成一个 **dll** 木马。

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114773_5c64dfd571fae.png!small)很容易就被确认为病毒。

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114784_5c64dfe0c3498.png!small)使用命令：

    
    
    type test.dll > 1.txt:ms

将dll写入数据流文件：

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114810_5c64dffa1f588.png!small)再次使用
**360** 联网完全体进行查杀，无法发现此类木马。  

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114831_5c64e00fe9147.png!small)使用命令：

    
    
    regsvr32 1.txt:ms
    

运行dll，当然由于病毒行为太明显没作处理，360还是会动态查杀的，这个配合一点其他的免杀技术完全过掉也不难，这边不再多做赘述。

![Clipboard
Image.png](https://image.3001.net/images/20190214/1550114879_5c64e03f831f5.png!small)

## 小结

目前杀毒软件和webshell查杀对ADS数据流技术的查杀支持并不是很好，并且木马可能进行依赖于盘符的驻留方式，希望能本文能有所帮助。

### 检测 ****

 ****

 ****

检测的工具常见的有 **LADS (List Alternate Data Streams)、Streams、Sfind** 等（供参考）

### 清除 ****

 ****

 ****

清除方式目前一个是个人用过的 **winhex** 和删除宿主文件这两种方式，另一个就是借助相关工具如 **IceSword** 删除。

## 参考

> <https://www.freebuf.com/articles/73270.html>
>
> <https://www.cnblogs.com/feiyucha/p/9940895.html>
>
> <https://blog.csdn.net/nzjdsds/article/details/81260524>
>
> <https://www.i0day.com/733.html>

***本文作者：3unshine，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


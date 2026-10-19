# 目标导读

    
    
    0x01、前言
    0x02、简介
    0x03、DedeCMS V5.7 SP2前台文件上传(CVE-2018-20129)
        01、漏洞复现
        02、漏洞分析
        03、遗留问题
        04、漏洞修复
        05、漏洞总结
    0x04、DedeCMS V5.7 SP2后台文件上传(CVE-2019-8362)
        01、漏洞复现
        02、漏洞分析
        03、漏洞修复
        04、漏洞总结
    
    0x05、总结
    

# 前言

前段时间看到有篇文章是关于DedeCMS后台文件上传(CNVD-2022-33420)，是绕过了对上传文件内容的黑名单过滤，碰巧前段时间学习过关于文件上传的知识，所以有了这篇文章，
**对DedeCMS的两个文件上传漏洞(CVE-2018-20129、CVE-2019-8362)做一个分析** 。

# 简介

DedeCMS由上海卓卓网络科技有限公司研发的国产PHP网站内容管理系统；具有高效率标签缓存机制；允许对类同的标签进行缓存，在生成
HTML的时候，有利于提高系统反应速度，降低系统消耗的资源。众多的应用支持；为用户提供了各类网站建设的一体化解决方案，在本版本中，增加了分类、书库、黄页、圈子、问答等模块，补充一些用户的特殊要求
。

# DedeCMS V5.7 SP2前台文件上传(CVE-2018-20129)

### 漏洞复现

复现环境：phpstudy、DedeCMS V5.7 SP2、php5.6.9  
前提条件：会员模块开启、以管理员权限登录。  
会员模块默认情况下是不开启的，需要管理员在后台手动。

登录到前台以后找到内容中心，发表一篇文章，点击下面编辑器中找到上传图片按钮，其实这里原本想实现的功能就是一个简单图片上传的功能。

![image](https://image.3001.net/images/20220530/1653904530_629494922c5612321e7dd.png!small)

然后使用BurpSuite抓包，把文件名称从1.png改成1.png.p*hp，然后放包上传。

![image](https://image.3001.net/images/20220530/1653904562_629494b235bbd2c21e58c.png!small)

在响应信息中得到上传文件的保存地址，并且文件的后缀也是PHP。

![image](https://image.3001.net/images/20220530/1653904576_629494c0ec7a55e4525e9.png!small)

但是当我们尝试去访问这个文件时会发现有的文件是不解析的，这跟我们上传的文件有关系，这个问题我们后面再解释。

上传的脚本文件可以正常利用。

![image](https://image.3001.net/images/20220530/1653904591_629494cf15dac5f47d60e.png!small)

### 漏洞分析

从抓取的数据包可以看到提交路径是/dedecmsgbk/include/dialog/select_images_post.php，跟进这个文件看一下进行了怎样的处理。

![image](https://image.3001.net/images/20220530/1653904625_629494f1437168d54ad82.png!small)

在select_images_post.php文件中的第36行，对文件名称进行了正则替换，正则会匹配`回车符、换行符、制表符、*、 % 、/ 、？、<、>、
|、 “、 ：、`并至少匹配1次，把匹配到的内容替换成‘
’（空），因为我们通过抓包把文件名称改成了1.png.p*hp，所以经过替换会变成1.png.php。

![image](https://image.3001.net/images/20220530/1653904649_6294950957df1628725e8.png!small)

紧接着在第38行对文件名称再次验证，文件名中只需要存在jpg、gif、png中任意一个，如果不存在程序就会提示错误信息，但这里有一个非常大的缺陷，就是程序只是验证文件名称中存在jpg、gif、png三个中的任意一个，并不是在验证文件的后缀。所以我们上传的文件名称1.png.php是可以绕过这个限制的。既然这个限制这么轻松就可以绕过，那我们可不可以直接把文件名称改成1.png.php，而不是1.png.p*hp呢？这个问题最后会进行解答。

![image](https://image.3001.net/images/20220530/1653904726_62949556610d94ee926ba.png!small)

程序在第44行对上传文件的MIME类型进行验证，这里进行白名单验证，在`$sparr`数组中定义了六个允许上传的MIME类型，然后把我们上传文件的MIME去除两端空格并转变成小写得到`$imgfile_type`，然后判断`$imgfile_type`是否在数组`$sparr`，如果不存在程序就会提示错误信息。

![image](https://image.3001.net/images/20220530/1653904735_6294955fc7c1774266096.png!small)

漏洞的产生还有一个非常重要的原因，从第57行开始分析，用户的UserID拼接上'-'再拼接上一段随机字符形成`$filename_name`，`$mdir`是年(年份后两位)月日，`$mdir`跟`$filename_name`拼接形成`$filename=$mdir/$filename_name`，然后使用explode函数按照'.'分割文件名`$imgfile_name`，形成数组`$fs`内容（'1'，'png'，'php'），然后取出数组中的最后一个元素拼接到了`$filename_name`参数后面组成文件名，而数组的最后一个元素正好是PHP，所以PHP文件就可以上传了。

![image](https://image.3001.net/images/20220530/1653904771_62949583273efba31154c.png!small)

并且在最后也可以看到完成的路径。

![image](https://image.3001.net/images/20220530/1653904798_6294959e0e978d6e32ebb.png!small)

程序的最后就是把上传文件的信息保存到了数据库中。

### 遗留问题

上面我们留下了两个疑问：1.直接上传PHP文件可不可行，2.为什么部分脚本文件上传失效。接下来我们将解决这两个问题。

 **1.直接上传PHP文件可不可以**

![image](https://image.3001.net/images/20220530/1653904812_629495acb10785cb358c0.png!small)

从返回信息中可以看到，不允许我们上传这种类型的文件，在select_images_post.php文件中包含了config.php文件，config.php文件包含了common.inc.php文件，common.inc.php文件包含了uploadsafe.inc.php文件，在uploadsafe.inc.php文件的第33行对文件的后缀进行了验证，定义了一些禁止上传的文件后缀`$cfg_not_allowall`，所以直接上传PHP文件是不可以的，上传PHP文件要配合
select_images_post.php文件中替换为空的操作进行利用。

![image](https://image.3001.net/images/20220530/1653904826_629495bac8a7ef17c7306.png!small)

这里的提示信息跟上面我们看到的是一样的。并且在这里面也发现了验证MIME类型。

![image](https://image.3001.net/images/20220530/1653904922_6294961a1c1b5c865d5a1.png!small)

 **2.为什么部分脚本文件上传不能利用**  
通过观察我们上传的PHP脚本文件，可以发现脚本文件被二次渲染了。  
比如这个：

![image](https://image.3001.net/images/20220530/1653904934_62949626b30296ca907c7.png!small)

但是对于PNG图片把恶意代码插入的IDAT数据块的脚本文件可以避免被二次渲染，并且可以成功利用。

![image](https://image.3001.net/images/20220530/1653904945_6294963103d6df1115f8d.png!small)

并成功执行命令。

![image](https://image.3001.net/images/20220530/1653904955_6294963bdc1d1187aebed.png!small)

### 漏洞修复

 **修复方式一**

在给文件名拼接后缀时，对后缀进行二次验证。

比如说在select_images_post.php的第60行添加如下代码。

![image](https://image.3001.net/images/20220530/1653904969_62949649c678eef5c20d5.png!small)  
如果再上传1.png.p*hp文件，程序执行到`$fs[count($fs)-1]`会取出最后一个数组成员php，而`$cfg_imgtype`是`jpg|gif|png`，不包含，所以程序提示报错信息，上传失败。

![image](https://image.3001.net/images/20220530/1653904981_6294965548c8977406c4f.png!small)

 **修复方式二**

在官方DedeCMS
V5.7.93版本中，uploadsafe.inc.php文件中由原先只要文件名中包含`$cfg_not_allowall`参数定义的这些文件后缀，改成了使用pathinfo()方法获取文件的后缀，然后判断后缀是否存在黑名单中，按照之前的文件名来说的话，这里获取的后缀是p*hp，依然不在黑名单数组中。

![image](https://image.3001.net/images/20220530/1653904996_62949664aeabb8c88c5ab.png!small)

因为更新迭代，此时的富文本编辑器中的数据提交到了select_images_post_wangEditor.php文件中，这里的正则匹配特殊字符替换成空，但是这里的文件后缀也采用pathinfo()方法获取文件后缀，之前文件名1.png.p*hp经过特殊字符替换成空，然后pathinfo()方法获取获取到的文件后缀为php，这里的白名单`$cfg_imgtype`是`jpg|gif|png`，显然php并不在其中，所以返回提示信息"您所上传的图片类型不在许可列表"。

![image](https://image.3001.net/images/20220530/1653905061_629496a540f1f7d4ca16d.png!small)

官方已修复该漏洞，请注意升级。补丁链接：  
https://www.dedecms.com/download

### 漏洞总结

从上面可以知道上传`p*hp`后缀的原因是在正则替换之前存在着一个黑名单验证，传入`p*hp`后缀后可以绕过这个黑名单验证然后被正则把*替换为空，而文件后缀获取时会取出最后一个数组成员php，并没有进行二次验证，所以造成了这次文件上传漏洞的产生。

# DedeCMS V5.7 SP2后台文件上传(CVE-2019-8362)

### 漏洞复现

复现环境：phpstudy、DedeCMS V5.7 SP2、php5.6.9

首先准备一个压缩包1.zip，压缩包里面的文件名为1.jpg.php，文件内容为：

![image](https://image.3001.net/images/20220530/1653905035_6294968bd150dafc44401.png!small)

安装完成之后登录到系统后台，默认账号/密码是admin/admin，点击在左侧当导航栏中的核心按钮，然后选中附件管理中的文件式管理器，进入其中的soft目录中。

![image](https://image.3001.net/images/20220530/1653905092_629496c424d27d0ae1b5d.png!small)

然后把之前准备好的压缩包上传上去。

![image](https://image.3001.net/images/20220530/1653905103_629496cfd890f89c617e1.png!small)

然后访问album_add.php文件发布新图集，这里需要提前创建一个图集主栏目，上传方式选择从ZIP压缩包中解压图片，选择之前上传的1.zip。

![image](https://image.3001.net/images/20220530/1653905116_629496dceb036f8596737.png!small)

上传完成之后，我们点击预览文档。

![image](https://image.3001.net/images/20220530/1653905131_629496eb87591a2a83686.png!small)

然后就会跳转到前台页面，点击下面的testZip。

![image](https://image.3001.net/images/20220530/1653905144_629496f8e360b3179deb6.png!small)

当点击testZip，页面跳转，之前压缩包内的1.jpg.php里面的代码会执行。

![image](https://image.3001.net/images/20220530/1653905162_6294970ac71593f031ec9.png!small)

我们来看一下这里正常上传图片的效果，当压缩包内是图片的话，这个会显示出图片，至于链接的话就是查看图片的链接。

![image](https://image.3001.net/images/20220530/1653905180_6294971c4de98d1c638b9.png!small)

![image](https://image.3001.net/images/20220530/1653905191_629497277d78182f2836a.png!small)

### 漏洞分析

使用burpSuite抓包，发现提交到了album_add.php文件，在/dede/album_add.php中找到这个文件，跟进程序看到底是怎么处理的。  
album_add.php文件的前半部分都是一些验证赋值操作，或者是验证关于相关栏目的信息，但是因为上传的时候选择的是从压缩包中解压图片，所以`$formzip`参数值为1，这个后面会用到。

![image](https://image.3001.net/images/20220530/1653905204_629497342c70c113ce096.png!small)

因为`$formzip`参数值为1，所以会解压压缩包中的图片，其实可以发现在程序的173行调用ExtractAll()方法完成解压操作，传入`$zipfile`和`$tmpzipdir`两个参数，`$zipfile`是压缩包的保存路径，`$tmpzipdir`是创建出来存在解压文件的路径。

![image](https://image.3001.net/images/20220530/1653905218_62949742b6e24614ddcd5.png!small)

跟进到ExtractAll()方法，查看程序的下一步执行。

![image](https://image.3001.net/images/20220530/1653905231_6294974f2a604540c1568.png!small)

在程序第309行会调用get_List()方法获取压缩包中的信息。

![image](https://image.3001.net/images/20220530/1653905245_6294975da237e70e6105c.png!small)

这里要提一下ReadCentralFileHeaders()方法，在这个方法中会读取到压缩包中的文件名等信息。

然后回到ExtractAll()方法，接着调用Extract()方法解压单个文件，这个方法中也会调用ReadCentralFileHeaders()方法读取到压缩包中的文件名等信息，然后在361行调用ExtractFile()方法，并把获取压缩包中文件信息(`$header`)、压缩包路径(`$zip`)、创建的目录(`$to`)这三个参数一起传入。

![image](https://image.3001.net/images/20220530/1653905263_6294976f319c02e74a961.png!small)

ExtractFile()方法中的大致流程就是首先会创建的目录下面创建一个gz文件，文件名称是`$header[‘filename’].gz`拼接的，也就是1.jpg.php.gz，接下来在创建一个`$header[‘filename’]`文件，此时这个文件名就是1.jpg.php，再把读取到的内容写入进去，这个过程中并没有对内容进行校验。

![image](https://image.3001.net/images/20220530/1653905273_629497799801553fb9bfe.png!small)

从调试中可以看到，写入的内容就是上传压缩包中文件的内容`<?php phpinfo();?>`，最后删除gz文件。完成解压。

![image](https://image.3001.net/images/20220530/1653905287_6294978794aff39442abb.png!small)

完成解压之后程序回到album_add.php文件中，在程序第176行，程序调用了GetMatchFiles()方法，并且传入了三个参数，分别是`$tmpzipdir`、`jpg|png|gif`、`$imgs`。

![image](https://image.3001.net/images/20220530/1653905302_6294979655ae97bf1c4be.png!small)

![image](https://image.3001.net/images/20220530/1653905315_629497a33f6d58d69694b.png!small)

在GetMatchFiles()方法中可以看到，其实就是读取`$tmpzipdir`目录中的文件，在程序第163行会有正则匹配文件名中是否包含`jpg|png|gif`，如果包含的话才会加到数组中，这也就是为什么要在文件名中加上jpg的原因，此时程序执行结束回到album_add.php文件，
继续跟进分析。

回到album_add.php文件。此时的`$imgs`就是读取到的文件名，此时会进行循环操作，循环中首先会组成一个保存路径`$savepath`，是由`$cfg_image_dir`拼接上年月组成，`$iurl`是由`$savepath`进行一系列的拼接组成，最关键的点是在程序的第184行，取出`$imgold`参数的最后四个字符，`$imgold`就是GetMatchFiles()方法读取到的文件路径，其中最后四个字符就是`.php`，然后拼接在`$iurl`上面，`$cfg_basedir`跟`$iurl`组成文件名，所以此时的文件后缀就是php，然后利用copy()方法，把`$imgold`中的内容复制到`$iurl`中，并且删除之前创建的ziptmp中的目录，最后就是进行一些图片的尺寸以及数据库的操作。

![image](https://image.3001.net/images/20220530/1653905334_629497b6344849e18b250.png!small)

程序继续向下进行，在第209行，会把`$iurl`参数参入到数据库中，就是把发表的信息都存入到数据库中。

![image](https://image.3001.net/images/20220530/1653905348_629497c44eb72d10e16c6.png!small)

最后如果选择删除压缩包，会把压缩包删除，再通过RmDirFiles()方法删除对应创建的目录`$tmpzipdir`。

当前台调用的时候可以发现跳转的链接，点击超链接进入。

![image](https://image.3001.net/images/20220530/1653905383_629497e7ca0810c677c27.png!small)

当要点击标题链接时，在左下角也会发现同样的URL，这个URL就是我们保存的PHP文件的路径。

![image](https://image.3001.net/images/20220530/1653905395_629497f3a87bcad5b3afe.png!small)

并且从代码中我们也可以看见，这个链接是写死在HTML文件中的。

![image](https://image.3001.net/images/20220530/1653905412_629498042a836adcddfa2.png!small)

所以点击链接就会跳转到PHP文件，执行文件中的代码。

### 漏洞修复

我们把/dede/file_class.php中第161行代码修改成：

    
    
    else if (in_array(pathinfo($filename, PATHINFO_EXTENSION), explode("|", $fileexp),true) === TRUE)  
    

这里之前是验证文件名，现在改成验证文件后缀，后续就会验证文件后缀是否存在`$fileexp`中了。

最新版中使用pathinfo()方法获取到文件的后缀，然后判断是否后缀是否在白名单数组中。然后再重复一次之前的上传流程，此时在这个断点处可以看到，php后缀并不满足判断条件，所以此时的文件名并不就加入到`$filearr`中，`$filearr`数组就是当时作为参数传入的`$imgs`数组，因为`$imgs`为空数组，所以接下来的循环复制操作也就不会执行了。

![image](https://image.3001.net/images/20220530/1653905429_62949815b7f480ec66354.png!small)

![image](https://image.3001.net/images/20220530/1653905441_6294982195cfe087978d5.png!small)

操作完成之后，再看之前的前台操作页面，已经没有之前的跳转链接了。

![image](https://image.3001.net/images/20220530/1653905452_6294982c140b095e609c1.png!small)

官方已修复该漏洞，请注意升级。补丁链接：

https://www.dedecms.com/download

### 漏洞总结

在分析过程中可以看到，对于压缩包中文件的后缀并没有进行验证，文件后缀的获取也没有进行二次验证，而是直接获取文件名称的最后四个字符拼接上去，最终造成了文件上传漏洞的产生。

# 总结

从上面两个实例中可以看到，第一个漏洞有用到黑名单验证，但并不是验证的文件后缀，两个漏洞都用白名单对文件名进行了验证，保存文件时对于文件后缀的获取并没有进行二次验证，而是直接获取拼接，所以才会造成文件上传漏洞的产生，造成系统的Getshell。

对于上传文件其实也要对内容进行验证的，并且这两个地方本来都是上传图片的功能，验证上传文件的头部信息，对上传文件进行二次渲染，在保存文件时对后缀进行二次验证，这样就可以极大程度的避免文件上传漏洞的产生。


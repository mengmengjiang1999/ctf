***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

今天放假闲着无事就找了个cms来挖挖漏洞，挖到的漏洞比较简单，适合新手入门，所以本篇文章就记录一下这几个漏洞的审计过程，以及如何从新手的角度去挖到cms一些常见的漏洞，如果是大佬就可以绕道了。

本文涉及相关实验：[任意文件下载漏洞的代码审计](https://www.hetianlab.com/expc.do?ec=ECID06a1-2876-4bfb-8e59-a0096299c167&pk_campaign=freebuf-wemedia)（通过本节的学习，了解文件下载漏洞的原理，通过代码审计掌握文件下载漏洞产生的原因以及修复方法。）

## 前置工作

### 寻找cms及搭建

一般来说我们可以到谷歌百度等引擎找到cms的官网下载源码，或者码云，然后在本地用phpstudy搭建起来环境

![headImg.action?news=0a8bbc01-91a0-4d8b-8ed6-d7f532d60e36.png](https://image.3001.net/images/20210518/1621329433_60a386193c2142e3a3bcf.png!small)

我们在这里下载cms的源码，下载之后怎么在本地搭建呢

我们打开phpstudy-》其他选项菜单-》站点域名管理里

![headImg.action?news=eab37afa-8cbf-4b74-bc63-b660b5031194.png](https://image.3001.net/images/20210518/1621329434_60a3861a3850679202de4.png!small)

把网站目录填写你下载源码的路径就好了，然后进hosts添加域名

![headImg.action?news=64445be5-93e6-439a-bb13-0444a95fac32.png](https://image.3001.net/images/20210518/1621329434_60a3861ae71665aa4f813.png!small)

然后不出意外就可以访问了

### 配置debug

在白盒代码审计的时候你可能会需要到断点调试，这个时候就需要用到`xdebug`，这里我个人用的是`vscode`编辑器，当然你用`phpstorm`也是可以的，配置过程如下

1.首先在`vscode`的应用商店下载`php debug`插件

2.在`php.ini`添加

    
    
    [XDebug]  
    xdebug.profiler_output_dir ="D:\phpStudy\PHPTutorial\tmp\xdebug"  
    xdebug.trace_output_dir ="D:\phpStudy\PHPTutorial\tmp\xdebug"  
    zend_extension="D:\phpStudy\PHPTutorial\php\php-7.1.13-nts\ext\php_xdebug.dll"  
    xdebug.remote_enable = on  
    xdebug.remote_autostart = on

3.在文件-》首选项-》设置-》用户-》扩展-》`settings.json`

    
    
    {  
    "php.validate.executablePath": "D:/phpStudy/PHPTutorial/php/php-7.1.13-nts/php.exe",  
    "editor.mouseWheelZoom": true,  
    "php.executablePath": "D:/phpStudy/PHPTutorial/php/php-7.1.13-nts/php.exe",  
    "workbench.editorAssociations": [  
    {  
    "viewType": "jupyter.notebook.ipynb",  
    "filenamePattern": "*.ipynb"  
    }  
    ],  
    "explorer.confirmDelete": false  
    }

`4.launch.json`添加

    
    
    {  
    "version": "0.2.0",  
    "configurations": [  
    {  
    "name": "Listen for Xdebug",  
    "type": "php",  
    "request": "launch",  
    "port": 9000  
    },  
    ]  
    }

上面一些路径自行更改一下，然后我们新建一个`1.php`打个断点，然后访问`http://127.0.0.1/1.php`，如果出现如下，就说明`xdebug`环境就成功搭建了

![headImg.action?news=d502638f-8968-4667-b2a9-d288acf0b78e.png](https://image.3001.net/images/20210518/1621329435_60a3861ba74345cc4861a.png!small)

## 文件上传漏洞

通常来说，漏洞等级评级高的就是可以`rce`的高危漏洞，而想要`rce`最常见的就是文件上传

找文件上传漏洞的话，有两种思路，分别为黑盒和白盒，对新手来说代码功底不强的话，黑盒应该是会比较简单的，这里分别从两个不同的角度来寻找漏洞

### 黑盒思路

一般来说网站的后台很多地方都是可以文件上传的，我们进入后台之后可以寻找诸如文章发布处，修改头像处，附件，插件管理等地方，特别是像在文章发布处有这种富文本编辑器的地方往往会有上传图片和上传附件的功能

我们拿刚刚搭建好的`cms`，进入后台之后在发布文章处找到有可以上传图片的地方

![headImg.action?news=acbac1ef-7220-43e1-8aaf-23618145f84e.png](https://image.3001.net/images/20210518/1621329436_60a3861c5ed90adb39b31.png!small)

我们随便上传一个`1.php`，发现提示上传图片发生错误，应该是被过滤了

![headImg.action?news=38798c38-9517-41bf-8134-4d8b31085267.png](https://image.3001.net/images/20210518/1621329437_60a3861d1bb7ddf04be2d.png!small)

但不确定是不是前端过滤还是后端过滤，我们先上传`1.jpg`，抓包改一下

![headImg.action?news=847f53ee-2bfd-43b5-a3de-8c1a8134b837.png](https://image.3001.net/images/20210518/1621329437_60a3861dd759579d44d4a.png!small)

发现上传成功，原来只是前端过滤，芜湖这不起飞，我们再访问一下我们上传的文件

![headImg.action?news=5c1b8045-d313-4e39-b20b-7582eda55915.png](https://image.3001.net/images/20210518/1621329438_60a3861ece12f35325148.png!small)

发现已经成功`getshell`

这里的过滤比较简单，新手可以学一下各种绕过的技巧：<https://xz.aliyun.com/t/6692>

那么除了发布文章处，我们还可以在上传图片这些地方入手

![headImg.action?news=12035fdd-c68a-4596-aca3-e7a4ec608967.png](https://image.3001.net/images/20210518/1621329439_60a3861fd09e8dc0e97cc.png!small)

我们在微信小程序这里的基本设置处看到有个首页分享封面

和上面一样，只是前端做了过滤，我们抓包改文件即可

![headImg.action?news=3561a211-0067-429f-8876-428675f3e430.png](https://image.3001.net/images/20210518/1621329440_60a38620bc30ce5e90ce8.png!small)

但是这里的话只是提示上传成功，没有回显出来文件的名字，我们可以在本地文件处看看到底上传了什么东西

![headImg.action?news=a371a196-d9e3-416f-8f03-e79a392e48b5.png](https://image.3001.net/images/20210518/1621329441_60a38621a69fb04bf356d.png!small)

发现上传了`wx_share_cover.php`，这个文件的名字是固定的，于是我们访问试试看

发现也已经成功`getshell`

### 白盒思路

对于初学者而言，找漏洞不能只看黑盒，也要基于白盒审计进行，所谓白盒审计可以简单地理解为就是看着代码找漏洞

我们知道`php`文件上传的函数是`move_uploaded_file()`，或者一般来说上传的方法名是有`upload`关键字的，我们可以全局搜索他们定位到上传功能的代码里面

我们找到相应的代码块如下

![headImg.action?news=d3764d49-2831-4bfc-99ca-67a7703cbf73.png](https://image.3001.net/images/20210518/1621329442_60a386226de6d3ff974fb.png!small)

可以看到`validate`的`check`就是这里的过滤，我们用上面的方法绕过即可，如果想清楚的跟踪进这个函数就可以在这里打个断点，然后分析

当然白盒寻找`rce`漏洞，我们还可以找找`file_put_content`等可以直接写文件的函数

## 任意文件删除

通常我们找文件删除漏洞的话，可以全局搜索`unlink`函数

### 第一处

![headImg.action?news=9e465590-26fa-43d5-b83e-deb3dbbdbd22.png](https://image.3001.net/images/20210518/1621329443_60a386233ff84762ae648.png!small)

这里的代码功能比较简单，正如注释所说的删除目录下面的所有文件，但不删除目录

我们可以看到`$directory`是我们可控的，而且没用做任何的过滤，说不定就可以穿越目录从而任意删除文件了，我们先手动加一个`var_dump(scandir("."));`来观察一下这里所处的位置

![headImg.action?news=06279025-6de4-477b-8a9c-00b46a8ffb99.png](https://image.3001.net/images/20210518/1621329444_60a386241f40b09ede47c.png!small)

可以看到现在是在`public`的目录下，那我们就在上一层目录随便新建一个目录，里面随便新建几个文件试试看

![headImg.action?news=7545c485-cd26-46e7-af2c-c2e7db1c6080.png](https://image.3001.net/images/20210518/1621329444_60a38624dcef84cae3b18.png!small)

我们输入

    
    
    http://www.test123.com/system/dir/del?directory=../123

可以发现`txt`文件都被删除了，但是文件夹没有被删除

![headImg.action?news=9af091a8-c743-4fff-b43b-61d61a722462.png](https://image.3001.net/images/20210518/1621329445_60a3862571e6f35d55df1.png!small)

因为这个功能不能删除目录，只能删除目录的文件，如果我们还想删`412315`里面的文件就可以输入

    
    
    http://www.test123.com/system/dir/del?directory=../123/412315

### 第二处

![headImg.action?news=9da606d2-dfbc-4d5b-ad7c-f43bcd7c76f1.png](https://image.3001.net/images/20210518/1621329446_60a386260a8116a8f0dde.png!small)

这里和第一处差不多，但是功能有点不一样，这里是可以把整个目录删除了，我们输入如下就可以删除整个`123`目录了

    
    
    http://www.test123.com/system/dir/delDir?directory=../123

## 反序列化漏洞

既然前面已经挖到了文件上传漏洞，这个`cms`又是`thinkphp6.0`的版本，我们可以再找一下有没有可以触发`phar`函数的漏洞

### 第一处

突然看到我们前面的任意文件删除漏洞处，不正是有个`is_dir`函数吗，而且又是可以控制的，真是踏破铁鞋无觅处得来全不费功夫

![headImg.action?news=d418c40e-8f60-4274-89c6-322ce07d5dc7.png](https://image.3001.net/images/20210518/1621329446_60a38626e0d810188a074.png!small)

我们先用网上公开的反序列化链生成`test.jpg`，然后利用上面的任意文件删除漏洞上传，上传到这个位置

    
    
    {"code":1,"msg":"上传成功","url":["http:\/\/www.test123.com\/uploads\/postImages\/20210404\\3c5ea1104433e1cb734be47ab8377a11.jpg"]}

我们再用`phar`协议去触发这个文件即可`rce`

    
    
    http://www.test123.com/system/dir/del?directory=phar://uploads/postImages/20210404/3c5ea1104433e1cb734be47ab8377a11.jpg

###
![headImg.action?news=1cbc1909-f1ec-4f0b-b82b-3e60fad1ca53.png](https://image.3001.net/images/20210518/1621329447_60a3862795e1bef97dba0.png!small)

### 第n处

除了上面那个任意文件删除处的`is_dir`，我们可以再找找还有没有其他地方能够触发的，随手一找又发现两处

![headImg.action?news=718ac01b-4905-4126-93d8-bd264ce92eb1.png](https://image.3001.net/images/20210518/1621329448_60a38628462dd6cac91ac.png!small)

![headImg.action?news=94c36d80-db9c-41c4-a4f9-dabde209379a.png](https://image.3001.net/images/20210518/1621329449_60a38629167be94ae794d.png!small)

这还只是单单用`is_dir`函数，没算上其他的就已经那么多了，这个 cms 真是"漏洞百出"

本文的漏洞已提交至 cnvd 平台，作为新手找一些少人用的 cms 挖上面几种漏洞还是比较容易的


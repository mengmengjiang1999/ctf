***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：davichi8282，属于FreeBuf漏洞奖励计划，未经许可禁止转载**  

## 0×00概述

**继上次审计HDWiki之后，最近拿到一套新的源码Ear_Music_20180510_UTF8最新版进行审计，发现这套cms还是比较安全的，而当我审计遇到一处下载点的时候发现存在安全问题，也就是任意文件下载漏洞，任意文件下载漏洞php最常见的函数就是readfile()这个函数，当里面的参数我们可以控制的话就会存在任意文件下载风险。**

## 0×01 白盒审计

源码信息：Ear_Music_20180510_UTF8

问题文件： \template\default\source\down.php  

漏洞类型：任意文件下载

站点地址：<http://www.erduo.in/index.php/download/>

首先进行安装之后主界面如下；

![3.png](https://image.3001.net/images/20180525/15272316823770.png!small)

由于我是习惯跟着功能点走的，个人习惯吧，有些人通读全文，有些人跟踪数据流等，各有各的利弊吧，这个cms发现功能点比较多，各种编辑上传什么的，当审计遇到一个“下载LRC歌词”功能点的时候发现是使用readfile()函数的，具体页面以及代码段如下：

![33.png](https://image.3001.net/images/20180525/15272341796305.png!small)

代码段为\template\default\source\down.php

![34.png](https://image.3001.net/images/20180525/15272346094323.png!small)

看到readfile()函数了，这里的$file函数是用户提交的歌词信息所以说是可控的，从这段代码可以看到$file参数是通过geturl和getfield两个函数生成的，分别跟进，首先geturl()函数路为/source/system/function_common.php。

![45.png](https://image.3001.net/images/20180525/15272351456698.png!small)

getfield()函数从函数名称就能看出来是用来获取数据库信息的所以此处没有写出来，重点看geturl()函数。可以看到通过一些正则来打出最后的$url参数，但是当$file参数不符合正则的时候直接将$file参数赋给$url即你上传的什么就读取什么，读取下载的时候未作任何过滤操作，好这时候我们就转向上传的地方看看。

具体路径为\source\user\music\ajax.php，这边是歌词上传。

![55.png](https://image.3001.net/images/20180525/15272364569681.png!small)

可以看到$lyric就是歌词参数，但是看到有checkrename(),unescape(),SafeRequest()三个函数过滤一个一个看，首先SafeRequest()函数，路径为\source\system\function_common.php。

![32.png](https://image.3001.net/images/20180525/15272375069058.png!small)

可以看到有addslashes过滤和'\\\'替换为空，一般这种替换成空的方法往往存在绕过可能。来看下一个函数unescape()，路径还是上面那个。

![555.png](https://image.3001.net/images/20180525/15272377563834.png!small)

可以看到里面还有SafeSql()函数，通过追踪发现也是过滤'\\\'的，这里就不截图了。

最后来看下最重要的函数checkrename()函数，路径为\source\system\function_common.php。

![65.png](https://image.3001.net/images/20180525/15272382366584.png!small)  

可以看到这里主要是使用正则来进行过滤，当匹配到"./","iframe",".php"这3个任何一个的时候直接显示'Safety
filter'字段进行过滤，还有上面几个函数是过滤"\"这个的，综合看来由于读取的时候未作任何过滤所以可以通过输入物理路径进行任意文件的下载读取。

##  **0×02 漏洞利用**

比如config.inc.php文件的物理路径为：

D:\phpStudy\WWW\Ear_Music_20180510_UTF8\source\system\config.inc.php

由于"\"会被过滤可使用"/"替换绕过，".php"会被过滤可通过后面加点进行绕过，综合起来最终的payload为：

D:/phpStudy/WWW/Ear_Music_20180510_UTF8/source/system/config.inc.php

首先注册一个账号进去之后到上传音乐页面。

![11.png](https://image.3001.net/images/20180525/15272388538439.png!small)

歌词位置填写上面的payload之后保存编辑，然后到待审音乐点击刚上传的音乐。

![43.png](https://image.3001.net/images/20180525/15272389674042.png!small)

跳到下面页面之后点击下面的"下载LRC歌词"，即可下载我们的配置文件了。

![46.png](https://image.3001.net/images/20180525/15272391637899.png!small)  

 ***本文原创作者：davichi8282，属于FreeBuf漏洞奖励计划，未经许可禁止转载**


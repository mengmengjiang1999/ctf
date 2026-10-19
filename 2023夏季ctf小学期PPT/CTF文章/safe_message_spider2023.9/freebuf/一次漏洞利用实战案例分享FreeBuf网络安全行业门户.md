## 写在前面

>
> 因为鄙人是一个才刚入门的安全小白，想着在这里记录一下我的安全成长之路，向各位多多学习。这也是我入门以来做的第一个实战项目，同时也是第一次在freebuf上发表自己的文章，有许多不足的地方，希望各位多多指教。

## fastadmin简述

> FastAdmin – 基于ThinkPHP和Bootstrap的极速后台开发框架，可以一键生成
> CRUD，自动生成控制器、模型、视图、JS、语言包、菜单、回收站。是基于Apache2.0开源协议发布，目前被广泛应用于各大行业应用后台管理。

fastadmin官方源码下载地址：<https://www.fastadmin.net/download.html>

## 漏洞的利用：弱口令+文件上传

> 弱口令进入后台，利用第三方插件进行getshell

1、ping一下域名，得到网站的ip，再尝试一下多地ping，得到ip为真实的ip。

![](https://image.3001.net/images/20201216/1608091149_5fd9860d9fe5ef665f1d2.png!small)

![](https://image.3001.net/images/20201114/1605344596_5faf9d546da1f7414fbc9.jpg!small)

2、在fofa中搜索一下该ip，得到一个后台登录的地址

![1608103324_5fd9b59c549c7330ea373.png!small?1608103324976](https://image.3001.net/images/20201216/1608103324_5fd9b59c549c7330ea373.png!small?1608103324976)

  

3、点击进入，点击登陆后台

![](https://image.3001.net/images/20201114/1605344652_5faf9d8c8d4dd032b1f43.jpg!small)

![](https://image.3001.net/images/20201114/1605344667_5faf9d9bd35959cdcbad4.jpg!small)

  

4、尝试弱口令，直接进入后台

![](https://image.3001.net/images/20201114/1605344745_5faf9de94588729a6c575.jpg!small)

5、默认会有插件管理功能，需要安装一个插件，离线下载插件，网址：<https://www.fastadmin.net/store/fileix.html>

插件管理默认是被阉割的，但是可以访问：[/admin/addon?ref=addtabs](https://49.235.220.130/admin/addon?ref=addtabs)看到，然后点击离线安装

![](https://image.3001.net/images/20201114/1605344807_5faf9e277607e92eb3edb.jpg!small)

6、此时插件已经安装成功

![](https://image.3001.net/images/20201114/1605344878_5faf9e6e4e12527908ec2.jpg!small)

7、插件安装成功之后，导航栏会出现文件光选项，点击文件管理进入

![](https://image.3001.net/images/20201114/1605344910_5faf9e8e9be684b589d63.jpg!small)

8、上传准备好的木马，这里我上传的是phpinfo的马。

![](https://image.3001.net/images/20201114/1605344986_5faf9eda3dd2aee7f257e.jpg!small)9、访问木马，成功的getshell。

![](https://image.3001.net/images/20201114/1605345081_5faf9f392453c6b99717e.jpg!small)

## 结束语

>
> 到这里，漏洞的分享就结束了。这篇文章其实没有什么技术含量，这是我在平台发表的第一篇文章，以后也会继续分享一下自己的学习经历，错误的地方，希望各位批评指出，谢谢！

PS：本文只是的用于技术讨论和研究，请勿用于非法用途，违者后果自负，与本作者无关。


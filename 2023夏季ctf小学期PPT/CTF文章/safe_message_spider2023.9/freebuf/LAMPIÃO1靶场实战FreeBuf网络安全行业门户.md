Lampiao是Vulnhub上的一个靶场，难度为easy。

下载地址为 <https://www.vulnhub.com/entry/lampiao-1,249/>

## 一、信息收集

在VM上搭建好靶机，就可以开始尝试渗透了。

首先先用nmap扫一下IP，锁定靶机的ip地址。

![](https://image.3001.net/images/20221227/1672128336_63aaa7505891b522c1e6b.png!small)

确认是192.168.250.130后，扫一下端口、服务和版本以及操作系统信息。

![](https://image.3001.net/images/20221227/1672128390_63aaa7864d9ac5f865ca0.png!small)![](https://image.3001.net/images/20221227/1672128417_63aaa7a140fb13ed24a2c.png!small)![](https://image.3001.net/images/20221227/1672128428_63aaa7acb35f55b42a97f.png!small)

从上述信息可以看到，Lampiao靶机一共开了3个端口，22、80和1898。操作系统的信息获取的不是很准确，只能确定内核是Linux3.2-4.9。

用御剑暴破一下目录，没有什么结果。

接下来分别访问80和1898端口看一下。

![](https://image.3001.net/images/20221227/1672128486_63aaa7e60b04ec5054d55.png!small)![](https://image.3001.net/images/20221227/1672128493_63aaa7edbee3afea71adc.png!small)

可以看到80就是一个静态页面，而1898则打开了一个登陆页面，并且发现其下方写着Powered by
Drupal。经过查询后得知其是一个使用PHP语言编写的开源内容管理框架。

这里就有两个思路，一个是我们可以看看1898这个web系统是否存在可以用的漏洞，另外就是Drupal框架是否有漏洞可以利用。

此时用御剑对1898进行目录暴破，得到结果如下：

![](https://image.3001.net/images/20221227/1672128557_63aaa82d059eb94692682.png!small)

## 二、漏洞挖掘

先针对靶场提供的web页面做下研究，首先就是登录，注册和修改密码页面。

![](https://image.3001.net/images/20221227/1672128631_63aaa8774700aa29eb80d.png!small)测试一下sql注入，没有找到明显的注入点。尝试注册一下，发现邮箱验证功能好像失效了，这样就无法获得可登录的账号密码。

![](https://image.3001.net/images/20221227/1672128642_63aaa8820266d14a4649f.png!small)除了登录等功能外，当我点击右方图片时页面也发生了变化，且url中出现了?q=node/1，这就让人很想把1换成其他数字试试看还有什么内容。当我们输入2时，页面显示出了两个文件并且提示“Quite
difficult using it. Trying to embed some sound and image… =(”，那我们就分别访问试试看。

![](https://image.3001.net/images/20221227/1672128690_63aaa8b25a46a6ac2410d.png!small)第一个文件是一个2s的音频，告诉了我们“user
trago”(获取到了用户名以后本来想尝试去暴破密码的，结果听了好几遍，一直以为是tragl，结果暴破了好久也没成功。。。)

![](https://image.3001.net/images/20221227/1672128698_63aaa8baf050607c6845d.png!small)另外一个文件是一个二维码，扫开以后内容是“Try
harder! muahuahua”，成功收到了作者的一段留言。

![](https://image.3001.net/images/20221227/1672128740_63aaa8e498d613f26e143.png!small)再尝试把数字换成3，又获得了一个新的音频文件名称，但这个音频文件只是一首歌曲。继续向后尝试，发现后面没有新的页面内容了。

![](https://image.3001.net/images/20221227/1672128751_63aaa8ef722e9a6c93bee.png!small)考虑到这个web系统提供的功能过少，直接到御剑找到的后台目录里边看一看。

![](https://image.3001.net/images/20221227/1672128791_63aaa9170d6d0ede857be.png!small)

首先，发现了其使用的是2.4.7版本的Apache，操作系统使用的是ubuntu。

其次，通过对一些文件的大致浏览，确定了其使用的是Drupal框架

![](https://image.3001.net/images/20221227/1672128863_63aaa95f283fa4a7af937.png!small)

除此之外并没有找到一些较为有效的信息，如数据库连接的用户名密码等。

关于靶机提供给我们的1898端口，我们大致能够分析出这些内容。接下来我们可以从Drupal框架入手看看有什么漏洞是可以利用的。

进入到msf中，查找有关Drupal框架的漏洞信息。

![](https://image.3001.net/images/20221227/1672128898_63aaa982c64b13788c820.png!small)可以看到漏洞数量还是不少的，那么我们就用这些exploit去尝试一下。

## 三、反弹Shell

根据刚刚得到的漏洞，先用第一个试试看。

![](https://image.3001.net/images/20221227/1672128959_63aaa9bf25051781badeb.png!small)很可惜，没有成功。接着再试试第二个。

![](https://image.3001.net/images/20221227/1672128969_63aaa9c9e5bb55ee99bd1.png!small)

这次成功进入了meterpreter并反弹了shell。

与此同时，由于之前通过找到的音频文件获取到了用户名，我们也可以尝试ssh暴破获取到密码，然后登录到靶场并反弹shell。

进入shell，并且查看一下当前用户的权限以及当前的目录。

![](https://image.3001.net/images/20221227/1672129047_63aaaa170428dd428069e.png!small)

发现只是个普通用户，那么我们就要考虑如何进行提权操作。

## 四、提升权限

使用uname -a获得到当前的操作系统详细信息。

Linux lampiao 4.4.0-31-generic #50~14.04.1-Ubuntu SMP Wed Jul 13 01:06:37 UTC
2016 i686 athlon i686 GNU/Linux

发现其使用的ubuntu为14.04.1，可以被脏牛漏洞提权。

首先先在msf中查找一下脏牛漏洞。

![](https://image.3001.net/images/20221227/1672129198_63aaaaae2b6ad5e476c84.png!small)这里我们选择40847脏牛漏洞，由于是.cpp文件，所以我们还要查看一下靶场是否具有编译环境。

![](https://image.3001.net/images/20221227/1672129221_63aaaac56ef2cbaba9b2d.png!small)

接下来我们就要利用meterpreter上传漏洞文件并根据漏洞文件的提示完成漏洞利用。

首先，我们要先查找一下40847.cpp的路径，并且打开确认一下漏洞利用方法。

![](https://image.3001.net/images/20221227/1672129244_63aaaadc6a831b73a35fd.png!small)![](https://image.3001.net/images/20221227/1672129251_63aaaae3f1ea62551bdbe.png!small)将40847.cpp上传到靶机并利用。

![](https://image.3001.net/images/20221227/1672129289_63aaab09bb63235c36bf5.png!small)![](https://image.3001.net/images/20221227/1672129296_63aaab10d53072ad0277f.png!small)注意，这里需要利用命令python
-c 'import pty; pty.spawn("/bin/bash")'切换至交互式shell，否则漏洞将会利用失败。

![](https://image.3001.net/images/20221227/1672129321_63aaab2915ec000cdcd6a.png!small)可以看到，此时我们已经提权成功，Lampiao靶场成功攻破。


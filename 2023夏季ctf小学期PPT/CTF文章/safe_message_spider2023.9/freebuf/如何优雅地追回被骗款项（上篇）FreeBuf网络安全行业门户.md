## 前言  

 **熟悉我的人都知道，我写的文章一般都是偏向于生活实战类，这次也是一样，故事的起因是我身边的朋友，被骗了，且看截图。**

![图片.png](https://image.3001.net/images/20181129/1543492368_5bffd31038428.png!small)

![图片.png](https://image.3001.net/images/20181129/1543492379_5bffd31bcb9a6.png!small)

  

![图片.png](https://image.3001.net/images/20181129/1543492388_5bffd324a383d.png!small)

其实身边很多朋友都想做刷单兼职，或者打字兼职什么的，但是很多都是骗所谓的保证金，交钱立马拉黑那种。

## 0*01信息收集阶段

我们现在所知道的信息比较有限，唯一知道的就是网站，与及那个人的qq号，所以我们还是先来看看网站的信息。

目标:[www.xxxx.com](http://www.xxxx.com)

首先打开网站

![图片.png](https://image.3001.net/images/20181129/1543492399_5bffd32f129a6.png!small)  

做工极其真实，包括如何付款，正在发生，等等，诱惑性很强，首先发现存在注册功能，那就先注册一下。

  
![图片.png](https://image.3001.net/images/20181129/1543492411_5bffd33b73c8b.png!small)

我发现这站点的各类功能都很齐全，可能会存在各种逻辑漏洞类似的，但我内心没有黑吃黑的想法，所以在测试了没有明显的注入与及文件上传之后就放弃掉了挖掘后台的漏洞。

首先我们来看看是否存在cdn，多地ping一下。

![图片.png](https://image.3001.net/images/20181129/1543492421_5bffd34504c3e.png!small)

接下来扫一下端口

![图片.png](https://image.3001.net/images/20181129/1543492429_5bffd34da0e64.png!small)

开放了四个端口，其中21的ftp爆破，3306的mysql，3389的rdp都可以采取爆破的方式，但是这样子很可能会打草惊蛇，所以不到万不得已不采取这种方法。

扫描目录结果如下：

我发现了一个非常有意思的事情，存在一些疑似后门的文件，与及管理后台都做了403处理。

![图片.png](https://image.3001.net/images/20181129/1543492439_5bffd35704eb5.png!small)

不妨来猜测一下管理员是如何访问后台目录的，有以下几种情况。

/referer头

/ip地址

/白名单，黑名单

/cookie头

没办法只能一步步来测试，首先是referer头，这里我用burp的intruder模块。

![图片.png](https://image.3001.net/images/20181129/1543492448_5bffd3604c6fd.png!small)

把127.0.0.1,localhost,google.com 与及扫描到的目录进行入库处理，当成爆破字典进行处理。然后go~

emmm

![图片.png](https://image.3001.net/images/20181129/1543492457_5bffd36904802.png!small)

失败了不虚 我们换一种方式。关于ip地址的伪造，如果对方使用某ip地址黑白名单，那我们很难猜测的出来，这里没办法测试。

所以我把目光主要放在了/cookie头上，思路非常简单遍历1-100，admin，guanliyuan等明文与及base64加密解密的密文，再传进http头里，有两种方式，一种是先处理好，然后丢burp里面，一种是用python来实现。

我在这里为了方便与及加代理池，就用python来实现。

![图片.png](https://image.3001.net/images/20181129/1543492465_5bffd3711bbe7.png!small)

等了十分钟左右，非常难受，并没有我想要的结果，难不成是我的想法错了吗？

![图片.png](https://image.3001.net/images/20181129/1543492479_5bffd37f2e419.png!small)

## 0*02艰难的渗透测试

我没有开始怀疑人生，摸摸了我身边二哈的狗头，继续整理思路。

如果这些文件都是故意设计出来引诱我们的，也就是说这些文件压根就是没用的，纯粹是被用来玩耍我们的，毕竟一个骗子的网站肯定经过千锤百炼，不应该会那么简单才对，明明业务在正常进行，怎么可能会存在后门文件那么明显的事情。

突然，我发现了一个之前很显眼的目录，但是被我忽略掉了，一大堆403蒙蔽了我的双眼。

然后我以xxxx.com/manager为目标去扫描该目录，得到以下结果，

![图片.png](https://image.3001.net/images/20181129/1543492488_5bffd38863d17.png!small)

尝试扫描manager目录

![图片.png](https://image.3001.net/images/20181129/1543492496_5bffd39046c44.png!small)

继续扫描

![图片.png](https://image.3001.net/images/20181129/1543492502_5bffd39639bfd.png!small)

得到后台地址！

![图片.png](https://image.3001.net/images/20181129/1543492512_5bffd3a080d7d.png!small)

可以看到没有验证码，所以这里也可以给它来一套全家桶爆破。

![图片.png](https://image.3001.net/images/20181129/1543492519_5bffd3a7b8656.png!small)

来总结一下对方信息。

对方服务器开放端口为

21

80

3306

3389

web容器为nginx

服务器识别为2008

与及后台目录为<http://xxxx.com/manager/admin/login.php>

常见的漏洞挖掘了一遍没找到啥有用的，似乎除了爆破大法，没啥好走的了，又陷入了死胡同。

![图片.png](https://image.3001.net/images/20181129/1543492528_5bffd3b0f1d82.png!small)

问题不大，点了一支烟，再次摸摸我家二哈的狗头，我发现它最近的头发跟我的一样稀疏了，有点小开心。

既然主站日不下，那就扫一下二级域名。

![图片.png](https://image.3001.net/images/20181129/1543492535_5bffd3b7e02d0.png!small)

没有任何子域名。

也对手机的模板在m目录中。也没别的业务了应该。

由于没有cdn我们可以直接扫描一下C段

扫描结果如下

![图片.png](https://image.3001.net/images/20181129/1543492541_5bffd3bd36511.png!small)

可以看得到，基本上c段的主机都存活，由于我是自己写的脚本，所以没加上批量识别端口的功能。

经过漫长的测试，我把目光放在了某个主机的web服务上。

首先看看这台机子开放的端口。

![图片.png](https://image.3001.net/images/20181129/1543492550_5bffd3c6b3486.png!small)

只开放了五个端口，脚本没有指纹识别的功能。（正在努力完善，还是太懒了）

首先打开80看看。

![图片.png](https://image.3001.net/images/20181129/1543492558_5bffd3ce3c02e.png!small)

看到这个页面的时候，我非常开心，这是个phpstudy的默认页面，也就是php探针，在下面还有一个mysql链接检测。

![图片.png](https://image.3001.net/images/20181129/1543492570_5bffd3daee92f.png!small)

一般来说，此类网站都是小白刚拿到手，连默认页面都没删，那么可以想到很可能存在弱口令之类的问题。

首先打开burp爆破一波。

![图片.png](https://image.3001.net/images/20181129/1543492579_5bffd3e32c8a6.png!small)

Top500的弱口令丢进去，几分钟就拿到了root的密码，心想，如果这时候再拿到一个phpmyadmin，那拿下这台机子岂不是非常简单的事情。

然后我拿起御剑就是一波扫描。

![图片.png](https://image.3001.net/images/20181129/1543492634_5bffd41a14404.png!small)

Ok不慌这里啥都没有，很奇怪连首页也没扫到，探针的默认页面应该是l.php才对。

还有一个端口81的，打开，页面如下。

![图片.png](https://image.3001.net/images/20181129/1543492641_5bffd42139cc3.png!small)  

Emmm应该是刚开始学php的娃...扫一下81口的目录。

![图片.png](https://image.3001.net/images/20181129/1543492650_5bffd42a4680b.png!small)

似乎没啥好玩的，除了爆破3389端口。抬头看了看时间，发现已经凌晨3点多，但是机智如我，并没有打算放弃。

  
![图片.png](https://image.3001.net/images/20181129/1543492657_5bffd43142a2c.png!small)

## 0*03一波三折

鬼使神差的我，想起了当初我上php课程的时候，用的是phpnow，两年前时候为了真实性，我也买了一个服务器，但是那时候特别懒，为了数据能在本地直接管理，我直接开放了mysql的外连，并且我那时候连接MySQL使用的是sqlyog这个神器。

我在d盘的不知道那个灰尘角落那搬出sqlyog，然后填上服务器地址，root账号密码

![图片.png](https://image.3001.net/images/20181129/1543492666_5bffd43ad0092.png!small)

看来似乎并没有开启外连，好像又走入了死胡同。

但是我突然想起，似乎mysql的链接方式并不止这些，比如说

![图片.png](https://image.3001.net/images/20181129/1543492675_5bffd4433688e.png!small)

Ok，确定思路之后，我找了十几个常见的mysql管理工具的http隧道文件名，然后一顿乱扫。

![图片.png](https://image.3001.net/images/20181129/1543492682_5bffd44a09292.png!small)

这是Navicat的默认mysql连接文件，如下

![图片.png](https://image.3001.net/images/20181129/1543492688_5bffd450bb17a.png!small)  

但是我不管怎么样尝试都是连不上，后来百度找到了原因，贼坑。

当mysql不允许外连的时候，就算是http隧道也连接不上。

还是（脱裤）拖得少，不然也不会在这浪费那么多时间。

一波三折过后的我，并不想就此放弃，抱着啥都没有的希望点开了8080.

![图片.png](https://image.3001.net/images/20181129/1543492695_5bffd457c00de.png!small)

403似乎有搞头，扫一波目录。

![图片.png](https://image.3001.net/images/20181129/1543492705_5bffd4613efd1.png!small)

终于找到了phpmyadmin，废话不多说，直接登陆。

对于phpmyadmin下root权限getshgell我相信大家都很熟悉，我就大概略过。

在前面我们已经知道了绝对路径，所以就不用再查询了，如果我们之前不知道的话，可以查询data变量。

![图片.png](https://image.3001.net/images/20181129/1543492712_5bffd46845d99.png!small)

首先查看generallog是否开启，我们的思路是开启general_log，然后设置general_log_file为一个php文件，最后用一句话木马进行查询来获取shell。

![图片.png](https://image.3001.net/images/20181129/1543492720_5bffd470d8399.png!small)

这里可以看出是关闭的，我们先打开它。

![图片.png](https://image.3001.net/images/20181129/1543492731_5bffd47b38e09.png!small)

然后把general_log_file设置为shell的绝对路径

![图片.png](https://image.3001.net/images/20181129/1543492739_5bffd483ecfa4.png!small)

接下来直接写shell

![图片.png](https://image.3001.net/images/20181129/1543492748_5bffd48c455df.png!small)

查看一下webshell

![图片.png](https://image.3001.net/images/20181129/1543492755_5bffd493ea05b.png!small)

  

没毛病，直接上菜刀。

![图片.png](https://image.3001.net/images/20181129/1543492762_5bffd49a7ccb5.png!small)  

看到这目录我大概知道了咋回事，应该是练习到了学习php的apache多个端口设置，所以才会分为那么多目录。

看看是啥权限。

![图片.png](https://image.3001.net/images/20181129/1543492770_5bffd4a28f33a.png!small)

Administrator权限很舒服，上mimikazi

![图片.png](https://image.3001.net/images/20181129/1543492778_5bffd4aa38dbe.png!small)

读个密码

![图片.png](https://image.3001.net/images/20181129/1543492785_5bffd4b20006d.png!small)

为了防止被爆菊，只能打重码，然后我们可以登陆上去看看。

![图片.png](https://image.3001.net/images/20181129/1543492793_5bffd4b991a23.png!small)

Ok上工具，根据外网的ip很容易推出这里的内网ip，在内网中，首先查看一下有没有域控，

  
![图片.png](https://image.3001.net/images/20181129/1543492802_5bffd4c244a4e.png!small)

没有，那就直接扫目标机器端口

![图片.png](https://image.3001.net/images/20181129/1543492808_5bffd4c87432b.png!small)

6个端口，还有一个没接触过的9191，不过当我看到445的时候，我突然想起了大名鼎鼎的smb溢出问题，在小型网络服务提供商中，系统没打补丁是个很正常的事情，上个小脚本扫一下。

![图片.png](https://image.3001.net/images/20181129/1543492815_5bffd4cff2ad2.png!small)

非常开心，基本可以确定这个系统是可以拿下来的了。

事情发展，请期待下篇！


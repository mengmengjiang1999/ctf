原创： 二狗子  合天智汇

  
  

  

今天基佬在群里发来一个国外的站然后让帮忙拿shell

  
![图片.png](https://image.3001.net/images/20181017/1539760816_5bc6e2b06972d.png!small)  

话不多说，我迎众基去了。

第一反应找上传。

![图片.png](https://image.3001.net/images/20181017/1539760837_5bc6e2c50a25d.png!small)  

该处找到一个上传，我们新建一个然后上传。经过简单的测试直接00截断就可以绕过了。emmmm但是尴尬才刚刚开始。

  
![图片.png](https://image.3001.net/images/20181017/1539760844_5bc6e2cc863c1.png!small)  

虽然成功上传了但没有路径，这个好解决直接去后台里同类新闻去看路径即可。

但是尴尬的事情发生了。

后台查看图片的路径是这样的：http://www.xxxxx.pt/admin/ewupl0ad10.php?rnd=1559055055&id=x_img&file=to_e_nado.jpg&version=thumbnail&download=1

看到file参数一下就想到了任意文件下载，但是一波操作以后确认并没有，ps：前台的图片路径测试一波？？？

但尴尬的是前台的新闻跟这个后台的这个不太相符，加之是英文的不太能看得懂所以一番折磨以后还是不太确认前台的图片路径是否就是。一度冷场。找到如下两个文件路径

前台图片路径1：

http://www.xxx.pt/assets/noticias/sp1_9043.jpg

文件路径2：

http://www.xxx.pt/assets/desporto/2018080166157.pdf

然后测试扫描一波吧。看看有没有uploadfiles之类的路径

  

![图片.png](https://image.3001.net/images/20181017/1539760857_5bc6e2d943ed7.png!small)  

一波扫下来依旧没有任何结果。然后我直接拿刚才那个下载去尝试一下下载我刚才的php文件呢？

http://www.xxx.pt//admin/ewupl0ad0.php?rnd=1559055055&id=x_img&file=17_0060.php&version=thumbnail&download=1

发现并不存在。

  
![图片.png](https://image.3001.net/images/20181017/1539760964_5bc6e344782a1.png!small)  

WAF???路径错误???

然后停顿了一下，怀疑到底是不是上传的时候限制了什么，再会回过头来看下发包的数据包，是路径错误？？？但是访问那个文件路径还是不行呀。

![图片.png](https://image.3001.net/images/20181017/1539760971_5bc6e34b07f68.png!small)  

这img干嘛的？？？改成file会不会来姨妈？

依旧返回了一个文件

  
![图片.png](https://image.3001.net/images/20181017/1539760978_5bc6e3523a920.png!small)  

访问。

http://www.xxx.pt/assets/desporto/2333_1232.php和

http://www.xxx.pt/assets/noticias/2333_1232.php

发现

http://www.xxx.pt/assets/desporto/2333_1232.php

成功getshell

![图片.png](https://image.3001.net/images/20181017/1539760985_5bc6e3598aa2b.png!small)  

  
![图片.png](https://image.3001.net/images/20181017/1539760991_5bc6e35f78345.png!small)  

  
![图片.png](https://image.3001.net/images/20181017/1539760997_5bc6e3650d71b.png!small)  

2012又开了安全模式，提权比较囧。把shell丢给基佬，基佬专注提权日内网十八年。

国外的站和国内的还不太一样，因为路径缘故还闹腾了不少时间。

该站是朋友在国外公司的项目所以是授权的.

emmm over

  

  


